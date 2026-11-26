from django.contrib import admin

from .models import Listing, Order


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "creator", "origin", "destination", "fee", "status")
    list_filter = ("type", "status")
    search_fields = ("origin", "destination", "description")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "requester", "provider", "amount", "status")
    list_filter = ("status",)