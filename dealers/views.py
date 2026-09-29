from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .auth import dealer_role_required
from .forms import BuyerRequestForm, BuyerRequestStaffForm, DealerForm, VehicleForm, VehicleImageForm
from .models import AuditEntry, BuyerRequest, Membership, OutboxEvent, Vehicle, VehicleImage
from .services import record_dealer_change, record_vehicle_change, save_vehicle

EDIT_ROLES = (Membership.Role.OWNER, Membership.Role.MANAGER)
STAFF_ROLES = (*EDIT_ROLES, Membership.Role.SALES, Membership.Role.VIEWER)

def require_dealer(request):
    if not request.dealer: raise Http404("No dealer is configured for this domain.")
    return request.dealer

def home(request):
    dealer = require_dealer(request)
    public = Vehicle.objects.filter(dealer=dealer, publication_status=Vehicle.Publication.PUBLISHED)
    return render(request, "public/home.html", {"featured": public.filter(is_featured=True)[:3], "arrivals": public.order_by("-published_at")[:4]})

def inventory(request):
    dealer = require_dealer(request)
    items = Vehicle.objects.filter(dealer=dealer, publication_status=Vehicle.Publication.PUBLISHED).prefetch_related("images")
    q = request.GET.get("q", "").strip()
    if q: items = items.filter(Q(make__icontains=q) | Q(model__icontains=q) | Q(description__icontains=q))
    if request.GET.get("make"): items = items.filter(make=request.GET["make"])
    if request.GET.get("availability"): items = items.filter(availability=request.GET["availability"])
    order = {"price_low": "price", "price_high": "-price", "newest": "-published_at"}.get(request.GET.get("sort"), "-published_at")
    items = items.order_by(order)
    makes = Vehicle.objects.filter(dealer=dealer, publication_status=Vehicle.Publication.PUBLISHED).values_list("make", flat=True).distinct().order_by("make")
    return render(request, "public/inventory.html", {"vehicles": items, "makes": makes, "q": q})

def vehicle_detail(request, slug):
    if request.method == "POST":
        address = request.META.get("REMOTE_ADDR", "unknown")
        key = f"buyer-request:{request.dealer.id if request.dealer else 'none'}:{address}"
        if cache.get(key, 0) >= 5:
            return render(request, "public/rate_limited.html", status=429)
        if not cache.add(key, 1, timeout=600): cache.incr(key)
    dealer = require_dealer(request)
    vehicle = get_object_or_404(Vehicle.objects.prefetch_related("images"), dealer=dealer, slug=slug, publication_status=Vehicle.Publication.PUBLISHED)
    form = BuyerRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        inquiry = form.save(commit=False); inquiry.dealer = dealer; inquiry.vehicle = vehicle; inquiry.offer_status = BuyerRequest.OfferStatus.PENDING if inquiry.kind == BuyerRequest.Kind.OFFER else BuyerRequest.OfferStatus.NOT_APPLICABLE; inquiry.save()
        messages.success(request, "Request received. The dealer will contact you; no sale or booking is confirmed yet.")
        return redirect(f"{reverse('vehicle_detail', args=[slug])}#request")
    similar = Vehicle.objects.filter(dealer=dealer, publication_status=Vehicle.Publication.PUBLISHED, availability=Vehicle.Availability.AVAILABLE).exclude(pk=vehicle.pk)[:3]
    return render(request, "public/vehicle_detail.html", {"vehicle": vehicle, "form": form, "similar": similar})

@dealer_role_required(*STAFF_ROLES)
def dashboard(request):
    vehicles = Vehicle.objects.filter(dealer=request.dealer)
    counts = {key: vehicles.filter(**query).count() for key, query in {
        "active": {"publication_status": Vehicle.Publication.PUBLISHED, "availability": Vehicle.Availability.AVAILABLE},
        "draft": {"publication_status": Vehicle.Publication.DRAFT}, "reserved": {"availability": Vehicle.Availability.RESERVED}, "sold": {"availability": Vehicle.Availability.SOLD},
    }.items()}
    return render(request, "dashboard/index.html", {"counts": counts, "vehicles": vehicles.order_by("-updated_at")[:8], "requests": BuyerRequest.objects.filter(dealer=request.dealer).order_by("-created_at")[:8], "outbox": OutboxEvent.objects.filter(dealer=request.dealer).order_by("-created_at")[:8]})

@dealer_role_required(*STAFF_ROLES)
def dashboard_inventory(request):
    return render(request, "dashboard/inventory.html", {"vehicles": Vehicle.objects.filter(dealer=request.dealer).prefetch_related("images").order_by("-updated_at")})

@dealer_role_required(*EDIT_ROLES)
def vehicle_create(request):
    form = VehicleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = save_vehicle(form, request.dealer, request.user)
        messages.success(request, "Vehicle saved.")
        return redirect("vehicle_edit", pk=item.pk)
    return render(request, "dashboard/vehicle_form.html", {"form": form, "title": "Create vehicle"})

@dealer_role_required(*EDIT_ROLES)
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, dealer=request.dealer)
    form = VehicleForm(request.POST or None, instance=vehicle)
    image_form = VehicleImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and request.POST.get("intent") == "vehicle" and form.is_valid():
        save_vehicle(form, request.dealer, request.user, vehicle)
        messages.success(request, "Changes saved and queued for marketplace sync when applicable.")
        return redirect("vehicle_edit", pk=pk)
    if request.method == "POST" and request.POST.get("intent") == "image" and image_form.is_valid():
        previous = Vehicle.objects.get(pk=vehicle.pk); image = image_form.save(commit=False); image.vehicle = vehicle; image.save(); vehicle.version += 1; vehicle.save(update_fields=["version", "updated_at"]); record_vehicle_change(vehicle, request.user, "vehicle.image_added", previous)
        messages.success(request, "Image uploaded.")
        return redirect("vehicle_edit", pk=pk)
    return render(request, "dashboard/vehicle_form.html", {"form": form, "image_form": image_form, "vehicle": vehicle, "title": f"Edit {vehicle.title}"})

@dealer_role_required(*STAFF_ROLES)
def requests_list(request):
    items = BuyerRequest.objects.filter(dealer=request.dealer).select_related("vehicle").order_by("-created_at")
    return render(request, "dashboard/requests.html", {"requests": items, "request_statuses": BuyerRequest.Status.choices, "offer_statuses": BuyerRequest.OfferStatus.choices, "appointment_outcomes": BuyerRequest.AppointmentOutcome.choices})

@require_POST
@dealer_role_required(Membership.Role.OWNER, Membership.Role.MANAGER, Membership.Role.SALES)
def request_status(request, pk):
    item = get_object_or_404(BuyerRequest, pk=pk, dealer=request.dealer)
    form = BuyerRequestStaffForm(request.POST, instance=item)
    if not form.is_valid():
        messages.error(request, "Please correct the workflow update.")
        return redirect("requests_list")
    item = form.save()
    AuditEntry.objects.create(dealer=request.dealer, actor=request.user, entity_type="buyer_request", entity_id=str(item.id), action="buyer_request.updated", data={"status": item.status, "offer_status": item.offer_status, "appointment_outcome": item.appointment_outcome})
    messages.success(request, "Buyer request updated. An accepted offer is not recorded as a completed sale.")
    return redirect("requests_list")

@dealer_role_required(Membership.Role.OWNER, Membership.Role.MANAGER)
def dealer_settings(request):
    form = DealerForm(request.POST or None, request.FILES or None, instance=request.dealer)
    if request.method == "POST" and form.is_valid():
        dealer = form.save(commit=False); dealer.version += 1; dealer.save(); record_dealer_change(dealer, request.user)
        messages.success(request, "Dealer profile updated.")
        return redirect("dealer_settings")
    return render(request, "dashboard/settings.html", {"form": form})

def health(request): return JsonResponse({"status": "ok"})

@require_POST
@dealer_role_required(*EDIT_ROLES)
def image_delete(request, pk):
    image = get_object_or_404(VehicleImage.objects.select_related("vehicle"), pk=pk, vehicle__dealer=request.dealer)
    vehicle = image.vehicle
    previous = Vehicle.objects.get(pk=vehicle.pk)
    image.delete()
    vehicle.version += 1
    vehicle.save(update_fields=["version", "updated_at"])
    record_vehicle_change(vehicle, request.user, "vehicle.image_removed", previous)
    messages.success(request, "Image removed and marketplace update queued.")
    return redirect("vehicle_edit", pk=vehicle.pk)

@require_POST
@dealer_role_required(*EDIT_ROLES)
@transaction.atomic
def image_move(request, pk):
    image = get_object_or_404(VehicleImage.objects.select_related("vehicle"), pk=pk, vehicle__dealer=request.dealer)
    direction = request.POST.get("direction")
    if direction not in {"up", "down"}: raise Http404
    lookup = {"vehicle": image.vehicle, "position__lt" if direction == "up" else "position__gt": image.position}
    other = VehicleImage.objects.filter(**lookup).order_by("-position" if direction == "up" else "position").first()
    if other:
        previous = Vehicle.objects.get(pk=image.vehicle_id)
        old_position, other_position = image.position, other.position
        image.position = 65535; image.save(update_fields=["position"])
        other.position = old_position; other.save(update_fields=["position"])
        image.position = other_position; image.save(update_fields=["position"])
        vehicle = image.vehicle; vehicle.version += 1; vehicle.save(update_fields=["version", "updated_at"])
        record_vehicle_change(vehicle, request.user, "vehicle.images_reordered", previous)
        messages.success(request, "Image order updated and marketplace update queued.")
    return redirect("vehicle_edit", pk=image.vehicle_id)

def sitemap(request):
    dealer = require_dealer(request)
    vehicles = Vehicle.objects.filter(dealer=dealer, publication_status=Vehicle.Publication.PUBLISHED).order_by("slug")
    return render(request, "public/sitemap.xml", {"vehicles": vehicles}, content_type="application/xml")

def robots(request):
    return HttpResponse("User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /admin/\nSitemap: " + request.build_absolute_uri(reverse("sitemap")) + "\n", content_type="text/plain")
