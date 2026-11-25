from django.conf import settings
from django.db import models


class TopUpRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Menunggu"
        APPROVED = "APPROVED", "Disetujui"
        REJECTED = "REJECTED", "Ditolak"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topup_requests",
    )
    amount = models.PositiveIntegerField()
    proof_image = models.ImageField(upload_to="topup_proofs/")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TopUp {self.user} - Rp{self.amount} ({self.status})"

class Transaction(models.Model):
    class Type(models.TextChoices):
        TOPUP = "TOPUP", "Top-up"
        HOLD = "HOLD", "Dana ditahan"
        RELEASE = "RELEASE", "Dana diteruskan"
        REFUND = "REFUND", "Dana dikembalikan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.user} - Rp{self.amount}"