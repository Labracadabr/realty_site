from django.contrib.auth.models import Group, Permission

from .models import PARTNERS_GROUP

# Partners get full rights over everything content-related in these apps/models.
PARTNER_MODELS = {
    "listings": ["property", "propertyimage", "propertyvideo", "region", "sharelink", "lead"],
}


def ensure_partner_group(sender=None, **kwargs):
    if sender is not None and sender.label not in PARTNER_MODELS:
        return
    group, _ = Group.objects.get_or_create(name=PARTNERS_GROUP)
    perms = Permission.objects.filter(
        content_type__app_label__in=PARTNER_MODELS.keys(),
    )
    allowed = [
        p for p in perms if p.content_type.model in PARTNER_MODELS.get(p.content_type.app_label, [])
    ]
    group.permissions.set(allowed)
