from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice


def current_code(device):
    return f"{totp(device.bin_key, device.step, device.t0, device.digits, device.drift):06d}"


@override_settings(ADMIN_2FA=True)
class TwoFactorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("boss", password="x" * 12)
        self.client.force_login(self.user)

    def test_admin_redirects_to_setup_until_verified(self):
        r = self.client.get("/manage/listings/property/")
        self.assertRedirects(r, "/manage/2fa/?next=/manage/listings/property/", fetch_redirect_response=False)
        r = self.client.get("/manage/2fa/")
        self.assertContains(r, 'class="qr"')
        self.assertEqual(self.client.post("/manage/translate/", data="{}", content_type="application/json").status_code, 302)

    def test_setup_then_access(self):
        self.client.get("/manage/2fa/")
        device = TOTPDevice.objects.get(user=self.user, confirmed=False)
        r = self.client.post("/manage/2fa/", {"token": "000000", "next": "/manage/"})
        self.assertEqual(r.status_code, 200)  # wrong code -> stays on page
        device.refresh_from_db()
        device.throttling_failure_count = 0
        device.throttling_failure_timestamp = None
        device.save()
        r = self.client.post("/manage/2fa/", {"token": current_code(device), "next": "/manage/listings/property/"})
        self.assertRedirects(r, "/manage/listings/property/", fetch_redirect_response=False)
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
        self.assertEqual(self.client.get("/manage/listings/property/").status_code, 200)

    def test_existing_device_asks_code_without_qr(self):
        TOTPDevice.objects.create(user=self.user, name="phone", confirmed=True)
        r = self.client.get("/manage/2fa/")
        self.assertNotContains(r, 'class="qr"')

    def test_public_site_unaffected(self):
        self.assertEqual(self.client.get("/en/").status_code, 200)

    def test_open_redirect_blocked(self):
        device = TOTPDevice.objects.create(user=self.user, name="phone", confirmed=True)
        r = self.client.post("/manage/2fa/", {"token": current_code(device), "next": "https://evil.example/"})
        self.assertEqual(r["Location"], "/manage/")


@override_settings(ADMIN_2FA=False)
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
            self.assertTrue(self.client.login(username=name, password="Strong-pass-123"))
            self.assertEqual(self.client.get("/manage/").status_code, 200)
            self.client.force_login(boss)
