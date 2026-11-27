"""Satu-satunya definisi "admin" di CampusGo: user.is_staff.

Pakai ini di app lain, jangan bikin pengecekan role sendiri:
    from users.permissions import admin_required        # function-based view
    from users.permissions import AdminRequiredMixin    # class-based view
"""
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin


def is_admin(user):
    return user.is_authenticated and user.is_staff


admin_required = user_passes_test(is_admin, login_url="users:login")


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)
