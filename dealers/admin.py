from django.contrib import admin
from .models import AuditEntry, BuyerRequest, Dealer, DealerDomain, MarketplaceListing, Membership, OutboxEvent, Vehicle, VehicleImage

for model in [Dealer, DealerDomain, Membership, Vehicle, VehicleImage, BuyerRequest, AuditEntry, OutboxEvent, MarketplaceListing]:
    admin.site.register(model)
