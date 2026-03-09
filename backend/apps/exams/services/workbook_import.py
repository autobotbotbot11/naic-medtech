import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from openpyxl import load_workbook

from apps.common.choices import (
    ExamFieldDataTypeChoices,
    ExamFieldInputTypeChoices,
    ExamRuleTypeChoices,
    ExamVersionStatusChoices,
    RenderLayoutTypeChoices,
)
from apps.exams.models import (
    ExamDefinition,
    ExamDefinitionVersion,
    ExamField,
    ExamFieldReferenceRange,
    ExamFieldSelectOption,
    ExamOption,
    ExamRenderProfile,
    ExamRule,
    ExamSection,
)


PATIENT_FIELDS = {
    "Name",
    "Age",
    "Sex",
    "Date",
    "Date/Time",
    "Examination",
    "Requesting Physician",
    "Room",
    "Case Number",
}

SIGNATORY_FIELDS = {"Medical Technologist", "Pathologist"}
SKIP_SECTION_LABELS = {"PATIENT INFORMATION"}

TEXT_MANUAL_FIELDS = {
    "LOT NUMBER",
    "PATIENT’S BLOOD TYPE",
    "PATIENT'S BLOOD TYPE",
    "BLOOD COMPONENT",
    "DONOR’S BLOOD TYPE",
    "DONOR'S BLOOD TYPE",
    "SOURCE OF BLOOD",
    "SERIAL NUMBER",
    "REMARKS",
    "RELEASED BY",
    "RELEASED TO",
    "OTHERS",
    "OTHERS  ",
}

DATE_FIELDS = {
    "DATE EXTRACTED",
    "DATE EXPIRY",
}

SHEET_META_MAP = {
    "URINE- Clinical Microscopy": {"exam_code": "urine", "exam_name": "Urine", "category": "Clinical Microscopy"},
    "SEROLOGY": {"exam_code": "serology", "exam_name": "Serology", "category": "Serology"},
    "SEMEN - Clinical Microscopy": {"exam_code": "semen", "exam_name": "Semen Analysis", "category": "Clinical Microscopy"},
    "OGTT - Blood Chemistry": {"exam_code": "ogtt", "exam_name": "Oral Glucose Tolerance Test", "category": "Blood Chemistry"},
    "MICROBIOLOGY": {"exam_code": "microbiology", "exam_name": "Microbiology", "category": "Microbiology"},
    "HEMATOLOGY": {"exam_code": "hematology", "exam_name": "Hematology", "category": "Hematology"},
    "HBA1C - Blood Chemistry": {"exam_code": "hba1c", "exam_name": "HBA1C", "category": "Blood Chemistry"},
    "FECALYSIS - Clinical Microscopy": {"exam_code": "fecalysis", "exam_name": "Fecalysis", "category": "Clinical Microscopy"},
    "CARDIACI - Serology": {"exam_code": "cardiaci", "exam_name": "Cardiac Markers", "category": "Serology"},
    "BCMALE - Blood Chemistry": {"exam_code": "bcmale", "exam_name": "Blood Chemistry Male", "category": "Blood Chemistry"},
    "BCFEMALE - Blood Chemistry": {"exam_code": "bcfemale", "exam_name": "Blood Chemistry Female", "category": "Blood Chemistry"},
    "BBANK - Blood Bank": {"exam_code": "bbank", "exam_name": "Blood Bank", "category": "Blood Bank"},
    "ABG - Blood Gas Analysis": {"exam_code": "abg", "exam_name": "Blood Gas Analysis", "category": "Blood Gas Analysis"},
    "HIV 1&2 TESTING - Serology": {"exam_code": "hiv-1-2-testing", "exam_name": "HIV 1 and 2 Testing", "category": "Serology"},
    "COVID 19 ANTIGEN (RAPID TEST) -": {"exam_code": "covid-19-antigen-rapid-test", "exam_name": "COVID 19 Antigen Rapid Test", "category": "Serology"},
    "PROTIME, APTT - Hematology": {"exam_code": "protime-aptt", "exam_name": "Protime and APTT", "category": "Hematology"},
}

UNSCOPED_FIELDS_BY_SHEET = {
    "SEROLOGY": {
        "HbsAg SCREENING:",
        "VDRL:",
        "ANTI-HCV:",
        "ASO TITER:",
        "OTHERS",
    },
    "OGTT - Blood Chemistry": {
        "2 HOURS POST PRANDIAL",
        "50 G ORAL GLUCOSE CHALLENGE",
        "Others",
    },
}

IMPORTER_SIGNATURE_VERSION = 4


@dataclass
class ImportStats:
    created_definitions: int = 0
    created_versions: int = 0
    skipped_versions: int = 0
    created_options: int = 0
    created_sections: int = 0
    created_fields: int = 0
    created_ranges: int = 0
    created_rules: int = 0


def normalize_text(value):
    if value is None:
        return ""
    return " ".join(str(value).replace("\n", " ").split()).strip()


def split_multiline(value):
    if not isinstance(value, str):
        return []
    parts = [normalize_text(part) for part in value.splitlines()]
    cleaned = [part for part in parts if part and set(part) != {"-"}]
    return cleaned


def make_meta(sheet_name):
    if sheet_name in SHEET_META_MAP:
        return SHEET_META_MAP[sheet_name]

    cleaned = sheet_name.strip().rstrip("-").strip()
    return {
        "exam_code": slugify(cleaned),
        "exam_name": cleaned,
        "category": "",
    }


def make_key(text):
    key = slugify(normalize_text(text)).replace("-", "_")
    return key or "field"


def make_field_key(section_key, field_label):
    base_key = make_key(field_label)
    if section_key:
        return f"{section_key}_{base_key}"
    return base_key


def decimal_or_none(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def parse_reference_range(text):
    raw = normalize_text(text)
    if not raw:
        return None

    between_match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*(?:-|to)\s*([+-]?\d+(?:\.\d+)?)", raw, flags=re.IGNORECASE)
    if between_match:
        low = decimal_or_none(between_match.group(1))
        high = decimal_or_none(between_match.group(2))
        if low is not None and high is not None:
            return {
                "range_type": "numeric_between",
                "min_numeric": low,
                "max_numeric": high,
                "reference_text": raw,
                "abnormal_rule": "outside_range",
            }

    lt_match = re.search(r"(?:<|less than)\s*([+-]?\d+(?:\.\d+)?)", raw, flags=re.IGNORECASE)
    if lt_match:
        high = decimal_or_none(lt_match.group(1))
        if high is not None:
            return {
                "range_type": "numeric_less_than",
                "min_numeric": None,
                "max_numeric": high,
                "reference_text": raw,
                "abnormal_rule": "greater_than_max",
            }

    gt_match = re.search(r"(?:>|greater than)\s*([+-]?\d+(?:\.\d+)?)", raw, flags=re.IGNORECASE)
    if gt_match:
        low = decimal_or_none(gt_match.group(1))
        if low is not None:
            return {
                "range_type": "numeric_greater_than",
                "min_numeric": low,
                "max_numeric": None,
                "reference_text": raw,
                "abnormal_rule": "less_than_min",
            }

    return {
        "range_type": "text_reference",
        "min_numeric": None,
        "max_numeric": None,
        "reference_text": raw,
        "abnormal_rule": "",
    }


def infer_field_types(sheet_name, field_label, input_type, raw_options, reference_text):
    normalized_label = normalize_text(field_label).upper()
    normalized_input = normalize_text(input_type).lower()
    normalized_reference = normalize_text(reference_text)
    normalized_options = normalize_text(raw_options)

    if sheet_name == "BBANK - Blood Bank" and normalized_label == "VITAL SIGNS":
        return ExamFieldInputTypeChoices.GROUPED_MEASUREMENT, ExamFieldDataTypeChoices.JSON

    if normalized_label == "NOTE":
        return ExamFieldInputTypeChoices.DISPLAY_NOTE, ExamFieldDataTypeChoices.STRING

    if normalized_input == "predefined selection":
        return ExamFieldInputTypeChoices.SELECT, ExamFieldDataTypeChoices.STRING

    if normalized_label in DATE_FIELDS:
        return ExamFieldInputTypeChoices.DATE, ExamFieldDataTypeChoices.DATE

    if "DATE/TIME" in normalized_label or normalized_label == "DATE TIME":
        return ExamFieldInputTypeChoices.DATETIME, ExamFieldDataTypeChoices.DATETIME

    if "DATE" in normalized_label and "TIME" not in normalized_label:
        return ExamFieldInputTypeChoices.DATE, ExamFieldDataTypeChoices.DATE

    if normalized_label in TEXT_MANUAL_FIELDS:
        return ExamFieldInputTypeChoices.TEXT, ExamFieldDataTypeChoices.STRING

    if normalized_label in {"OTHERS", "OTHERS  "}:
        return ExamFieldInputTypeChoices.TEXTAREA, ExamFieldDataTypeChoices.STRING

    if normalized_reference and re.search(r"\d", normalized_reference):
        return ExamFieldInputTypeChoices.DECIMAL, ExamFieldDataTypeChoices.DECIMAL

    if normalized_options and "\n" not in str(raw_options) and normalized_options not in {"------------------------------------", "-----------------------------"}:
        if re.search(r"[A-Za-z/%]", normalized_options):
            return ExamFieldInputTypeChoices.DECIMAL, ExamFieldDataTypeChoices.DECIMAL

    return ExamFieldInputTypeChoices.TEXT, ExamFieldDataTypeChoices.STRING


def extract_unit(input_type, raw_options):
    normalized_input = normalize_text(input_type).lower()
    if normalized_input != "manual entry":
        return ""

    value = normalize_text(raw_options)
    if not value or set(value) == {"-"}:
        return ""
    if "\n" in str(raw_options):
        return ""
    return value


def parse_grouped_measurement_config(raw_options):
    grouped_fields = []
    for position, line in enumerate(split_multiline(raw_options), start=1):
        label = line
        unit = ""
        if ":" in line:
            label_part, unit_part = line.split(":", 1)
            label = normalize_text(label_part)
            unit = normalize_text(unit_part)

        grouped_fields.append(
            {
                "key": make_key(label),
                "label": label,
                "unit": unit,
                "input_type": ExamFieldInputTypeChoices.TEXT,
                "sort_order": position,
            }
        )

    return grouped_fields


def build_field_config(field_input_type, raw_options):
    raw_option_lines = split_multiline(raw_options)
    config = {}
    if raw_option_lines:
        config["raw_options_lines"] = raw_option_lines

    if field_input_type == ExamFieldInputTypeChoices.GROUPED_MEASUREMENT:
        config["grouped_fields"] = parse_grouped_measurement_config(raw_options)

    return config


def sheet_payload(ws):
    rows = []
    for row_idx in range(1, ws.max_row + 1):
        row = {
            "row": row_idx,
            "field": normalize_text(ws.cell(row_idx, 1).value),
            "input_type": normalize_text(ws.cell(row_idx, 2).value),
            "raw_options": ws.cell(row_idx, 3).value or "",
            "reference": normalize_text(ws.cell(row_idx, 4).value),
            "notes": normalize_text(ws.cell(row_idx, 5).value),
        }
        if any(row.values()):
            rows.append(row)
    return rows


def payload_hash(payload):
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_source_reference(sheet_name, payload, importer_signature_version=IMPORTER_SIGNATURE_VERSION):
    signature = {
        "sheet_name": sheet_name,
        "importer_signature_version": importer_signature_version,
        "payload": payload,
    }
    return f"v{importer_signature_version}:{payload_hash(signature)}"


def create_rule(version, rule_type, target_type, target_id, condition, effect, sort_order):
    return ExamRule.objects.create(
        exam_version=version,
        rule_type=rule_type,
        target_type=target_type,
        target_id=target_id,
        condition_json=condition,
        effect_json=effect,
        sort_order=sort_order,
        active=True,
    )


def build_safe_rules(sheet_name, version, options_by_key, sections_by_key, fields_by_key):
    created = 0
    sort_order = 0

    for field in fields_by_key.values():
        label = normalize_text(field.field_label).upper()
        if label.endswith("(M)"):
            sort_order += 1
            create_rule(
                version,
                ExamRuleTypeChoices.VISIBILITY,
                "field",
                field.id,
                {"patient_sex": ["male"]},
                {"visible": True},
                sort_order,
            )
            created += 1
        elif label.endswith("(F)"):
            sort_order += 1
            create_rule(
                version,
                ExamRuleTypeChoices.VISIBILITY,
                "field",
                field.id,
                {"patient_sex": ["female"]},
                {"visible": True},
                sort_order,
            )
            created += 1

    if sheet_name == "URINE- Clinical Microscopy":
        pregnancy_field = fields_by_key.get("microscopic_finding_pregnancy_test") or fields_by_key.get("pregnancy_test")
        if pregnancy_field:
            pregnancy_options = [key for key, option in options_by_key.items() if "pregnancy" in option.option_label.lower()]
            if pregnancy_options:
                sort_order += 1
                create_rule(
                    version,
                    ExamRuleTypeChoices.VISIBILITY,
                    "field",
                    pregnancy_field.id,
                    {"exam_option_keys": pregnancy_options},
                    {"visible": True},
                    sort_order,
                )
                created += 1

    if sheet_name == "OGTT - Blood Chemistry":
        option_map = {
            "50G ORAL GLUCOSE TOLERANCE": "50g ogtt",
            "75G ORAL GLUCOSE TOLERANCE": "75g ogtt",
            "100G ORAL GLUCOSE TOLERANCE": "100g ogtt",
        }
        for section_key, section in sections_by_key.items():
            label = normalize_text(section.section_label).upper()
            matched_option_keys = [
                key for key, option in options_by_key.items()
                if option_map.get(label, "").lower() == option.option_label.lower()
            ]
            if matched_option_keys:
                sort_order += 1
                create_rule(
                    version,
                    ExamRuleTypeChoices.VISIBILITY,
                    "section",
                    section.id,
                    {"exam_option_keys": matched_option_keys},
                    {"visible": True},
                    sort_order,
                )
                created += 1

    if sheet_name == "PROTIME, APTT - Hematology":
        mappings = {
            "pro_time": ["protime", "protime_aptt"],
            "aptt": ["aptt", "protime_aptt"],
        }
        for section_key, allowed in mappings.items():
            section = sections_by_key.get(section_key)
            if not section:
                continue
            matched_option_keys = [key for key in options_by_key if key in allowed]
            if matched_option_keys:
                sort_order += 1
                create_rule(
                    version,
                    ExamRuleTypeChoices.VISIBILITY,
                    "section",
                    section.id,
                    {"exam_option_keys": matched_option_keys},
                    {"visible": True},
                    sort_order,
                )
                created += 1

    if sheet_name == "COVID 19 ANTIGEN (RAPID TEST) -":
        attachment_field = fields_by_key.get("result_image")
        if attachment_field:
            sort_order += 1
            create_rule(
                version,
                ExamRuleTypeChoices.REQUIREMENT,
                "field",
                attachment_field.id,
                {"item_status": ["released"]},
                {"required": True},
                sort_order,
            )
            created += 1

    return created


def default_render_layout(has_sections, has_reference_ranges):
    if has_sections:
        return RenderLayoutTypeChoices.SECTIONED_REPORT
    if has_reference_ranges:
        return RenderLayoutTypeChoices.RESULT_TABLE
    return RenderLayoutTypeChoices.LABEL_VALUE_LIST


@transaction.atomic
def import_workbook(
    workbook_path,
    publish=True,
    archive_old=True,
    force=False,
    importer_signature_version=IMPORTER_SIGNATURE_VERSION,
):
    workbook_path = Path(workbook_path)
    wb = load_workbook(workbook_path, data_only=True)
    stats = ImportStats()

    for ws in wb.worksheets:
        meta = make_meta(ws.title)
        payload = sheet_payload(ws)
        source_reference = build_source_reference(
            sheet_name=ws.title,
            payload=payload,
            importer_signature_version=importer_signature_version,
        )
        unscoped_fields = {normalize_text(value) for value in UNSCOPED_FIELDS_BY_SHEET.get(ws.title, set())}

        exam_definition, created_definition = ExamDefinition.objects.get_or_create(
            exam_code=meta["exam_code"],
            defaults={
                "exam_name": meta["exam_name"],
                "category": meta["category"],
                "description": ws.title,
                "active": True,
            },
        )
        if created_definition:
            stats.created_definitions += 1
        else:
            exam_definition.exam_name = meta["exam_name"]
            exam_definition.category = meta["category"]
            exam_definition.description = ws.title
            exam_definition.active = True
            exam_definition.save(update_fields=["exam_name", "category", "description", "active", "updated_at"])

        latest_published = exam_definition.versions.filter(version_status=ExamVersionStatusChoices.PUBLISHED).order_by("-version_no").first()
        if not force and latest_published and latest_published.source_reference == source_reference:
            stats.skipped_versions += 1
            continue

        if archive_old:
            exam_definition.versions.filter(version_status=ExamVersionStatusChoices.PUBLISHED).update(
                version_status=ExamVersionStatusChoices.ARCHIVED
            )

        next_version_no = (exam_definition.versions.order_by("-version_no").values_list("version_no", flat=True).first() or 0) + 1
        version = ExamDefinitionVersion.objects.create(
            exam_definition=exam_definition,
            version_no=next_version_no,
            version_status=ExamVersionStatusChoices.PUBLISHED if publish else ExamVersionStatusChoices.DRAFT,
            source_type="xlsx_import",
            source_reference=source_reference,
            published_at=timezone.now() if publish else None,
            change_summary=f"Imported from workbook sheet: {ws.title}",
        )
        stats.created_versions += 1

        options_by_key = {}
        sections_by_key = {}
        fields_by_key = {}
        section_occurrences = {}
        current_section = None
        section_sort_order = 0
        field_sort_order = 0

        exam_option_lines = split_multiline(ws.cell(7, 3).value)
        for position, option_label in enumerate(exam_option_lines, start=1):
            option = ExamOption.objects.create(
                exam_version=version,
                option_key=make_key(option_label),
                option_label=option_label,
                sort_order=position,
                active=True,
            )
            options_by_key[option.option_key] = option
            stats.created_options += 1

        for row in payload:
            field_label = row["field"]
            input_type = row["input_type"]
            raw_options = row["raw_options"]
            reference = row["reference"]
            notes = row["notes"]

            if not field_label or field_label == "Field":
                continue

            if field_label in PATIENT_FIELDS or field_label in SIGNATORY_FIELDS:
                continue

            if not input_type:
                if field_label in SKIP_SECTION_LABELS:
                    current_section = None
                    continue

                base_section_key = make_key(field_label)
                occurrence = section_occurrences.get(base_section_key, 0) + 1
                section_occurrences[base_section_key] = occurrence
                section_key = base_section_key if occurrence == 1 else f"{base_section_key}_{occurrence}"
                section_sort_order += 1
                current_section = ExamSection.objects.create(
                    exam_version=version,
                    section_key=section_key,
                    section_label=field_label,
                    sort_order=section_sort_order,
                    active=True,
                )
                sections_by_key[section_key] = current_section
                stats.created_sections += 1
                continue

            effective_section = current_section
            normalized_field_label = normalize_text(field_label)
            if normalized_field_label in unscoped_fields:
                effective_section = None

            field_input_type, data_type = infer_field_types(ws.title, field_label, input_type, raw_options, reference)
            field_key = make_field_key(effective_section.section_key if effective_section else "", field_label)
            unit = extract_unit(input_type, raw_options)
            field_config = build_field_config(field_input_type, raw_options)
            field_sort_order += 1

            exam_field = ExamField.objects.create(
                exam_version=version,
                section=effective_section,
                field_key=field_key,
                field_label=field_label,
                input_type=field_input_type,
                data_type=data_type,
                unit=unit,
                required=False,
                sort_order=field_sort_order,
                default_value="",
                help_text=notes,
                placeholder_text="",
                reference_text=reference,
                config_json=field_config,
                supports_attachment=field_input_type == ExamFieldInputTypeChoices.ATTACHMENT,
                active=True,
            )
            fields_by_key[field_key] = exam_field
            stats.created_fields += 1

            if field_input_type == ExamFieldInputTypeChoices.SELECT:
                for position, option_label in enumerate(split_multiline(raw_options), start=1):
                    ExamFieldSelectOption.objects.create(
                        field=exam_field,
                        option_value=make_key(option_label),
                        option_label=option_label,
                        sort_order=position,
                        active=True,
                    )

            parsed_range = parse_reference_range(reference)
            if parsed_range:
                ExamFieldReferenceRange.objects.create(
                    field=exam_field,
                    option_scope=None,
                    sex_scope="",
                    range_type=parsed_range["range_type"],
                    min_numeric=parsed_range["min_numeric"],
                    max_numeric=parsed_range["max_numeric"],
                    reference_text=parsed_range["reference_text"],
                    abnormal_rule=parsed_range["abnormal_rule"],
                    sort_order=1,
                )
                stats.created_ranges += 1

        if ws.title == "COVID 19 ANTIGEN (RAPID TEST) -":
            field_sort_order += 1
            attachment_field = ExamField.objects.create(
                exam_version=version,
                section=None,
                field_key="result_image",
                field_label="Result Image",
                input_type=ExamFieldInputTypeChoices.ATTACHMENT,
                data_type=ExamFieldDataTypeChoices.STRING,
                unit="",
                required=False,
                sort_order=field_sort_order,
                default_value="",
                help_text="Imported from workbook note: kelangan may picture sa result",
                placeholder_text="",
                reference_text="",
                config_json={},
                supports_attachment=True,
                active=True,
            )
            fields_by_key[attachment_field.field_key] = attachment_field
            stats.created_fields += 1

        stats.created_rules += build_safe_rules(ws.title, version, options_by_key, sections_by_key, fields_by_key)

        has_sections = bool(sections_by_key)
        has_reference_ranges = ExamFieldReferenceRange.objects.filter(field__exam_version=version).exists()
        ExamRenderProfile.objects.create(
            exam_version=version,
            layout_type=default_render_layout(has_sections, has_reference_ranges),
            config_json={
                "sheet_name": ws.title,
                "show_reference_ranges": has_reference_ranges,
                "show_units": True,
            },
            active=True,
        )

    return stats
