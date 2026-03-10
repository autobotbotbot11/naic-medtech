from collections import defaultdict
from decimal import Decimal, InvalidOperation

from django import forms
from django.db import transaction
from django.utils import timezone

from apps.common.choices import (
    ExamFieldInputTypeChoices,
    ExamRuleTypeChoices,
    LabRequestItemStatusChoices,
    LabRequestStatusChoices,
    SignatoryTypeChoices,
)
from apps.core.models import Signatory
from apps.results.models import Attachment, LabResultValue

SIGNATORY_FIELD_NAMES = ("medtech_signatory", "pathologist_signatory")


def build_rule_context(item):
    exam_option_keys = []
    if item.exam_option:
        exam_option_keys.append(item.exam_option.option_key)

    patient_sex = []
    if item.lab_request.sex_snapshot:
        patient_sex.append(item.lab_request.sex_snapshot)

    item_status = []
    if item.item_status:
        item_status.append(item.item_status)

    return {
        "exam_option_keys": exam_option_keys,
        "patient_sex": patient_sex,
        "item_status": item_status,
    }


def condition_matches(condition, context):
    if not condition:
        return True

    for key, expected_values in condition.items():
        actual_values = context.get(key, [])
        if not isinstance(expected_values, list):
            expected_values = [expected_values]
        if not isinstance(actual_values, list):
            actual_values = [actual_values]

        if not any(value in actual_values for value in expected_values):
            return False

    return True


def build_visibility_maps(item):
    visibility_rules = defaultdict(list)
    requirement_rules = defaultdict(list)

    for rule in item.exam_definition_version.rules.filter(active=True).order_by("sort_order", "id"):
        target_key = (rule.target_type, rule.target_id)
        if rule.rule_type == ExamRuleTypeChoices.VISIBILITY:
            visibility_rules[target_key].append(rule)
        elif rule.rule_type == ExamRuleTypeChoices.REQUIREMENT:
            requirement_rules[target_key].append(rule)

    return visibility_rules, requirement_rules


def target_is_visible(target_type, target_id, visibility_rules, context):
    rules = visibility_rules.get((target_type, target_id), [])
    if not rules:
        return True
    return any(condition_matches(rule.condition_json, context) for rule in rules)


def field_is_required(field, requirement_rules, context):
    if field.required:
        return True

    rules = requirement_rules.get(("field", field.id), [])
    for rule in rules:
        if condition_matches(rule.condition_json, context) and rule.effect_json.get("required"):
            return True

    return False


def make_widget_attrs(field):
    attrs = {"class": "form-control"}
    if field.input_type == ExamFieldInputTypeChoices.DECIMAL:
        attrs["step"] = "0.01"
    if field.input_type == ExamFieldInputTypeChoices.INTEGER:
        attrs["step"] = "1"
    return attrs


def make_form_field(field, required):
    label = field.field_label
    if field.unit:
        label = f"{label} ({field.unit})"

    if field.input_type == ExamFieldInputTypeChoices.TEXT:
        return forms.CharField(required=required, label=label, widget=forms.TextInput(attrs=make_widget_attrs(field)))
    if field.input_type == ExamFieldInputTypeChoices.TEXTAREA:
        return forms.CharField(required=required, label=label, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
    if field.input_type == ExamFieldInputTypeChoices.DECIMAL:
        return forms.DecimalField(required=required, label=label, widget=forms.NumberInput(attrs=make_widget_attrs(field)))
    if field.input_type == ExamFieldInputTypeChoices.INTEGER:
        return forms.IntegerField(required=required, label=label, widget=forms.NumberInput(attrs=make_widget_attrs(field)))
    if field.input_type == ExamFieldInputTypeChoices.SELECT:
        choices = [("", "---------")]
        choices.extend((option.option_value, option.option_label) for option in field.select_options.order_by("sort_order", "id"))
        return forms.ChoiceField(required=required, label=label, choices=choices, widget=forms.Select(attrs={"class": "form-control"}))
    if field.input_type == ExamFieldInputTypeChoices.DATE:
        return forms.DateField(required=required, label=label, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    if field.input_type == ExamFieldInputTypeChoices.DATETIME:
        return forms.DateTimeField(
            required=required,
            label=label,
            input_formats=["%Y-%m-%dT%H:%M"],
            widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        )
    if field.input_type == ExamFieldInputTypeChoices.BOOLEAN:
        return forms.TypedChoiceField(
            required=required,
            label=label,
            choices=[("", "---------"), ("true", "Yes"), ("false", "No")],
            coerce=lambda value: {"true": True, "false": False}.get(value),
            empty_value=None,
            widget=forms.Select(attrs={"class": "form-control"}),
        )
    if field.input_type == ExamFieldInputTypeChoices.ATTACHMENT:
        return forms.FileField(required=required, label=label, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))

    return forms.CharField(required=required, label=label, widget=forms.TextInput(attrs=make_widget_attrs(field)))


def existing_initial_for_field(result_value, field):
    if not result_value:
        return None

    if field.input_type == ExamFieldInputTypeChoices.SELECT:
        return result_value.selected_option_value
    if field.input_type == ExamFieldInputTypeChoices.DECIMAL:
        return result_value.value_number
    if field.input_type == ExamFieldInputTypeChoices.INTEGER:
        return int(result_value.value_number) if result_value.value_number is not None else None
    if field.input_type == ExamFieldInputTypeChoices.DATE:
        return result_value.value_date
    if field.input_type == ExamFieldInputTypeChoices.DATETIME:
        if result_value.value_datetime:
            current_value = result_value.value_datetime
            if timezone.is_aware(current_value):
                current_value = timezone.localtime(current_value)
            return current_value.strftime("%Y-%m-%dT%H:%M")
        return None
    if field.input_type == ExamFieldInputTypeChoices.BOOLEAN:
        if result_value.value_boolean is True:
            return "true"
        if result_value.value_boolean is False:
            return "false"
        return None

    return result_value.value_text


def get_applicable_reference_range(field, item):
    candidate_ranges = []
    for reference_range in field.reference_ranges.all():
        if reference_range.sex_scope and reference_range.sex_scope != item.lab_request.sex_snapshot:
            continue
        if reference_range.option_scope_id and reference_range.option_scope_id != item.exam_option_id:
            continue

        specificity = 0
        if reference_range.option_scope_id:
            specificity += 2
        if reference_range.sex_scope:
            specificity += 1

        candidate_ranges.append((specificity, reference_range.sort_order, reference_range))

    if not candidate_ranges:
        return None

    candidate_ranges.sort(key=lambda value: (-value[0], value[1]))
    return candidate_ranges[0][2]


def evaluate_abnormal_flag(field, item, numeric_value):
    if numeric_value in (None, ""):
        return False, ""

    try:
        comparable_value = Decimal(str(numeric_value))
    except (InvalidOperation, TypeError, ValueError):
        return False, ""

    reference_range = get_applicable_reference_range(field, item)
    if not reference_range:
        return False, ""

    if reference_range.range_type == "numeric_between":
        if reference_range.min_numeric is not None and comparable_value < reference_range.min_numeric:
            return True, f"Below normal range ({reference_range.reference_text})"
        if reference_range.max_numeric is not None and comparable_value > reference_range.max_numeric:
            return True, f"Above normal range ({reference_range.reference_text})"
    elif reference_range.range_type == "numeric_less_than":
        if reference_range.max_numeric is not None and comparable_value >= reference_range.max_numeric:
            return True, f"Above limit ({reference_range.reference_text})"
    elif reference_range.range_type == "numeric_greater_than":
        if reference_range.min_numeric is not None and comparable_value <= reference_range.min_numeric:
            return True, f"Below limit ({reference_range.reference_text})"

    return False, ""


def result_entry_schema(item):
    context = build_rule_context(item)
    visibility_rules, requirement_rules = build_visibility_maps(item)
    existing_results = {
        result_value.field_id: result_value
        for result_value in item.result_values.select_related("field")
    }
    existing_attachments = {
        attachment.field_id: attachment
        for attachment in item.attachments.select_related("field")
        if attachment.field_id
    }

    groups = []
    group_lookup = {}
    bindings = []

    def get_group(section):
        group_key = section.id if section else "general"
        if group_key not in group_lookup:
            group_lookup[group_key] = {
                "title": section.section_label if section else "",
                "section": section,
                "entries": [],
            }
            groups.append(group_lookup[group_key])
        return group_lookup[group_key]

    form_fields = {
        "medtech_signatory": forms.ModelChoiceField(
            queryset=Signatory.objects.filter(
                active=True,
                signatory_type=SignatoryTypeChoices.MEDTECH,
            ).order_by("display_name"),
            required=False,
            label="Medical Technologist",
            widget=forms.Select(attrs={"class": "form-control"}),
        ),
        "pathologist_signatory": forms.ModelChoiceField(
            queryset=Signatory.objects.filter(
                active=True,
                signatory_type=SignatoryTypeChoices.PATHOLOGIST,
            ).order_by("display_name"),
            required=False,
            label="Pathologist",
            widget=forms.Select(attrs={"class": "form-control"}),
        ),
    }
    initial_values = {
        "medtech_signatory": item.medtech_signatory_id,
        "pathologist_signatory": item.pathologist_signatory_id,
    }
    all_fields = item.exam_definition_version.fields.select_related("section").prefetch_related(
        "select_options",
        "reference_ranges",
    ).order_by("sort_order", "id")

    for field in all_fields:
        if field.section and not target_is_visible("section", field.section_id, visibility_rules, context):
            continue
        if not target_is_visible("field", field.id, visibility_rules, context):
            continue

        required = field_is_required(field, requirement_rules, context)
        group = get_group(field.section)
        reference_range = get_applicable_reference_range(field, item)
        reference_text = reference_range.reference_text if reference_range else field.reference_text
        existing_value = existing_results.get(field.id)
        existing_attachment = existing_attachments.get(field.id)

        if field.input_type == ExamFieldInputTypeChoices.DISPLAY_NOTE:
            group["entries"].append(
                {
                    "kind": "note",
                    "field": field,
                    "text": field.help_text or field.reference_text or field.field_label,
                }
            )
            bindings.append({"kind": "note", "field": field})
            continue

        if field.input_type == ExamFieldInputTypeChoices.GROUPED_MEASUREMENT:
            subfields = []
            existing_json = existing_value.value_json if existing_value else {}
            for subfield in field.config_json.get("grouped_fields", []):
                input_name = f"field_{field.id}__{subfield['key']}"
                form_fields[input_name] = forms.CharField(
                    required=False,
                    label=subfield["label"],
                    widget=forms.TextInput(attrs={"class": "form-control"}),
                )
                initial_values[input_name] = existing_json.get(subfield["key"], "")
                subfields.append(
                    {
                        "name": input_name,
                        "key": subfield["key"],
                        "label": subfield["label"],
                        "unit": subfield.get("unit", ""),
                    }
                )

            group["entries"].append(
                {
                    "kind": "grouped",
                    "field": field,
                    "required": required,
                    "reference_text": reference_text,
                    "help_text": field.help_text,
                    "subfields": subfields,
                }
            )
            bindings.append({"kind": "grouped", "field": field, "subfields": subfields})
            continue

        input_name = f"field_{field.id}"
        form_fields[input_name] = make_form_field(field, required)
        current_initial = existing_initial_for_field(existing_value, field)
        if current_initial not in (None, ""):
            initial_values[input_name] = current_initial

        group["entries"].append(
            {
                "kind": "field",
                "field": field,
                "name": input_name,
                "required": required,
                "reference_text": reference_text,
                "help_text": field.help_text,
                "existing_attachment": existing_attachment,
            }
        )
        bindings.append({"kind": "field", "field": field, "name": input_name})

    form_class = type("DynamicResultEntryForm", (forms.Form,), form_fields)
    return form_class, groups, bindings, initial_values


def build_result_entry(item, data=None, files=None):
    form_class, groups, bindings, initial_values = result_entry_schema(item)
    form = form_class(data=data or None, files=files or None, initial=initial_values)
    return form, groups, bindings


def update_request_status(lab_request):
    items = list(lab_request.items.all())
    if not items:
        lab_request.status = LabRequestStatusChoices.DRAFT
    elif all(item.result_values.exists() or item.attachments.exists() for item in items):
        lab_request.status = LabRequestStatusChoices.COMPLETED
    else:
        lab_request.status = LabRequestStatusChoices.IN_PROGRESS
    lab_request.save(update_fields=["status", "updated_at"])


def save_snapshot_defaults(result_value, field):
    result_value.field_key_snapshot = field.field_key
    result_value.field_label_snapshot = field.field_label
    result_value.section_key_snapshot = field.section.section_key if field.section else ""
    result_value.input_type_snapshot = field.input_type
    result_value.unit_snapshot = field.unit
    result_value.reference_text_snapshot = field.reference_text
    result_value.sort_order_snapshot = field.sort_order


def clear_value_columns(result_value):
    result_value.value_text = ""
    result_value.value_number = None
    result_value.value_boolean = None
    result_value.value_date = None
    result_value.value_datetime = None
    result_value.value_json = {}
    result_value.selected_option_value = ""
    result_value.selected_option_label_snapshot = ""
    result_value.abnormal_flag = False
    result_value.abnormal_reason = ""


@transaction.atomic
def persist_result_entry(item, cleaned_data, bindings, uploaded_by=None):
    item.medtech_signatory = cleaned_data.get("medtech_signatory")
    item.pathologist_signatory = cleaned_data.get("pathologist_signatory")

    existing_results = {
        result_value.field_id: result_value
        for result_value in item.result_values.select_related("field")
    }
    existing_attachments = {
        attachment.field_id: attachment
        for attachment in item.attachments.select_related("field")
        if attachment.field_id
    }

    for binding in bindings:
        field = binding["field"]

        if binding["kind"] == "note":
            continue

        result_value = existing_results.get(field.id)
        if not result_value:
            result_value = LabResultValue(lab_request_item=item, field=field)

        if binding["kind"] == "grouped":
            grouped_value = {}
            for subfield in binding["subfields"]:
                current_value = cleaned_data.get(subfield["name"])
                if current_value not in (None, ""):
                    grouped_value[subfield["key"]] = current_value

            if not grouped_value:
                if result_value.pk:
                    result_value.delete()
                continue

            save_snapshot_defaults(result_value, field)
            clear_value_columns(result_value)
            result_value.value_json = grouped_value
            result_value.value_text = ""
            result_value.save()
            existing_results[field.id] = result_value
            continue

        current_value = cleaned_data.get(binding["name"])

        if field.input_type == ExamFieldInputTypeChoices.ATTACHMENT:
            current_attachment = existing_attachments.get(field.id)
            if current_value:
                if current_attachment:
                    current_attachment.file.delete(save=False)
                    current_attachment.delete()
                current_attachment = Attachment.objects.create(
                    lab_request_item=item,
                    field=field,
                    attachment_type=field.field_key,
                    file=current_value,
                    original_name=current_value.name,
                    mime_type=getattr(current_value, "content_type", ""),
                    uploaded_by=uploaded_by if getattr(uploaded_by, "is_authenticated", False) else None,
                )
                existing_attachments[field.id] = current_attachment

            if not current_attachment:
                if result_value.pk:
                    result_value.delete()
                continue

            save_snapshot_defaults(result_value, field)
            clear_value_columns(result_value)
            result_value.value_text = current_attachment.original_name
            result_value.value_json = {
                "attachment_id": current_attachment.id,
                "file_name": current_attachment.original_name,
                "mime_type": current_attachment.mime_type,
            }
            result_value.save()
            existing_results[field.id] = result_value
            continue

        if current_value in (None, "", []):
            if result_value.pk:
                result_value.delete()
            continue

        save_snapshot_defaults(result_value, field)
        clear_value_columns(result_value)

        if field.input_type in {ExamFieldInputTypeChoices.TEXT, ExamFieldInputTypeChoices.TEXTAREA}:
            result_value.value_text = str(current_value)
        elif field.input_type == ExamFieldInputTypeChoices.DECIMAL:
            result_value.value_number = current_value
        elif field.input_type == ExamFieldInputTypeChoices.INTEGER:
            result_value.value_number = current_value
        elif field.input_type == ExamFieldInputTypeChoices.SELECT:
            result_value.selected_option_value = current_value
            selected_option = next(
                (option for option in field.select_options.all() if option.option_value == current_value),
                None,
            )
            result_value.selected_option_label_snapshot = selected_option.option_label if selected_option else ""
            result_value.value_text = result_value.selected_option_label_snapshot or current_value
        elif field.input_type == ExamFieldInputTypeChoices.DATE:
            result_value.value_date = current_value
        elif field.input_type == ExamFieldInputTypeChoices.DATETIME:
            if timezone.is_naive(current_value):
                current_value = timezone.make_aware(current_value, timezone.get_current_timezone())
            result_value.value_datetime = current_value
        elif field.input_type == ExamFieldInputTypeChoices.BOOLEAN:
            result_value.value_boolean = current_value
            result_value.value_text = "Yes" if current_value else "No"
        else:
            result_value.value_text = str(current_value)

        abnormal_flag, abnormal_reason = evaluate_abnormal_flag(field, item, result_value.value_number)
        result_value.abnormal_flag = abnormal_flag
        result_value.abnormal_reason = abnormal_reason
        reference_range = get_applicable_reference_range(field, item)
        result_value.reference_text_snapshot = reference_range.reference_text if reference_range else field.reference_text
        result_value.save()
        existing_results[field.id] = result_value

    item.item_status = LabRequestItemStatusChoices.FOR_REVIEW if item.result_values.exists() or item.attachments.exists() else LabRequestItemStatusChoices.ENCODING
    item.performed_at = item.performed_at or timezone.now()
    item.save(
        update_fields=[
            "item_status",
            "performed_at",
            "medtech_signatory",
            "pathologist_signatory",
            "updated_at",
        ]
    )
    update_request_status(item.lab_request)
