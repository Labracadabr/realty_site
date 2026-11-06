from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import Page, SiteSettings


class Command(BaseCommand):
    help = "Convert page and hero images uploaded before automatic optimisation to web-sized WebP. Safe to re-run."

    def handle(self, *args, **opts):
        targets = [(page, "image") for page in Page.objects.exclude(image="")]
        targets.append((SiteSettings.load(), "hero_image"))
        for obj, field in targets:
            current = getattr(obj, field)
            if not current or current.name.endswith(".webp"):
                continue
            old_name, old_size = current.name, current.size
            with current.open("rb") as f:
                data = f.read()
            # Assigning a new file makes the model's save() optimise it. The original stays on disk.
            setattr(obj, field, ContentFile(data, name=Path(old_name).name))
            obj.save()
            new = getattr(obj, field)
            self.stdout.write(f"{old_name} ({old_size // 1024} KB) -> {new.name} ({new.size // 1024} KB)")
        self.stdout.write("Done.")
