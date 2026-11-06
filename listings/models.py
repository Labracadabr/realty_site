import builtins
import secrets
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps

from core.images import encode_webp


class Region(models.Model):
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("region")
        verbose_name_plural = _("regions")

    def __str__(self):
        return self.name


class Property(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        UNLISTED = "unlisted", _("Link only")
        SOLD = "sold", _("Sold")

    class Kind(models.TextChoices):
        LAND = "land", _("Land plot")
        BEACHFRONT = "beachfront", _("Beachfront land")
        ISLAND = "island", _("Island")
        ESTATE = "estate", _("Land with buildings")

    class TitleType(models.TextChoices):
        SHM = "shm", _("Freehold (SHM)")
        HGB = "hgb", _("HGB (right to build)")
        HAK_PAKAI = "hak_pakai", _("Hak Pakai (right to use)")
        LEASEHOLD = "leasehold", _("Leasehold")
        OTHER = "other", _("Other / on request")

    class Zoning(models.TextChoices):
        TOURISM = "tourism", _("Tourism (pink zone)")
        RESIDENTIAL = "residential", _("Residential (yellow zone)")
        COMMERCIAL = "commercial", _("Commercial")
        MIXED = "mixed", _("Mixed")
        AGRICULTURAL = "agricultural", _("Agricultural (green zone)")
        UNKNOWN = "unknown", _("To be confirmed")

    # --- identity & publishing
    ref = models.CharField(_("reference"), max_length=20, unique=True, blank=True, help_text="Auto: BI-001")
    title = models.CharField(_("title"), max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True, help_text="Auto from English title")
    status = models.CharField(_("status"), max_length=12, choices=Status.choices, default=Status.DRAFT)
    featured = models.BooleanField(_("featured on home page"), default=False)
    order = models.PositiveIntegerField(_("sort order"), default=0, help_text="Lower comes first")

    # --- what & where
    kind = models.CharField(_("type"), max_length=12, choices=Kind.choices, default=Kind.LAND)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="properties", verbose_name=_("region"))
    location = models.CharField(_("location"), max_length=160, help_text="e.g. Kalibukbuk, Lovina")
    map_link = models.CharField(
        _("Google Maps link"),
        max_length=1000,
        blank=True,
        help_text="Paste any Google Maps link to the spot (or coordinates). Latitude/longitude are filled on save.",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # --- numbers
    land_area_m2 = models.DecimalField(_("land area, m²"), max_digits=12, decimal_places=2)
    price_usd = models.DecimalField(_("price, USD"), max_digits=14, decimal_places=0, null=True, blank=True)
    price_on_request = models.BooleanField(_("price on request"), default=False)

    # --- legal
    title_type = models.CharField(_("title / ownership"), max_length=12, choices=TitleType.choices, default=TitleType.SHM)
    lease_years = models.PositiveIntegerField(_("lease term, years"), null=True, blank=True)
    zoning = models.CharField(_("zoning"), max_length=14, choices=Zoning.choices, default=Zoning.UNKNOWN)
    legal_notes = models.TextField(
        _("legal notes"), blank=True, help_text="Foreign ownership options, permits, restrictions"
    )

    # --- features
    road_access = models.BooleanField(_("road access"), default=False)
    electricity = models.BooleanField(_("electricity"), default=False)
    water = models.BooleanField(_("water source"), default=False)
    ocean_view = models.BooleanField(_("ocean view"), default=False)
    beachfront = models.BooleanField(_("beachfront"), default=False)
    distance_beach_km = models.DecimalField(_("to the beach, km"), max_digits=6, decimal_places=1, null=True, blank=True)
    distance_airport_km = models.DecimalField(_("to airport, km"), max_digits=6, decimal_places=1, null=True, blank=True)

    # --- texts (translated: see translation.py)
    summary = models.CharField(_("short summary"), max_length=300, blank=True, help_text="1–2 sentences for cards")
    description = models.TextField(_("description"), blank=True)
    highlights = models.TextField(_("highlights"), blank=True, help_text="One per line")
    seo_title = models.CharField(_("SEO title"), max_length=70, blank=True)
    seo_description = models.CharField(_("SEO description"), max_length=170, blank=True)

    # --- translation review flags
    reviewed_ru = models.BooleanField(_("RU text checked"), default=False)
    reviewed_tr = models.BooleanField(_("TR text checked"), default=False)

    # --- people
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_properties",
        verbose_name=_("responsible agent"),
        help_text="Gets Telegram notifications for leads on this object",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+", editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["order", "-published_at", "-created_at"]
        verbose_name = _("property")
        verbose_name_plural = _("properties")

    def __str__(self):
        return f"{self.ref} · {self.title}" if self.ref else self.title

    # Statuses visible to the public catalog / by direct URL
    PUBLIC_STATUSES = (Status.PUBLISHED, Status.SOLD)
    # Statuses reachable via a share link
    SHAREABLE_STATUSES = (Status.PUBLISHED, Status.SOLD, Status.UNLISTED)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title)[:160] or "property"
            slug, n = base, 2
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        if not self.ref:
            last = Property.objects.order_by("-id").first()
            self.ref = f"BI-{(last.id + 1) if last else 1:03d}"
            while Property.objects.filter(ref=self.ref).exists():
                self.ref = f"BI-{int(self.ref[3:]) + 1:03d}"
        if self.status in (self.Status.PUBLISHED, self.Status.UNLISTED) and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("listings:detail", kwargs={"slug": self.slug})

    @property
    def is_public(self):
        return self.status in self.PUBLIC_STATUSES

    @property
    def is_sold(self):
        return self.status == self.Status.SOLD

    @property
    def area_are(self):
        return (self.land_area_m2 / 100).quantize(Decimal("0.01"))

    @property
    def area_ha(self):
        return (self.land_area_m2 / 10000).quantize(Decimal("0.01"))

    @property
    def show_price(self):
        return bool(self.price_usd) and not self.price_on_request

    @property
    def price_per_are(self):
        if self.show_price and self.land_area_m2:
            return (self.price_usd / self.area_are).quantize(Decimal("1"))
        return None

    @property
    def highlight_list(self):
        return [line.strip(" -•\t") for line in (self.highlights or "").splitlines() if line.strip()]

    @property
    def cover(self):
        images = list(self.images.all())
        return next((i for i in images if i.is_cover), images[0] if images else None)

    @property
    def has_coords(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def google_maps_url(self):
        if self.map_link.startswith(("https://", "http://")):
            return self.map_link
        return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"

    def default_share_link(self):
        link = self.share_links.filter(owner__isnull=True, label="").first()
        return link or ShareLink.objects.create(property=self)


def _upload_to(instance, filename):
    return f"properties/{instance.property_id or 'new'}/{secrets.token_hex(6)}{Path(filename).suffix.lower()}"


class PropertyImage(models.Model):
    MAX_SIDE = 2400
    THUMB_SIDE = 900

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(_("image"), upload_to=_upload_to)
    thumb = models.ImageField(upload_to=_upload_to, blank=True, editable=False)
    caption = models.CharField(_("caption"), max_length=200, blank=True)
    is_cover = models.BooleanField(_("cover"), default=False)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __str__(self):
        return self.caption or Path(self.image.name).name

    def save(self, *args, **kwargs):
        # Normalise once: re-encode original to WebP (max 2400px) and build a thumbnail.
        newly_uploaded = self.image and not getattr(self.image, "_committed", True)
        if newly_uploaded or (self.image and not self.thumb):
            img = ImageOps.exif_transpose(Image.open(self.image)).convert("RGB")
            self.image = encode_webp(img, self.MAX_SIDE, quality=84)
            self.thumb = encode_webp(img, self.THUMB_SIDE, quality=78)
        super().save(*args, **kwargs)

    @builtins.property
    def thumb_url(self):
        return (self.thumb or self.image).url


class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="videos")
    url = models.URLField(_("YouTube / Vimeo link"), blank=True)
    file = models.FileField(_("or video file (mp4)"), upload_to=_upload_to, blank=True)
    title = models.CharField(_("title"), max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("video")
        verbose_name_plural = _("videos")

    def __str__(self):
        return self.title or self.url or self.file.name

    @builtins.property
    def embed_url(self):
        from .utils import video_embed_url

        return video_embed_url(self.url) if self.url else None


def _token():
    return secrets.token_urlsafe(9)


class ShareLink(models.Model):
    """Private / referral link to a property: /s/<token>/.
    Works for unlisted objects; leads arriving through it are attributed to its owner."""

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="share_links")
    token = models.CharField(max_length=32, unique=True, default=_token, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="share_links",
        verbose_name=_("referrer"),
        help_text="Partner who shares this link (lead attribution)",
    )
    label = models.CharField(_("label"), max_length=120, blank=True, help_text="e.g. “for Mehmet, Istanbul”")
    language = models.CharField(
        _("language"),
        max_length=5,
        blank=True,
        choices=settings.LANGUAGES,
        help_text="Empty = visitor's browser language",
    )
    is_active = models.BooleanField(_("active"), default=True)
    expires_at = models.DateTimeField(_("expires"), null=True, blank=True)
    views = models.PositiveIntegerField(default=0, editable=False)
    last_viewed_at = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("share link")
        verbose_name_plural = _("share links")

    def __str__(self):
        return f"{self.property.ref} · {self.label or 'default'}"

    def get_absolute_url(self):
        # Language-neutral entry point; redirects to /<lang>/s/<token>/
        return reverse("share_entry", kwargs={"token": self.token})

    @builtins.property
    def full_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    @builtins.property
    def is_usable(self):
        return (
            self.is_active
            and self.property.status in Property.SHAREABLE_STATUSES
            and (self.expires_at is None or self.expires_at > timezone.now())
        )

    def register_view(self):
        ShareLink.objects.filter(pk=self.pk).update(views=models.F("views") + 1, last_viewed_at=timezone.now())


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("New")
        IN_PROGRESS = "in_progress", _("In progress")
        DEAL = "deal", _("Deal")
        CLOSED = "closed", _("Closed / lost")
        SPAM = "spam", _("Spam")

    name = models.CharField(_("name"), max_length=120)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone / WhatsApp"), max_length=40, blank=True)
    telegram = models.CharField(_("Telegram"), max_length=60, blank=True)
    message = models.TextField(_("message"), blank=True)
    interest = models.CharField(_("interest"), max_length=40, blank=True)

    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    share_link = models.ForeignKey(ShareLink, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="referred_leads"
    )
    language = models.CharField(max_length=5, blank=True)
    page_url = models.CharField(max_length=500, blank=True)
    utm = models.JSONField(default=dict, blank=True)

    status = models.CharField(_("status"), max_length=12, choices=Status.choices, default=Status.NEW)
    notes = models.TextField(_("internal notes"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("lead")
        verbose_name_plural = _("leads")

    def __str__(self):
        return f"{self.name} · {self.created_at:%Y-%m-%d}"
