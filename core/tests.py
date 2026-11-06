import json
import re
import shutil
import tempfile
from decimal import Decimal
from io import BytesIO, StringIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from listings.models import Property, Region, ShareLink

from .models import Page, SiteSettings

MEDIA = tempfile.mkdtemp()
GTM_SCRIPT = "googletagmanager.com/gtm.js?id=GTM-TEST"


def image_bytes(fmt="JPEG", mode="RGB", size=(3000, 2000)):
    buf = BytesIO()
    Image.new(mode, size, (90, 140, 120, 0)[: len(mode)]).save(buf, fmt)
    return buf.getvalue()


def json_ld(response):
    block = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)
    return json.loads(block.group(1))


class CanonicalHostTests(TestCase):
    @override_settings(SITE_URL="https://www.example.com", ALLOWED_HOSTS=["example.com", "www.example.com", "other.test"])
    def test_bare_domain_redirects_to_www_keeping_path_and_query(self):
        r = self.client.get("/en/properties/?kind=island", HTTP_HOST="example.com")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r["Location"], "https://www.example.com/en/properties/?kind=island")

    @override_settings(SITE_URL="https://www.example.com", ALLOWED_HOSTS=["example.com", "www.example.com", "other.test"])
    def test_main_domain_and_other_hosts_are_left_alone(self):
        self.assertEqual(self.client.get("/en/", HTTP_HOST="www.example.com").status_code, 200)
        self.assertEqual(self.client.get("/en/", HTTP_HOST="other.test").status_code, 200)

    @override_settings(SITE_URL="https://example.com", ALLOWED_HOSTS=["example.com", "www.example.com"])
    def test_www_redirects_when_bare_domain_is_main(self):
        r = self.client.get("/en/", HTTP_HOST="www.example.com")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r["Location"], "https://example.com/en/")


@override_settings(MEDIA_ROOT=MEDIA, GTM_ID="GTM-TEST")
class SeoPageTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        region = Region.objects.create(name="North Bali", slug="north-bali")
        self.prop = Property.objects.create(
            title_en="Sea view plot", status=Property.Status.PUBLISHED, region=region, location="Lovina",
            land_area_m2=Decimal("1500"), price_usd=Decimal("300000"),
            latitude=Decimal("-8.183972"), longitude=Decimal("114.907278"),
        )
        self.hidden = Property.objects.create(
            title_en="Secret island", status=Property.Status.UNLISTED, region=region, location="Lovina",
            land_area_m2=Decimal("1500"), price_usd=Decimal("300000"),
        )

    def test_tag_on_public_pages(self):
        self.assertContains(self.client.get("/en/"), GTM_SCRIPT)
        self.assertContains(self.client.get(self.prop.get_absolute_url()), GTM_SCRIPT)

    @override_settings(GTM_ID="")
    def test_no_tag_when_not_configured(self):
        self.assertNotContains(self.client.get("/en/"), "googletagmanager")

    def test_no_tag_on_private_share_links(self):
        link = self.hidden.default_share_link()
        r = self.client.get(f"/en/s/{link.token}/")
        self.assertContains(r, "Secret island")
        self.assertNotContains(r, "googletagmanager")

    def test_no_tag_on_expired_share_links(self):
        link = self.hidden.default_share_link()
        ShareLink.objects.filter(pk=link.pk).update(is_active=False)
        r = self.client.get(f"/en/s/{link.token}/")
        self.assertNotContains(r, "googletagmanager", status_code=410)

    def test_robots_does_not_reveal_admin_address(self):
        with override_settings(ADMIN_URL="hidden-office/"):
            r = self.client.get("/robots.txt")
        self.assertNotContains(r, "hidden-office")
        self.assertContains(r, "Disallow: /s/")

    def test_default_share_image_is_absolute_and_not_svg(self):
        for url in ("/en/", self.prop.get_absolute_url()):  # the property has no photos yet
            html = self.client.get(url).content.decode()
            image = re.search(r'property="og:image" content="([^"]+)"', html).group(1)
            self.assertTrue(image.startswith("http"), image)
            self.assertIn("og-default", image)
            self.assertTrue(image.endswith(".jpg"), image)

    def test_default_share_image_file_is_social_size(self):
        path = Path(__file__).resolve().parent.parent / "static/img/og-default.jpg"
        with Image.open(path) as im:
            self.assertEqual(im.size, (1200, 630))

    def test_structured_data_is_valid_json_in_every_language(self):
        for lang in ("en", "ru", "tr"):
            r = self.client.get(f"/{lang}/properties/sea-view-plot/")
            data = json_ld(r)
            geo = data["about"]["geo"]
            self.assertEqual(geo["latitude"], -8.183972, lang)
            self.assertEqual(geo["longitude"], 114.907278, lang)
            self.assertEqual(data["offers"]["price"], "300000", lang)


@override_settings(MEDIA_ROOT=MEDIA)
class ImageOptimizationTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def _upload(self, data=None, name="photo.jpg"):
        return SimpleUploadedFile(name, data or image_bytes(), content_type="image/jpeg")

    def test_page_upload_becomes_resized_webp(self):
        page = Page.objects.create(slug="about", title="About", image=self._upload())
        self.assertTrue(page.image.name.endswith(".webp"))
        with Image.open(page.image.path) as im:
            self.assertEqual(max(im.size), 1600)

    def test_hero_upload_becomes_resized_webp(self):
        site = SiteSettings.load()
        site.hero_image = self._upload(image_bytes(size=(3600, 2000)))
        site.save()
        self.assertTrue(site.hero_image.name.endswith(".webp"))
        with Image.open(site.hero_image.path) as im:
            self.assertEqual(max(im.size), 2400)

    def test_resaving_does_not_re_encode(self):
        page = Page.objects.create(slug="about", title="About", image=self._upload())
        name = page.image.name
        page.title = "Changed"
        page.save()
        self.assertEqual(Page.objects.get(pk=page.pk).image.name, name)

    def test_transparency_is_kept(self):
        data = image_bytes("PNG", "RGBA", (100, 100))
        page = Page.objects.create(slug="logo", title="Logo", image=self._upload(data, "logo.png"))
        with Image.open(page.image.path) as im:
            self.assertEqual(im.mode, "RGBA")

    def test_command_converts_old_images_once_and_keeps_originals(self):
        page = Page(slug="about", title="About")
        # Store the file the way older uploads were stored, without optimisation.
        page.image.save("old.jpg", ContentFile(image_bytes()), save=False)
        Page.objects.bulk_create([page])
        original = Page.objects.get(slug="about").image
        original_path, original_name = original.path, original.name
        self.assertTrue(original_name.endswith(".jpg"))

        call_command("optimize_images", stdout=StringIO())

        converted = Page.objects.get(slug="about").image
        self.assertTrue(converted.name.endswith(".webp"))
        self.assertTrue(Path(original_path).exists())

        out = StringIO()
        call_command("optimize_images", stdout=out)
        self.assertEqual(Page.objects.get(slug="about").image.name, converted.name)
        self.assertNotIn("->", out.getvalue())
