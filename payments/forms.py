from django import forms

from .models import TopUpRequest


class TopUpForm(forms.ModelForm):
    class Meta:
        model = TopUpRequest
        fields = ["amount", "proof_image"]

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount < 10000:
            raise forms.ValidationError("Minimal top-up Rp10.000.")
        return amount