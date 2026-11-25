from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import TopUpForm
from .models import TopUpRequest


@login_required
def topup_create(request):
    if request.method == "POST":
        form = TopUpForm(request.POST, request.FILES)
        if form.is_valid():
            topup = form.save(commit=False)
            topup.user = request.user
            topup.save()
            messages.success(request, "Top-up dikirim, menunggu verifikasi admin.")
            return redirect("payments:topup_history")
    else:
        form = TopUpForm()
    return render(request, "payments/topup_form.html", {"form": form})


@login_required
def topup_history(request):
    topups = TopUpRequest.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "payments/topup_history.html", {"topups": topups})