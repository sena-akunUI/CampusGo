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
