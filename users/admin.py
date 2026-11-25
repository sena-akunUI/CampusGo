from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Campus Information",
            {
                "fields": (
                    "faculty",
                    "phone_number",
                    "saldo",
                )
            }
        ),
    )

    readonly_fields = ("saldo",)

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "faculty",
                    "phone_number",
                )
            }
        ),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "faculty",
        "saldo",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )