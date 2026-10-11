from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Users & roles"

    def ready(self):
        from .roles import ensure_partner_group

        # Runs after each app's post_migrate (listings perms are created after accounts').
        post_migrate.connect(ensure_partner_group, dispatch_uid="ensure_partner_group")
