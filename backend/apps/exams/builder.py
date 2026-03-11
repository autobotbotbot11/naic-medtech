from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.common.choices import (
    ExamFieldInputTypeChoices,
    ExamRuleTypeChoices,
    ExamVersionStatusChoices,
    RenderLayoutTypeChoices,
)
from apps.exams.models import (
    ExamDefinitionVersion,
    ExamField,
    ExamFieldReferenceRange,
    ExamFieldSelectOption,
    ExamOption,
    ExamRenderProfile,
    ExamRule,
    ExamSection,
)


SUPPORTED_RULE_TYPES = {
    ExamRuleTypeChoices.VISIBILITY,
    ExamRuleTypeChoices.REQUIREMENT,
}


def manual_render_profile_defaults():
    return {
        "layout_type": RenderLayoutTypeChoices.RESULT_TABLE,
        "config_json": {
            "show_units": True,
            "show_reference_ranges": True,
        },
    }


def get_existing_draft(definition):
    return definition.versions.filter(version_status=ExamVersionStatusChoices.DRAFT).order_by("-version_no").first()


def get_latest_published(definition):
    return definition.versions.filter(version_status=ExamVersionStatusChoices.PUBLISHED).order_by("-version_no").first()


def get_next_version_no(definition):
    latest = definition.versions.order_by("-version_no").first()
    return 1 if latest is None else latest.version_no + 1


def ensure_render_profile(version):
    render_profile = getattr(version, "render_profile", None)
    if render_profile:
        return render_profile

    defaults = manual_render_profile_defaults()
    return ExamRenderProfile.objects.create(
        exam_version=version,
        layout_type=defaults["layout_type"],
        config_json=defaults["config_json"],
        active=True,
    )


@transaction.atomic
def create_draft_version(definition, *, user=None, source_version=None):
    existing_draft = get_existing_draft(definition)
    if existing_draft:
        return existing_draft, False

    source_version = source_version or get_latest_published(definition) or definition.versions.order_by("-version_no").first()
    draft = ExamDefinitionVersion.objects.create(
        exam_definition=definition,
        version_no=get_next_version_no(definition),
        version_status=ExamVersionStatusChoices.DRAFT,
        source_type="manual_builder",
        source_reference=(
            f"manual-builder:clone-v{source_version.version_no}"
            if source_version
            else "manual-builder:new-exam"
        ),
        change_summary="",
    )

    if not source_version:
        ensure_render_profile(draft)
        return draft, True

    option_map = {}
    for option in source_version.options.all().order_by("sort_order", "id"):
        option_map[option.id] = ExamOption.objects.create(
            exam_version=draft,
            option_key=option.option_key,
            option_label=option.option_label,
            sort_order=option.sort_order,
            active=option.active,
        )

    section_map = {}
    for section in source_version.sections.all().order_by("sort_order", "id"):
        section_map[section.id] = ExamSection.objects.create(
            exam_version=draft,
            section_key=section.section_key,
            section_label=section.section_label,
            sort_order=section.sort_order,
            active=section.active,
        )

    field_map = {}
    for field in source_version.fields.select_related("section").all().order_by("sort_order", "id"):
        field_map[field.id] = ExamField.objects.create(
            exam_version=draft,
            section=section_map.get(field.section_id),
            field_key=field.field_key,
            field_label=field.field_label,
            input_type=field.input_type,
            data_type=field.data_type,
            unit=field.unit,
            required=field.required,
            sort_order=field.sort_order,
            default_value=field.default_value,
            help_text=field.help_text,
            placeholder_text=field.placeholder_text,
            reference_text=field.reference_text,
            config_json=deepcopy(field.config_json),
            supports_attachment=field.supports_attachment,
            active=field.active,
        )

    for field in source_version.fields.all():
        cloned_field = field_map[field.id]
        for option in field.select_options.all().order_by("sort_order", "id"):
            ExamFieldSelectOption.objects.create(
                field=cloned_field,
                option_value=option.option_value,
                option_label=option.option_label,
                sort_order=option.sort_order,
                active=option.active,
            )
        for reference_range in field.reference_ranges.select_related("option_scope").all().order_by("sort_order", "id"):
            ExamFieldReferenceRange.objects.create(
                field=cloned_field,
                option_scope=option_map.get(reference_range.option_scope_id),
                sex_scope=reference_range.sex_scope,
                range_type=reference_range.range_type,
                min_numeric=reference_range.min_numeric,
                max_numeric=reference_range.max_numeric,
                reference_text=reference_range.reference_text,
                abnormal_rule=reference_range.abnormal_rule,
                sort_order=reference_range.sort_order,
            )

    for rule in source_version.rules.all().order_by("sort_order", "id"):
        target_id = rule.target_id
        if rule.target_type == "field":
            target_id = field_map[target_id].id
        elif rule.target_type == "section":
            target_id = section_map[target_id].id

        ExamRule.objects.create(
            exam_version=draft,
            rule_type=rule.rule_type,
            target_type=rule.target_type,
            target_id=target_id,
            condition_json=deepcopy(rule.condition_json),
            effect_json=deepcopy(rule.effect_json),
            sort_order=rule.sort_order,
            active=rule.active,
        )

    source_render_profile = getattr(source_version, "render_profile", None)
    if source_render_profile:
        ExamRenderProfile.objects.create(
            exam_version=draft,
            layout_type=source_render_profile.layout_type,
            config_json=deepcopy(source_render_profile.config_json),
            active=source_render_profile.active,
        )
    else:
        ensure_render_profile(draft)

    return draft, True


def validate_draft_version(version):
    errors = []

    if version.version_status != ExamVersionStatusChoices.DRAFT:
        errors.append("Only draft versions can be published.")
        return errors

    active_fields = list(version.fields.filter(active=True).select_related("section"))
    if not active_fields:
        errors.append("Add at least one active field before publishing.")

    render_profile = getattr(version, "render_profile", None)
    if render_profile is None:
        errors.append("Create the render profile before publishing.")
    elif not render_profile.layout_type:
        errors.append("Choose a print layout type before publishing.")

    version_option_ids = set(version.options.values_list("id", flat=True))
    version_option_keys = set(version.options.values_list("option_key", flat=True))
    version_field_ids = set(version.fields.values_list("id", flat=True))
    version_section_ids = set(version.sections.values_list("id", flat=True))

    for field in active_fields:
        if field.section_id and field.section_id not in version_section_ids:
            errors.append(f"Field '{field.field_label}' points to a section outside this draft.")

        if field.input_type == ExamFieldInputTypeChoices.SELECT:
            if not field.select_options.filter(active=True).exists():
                errors.append(f"Select field '{field.field_label}' needs at least one active choice.")

        if field.input_type == ExamFieldInputTypeChoices.GROUPED_MEASUREMENT:
            grouped_fields = field.config_json.get("grouped_fields", [])
            if not isinstance(grouped_fields, list) or not grouped_fields:
                errors.append(f"Grouped field '{field.field_label}' needs grouped field configuration.")
            else:
                for grouped_field in grouped_fields:
                    if not grouped_field.get("key") or not grouped_field.get("label"):
                        errors.append(f"Grouped field '{field.field_label}' has an incomplete grouped-field entry.")
                        break

        if field.input_type == ExamFieldInputTypeChoices.ATTACHMENT and not field.supports_attachment:
            errors.append(f"Attachment field '{field.field_label}' must support attachments.")

    for reference_range in ExamFieldReferenceRange.objects.filter(field__exam_version=version).select_related("field", "option_scope"):
        if reference_range.option_scope_id and reference_range.option_scope_id not in version_option_ids:
            errors.append(
                f"Reference range '{reference_range.reference_text or reference_range.range_type}' points to an option outside this draft."
            )

        if reference_range.range_type == "numeric_between":
            if reference_range.min_numeric is None or reference_range.max_numeric is None:
                errors.append(f"Range '{reference_range}' requires both minimum and maximum values.")
            elif reference_range.min_numeric > reference_range.max_numeric:
                errors.append(f"Range '{reference_range}' has a minimum greater than the maximum.")
        elif reference_range.range_type == "numeric_less_than":
            if reference_range.max_numeric is None:
                errors.append(f"Range '{reference_range}' requires a maximum value.")
        elif reference_range.range_type == "numeric_greater_than":
            if reference_range.min_numeric is None:
                errors.append(f"Range '{reference_range}' requires a minimum value.")

    for rule in version.rules.all():
        if rule.rule_type not in SUPPORTED_RULE_TYPES:
            errors.append(f"Rule '{rule}' uses an unsupported rule type for manual publishing.")
            continue

        if rule.target_type == "field" and rule.target_id not in version_field_ids:
            errors.append(f"Rule '{rule}' points to a field outside this draft.")
        elif rule.target_type == "section" and rule.target_id not in version_section_ids:
            errors.append(f"Rule '{rule}' points to a section outside this draft.")
        elif rule.target_type not in {"field", "section"}:
            errors.append(f"Rule '{rule}' has an unsupported target type.")

        condition_json = rule.condition_json or {}
        if not condition_json:
            errors.append(f"Rule '{rule}' needs at least one condition.")
            continue

        option_keys = condition_json.get("exam_option_keys", [])
        if option_keys and not set(option_keys).issubset(version_option_keys):
            errors.append(f"Rule '{rule}' references an exam option not found in this draft.")

        sex_values = condition_json.get("patient_sex", [])
        if any(value not in {"male", "female"} for value in sex_values):
            errors.append(f"Rule '{rule}' uses an invalid sex condition.")

        if rule.rule_type == ExamRuleTypeChoices.REQUIREMENT and not rule.effect_json.get("required"):
            errors.append(f"Rule '{rule}' must set a required effect.")
        if rule.rule_type == ExamRuleTypeChoices.VISIBILITY and not rule.effect_json.get("visible", True):
            errors.append(f"Rule '{rule}' must use the visible effect.")

    deduped = []
    seen = set()
    for error in errors:
        if error not in seen:
            deduped.append(error)
            seen.add(error)
    return deduped


@transaction.atomic
def publish_draft_version(version, *, user=None, change_summary=""):
    errors = validate_draft_version(version)
    if errors:
        raise ValidationError(errors)

    version.exam_definition.versions.filter(version_status=ExamVersionStatusChoices.PUBLISHED).exclude(pk=version.pk).update(
        version_status=ExamVersionStatusChoices.ARCHIVED
    )
    version.version_status = ExamVersionStatusChoices.PUBLISHED
    version.published_at = timezone.now()
    version.published_by = user if getattr(user, "is_authenticated", False) else None
    version.change_summary = change_summary
    version.save(
        update_fields=[
            "version_status",
            "published_at",
            "published_by",
            "change_summary",
        ]
    )
    ensure_render_profile(version)
    return version
