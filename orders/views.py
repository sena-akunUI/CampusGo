from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import ListingForm
from .models import Listing, Order

# Sementara: pakai login admin. Ganti ke halaman login Sena kalau sudah ada.
LOGIN_URL = "/admin/login/"

# Status yang dianggap "masih berjalan"; sisanya masuk riwayat.
ONGOING = [
    Order.Status.PENDING,
    Order.Status.ACCEPTED,
    Order.Status.ON_DELIVERY,
    Order.Status.DISPUTED,
]


def listing_list(request):
    """Papan utama: dua mode (Request / Jastip) dengan pencarian lokasi."""
    mode = request.GET.get("mode", Listing.Type.REQUEST)
    if mode not in Listing.Type.values:
        mode = Listing.Type.REQUEST
    q = request.GET.get("q", "").strip()

    listings = Listing.objects.filter(
        type=mode, status=Listing.Status.OPEN
    ).select_related("creator")
    if q:
        listings = listings.filter(
            Q(origin__icontains=q) | Q(destination__icontains=q)
        )
    listings = listings.order_by("-created_at")

    context = {
        "listings": listings,
        "mode": mode,
        "q": q,
        "modes": Listing.Type.choices,
    }
    return render(request, "orders/listing_list.html", context)


@login_required(login_url=LOGIN_URL)
def listing_create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.save()
            messages.success(request, "Postingan berhasil dibuat.")
            return redirect("orders:listing_list")
    else:
        form = ListingForm(initial={"type": request.GET.get("mode")})
    return render(request, "orders/listing_form.html", {"form": form})


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