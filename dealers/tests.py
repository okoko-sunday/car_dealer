from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from .forms import VehicleForm
from .models import BuyerRequest, Dealer, DealerDomain, MarketplaceListing, Membership, OutboxEvent, Vehicle, VehicleImage
from .services import apply_to_simulator, deliver_event, save_vehicle

@override_settings(ALLOWED_HOSTS=["*"])
class PlatformTests(TestCase):
    def setUp(self):
        User=get_user_model(); self.user=User.objects.create_user("owner",password="pass")
        self.a=Dealer.objects.create(name="A",slug="a",email="a@a.test",phone="1",address="Lagos")
        self.b=Dealer.objects.create(name="B",slug="b",email="b@b.test",phone="2",address="Abuja")
        DealerDomain.objects.create(dealer=self.a,hostname="a.test"); DealerDomain.objects.create(dealer=self.b,hostname="b.test")
        Membership.objects.create(dealer=self.a,user=self.user,role=Membership.Role.OWNER)
        self.car=Vehicle.objects.create(dealer=self.b,slug="secret",make="Toyota",model="Camry",year=2020,price=100,mileage_km=1,transmission="Auto",fuel_type="Petrol",condition="Used",location="Abuja",description="B only")
    def test_tenant_publication_isolation(self):
        self.car.publication_status=Vehicle.Publication.PUBLISHED; self.car.save()
        self.assertNotContains(self.client.get(reverse("inventory"),HTTP_HOST="a.test"),"Camry")
        self.assertContains(self.client.get(reverse("inventory"),HTTP_HOST="b.test"),"Camry")
    def test_cross_tenant_edit_is_not_found(self):
        self.client.login(username="owner",password="pass")
        response=self.client.get(reverse("vehicle_edit",args=[self.car.pk]),HTTP_HOST="a.test")
        self.assertEqual(response.status_code,404)
    def test_viewer_cannot_edit(self):
        Membership.objects.filter(dealer=self.a,user=self.user).update(role=Membership.Role.VIEWER)
        self.client.login(username="owner",password="pass")
        self.assertEqual(self.client.get(reverse("vehicle_create"),HTTP_HOST="a.test").status_code,403)
    def test_out_of_order_and_duplicate_events_do_not_overwrite(self):
        self.car.publication_status=Vehicle.Publication.PUBLISHED; self.car.version=2; self.car.save()
        newer=OutboxEvent.objects.create(dealer=self.b,aggregate_type="vehicle",aggregate_id=self.car.id,aggregate_version=2,event_type="vehicle.sold.v1",payload={"price":"90","availability":"sold"})
        older=OutboxEvent.objects.create(dealer=self.b,aggregate_type="vehicle",aggregate_id=self.car.id,aggregate_version=1,event_type="vehicle.published.v1",payload={"price":"100","availability":"available"})
        apply_to_simulator(newer); apply_to_simulator(older); apply_to_simulator(newer)
        listing=MarketplaceListing.objects.get(source_vehicle_id=self.car.id)
        self.assertEqual(listing.source_version,2); self.assertEqual(listing.dealer_data["availability"],"sold")
    def test_hidden_marketplace_decision_survives_update(self):
        self.car.publication_status=Vehicle.Publication.PUBLISHED; self.car.save()
        first=OutboxEvent.objects.create(dealer=self.b,aggregate_type="vehicle",aggregate_id=self.car.id,aggregate_version=1,event_type="vehicle.published.v1",payload={"price":"100"})
        deliver_event(first); listing=MarketplaceListing.objects.get(); listing.visibility=MarketplaceListing.Visibility.HIDDEN; listing.save()
        second=OutboxEvent.objects.create(dealer=self.b,aggregate_type="vehicle",aggregate_id=self.car.id,aggregate_version=2,event_type="vehicle.updated.v1",payload={"price":"80"})
        deliver_event(second); listing.refresh_from_db()
        self.assertEqual(listing.visibility,MarketplaceListing.Visibility.HIDDEN); self.assertEqual(listing.dealer_data["price"],"80")
    def test_withdrawal_forces_non_public_state(self):
        event=OutboxEvent.objects.create(dealer=self.b,aggregate_type="vehicle",aggregate_id=self.car.id,aggregate_version=1,event_type="vehicle.withdrawn.v1",payload={"publication_status":"unpublished"})
        deliver_event(event)
        self.assertEqual(MarketplaceListing.objects.get().visibility,MarketplaceListing.Visibility.WITHDRAWN)
    def test_offer_starts_pending_and_does_not_sell_vehicle(self):
        self.car.publication_status=Vehicle.Publication.PUBLISHED; self.car.save()
        response=self.client.post(reverse("vehicle_detail",args=[self.car.slug]), {"kind":"offer","name":"Buyer","email":"buyer@example.test","phone":"0800","message":"Please consider","offer_amount":"90","consent":"on"}, HTTP_HOST="b.test")
        self.assertEqual(response.status_code,302)
        inquiry=BuyerRequest.objects.get()
        self.assertEqual(inquiry.offer_status,BuyerRequest.OfferStatus.PENDING)
        self.car.refresh_from_db(); self.assertNotEqual(self.car.availability,Vehicle.Availability.SOLD)
    def test_counteroffer_requires_amount(self):
        own=Vehicle.objects.create(dealer=self.a,slug="own",make="Honda",model="Civic",year=2021,price=100,mileage_km=2,transmission="Auto",fuel_type="Petrol",condition="Used",location="Lagos",description="Own")
        inquiry=BuyerRequest.objects.create(dealer=self.a,vehicle=own,kind=BuyerRequest.Kind.OFFER,name="Buyer",email="b@example.test",phone="1",offer_amount=80,offer_status=BuyerRequest.OfferStatus.PENDING)
        self.client.login(username="owner",password="pass")
        response=self.client.post(reverse("request_status",args=[inquiry.pk]), {"status":"contacted","appointment_outcome":"not_set","offer_status":"countered","counter_offer_amount":"","staff_note":""}, HTTP_HOST="a.test")
        self.assertEqual(response.status_code,302)
        inquiry.refresh_from_db(); self.assertEqual(inquiry.offer_status,BuyerRequest.OfferStatus.PENDING)
    def test_cross_tenant_image_delete_is_not_found(self):
        image=VehicleImage.objects.create(vehicle=self.car,image="vehicles/test.jpg",alt_text="Test",position=0)
        self.client.login(username="owner",password="pass")
        self.assertEqual(self.client.post(reverse("image_delete",args=[image.pk]),HTTP_HOST="a.test").status_code,404)
    def test_sitemap_contains_only_current_tenant(self):
        self.car.publication_status=Vehicle.Publication.PUBLISHED; self.car.save()
        own=Vehicle.objects.create(dealer=self.a,slug="own-map",make="Honda",model="Civic",year=2021,price=100,mileage_km=2,transmission="Auto",fuel_type="Petrol",condition="Used",location="Lagos",description="Own",publication_status=Vehicle.Publication.PUBLISHED)
        response=self.client.get(reverse("sitemap"),HTTP_HOST="a.test")
        self.assertContains(response,"own-map"); self.assertNotContains(response,"secret")
    def test_staff_workflow_dashboard_renders(self):
        own=Vehicle.objects.create(dealer=self.a,slug="workflow",make="Honda",model="Accord",year=2021,price=100,mileage_km=2,transmission="Auto",fuel_type="Petrol",condition="Used",location="Lagos",description="Own")
        BuyerRequest.objects.create(dealer=self.a,vehicle=own,kind=BuyerRequest.Kind.OFFER,name="Buyer",email="b@example.test",phone="1",offer_amount=80,offer_status=BuyerRequest.OfferStatus.PENDING)
        self.client.login(username="owner",password="pass")
        response=self.client.get(reverse("requests_list"),HTTP_HOST="a.test")
        self.assertContains(response,"Update workflow"); self.assertContains(response,"sale or mark the car Sold")
    def test_vehicle_media_editor_renders_controls(self):
        own=Vehicle.objects.create(dealer=self.a,slug="media",make="Honda",model="Pilot",year=2021,price=100,mileage_km=2,transmission="Auto",fuel_type="Petrol",condition="Used",location="Lagos",description="Own")
        VehicleImage.objects.create(vehicle=own,image="vehicles/test.jpg",alt_text="Front view",position=0)
        self.client.login(username="owner",password="pass")
        response=self.client.get(reverse("vehicle_edit",args=[own.pk]),HTTP_HOST="a.test")
        self.assertContains(response,"Move image earlier"); self.assertContains(response,"Remove")
