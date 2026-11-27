from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import Order

# Sementara: pakai login admin. Ganti ke halaman login Sena kalau sudah ada.
LOGIN_URL = "/admin/login/"

# Status yang dianggap "masih berjalan"; sisanya masuk riwayat.
ONGOING = [
    Order.Status.PENDING,
    Order.Status.ACCEPTED,
    Order.Status.ON_DELIVERY,
    Order.Status.DISPUTED,
]


@login_required(login_url=LOGIN_URL)
def my_orders(request):
    orders = (
        Order.objects.filter(
            Q(requester=request.user) | Q(provider=request.user)
        )
        .select_related("listing", "requester", "provider")
        .order_by("-created_at")
    )
    sections = [
        ("Pesanan berjalan", orders.filter(status__in=ONGOING)),
        ("Riwayat", orders.exclude(status__in=ONGOING)),
    ]
    return render(request, "orders/my_orders.html", {"sections": sections})