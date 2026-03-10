from decimal import Decimal

from django.utils import timezone

from apps.common.choices import ExamFieldInputTypeChoices, RenderLayoutTypeChoices
from apps.results.services import (
    build_rule_context,
    build_visibility_maps,
    get_applicable_reference_range,
    target_is_visible,
)


def format_decimal(value):
    if value is None:
        return ""
    rendered = format(Decimal(str(value)), "f")
    rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def format_date(value):
    if not value:
        return ""
    return value.strftime("%b %d, %Y")


def format_datetime(value):
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime("%b %d, %Y %I:%M %p")


def value_display_for_field(field, result_value):
    if not result_value:
        return ""

    if field.input_type == ExamFieldInputTypeChoices.SELECT:
        return result_value.selected_option_label_snapshot or result_value.value_text
    if field.input_type == ExamFieldInputTypeChoices.DECIMAL:
        return format_decimal(result_value.value_number)
    if field.input_type == ExamFieldInputTypeChoices.INTEGER:
        return format_decimal(result_value.value_number)
    if field.input_type == ExamFieldInputTypeChoices.DATE:
        return format_date(result_value.value_date)
    if field.input_type == ExamFieldInputTypeChoices.DATETIME:
        return format_datetime(result_value.value_datetime)
    if field.input_type == ExamFieldInputTypeChoices.BOOLEAN:
        if result_value.value_boolean is True:
            return "Yes"
        if result_value.value_boolean is False:
            return "No"
        return ""
    if field.input_type == ExamFieldInputTypeChoices.ATTACHMENT:
        return result_value.value_text

    return result_value.value_text


def attachment_preview(attachment):
    if not attachment:
        return None

    mime_type = attachment.mime_type or ""
    return {
        "name": attachment.original_name or attachment.file.name,
        "url": attachment.file.url if attachment.file else "",
        "mime_type": mime_type,
        "is_image": mime_type.startswith("image/"),
    }


def safe_media_url(file_field):
    if not file_field:
        return ""

    try:
        return file_field.url
    except ValueError:
        return ""


def build_render_groups(item):
    context = build_rule_context(item)
    visibility_rules, _requirement_rules = build_visibility_maps(item)
    result_values_by_field_id = {
        result_value.field_id: result_value
        for result_value in item.result_values.select_related("field").order_by("sort_order_snapshot", "id")
    }
    attachments_by_field_id = {
        attachment.field_id: attachment
        for attachment in item.attachments.select_related("field")
        if attachment.field_id
    }

    groups = []
    group_lookup = {}
    all_fields = item.exam_definition_version.fields.select_related("section").prefetch_related(
        "reference_ranges",
        "select_options",
    ).order_by("sort_order", "id")

    def get_group(section):
        group_key = section.id if section else "general"
        if group_key not in group_lookup:
            group_lookup[group_key] = {
                "title": section.section_label if section else "",
                "section": section,
                "section_key": section.section_key if section else "",
                "entries": [],
            }
            groups.append(group_lookup[group_key])
        return group_lookup[group_key]

    for field in all_fields:
        if field.section and not target_is_visible("section", field.section_id, visibility_rules, context):
            continue
        if not target_is_visible("field", field.id, visibility_rules, context):
            continue

        group = get_group(field.section)
        result_value = result_values_by_field_id.get(field.id)
        attachment = attachments_by_field_id.get(field.id)
        applicable_range = get_applicable_reference_range(field, item)
        reference_text = ""
        if result_value and result_value.reference_text_snapshot:
            reference_text = result_value.reference_text_snapshot
        elif applicable_range and applicable_range.reference_text:
            reference_text = applicable_range.reference_text
        else:
            reference_text = field.reference_text

        if field.input_type == ExamFieldInputTypeChoices.DISPLAY_NOTE:
            group["entries"].append(
                {
                    "kind": "note",
                    "field_key": field.field_key,
                    "label": field.field_label,
                    "text": field.help_text or field.reference_text or field.field_label,
                }
            )
            continue

        if field.input_type == ExamFieldInputTypeChoices.GROUPED_MEASUREMENT:
            grouped_json = result_value.value_json if result_value else {}
            subrows = []
            for subfield in field.config_json.get("grouped_fields", []):
                current_value = grouped_json.get(subfield["key"], "")
                subrows.append(
                    {
                        "label": subfield["label"],
                        "unit": subfield.get("unit", ""),
                        "value_display": current_value or "-",
                        "has_value": current_value not in (None, ""),
                    }
                )

            group["entries"].append(
                {
                    "kind": "grouped",
                    "field_key": field.field_key,
                    "label": field.field_label,
                    "reference_text": reference_text,
                    "help_text": field.help_text,
                    "subrows": subrows,
                    "has_value": any(row["has_value"] for row in subrows),
                }
            )
            continue

        display_value = value_display_for_field(field, result_value)
        current_attachment = attachment_preview(attachment)
        has_value = bool(display_value) or bool(current_attachment)
        group["entries"].append(
            {
                "kind": "field",
                "field_key": field.field_key,
                "label": field.field_label,
                "unit": field.unit,
                "value_display": display_value or "-",
                "raw_value_display": display_value,
                "reference_text": reference_text,
                "help_text": field.help_text,
                "abnormal_flag": bool(result_value and result_value.abnormal_flag),
                "abnormal_reason": result_value.abnormal_reason if result_value else "",
                "attachment": current_attachment,
                "has_value": has_value,
            }
        )

    return groups


def first_group_by_section_key(groups, section_key):
    return next((group for group in groups if group["section_key"] == section_key), None)


def first_entry_by_field_key(groups, field_key):
    for group in groups:
        for entry in group["entries"]:
            if entry.get("field_key") == field_key:
                return entry
    return None


def entries_by_field_keys(groups, field_keys):
    return [entry for field_key in field_keys if (entry := first_entry_by_field_key(groups, field_key))]


def split_group_entries(group):
    if not group:
        return {"fields": [], "grouped": [], "notes": []}

    return {
        "fields": [entry for entry in group["entries"] if entry["kind"] == "field"],
        "grouped": [entry for entry in group["entries"] if entry["kind"] == "grouped"],
        "notes": [entry for entry in group["entries"] if entry["kind"] == "note"],
    }


def build_abg_variant_context(groups, render_config):
    left_group = first_group_by_section_key(groups, render_config.get("left_section_key", ""))
    right_groups = [
        first_group_by_section_key(groups, section_key)
        for section_key in render_config.get("right_section_keys", [])
    ]
    note_entries = entries_by_field_keys(groups, render_config.get("note_field_keys", []))

    return {
        "left_group": {
            "title": left_group["title"] if left_group else "",
            "entries": split_group_entries(left_group)["fields"],
        },
        "right_groups": [
            {
                "title": group["title"],
                "entries": split_group_entries(group)["fields"],
            }
            for group in right_groups
            if group
        ],
        "notes": note_entries,
    }


def build_bbank_variant_context(groups, render_config):
    general_entries = entries_by_field_keys(groups, render_config.get("general_field_keys", []))
    general_rows = []
    row_sizes = [3, 2, 2]
    index = 0
    for row_size in row_sizes:
        current_row = general_entries[index:index + row_size]
        if current_row:
            general_rows.append(current_row)
        index += row_size
    if index < len(general_entries):
        general_rows.append(general_entries[index:])

    crossmatch_group = first_group_by_section_key(groups, render_config.get("crossmatch_section_key", ""))
    crossmatch_result_entries = entries_by_field_keys(groups, render_config.get("crossmatch_result_field_keys", []))
    remarks_entry = first_entry_by_field_key(groups, render_config.get("remarks_field_key", ""))
    vital_signs_entry = first_entry_by_field_key(groups, render_config.get("vital_signs_field_key", ""))
    release_entries = entries_by_field_keys(groups, render_config.get("release_field_keys", []))

    return {
        "general_rows": general_rows,
        "crossmatch_title": crossmatch_group["title"] if crossmatch_group else "Type of Crossmatching",
        "crossmatch_result_entries": crossmatch_result_entries,
        "remarks_entry": remarks_entry,
        "vital_signs_entry": vital_signs_entry,
        "release_entries": release_entries,
    }


def build_variant_context(render_variant, groups, render_config):
    if render_variant == "abg_compact":
        return build_abg_variant_context(groups, render_config)
    if render_variant == "bbank_crossmatch":
        return build_bbank_variant_context(groups, render_config)
    return {}


def render_profile_for_item(item):
    return getattr(item.exam_definition_version, "render_profile", None)


def build_result_print_context(item):
    render_profile = render_profile_for_item(item)
    layout_type = render_profile.layout_type if render_profile else RenderLayoutTypeChoices.LABEL_VALUE_LIST
    render_config = render_profile.config_json if render_profile else {}
    groups = build_render_groups(item)
    render_variant = render_config.get("render_variant", "generic")
    variant_context = build_variant_context(render_variant, groups, render_config)
    lab_request = item.lab_request
    facility = lab_request.facility
    organization_name = lab_request.organization_name_snapshot
    if not organization_name and facility:
        organization_name = facility.organization.display_name or facility.organization.legal_name

    facility_name = lab_request.facility_name_snapshot
    if not facility_name and facility:
        facility_name = facility.display_name

    facility_address = lab_request.facility_address_snapshot
    if not facility_address and facility:
        facility_address = facility.address

    facility_contact_numbers = lab_request.facility_contact_numbers_snapshot
    if not facility_contact_numbers and facility:
        facility_contact_numbers = facility.contact_numbers

    branding_image_url = safe_media_url(lab_request.facility_header_image_snapshot)
    if not branding_image_url and facility:
        branding_image_url = safe_media_url(facility.report_header_image)

    return {
        "request_item": item,
        "layout_type": layout_type,
        "render_profile": render_profile,
        "render_config": render_config,
        "render_variant": render_variant,
        "variant_context": variant_context,
        "groups": groups,
        "header": {
            "exam_name": item.exam_definition.exam_name,
            "exam_option": item.exam_option.option_label if item.exam_option else "",
            "request_no": item.lab_request.request_no,
            "case_number": item.lab_request.case_number,
            "patient_name": item.lab_request.patient_name_snapshot,
            "age_text": item.lab_request.age_snapshot_text,
            "sex_text": item.lab_request.get_sex_snapshot_display(),
            "request_datetime_text": format_datetime(item.lab_request.request_datetime),
            "organization_name": organization_name,
            "facility_name": facility_name,
            "facility_address": facility_address,
            "facility_contact_numbers": facility_contact_numbers,
            "branding_image_url": branding_image_url,
            "physician_name": item.lab_request.physician_name_snapshot,
            "room_name": item.lab_request.room_name_snapshot,
            "version_text": f"v{item.exam_definition_version.version_no}",
            "medtech_name": item.medtech_signatory.display_name if item.medtech_signatory else "",
            "pathologist_name": item.pathologist_signatory.display_name if item.pathologist_signatory else "",
        },
        "summary": {
            "show_reference_ranges": render_config.get("show_reference_ranges", True),
            "show_units": render_config.get("show_units", True),
            "has_sections": any(group["title"] for group in groups),
        },
    }
