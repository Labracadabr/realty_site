import shutil
import tempfile
from decimal import Decimal
from io import BytesIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from accounts.models import PARTNERS_GROUP
from accounts.roles import ensure_partner_group

from .models import Lead, Property, PropertyImage, Region, ShareLink
from .utils import video_embed_url

MEDIA = tempfile.mkdtemp()


def jpeg(name="p.jpg", size=(3000, 2000)):
    buf = BytesIO()
    Image.new("RGB", size, (90, 140, 120)).save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=MEDIA, TELEGRAM_BOT_TOKEN="")
class ListingTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.region = Region.objects.create(name="North Bali", slug="north-bali")
        self.pub = self._prop("Sea view plot", Property.Status.PUBLISHED)
        self.hidden = self._prop("Secret island", Property.Status.UNLISTED)
        self.draft = self._prop("Draft plot", Property.Status.DRAFT)

    def _prop(self, title, status, **kw):
        return Property.objects.create(
            title_en=title, status=status, region=self.region, location="Lovina",
            land_area_m2=Decimal("1500"), price_usd=Decimal("300000"), **kw
        )

    def test_ref_slug_and_numbers(self):
        self.assertEqual(self.pub.ref, "BI-001")
        self.assertEqual(self.pub.slug, "sea-view-plot")
        self.assertEqual(self.pub.area_are, Decimal("15.00"))
        self.assertEqual(self.pub.price_per_are, Decimal("20000"))

    def test_catalog_shows_only_public(self):
        r = self.client.get("/en/properties/")
        self.assertContains(r, "Sea view plot")
        self.assertNotContains(r, "Secret island")
        self.assertNotContains(r, "Draft plot")

    def test_unlisted_and_draft_hidden_by_slug(self):
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)

    def test_share_link_opens_unlisted_with_noindex_and_counts_views(self):
        link = self.hidden.default_share_link()
        r = self.client.get(f"/s/{link.token}/", HTTP_ACCEPT_LANGUAGE="tr")
        self.assertRedirects(r, f"/tr/s/{link.token}/", fetch_redirect_response=False)
        r = self.client.get(f"/tr/s/{link.token}/")
        self.assertContains(r, "Secret island")
        self.assertContains(r, 'name="robots" content="noindex')
        link.refresh_from_db()
        self.assertEqual(link.views, 1)

    def test_share_link_forced_language(self):
        link = ShareLink.objects.create(property=self.hidden, language="ru")
        r = self.client.get(f"/s/{link.token}/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(r, f"/ru/s/{link.token}/", fetch_redirect_response=False)

    def test_inactive_or_draft_share_link_is_gone(self):
        link = self.hidden.default_share_link()
        link.is_active = False
        link.save()
        self.assertEqual(self.client.get(f"/en/s/{link.token}/").status_code, 410)
        draft_link = self.draft.default_share_link()
        self.assertEqual(self.client.get(f"/en/s/{draft_link.token}/").status_code, 410)

    def test_lead_attributed_to_referral_link(self):
        partner = get_user_model().objects.create_user("p", password="x" * 12, is_staff=True)
        link = ShareLink.objects.create(property=self.hidden, owner=partner, label="Mehmet")
        self.client.get(f"/en/s/{link.token}/?utm_source=ig")
        with mock.patch("listings.views.notify_lead") as notify:
            r = self.client.post("/en/inquiry/", {
                "name": "Mehmet", "phone": "+90 555", "property_id": self.hidden.pk, "next": f"/en/s/{link.token}/",
            })
        self.assertEqual(r.status_code, 302)
        lead = Lead.objects.get()
        self.assertEqual((lead.referrer, lead.share_link, lead.property), (partner, link, self.hidden))
        self.assertEqual(lead.utm, {"utm_source": "ig"})
        self.assertEqual(lead.language, "en")
        notify.assert_called_once()

    def test_lead_requires_contact_and_honeypot_drops_bots(self):
        self.client.post("/en/inquiry/", {"name": "No contact"})
        self.client.post("/en/inquiry/", {"name": "Bot", "email": "b@x.io", "website": "spam"})
        self.assertFalse(Lead.objects.exists())

    def test_lead_redirect_not_open(self):
        r = self.client.post("/en/inquiry/", {"name": "A", "email": "a@b.co", "next": "https://evil.example/"})
        self.assertTrue(r["Location"].startswith("/en/"))

    def test_image_converted_to_webp_with_thumb(self):
        img = PropertyImage.objects.create(property=self.pub, image=jpeg())
        self.assertTrue(img.image.name.endswith(".webp"))
        self.assertTrue(img.thumb.name.endswith(".webp"))
        with Image.open(img.image.path) as im:
            self.assertEqual(max(im.size), PropertyImage.MAX_SIDE)
        with Image.open(img.thumb.path) as im:
            self.assertEqual(max(im.size), PropertyImage.THUMB_SIDE)

    def test_sitemap_and_robots(self):
        r = self.client.get("/sitemap.xml")
        self.assertContains(r, "/en/properties/sea-view-plot/")
        self.assertContains(r, 'hreflang="tr"')
        self.assertNotContains(r, "secret-island")
        self.assertContains(self.client.get("/robots.txt"), "Disallow: /s/")

    def test_language_versions(self):
        self.pub.title_ru = "Участок с видом на море"
        self.pub.save()
        self.assertContains(self.client.get("/ru/properties/sea-view-plot/"), "Участок с видом на море")
        # TR falls back to English
        self.assertContains(self.client.get("/tr/properties/sea-view-plot/"), "Sea view plot")


@override_settings(MEDIA_ROOT=MEDIA)
class AdminRoleTests(TestCase):
    def setUp(self):
        ensure_partner_group()
        User = get_user_model()
        self.admin = User.objects.create_superuser("boss", password="x" * 12)
        self.partner = User.objects.create_user("partner", password="x" * 12, is_staff=True)
        self.partner.groups.add(Group.objects.get(name=PARTNERS_GROUP))

    def test_partner_manages_listings_but_not_technical(self):
        self.client.force_login(self.partner)
        for url in ("/manage/listings/property/", "/manage/listings/property/add/", "/manage/listings/lead/",
                    "/manage/listings/sharelink/"):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for url in ("/manage/accounts/user/", "/manage/core/sitesettings/", "/manage/core/page/"):
            self.assertEqual(self.client.get(url).status_code, 403, url)

    def test_admin_sees_everything(self):
        self.client.force_login(self.admin)
        for url in ("/manage/accounts/user/", "/manage/core/page/", "/manage/listings/property/add/"):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_translate_endpoint(self):
        self.client.force_login(self.partner)
        with mock.patch("core.admin_views.translate_many", side_effect=lambda t, s, d: [f"[{d}] {x}" for x in t]):
            r = self.client.post(
                "/manage/translate/",
                data='{"source": "en", "targets": ["ru", "tr"], "fields": {"title": "Plot"}}',
                content_type="application/json",
            )
        self.assertEqual(r.json()["translations"], {"ru": {"title": "[ru] Plot"}, "tr": {"title": "[tr] Plot"}})

    def test_translate_endpoint_requires_staff(self):
        r = self.client.post("/manage/translate/", data="{}", content_type="application/json")
        self.assertEqual(r.status_code, 302)

    def test_admin_create_property_with_bulk_photos(self):
        self.client.force_login(self.partner)
        region = Region.objects.create(name="Tabanan", slug="tabanan")
        data = {
            "status": "draft", "order": 0, "title_en": "New plot", "kind": "land", "region": region.pk,
            "location": "Kedungu", "land_area_m2": "1000", "map_link": "https://www.google.com/maps?q=-8.6112,115.0874", "title_type": "shm", "zoning": "unknown",
            "upload_photos": [jpeg("a.jpg", (800, 600)), jpeg("b.jpg", (800, 600))],
        }
        for prefix in ("images", "videos", "share_links"):
            data.update({f"{prefix}-TOTAL_FORMS": 0, f"{prefix}-INITIAL_FORMS": 0})
        r = self.client.post("/manage/listings/property/add/", data)
        self.assertEqual(r.status_code, 302, r.content[:2000])
        prop = Property.objects.get(title_en="New plot")
        self.assertEqual(prop.images.count(), 2)
        self.assertEqual(prop.images.filter(is_cover=True).count(), 1)
        self.assertEqual(prop.created_by, self.partner)
        self.assertEqual((prop.latitude, prop.longitude), (Decimal("-8.611200"), Decimal("115.087400")))
        self.assertTrue(prop.share_links.exists())


class VideoUrlTests(TestCase):
    def test_embed(self):
        self.assertEqual(video_embed_url("https://youtu.be/dQw4w9WgXcQ"), "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0")
        self.assertEqual(video_embed_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1"), "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0")
        self.assertEqual(video_embed_url("https://vimeo.com/123456"), "https://player.vimeo.com/video/123456")
        self.assertIsNone(video_embed_url("https://example.com/video"))


class MapLinkTests(TestCase):
    LOVINA = (Decimal("-8.172400"), Decimal("115.019800"))

    def test_formats_without_network(self):
        from .geo import coords_from_map_link

        cases = [
            # place link: exact pin (!3d!4d) wins over the viewport centre (@)
            "https://www.google.com/maps/place/Lovina/@-8.1600,115.0000,15z/data=!3m1!4b1!4m6!3m5!1s0x0:0x0!8m2!3d-8.1724!4d115.0198",
            "https://www.google.com/maps/@-8.1724,115.0198,17z",
            "https://www.google.com/maps?q=-8.1724,115.0198",
            "https://maps.google.com/?q=loc:-8.1724,115.0198",
            "https://www.google.com/maps/search/?api=1&query=-8.1724%2C115.0198",
            "https://www.google.co.id/maps/search/-8.1724,+115.0198?entry=ttu",
            "https://www.google.com/maps/dir//-8.1724,115.0198",
            "-8.1724, 115.0198",
            "-8.1724,115.0198",
            "8°10'20.6\"S 115°01'11.3\"E",
        ]
        for link in cases:
            lat, lng = coords_from_map_link(link)
            self.assertAlmostEqual(float(lat), -8.1724, places=3, msg=link)
            self.assertAlmostEqual(float(lng), 115.0198, places=3, msg=link)

    def test_short_link_followed_through_google_only(self):
        from .geo import MapLinkError, coords_from_map_link

        def fake_get(url, **kw):
            resp = mock.Mock(is_redirect=True, status_code=302, text="")
            if "maps.app.goo.gl" in url:
                resp.headers = {"Location": "https://www.google.com/maps/place/X/data=!3d-8.1724!4d115.0198"}
            else:
                resp.headers = {"Location": "https://evil.example/"}
            return resp

        with mock.patch("listings.geo.requests.Session.get", side_effect=fake_get):
            lat, lng = coords_from_map_link("https://maps.app.goo.gl/AbCdEf123")
            self.assertAlmostEqual(float(lat), -8.1724, places=4)
            with self.assertRaises(MapLinkError):
                coords_from_map_link("https://evil.example/maps")

    def test_page_pin_trusted_but_viewport_centre_ignored(self):
        from .geo import MapLinkError, coords_from_map_link

        page = mock.Mock(is_redirect=False, status_code=200, headers={}, text='...data=!3d-8.1724!4d115.0198...')
        with mock.patch("listings.geo.requests.Session.get", return_value=page):
            lat, _ = coords_from_map_link("https://www.google.com/maps/place/Some+Villa")
        self.assertAlmostEqual(float(lat), -8.1724, places=4)

        # Place-name-only page: just the IP-based default viewport -> must not be used
        page.text = "...staticmap?center=-8.6966%2C115.2319&zoom=11..."
        with mock.patch("listings.geo.requests.Session.get", return_value=page):
            with self.assertRaises(MapLinkError):
                coords_from_map_link("https://www.google.com/maps/place/Lovina+Beach")

    def test_garbage_rejected(self):
        from .geo import MapLinkError, coords_from_map_link

        for bad in ("hello", "0,0", "-95.1, 115.2"):
            with self.assertRaises(MapLinkError, msg=bad):
                coords_from_map_link(bad)
