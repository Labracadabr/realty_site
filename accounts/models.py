from django.contrib.auth.models import AbstractUser
from django.db import models

PARTNERS_GROUP = "Partners"


class User(AbstractUser):
    """Admin = superuser (everything incl. technical settings).
    Partner = staff user in the "Partners" group (all listings, leads, share links)."""

    phone = models.CharField("Phone / WhatsApp", max_length=40, blank=True)
    telegram_chat_id = models.CharField(
        "Telegram chat ID",
        max_length=40,
        blank=True,
        help_text="Lead notifications for this user's objects and links. Get it from @userinfobot.",
    )

    @property
    def is_partner(self):
        return self.groups.filter(name=PARTNERS_GROUP).exists()

    def __str__(self):
        return self.get_full_name() or self.username
