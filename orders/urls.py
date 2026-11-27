from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.listing_list, name="listing_list"),
    path("baru/", views.listing_create, name="listing_create"),
    path("saya/", views.my_orders, name="my_orders"),
    path("<int:pk>/ambil/", views.listing_take, name="listing_take"),
    path("pesanan/<int:pk>/<str:action>/", views.order_action, name="order_action"),
]