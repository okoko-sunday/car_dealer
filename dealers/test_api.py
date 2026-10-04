from io import BytesIO
from unittest.mock import patch
from django.db import IntegrityError
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from .models import BuyerRequest, Dealer, DealerDomain, Membership, OutboxEvent, Vehicle

@override_settings(ALLOWED_HOSTS=["*"])
class ApiTests(APITestCase):
    def setUp(self):
        self.a=Dealer.objects.create(name="Dealer A",slug="dealer-a",email="a@example.test",phone="1",address="Lagos")
        self.b=Dealer.objects.create(name="Dealer B",slug="dealer-b",email="b@example.test",phone="2",address="Abuja")
        DealerDomain.objects.create(dealer=self.a,hostname="a.test"); DealerDomain.objects.create(dealer=self.b,hostname="b.test")
        self.user=get_user_model().objects.create_user("owner",password="secret")
        Membership.objects.create(dealer=self.a,user=self.user,role=Membership.Role.OWNER)
        self.car=Vehicle.objects.create(dealer=self.a,slug="lexus",make="Lexus",model="RX",year=2022,price=500,mileage_km=10,transmission="Auto",fuel_type="Petrol",condition="Pre-owned",location="Lagos",description="Dealer A car",publication_status=Vehicle.Publication.PUBLISHED)
        Vehicle.objects.create(dealer=self.b,slug="hidden-tenant",make="Toyota",model="Camry",year=2020,price=200,mileage_km=20,transmission="Auto",fuel_type="Petrol",condition="Pre-owned",location="Abuja",description="Dealer B car",publication_status=Vehicle.Publication.PUBLISHED)
    def headers(self,host="a.test"): return {"HTTP_X_DEALER_HOST":host}
    def login(self,host="a.test"):
        response=self.client.post("/api/v1/auth/token/",{"username":"owner","password":"secret"},format="json",**self.headers(host))
        if response.status_code==200:self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        return response
    def test_public_api_is_tenant_scoped(self):
        response=self.client.get("/api/v1/vehicles/",**self.headers())
        self.assertEqual(response.status_code,200); self.assertEqual(len(response.data),1); self.assertEqual(response.data[0]["slug"],"lexus")
    def test_public_inventory_search_availability_and_sort(self):
        Vehicle.objects.create(dealer=self.a,slug="reserved-toyota",make="Toyota",model="Corolla",year=2021,price=300,mileage_km=20,transmission="Auto",fuel_type="Petrol",condition="Pre-owned",location="Lagos",description="Reserved family sedan",publication_status=Vehicle.Publication.PUBLISHED,availability=Vehicle.Availability.RESERVED)
        search=self.client.get("/api/v1/vehicles/?q=toyota",**self.headers())
        self.assertEqual([item["slug"] for item in search.data],["reserved-toyota"])
        available=self.client.get("/api/v1/vehicles/?availability=available",**self.headers())
        self.assertEqual([item["slug"] for item in available.data],["lexus"])
        ordered=self.client.get("/api/v1/vehicles/?sort=price_low",**self.headers())
        self.assertEqual([item["slug"] for item in ordered.data],["reserved-toyota","lexus"])
    def test_login_rejects_other_dealer(self):
        self.assertEqual(self.login("b.test").status_code,403)
    def test_staff_api_requires_membership_for_selected_tenant(self):
        self.assertEqual(self.login().status_code,200)
        self.assertEqual(self.client.get("/api/v1/staff/overview/",**self.headers("b.test")).status_code,403)
    def test_public_offer_is_pending_and_not_a_sale(self):
        response=self.client.post("/api/v1/vehicles/lexus/",{"kind":"offer","name":"Buyer","email":"buyer@example.test","phone":"0800","message":"Offer","offer_amount":"400","consent":True},format="json",**self.headers())
        self.assertEqual(response.status_code,201); inquiry=BuyerRequest.objects.get(); self.assertEqual(inquiry.offer_status,"pending")
        self.car.refresh_from_db(); self.assertEqual(self.car.availability,"available")
    def test_buyer_requests_limit_by_dealer_contact(self):
        payload={"kind":"inquiry","name":"Buyer","email":"buyer@example.test","phone":"0800","consent":True}
        for _ in range(5):
            self.assertEqual(self.client.post("/api/v1/vehicles/lexus/",payload,format="json",**self.headers()).status_code,201)
        self.assertEqual(self.client.post("/api/v1/vehicles/lexus/",payload,format="json",**self.headers()).status_code,429)
        payload["email"]="another@example.test";payload["phone"]="0900"
        self.assertEqual(self.client.post("/api/v1/vehicles/lexus/",payload,format="json",**self.headers()).status_code,201)

    def test_buyer_must_consent(self):
        response=self.client.post("/api/v1/vehicles/lexus/",{"kind":"inquiry","name":"Buyer","email":"buyer@example.test","phone":"0800","consent":False},format="json",**self.headers())
        self.assertEqual(response.status_code,400)
        self.assertFalse(BuyerRequest.objects.exists())

    def test_staff_image_upload_is_tenant_scoped_and_versioned(self):
        self.login()
        buffer=BytesIO(); Image.new("RGB",(8,8),"white").save(buffer,format="PNG")
        upload=SimpleUploadedFile("vehicle.png",buffer.getvalue(),content_type="image/png")
        response=self.client.post(f"/api/v1/staff/vehicles/{self.car.id}/images/",{"image":upload,"alt_text":"Front view in daylight"},format="multipart",**self.headers())
        self.assertEqual(response.status_code,201); self.assertEqual(len(response.data["images"]),1); self.assertEqual(response.data["version"],2)
        other=Vehicle.objects.get(slug="hidden-tenant")
        image_id=response.data["images"][0]["id"]
        denied=self.client.delete(f"/api/v1/staff/vehicles/{other.id}/images/{image_id}/",**self.headers())
        self.assertEqual(denied.status_code,404)
    def test_second_gallery_upload_gets_distinct_position(self):
        self.login()
        for index in range(2):
            buffer=BytesIO(); Image.new("RGB",(8,8),"white").save(buffer,format="PNG")
            upload=SimpleUploadedFile(f"vehicle-{index}.png",buffer.getvalue(),content_type="image/png")
            response=self.client.post(f"/api/v1/staff/vehicles/{self.car.id}/images/",{"image":upload,"alt_text":f"View {index}"},format="multipart",**self.headers())
            self.assertEqual(response.status_code,201)
        self.assertEqual([image["position"] for image in response.data["images"]],[0,1])

    def test_failed_outbox_write_rolls_back_vehicle_price(self):
        self.login()
        with patch("dealers.services.OutboxEvent.objects.create",side_effect=IntegrityError("outbox unavailable")):
            with self.assertRaises(IntegrityError):
                self.client.patch(f"/api/v1/staff/vehicles/{self.car.id}/",{"price":"550.00"},format="json",**self.headers())
        self.car.refresh_from_db()
        self.assertEqual(self.car.price,500)

    def test_staff_inventory_is_paginated_and_filterable(self):
        self.login()
        for index in range(15):
            Vehicle.objects.create(dealer=self.a,slug=f"stock-{index}",make="Honda" if index==14 else "BMW",model=f"Model {index}",year=2020,price=100+index,mileage_km=index,transmission="Auto",fuel_type="Petrol",condition="Pre-owned",location="Lagos",description="Stock",publication_status=Vehicle.Publication.DRAFT)
        first=self.client.get("/api/v1/staff/vehicles/",**self.headers())
        self.assertEqual(first.status_code,200); self.assertEqual(first.data["count"],16); self.assertEqual(len(first.data["results"]),12); self.assertEqual(first.data["pages"],2)
        filtered=self.client.get("/api/v1/staff/vehicles/?q=Honda&publication=draft",**self.headers())
        self.assertEqual(filtered.data["count"],1); self.assertEqual(filtered.data["results"][0]["slug"],"stock-14")
    def test_staff_update_versions_and_queues_event(self):
        self.login(); response=self.client.patch(f"/api/v1/staff/vehicles/{self.car.id}/",{"price":"550.00"},format="json",**self.headers())
        self.assertEqual(response.status_code,200); self.assertEqual(response.data["version"],2); self.assertTrue(OutboxEvent.objects.filter(aggregate_id=self.car.id,aggregate_version=2).exists())
