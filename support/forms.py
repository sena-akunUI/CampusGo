from django import forms

from .models import Dispute


class DisputeForm(forms.ModelForm):
    class Meta:
        model = Dispute
        fields = ["category", "reason"]
        labels = {
            "category": "Jenis masalah",
            "reason": "Ceritakan masalahnya",
        }
        widgets = {"reason": forms.Textarea(attrs={"rows": 5})}