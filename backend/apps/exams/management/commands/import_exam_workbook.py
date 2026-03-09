from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.exams.services.workbook_import import import_workbook


class Command(BaseCommand):
    help = "Import workbook-based exam definitions into the configurable exam engine."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="NAIC MEDTECH SYSTEM DATA.xlsx",
            help="Path to the workbook file to import.",
        )
        parser.add_argument(
            "--draft",
            action="store_true",
            help="Create imported versions as draft instead of published.",
        )
        parser.add_argument(
            "--keep-published",
            action="store_true",
            help="Do not archive existing published versions before importing a new one.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create a new version even when the workbook source reference matches the latest published version.",
        )

    def handle(self, *args, **options):
        workbook_path = Path(options["file"])
        if not workbook_path.is_absolute():
            workbook_path = Path.cwd() / workbook_path

        if not workbook_path.exists():
            raise CommandError(f"Workbook not found: {workbook_path}")

        stats = import_workbook(
            workbook_path=workbook_path,
            publish=not options["draft"],
            archive_old=not options["keep_published"],
            force=options["force"],
        )

        self.stdout.write(self.style.SUCCESS("Workbook import completed."))
        self.stdout.write(f"Created exam definitions: {stats.created_definitions}")
        self.stdout.write(f"Created versions: {stats.created_versions}")
        self.stdout.write(f"Skipped versions: {stats.skipped_versions}")
        self.stdout.write(f"Created options: {stats.created_options}")
        self.stdout.write(f"Created sections: {stats.created_sections}")
        self.stdout.write(f"Created fields: {stats.created_fields}")
        self.stdout.write(f"Created ranges: {stats.created_ranges}")
        self.stdout.write(f"Created rules: {stats.created_rules}")
