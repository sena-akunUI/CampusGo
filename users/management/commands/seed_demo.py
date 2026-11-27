"""Isi database dengan akun & data demo.

    python manage.py seed_demo          # buat / perbarui data demo
    python manage.py seed_demo --reset  # hapus data demo lama lalu buat ulang

Semua akun demo memakai password yang sama (lihat DEMO_PASSWORD).
"""
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from orders.models import Listing, Order
from payments.models import TopUpRequest
from support.models import Dispute

User = get_user_model()
DEMO_PASSWORD = "campusgo123"

# username, nama depan, nama belakang, fakultas, saldo awal, admin?
DEMO_USERS = [
    ("andi", "Andi", "Pratama", "Fasilkom", 150_000, False),
    ("budi", "Budi", "Santoso", "Teknik", 50_000, False),
    ("citra", "Citra", "Lestari", "FEB", 80_000, False),
    ("admin", "Admin", "CampusGo", "", 0, True),
]

# pembuat, jenis, asal, tujuan, deskripsi, fee
DEMO_LISTINGS = [
    ("andi", "REQUEST", "Kantin Fasilkom", "Asrama UI", "Titip nasi ayam geprek level 2 + es teh manis.", 5000),
    ("citra", "REQUEST", "Perpustakaan Pusat", "FEB", "Tolong ambilkan buku pinjaman atas nama Citra di loket.", 7000),
    ("andi", "REQUEST", "Stasiun UI", "Fasilkom", "Beliin kopi susu gula aren 2 cup dari kedai depan stasiun.", 6000),
    ("budi", "JASTIP", "Margonda / Detos", "Teknik", "Jam 4 sore ke Detos, bisa titip makanan/ATK. Maks 3 titipan.", 5000),
    ("citra", "JASTIP", "Pondok Cina", "Balairung", "Lewat Pocin tiap pagi, terima titip sarapan.", 4000),
]


def tiny_png():
    """Gambar placeholder untuk bukti transfer top-up."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (480, 300), "#ecfdf5")
    ImageDraw.Draw(img).text((24, 24), "BUKTI TRANSFER (DEMO)\nRp 100.000", fill="#047857")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name="bukti_demo.png")


class Command(BaseCommand):
    help = "Buat akun & data demo CampusGo. --reset untuk hapus data demo lama."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Hapus data demo lama dulu.")

    @transaction.atomic
    def handle(self, *args, **opts):
        usernames = [u[0] for u in DEMO_USERS]
        if opts["reset"]:
            # CASCADE ikut menghapus listing, order, top-up, dan laporan milik akun demo.
            User.objects.filter(username__in=usernames).delete()
            self.stdout.write(self.style.WARNING("Data demo lama dihapus."))

        users = {}
        for username, first, last, faculty, saldo, is_admin in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@campusgo.test"},
            )
            user.first_name, user.last_name, user.faculty = first, last, faculty
            user.saldo = saldo
            user.is_staff = user.is_superuser = is_admin
            user.set_password(DEMO_PASSWORD)
            user.save()
            users[username] = user

        if Listing.objects.filter(creator__username__in=usernames).exists():
            self.stdout.write("Postingan demo sudah ada (pakai --reset untuk buat ulang).")
        else:
            listings = [
                Listing.objects.create(
                    creator=users[c], type=t, origin=o, destination=d, description=desc, fee=fee
                )
                for c, t, o, d, desc, fee in DEMO_LISTINGS
            ]
            # Pesanan di berbagai status, supaya halaman My Order tidak kosong.
            geprek, buku, _, detos, _ = listings
            geprek.status = buku.status = Listing.Status.CLOSED
            geprek.save(update_fields=["status"])
            buku.save(update_fields=["status"])

            Order.objects.create(listing=geprek, requester=users["andi"], provider=users["budi"],
                                 amount=geprek.fee, status=Order.Status.ON_DELIVERY)
            Order.objects.create(listing=detos, requester=users["andi"], provider=users["budi"],
                                 amount=detos.fee, status=Order.Status.COMPLETED)
            disputed = Order.objects.create(listing=buku, requester=users["citra"], provider=users["budi"],
                                            amount=buku.fee, status=Order.Status.DISPUTED)

            # Satu laporan menunggu keputusan admin -> bahan demo mediasi.
            Dispute.objects.create(
                reporter=users["citra"], order=disputed, category=Dispute.Category.NO_RESPONSE,
                reason="Sudah 2 jam kurir tidak membalas chat dan buku belum diantar.",
            )
            # Satu top-up menunggu verifikasi admin.
            TopUpRequest.objects.create(user=users["andi"], amount=100_000, proof_image=tiny_png())

        self.stdout.write(self.style.SUCCESS("\nAkun demo siap (password semua: %s)" % DEMO_PASSWORD))
        for username, *_rest, is_admin in DEMO_USERS:
            self.stdout.write(f"  - {username:<6} {'(admin)' if is_admin else ''}")
