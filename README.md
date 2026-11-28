# CampusGo

Aplikasi web **jastip dan titip-beli di lingkungan kampus**, dibuat untuk tugas kelompok mata kuliah Dasar-Dasar Pemrograman (DDP1) Fasilkom UI, **Kelompok 17**. Mahasiswa bisa memasang permintaan ("tolong belikan / ambilkan") atau membuka slot jastip ("aku lewat sini, boleh titip"), lalu pesanan dipantau sampai selesai. Jika ada masalah, admin bisa menengahi.

Dibangun dengan **Django 5.2**, database SQLite untuk pengembangan, dan Tailwind CSS (via CDN) untuk tampilan.

## Link

- Repositori: https://github.com/sena-akunUI/CampusGo
- Website publik: _(diisi setelah proses deploy)_

## Fitur

| Fitur | Keterangan | Status |
|---|---|---|
| Akun | Daftar, login, logout, profil (fakultas, nomor HP, saldo) | Selesai |
| Papan (beranda) | Dua mode: **Request** (cari yang mau membelikan) dan **Jastip** (buka slot titipan), dengan pencarian lokasi asal/tujuan | Selesai |
| Buat postingan | Pengguna membuat request atau slot jastip beserta upah | Selesai |
| Ambil / Titip | Mengambil request atau menitip pada slot jastip, otomatis membuat pesanan | Selesai |
| My Order | Daftar pesanan berjalan dan riwayat, dengan aksi **Mulai antar**, **Selesai**, dan **Batalkan** | Selesai |
| Top-up saldo | Pengguna mengunggah bukti transfer, admin memverifikasi manual | Selesai |
| Lapor masalah | Pengguna melaporkan masalah pada pesanan, pesanan ditandai "Bermasalah" | Selesai |
| Panel admin | Mengelola pengguna, postingan, pesanan, top-up, dan laporan (ubah status, catat keputusan) | Selesai |
| Escrow (dana ditahan) | Dana pemesan ditahan saat pesanan diterima, dilepas saat selesai, dikembalikan saat batal atau refund | Dalam pengerjaan |
| Mediasi admin | Aksi refund / release dana pada laporan | Menunggu escrow |

## Teknologi

- Python 3 dan Django 5.2
- SQLite (pengembangan), PostgreSQL siap dipakai lewat `psycopg2-binary`
- Pillow (unggah gambar bukti transfer)
- Tailwind CSS v4 via CDN dan font Plus Jakarta Sans
- Gunicorn dan WhiteNoise (persiapan deploy)

## Struktur proyek

```
CampusGo/          pengaturan proyek (settings, urls utama)
templates/         base.html dan komponen bersama (navbar, field form)
users/             akun: model User kustom, login, daftar, profil, data demo
orders/            papan, postingan (Listing), pesanan (Order), My Order
payments/          top-up saldo dan transaksi
support/           laporan masalah (Dispute) dan penanganannya di admin
manage.py
requirements.txt
```

## Cara menjalankan di komputer sendiri (Windows)

1. Clone repositori dan masuk ke foldernya:
   ```
   git clone https://github.com/sena-akunUI/CampusGo.git
   cd CampusGo
   ```
2. Buat dan aktifkan virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Pasang dependensi:
   ```
   python -m pip install -r requirements.txt
   ```
4. Siapkan database:
   ```
   python manage.py migrate
   ```
5. (Opsional) Isi data demo:
   ```
   python manage.py seed_demo
   ```
6. Jalankan server:
   ```
   python manage.py runserver
   ```
7. Buka http://127.0.0.1:8000/ di browser.

### Akun demo

Setelah `seed_demo`, semua akun memakai password `campusgo123`:

| Username | Peran |
|---|---|
| `andi`, `budi`, `citra` | Pengguna biasa |
| `admin` | Admin (akses ke `/admin/`) |

Untuk membuat admin sendiri: `python manage.py createsuperuser`.

## Halaman utama

| Alamat | Fungsi |
|---|---|
| `/orders/` | Papan: lihat dan ambil postingan |
| `/orders/baru/` | Buat postingan |
| `/orders/saya/` | My Order |
| `/payments/topup/` | Ajukan top-up saldo |
| `/support/` | Daftar laporan saya |
| `/support/baru/` | Lapor masalah |
| `/akun/masuk/` | Login |
| `/admin/` | Panel admin |

## Alur pesanan

1. Pembuat memasang postingan (Request atau Jastip).
2. Orang lain menekan **Ambil** (Request) atau **Titip** (Jastip), maka pesanan dibuat berstatus **Diterima**.
3. Penyedia menekan **Mulai antar**, status menjadi **Dalam perjalanan**.
4. Pemesan menekan **Selesai**, status menjadi **Selesai**.
5. Pesanan yang belum berjalan bisa **Dibatalkan**. Jika ada masalah, pengguna menekan **Laporkan masalah** dan admin memprosesnya.

## Menjalankan tes

```
python manage.py test
```

## Pembagian tugas (Kelompok 17)

| Anggota | Bagian |
|---|---|
| Sena | App `users`, template dasar, login |
| Tito | App `payments` (top-up dan escrow) |
| Zaki | App `orders` |
| Kezia | App `support`, Django Admin, tampilan dan QA, serta melanjutkan sebagian `orders` |

## Catatan pengembangan

- Satu fitur satu branch, lalu Pull Request ke `main`. Jangan push langsung ke `main`.
- Jalankan `git pull origin main` sebelum mulai bekerja.
- `db.sqlite3` dan folder `media/` tidak ikut di Git.