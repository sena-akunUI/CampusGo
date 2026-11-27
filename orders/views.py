from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ListingForm
from .models import Listing, Order

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


@login_required
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


@login_required
@require_POST
def listing_take(request, pk):
    """Ambil postingan Request, atau titip pada slot Jastip -> buat Order."""
    listing = get_object_or_404(Listing, pk=pk, status=Listing.Status.OPEN)
    if listing.creator == request.user:
        messages.error(request, "Kamu tidak bisa mengambil postinganmu sendiri.")
        return redirect("orders:listing_list")

    if listing.type == Listing.Type.REQUEST:
        # Pembuat postingan = pemesan; yang mengambil = penyedia jasa.
        requester, provider = listing.creator, request.user
    else:
        # Pembuat postingan = penyedia (jastip); yang menitip = pemesan.
        requester, provider = request.user, listing.creator

    Order.objects.create(
        listing=listing,
        requester=requester,
        provider=provider,
        amount=listing.fee,
        status=Order.Status.ACCEPTED,
    )
    # TODO (escrow, nunggu fungsi dari Tito): tahan dana pemesan di sini.

    # Request cuma bisa diambil satu orang; slot Jastip tetap terbuka.
    if listing.type == Listing.Type.REQUEST:
        listing.status = Listing.Status.CLOSED
        listing.save(update_fields=["status"])

    messages.success(request, "Pesanan dibuat. Pantau di My Order.")
    return redirect("orders:my_orders")


@login_required
@require_POST
def order_action(request, pk, action):
    """Ubah status pesanan: mulai antar / selesai / batal."""
    order = get_object_or_404(Order, pk=pk)
    user = request.user
    if user not in (order.requester, order.provider):
        raise PermissionDenied

    if (
        action == "mulai"
        and user == order.provider
        and order.status == Order.Status.ACCEPTED
    ):
        order.status = Order.Status.ON_DELIVERY
        text = "Pesanan dalam perjalanan."
    elif (
        action == "selesai"
        and user == order.requester
        and order.status == Order.Status.ON_DELIVERY
    ):
        order.status = Order.Status.COMPLETED
        text = "Pesanan selesai."
        # TODO (escrow, nunggu fungsi dari Tito): teruskan dana ke penyedia di sini.
    elif action == "batal" and order.status in (
        Order.Status.PENDING,
        Order.Status.ACCEPTED,
    ):
        order.status = Order.Status.CANCELLED
        text = "Pesanan dibatalkan."
        # TODO (escrow, nunggu fungsi dari Tito): kembalikan dana ke pemesan di sini.
    else:
        messages.error(request, "Aksi tidak bisa dilakukan untuk pesanan ini.")
        return redirect("orders:my_orders")

    order.save(update_fields=["status", "updated_at"])
    messages.success(request, text)
    return redirect("orders:my_orders")


@login_required
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