from django.conf import settings
from django.db import models


class Dispute(models.Model):
    class Category(models.TextChoices):
        WRONG_ITEM = "WRONG_ITEM", "Pesanan tidak sesuai"
        DAMAGED = "DAMAGED", "Barang rusak"
        NO_RESPONSE = "NO_RESPONSE", "Pihak lain tidak bertanggung jawab"
        OTHER = "OTHER", "Lainnya"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Menunggu"
        IN_REVIEW = "IN_REVIEW", "Sedang ditinjau"
        RESOLVED = "RESOLVED", "Selesai"
        REJECTED = "REJECTED", "Ditolak"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="disputes",
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    admin_decision = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dispute #{self.pk} oleh {self.reporter} ({self.get_status_display()})"