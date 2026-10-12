"""Mandatory TOTP second factor for the admin.

After the normal password login every staff user must enter a 6-digit code from an
authenticator app. Users without a device get a QR code to set one up first.
Enabled when ADMIN_2FA=True (default: on in production, off for local DEBUG).
"""

from base64 import b32encode
from io import BytesIO

import django_otp
import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from django_otp.plugins.otp_totp.models import TOTPDevice

ADMIN_PREFIX = "/" + settings.ADMIN_URL
EXEMPT = ("login/", "logout/", "2fa/", "jsi18n/")


class AdminTwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if (
            settings.ADMIN_2FA
            and path.startswith(ADMIN_PREFIX)
            and not path[len(ADMIN_PREFIX):].startswith(EXEMPT)
            and request.user.is_authenticated
            and request.user.is_staff
            and not request.user.is_verified()
        ):
            return redirect(f"{reverse('admin_2fa')}?next={request.get_full_path()}")
        return self.get_response(request)


def _qr_svg(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=8)
    buf = BytesIO()
    img.save(buf)
    return mark_safe(buf.getvalue().decode())


@staff_member_required
def two_factor(request):
    user = request.user
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("admin:index")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse("admin:index")

    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    setup = device is None
    if setup:
        # One pending device per user; regenerated only when it's deleted.
        device, _ = TOTPDevice.objects.get_or_create(user=user, confirmed=False, defaults={"name": "Authenticator"})

    if request.method == "POST":
        token = "".join(ch for ch in request.POST.get("token", "") if ch.isdigit())
        if device.verify_token(token):
            if setup:
                device.confirmed = True
                device.save(update_fields=["confirmed"])
            django_otp.login(request, device)
            return redirect(next_url)
        messages.error(request, "Wrong or expired code. Check the time on your phone and try again.")

    context = {
        **admin.site.each_context(request),
        "has_permission": False,  # hide the nav sidebar until verified
        "title": "Set up two-factor authentication" if setup else "Two-factor authentication",
        "setup": setup,
        "next": next_url,
    }
    if setup:
        context["qr"] = _qr_svg(device.config_url)
        context["secret"] = b32encode(device.bin_key).decode().rstrip("=")
    return render(request, "admin/two_factor.html", context)
