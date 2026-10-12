from django.contrib.auth import get_user_model
from django.test import TestCase


class UserAdminTests(TestCase):
    def test_superuser_and_partner_get_staff_flag(self):
        from django.contrib.auth.models import Group

        from accounts.models import PARTNERS_GROUP
        from accounts.roles import ensure_partner_group

        ensure_partner_group()
        User = get_user_model()
        boss = User.objects.create_superuser("boss", password="x" * 12)
        self.client.force_login(boss)
        group = Group.objects.get(name=PARTNERS_GROUP)
        for name, extra in (("admin2", {"is_superuser": "on"}), ("partner2", {"groups": [group.pk]})):
            self.client.post("/manage/accounts/user/add/", {
                "username": name, "password1": "Strong-pass-123", "password2": "Strong-pass-123", "usable_password": "true",
            })
            user = User.objects.get(username=name)
            data = {"username": name, "is_active": "on", "date_joined_0": "2026-01-01", "date_joined_1": "00:00:00", **extra}
            r = self.client.post(f"/manage/accounts/user/{user.pk}/change/", data)
            self.assertEqual(r.status_code, 302, r.content[:3000])
            user.refresh_from_db()
            self.assertTrue(user.is_staff, name)
            self.client.logout()
            self.client.post("/manage/login/", {"username": name, "password": "Strong-pass-123"})
            self.assertEqual(self.client.get("/manage/").status_code, 200)
            self.client.force_login(boss)


class LoginLockoutTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_superuser("boss", password="Right-pass-123")

    def _login(self, password, ip="203.0.113.7"):
        return self.client.post(
            "/manage/login/?next=/manage/",
            {"username": "boss", "password": password},
            HTTP_X_FORWARDED_FOR=f"1.1.1.1, {ip}",
        )

    def test_ip_locked_after_five_failures(self):
        for _ in range(4):
            self.assertEqual(self._login("wrong").status_code, 200)
        self.assertEqual(self._login("wrong").status_code, 429)
        # Even the right password is refused from that IP during the cool-off
        r = self._login("Right-pass-123")
        self.assertEqual(r.status_code, 429)
        self.assertContains(r, "Too many failed login attempts", status_code=429)

    def test_other_ip_and_real_admin_unaffected(self):
        for _ in range(5):
            self._login("wrong", ip="203.0.113.7")
        r = self._login("Right-pass-123", ip="198.51.100.20")
        self.assertRedirects(r, "/manage/", fetch_redirect_response=False)

    def test_success_resets_counter(self):
        for _ in range(4):
            self._login("wrong")
        self._login("Right-pass-123")
        self.client.logout()
        for _ in range(4):
            self.assertEqual(self._login("wrong").status_code, 200)
