import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.common.choices import (
    ExamFieldDataTypeChoices,
    ExamFieldInputTypeChoices,
    ExamVersionStatusChoices,
)
from apps.core.models import LabRequest, Patient
from apps.core.models import Facility, Organization, Signatory
from apps.exams.models import (
    ExamDefinition,
    ExamDefinitionVersion,
    ExamField,
    ExamFieldReferenceRange,
    ExamSection,
    ExamRenderProfile,
    ExamFieldSelectOption,
    ExamOption,
)
from apps.results.models import Attachment, LabRequestItem, LabResultValue

User = get_user_model()


class ResultEntryFlowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.user = User.objects.create_user(
            username="resultuser",
            password="StrongPass123!",
            role="encoder",
        )
        self.client.force_login(self.user)

        self.patient = Patient.objects.create(full_name="Maria Santos", sex="female")
        self.organization = Organization.objects.create(
            legal_name="Naic Doctors Hospital Inc.",
            display_name="Naic Doctors Hospital Inc.",
            active=True,
        )
        self.facility = Facility.objects.create(
            organization=self.organization,
            display_name="Naic Main Facility",
            address="Brgy. Makina Naic, Cavite",
            contact_numbers="(046) 412-1443 / (046) 507-1510",
            active=True,
        )
        self.medtech = Signatory.objects.create(
            signatory_type="medtech",
            display_name="Imelda A. Elemia",
            license_no="MT-001",
            active=True,
        )
        self.pathologist = Signatory.objects.create(
            signatory_type="pathologist",
            display_name="Dr. Patho Sample",
            license_no="P-001",
            active=True,
        )
        self.lab_request = LabRequest.objects.create(
            request_no="REQ-20260310-0001",
            patient=self.patient,
            patient_name_snapshot="Maria Santos",
            age_snapshot_text="35 y/o",
            sex_snapshot="female",
            request_datetime=timezone.now(),
            facility=self.facility,
            organization_name_snapshot=self.organization.display_name,
            facility_name_snapshot=self.facility.display_name,
            facility_address_snapshot=self.facility.address,
            facility_contact_numbers_snapshot=self.facility.contact_numbers,
        )
        self.exam_definition = ExamDefinition.objects.create(
            exam_code="demo-exam",
            exam_name="Demo Exam",
            category="Demo",
            active=True,
        )
        self.version = ExamDefinitionVersion.objects.create(
            exam_definition=self.exam_definition,
            version_no=1,
            version_status=ExamVersionStatusChoices.PUBLISHED,
            source_type="test",
            source_reference="test-v1",
            published_at=timezone.now(),
        )
        self.option = ExamOption.objects.create(
            exam_version=self.version,
            option_key="package_a",
            option_label="Package A",
            sort_order=1,
            active=True,
        )
        self.numeric_field = ExamField.objects.create(
            exam_version=self.version,
            field_key="hemoglobin",
            field_label="Hemoglobin",
            input_type=ExamFieldInputTypeChoices.DECIMAL,
            data_type=ExamFieldDataTypeChoices.DECIMAL,
            sort_order=1,
            unit="g/dL",
            reference_text="3 - 5",
            active=True,
            config_json={},
        )
        ExamFieldReferenceRange.objects.create(
            field=self.numeric_field,
            range_type="numeric_between",
            min_numeric="3",
            max_numeric="5",
            reference_text="3 - 5",
            abnormal_rule="outside_range",
            sort_order=1,
        )
        self.select_field = ExamField.objects.create(
            exam_version=self.version,
            field_key="qualitative_status",
            field_label="Qualitative Status",
            input_type=ExamFieldInputTypeChoices.SELECT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=2,
            active=True,
            config_json={},
        )
        ExamFieldSelectOption.objects.create(
            field=self.select_field,
            option_value="positive",
            option_label="Positive",
            sort_order=1,
            active=True,
        )
        self.grouped_field = ExamField.objects.create(
            exam_version=self.version,
            field_key="vital_signs",
            field_label="Vital Signs",
            input_type=ExamFieldInputTypeChoices.GROUPED_MEASUREMENT,
            data_type=ExamFieldDataTypeChoices.JSON,
            sort_order=3,
            active=True,
            config_json={
                "grouped_fields": [
                    {"key": "blood_pressure", "label": "Blood Pressure", "unit": "mmHg", "input_type": "text", "sort_order": 1},
                    {"key": "temperature", "label": "Temperature", "unit": "C", "input_type": "text", "sort_order": 2},
                ],
            },
        )
        self.attachment_field = ExamField.objects.create(
            exam_version=self.version,
            field_key="result_image",
            field_label="Result Image",
            input_type=ExamFieldInputTypeChoices.ATTACHMENT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=4,
            supports_attachment=True,
            active=True,
            config_json={},
        )
        ExamRenderProfile.objects.create(
            exam_version=self.version,
            layout_type="result_table",
            config_json={"show_reference_ranges": True, "show_units": True},
            active=True,
        )

    def tearDown(self):
        self.settings_override.disable()

    def create_result_value(self, item, field, **kwargs):
        defaults = {
            "lab_request_item": item,
            "field": field,
            "field_key_snapshot": field.field_key,
            "field_label_snapshot": field.field_label,
            "section_key_snapshot": field.section.section_key if field.section else "",
            "input_type_snapshot": field.input_type,
            "unit_snapshot": field.unit,
            "reference_text_snapshot": field.reference_text,
            "sort_order_snapshot": field.sort_order,
        }
        defaults.update(kwargs)
        return LabResultValue.objects.create(**defaults)

    def test_add_item_view_creates_request_item_from_latest_published_version(self):
        response = self.client.post(
            reverse("request_add_item", args=[self.lab_request.pk]),
            {
                "exam_definition": self.exam_definition.pk,
                "exam_option": self.option.pk,
                "notes": "Initial item",
            },
        )

        self.assertEqual(response.status_code, 302)
        item = LabRequestItem.objects.get()
        self.assertEqual(item.exam_definition, self.exam_definition)
        self.assertEqual(item.exam_definition_version, self.version)
        self.assertEqual(item.exam_option, self.option)

    def test_result_entry_view_renders_dynamic_fields(self):
        item = LabRequestItem.objects.create(
            lab_request=self.lab_request,
            exam_definition=self.exam_definition,
            exam_definition_version=self.version,
            exam_option=self.option,
        )

        response = self.client.get(reverse("item_result_entry", args=[item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hemoglobin")
        self.assertContains(response, "Qualitative Status")
        self.assertContains(response, "Vital Signs")

    def test_result_entry_view_saves_dynamic_values_and_attachment(self):
        item = LabRequestItem.objects.create(
            lab_request=self.lab_request,
            exam_definition=self.exam_definition,
            exam_definition_version=self.version,
            exam_option=self.option,
        )

        response = self.client.post(
            reverse("item_result_entry", args=[item.pk]),
            {
                f"field_{self.numeric_field.pk}": "6.2",
                f"field_{self.select_field.pk}": "positive",
                f"field_{self.grouped_field.pk}__blood_pressure": "120/80",
                f"field_{self.grouped_field.pk}__temperature": "37.1",
                "medtech_signatory": self.medtech.pk,
                "pathologist_signatory": self.pathologist.pk,
                f"field_{self.attachment_field.pk}": SimpleUploadedFile(
                    "result.jpg",
                    b"fake-image-content",
                    content_type="image/jpeg",
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        numeric_value = LabResultValue.objects.get(field=self.numeric_field)
        select_value = LabResultValue.objects.get(field=self.select_field)
        grouped_value = LabResultValue.objects.get(field=self.grouped_field)
        attachment_value = LabResultValue.objects.get(field=self.attachment_field)
        attachment = Attachment.objects.get(field=self.attachment_field)

        self.assertEqual(item.medtech_signatory, self.medtech)
        self.assertEqual(item.pathologist_signatory, self.pathologist)
        self.assertTrue(numeric_value.abnormal_flag)
        self.assertEqual(select_value.selected_option_label_snapshot, "Positive")
        self.assertEqual(grouped_value.value_json["blood_pressure"], "120/80")
        self.assertEqual(grouped_value.value_json["temperature"], "37.1")
        self.assertEqual(attachment.original_name, "result.jpg")
        self.assertEqual(attachment_value.value_json["attachment_id"], attachment.id)

    def test_print_view_renders_saved_results(self):
        item = LabRequestItem.objects.create(
            lab_request=self.lab_request,
            exam_definition=self.exam_definition,
            exam_definition_version=self.version,
            exam_option=self.option,
            medtech_signatory=self.medtech,
            pathologist_signatory=self.pathologist,
        )
        self.create_result_value(
            item,
            self.numeric_field,
            value_number="6.2",
            reference_text_snapshot="3 - 5",
            abnormal_flag=True,
            abnormal_reason="Above normal range (3 - 5)",
        )
        self.create_result_value(
            item,
            self.select_field,
            value_text="Positive",
            selected_option_value="positive",
            selected_option_label_snapshot="Positive",
        )
        self.create_result_value(
            item,
            self.grouped_field,
            value_json={"blood_pressure": "120/80", "temperature": "37.1"},
        )
        attachment = Attachment.objects.create(
            lab_request_item=item,
            field=self.attachment_field,
            attachment_type=self.attachment_field.field_key,
            file=SimpleUploadedFile("result.jpg", b"image-bytes", content_type="image/jpeg"),
            original_name="result.jpg",
            mime_type="image/jpeg",
        )
        self.create_result_value(
            item,
            self.attachment_field,
            value_text="result.jpg",
            value_json={"attachment_id": attachment.id, "file_name": "result.jpg"},
        )

        response = self.client.get(reverse("item_result_print", args=[item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo Exam")
        self.assertContains(response, "Maria Santos")
        self.assertContains(response, "Naic Doctors Hospital Inc.")
        self.assertContains(response, "Brgy. Makina Naic, Cavite")
        self.assertContains(response, "(046) 412-1443 / (046) 507-1510")
        self.assertContains(response, "Hemoglobin")
        self.assertContains(response, "6.2")
        self.assertContains(response, "Above normal range (3 - 5)")
        self.assertContains(response, "Qualitative Status")
        self.assertContains(response, "Positive")
        self.assertContains(response, "Vital Signs")
        self.assertContains(response, "120/80")
        self.assertContains(response, "37.1")
        self.assertContains(response, "result.jpg")

    def test_abg_variant_print_view_renders_compact_layout_without_internal_note(self):
        exam_definition = ExamDefinition.objects.create(
            exam_code="abg-variant",
            exam_name="ABG Variant",
            category="Blood Gas Analysis",
            active=True,
        )
        version = ExamDefinitionVersion.objects.create(
            exam_definition=exam_definition,
            version_no=1,
            version_status=ExamVersionStatusChoices.PUBLISHED,
            source_type="test",
            source_reference="abg-variant-v1",
            published_at=timezone.now(),
        )
        left_section = ExamSection.objects.create(
            exam_version=version,
            section_key="blood_gas_value_abg",
            section_label="Blood gas value (ABG)",
            sort_order=1,
            active=True,
        )
        oximetry_section = ExamSection.objects.create(
            exam_version=version,
            section_key="calculated_values_oximetry",
            section_label="Calculated values (OXIMETRY)",
            sort_order=2,
            active=True,
        )
        acid_section = ExamSection.objects.create(
            exam_version=version,
            section_key="calculated_values_acid_base_status",
            section_label="Calculated values (ACID BASE STATUS)",
            sort_order=3,
            active=True,
        )
        ph_field = ExamField.objects.create(
            exam_version=version,
            section=left_section,
            field_key="blood_gas_value_abg_ph",
            field_label="pH",
            input_type=ExamFieldInputTypeChoices.DECIMAL,
            data_type=ExamFieldDataTypeChoices.DECIMAL,
            sort_order=1,
            reference_text="7.35-7.45",
            active=True,
            config_json={},
        )
        so2_field = ExamField.objects.create(
            exam_version=version,
            section=oximetry_section,
            field_key="calculated_values_oximetry_so2",
            field_label="sO2",
            input_type=ExamFieldInputTypeChoices.DECIMAL,
            data_type=ExamFieldDataTypeChoices.DECIMAL,
            sort_order=2,
            unit="%",
            reference_text="95-100 %",
            active=True,
            config_json={},
        )
        hco3_field = ExamField.objects.create(
            exam_version=version,
            section=acid_section,
            field_key="calculated_values_acid_base_status_hco3",
            field_label="HCO3",
            input_type=ExamFieldInputTypeChoices.DECIMAL,
            data_type=ExamFieldDataTypeChoices.DECIMAL,
            sort_order=3,
            unit="mmol/L",
            reference_text="22-28 mmol/L",
            active=True,
            config_json={},
        )
        ExamRenderProfile.objects.create(
            exam_version=version,
            layout_type="sectioned_report",
            config_json={
                "render_variant": "abg_compact",
                "show_reference_ranges": True,
                "show_units": True,
                "left_section_key": "blood_gas_value_abg",
                "right_section_keys": [
                    "calculated_values_oximetry",
                    "calculated_values_acid_base_status",
                ],
            },
            active=True,
        )
        item = LabRequestItem.objects.create(
            lab_request=self.lab_request,
            exam_definition=exam_definition,
            exam_definition_version=version,
        )
        self.create_result_value(item, ph_field, value_number="7.20", abnormal_flag=True, abnormal_reason="Below normal range (7.35-7.45)")
        self.create_result_value(item, so2_field, value_number="98")
        self.create_result_value(item, hco3_field, value_number="24")

        response = self.client.get(reverse("item_result_print", args=[item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "abg-grid")
        self.assertContains(response, "Blood gas value (ABG)")
        self.assertContains(response, "Calculated values (OXIMETRY)")
        self.assertContains(response, "Calculated values (ACID BASE STATUS)")
        self.assertContains(response, "7.2")
        self.assertContains(response, "Below normal range (7.35-7.45)")
        self.assertNotContains(response, "All out-of-range ABG values should print in red.")

    def test_bbank_variant_print_view_renders_crossmatch_layout(self):
        exam_definition = ExamDefinition.objects.create(
            exam_code="bbank-variant",
            exam_name="Blood Bank Variant",
            category="Blood Bank",
            active=True,
        )
        version = ExamDefinitionVersion.objects.create(
            exam_definition=exam_definition,
            version_no=1,
            version_status=ExamVersionStatusChoices.PUBLISHED,
            source_type="test",
            source_reference="bbank-variant-v1",
            published_at=timezone.now(),
        )
        crossmatch_section = ExamSection.objects.create(
            exam_version=version,
            section_key="type_of_crossmatching",
            section_label="TYPE OF CROSSMATCHING",
            sort_order=1,
            active=True,
        )
        general_fields = []
        for index, (field_key, label, input_type) in enumerate(
            [
                ("patients_blood_type", "PATIENT'S BLOOD TYPE", ExamFieldInputTypeChoices.TEXT),
                ("blood_component", "BLOOD COMPONENT", ExamFieldInputTypeChoices.TEXT),
                ("donors_blood_type", "DONOR'S BLOOD TYPE", ExamFieldInputTypeChoices.TEXT),
                ("source_of_blood", "SOURCE OF BLOOD", ExamFieldInputTypeChoices.TEXT),
                ("serial_number", "SERIAL NUMBER", ExamFieldInputTypeChoices.TEXT),
                ("date_extracted", "DATE EXTRACTED", ExamFieldInputTypeChoices.DATE),
                ("date_expiry", "DATE EXPIRY", ExamFieldInputTypeChoices.DATE),
            ],
            start=1,
        ):
            general_fields.append(
                ExamField.objects.create(
                    exam_version=version,
                    field_key=field_key,
                    field_label=label,
                    input_type=input_type,
                    data_type=ExamFieldDataTypeChoices.STRING if input_type == ExamFieldInputTypeChoices.TEXT else ExamFieldDataTypeChoices.DATE,
                    sort_order=index,
                    active=True,
                    config_json={},
                )
            )

        immediate_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_immediate_spin_saline_phase",
            field_label="IMMEDIATE SPIN/ SALINE PHASE",
            input_type=ExamFieldInputTypeChoices.TEXT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=20,
            active=True,
            config_json={},
        )
        albumin_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_albumin_phase_37_c",
            field_label="ALBUMIN PHASE /37 C",
            input_type=ExamFieldInputTypeChoices.TEXT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=21,
            active=True,
            config_json={},
        )
        antihuman_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_anti_human_globilin_phase",
            field_label="ANTI HUMAN GLOBILIN PHASE",
            input_type=ExamFieldInputTypeChoices.TEXT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=22,
            active=True,
            config_json={},
        )
        remarks_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_remarks",
            field_label="REMARKS",
            input_type=ExamFieldInputTypeChoices.TEXT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=23,
            active=True,
            config_json={},
        )
        vital_signs_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_vital_signs",
            field_label="VITAL SIGNS",
            input_type=ExamFieldInputTypeChoices.GROUPED_MEASUREMENT,
            data_type=ExamFieldDataTypeChoices.JSON,
            sort_order=24,
            active=True,
            config_json={
                "grouped_fields": [
                    {"key": "blood_pressure", "label": "BLOOD PRESSURE", "unit": "mmHg", "input_type": "text", "sort_order": 1},
                    {"key": "pulse_rate", "label": "PULSE RATE", "unit": "bpm", "input_type": "text", "sort_order": 2},
                ],
            },
            reference_text="Vitals are encoded manually.",
            help_text="Enter monitoring values during crossmatch.",
        )
        released_by_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_released_by",
            field_label="RELEASED BY",
            input_type=ExamFieldInputTypeChoices.TEXT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=25,
            active=True,
            config_json={},
        )
        released_to_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_released_to",
            field_label="RELEASED TO",
            input_type=ExamFieldInputTypeChoices.TEXT,
            data_type=ExamFieldDataTypeChoices.STRING,
            sort_order=26,
            active=True,
            config_json={},
        )
        datetime_field = ExamField.objects.create(
            exam_version=version,
            section=crossmatch_section,
            field_key="type_of_crossmatching_datetime",
            field_label="DATE/TIME",
            input_type=ExamFieldInputTypeChoices.DATETIME,
            data_type=ExamFieldDataTypeChoices.DATETIME,
            sort_order=27,
            active=True,
            config_json={},
        )
        ExamRenderProfile.objects.create(
            exam_version=version,
            layout_type="sectioned_report",
            config_json={
                "render_variant": "bbank_crossmatch",
                "show_reference_ranges": False,
                "show_units": True,
                "general_field_keys": [
                    "patients_blood_type",
                    "blood_component",
                    "donors_blood_type",
                    "source_of_blood",
                    "serial_number",
                    "date_extracted",
                    "date_expiry",
                ],
                "crossmatch_section_key": "type_of_crossmatching",
                "crossmatch_result_field_keys": [
                    "type_of_crossmatching_immediate_spin_saline_phase",
                    "type_of_crossmatching_albumin_phase_37_c",
                    "type_of_crossmatching_anti_human_globilin_phase",
                ],
                "remarks_field_key": "type_of_crossmatching_remarks",
                "vital_signs_field_key": "type_of_crossmatching_vital_signs",
                "release_field_keys": [
                    "type_of_crossmatching_released_by",
                    "type_of_crossmatching_released_to",
                    "type_of_crossmatching_datetime",
                ],
            },
            active=True,
        )
        item = LabRequestItem.objects.create(
            lab_request=self.lab_request,
            exam_definition=exam_definition,
            exam_definition_version=version,
        )
        self.create_result_value(item, general_fields[0], value_text="O Positive")
        self.create_result_value(item, general_fields[1], value_text="PRBC")
        self.create_result_value(item, general_fields[2], value_text="A Positive")
        self.create_result_value(item, general_fields[3], value_text="PRC Dasmarinas")
        self.create_result_value(item, general_fields[4], value_text="SN-001")
        self.create_result_value(item, general_fields[5], value_date=timezone.localdate())
        self.create_result_value(item, general_fields[6], value_date=timezone.localdate())
        self.create_result_value(item, immediate_field, value_text="Negative")
        self.create_result_value(item, albumin_field, value_text="Negative")
        self.create_result_value(item, antihuman_field, value_text="Negative")
        self.create_result_value(item, remarks_field, value_text="COMPATIBLE")
        self.create_result_value(item, vital_signs_field, value_json={"blood_pressure": "120/80", "pulse_rate": "88"})
        self.create_result_value(item, released_by_field, value_text="Imelda A. Elemia")
        self.create_result_value(item, released_to_field, value_text="Ward Nurse")
        self.create_result_value(item, datetime_field, value_datetime=timezone.now())

        response = self.client.get(reverse("item_result_print", args=[item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bbank-crossmatch")
        self.assertContains(response, "PATIENT&#x27;S BLOOD TYPE")
        self.assertContains(response, "TYPE OF CROSSMATCHING")
        self.assertContains(response, "COMPATIBLE")
        self.assertContains(response, "120/80")
        self.assertContains(response, "Imelda A. Elemia")
