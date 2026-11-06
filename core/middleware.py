from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponsePermanentRedirect

UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid")


class CanonicalHostMiddleware:
    """301 the www / non-www twin of SITE_URL's host to SITE_URL, so the site has one address."""

    def __init__(self, get_response):
        self.get_response = get_response
        host = urlparse(settings.SITE_URL).netloc.lower()
        self.twin = host.removeprefix("www.") if host.startswith("www.") else f"www.{host}"

    def __call__(self, request):
        if request.get_host().lower() == self.twin:
            return HttpResponsePermanentRedirect(settings.SITE_URL + request.get_full_path())
        return self.get_response(request)


class UTMMiddleware:
    """Remember the first ad/campaign parameters of a visit for lead attribution."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        params = {k: request.GET[k][:200] for k in UTM_KEYS if k in request.GET}
        if params and "utm" not in request.session:
            request.session["utm"] = params
        return self.get_response(request)
