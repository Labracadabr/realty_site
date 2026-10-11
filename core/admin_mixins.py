from django.conf import settings
from django.urls import reverse


class AutoTranslateMixin:
    """Adds the "auto-translate" toolbar to a modeltranslation admin form."""

    class Media:
        js = ("admin/autotranslate.js",)
        css = {"all": ("admin/lovina-admin.css",)}

    def render_change_form(self, request, context, *args, **kwargs):
        context["autotranslate"] = {
            "url": reverse("admin_translate"),
            "languages": [code for code, _ in settings.LANGUAGES],
        }
        return super().render_change_form(request, context, *args, **kwargs)
