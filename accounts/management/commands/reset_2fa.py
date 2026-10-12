from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = "Remove a user's authenticator devices (lost phone). They set up a new one at next login."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, username, **opts):
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            raise CommandError(f"No user {username!r}")
        count, _ = TOTPDevice.objects.filter(user=user).delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {count} device(s) for {username}."))
