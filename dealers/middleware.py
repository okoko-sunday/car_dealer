from django.http import Http404
from .models import Dealer, DealerDomain

class DealerTenantMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        request.dealer = None
        host = request.get_host().split(":")[0].lower()
        domain = DealerDomain.objects.select_related("dealer").filter(hostname=host, dealer__is_active=True).first()
        if domain:
            request.dealer = domain.dealer
        elif host in {"localhost", "127.0.0.1", "testserver"}:
            slug = request.GET.get("dealer") or request.session.get("dealer_slug")
            request.dealer = Dealer.objects.filter(slug=slug, is_active=True).first() if slug else Dealer.objects.filter(is_active=True).first()
            if request.GET.get("dealer") and request.dealer:
                request.session["dealer_slug"] = request.dealer.slug
        return self.get_response(request)
