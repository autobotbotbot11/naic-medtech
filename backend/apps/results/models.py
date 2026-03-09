from django.db import models
from apps.common.choices import LabRequestItemStatusChoices
from apps.common.models import TimeStampedModel


class LabRequestItem(TimeStampedModel):
    lab_request = models.ForeignKey(
        "core.LabRequest",
        on_delete=models.CASCADE,
        related_name="items",
    )
    exam_definition = models.ForeignKey(
        "exams.ExamDefinition",
        on_delete=models.PROTECT,
        related_name="request_items",
    )
    exam_definition_version = models.ForeignKey(
        "exams.ExamDefinitionVersion",
        on_delete=models.PROTECT,
        related_name="request_items",
    )
    exam_option = models.ForeignKey(
        "exams.ExamOption",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="request_items",
    )
    item_status = models.CharField(
        max_length=32,
        choices=LabRequestItemStatusChoices.choices,
        default=LabRequestItemStatusChoices.DRAFT,
    )
    performed_at = models.DateTimeField(blank=True, null=True)
    released_at = models.DateTimeField(blank=True, null=True)
    printed_at = models.DateTimeField(blank=True, null=True)
    medtech_signatory = models.ForeignKey(
        "core.Signatory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medtech_request_items",
    )
    pathologist_signatory = models.ForeignKey(
        "core.Signatory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pathologist_request_items",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_request_items",
    )
    released_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="released_request_items",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["item_status"]),
            models.Index(fields=["released_at"]),
        ]

    def __str__(self):
        return f"{self.lab_request.request_no} - {self.exam_definition.exam_name}"


class LabResultValue(TimeStampedModel):
    lab_request_item = models.ForeignKey(
        "results.LabRequestItem",
        on_delete=models.CASCADE,
        related_name="result_values",
    )
    field = models.ForeignKey(
        "exams.ExamField",
        on_delete=models.PROTECT,
        related_name="result_values",
    )
    field_key_snapshot = models.CharField(max_length=128)
    field_label_snapshot = models.CharField(max_length=255)
    section_key_snapshot = models.CharField(max_length=128, blank=True)
    input_type_snapshot = models.CharField(max_length=32)
    unit_snapshot = models.CharField(max_length=64, blank=True)
    value_text = models.TextField(blank=True)
    value_number = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_datetime = models.DateTimeField(blank=True, null=True)
    value_json = models.JSONField(default=dict, blank=True)
    selected_option_value = models.CharField(max_length=255, blank=True)
    selected_option_label_snapshot = models.CharField(max_length=255, blank=True)
    reference_text_snapshot = models.CharField(max_length=255, blank=True)
    abnormal_flag = models.BooleanField(default=False)
    abnormal_reason = models.CharField(max_length=255, blank=True)
    sort_order_snapshot = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order_snapshot", "id"]
        indexes = [
            models.Index(fields=["field_key_snapshot"]),
            models.Index(fields=["abnormal_flag"]),
        ]

    def __str__(self):
        return self.field_label_snapshot


class Attachment(TimeStampedModel):
    lab_request_item = models.ForeignKey(
        "results.LabRequestItem",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    attachment_type = models.CharField(max_length=64)
    file = models.FileField(upload_to="attachments/%Y/%m/")
    original_name = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=128, blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="uploaded_attachments",
    )

    def __str__(self):
        return self.original_name or self.file.name


class AuditLog(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audit_logs",
    )
    entity_type = models.CharField(max_length=64)
    entity_id = models.PositiveIntegerField()
    action = models.CharField(max_length=64)
    before_json = models.JSONField(default=dict, blank=True)
    after_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} {self.action}"
