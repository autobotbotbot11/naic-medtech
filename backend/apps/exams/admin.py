from django.contrib import admin
from .models import (
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


@admin.register(ExamDefinition)
class ExamDefinitionAdmin(admin.ModelAdmin):
    list_display = ("exam_code", "exam_name", "category", "active")
    list_filter = ("active", "category")
    search_fields = ("exam_code", "exam_name", "category")


@admin.register(ExamDefinitionVersion)
class ExamDefinitionVersionAdmin(admin.ModelAdmin):
    list_display = ("exam_definition", "version_no", "version_status", "published_at")
    list_filter = ("version_status",)
    search_fields = ("exam_definition__exam_code", "exam_definition__exam_name")
    autocomplete_fields = ("exam_definition", "published_by")


@admin.register(ExamOption)
class ExamOptionAdmin(admin.ModelAdmin):
    list_display = ("option_label", "option_key", "exam_version", "sort_order", "active")
    list_filter = ("active",)
    search_fields = ("option_label", "option_key")
    autocomplete_fields = ("exam_version",)


@admin.register(ExamSection)
class ExamSectionAdmin(admin.ModelAdmin):
    list_display = ("section_label", "section_key", "exam_version", "sort_order", "active")
    list_filter = ("active",)
    search_fields = ("section_label", "section_key")
    autocomplete_fields = ("exam_version",)


@admin.register(ExamField)
class ExamFieldAdmin(admin.ModelAdmin):
    list_display = ("field_label", "field_key", "exam_version", "input_type", "required", "active")
    list_filter = ("input_type", "data_type", "required", "active")
    search_fields = ("field_label", "field_key")
    autocomplete_fields = ("exam_version", "section")


@admin.register(ExamFieldSelectOption)
class ExamFieldSelectOptionAdmin(admin.ModelAdmin):
    list_display = ("option_label", "option_value", "field", "sort_order", "active")
    list_filter = ("active",)
    search_fields = ("option_label", "option_value", "field__field_label", "field__field_key")
    autocomplete_fields = ("field",)


@admin.register(ExamFieldReferenceRange)
class ExamFieldReferenceRangeAdmin(admin.ModelAdmin):
    list_display = ("field", "range_type", "sex_scope", "option_scope", "reference_text")
    list_filter = ("range_type", "sex_scope")
    search_fields = ("field__field_label", "reference_text")
    autocomplete_fields = ("field", "option_scope")


@admin.register(ExamRule)
class ExamRuleAdmin(admin.ModelAdmin):
    list_display = ("exam_version", "rule_type", "target_type", "target_id", "sort_order", "active")
    list_filter = ("rule_type", "target_type", "active")
    search_fields = ("target_type",)
    autocomplete_fields = ("exam_version",)


@admin.register(ExamRenderProfile)
class ExamRenderProfileAdmin(admin.ModelAdmin):
    list_display = ("exam_version", "layout_type", "active")
    list_filter = ("layout_type", "active")
    autocomplete_fields = ("exam_version",)
