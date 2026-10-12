from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.admin_views import translate_fields
from core.sitemaps import sitemaps
from core.views import robots_txt
from listings.views import share_entry

urlpatterns = [
    path(f"{settings.ADMIN_URL}translate/", translate_fields, name="admin_translate"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt),
    path("s/<str:token>/", share_entry, name="share_entry"),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("", include("listings.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
