from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw
from dealers.models import Dealer, DealerDomain, Membership, Vehicle, VehicleImage
from dealers.services import record_dealer_change, record_vehicle_change

class Command(BaseCommand):
    help = "Create clearly labelled development fixtures."
    def handle(self, *args, **options):
        dealer, created = Dealer.objects.get_or_create(slug="atelier-motors", defaults={"name":"Atelier Motors","tagline":"Remarkable cars, honestly presented.","story":"We choose character over spectacle. Every listing gives buyers useful details, known imperfections, and room to make a considered decision.","email":"hello@example.test","phone":"+234 800 000 0000","whatsapp":"+234 800 000 0000","address":"12 Admiralty Way, Lekki, Lagos","opening_hours":"Mon–Sat · 9:00–18:00","primary_color":"#B94D2D","accent_color":"#E4BD75"})
        DealerDomain.objects.get_or_create(hostname="atelier.localhost", defaults={"dealer":dealer,"is_primary":True})
        User = get_user_model(); user, _ = User.objects.get_or_create(username="owner", defaults={"email":"owner@example.test","first_name":"Ada"})
        user.set_password("demo-pass-2026"); user.save()
        Membership.objects.get_or_create(dealer=dealer, user=user, defaults={"role":Membership.Role.OWNER})
        if created: record_dealer_change(dealer, user, created=True)
        fixtures = [("Lexus","RX 350",2022,68500000,32200,True,"#24333b"),("Mercedes-Benz","GLE 450",2021,97500000,48100,True,"#745c4f"),("Toyota","Land Cruiser Prado",2020,79000000,59300,False,"#646e5d"),("Porsche","Macan S",2019,73500000,55700,False,"#5c2630")]
        for make,model,year,price,mileage,featured,color in fixtures:
            slug=f"{year}-{make}-{model}".lower().replace(" ","-")
            car, added = Vehicle.objects.get_or_create(dealer=dealer, slug=slug, defaults={"make":make,"model":model,"year":year,"price":price,"mileage_km":mileage,"transmission":"Automatic","fuel_type":"Petrol","condition":"Dealer-described: pre-owned","location":"Lekki, Lagos","description":"A development fixture ready to be replaced with an accurately described dealer vehicle.","features":"Leather interior\nReverse camera\nClimate control\nBluetooth audio","known_issues":"Minor age-related marks may be present; request the latest walk-around.","seller_history":"Imported pre-owned. Supporting documents available for in-person review.","publication_status":Vehicle.Publication.PUBLISHED,"availability":Vehicle.Availability.AVAILABLE,"is_featured":featured})
            if added:
                record_vehicle_change(car,user,"vehicle.created")
                image=Image.new("RGB",(1400,900),color); draw=ImageDraw.Draw(image); draw.rounded_rectangle((180,300,1220,650),70,fill="#d7d0c4"); draw.ellipse((280,570,500,790),fill="#171713"); draw.ellipse((900,570,1120,790),fill="#171713"); draw.text((70,70),f"DEVELOPMENT FIXTURE · {car.title}",fill="#f5f1e9")
                output=BytesIO(); image.save(output,"JPEG",quality=88)
                VehicleImage.objects.create(vehicle=car,alt_text=f"Development placeholder illustration for {car.title}",position=0,image=ContentFile(output.getvalue(),name=f"{slug}.jpg"))
        self.stdout.write(self.style.SUCCESS("Demo ready: owner / demo-pass-2026 (development only)"))
