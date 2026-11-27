from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="student01",
            email="student01@example.com",
            password="CampusTest123!",
            faculty="Fasilkom"
        )

        self.assertEqual(user.username, "student01")
        self.assertEqual(user.email, "student01@example.com")
        self.assertEqual(user.faculty, "Fasilkom")

        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_password_is_hashed(self):
        password = "CampusTest123!"

        user = User.objects.create_user(
            username="student02",
            email="student02@example.com",
            password=password
        )

        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))

    def test_duplicate_email(self):
        User.objects.create_user(
            username="student03",
            email="student03@example.com",
            password="CampusTest123!"
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="student04",
                    email="student03@example.com",
                    password="CampusTest123!"
                )

    def test_duplicate_username(self):
        User.objects.create_user(
            username="student05",
            email="student05@example.com",
            password="CampusTest123!"
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="student05",
                    email="student06@example.com",
                    password="CampusTest123!"
                )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminTest123!"
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_string_representation(self):
        user = User.objects.create_user(
            username="student07",
            email="student07@example.com",
            password="CampusTest123!"
        )

        self.assertEqual(str(user), "student07")


class AuthPagesTests(TestCase):
    def setUp(self):
        self.password = "CampusTest123!"
        self.user = User.objects.create_user(
            username="andi", email="andi@example.com", password=self.password
        )

    def test_home_redirects_to_board(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/orders/")

    def test_login_page_renders_with_navbar(self):
        response = self.client.get("/akun/masuk/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Masuk ke CampusGo")
        self.assertContains(response, 'href="/akun/daftar/"')

    def test_login_then_redirect_to_board(self):
        response = self.client.post(
            "/akun/masuk/", {"username": "andi", "password": self.password}
        )
        self.assertRedirects(response, "/orders/")

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post("/akun/daftar/", {
            "full_name": "Budi Santoso",
            "username": "budi",
            "email": "budi@example.com",
            "password1": "SangatRahasia123!",
            "faculty": "Teknik",
        })
        self.assertRedirects(response, "/orders/")
        budi = User.objects.get(username="budi")
        self.assertEqual(budi.get_full_name(), "Budi Santoso")
        self.assertEqual(int(self.client.session["_auth_user_id"]),
                         User.objects.get(username="budi").pk)

    def test_profile_requires_login(self):
        response = self.client.get("/akun/profil/")
        self.assertRedirects(response, "/akun/masuk/?next=/akun/profil/")

    def test_profile_update(self):
        self.client.force_login(self.user)
        response = self.client.post("/akun/profil/", {
            "full_name": "Andi Pratama", "email": "andi@example.com",
            "faculty": "Fasilkom", "phone_number": "0812",
        })
        self.assertRedirects(response, "/akun/profil/")
        self.user.refresh_from_db()
        self.assertEqual(self.user.faculty, "Fasilkom")
        self.assertEqual(self.user.get_full_name(), "Andi Pratama")

    def test_register_rejects_weak_password(self):
        response = self.client.post("/akun/daftar/", {
            "full_name": "Citra", "username": "citra", "email": "c@example.com",
            "password1": "123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="citra").exists())
        self.assertContains(response, 'aria-invalid="true"')

    def test_forms_have_autofill_attributes(self):
        login = self.client.get("/akun/masuk/").content.decode()
        self.assertIn('autocomplete="username"', login)
        self.assertIn('autocomplete="current-password"', login)
        self.assertIn('spellcheck="false"', login)
        register = self.client.get("/akun/daftar/").content.decode()
        self.assertIn('autocomplete="new-password"', register)
        self.assertIn('autocomplete="name"', register)
        self.assertIn('type="tel"', register)
        self.assertNotIn('name="password2"', register)

    def test_navbar_marks_current_page(self):
        self.client.force_login(self.user)
        page = self.client.get("/akun/profil/").content.decode()
        self.assertIn('aria-current="page"', page)
        self.assertNotIn("<details", page)

    def test_logout_via_post(self):
        self.client.force_login(self.user)
        response = self.client.post("/akun/keluar/")
        self.assertRedirects(response, "/akun/masuk/")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_link_only_for_staff(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get("/akun/profil/"), 'href="/admin/"')
        self.user.is_staff = True
        self.user.save()
        self.assertContains(self.client.get("/akun/profil/"), 'href="/admin/"')


class SeedDemoTests(TestCase):
    def test_seed_demo_runs_twice(self):
        import tempfile
        from io import StringIO
        from django.core.management import call_command
        from django.test import override_settings

        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            call_command("seed_demo", stdout=StringIO())
            call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertTrue(User.objects.get(username="admin").is_staff)
        self.assertEqual(User.objects.get(username="andi").saldo, 150_000)
