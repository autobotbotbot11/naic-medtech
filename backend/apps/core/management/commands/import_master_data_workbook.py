from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.core.master_data_import import import_master_data


class Command(BaseCommand):
    help = "Import physicians, rooms, and signatories from the clinic workbook."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="NAIC MEDTECH SYSTEM DATA.xlsx",
            help="Path to the workbook file to import.",
        )

    def handle(self, *args, **options):
        workbook_path = Path(options["file"])
        if not workbook_path.is_absolute():
            workbook_path = Path.cwd() / workbook_path

        if not workbook_path.exists():
            raise CommandError(f"Workbook not found: {workbook_path}")

        stats = import_master_data(workbook_path=workbook_path)

        self.stdout.write(self.style.SUCCESS("Master data import completed."))
        self.stdout.write(f"Workbook: {stats.workbook_path}")
        self.stdout.write(f"Physicians found: {stats.physician_source_count}")
        self.stdout.write(f"Rooms found: {stats.room_source_count}")
        self.stdout.write(f"Signatories found: {stats.signatory_source_count}")
        self.stdout.write(
            "Created/reactivated physicians: "
            f"{stats.physicians_created}/{stats.physicians_reactivated}"
        )
        self.stdout.write(
            "Created/reactivated rooms: "
            f"{stats.rooms_created}/{stats.rooms_reactivated}"
        )
        self.stdout.write(
            "Created/reactivated signatories: "
            f"{stats.signatories_created}/{stats.signatories_reactivated}"
        )
        self.stdout.write(f"Filled blank signatory licenses: {stats.signatories_license_filled}")
        if stats.warnings:
            self.stdout.write(self.style.WARNING("Warnings:"))
            for warning in stats.warnings:
                self.stdout.write(f"- {warning}")
