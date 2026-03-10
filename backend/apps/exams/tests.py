import tempfile
from pathlib import Path

from django.test import SimpleTestCase, TestCase
from openpyxl import Workbook

from apps.common.choices import ExamFieldDataTypeChoices, ExamFieldInputTypeChoices, RenderLayoutTypeChoices
from apps.exams.models import ExamDefinition
from apps.exams.services.workbook_import import (
    default_render_profile,
    infer_field_types,
    import_workbook,
    make_field_key,
    parse_reference_range,
)


class WorkbookImportHelpersTests(SimpleTestCase):
    def test_make_field_key_prefixes_section(self):
        self.assertEqual(
            make_field_key("typhidot", "IgM"),
            "typhidot_igm",
        )

    def test_parse_between_reference_range(self):
        parsed = parse_reference_range("3.5 - 5.3 mEq/L")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["range_type"], "numeric_between")
        self.assertEqual(str(parsed["min_numeric"]), "3.5")
        self.assertEqual(str(parsed["max_numeric"]), "5.3")

    def test_parse_less_than_reference_range(self):
        parsed = parse_reference_range("< 200 mg/dl")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["range_type"], "numeric_less_than")
        self.assertEqual(str(parsed["max_numeric"]), "200")

    def test_infer_grouped_measurement_field(self):
        input_type, data_type = infer_field_types(
            "BBANK - Blood Bank",
            "VITAL SIGNS",
            "Predefined Selection",
            "BLOOD PRESSURE: mmHg",
            "",
        )
        self.assertEqual(input_type, ExamFieldInputTypeChoices.GROUPED_MEASUREMENT)
        self.assertEqual(data_type, ExamFieldDataTypeChoices.JSON)

    def test_infer_display_note_field(self):
        input_type, data_type = infer_field_types(
            "ABG - Blood Gas Analysis",
            "NOTE",
            "Manual Entry",
            "",
            "",
        )
        self.assertEqual(input_type, ExamFieldInputTypeChoices.DISPLAY_NOTE)
        self.assertEqual(data_type, ExamFieldDataTypeChoices.STRING)

    def test_default_render_profile_sets_abg_variant(self):
        layout_type, config = default_render_profile(
            "ABG - Blood Gas Analysis",
            has_sections=True,
            has_reference_ranges=True,
        )

        self.assertEqual(layout_type, RenderLayoutTypeChoices.SECTIONED_REPORT)
        self.assertEqual(config["render_variant"], "abg_compact")
        self.assertEqual(config["left_section_key"], "blood_gas_value_abg")

    def test_default_render_profile_sets_bbank_variant(self):
        layout_type, config = default_render_profile(
            "BBANK - Blood Bank",
            has_sections=True,
            has_reference_ranges=True,
        )

        self.assertEqual(layout_type, RenderLayoutTypeChoices.SECTIONED_REPORT)
        self.assertEqual(config["render_variant"], "bbank_crossmatch")
        self.assertFalse(config["show_reference_ranges"])


class WorkbookImportIntegrationTests(TestCase):
    def write_workbook(self, path, sheet_title, rows, exam_options=None):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = sheet_title
        worksheet.cell(1, 1, "Field")
        worksheet.cell(1, 2, "Input Type")
        worksheet.cell(1, 3, "Selection / Unit")
        worksheet.cell(1, 4, "Normal Range")
        worksheet.cell(1, 5, "Notes")

        if exam_options:
            worksheet.cell(7, 3, "\n".join(exam_options))

        for row_index, row in enumerate(rows, start=2):
            field, input_type, raw_options, reference, notes = row
            worksheet.cell(row_index, 1, field)
            worksheet.cell(row_index, 2, input_type)
            worksheet.cell(row_index, 3, raw_options)
            worksheet.cell(row_index, 4, reference)
            worksheet.cell(row_index, 5, notes)

        workbook.save(path)

    def test_serology_hbsag_is_not_scoped_to_typhidot_section(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "serology.xlsx"
            self.write_workbook(
                workbook_path,
                "SEROLOGY",
                [
                    ("TYPHIDOT", "", "", "", ""),
                    ("IgM", "Manual Entry", "", "", ""),
                    ("HbsAg SCREENING:", "Manual Entry", "", "", ""),
                ],
            )

            import_workbook(workbook_path)

        exam = ExamDefinition.objects.get(exam_code="serology")
        version = exam.versions.get(version_no=1)
        igm_field = version.fields.get(field_key="typhidot_igm")
        hbsag_field = version.fields.get(field_key="hbsag_screening")

        self.assertEqual(igm_field.section.section_key, "typhidot")
        self.assertIsNone(hbsag_field.section)

    def test_ogtt_post_prandial_is_not_scoped_to_100g_section(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "ogtt.xlsx"
            self.write_workbook(
                workbook_path,
                "OGTT - Blood Chemistry",
                [
                    ("100G ORAL GLUCOSE TOLERANCE", "", "", "", ""),
                    ("1ST HOUR", "Manual Entry", "", "70 - 105", ""),
                    ("2 HOURS POST PRANDIAL", "Manual Entry", "", "70 - 140", ""),
                ],
            )

            import_workbook(workbook_path)

        exam = ExamDefinition.objects.get(exam_code="ogtt")
        version = exam.versions.get(version_no=1)
        first_hour_field = version.fields.get(field_key="100g_oral_glucose_tolerance_1st_hour")
        post_prandial_field = version.fields.get(field_key="2_hours_post_prandial")

        self.assertEqual(first_hour_field.section.section_key, "100g_oral_glucose_tolerance")
        self.assertIsNone(post_prandial_field.section)

    def test_force_reimport_creates_new_version_for_same_workbook(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "serology.xlsx"
            self.write_workbook(
                workbook_path,
                "SEROLOGY",
                [
                    ("HbsAg SCREENING:", "Manual Entry", "", "", ""),
                ],
            )

            first_stats = import_workbook(workbook_path)
            second_stats = import_workbook(workbook_path)
            forced_stats = import_workbook(workbook_path, force=True)

        exam = ExamDefinition.objects.get(exam_code="serology")

        self.assertEqual(first_stats.created_versions, 1)
        self.assertEqual(second_stats.skipped_versions, 1)
        self.assertEqual(forced_stats.created_versions, 1)
        self.assertEqual(exam.versions.count(), 2)
        self.assertEqual(exam.versions.order_by("-version_no").first().version_no, 2)

    def test_grouped_measurement_field_keeps_subfield_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "bbank.xlsx"
            self.write_workbook(
                workbook_path,
                "BBANK - Blood Bank",
                [
                    ("TYPE OF CROSSMATCHING", "", "", "", ""),
                    (
                        "VITAL SIGNS",
                        "Predefined Selection",
                        "BLOOD PRESSURE: mmHg\nPULSE RATE: bpm\n",
                        "Use dropdowns plus numeric entry",
                        "",
                    ),
                ],
            )

            import_workbook(workbook_path)

        exam = ExamDefinition.objects.get(exam_code="bbank")
        version = exam.versions.get(version_no=1)
        field = version.fields.get(field_key="type_of_crossmatching_vital_signs")

        self.assertEqual(field.input_type, ExamFieldInputTypeChoices.GROUPED_MEASUREMENT)
        self.assertEqual(
            field.config_json["grouped_fields"],
            [
                {
                    "key": "blood_pressure",
                    "label": "BLOOD PRESSURE",
                    "unit": "mmHg",
                    "input_type": ExamFieldInputTypeChoices.TEXT,
                    "sort_order": 1,
                },
                {
                    "key": "pulse_rate",
                    "label": "PULSE RATE",
                    "unit": "bpm",
                    "input_type": ExamFieldInputTypeChoices.TEXT,
                    "sort_order": 2,
                },
            ],
        )
