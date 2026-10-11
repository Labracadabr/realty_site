from pathlib import Path

import polib
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compile locale/*/LC_MESSAGES/*.po to .mo without GNU gettext (works on Windows)."

    def handle(self, *args, **opts):
        for locale_dir in settings.LOCALE_PATHS:
            for po_path in Path(locale_dir).glob("*/LC_MESSAGES/*.po"):
                po = polib.pofile(str(po_path))
                po.save_as_mofile(str(po_path.with_suffix(".mo")))
                self.stdout.write(f"{po_path.relative_to(settings.BASE_DIR)}: {po.percent_translated()}% translated")
