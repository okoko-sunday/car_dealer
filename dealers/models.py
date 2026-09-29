import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Dealer(TimeStamped):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=240, blank=True)
    story = models.TextField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    whatsapp = models.CharField(max_length=40, blank=True)
    address = models.TextField()
    opening_hours = models.CharField(max_length=240, blank=True)
    primary_color = models.CharField(max_length=7, default="#C8532D")
    accent_color = models.CharField(max_length=7, default="#E8C17A")
    logo = models.ImageField(upload_to="dealers/logos/", blank=True)
    is_active = models.BooleanField(default=True)
    version = models.PositiveBigIntegerField(default=1)
    def __str__(self): return self.name

class DealerDomain(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="domains")
    hostname = models.CharField(max_length=253, unique=True)
    is_primary = models.BooleanField(default=False)
    class Meta:
        indexes = [models.Index(fields=["hostname"])]

class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        SALES = "sales", "Sales"
        VIEWER = "viewer", "Viewer"
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dealer_memberships")
    role = models.CharField(max_length=16, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["dealer", "user"], name="unique_dealer_member")]

class Vehicle(TimeStamped):
    class Publication(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        UNPUBLISHED = "unpublished", "Unpublished"
    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        RESERVED = "reserved", "Reserved"
        SOLD = "sold", "Sold"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT, related_name="vehicles")
    slug = models.SlugField(max_length=180)
    make = models.CharField(max_length=80)
    model = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    mileage_km = models.PositiveIntegerField(default=0)
    transmission = models.CharField(max_length=40)
    fuel_type = models.CharField(max_length=40)
    condition = models.CharField(max_length=80, help_text="Dealer-provided condition")
    location = models.CharField(max_length=160)
    description = models.TextField()
    features = models.TextField(blank=True, help_text="One feature per line")
    known_issues = models.TextField(blank=True)
    seller_history = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    publication_status = models.CharField(max_length=16, choices=Publication.choices, default=Publication.DRAFT)
    availability = models.CharField(max_length=16, choices=Availability.choices, default=Availability.AVAILABLE)
    is_featured = models.BooleanField(default=False)
    version = models.PositiveBigIntegerField(default=1)
    published_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["dealer", "slug"], name="unique_vehicle_slug_per_dealer")]
        indexes = [models.Index(fields=["dealer", "publication_status", "availability"]), models.Index(fields=["dealer", "-created_at"])]
    @property
    def title(self): return f"{self.year} {self.make} {self.model}"
    @property
    def feature_list(self): return [x.strip() for x in self.features.splitlines() if x.strip()]
    def __str__(self): return self.title

class VehicleImage(TimeStamped):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="vehicles/%Y/%m/")
    alt_text = models.CharField(max_length=180)
    position = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ["position", "id"]
        constraints = [models.UniqueConstraint(fields=["vehicle", "position"], name="unique_vehicle_image_position")]

class BuyerRequest(TimeStamped):
    class Kind(models.TextChoices):
        INQUIRY = "inquiry", "General inquiry"
        VIEWING = "viewing", "Viewing / test drive"
        OFFER = "offer", "Offer"
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        SCHEDULED = "scheduled", "Scheduled"
        CLOSED = "closed", "Closed"
    class OfferStatus(models.TextChoices):
        NOT_APPLICABLE = "not_applicable", "Not applicable"
        PENDING = "pending", "Pending review"
        COUNTERED = "countered", "Counteroffer sent"
        ACCEPTED = "accepted", "Offer accepted — sale not completed"
        DECLINED = "declined", "Declined"
    class AppointmentOutcome(models.TextChoices):
        NOT_SET = "not_set", "Not set"
        ATTENDED = "attended", "Attended"
        NO_SHOW = "no_show", "No-show"
        RESCHEDULED = "rescheduled", "Rescheduled"
        CANCELLED = "cancelled", "Cancelled"
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="buyer_requests")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="buyer_requests")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    message = models.TextField(blank=True)
    preferred_at = models.DateTimeField(null=True, blank=True)
    offer_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    counter_offer_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    offer_status = models.CharField(max_length=24, choices=OfferStatus.choices, default=OfferStatus.NOT_APPLICABLE)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    appointment_outcome = models.CharField(max_length=20, choices=AppointmentOutcome.choices, default=AppointmentOutcome.NOT_SET)
    staff_note = models.TextField(blank=True)
    class Meta:
        indexes = [models.Index(fields=["dealer", "status", "-created_at"])]

class AuditEntry(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT, related_name="audit_entries")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    entity_type = models.CharField(max_length=40)
    entity_id = models.CharField(max_length=64)
    action = models.CharField(max_length=80)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=["dealer", "-created_at"]), models.Index(fields=["entity_type", "entity_id"])]

class OutboxEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT, related_name="outbox_events")
    aggregate_type = models.CharField(max_length=32)
    aggregate_id = models.UUIDField()
    aggregate_version = models.PositiveBigIntegerField()
    event_type = models.CharField(max_length=80)
    payload = models.JSONField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveSmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["aggregate_type", "aggregate_id", "aggregate_version", "event_type"], name="unique_versioned_event")]
        indexes = [models.Index(fields=["status", "next_attempt_at"])]

class MarketplaceListing(models.Model):
    """Local simulator only: marketplace-owned visibility is deliberately separate."""
    class Visibility(models.TextChoices):
        PENDING = "pending_review", "Pending review"
        PUBLIC = "public", "Public"
        HIDDEN = "hidden", "Hidden"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"
    source_vehicle_id = models.UUIDField(unique=True)
    dealer_id = models.UUIDField()
    source_version = models.PositiveBigIntegerField()
    dealer_data = models.JSONField()
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PENDING)
    updated_at = models.DateTimeField(auto_now=True)
