from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "users"

urlpatterns = [
    path(
        "masuk/",
        auth_views.LoginView.as_view(
            template_name="users/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # Django 5: logout wajib lewat POST (lihat form di navbar).
    path("keluar/", auth_views.LogoutView.as_view(), name="logout"),
    path("daftar/", views.register, name="register"),
    path("profil/", views.profile, name="profile"),
]
