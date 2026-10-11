from modeltranslation.translator import TranslationOptions, register

from .models import Page, Service, SiteSettings, Testimonial


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ("hero_title", "hero_subtitle", "stats", "seo_description")


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "lead", "body", "seo_title", "seo_description")
    required_languages = ("en",)


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ("title", "summary", "body")
    required_languages = ("en",)


@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ("text",)
