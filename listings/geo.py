"""Extract coordinates from whatever an admin pastes: a Google Maps link (long or short)
or plain coordinates copied from the map ("-8.1724, 115.0198" or 8°10'20.6"S 115°01'11.3"E)."""

import logging
import re
from decimal import Decimal
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests

log = logging.getLogger(__name__)

NUM = r"[-+]?\d{1,3}(?:\.\d+)?"
PAIR = re.compile(rf"({NUM})\s*,\s*\+?\s*({NUM})")
PIN = re.compile(rf"!3d({NUM})!4d({NUM})")  # exact marker of a place
AT = re.compile(rf"@({NUM}),({NUM})")  # map viewport centre
DMS = re.compile(
    r"(\d{1,2})°\s*(\d{1,2})['′]\s*([\d.]+)?[\"″]?\s*([NS])[\s,]+"
    r"(\d{1,3})°\s*(\d{1,2})['′]\s*([\d.]+)?[\"″]?\s*([EW])",
    re.I,
)
QUERY_KEYS = ("q", "query", "ll", "center", "destination", "daddr", "sll")
# Only the exact place marker is trusted in page HTML: "center=" / "@" there is just the
# default viewport (geo-located by the server IP), which would silently give a wrong spot.
BODY_PATTERNS = (PIN,)
SHORT_HOSTS = ("maps.app.goo.gl", "goo.gl", "g.co")
MAX_HOPS = 6


class MapLinkError(ValueError):
    pass


def _valid(lat, lng):
    try:
        lat, lng = Decimal(lat), Decimal(lng)
    except ArithmeticError:
        return None
    if -90 <= lat <= 90 and -180 <= lng <= 180 and (lat, lng) != (0, 0):
        return lat.quantize(Decimal("0.000001")), lng.quantize(Decimal("0.000001"))
    return None


def _from_dms(text):
    m = DMS.search(text)
    if not m:
        return None
    d1, m1, s1, h1, d2, m2, s2, h2 = m.groups()
    lat = Decimal(d1) + Decimal(m1) / 60 + Decimal(s1 or 0) / 3600
    lng = Decimal(d2) + Decimal(m2) / 60 + Decimal(s2 or 0) / 3600
    return _valid(-lat if h1.upper() == "S" else lat, -lng if h2.upper() == "W" else lng)


def coords_from_text(text):
    """Parse coordinates from a URL or free text without any network access."""
    text = unquote(unquote(text.strip()))
    if (m := PIN.search(text)) and (found := _valid(*m.groups())):
        return found
    parsed = urlparse(text)
    if parsed.query:
        params = parse_qs(parsed.query)
        for key in QUERY_KEYS:
            for value in params.get(key, []):
                if m := PAIR.search(value.removeprefix("loc:")):
                    if found := _valid(*m.groups()):
                        return found
    for pattern in (AT, PAIR):
        if m := pattern.search(text):
            if found := _valid(*m.groups()):
                return found
    return _from_dms(text)


GOOGLE_HOST = re.compile(r"^(?:[a-z0-9-]+\.)*google\.(?:com|[a-z]{2,3}|co\.[a-z]{2}|com\.[a-z]{2})$")


def _is_google(host):
    host = (host or "").lower()
    return host in SHORT_HOSTS or bool(GOOGLE_HOST.match(host))


def resolve(url):
    """Follow redirects of a Google short link (only through Google hosts). Returns (final_url, body)."""
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; BaliIslandsBot/1.0)"
    session.cookies.set("CONSENT", "YES+", domain=".google.com")
    for _ in range(MAX_HOPS):
        if not _is_google(urlparse(url).hostname):
            raise MapLinkError("Only Google Maps links are supported.")
        resp = session.get(url, allow_redirects=False, timeout=10)
        if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
            url = urljoin(url, resp.headers.get("Location", ""))
            # EU consent wall: the real target sits in ?continue=
            if "consent." in (urlparse(url).hostname or ""):
                url = parse_qs(urlparse(url).query).get("continue", [url])[0]
            if coords_from_text(url):
                return url, ""
            continue
        return url, resp.text[:2_000_000]
    raise MapLinkError("Too many redirects.")


def coords_from_map_link(value):
    """Main entry point. Returns (lat, lng) or raises MapLinkError with a human message."""
    value = (value or "").strip()
    if not value:
        raise MapLinkError("Empty link.")
    if found := coords_from_text(value):
        return found
    if not value.startswith(("http://", "https://")):
        raise MapLinkError("Paste a Google Maps link or coordinates like “-8.1724, 115.0198”.")
    try:
        final_url, body = resolve(value)
    except requests.RequestException as exc:
        log.warning("Map link resolve failed: %s", exc)
        raise MapLinkError("Couldn't open the link. Check it, or paste coordinates instead.") from exc
    if found := coords_from_text(final_url):
        return found
    for pattern in BODY_PATTERNS:
        if m := pattern.search(body):
            if found := _valid(*m.groups()):
                return found
    raise MapLinkError(
        "No coordinates in this link. In Google Maps right-click the exact spot, "
        "click the coordinates to copy them and paste here."
    )
