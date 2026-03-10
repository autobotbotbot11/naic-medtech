from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import LabRequest, Patient


def generate_request_no(request_datetime=None):
    current_dt = timezone.localtime(request_datetime or timezone.now())
    prefix = f"REQ-{current_dt:%Y%m%d}"
    latest_request = LabRequest.objects.filter(request_no__startswith=prefix).order_by("-request_no").first()
    next_sequence = 1
    if latest_request:
        try:
            next_sequence = int(latest_request.request_no.rsplit("-", 1)[-1]) + 1
        except (IndexError, ValueError):
            next_sequence = 1

    return f"{prefix}-{next_sequence:04d}"


def derive_age_snapshot_text(birth_date, reference_datetime):
    if not birth_date:
        return ""

    reference_date = timezone.localtime(reference_datetime).date() if timezone.is_aware(reference_datetime) else reference_datetime.date()
    years = reference_date.year - birth_date.year
    before_birthday = (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day)
    if before_birthday:
        years -= 1
    years = max(years, 0)
    return f"{years} y/o"


def resolve_patient(full_name, sex="", birth_date=None):
    patient = Patient.objects.filter(
        full_name__iexact=full_name.strip(),
        sex=sex,
        birth_date=birth_date,
    ).first()
    if patient:
        return patient

    return Patient.objects.create(
        full_name=full_name.strip(),
        sex=sex,
        birth_date=birth_date,
    )


def facility_snapshot_defaults(facility):
    if not facility:
        return {
            "facility": None,
            "organization_name_snapshot": "",
            "facility_name_snapshot": "",
            "facility_address_snapshot": "",
            "facility_contact_numbers_snapshot": "",
        }

    return {
        "facility": facility,
        "organization_name_snapshot": facility.organization.display_name or facility.organization.legal_name,
        "facility_name_snapshot": facility.display_name,
        "facility_address_snapshot": facility.address,
        "facility_contact_numbers_snapshot": facility.contact_numbers,
    }


def capture_facility_branding_snapshot(lab_request, facility):
    if not facility or not facility.report_header_image:
        return

    source_file = facility.report_header_image
    source_file.open("rb")
    try:
        filename = Path(source_file.name).name
        snapshot_name = f"{slugify(lab_request.request_no)}-{filename}"
        lab_request.facility_header_image_snapshot.save(
            snapshot_name,
            ContentFile(source_file.read()),
            save=False,
        )
    finally:
        source_file.close()
