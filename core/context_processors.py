from django.conf import settings
from django.urls import translate_url

from .models import SiteSettings


def site(request):
    path = request.get_full_path()
    return {
        "site": SiteSettings.load(),
        "SITE_URL": settings.SITE_URL,
        "GTM_ID": settings.GTM_ID,
        "language_links": [
            {"code": code, "name": name, "url": translate_url(path, code)} for code, name in settings.LANGUAGES
        ],
    }
