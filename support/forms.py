from django import forms
from django.db.models import Q

from orders.models import Order

from .models import Dispute


class DisputeForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            # Pengguna hanya bisa melaporkan pesanan yang dia ikuti
            # (sebagai pemesan atau penyedia jasa).
            self.fields["order"].queryset = Order.objects.filter(
                Q(requester=user) | Q(provider=user)
            ).distinct()
        self.fields["order"].required = False
        self.fields["order"].empty_label = "(tidak terkait pesanan)"

    class Meta:
        model = Dispute
        fields = ["order", "category", "reason"]
        labels = {
            "order": "Pesanan terkait",
            "category": "Jenis masalah",
            "reason": "Ceritakan masalahnya",
        }
        widgets = {"reason": forms.Textarea(attrs={"rows": 5})}