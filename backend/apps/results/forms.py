from django import forms

from apps.common.choices import LabRequestItemStatusChoices, LabRequestStatusChoices, ExamVersionStatusChoices
from apps.exams.models import ExamDefinition, ExamOption
from apps.results.models import LabRequestItem


class LabRequestItemCreateForm(forms.Form):
    exam_definition = forms.ModelChoiceField(
        queryset=ExamDefinition.objects.filter(active=True).order_by("exam_name"),
        label="Exam",
    )
    exam_option = forms.ModelChoiceField(
        queryset=ExamOption.objects.none(),
        required=False,
        label="Exam option",
        empty_label="No specific option",
    )
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        selected_definition = None

        if self.is_bound:
            exam_definition_id = self.data.get("exam_definition")
            if exam_definition_id:
                selected_definition = ExamDefinition.objects.filter(pk=exam_definition_id).first()
        else:
            selected_definition = self.initial.get("exam_definition")
            if selected_definition and not isinstance(selected_definition, ExamDefinition):
                selected_definition = ExamDefinition.objects.filter(pk=selected_definition).first()

        if selected_definition:
            version = selected_definition.versions.filter(version_status=ExamVersionStatusChoices.PUBLISHED).order_by("-version_no").first()
            if version:
                self.fields["exam_option"].queryset = version.options.order_by("sort_order")

    def clean(self):
        cleaned_data = super().clean()
        exam_definition = cleaned_data.get("exam_definition")
        exam_option = cleaned_data.get("exam_option")

        if not exam_definition:
            return cleaned_data

        version = exam_definition.versions.filter(version_status=ExamVersionStatusChoices.PUBLISHED).order_by("-version_no").first()
        if not version:
            raise forms.ValidationError("The selected exam has no published version yet.")

        options_qs = version.options.order_by("sort_order")
        self.fields["exam_option"].queryset = options_qs

        if options_qs.exists() and not exam_option:
            self.add_error("exam_option", "Choose the specific exam option/package to use for this request item.")

        if exam_option and exam_option.exam_version_id != version.id:
            self.add_error("exam_option", "The selected option does not belong to the current published exam version.")

        cleaned_data["exam_version"] = version
        return cleaned_data

    def save(self, lab_request, user=None):
        exam_definition = self.cleaned_data["exam_definition"]
        exam_version = self.cleaned_data["exam_version"]
        exam_option = self.cleaned_data.get("exam_option")

        item = LabRequestItem.objects.create(
            lab_request=lab_request,
            exam_definition=exam_definition,
            exam_definition_version=exam_version,
            exam_option=exam_option,
            item_status=LabRequestItemStatusChoices.ENCODING,
            created_by=user if getattr(user, "is_authenticated", False) else None,
            notes=self.cleaned_data["notes"],
        )

        if lab_request.status == LabRequestStatusChoices.DRAFT:
            lab_request.status = LabRequestStatusChoices.IN_PROGRESS
            lab_request.save(update_fields=["status", "updated_at"])

        return item
