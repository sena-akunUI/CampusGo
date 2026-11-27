from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from orders.models import Order

from .forms import DisputeForm
from .models import Dispute

# Sementara: pakai login admin. Ganti ke halaman login Sena kalau sudah ada.
LOGIN_URL = "/admin/login/"


@login_required(login_url=LOGIN_URL)
def dispute_create(request):
    if request.method == "POST":
        form = DisputeForm(request.POST, user=request.user)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.reporter = request.user
            dispute.save()
            # Kalau laporan terkait pesanan, tandai pesanannya "Bermasalah".
            if dispute.order:
                dispute.order.status = Order.Status.DISPUTED
                dispute.order.save(update_fields=["status", "updated_at"])
            messages.success(request, "Laporan terkirim.")
            return redirect("support:dispute_list")
    else:
        form = DisputeForm(
            user=request.user,
            initial={"order": request.GET.get("order")},
        )
    return render(request, "support/dispute_form.html", {"form": form})


@login_required(login_url=LOGIN_URL)
def dispute_list(request):
    disputes = (
        Dispute.objects.filter(reporter=request.user)
        .select_related("order")
        .order_by("-created_at")
    )
    return render(request, "support/dispute_list.html", {"disputes": disputes})
