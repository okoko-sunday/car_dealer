from django.core.management.base import BaseCommand
from django.utils import timezone
from dealers.models import OutboxEvent
from dealers.services import deliver_event, fail_event

class Command(BaseCommand):
    help = "Deliver pending marketplace events; safe to run repeatedly."
    def add_arguments(self, parser): parser.add_argument("--limit", type=int, default=100)
    def handle(self, *args, **options):
        events = OutboxEvent.objects.filter(status__in=[OutboxEvent.Status.PENDING, OutboxEvent.Status.FAILED], next_attempt_at__lte=timezone.now()).order_by("created_at")[:options["limit"]]
        for event in events:
            try:
                deliver_event(event); self.stdout.write(self.style.SUCCESS(f"Delivered {event.id} {event.event_type}"))
            except Exception as exc:
                fail_event(event, exc); self.stderr.write(f"Failed {event.id}: {exc}")
