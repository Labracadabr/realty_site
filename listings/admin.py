from adminsortable2.admin import SortableAdminBase, SortableAdminMixin, SortableTabularInline
from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Max, Q
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from core.admin_mixins import AutoTranslateMixin

from .models import Lead, Property, PropertyImage, PropertyVideo, Region, ShareLink


class StaffUserChoicesMixin:
    """User dropdowns list only admins/partners (partners can't browse the users admin)."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.remote_field.model is get_user_model():
            kwargs["queryset"] = get_user_model().objects.filter(is_staff=True, is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleImageInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [super(MultipleImageField, self).clean(item, initial) for item in data]
        return [super().clean(data, initial)] if data else []


class PropertyAdminForm(forms.ModelForm):
    upload_photos = MultipleImageField(
        required=False,
        label="Add photos",
        help_text="Select many files at once. They are converted to WebP and appended to the gallery below.",
    )

    class Meta:
        model = Property
        fields = "__all__"


def _thumb(image, size=90):
    if not image:
        return "—"
    return format_html('<img src="{}" style="height:{}px;border-radius:6px;object-fit:cover">', image.thumb_url, size)


def _copy_button(url):
    return format_html(
        '<span class="ll-copy" data-copy="{0}" title="{0}">🔗 copy</span> <a href="{0}" target="_blank">open ↗</a>', url
    )


class PropertyImageInline(SortableTabularInline):
    model = PropertyImage
    extra = 0
    fields = ("preview", "image", "caption", "is_cover")
    readonly_fields = ("preview",)

    @admin.display(description="")
    def preview(self, obj):
        return _thumb(obj if obj.pk else None, 70)


class PropertyVideoInline(SortableTabularInline):
    model = PropertyVideo
    extra = 0
    fields = ("url", "file", "title")


class ShareLinkInline(StaffUserChoicesMixin, admin.TabularInline):
    model = ShareLink
    extra = 0
    fields = ("label", "owner", "language", "is_active", "expires_at", "link", "views", "last_viewed_at")
    readonly_fields = ("link", "views", "last_viewed_at")
    verbose_name_plural = "Share links (private & referral)"

    @admin.display(description="Link")
    def link(self, obj):
        return _copy_button(obj.full_url) if obj.pk else "saved on submit"


class TranslationCheckFilter(admin.SimpleListFilter):
    title = "translations"
    parameter_name = "translations"

    def lookups(self, request, model_admin):
        return (("unchecked", "RU or TR not checked"),)

    def queryset(self, request, queryset):
        if self.value() == "unchecked":
            return queryset.filter(Q(reviewed_ru=False) | Q(reviewed_tr=False))
        return queryset


@admin.register(Property)
class PropertyAdmin(StaffUserChoicesMixin, SortableAdminBase, AutoTranslateMixin, TranslationAdmin):
    form = PropertyAdminForm
    inlines = (PropertyImageInline, PropertyVideoInline, ShareLinkInline)
    list_display = (
        "cover_preview",
        "ref",
        "title",
        "status",
        "kind",
        "region",
        "area",
        "price",
        "featured",
        "reviewed_ru",
        "reviewed_tr",
        "lead_count",
        "private_link",
    )
    list_display_links = ("cover_preview", "ref", "title")
    list_editable = ("status", "featured")
    list_filter = ("status", "kind", "region", "title_type", "featured", TranslationCheckFilter)
    search_fields = ("ref", "title_en", "title_ru", "title_tr", "location")
    readonly_fields = ("ref", "created_by", "created_at", "updated_at", "published_at")
    save_on_top = True
    fieldsets = (
        ("Publishing", {"fields": (("status", "featured", "order"), ("ref", "slug"), "responsible")}),
        ("Object", {"fields": ("title", "summary", ("kind", "region"), "location", ("latitude", "longitude"))}),
        (
            "Price & size",
            {"fields": (("land_area_m2", "price_usd", "price_on_request"),)},
        ),
        ("Legal", {"fields": (("title_type", "lease_years", "zoning"), "legal_notes")}),
        (
            "Features",
            {
                "fields": (
                    ("road_access", "electricity", "water", "ocean_view", "beachfront"),
                    ("distance_beach_km", "distance_airport_km"),
                )
            },
        ),
        ("Texts", {"fields": ("description", "highlights")}),
        ("Photos", {"fields": ("upload_photos",)}),
        ("SEO", {"classes": ("collapse",), "fields": ("seo_title", "seo_description")}),
        ("Translation check", {"fields": (("reviewed_ru", "reviewed_tr"),)}),
        ("Meta", {"classes": ("collapse",), "fields": ("created_by", "created_at", "updated_at", "published_at")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("region")
            .prefetch_related("images", "share_links")
            .annotate(_leads=Count("leads", distinct=True))
        )

    @admin.display(description="")
    def cover_preview(self, obj):
        return _thumb(obj.cover, 48)

    @admin.display(description="Area")
    def area(self, obj):
        return f"{obj.area_are:,} are"

    @admin.display(description="Price", ordering="price_usd")
    def price(self, obj):
        if obj.price_on_request or not obj.price_usd:
            return "on request"
        return f"${obj.price_usd:,.0f}"

    @admin.display(description="Leads", ordering="_leads")
    def lead_count(self, obj):
        return obj._leads

    @admin.display(description="Private link")
    def private_link(self, obj):
        link = next((s for s in obj.share_links.all() if s.owner_id is None and not s.label), None)
        return _copy_button(link.full_url) if link else "—"

    def view_on_site(self, obj):
        return obj.get_absolute_url() if obj.is_public else obj.default_share_link().get_absolute_url()

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        prop = form.instance
        photos = form.cleaned_data.get("upload_photos") or []
        if photos:
            start = (prop.images.aggregate(m=Max("order"))["m"] or 0) + 1
            for i, f in enumerate(photos):
                PropertyImage.objects.create(property=prop, image=f, order=start + i)
            messages.success(request, f"{len(photos)} photo(s) added.")
        if not prop.images.filter(is_cover=True).exists() and (first := prop.images.first()):
            first.is_cover = True
            first.save(update_fields=["is_cover"])
        prop.default_share_link()


@admin.register(Region)
class RegionAdmin(SortableAdminMixin, AutoTranslateMixin, TranslationAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name_en",)


@admin.register(ShareLink)
class ShareLinkAdmin(StaffUserChoicesMixin, admin.ModelAdmin):
    list_display = ("property", "label", "owner", "is_active", "views", "last_viewed_at", "lead_count", "link")
    list_filter = ("is_active", "owner")
    search_fields = ("label", "property__ref", "property__title_en")
    autocomplete_fields = ("property",)
    readonly_fields = ("link", "views", "last_viewed_at", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("property", "owner").annotate(_leads=Count("leads"))

    def get_changeform_initial_data(self, request):
        return {"owner": request.user.pk, **super().get_changeform_initial_data(request)}

    @admin.display(description="Leads", ordering="_leads")
    def lead_count(self, obj):
        return obj._leads

    @admin.display(description="Link")
    def link(self, obj):
        return _copy_button(obj.full_url) if obj.pk else "—"


@admin.register(Lead)
class LeadAdmin(StaffUserChoicesMixin, admin.ModelAdmin):
    list_display = ("created_at", "name", "contact", "property", "referrer", "language", "status")
    list_editable = ("status",)
    list_filter = ("status", "language", "referrer", "property")
    search_fields = ("name", "email", "phone", "telegram", "message")
    readonly_fields = ("created_at", "page_url", "utm", "language", "share_link")
    fields = (
        ("name", "status"),
        ("email", "phone", "telegram"),
        "interest",
        "message",
        ("property", "referrer"),
        "notes",
        ("share_link", "language", "created_at"),
        "page_url",
        "utm",
    )
    autocomplete_fields = ("property",)
    date_hierarchy = "created_at"

    @admin.display(description="Contact")
    def contact(self, obj):
        return " · ".join(v for v in (obj.phone, obj.email, obj.telegram) if v)
