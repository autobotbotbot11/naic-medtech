from pathlib import Path

from django import forms

from apps.core.master_data_import import DEFAULT_MASTER_DATA_WORKBOOK
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization_code"].help_text = "Optional internal code for your own tracking."
        self.fields["display_name"].help_text = "Use this if the printed display name should differ from the legal name."
        self.fields["active"].help_text = "Turn this off instead of deleting the record."


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["facility_code"].help_text = "Optional internal code for the branch/facility."
        self.fields["organization"].help_text = "Choose the company/legal entity that owns this facility."
        self.fields["display_name"].help_text = "This name appears in request setup and can appear in reports."
        self.fields["address"].help_text = "This address appears in the report header."
        self.fields["contact_numbers"].help_text = "Example: (046) 412-1443 / (046) 507-1510"
        self.fields["report_header_image"].help_text = "Upload the logo or branding image used on printed reports."
        self.fields["active"].help_text = "Turn this off instead of deleting the record."


class PhysicianForm(forms.ModelForm):
    class Meta:
        model = Physician
        fields = ("physician_code", "display_name", "active")
        widgets = {
            "physician_code": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["physician_code"].help_text = "Optional internal code."
        self.fields["display_name"].help_text = "Use the name staff should see in the request form."
        self.fields["active"].help_text = "Turn this off instead of deleting the record."


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("room_code", "display_name", "active")
        widgets = {
            "room_code": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room_code"].help_text = "Optional internal code."
        self.fields["display_name"].help_text = "Example: ER, Ward 2, OPD, ICU."
        self.fields["active"].help_text = "Turn this off instead of deleting the record."


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["signatory_type"].help_text = "Choose whether this person signs as medtech or pathologist."
        self.fields["display_name"].help_text = "This name appears on reports."
        self.fields["license_no"].help_text = "Optional, if the clinic wants to store license details."
        self.fields["signature_image"].help_text = "Optional signature file for future report enhancements."
        self.fields["active"].help_text = "Turn this off instead of deleting the record."


class MasterDataImportForm(forms.Form):
    workbook_path = forms.CharField(
        label="Workbook path",
        initial=str(DEFAULT_MASTER_DATA_WORKBOOK),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workbook_path"].help_text = (
            "Use the clinic workbook path. Relative paths are resolved from the project root."
        )

    def clean_workbook_path(self):
        raw_value = self.cleaned_data["workbook_path"].strip()
        workbook_path = Path(raw_value)
        if not workbook_path.is_absolute():
            workbook_path = Path.cwd() / workbook_path

        if not workbook_path.exists():
            raise forms.ValidationError("Workbook file not found.")

        return str(workbook_path)
