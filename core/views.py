from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from listings.forms import LeadForm
from listings.models import Property
from listings.views import public_properties

from .models import Page, Service, Testimonial


def _page(slug, required=False):
    page = Page.objects.filter(slug=slug).first()
    if page is None and required:
        raise Http404
    return page


def home(request):
    props = public_properties().exclude(status=Property.Status.SOLD)
    featured = list(props.filter(featured=True).order_by("order")[:6]) or list(props.order_by("order")[:6])
    return render(
        request,
        "core/home.html",
        {
            "featured": featured,
            "services": Service.objects.all()[:6],
            "testimonials": Testimonial.objects.filter(is_active=True)[:6],
            "about": _page("about"),
            "sold_count": Property.objects.filter(status=Property.Status.SOLD).count(),
            "form": LeadForm(),
        },
    )


def services(request):
    return render(request, "core/services.html", {"services": Service.objects.all(), "form": LeadForm()})


def about(request):
    return render(
        request,
        "core/about.html",
        {
            "page": _page("about", required=True),
            "testimonials": Testimonial.objects.filter(is_active=True),
            "form": LeadForm(),
        },
    )


def how_to_buy(request):
    return render(request, "core/page.html", {"page": _page("how-to-buy", required=True), "form": LeadForm(), "with_form": True})


def page(request, slug):
    return render(request, "core/page.html", {"page": _page(slug, required=True)})


def contact(request):
    return render(request, "core/contact.html", {"form": LeadForm()})


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /s/",
        "Disallow: /*/s/",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
