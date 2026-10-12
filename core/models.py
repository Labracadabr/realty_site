from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Singleton with contacts and editable home-page texts."""

    brand = models.CharField(max_length=60, default="Bali Islands")
    legal_name = models.CharField(_("company legal name"), max_length=120, blank=True, help_text="PT ...")
    nib = models.CharField("NIB", max_length=40, blank=True)
    kbli = models.CharField("KBLI", max_length=60, blank=True, help_text="e.g. 68200")
    address = models.CharField(_("address"), max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(_("phone"), max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=20, blank=True, help_text="Digits only, with country code: 62812...")
    telegram = models.CharField("Telegram username", max_length=60, blank=True, help_text="Without @")
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    hero_title = models.CharField(_("hero title"), max_length=160, default="Exclusive land in Bali, off-market")
    hero_subtitle = models.CharField(_("hero subtitle"), max_length=300, blank=True)
    hero_image = models.ImageField(_("hero image"), upload_to="site/", blank=True)
    hero_video = models.FileField(_("hero video (mp4, muted loop)"), upload_to="site/", blank=True)
    stats = models.TextField(
        _("key numbers"), blank=True, help_text="One per line: value | label   (e.g. 12 | years in Bali)"
    )
    seo_description = models.CharField(max_length=170, blank=True)

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def stat_list(self):
        rows = []
        for line in (self.stats or "").splitlines():
            if "|" in line:
                value, label = line.split("|", 1)
                rows.append({"value": value.strip(), "label": label.strip()})
        return rows

    @property
    def whatsapp_url(self):
        digits = "".join(ch for ch in self.whatsapp if ch.isdigit())
        return f"https://wa.me/{digits}" if digits else ""

    @property
    def telegram_url(self):
        return f"https://t.me/{self.telegram.lstrip('@')}" if self.telegram else ""


class Page(models.Model):
    """Editable text pages: about, how-to-buy, privacy, terms."""

    slug = models.SlugField(unique=True, help_text="about · how-to-buy · privacy · terms")
    title = models.CharField(_("title"), max_length=160)
    lead = models.TextField(_("intro"), blank=True)
    body = models.TextField(
        _("body"), blank=True, help_text="Blank line = new paragraph. “## ” heading, “- ” list item, **bold**."
    )
    image = models.ImageField(_("image"), upload_to="pages/", blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=170, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        named = {"about": "core:about", "how-to-buy": "core:how_to_buy"}
        if self.slug in named:
            return reverse(named[self.slug])
        return reverse("core:page", kwargs={"slug": self.slug})


class Service(models.Model):
    class Icon(models.TextChoices):
        SEARCH = "search", "Search / due diligence"
        DOCUMENT = "document", "Documents"
        BUILDING = "building", "Company / PT PMA"
        STAMP = "stamp", "Notary / permits"
        CRANE = "crane", "Construction"
        KEY = "key", "Management / handover"

    title = models.CharField(_("title"), max_length=120)
    summary = models.CharField(_("summary"), max_length=300)
    body = models.TextField(_("details"), blank=True, help_text="Same formatting as pages")
    icon = models.CharField(max_length=12, choices=Icon.choices, default=Icon.DOCUMENT)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    author = models.CharField(_("author"), max_length=120)
    origin = models.CharField(_("country / company"), max_length=120, blank=True)
    text = models.TextField(_("text"))
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("testimonial")
        verbose_name_plural = _("testimonials")

    def __str__(self):
        return self.author
