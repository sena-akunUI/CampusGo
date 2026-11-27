from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.listing_list, name="listing_list"),
    path("baru/", views.listing_create, name="listing_create"),
    path("saya/", views.my_orders, name="my_orders"),
]