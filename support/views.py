from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import DisputeForm
from .models import Dispute

# Sementara: pakai login admin. Ganti ke halaman login Sena kalau sudah ada.
LOGIN_URL = "/admin/login/"


@login_required(login_url=LOGIN_URL)
def dispute_create(request):
    if request.method == "POST":
        form = DisputeForm(request.POST)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.reporter = request.user
            dispute.save()
            messages.success(request, "Laporan terkirim.")
            return redirect("support:dispute_list")
    else:
        form = DisputeForm()
    return render(request, "support/dispute_form.html", {"form": form})


@login_required(login_url=LOGIN_URL)
def dispute_list(request):
    disputes = Dispute.objects.filter(reporter=request.user).order_by("-created_at")
    return render(request, "support/dispute_list.html", {"disputes": disputes})
