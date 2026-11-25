from django.contrib import admin
from django.utils import timezone

from .models import Dispute


@admin.action(description="Tandai sedang ditinjau")
def mark_in_review(modeladmin, request, queryset):
    queryset.filter(status=Dispute.Status.OPEN).update(
        status=Dispute.Status.IN_REVIEW
    )


@admin.action(description="Tolak laporan")
def mark_rejected(modeladmin, request, queryset):
    queryset.exclude(status=Dispute.Status.RESOLVED).update(
        status=Dispute.Status.REJECTED, resolved_at=timezone.now()
    )


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("reporter__username", "reason")
    readonly_fields = ("created_at",)
    actions = [mark_in_review, mark_rejected]