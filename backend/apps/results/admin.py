from django.contrib import admin
from .models import Attachment, AuditLog, LabRequestItem, LabResultValue


@admin.register(LabRequestItem)
class LabRequestItemAdmin(admin.ModelAdmin):
    list_display = ("lab_request", "exam_definition", "exam_option", "item_status", "released_at")
    list_filter = ("item_status",)
    search_fields = ("lab_request__request_no", "exam_definition__exam_name", "lab_request__patient_name_snapshot")
    autocomplete_fields = (
        "lab_request",
        "exam_definition",
        "exam_definition_version",
        "exam_option",
        "medtech_signatory",
        "pathologist_signatory",
        "created_by",
        "released_by",
    )


@admin.register(LabResultValue)
class LabResultValueAdmin(admin.ModelAdmin):
    list_display = ("lab_request_item", "field_label_snapshot", "abnormal_flag")
    list_filter = ("abnormal_flag",)
    search_fields = ("field_label_snapshot", "field_key_snapshot", "lab_request_item__lab_request__request_no")
    autocomplete_fields = ("lab_request_item", "field")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("lab_request_item", "attachment_type", "original_name", "uploaded_by")
    search_fields = ("attachment_type", "original_name")
    autocomplete_fields = ("lab_request_item", "uploaded_by")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "entity_id", "action", "user", "created_at")
    list_filter = ("entity_type", "action")
    search_fields = ("entity_type", "entity_id", "action")
    autocomplete_fields = ("user",)
