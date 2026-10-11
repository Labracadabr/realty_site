from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from listings.models import Property

from .models import Page

PROTOCOL = urlparse(settings.SITE_URL).scheme or "https"


class _I18nSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    protocol = PROTOCOL


class StaticSitemap(_I18nSitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["core:home", "listings:catalog", "core:services", "core:contact"]

    def location(self, item):
        return reverse(item)


class PageSitemap(_I18nSitemap):
    priority = 0.6

    def items(self):
        return Page.objects.exclude(slug__in=["privacy", "terms"])

    def lastmod(self, obj):
        return obj.updated_at


class PropertySitemap(_I18nSitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return Property.objects.filter(status__in=Property.PUBLIC_STATUSES)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {"static": StaticSitemap, "pages": PageSitemap, "properties": PropertySitemap}
