from django import forms

from apps.core.models import Facility, Organization, Physician, Room, Signatory


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("organization_code", "legal_name", "display_name", "active")
        widgets = {
            "organization_code": forms.TextInput(attrs={"class": "form-control"}),
            "legal_name": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = (
            "facility_code",
            "organization",
            "display_name",
            "address",
            "contact_numbers",
            "report_header_image",
            "active",
        )
        widgets = {
            "facility_code": forms.TextInput(attrs={"class": "form-control"}),
            "organization": forms.Select(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "contact_numbers": forms.TextInput(attrs={"class": "form-control"}),
            "report_header_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class PhysicianForm(forms.ModelForm):
    class Meta:
        model = Physician
        fields = ("physician_code", "display_name", "active")
        widgets = {
            "physician_code": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("room_code", "display_name", "active")
        widgets = {
            "room_code": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class SignatoryForm(forms.ModelForm):
    class Meta:
        model = Signatory
        fields = ("signatory_type", "display_name", "license_no", "signature_image", "active")
        widgets = {
            "signatory_type": forms.Select(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "license_no": forms.TextInput(attrs={"class": "form-control"}),
            "signature_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
