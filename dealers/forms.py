from django import forms
from .models import BuyerRequest, Dealer, Vehicle, VehicleImage

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["make", "model", "year", "price", "mileage_km", "transmission", "fuel_type", "condition", "location", "description", "features", "known_issues", "seller_history", "video_url", "publication_status", "availability", "is_featured"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5}), "features": forms.Textarea(attrs={"rows": 4}), "known_issues": forms.Textarea(attrs={"rows": 3}), "seller_history": forms.Textarea(attrs={"rows": 3})}
    def clean(self):
        data = super().clean()
        if data.get("availability") == Vehicle.Availability.SOLD and data.get("publication_status") == Vehicle.Publication.DRAFT:
            self.add_error("availability", "A draft cannot be marked Sold; publish or unpublish it first.")
        return data

class VehicleImageForm(forms.ModelForm):
    class Meta:
        model = VehicleImage
        fields = ["image", "alt_text", "position"]
    def clean_image(self):
        image = self.cleaned_data["image"]
        if image.size > 8 * 1024 * 1024: raise forms.ValidationError("Images must be no larger than 8 MB.")
        if image.content_type not in {"image/jpeg", "image/png", "image/webp"}: raise forms.ValidationError("Use JPEG, PNG, or WebP.")
        return image

class BuyerRequestForm(forms.ModelForm):
    consent = forms.BooleanField(label="I agree that the dealer may contact me about this request.")
    class Meta:
        model = BuyerRequest
        fields = ["kind", "name", "email", "phone", "message", "preferred_at", "offer_amount"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4}), "preferred_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}
    def clean(self):
        data = super().clean()
        if data.get("kind") == BuyerRequest.Kind.OFFER and not data.get("offer_amount"):
            self.add_error("offer_amount", "Enter the amount you would like the dealer to consider.")
        return data

class BuyerRequestStaffForm(forms.ModelForm):
    class Meta:
        model = BuyerRequest
        fields = ["status", "scheduled_for", "appointment_outcome", "offer_status", "counter_offer_amount", "staff_note"]
        widgets = {"scheduled_for": forms.DateTimeInput(attrs={"type": "datetime-local"}), "staff_note": forms.Textarea(attrs={"rows": 3})}
    def clean(self):
        data = super().clean()
        if data.get("offer_status") == BuyerRequest.OfferStatus.COUNTERED and not data.get("counter_offer_amount"):
            self.add_error("counter_offer_amount", "Enter the counteroffer amount.")
        if self.instance.kind != BuyerRequest.Kind.OFFER and data.get("offer_status") != BuyerRequest.OfferStatus.NOT_APPLICABLE:
            self.add_error("offer_status", "Offer decisions apply only to offer requests.")
        return data

class DealerForm(forms.ModelForm):
    class Meta:
        model = Dealer
        fields = ["name", "tagline", "story", "email", "phone", "whatsapp", "address", "opening_hours", "primary_color", "accent_color", "logo"]
        widgets = {"story": forms.Textarea(attrs={"rows": 5}), "address": forms.Textarea(attrs={"rows": 3}), "primary_color": forms.TextInput(attrs={"type": "color"}), "accent_color": forms.TextInput(attrs={"type": "color"})}
