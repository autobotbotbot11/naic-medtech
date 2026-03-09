from django.utils import timezone

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
