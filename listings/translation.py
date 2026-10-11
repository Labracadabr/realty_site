from modeltranslation.translator import TranslationOptions, register

from .models import Property, Region


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Property)
class PropertyTranslationOptions(TranslationOptions):
    fields = ("title", "summary", "description", "highlights", "legal_notes", "seo_title", "seo_description")
    required_languages = ("en",)
