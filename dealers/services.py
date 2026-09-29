import hashlib
import hmac
import json
import urllib.request
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from .models import AuditEntry, MarketplaceListing, OutboxEvent, Vehicle

def dealer_payload(dealer):
    return {"id": str(dealer.id), "version": dealer.version, "name": dealer.name, "slug": dealer.slug,
        "tagline": dealer.tagline, "email": dealer.email, "phone": dealer.phone, "address": dealer.address,
        "opening_hours": dealer.opening_hours, "updated_at": dealer.updated_at.isoformat()}

def record_dealer_change(dealer, actor, created=False):
    OutboxEvent.objects.create(dealer=dealer, aggregate_type="dealer", aggregate_id=dealer.id,
        aggregate_version=dealer.version, event_type="dealer.created.v1" if created else "dealer.updated.v1", payload=dealer_payload(dealer))
    AuditEntry.objects.create(dealer=dealer, actor=actor, entity_type="dealer", entity_id=str(dealer.id),
        action="dealer.created" if created else "dealer.updated", data={"version": dealer.version})

def vehicle_payload(vehicle):
    return {
        "id": str(vehicle.id), "dealer_id": str(vehicle.dealer_id), "version": vehicle.version,
        "title": vehicle.title, "slug": vehicle.slug, "make": vehicle.make, "model": vehicle.model,
        "year": vehicle.year, "price": str(vehicle.price), "currency": "NGN",
        "mileage_km": vehicle.mileage_km, "transmission": vehicle.transmission,
        "fuel_type": vehicle.fuel_type, "condition": vehicle.condition, "location": vehicle.location,
        "description": vehicle.description, "features": vehicle.feature_list,
        "known_issues": vehicle.known_issues, "seller_history": vehicle.seller_history,
        "availability": vehicle.availability, "publication_status": vehicle.publication_status,
        "images": [{"url": i.image.url, "alt": i.alt_text, "position": i.position} for i in vehicle.images.all()],
        "updated_at": vehicle.updated_at.isoformat(),
    }

def event_name(vehicle, previous=None):
    if vehicle.publication_status == Vehicle.Publication.UNPUBLISHED: return "vehicle.withdrawn.v1"
    if vehicle.availability == Vehicle.Availability.SOLD: return "vehicle.sold.v1"
    if previous and previous.availability != vehicle.availability: return "vehicle.availability_changed.v1"
    if vehicle.version == 1 or (previous and previous.publication_status != Vehicle.Publication.PUBLISHED): return "vehicle.published.v1"
    return "vehicle.updated.v1"

def record_vehicle_change(vehicle, actor, action, previous=None):
    if vehicle.publication_status != Vehicle.Publication.DRAFT or (previous and previous.publication_status == Vehicle.Publication.PUBLISHED):
        OutboxEvent.objects.create(dealer=vehicle.dealer, aggregate_type="vehicle", aggregate_id=vehicle.id,
            aggregate_version=vehicle.version, event_type=event_name(vehicle, previous), payload=vehicle_payload(vehicle))
    AuditEntry.objects.create(dealer=vehicle.dealer, actor=actor, entity_type="vehicle", entity_id=str(vehicle.id), action=action,
        data={"version": vehicle.version, "publication": vehicle.publication_status, "availability": vehicle.availability})

@transaction.atomic
def save_vehicle(form, dealer, actor, vehicle=None):
    previous = None
    if vehicle:
        previous = Vehicle.objects.get(pk=vehicle.pk)
    item = form.save(commit=False)
    item.dealer = dealer
    if not item.slug: item.slug = slugify(item.title)
    if previous:
        item.version = previous.version + 1
    if item.publication_status == Vehicle.Publication.PUBLISHED and not item.published_at:
        item.published_at = timezone.now()
    item.save()
    record_vehicle_change(item, actor, "vehicle.updated" if previous else "vehicle.created", previous)
    return item

def apply_to_simulator(event):
    if event.aggregate_type == "dealer":
        return
    data = event.payload
    current = MarketplaceListing.objects.filter(source_vehicle_id=event.aggregate_id).first()
    if current and current.source_version >= event.aggregate_version:
        return
    if not current:
        current = MarketplaceListing(source_vehicle_id=event.aggregate_id, dealer_id=event.dealer_id,
            source_version=event.aggregate_version, dealer_data=data)
    else:
        current.source_version = event.aggregate_version
        current.dealer_data = data
    if event.event_type == "vehicle.withdrawn.v1":
        current.visibility = MarketplaceListing.Visibility.WITHDRAWN
    # Never reset marketplace visibility on ordinary dealer updates.
    current.save()

def deliver_event(event):
    body = json.dumps({"event_id": str(event.id), "event_type": event.event_type, "occurred_at": event.created_at.isoformat(), "data": event.payload}, separators=(",", ":")).encode()
    if settings.MARKETPLACE_WEBHOOK_URL:
        signature = hmac.new(settings.MARKETPLACE_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        request = urllib.request.Request(settings.MARKETPLACE_WEBHOOK_URL, body, {"Content-Type": "application/json", "X-Showroom-Signature": f"sha256={signature}", "X-Event-ID": str(event.id)})
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status >= 300: raise RuntimeError(f"Marketplace returned {response.status}")
    else:
        apply_to_simulator(event)
    event.status = OutboxEvent.Status.DELIVERED
    event.delivered_at = timezone.now()
    event.attempts += 1
    event.last_error = ""
    event.save(update_fields=["status", "delivered_at", "attempts", "last_error"])

def fail_event(event, error):
    event.attempts += 1
    event.status = OutboxEvent.Status.FAILED
    event.last_error = str(error)[:2000]
    event.next_attempt_at = timezone.now() + timedelta(minutes=min(2 ** event.attempts, 60))
    event.save(update_fields=["attempts", "status", "last_error", "next_attempt_at"])
