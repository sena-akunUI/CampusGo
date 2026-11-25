from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("topup/", views.topup_create, name="topup_create"),
    path("topup/riwayat/", views.topup_history, name="topup_history"),
]