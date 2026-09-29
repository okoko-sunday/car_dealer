from rest_framework import serializers
from django.conf import settings
from dealers.models import BuyerRequest, Dealer, Vehicle, VehicleImage

class DealerSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    class Meta:
        model = Dealer
        fields = ["id","slug","name","tagline","story","email","phone","whatsapp","address","opening_hours","primary_color","accent_color","logo_url","version"]
    def get_logo_url(self, obj):
        return f"{settings.PUBLIC_API_URL.rstrip('/')}{obj.logo.url}" if obj.logo and settings.PUBLIC_API_URL else (self.context["request"].build_absolute_uri(obj.logo.url) if obj.logo else None)

class VehicleImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = VehicleImage
        fields = ["id","url","alt_text","position"]
    def get_url(self, obj):
        return f"{settings.PUBLIC_API_URL.rstrip('/')}{obj.image.url}" if settings.PUBLIC_API_URL else self.context["request"].build_absolute_uri(obj.image.url)

class VehicleSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField()
    images = VehicleImageSerializer(many=True, read_only=True)
    features = serializers.SerializerMethodField()
    class Meta:
        model = Vehicle
        fields = ["id","slug","title","make","model","year","price","mileage_km","transmission","fuel_type","condition","location","description","features","known_issues","seller_history","video_url","publication_status","availability","is_featured","version","published_at","created_at","updated_at","images"]
    def get_features(self,obj): return obj.feature_list

class VehicleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["make","model","year","price","mileage_km","transmission","fuel_type","condition","location","description","features","known_issues","seller_history","video_url","publication_status","availability","is_featured"]

class BuyerRequestCreateSerializer(serializers.ModelSerializer):
    consent = serializers.BooleanField(write_only=True)
    class Meta:
        model = BuyerRequest
        fields = ["kind","name","email","phone","message","preferred_at","offer_amount","consent"]
    def validate(self, data):
        if data.get("kind") == BuyerRequest.Kind.OFFER and not data.get("offer_amount"):
            raise serializers.ValidationError({"offer_amount":"An offer amount is required."})
        return data

class BuyerRequestSerializer(serializers.ModelSerializer):
    vehicle_title = serializers.CharField(source="vehicle.title", read_only=True)
    class Meta:
        model = BuyerRequest
        fields = ["id","vehicle","vehicle_title","kind","status","name","email","phone","message","preferred_at","offer_amount","counter_offer_amount","offer_status","scheduled_for","appointment_outcome","staff_note","created_at","updated_at"]
        read_only_fields = ["id","vehicle","vehicle_title","kind","name","email","phone","message","preferred_at","offer_amount","created_at","updated_at"]
