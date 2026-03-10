from django.contrib import admin
from .models import Facility, LabRequest, Organization, Patient, Physician, Room, Signatory


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("legal_name", "display_name", "active")
    list_filter = ("active",)
    search_fields = ("legal_name", "display_name", "organization_code")


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("display_name", "organization", "contact_numbers", "active")
    list_filter = ("active", "organization")
    search_fields = ("display_name", "facility_code", "organization__legal_name")
    autocomplete_fields = ("organization",)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "patient_code", "sex", "birth_date")
    search_fields = ("full_name", "patient_code")


@admin.register(Physician)
class PhysicianAdmin(admin.ModelAdmin):
    list_display = ("display_name", "physician_code", "active")
    list_filter = ("active",)
    search_fields = ("display_name", "physician_code")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("display_name", "room_code", "active")
    list_filter = ("active",)
    search_fields = ("display_name", "room_code")


@admin.register(Signatory)
class SignatoryAdmin(admin.ModelAdmin):
    list_display = ("display_name", "signatory_type", "license_no", "active")
    list_filter = ("signatory_type", "active")
    search_fields = ("display_name", "license_no")


@admin.register(LabRequest)
class LabRequestAdmin(admin.ModelAdmin):
    list_display = (
        "request_no",
        "case_number",
        "patient_name_snapshot",
        "facility_name_snapshot",
        "status",
        "request_datetime",
    )
    list_filter = ("status", "sex_snapshot", "facility")
    search_fields = (
        "request_no",
        "case_number",
        "patient_name_snapshot",
        "organization_name_snapshot",
        "facility_name_snapshot",
    )
    autocomplete_fields = ("patient", "facility", "physician", "room", "created_by")
