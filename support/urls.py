from django.urls import path

from . import views

app_name = "support"

urlpatterns = [
    path("", views.dispute_list, name="dispute_list"),
    path("baru/", views.dispute_create, name="dispute_create"),
]