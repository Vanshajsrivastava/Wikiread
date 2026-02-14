from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from encyclopedia.models import Entry


class Command(BaseCommand):
    help = "Import markdown files from entries/ directory into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing DB entries before import.",
        )

    def handle(self, *args, **options):
        entries_dir = Path(settings.BASE_DIR) / "entries"
        if not entries_dir.exists() or not entries_dir.is_dir():
            self.stdout.write(self.style.ERROR("entries/ directory not found."))
            return

        if options["clear"]:
            deleted, _ = Entry.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing rows."))

        imported = 0
        updated = 0

        for md_file in sorted(entries_dir.glob("*.md")):
            title = md_file.stem
            content = md_file.read_text(encoding="utf-8")

            obj, created = Entry.objects.update_or_create(
                title=title,
                defaults={"content": content},
            )
            if created:
                imported += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created: {imported}, Updated: {updated}, Total: {imported + updated}"
            )
        )
