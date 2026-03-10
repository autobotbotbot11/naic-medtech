from django import forms
from django.utils import timezone

from apps.core.models import Facility, LabRequest, Physician, Room
from apps.core.services import (
    capture_facility_branding_snapshot,
    derive_age_snapshot_text,
    facility_snapshot_defaults,
    generate_request_no,
    resolve_patient,
)


class LabRequestCreateForm(forms.Form):
    patient_full_name = forms.CharField(max_length=255, label="Patient name")
    patient_sex = forms.ChoiceField(
        choices=[("", "---------"), *LabRequest._meta.get_field("sex_snapshot").choices],
        required=False,
        label="Sex",
    )
    patient_birth_date = forms.DateField(
        required=False,
        label="Birth date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    age_snapshot_text = forms.CharField(max_length=64, required=False, label="Age text")
    request_datetime = forms.DateTimeField(
        label="Request date/time",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    case_number = forms.CharField(max_length=64, required=False)
    facility = forms.ModelChoiceField(queryset=Facility.objects.none(), required=False)
    physician = forms.ModelChoiceField(queryset=Physician.objects.none(), required=False)
    room = forms.ModelChoiceField(queryset=Room.objects.none(), required=False)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_facilities = Facility.objects.filter(active=True).select_related("organization").order_by(
            "organization__legal_name",
            "display_name",
        )
        self.fields["facility"].queryset = active_facilities
        self.fields["physician"].queryset = Physician.objects.filter(active=True).order_by("display_name")
        self.fields["room"].queryset = Room.objects.filter(active=True).order_by("display_name")
        if not self.is_bound:
            self.initial.setdefault(
                "request_datetime",
                timezone.localtime(timezone.now()).strftime("%Y-%m-%dT%H:%M"),
            )
            if active_facilities.count() == 1:
                self.initial.setdefault("facility", active_facilities.first())

    def clean(self):
        cleaned_data = super().clean()
        if self.fields["facility"].queryset.exists() and not cleaned_data.get("facility"):
            self.add_error("facility", "Choose the facility/branch that owns this lab request.")
        return cleaned_data

    def save(self, user=None):
        cleaned_data = self.cleaned_data
        request_datetime = cleaned_data["request_datetime"]
        if timezone.is_naive(request_datetime):
            request_datetime = timezone.make_aware(request_datetime, timezone.get_current_timezone())

        patient = resolve_patient(
            full_name=cleaned_data["patient_full_name"],
            sex=cleaned_data["patient_sex"],
            birth_date=cleaned_data["patient_birth_date"],
        )
        age_snapshot_text = cleaned_data["age_snapshot_text"] or derive_age_snapshot_text(
            cleaned_data["patient_birth_date"],
            request_datetime,
        )
        facility = cleaned_data["facility"]
        physician = cleaned_data["physician"]
        room = cleaned_data["room"]
        snapshot_defaults = facility_snapshot_defaults(facility)

        lab_request = LabRequest.objects.create(
            request_no=generate_request_no(request_datetime),
            case_number=cleaned_data["case_number"],
            patient=patient,
            patient_name_snapshot=cleaned_data["patient_full_name"].strip(),
            age_snapshot_text=age_snapshot_text,
            sex_snapshot=cleaned_data["patient_sex"],
            request_datetime=request_datetime,
            **snapshot_defaults,
            physician=physician,
            physician_name_snapshot=physician.display_name if physician else "",
            room=room,
            room_name_snapshot=room.display_name if room else "",
            created_by=user if getattr(user, "is_authenticated", False) else None,
            notes=cleaned_data["notes"],
        )
        capture_facility_branding_snapshot(lab_request, facility)
        if lab_request.facility_header_image_snapshot:
            lab_request.save(update_fields=["facility_header_image_snapshot", "updated_at"])
        return lab_request
