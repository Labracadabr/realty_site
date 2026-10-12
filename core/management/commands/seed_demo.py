import math
import random
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFilter

from accounts.models import PARTNERS_GROUP
from accounts.roles import ensure_partner_group
from core.management import demo_data as D
from core.models import Page, Service, SiteSettings
from listings.models import Property, PropertyImage, Region, ShareLink

LANGS = ("en", "ru", "tr")


def tr(obj, field, values):
    for lang in LANGS:
        setattr(obj, f"{field}_{lang}", values.get(lang, ""))


def demo_image(palette, variant, size=(1600, 1100)):
    """Painterly placeholder: sky gradient, sun, layered hills/sea."""
    w, h = size
    sky_top, sky_bottom, mid, fg = palette
    rnd = random.Random(variant * 7919 + sum(sky_top))
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    horizon = int(h * (0.48 + 0.1 * rnd.random()))
    for y in range(h):
        t = min(y / horizon, 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip(sky_top, sky_bottom))
        draw.line([(0, y), (w, y)], fill=c)
    sx, sy = int(w * (0.25 + 0.5 * rnd.random())), int(horizon * (0.55 + 0.3 * rnd.random()))
    for r, alpha in ((180, 40), (110, 70), (55, 255)):
        overlay = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 241, 210, alpha))
        img.paste(overlay, (0, 0), overlay)
    draw = ImageDraw.Draw(img)

    def ridge(base_y, amp, color, freq):
        phase = rnd.random() * 6.28
        pts = [(0, h)]
        for x in range(0, w + 20, 20):
            y = base_y + amp * math.sin(x / w * freq * 6.28 + phase) + amp * 0.4 * math.sin(x / w * freq * 15 + phase)
            pts.append((x, y))
        pts.append((w, h))
        draw.polygon(pts, fill=color)

    shade = lambda c, k: tuple(max(0, min(255, int(v * k))) for v in c)  # noqa: E731
    ridge(horizon - 40, 30, shade(mid, 1.15), 1.3)
    ridge(horizon + 10, 18, mid, 2.1)
    ridge(horizon + 140 + 40 * variant, 60, fg, 0.9 + variant * 0.3)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    draw = ImageDraw.Draw(img)
    draw.text((28, h - 46), "DEMO PHOTO — replace in admin", fill=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, "JPEG", quality=88)
    return ContentFile(buf.getvalue(), name=f"demo-{variant}.jpg")


class Command(BaseCommand):
    help = "Create demo content and local test accounts (DEBUG only)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing properties first")
        parser.add_argument(
            "--content-only",
            action="store_true",
            help="Production-safe: only create missing pages, services, regions and home texts. "
            "No demo objects, no test users, never overwrites existing content.",
        )

    def handle(self, *args, reset=False, content_only=False, **opts):
        if not settings.DEBUG and not content_only:
            raise CommandError("Full demo seed is for local development only. On production use --content-only.")

        ensure_partner_group()
        if not content_only:
            admin_user, partner = self._users()
            if reset:
                Property.objects.all().delete()

        fresh_site = not SiteSettings.objects.exists()
        site = SiteSettings.load()
        if not content_only:
            for key in ("brand", "legal_name", "address", "email", "whatsapp", "telegram"):
                setattr(site, key, D.SITE[key])
        if fresh_site or not content_only:
            for key in ("hero_title", "hero_subtitle", "stats"):
                tr(site, key, D.SITE[key])
            site.save()

        regions = {}
        for i, (slug, names) in enumerate(D.REGIONS):
            region, created = Region.objects.get_or_create(slug=slug, defaults={"order": i, "name": names["en"]})
            if created or not content_only:
                tr(region, "name", names)
                region.save()
            regions[slug] = region

        if not Service.objects.exists():
            for i, (icon, data) in enumerate(D.SERVICES):
                s = Service(icon=icon, order=i)
                tr(s, "title", data["title"])
                tr(s, "summary", data["summary"])
                s.save()

        for slug, data in (("about", D.ABOUT), ("how-to-buy", D.HOW_TO_BUY), *D.LEGAL_PAGES.items()):
            page, created = Page.objects.get_or_create(slug=slug, defaults={"title": data["title"]["en"]})
            if content_only and not created:
                continue
            for field in ("title", "lead", "body"):
                if field in data:
                    tr(page, field, data[field])
            page.save()

        if content_only:
            self.stdout.write(self.style.SUCCESS("Base content ready (pages, services, regions)."))
            return

        for i, data in enumerate(D.PROPERTIES):
            if Property.objects.filter(title_en=data["title"]["en"]).exists():
                continue
            p = Property(
                region=regions[data["region"]],
                kind=data["kind"],
                status=data["status"],
                featured=data["featured"],
                order=i,
                location=data["location"],
                latitude=Decimal(data["lat"]),
                longitude=Decimal(data["lng"]),
                land_area_m2=Decimal(data["area"]),
                price_usd=Decimal(data["price"]) if data["price"] else None,
                price_on_request=data.get("on_request", False),
                title_type=data["title_type"],
                lease_years=data.get("lease_years"),
                zoning=data["zoning"],
                distance_beach_km=Decimal(str(data["beach"])),
                distance_airport_km=Decimal(str(data["airport"])),
                reviewed_ru=True,
                reviewed_tr=True,
                responsible=admin_user,
                created_by=admin_user,
                **data["features"],
            )
            for field in ("title", "summary", "description", "highlights", "legal_notes"):
                if field in data:
                    tr(p, field, data[field])
            p.save()
            for v in range(4):
                PropertyImage.objects.create(
                    property=p, image=demo_image(data["palette"], v), order=v, is_cover=v == 0
                )
            p.default_share_link()
            if data["status"] == "unlisted":
                ShareLink.objects.create(property=p, owner=partner, label="for Mehmet, Istanbul (demo)", language="tr")
            self.stdout.write(f"  + {p}")

        self.stdout.write(self.style.SUCCESS("Demo content ready."))
        self.stdout.write(f"Admin panel: {settings.SITE_URL}/{settings.ADMIN_URL} (accounts from DEV_* in .env)")

    def _users(self):
        User = get_user_model()
        env = settings.BASE_DIR / ".env"
        import environ

        e = environ.Env()
        if env.exists():
            environ.Env.read_env(env)
        admin_name = e("DEV_ADMIN_USERNAME", default="admin")
        partner_name = e("DEV_PARTNER_USERNAME", default="partner")

        admin_user, created = User.objects.get_or_create(
            username=admin_name, defaults={"is_staff": True, "is_superuser": True, "first_name": "Admin"}
        )
        if created:
            admin_user.set_password(e("DEV_ADMIN_PASSWORD", default="lovina-admin-dev"))
            admin_user.save()

        partner, created = User.objects.get_or_create(
            username=partner_name, defaults={"is_staff": True, "first_name": "Demo", "last_name": "Partner"}
        )
        if created:
            partner.set_password(e("DEV_PARTNER_PASSWORD", default="lovina-partner-dev"))
            partner.save()
        partner.groups.add(Group.objects.get(name=PARTNERS_GROUP))
        return admin_user, partner
