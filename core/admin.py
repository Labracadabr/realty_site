from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from modeltranslation.admin import TranslationAdmin

from .admin_mixins import AutoTranslateMixin
from .models import Page, Service, SiteSettings, Testimonial

admin.site.site_header = "Bali Islands"
admin.site.site_title = "Bali Islands admin"
admin.site.index_title = "Management"


@admin.register(SiteSettings)
class SiteSettingsAdmin(AutoTranslateMixin, TranslationAdmin):
    fieldsets = (
        ("Company", {"fields": ("brand", "legal_name", "nib", "kbli", "address")}),
        ("Contacts", {"fields": ("email", "phone", "whatsapp", "telegram", "instagram", "youtube")}),
        ("Home page", {"fields": ("hero_title", "hero_subtitle", "hero_image", "hero_video", "stats", "seo_description")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        return redirect("admin:core_sitesettings_change", SiteSettings.load().pk)


@admin.register(Page)
class PageAdmin(AutoTranslateMixin, TranslationAdmin):
    list_display = ("title", "slug", "updated_at")
    fieldsets = ((None, {"fields": ("slug", "title", "lead", "body", "image")}), ("SEO", {"fields": ("seo_title", "seo_description")}))


@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, AutoTranslateMixin, TranslationAdmin):
    list_display = ("title", "icon")
    fields = ("title", "summary", "body", "icon")


@admin.register(Testimonial)
class TestimonialAdmin(SortableAdminMixin, AutoTranslateMixin, TranslationAdmin):
    list_display = ("author", "origin", "is_active")
    fields = ("author", "origin", "text", "is_active")
