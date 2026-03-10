from django.db import models
from apps.common.choices import (
    LabRequestStatusChoices,
    SexChoices,
    SignatoryTypeChoices,
)
from apps.common.models import TimeStampedModel


class Organization(TimeStampedModel):
    organization_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    legal_name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["legal_name"]

    def __str__(self):
        return self.display_name or self.legal_name


class Facility(TimeStampedModel):
    facility_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        related_name="facilities",
    )
    display_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_numbers = models.CharField(max_length=255, blank=True)
    report_header_image = models.ImageField(upload_to="facility_branding/", blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["organization__legal_name", "display_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "display_name"],
                name="uq_facility_name_per_organization",
            ),
        ]

    def __str__(self):
        return self.display_name


class Patient(TimeStampedModel):
    patient_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=16, choices=SexChoices.choices, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    contact_no = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Physician(TimeStampedModel):
    physician_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    display_name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class Room(TimeStampedModel):
    room_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    display_name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class Signatory(TimeStampedModel):
    signatory_type = models.CharField(max_length=32, choices=SignatoryTypeChoices.choices)
    display_name = models.CharField(max_length=255)
    license_no = models.CharField(max_length=128, blank=True)
    signature_image = models.ImageField(upload_to="signatures/", blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["signatory_type", "display_name"]

    def __str__(self):
        return f"{self.display_name} ({self.signatory_type})"


class LabRequest(TimeStampedModel):
    request_no = models.CharField(max_length=64, unique=True)
    case_number = models.CharField(max_length=64, blank=True)
    patient = models.ForeignKey(
        "core.Patient",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    patient_name_snapshot = models.CharField(max_length=255)
    age_snapshot_text = models.CharField(max_length=64, blank=True)
    sex_snapshot = models.CharField(max_length=16, choices=SexChoices.choices, blank=True)
    request_datetime = models.DateTimeField()
    facility = models.ForeignKey(
        "core.Facility",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    organization_name_snapshot = models.CharField(max_length=255, blank=True)
    facility_name_snapshot = models.CharField(max_length=255, blank=True)
    facility_address_snapshot = models.TextField(blank=True)
    facility_contact_numbers_snapshot = models.CharField(max_length=255, blank=True)
    facility_header_image_snapshot = models.ImageField(
        upload_to="request_branding/%Y/%m/",
        blank=True,
        null=True,
    )
    physician = models.ForeignKey(
        "core.Physician",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    physician_name_snapshot = models.CharField(max_length=255, blank=True)
    room = models.ForeignKey(
        "core.Room",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    room_name_snapshot = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_lab_requests",
    )
    status = models.CharField(
        max_length=32,
        choices=LabRequestStatusChoices.choices,
        default=LabRequestStatusChoices.DRAFT,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-request_datetime", "-id"]
        indexes = [
            models.Index(fields=["request_no"]),
            models.Index(fields=["case_number"]),
            models.Index(fields=["request_datetime"]),
            models.Index(fields=["status"]),
            models.Index(fields=["facility"]),
        ]

    def __str__(self):
        return self.request_no
