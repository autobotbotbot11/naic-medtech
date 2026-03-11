from collections import Counter, defaultdict
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


def field_entries_for_group(group):
    return split_group_entries(group)["fields"]


def entries_with_values(entries):
    return [entry for entry in entries if entry.get("has_value")]


def nonempty_groups(groups):
    populated = []
    for group in groups:
        valued_entries = entries_with_values(field_entries_for_group(group))
        grouped_entries = [entry for entry in split_group_entries(group)["grouped"] if entry.get("has_value")]
        note_entries = split_group_entries(group)["notes"]
        if valued_entries or grouped_entries or note_entries:
            populated.append(
                {
                    "title": group["title"],
                    "section_key": group["section_key"],
                    "entries": valued_entries,
                    "grouped_entries": grouped_entries,
                    "notes": note_entries,
                }
            )
    return populated


def split_group_entries(group):
    if not group:
        return {"fields": [], "grouped": [], "notes": []}

    return {
        "fields": [entry for entry in group["entries"] if entry["kind"] == "field"],
        "grouped": [entry for entry in group["entries"] if entry["kind"] == "grouped"],
        "notes": [entry for entry in group["entries"] if entry["kind"] == "note"],
    }


def clone_entry(entry, **updates):
    cloned = dict(entry)
    cloned.update(updates)
    return cloned


def filter_entries(entries, excluded_field_keys=None):
    excluded_field_keys = set(excluded_field_keys or [])
    return [entry for entry in entries if entry.get("field_key") not in excluded_field_keys]


def option_section_groups(groups, section_keys, excluded_field_keys=None, populated_only=False):
    section_groups = []
    for section_key in section_keys:
        group = first_group_by_section_key(groups, section_key)
        if not group:
            continue
        entries = filter_entries(field_entries_for_group(group), excluded_field_keys)
        if populated_only:
            entries = entries_with_values(entries)
        if entries:
            section_groups.append(
                {
                    "title": group["title"],
                    "section_key": group["section_key"],
                    "entries": entries,
                }
            )
    return section_groups


def disambiguate_duplicate_group_titles(groups):
    title_counts = Counter(group.get("title", "") for group in groups if group.get("title"))
    title_indexes = defaultdict(int)
    disambiguated = []
    for group in groups:
        title = group.get("title", "")
        if title and title_counts[title] > 1:
            title_indexes[title] += 1
            group = {**group, "title": f"{title} ({title_indexes[title]})"}
        disambiguated.append(group)
    return disambiguated


def resolve_sex_specific_entry(groups, token, sex_specific_field_map, sex_value):
    config = sex_specific_field_map.get(token)
    if not config:
        return first_entry_by_field_key(groups, token)

    preferred_key = config.get(sex_value or "")
    fallback_keys = [preferred_key] if preferred_key else []
    fallback_keys.extend(
        field_key
        for field_key in (config.get("female"), config.get("male"))
        if field_key and field_key not in fallback_keys
    )

    for field_key in fallback_keys:
        entry = first_entry_by_field_key(groups, field_key)
        if entry:
            return clone_entry(entry, label=config.get("label", entry["label"]))
    return None


def resolve_entry_tokens(groups, tokens, sex_specific_field_map, sex_value):
    entries = []
    for token in tokens:
        entry = resolve_sex_specific_entry(groups, token, sex_specific_field_map, sex_value)
        if entry:
            entries.append(entry)
    return entries


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


def build_serology_variant_context(item, groups, render_config):
    option_key = item.exam_option.option_key if item.exam_option else ""
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    option_to_section_keys = render_config.get("option_to_section_keys", {})
    option_to_field_keys = render_config.get("option_to_field_keys", {})

    primary_section_key = option_to_section_keys.get(option_key)
    primary_group = first_group_by_section_key(groups, primary_section_key) if primary_section_key else None
    primary_entries = field_entries_for_group(primary_group) if primary_group else []
    if not primary_entries:
        primary_entries = entries_by_field_keys(groups, option_to_field_keys.get(option_key, []))

    primary_entries = primary_entries or entries_with_values(
        [
            entry
            for group in groups
            for entry in field_entries_for_group(group)
        ]
    )

    primary_field_keys = {entry.get("field_key") for entry in primary_entries}
    supplemental_groups = []
    for group in nonempty_groups(groups):
        if primary_group and group["section_key"] == primary_group["section_key"]:
            continue
        filtered_entries = [entry for entry in group["entries"] if entry.get("field_key") not in primary_field_keys]
        if filtered_entries or group["grouped_entries"] or group["notes"]:
            supplemental_groups.append(
                {
                    "title": group["title"],
                    "entries": filtered_entries,
                    "grouped_entries": group["grouped_entries"],
                    "notes": group["notes"],
                }
            )

    return {
        "option_label": option_label,
        "primary_title": primary_group["title"] if primary_group else option_label,
        "primary_entries": primary_entries,
        "supplemental_groups": supplemental_groups,
        "shows_single_result": len(primary_entries) == 1,
    }


def build_ogtt_variant_context(item, groups, render_config):
    option_key = item.exam_option.option_key if item.exam_option else ""
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    option_to_section_keys = render_config.get("option_to_section_keys", {})
    option_to_field_keys = render_config.get("option_to_field_keys", {})

    primary_section_key = option_to_section_keys.get(option_key)
    primary_group = first_group_by_section_key(groups, primary_section_key) if primary_section_key else None
    primary_entries = field_entries_for_group(primary_group) if primary_group else []
    if not primary_entries:
        primary_entries = entries_by_field_keys(groups, option_to_field_keys.get(option_key, []))

    primary_entries = primary_entries or entries_with_values(
        [
            entry
            for group in groups
            for entry in field_entries_for_group(group)
        ]
    )

    primary_field_keys = {entry.get("field_key") for entry in primary_entries}
    supplemental_groups = []
    for group in nonempty_groups(groups):
        if primary_group and group["section_key"] == primary_group["section_key"]:
            continue
        filtered_entries = [entry for entry in group["entries"] if entry.get("field_key") not in primary_field_keys]
        if filtered_entries or group["grouped_entries"] or group["notes"]:
            supplemental_groups.append(
                {
                    "title": group["title"],
                    "entries": filtered_entries,
                    "grouped_entries": group["grouped_entries"],
                    "notes": group["notes"],
                }
            )

    abnormal_entries = [entry for entry in primary_entries if entry.get("abnormal_flag")]
    return {
        "option_label": option_label,
        "timeline_title": primary_group["title"] if primary_group else option_label,
        "timeline_entries": primary_entries,
        "supplemental_groups": supplemental_groups,
        "abnormal_entries": abnormal_entries,
    }


def build_hematology_variant_context(item, groups, render_config):
    option_key = item.exam_option.option_key if item.exam_option else ""
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    sex_value = (item.lab_request.sex_snapshot or "").lower()
    sex_specific_field_map = render_config.get("sex_specific_field_map", {})
    option_to_panels = render_config.get("option_to_panels", {})

    panels = []
    for panel_config in option_to_panels.get(option_key, []):
        entries = resolve_entry_tokens(groups, panel_config.get("keys", []), sex_specific_field_map, sex_value)
        if entries:
            panels.append(
                {
                    "title": panel_config["title"],
                    "entries": entries,
                }
            )

    if not panels:
        fallback_entries = entries_with_values(
            [
                entry
                for group in groups
                for entry in field_entries_for_group(group)
            ]
        )
        if fallback_entries:
            panels.append(
                {
                    "title": option_label,
                    "entries": fallback_entries,
                }
            )

    primary_field_keys = {
        entry.get("field_key")
        for panel in panels
        for entry in panel["entries"]
    }
    supplemental_entries = [
        entry
        for group in groups
        for entry in entries_with_values(field_entries_for_group(group))
        if entry.get("field_key") not in primary_field_keys
    ]

    return {
        "option_label": option_label,
        "panels": panels,
        "supplemental_entries": supplemental_entries,
        "sex_label": sex_value.title() if sex_value else "",
    }


def build_microscopy_variant_context(item, groups, render_config):
    option_key = item.exam_option.option_key if item.exam_option else ""
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    option_to_sections = render_config.get("option_to_sections", {})
    option_to_field_keys = render_config.get("option_to_field_keys", {})
    option_to_excluded_field_keys = render_config.get("option_to_excluded_field_keys", {})

    mapped_section_keys = option_to_sections.get(option_key, [])
    mapped_field_keys = option_to_field_keys.get(option_key, [])
    excluded_field_keys = option_to_excluded_field_keys.get(option_key, [])

    section_groups = option_section_groups(
        groups,
        mapped_section_keys,
        excluded_field_keys=excluded_field_keys,
    )
    focus_entries = filter_entries(
        entries_by_field_keys(groups, mapped_field_keys),
        excluded_field_keys=excluded_field_keys,
    )

    if not section_groups and not focus_entries:
        fallback_groups = []
        for group in nonempty_groups(groups):
            entries = filter_entries(group["entries"], excluded_field_keys)
            if entries:
                fallback_groups.append(
                    {
                        "title": group["title"],
                        "section_key": group["section_key"],
                        "entries": entries,
                    }
                )
        section_groups = fallback_groups

    primary_field_keys = {
        entry.get("field_key")
        for group in section_groups
        for entry in group["entries"]
    }
    primary_field_keys.update(entry.get("field_key") for entry in focus_entries)

    supplemental_groups = []
    for group in nonempty_groups(groups):
        if group["section_key"] in {mapped_group["section_key"] for mapped_group in section_groups if mapped_group["section_key"]}:
            continue
        filtered_entries = [
            entry
            for entry in filter_entries(group["entries"], excluded_field_keys)
            if entry.get("field_key") not in primary_field_keys
        ]
        if filtered_entries:
            supplemental_groups.append(
                {
                    "title": group["title"],
                    "entries": filtered_entries,
                }
            )

    section_groups = disambiguate_duplicate_group_titles(section_groups)
    supplemental_groups = disambiguate_duplicate_group_titles(supplemental_groups)

    return {
        "option_label": option_label,
        "focus_entries": focus_entries,
        "section_groups": section_groups,
        "supplemental_groups": supplemental_groups,
        "shows_single_focus": len(focus_entries) == 1,
    }


def build_chemistry_variant_context(item, groups, render_config):
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    panel_groups = render_config.get("panel_groups", [])

    panels = []
    for panel_config in panel_groups:
        entries = entries_with_values(entries_by_field_keys(groups, panel_config.get("keys", [])))
        if entries:
            panels.append(
                {
                    "title": panel_config["title"],
                    "entries": entries,
                }
            )

    if not panels:
        fallback_entries = entries_with_values(
            [
                entry
                for group in groups
                for entry in field_entries_for_group(group)
            ]
        )
        if fallback_entries:
            panels.append(
                {
                    "title": option_label,
                    "entries": fallback_entries,
                }
            )

    primary_field_keys = {
        entry.get("field_key")
        for panel in panels
        for entry in panel["entries"]
    }
    supplemental_entries = [
        entry
        for group in groups
        for entry in entries_with_values(field_entries_for_group(group))
        if entry.get("field_key") not in primary_field_keys
    ]

    return {
        "option_label": option_label,
        "panels": panels,
        "supplemental_entries": supplemental_entries,
    }


def build_coagulation_variant_context(item, groups, render_config):
    option_key = item.exam_option.option_key if item.exam_option else ""
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    option_to_sections = render_config.get("option_to_sections", {})
    mapped_section_keys = option_to_sections.get(option_key, [])
    selected_section_keys = set(mapped_section_keys)

    panels = option_section_groups(groups, mapped_section_keys)
    if not panels:
        panels = [
            {
                "title": group["title"],
                "section_key": group["section_key"],
                "entries": group["entries"],
            }
            for group in nonempty_groups(groups)
        ]

    primary_field_keys = {
        entry.get("field_key")
        for panel in panels
        for entry in panel["entries"]
    }
    supplemental_groups = []
    for group in nonempty_groups(groups):
        if group["section_key"] in {panel["section_key"] for panel in panels if panel["section_key"]}:
            continue
        if selected_section_keys and group["section_key"] and group["section_key"] not in selected_section_keys:
            continue
        filtered_entries = [entry for entry in group["entries"] if entry.get("field_key") not in primary_field_keys]
        if filtered_entries:
            supplemental_groups.append(
                {
                    "title": group["title"],
                    "entries": filtered_entries,
                }
            )

    abnormal_entries = [
        clone_entry(entry, section_title=panel["title"])
        for panel in panels
        for entry in panel["entries"]
        if entry.get("abnormal_flag")
    ]

    return {
        "option_label": option_label,
        "panels": panels,
        "supplemental_groups": supplemental_groups,
        "abnormal_entries": abnormal_entries,
        "shows_single_panel": len(panels) == 1,
    }


def build_semen_variant_context(item, groups, render_config):
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    sample_entries = entries_by_field_keys(groups, render_config.get("sample_field_keys", []))
    panels = option_section_groups(groups, render_config.get("section_keys", []))

    if not panels:
        panels = [
            {
                "title": group["title"],
                "section_key": group["section_key"],
                "entries": group["entries"],
            }
            for group in nonempty_groups(groups)
            if group["section_key"]
        ]

    primary_field_keys = {entry.get("field_key") for entry in sample_entries}
    primary_field_keys.update(
        entry.get("field_key")
        for panel in panels
        for entry in panel["entries"]
    )

    supplemental_entries = [
        entry
        for group in nonempty_groups(groups)
        for entry in group["entries"]
        if entry.get("field_key") not in primary_field_keys
    ]

    return {
        "option_label": option_label,
        "sample_entries": sample_entries,
        "panels": panels,
        "supplemental_entries": supplemental_entries,
    }


def build_single_result_focus_context(item, groups, render_config):
    option_key = item.exam_option.option_key if item.exam_option else ""
    option_label = item.exam_option.option_label if item.exam_option else item.exam_definition.exam_name
    option_to_field_keys = render_config.get("option_to_field_keys", {})
    field_keys = option_to_field_keys.get(option_key) or render_config.get("field_keys", [])
    focus_entries = entries_by_field_keys(groups, field_keys)

    if not focus_entries:
        focus_entries = entries_with_values(
            [
                entry
                for group in groups
                for entry in field_entries_for_group(group)
            ]
        )

    primary_field_keys = {entry.get("field_key") for entry in focus_entries}
    supplemental_groups = []
    for group in nonempty_groups(groups):
        filtered_entries = [entry for entry in group["entries"] if entry.get("field_key") not in primary_field_keys]
        if filtered_entries:
            supplemental_groups.append(
                {
                    "title": group["title"],
                    "entries": filtered_entries,
                }
            )

    return {
        "option_label": option_label,
        "focus_entries": focus_entries,
        "supplemental_groups": supplemental_groups,
        "shows_single_focus": len(focus_entries) == 1,
    }


def build_variant_context(item, render_variant, groups, render_config):
    if render_variant == "abg_compact":
        return build_abg_variant_context(groups, render_config)
    if render_variant == "bbank_crossmatch":
        return build_bbank_variant_context(groups, render_config)
    if render_variant == "serology_panel":
        return build_serology_variant_context(item, groups, render_config)
    if render_variant == "ogtt_timeline":
        return build_ogtt_variant_context(item, groups, render_config)
    if render_variant == "hematology_panel":
        return build_hematology_variant_context(item, groups, render_config)
    if render_variant == "microscopy_sections":
        return build_microscopy_variant_context(item, groups, render_config)
    if render_variant == "chemistry_panel":
        return build_chemistry_variant_context(item, groups, render_config)
    if render_variant == "coagulation_panel":
        return build_coagulation_variant_context(item, groups, render_config)
    if render_variant == "semen_analysis":
        return build_semen_variant_context(item, groups, render_config)
    if render_variant == "single_result_focus":
        return build_single_result_focus_context(item, groups, render_config)
    return {}


def render_profile_for_item(item):
    return getattr(item.exam_definition_version, "render_profile", None)


def build_result_print_context(item):
    render_profile = render_profile_for_item(item)
    layout_type = render_profile.layout_type if render_profile else RenderLayoutTypeChoices.LABEL_VALUE_LIST
    render_config = render_profile.config_json if render_profile else {}
    groups = build_render_groups(item)
    render_variant = render_config.get("render_variant", "generic")
    variant_context = build_variant_context(item, render_variant, groups, render_config)
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
