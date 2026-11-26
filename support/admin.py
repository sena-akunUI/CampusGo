from django.contrib import admin
from django.utils import timezone

from .models import Dispute


@admin.action(description="Tandai sedang ditinjau")
def mark_in_review(modeladmin, request, queryset):
    queryset.filter(status=Dispute.Status.OPEN).update(
        status=Dispute.Status.IN_REVIEW
    )


@admin.action(description="Tandai selesai")
def mark_resolved(modeladmin, request, queryset):
    queryset.filter(
        status__in=[Dispute.Status.OPEN, Dispute.Status.IN_REVIEW]
    ).update(status=Dispute.Status.RESOLVED, resolved_at=timezone.now())


@admin.action(description="Tolak laporan")
def mark_rejected(modeladmin, request, queryset):
    queryset.filter(
        status__in=[Dispute.Status.OPEN, Dispute.Status.IN_REVIEW]
    ).update(status=Dispute.Status.REJECTED, resolved_at=timezone.now())


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("reporter__username", "reason")
    actions = [mark_in_review, mark_resolved, mark_rejected]

    def get_readonly_fields(self, request, obj=None):
        # Saat membuka laporan yang sudah ada, isi laporan tidak boleh diubah admin.
        if obj:
            return ("reporter", "category", "reason", "created_at", "resolved_at")
        return ("created_at",)

    def save_model(self, request, obj, form, change):
        # Kalau admin mengubah status ke selesai/ditolak lewat form, isi waktunya otomatis.
        final = (Dispute.Status.RESOLVED, Dispute.Status.REJECTED)
        if obj.status in final and obj.resolved_at is None:
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)