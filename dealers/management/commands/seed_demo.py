from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from dealers.models import Dealer, DealerDomain, Membership, Vehicle, VehicleImage
from dealers.services import record_dealer_change, record_vehicle_change

class Command(BaseCommand):
    help = "Create clearly labelled development fixtures."
    def handle(self, *args, **options):
        dealer, created = Dealer.objects.get_or_create(slug="atelier-motors", defaults={"name":"Atelier Motors","tagline":"Considered cars. Clear conversations.","story":"We source distinctive vehicles for people who care about the details. Every listing is presented with useful context, known imperfections, and the space to make a considered decision.","email":"hello@example.test","phone":"+234 800 000 0000","whatsapp":"+234 800 000 0000","address":"12 Admiralty Way, Lekki, Lagos","opening_hours":"Monday–Saturday · 09:00–18:00","primary_color":"#B64A2B","accent_color":"#C6A66A"})
        DealerDomain.objects.get_or_create(hostname="atelier.localhost", defaults={"dealer":dealer,"is_primary":True})
        User=get_user_model(); user,_=User.objects.get_or_create(username="owner",defaults={"email":"owner@example.test","first_name":"Ada"}); user.set_password("demo-pass-2026"); user.save()
        Membership.objects.get_or_create(dealer=dealer,user=user,defaults={"role":Membership.Role.OWNER})
        if created: record_dealer_change(dealer,user,created=True)
        fixtures=[
            ("Lexus","RX 350",2022,68500000,32200,True,"lexus-rx.jpg"),
            ("Mercedes-Benz","GLE 450",2021,97500000,48100,True,"mercedes-gle.jpg"),
            ("Toyota","Land Cruiser Prado",2020,79000000,59300,False,"toyota-prado.jpg"),
            ("Porsche","Macan S",2019,73500000,55700,False,"porsche-macan.jpg"),
        ]
        for make,model,year,price,mileage,featured,filename in fixtures:
            slug=f"{year}-{make}-{model}".lower().replace(" ","-")
            car,added=Vehicle.objects.get_or_create(dealer=dealer,slug=slug,defaults={"make":make,"model":model,"year":year,"price":price,"mileage_km":mileage,"transmission":"Automatic","fuel_type":"Petrol","condition":"Dealer-described: pre-owned","location":"Lekki, Lagos","description":"A development fixture demonstrating the listing experience. Replace this copy and photography with accurate dealer-supplied information before launch.","features":"Leather interior\nReverse camera\nClimate control\nBluetooth audio","known_issues":"Minor age-related marks may be present; request the latest walk-around.","seller_history":"Imported pre-owned. Supporting documents available for in-person review.","publication_status":Vehicle.Publication.PUBLISHED,"availability":Vehicle.Availability.AVAILABLE,"is_featured":featured})
            if added: record_vehicle_change(car,user,"vehicle.created")
            source=Path(settings.BASE_DIR)/"fixtures"/"vehicle-photos"/filename
            image=car.images.order_by("position").first() or VehicleImage(vehicle=car,position=0)
            if source.exists():
                with source.open("rb") as handle: image.image.save(filename,File(handle),save=False)
                image.alt_text=f"Development stock photograph accompanying the sample {car.title} listing"
                image.save()
        self.stdout.write(self.style.SUCCESS("Demo ready: owner / demo-pass-2026 (development only)"))
