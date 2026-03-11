from django import forms
from django.utils.text import slugify

from apps.common.choices import (
    ExamFieldDataTypeChoices,
    ExamFieldInputTypeChoices,
    ExamRuleTypeChoices,
    RenderLayoutTypeChoices,
    SexChoices,
)
from apps.exams.builder import ensure_render_profile
from apps.exams.models import (
    ExamDefinition,
    ExamField,
    ExamFieldReferenceRange,
    ExamFieldSelectOption,
    ExamOption,
    ExamRenderProfile,
    ExamRule,
    ExamSection,
)


REFERENCE_RANGE_CHOICES = (
    ("numeric_between", "Between two values"),
    ("numeric_less_than", "Less than a value"),
    ("numeric_greater_than", "Greater than a value"),
    ("text_only", "Text only / display only"),
)


FIELD_INPUT_TYPE_HELP = {
    ExamFieldInputTypeChoices.TEXT: "Short free-text value.",
    ExamFieldInputTypeChoices.TEXTAREA: "Longer notes or descriptive result.",
    ExamFieldInputTypeChoices.INTEGER: "Whole numbers only.",
    ExamFieldInputTypeChoices.DECIMAL: "Numbers that may contain decimals.",
    ExamFieldInputTypeChoices.SELECT: "Dropdown with predefined choices.",
    ExamFieldInputTypeChoices.DATE: "Calendar date only.",
    ExamFieldInputTypeChoices.DATETIME: "Date and time value.",
    ExamFieldInputTypeChoices.BOOLEAN: "Yes / No choice.",
    ExamFieldInputTypeChoices.ATTACHMENT: "File upload such as an image or scanned result.",
    ExamFieldInputTypeChoices.DISPLAY_NOTE: "Display-only note block; not a data field.",
    ExamFieldInputTypeChoices.GROUPED_MEASUREMENT: "Advanced grouped values. Needs grouped config before publish.",
}


def default_data_type_for_input(input_type):
    mapping = {
        ExamFieldInputTypeChoices.TEXT: ExamFieldDataTypeChoices.STRING,
        ExamFieldInputTypeChoices.TEXTAREA: ExamFieldDataTypeChoices.STRING,
        ExamFieldInputTypeChoices.INTEGER: ExamFieldDataTypeChoices.INT,
        ExamFieldInputTypeChoices.DECIMAL: ExamFieldDataTypeChoices.DECIMAL,
        ExamFieldInputTypeChoices.SELECT: ExamFieldDataTypeChoices.STRING,
        ExamFieldInputTypeChoices.DATE: ExamFieldDataTypeChoices.DATE,
        ExamFieldInputTypeChoices.DATETIME: ExamFieldDataTypeChoices.DATETIME,
        ExamFieldInputTypeChoices.BOOLEAN: ExamFieldDataTypeChoices.BOOLEAN,
        ExamFieldInputTypeChoices.ATTACHMENT: ExamFieldDataTypeChoices.STRING,
        ExamFieldInputTypeChoices.DISPLAY_NOTE: ExamFieldDataTypeChoices.STRING,
        ExamFieldInputTypeChoices.GROUPED_MEASUREMENT: ExamFieldDataTypeChoices.JSON,
    }
    return mapping[input_type]


class ExamDefinitionForm(forms.ModelForm):
    exam_code = forms.SlugField(required=False)

    class Meta:
        model = ExamDefinition
        fields = ["exam_code", "exam_name", "category", "description", "active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exam_code"].help_text = "Optional. Leave blank to auto-generate from the exam name."
        self.fields["exam_name"].help_text = "The staff-facing name of the exam."
        self.fields["category"].help_text = "Optional grouping label such as Chemistry, Serology, or Hematology."
        self.fields["description"].help_text = "Optional internal description for admins."
        self.fields["active"].help_text = "Turn this off instead of deleting the exam definition."
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_exam_code(self):
        exam_code = self.cleaned_data.get("exam_code", "").strip()
        exam_name = self.cleaned_data.get("exam_name", "").strip()
        if not exam_code and exam_name:
            exam_code = slugify(exam_name)[:64]
        if not exam_code:
            raise forms.ValidationError("Provide an exam code or an exam name that can generate one.")

        queryset = ExamDefinition.objects.filter(exam_code=exam_code)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("That exam code is already in use.")
        return exam_code


class ExamOptionForm(forms.ModelForm):
    option_key = forms.SlugField(required=False)

    class Meta:
        model = ExamOption
        fields = ["option_key", "option_label", "sort_order", "active"]

    def __init__(self, *args, **kwargs):
        self.exam_version = kwargs.pop("exam_version", None)
        super().__init__(*args, **kwargs)
        self.fields["option_key"].help_text = "Optional. Leave blank to auto-generate from the option label."
        self.fields["option_label"].help_text = "This is the package/test name shown to staff."
        self.fields["sort_order"].help_text = "Lower numbers appear first."
        self.fields["active"].help_text = "Turn this off instead of deleting the option."
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_option_key(self):
        option_key = self.cleaned_data.get("option_key", "").strip()
        option_label = self.cleaned_data.get("option_label", "").strip()
        if not option_key and option_label:
            option_key = slugify(option_label)[:128]
        if not option_key:
            raise forms.ValidationError("Provide an option key or an option label that can generate one.")

        exam_version = self.exam_version or self.instance.exam_version
        queryset = ExamOption.objects.filter(exam_version=exam_version, option_key=option_key)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("That option key already exists in this draft.")
        return option_key

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.exam_version:
            instance.exam_version = self.exam_version
        if commit:
            instance.save()
        return instance


class ExamSectionForm(forms.ModelForm):
    section_key = forms.SlugField(required=False)

    class Meta:
        model = ExamSection
        fields = ["section_key", "section_label", "sort_order", "active"]

    def __init__(self, *args, **kwargs):
        self.exam_version = kwargs.pop("exam_version", None)
        super().__init__(*args, **kwargs)
        self.fields["section_key"].help_text = "Optional. Leave blank to auto-generate from the section label."
        self.fields["section_label"].help_text = "The title shown inside the report or encoder."
        self.fields["sort_order"].help_text = "Lower numbers appear first."
        self.fields["active"].help_text = "Turn this off instead of deleting the section."
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_section_key(self):
        section_key = self.cleaned_data.get("section_key", "").strip()
        section_label = self.cleaned_data.get("section_label", "").strip()
        if not section_key and section_label:
            section_key = slugify(section_label)[:128]
        if not section_key:
            raise forms.ValidationError("Provide a section key or a section label that can generate one.")

        exam_version = self.exam_version or self.instance.exam_version
        queryset = ExamSection.objects.filter(exam_version=exam_version, section_key=section_key)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("That section key already exists in this draft.")
        return section_key

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.exam_version:
            instance.exam_version = self.exam_version
        if commit:
            instance.save()
        return instance


class ExamFieldForm(forms.ModelForm):
    field_key = forms.SlugField(required=False)
    data_type = forms.ChoiceField(
        required=False,
        choices=[("", "Auto from input type")] + list(ExamFieldDataTypeChoices.choices),
    )
    config_json = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 8, "class": "form-control"}),
    )

    class Meta:
        model = ExamField
        fields = [
            "section",
            "field_key",
            "field_label",
            "input_type",
            "data_type",
            "unit",
            "required",
            "sort_order",
            "default_value",
            "help_text",
            "placeholder_text",
            "reference_text",
            "supports_attachment",
            "config_json",
            "active",
        ]
        widgets = {
            "help_text": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.exam_version = kwargs.pop("exam_version", None)
        super().__init__(*args, **kwargs)
        exam_version = self.exam_version or getattr(self.instance, "exam_version", None)
        if exam_version:
            self.fields["section"].queryset = exam_version.sections.order_by("sort_order", "id")
        else:
            self.fields["section"].queryset = ExamSection.objects.none()
        self.fields["section"].required = False
        self.fields["field_key"].help_text = "Optional. Leave blank to auto-generate from the field label."
        self.fields["field_label"].help_text = "The visible label shown in encoding and printing."
        self.fields["input_type"].help_text = "Choose how staff will enter or view this field."
        self.fields["data_type"].help_text = "Usually safe to leave on auto."
        self.fields["unit"].help_text = "Optional unit like mg/dL or mmHg."
        self.fields["required"].help_text = "If checked, staff must supply a value before saving."
        self.fields["sort_order"].help_text = "Lower numbers appear first."
        self.fields["default_value"].help_text = "Optional starting value."
        self.fields["help_text"].help_text = "Optional internal guidance shown in the encoder."
        self.fields["placeholder_text"].help_text = "Optional placeholder text."
        self.fields["reference_text"].help_text = "Optional visible reference text shown on forms and prints."
        self.fields["supports_attachment"].help_text = "Automatically enabled for attachment fields."
        self.fields["config_json"].help_text = (
            "Advanced only. Leave blank for normal fields. "
            "Grouped measurements need a `grouped_fields` list before publishing."
        )
        self.fields["active"].help_text = "Turn this off instead of deleting the field."
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_field_key(self):
        field_key = self.cleaned_data.get("field_key", "").strip()
        field_label = self.cleaned_data.get("field_label", "").strip()
        if not field_key and field_label:
            field_key = slugify(field_label)[:128]
        if not field_key:
            raise forms.ValidationError("Provide a field key or a field label that can generate one.")

        exam_version = self.exam_version or self.instance.exam_version
        queryset = ExamField.objects.filter(exam_version=exam_version, field_key=field_key)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("That field key already exists in this draft.")
        return field_key

    def clean(self):
        cleaned_data = super().clean()
        input_type = cleaned_data.get("input_type")
        if not input_type:
            return cleaned_data

        data_type = cleaned_data.get("data_type") or default_data_type_for_input(input_type)
        cleaned_data["data_type"] = data_type
        cleaned_data["config_json"] = cleaned_data.get("config_json") or {}

        if input_type == ExamFieldInputTypeChoices.ATTACHMENT:
            cleaned_data["supports_attachment"] = True
        if input_type == ExamFieldInputTypeChoices.DISPLAY_NOTE:
            cleaned_data["required"] = False
        if input_type != ExamFieldInputTypeChoices.ATTACHMENT:
            cleaned_data["supports_attachment"] = bool(cleaned_data.get("supports_attachment"))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.exam_version:
            instance.exam_version = self.exam_version
        if commit:
            instance.save()
        return instance


class ExamFieldSelectOptionForm(forms.ModelForm):
    option_value = forms.CharField(required=False)

    class Meta:
        model = ExamFieldSelectOption
        fields = ["option_value", "option_label", "sort_order", "active"]

    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop("field", None)
        super().__init__(*args, **kwargs)
        self.fields["option_value"].help_text = "Optional. Leave blank to auto-generate from the option label."
        self.fields["option_label"].help_text = "The visible choice label shown to staff."
        self.fields["sort_order"].help_text = "Lower numbers appear first."
        self.fields["active"].help_text = "Turn this off instead of deleting the choice."
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_option_value(self):
        option_value = self.cleaned_data.get("option_value", "").strip()
        option_label = self.cleaned_data.get("option_label", "").strip()
        if not option_value and option_label:
            option_value = slugify(option_label)
        if not option_value:
            raise forms.ValidationError("Provide an option value or an option label that can generate one.")

        field = self.field or self.instance.field
        queryset = ExamFieldSelectOption.objects.filter(field=field, option_value=option_value)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("That option value already exists for this field.")
        return option_value

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.field:
            instance.field = self.field
        if commit:
            instance.save()
        return instance


class ExamReferenceRangeForm(forms.ModelForm):
    range_type = forms.ChoiceField(choices=REFERENCE_RANGE_CHOICES)

    class Meta:
        model = ExamFieldReferenceRange
        fields = [
            "option_scope",
            "sex_scope",
            "range_type",
            "min_numeric",
            "max_numeric",
            "reference_text",
            "abnormal_rule",
            "sort_order",
        ]

    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop("field", None)
        super().__init__(*args, **kwargs)
        field = self.field or self.instance.field
        exam_version = field.exam_version if field else None
        if exam_version:
            self.fields["option_scope"].queryset = exam_version.options.order_by("sort_order", "id")
        else:
            self.fields["option_scope"].queryset = ExamOption.objects.none()
        self.fields["option_scope"].required = False
        self.fields["sex_scope"].required = False
        self.fields["sex_scope"].choices = [("", "All sexes")] + list(SexChoices.choices)
        self.fields["option_scope"].help_text = "Optional. Use this if the range only applies to a specific exam option/package."
        self.fields["sex_scope"].help_text = "Optional. Use this when normal values differ by sex."
        self.fields["range_type"].help_text = "Choose how the numeric rule should be interpreted."
        self.fields["reference_text"].help_text = "Text shown to staff and on prints, such as `3.5 - 5.3`."
        self.fields["abnormal_rule"].help_text = "Optional internal note about how the abnormal flag should be interpreted."
        self.fields["sort_order"].help_text = "Lower numbers appear first."
        for form_field in self.fields.values():
            form_field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        range_type = cleaned_data.get("range_type")
        min_numeric = cleaned_data.get("min_numeric")
        max_numeric = cleaned_data.get("max_numeric")

        if range_type == "numeric_between":
            if min_numeric is None or max_numeric is None:
                raise forms.ValidationError("Between ranges need both minimum and maximum values.")
            if min_numeric > max_numeric:
                raise forms.ValidationError("The minimum value cannot be greater than the maximum value.")
        elif range_type == "numeric_less_than" and max_numeric is None:
            raise forms.ValidationError("Less-than ranges need a maximum value.")
        elif range_type == "numeric_greater_than" and min_numeric is None:
            raise forms.ValidationError("Greater-than ranges need a minimum value.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.field:
            instance.field = self.field
        if commit:
            instance.save()
        return instance


class ExamRuleForm(forms.ModelForm):
    rule_type = forms.ChoiceField(
        choices=[
            (ExamRuleTypeChoices.VISIBILITY, "Show only when conditions match"),
            (ExamRuleTypeChoices.REQUIREMENT, "Require value when conditions match"),
        ]
    )
    target_type = forms.ChoiceField(
        choices=[
            ("field", "Field"),
            ("section", "Section"),
        ]
    )
    target_field = forms.ModelChoiceField(queryset=ExamField.objects.none(), required=False)
    target_section = forms.ModelChoiceField(queryset=ExamSection.objects.none(), required=False)
    option_scopes = forms.ModelMultipleChoiceField(queryset=ExamOption.objects.none(), required=False)
    sex_scope = forms.ChoiceField(required=False, choices=[("", "Any sex")] + list(SexChoices.choices))

    class Meta:
        model = ExamRule
        fields = [
            "rule_type",
            "target_type",
            "target_field",
            "target_section",
            "option_scopes",
            "sex_scope",
            "sort_order",
            "active",
        ]

    def __init__(self, *args, **kwargs):
        self.exam_version = kwargs.pop("exam_version", None)
        super().__init__(*args, **kwargs)
        exam_version = self.exam_version or getattr(self.instance, "exam_version", None)
        if exam_version:
            self.fields["target_field"].queryset = exam_version.fields.order_by("sort_order", "id")
            self.fields["target_section"].queryset = exam_version.sections.order_by("sort_order", "id")
            self.fields["option_scopes"].queryset = exam_version.options.order_by("sort_order", "id")
        self.fields["rule_type"].help_text = "Choose whether the rule shows something or makes it required."
        self.fields["target_type"].help_text = "Choose whether the rule affects a field or a whole section."
        self.fields["target_field"].help_text = "Only used when the target type is Field."
        self.fields["target_section"].help_text = "Only used when the target type is Section."
        self.fields["option_scopes"].help_text = "Optional. The rule will apply only when one of these exam options is selected."
        self.fields["sex_scope"].help_text = "Optional. The rule will apply only when the patient sex matches this value."
        self.fields["sort_order"].help_text = "Lower numbers are evaluated first."
        self.fields["active"].help_text = "Turn this off instead of deleting the rule."
        for form_field in self.fields.values():
            form_field.widget.attrs.setdefault("class", "form-control")

        if self.instance.pk:
            self.initial["target_type"] = self.instance.target_type
            if self.instance.target_type == "field":
                self.initial["target_field"] = self.instance.target_id
            elif self.instance.target_type == "section":
                self.initial["target_section"] = self.instance.target_id

            condition_json = self.instance.condition_json or {}
            option_keys = condition_json.get("exam_option_keys", [])
            if option_keys and exam_version:
                self.initial["option_scopes"] = list(exam_version.options.filter(option_key__in=option_keys).values_list("pk", flat=True))
            sex_values = condition_json.get("patient_sex", [])
            if len(sex_values) == 1:
                self.initial["sex_scope"] = sex_values[0]

    def clean(self):
        cleaned_data = super().clean()
        target_type = cleaned_data.get("target_type")
        target_field = cleaned_data.get("target_field")
        target_section = cleaned_data.get("target_section")
        option_scopes = cleaned_data.get("option_scopes")
        sex_scope = cleaned_data.get("sex_scope")

        if target_type == "field" and not target_field:
            raise forms.ValidationError("Choose the field affected by this rule.")
        if target_type == "section" and not target_section:
            raise forms.ValidationError("Choose the section affected by this rule.")
        if not option_scopes and not sex_scope:
            raise forms.ValidationError("Add at least one condition so the rule is not always on.")

        condition_json = {}
        if option_scopes:
            condition_json["exam_option_keys"] = [option.option_key for option in option_scopes]
        if sex_scope:
            condition_json["patient_sex"] = [sex_scope]
        cleaned_data["condition_json"] = condition_json

        if cleaned_data.get("rule_type") == ExamRuleTypeChoices.VISIBILITY:
            cleaned_data["effect_json"] = {"visible": True}
        else:
            cleaned_data["effect_json"] = {"required": True}
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.exam_version:
            instance.exam_version = self.exam_version
        instance.target_type = self.cleaned_data["target_type"]
        if instance.target_type == "field":
            instance.target_id = self.cleaned_data["target_field"].id
        else:
            instance.target_id = self.cleaned_data["target_section"].id
        instance.condition_json = self.cleaned_data["condition_json"]
        instance.effect_json = self.cleaned_data["effect_json"]
        if commit:
            instance.save()
        return instance


class ExamRenderProfileForm(forms.ModelForm):
    show_units = forms.BooleanField(required=False)
    show_reference_ranges = forms.BooleanField(required=False)
    advanced_config_json = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 8, "class": "form-control"}),
    )

    class Meta:
        model = ExamRenderProfile
        fields = ["layout_type", "show_units", "show_reference_ranges", "advanced_config_json", "active"]

    def __init__(self, *args, **kwargs):
        self.exam_version = kwargs.pop("exam_version", None)
        super().__init__(*args, **kwargs)
        render_profile = self.instance if self.instance.pk else ensure_render_profile(self.exam_version)
        config_json = dict(render_profile.config_json or {})
        self.initial.setdefault("show_units", config_json.pop("show_units", True))
        self.initial.setdefault("show_reference_ranges", config_json.pop("show_reference_ranges", True))
        self.initial.setdefault("advanced_config_json", config_json)
        self.fields["layout_type"].choices = list(RenderLayoutTypeChoices.choices)
        self.fields["layout_type"].help_text = "Choose the general print layout."
        self.fields["show_units"].help_text = "Show field units on forms and prints when available."
        self.fields["show_reference_ranges"].help_text = "Show reference ranges on forms and prints when available."
        self.fields["advanced_config_json"].help_text = (
            "Advanced only. Existing specialized render settings stay here for imported exams. "
            "Leave unchanged unless you know exactly what needs to change."
        )
        self.fields["active"].help_text = "Turn this off only if the draft should not use this render profile."
        for form_field in self.fields.values():
            form_field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.exam_version:
            instance.exam_version = self.exam_version
        advanced_config_json = self.cleaned_data.get("advanced_config_json") or {}
        config_json = dict(advanced_config_json)
        config_json["show_units"] = bool(self.cleaned_data.get("show_units"))
        config_json["show_reference_ranges"] = bool(self.cleaned_data.get("show_reference_ranges"))
        instance.config_json = config_json
        if commit:
            instance.save()
        return instance
