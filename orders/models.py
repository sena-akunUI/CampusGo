from django.conf import settings
from django.db import models


class Listing(models.Model):
    """Papan informasi: titipan (Request) atau slot jastip yang dibuka."""

    class Type(models.TextChoices):
        REQUEST = "REQUEST", "Request (cari yang mau membelikan)"
        JASTIP = "JASTIP", "Jastip (buka slot titipan)"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Terbuka"
        CLOSED = "CLOSED", "Ditutup"
        CANCELLED = "CANCELLED", "Dibatalkan"

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    description = models.TextField()
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.origin} -> {self.destination}"


class Order(models.Model):
    """Transaksi antara pemesan dan penyedia jasa untuk satu listing."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Menunggu"
        ACCEPTED = "ACCEPTED", "Diterima"
        ON_DELIVERY = "ON_DELIVERY", "Dalam perjalanan"
        COMPLETED = "COMPLETED", "Selesai"
        DISPUTED = "DISPUTED", "Bermasalah"
        CANCELLED = "CANCELLED", "Dibatalkan"

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="orders"
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_as_requester",
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_as_provider",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"