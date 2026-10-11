import time
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Case, IntegerField, Prefetch, Value, When
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import translation
from django.utils.translation import get_language, get_language_from_request
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.telegram import notify_lead

from .forms import LeadForm
from .models import Lead, Property, PropertyImage, Region, ShareLink

SORTS = {
    "new": ("sold_last", "order", "-published_at"),
    "price_asc": ("sold_last", "price_usd"),
    "price_desc": ("sold_last", "-price_usd"),
    "area_desc": ("sold_last", "-land_area_m2"),
}


def _decimal(value):
    try:
        return Decimal(value) if value not in (None, "") else None
    except InvalidOperation:
        return None


def public_properties():
    return (
        Property.objects.filter(status__in=Property.PUBLIC_STATUSES)
        .select_related("region")
        .prefetch_related(Prefetch("images", queryset=PropertyImage.objects.order_by("order", "id")))
        .annotate(
            sold_last=Case(
                When(status=Property.Status.SOLD, then=Value(1)), default=Value(0), output_field=IntegerField()
            )
        )
    )


def catalog(request):
    qs = public_properties()
    f = {
        "kind": request.GET.get("kind", ""),
        "region": request.GET.get("region", ""),
        "price_max": request.GET.get("price_max", ""),
        "area_min": request.GET.get("area_min", ""),
        "sort": request.GET.get("sort", "new") if request.GET.get("sort") in SORTS else "new",
        "sold": request.GET.get("sold", "1"),
    }
    if f["kind"] in Property.Kind.values:
        qs = qs.filter(kind=f["kind"])
    if f["region"]:
        qs = qs.filter(region__slug=f["region"])
    if (price_max := _decimal(f["price_max"])) is not None:
        qs = qs.filter(price_usd__lte=price_max, price_on_request=False)
    if (area_min := _decimal(f["area_min"])) is not None:
        qs = qs.filter(land_area_m2__gte=area_min * 100)  # input in are
    if f["sold"] == "0":
        qs = qs.exclude(status=Property.Status.SOLD)
    qs = qs.order_by(*SORTS[f["sort"]])

    return render(
        request,
        "listings/catalog.html",
        {
            "properties": qs,
            "filters": f,
            "kinds": Property.Kind.choices,
            "regions": Region.objects.filter(properties__status__in=Property.PUBLIC_STATUSES).distinct(),
            "is_filtered": any(f[k] for k in ("kind", "region", "price_max", "area_min")),
        },
    )


def _render_property(request, prop, share_link=None):
    similar = (
        public_properties()
        .exclude(pk=prop.pk)
        .exclude(status=Property.Status.SOLD)
        .order_by("-featured", "order")[:3]
    )
    return render(
        request,
        "listings/detail.html",
        {
            "property": prop,
            "images": list(prop.images.all()),
            "videos": list(prop.videos.all()),
            "similar": similar,
            "share_link": share_link,
            "noindex": share_link is not None or not prop.is_public,
            "is_preview": not prop.is_public and share_link is None,
            "form": LeadForm(initial={"property_id": prop.pk}),
        },
    )


def detail(request, slug):
    prop = get_object_or_404(Property.objects.select_related("region"), slug=slug)
    if not prop.is_public:
        # Staff can preview drafts / unlisted objects; everyone else gets 404.
        if not request.user.is_staff:
            raise Http404
    return _render_property(request, prop)


def share_entry(request, token):
    """Language-neutral /s/<token>/ -> /<lang>/s/<token>/ (keeps query string, e.g. utm)."""
    link = get_object_or_404(ShareLink, token=token)
    lang = link.language or get_language_from_request(request)
    with translation.override(lang):
        url = reverse("listings:share", kwargs={"token": token})
    if request.GET:
        url += "?" + request.GET.urlencode()
    return HttpResponseRedirect(url)


def share(request, token):
    link = get_object_or_404(ShareLink.objects.select_related("property__region", "owner"), token=token)
    if not link.is_usable:
        return render(request, "listings/link_expired.html", status=410)
    if not request.user.is_staff:
        link.register_view()
    request.session["share_token"] = link.token
    return _render_property(request, link.property, share_link=link)


@require_POST
def submit_lead(request):
    form = LeadForm(request.POST)
    back = request.POST.get("next") or reverse("core:home")
    if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
        back = reverse("core:home")

    if not form.is_valid():
        for errors in form.errors.values():
            for e in errors:
                messages.error(request, e)
        request.session["lead_form_data"] = {k: v for k, v in request.POST.items() if k in form.fields}
        return redirect(back + "#inquiry")

    data = form.cleaned_data
    if data["website"]:  # honeypot
        return redirect(back + "#inquiry")

    # Simple per-session throttle: max 5 inquiries per hour.
    now = time.time()
    stamps = [t for t in request.session.get("lead_times", []) if now - t < 3600]
    if len(stamps) >= 5:
        messages.error(request, _("Too many requests. Please contact us via WhatsApp or Telegram."))
        return redirect(back + "#inquiry")
    request.session["lead_times"] = stamps + [now]

    prop = Property.objects.filter(pk=data.get("property_id")).first() if data.get("property_id") else None
    link = None
    if token := request.session.get("share_token"):
        link = ShareLink.objects.filter(token=token).select_related("owner", "property").first()

    lead = Lead.objects.create(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        telegram=data["telegram"],
        interest=data["interest"],
        message=data["message"],
        property=prop,
        share_link=link,
        referrer=link.owner if link else None,
        language=get_language(),
        page_url=back[:500],
        utm=request.session.get("utm", {}),
    )
    notify_lead(lead)
    request.session.pop("lead_form_data", None)
    messages.success(request, _("Thank you! We will contact you within 24 hours."))
    return redirect(back + "#inquiry")
