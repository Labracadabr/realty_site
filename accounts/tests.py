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
