import shutil
import tempfile

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
from apps.exams.models import (
    ExamDefinition,
    ExamDefinitionVersion,
    ExamField,
    ExamFieldReferenceRange,
    ExamRenderProfile,
    ExamFieldSelectOption,
    ExamOption,
)
from apps.results.models import Attachment, LabRequestItem, LabResultValue


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

        self.patient = Patient.objects.create(full_name="Maria Santos", sex="female")
        self.lab_request = LabRequest.objects.create(
            request_no="REQ-20260310-0001",
            patient=self.patient,
            patient_name_snapshot="Maria Santos",
            age_snapshot_text="35 y/o",
            sex_snapshot="female",
            request_datetime=timezone.now(),
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
                f"field_{self.attachment_field.pk}": SimpleUploadedFile(
                    "result.jpg",
                    b"fake-image-content",
                    content_type="image/jpeg",
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        numeric_value = LabResultValue.objects.get(field=self.numeric_field)
        select_value = LabResultValue.objects.get(field=self.select_field)
        grouped_value = LabResultValue.objects.get(field=self.grouped_field)
        attachment_value = LabResultValue.objects.get(field=self.attachment_field)
        attachment = Attachment.objects.get(field=self.attachment_field)

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
        )
        numeric_value = LabResultValue.objects.create(
            lab_request_item=item,
            field=self.numeric_field,
            field_key_snapshot=self.numeric_field.field_key,
            field_label_snapshot=self.numeric_field.field_label,
            section_key_snapshot="",
            input_type_snapshot=self.numeric_field.input_type,
            unit_snapshot=self.numeric_field.unit,
            value_number="6.2",
            reference_text_snapshot="3 - 5",
            abnormal_flag=True,
            abnormal_reason="Above normal range (3 - 5)",
            sort_order_snapshot=self.numeric_field.sort_order,
        )
        select_value = LabResultValue.objects.create(
            lab_request_item=item,
            field=self.select_field,
            field_key_snapshot=self.select_field.field_key,
            field_label_snapshot=self.select_field.field_label,
            section_key_snapshot="",
            input_type_snapshot=self.select_field.input_type,
            unit_snapshot="",
            value_text="Positive",
            selected_option_value="positive",
            selected_option_label_snapshot="Positive",
            sort_order_snapshot=self.select_field.sort_order,
        )
        grouped_value = LabResultValue.objects.create(
            lab_request_item=item,
            field=self.grouped_field,
            field_key_snapshot=self.grouped_field.field_key,
            field_label_snapshot=self.grouped_field.field_label,
            section_key_snapshot="",
            input_type_snapshot=self.grouped_field.input_type,
            unit_snapshot="",
            value_json={"blood_pressure": "120/80", "temperature": "37.1"},
            sort_order_snapshot=self.grouped_field.sort_order,
        )
        attachment = Attachment.objects.create(
            lab_request_item=item,
            field=self.attachment_field,
            attachment_type=self.attachment_field.field_key,
            file=SimpleUploadedFile("result.jpg", b"image-bytes", content_type="image/jpeg"),
            original_name="result.jpg",
            mime_type="image/jpeg",
        )
        attachment_value = LabResultValue.objects.create(
            lab_request_item=item,
            field=self.attachment_field,
            field_key_snapshot=self.attachment_field.field_key,
            field_label_snapshot=self.attachment_field.field_label,
            section_key_snapshot="",
            input_type_snapshot=self.attachment_field.input_type,
            unit_snapshot="",
            value_text="result.jpg",
            value_json={"attachment_id": attachment.id, "file_name": "result.jpg"},
            sort_order_snapshot=self.attachment_field.sort_order,
        )

        response = self.client.get(reverse("item_result_print", args=[item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo Exam")
        self.assertContains(response, "Maria Santos")
        self.assertContains(response, "Hemoglobin")
        self.assertContains(response, "6.2")
        self.assertContains(response, "Above normal range (3 - 5)")
        self.assertContains(response, "Qualitative Status")
        self.assertContains(response, "Positive")
        self.assertContains(response, "Vital Signs")
        self.assertContains(response, "120/80")
        self.assertContains(response, "37.1")
        self.assertContains(response, "result.jpg")
