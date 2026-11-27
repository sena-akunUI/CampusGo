from django import forms

from .models import Listing


class ListingForm(forms.ModelForm):
    fee = forms.DecimalField(
        label="Upah / fee (Rp)", min_value=0, max_digits=10, decimal_places=2
    )

    class Meta:
        model = Listing
        fields = ["type", "origin", "destination", "description", "fee"]
        labels = {
            "type": "Jenis",
            "origin": "Lokasi asal",
            "destination": "Lokasi tujuan",
            "description": "Deskripsi",
        }
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}