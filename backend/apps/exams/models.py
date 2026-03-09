from django.db import models
from apps.common.choices import (
    ExamFieldDataTypeChoices,
    ExamFieldInputTypeChoices,
    ExamRuleTypeChoices,
    ExamVersionStatusChoices,
    RenderLayoutTypeChoices,
    SexChoices,
)
from apps.common.models import TimeStampedModel


class ExamDefinition(TimeStampedModel):
    exam_code = models.SlugField(max_length=64, unique=True)
    exam_name = models.CharField(max_length=255)
    category = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["exam_name"]

    def __str__(self):
        return self.exam_name


class ExamDefinitionVersion(models.Model):
    exam_definition = models.ForeignKey(
        "exams.ExamDefinition",
        on_delete=models.PROTECT,
        related_name="versions",
    )
    version_no = models.PositiveIntegerField()
    version_status = models.CharField(
        max_length=32,
        choices=ExamVersionStatusChoices.choices,
        default=ExamVersionStatusChoices.DRAFT,
    )
    source_type = models.CharField(max_length=32, blank=True)
    source_reference = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(blank=True, null=True)
    published_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="published_exam_versions",
    )
    change_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam_definition", "version_no"],
                name="uq_exam_version_number",
            ),
        ]
        indexes = [
            models.Index(fields=["version_status"]),
        ]

    def __str__(self):
        return f"{self.exam_definition.exam_code} v{self.version_no}"


class ExamOption(TimeStampedModel):
    exam_version = models.ForeignKey(
        "exams.ExamDefinitionVersion",
        on_delete=models.CASCADE,
        related_name="options",
    )
    option_key = models.SlugField(max_length=128)
    option_label = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam_version", "option_key"],
                name="uq_exam_option_key",
            ),
        ]

    def __str__(self):
        return self.option_label


class ExamSection(TimeStampedModel):
    exam_version = models.ForeignKey(
        "exams.ExamDefinitionVersion",
        on_delete=models.CASCADE,
        related_name="sections",
    )
    section_key = models.SlugField(max_length=128)
    section_label = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam_version", "section_key"],
                name="uq_exam_section_key",
            ),
        ]

    def __str__(self):
        return self.section_label


class ExamField(TimeStampedModel):
    exam_version = models.ForeignKey(
        "exams.ExamDefinitionVersion",
        on_delete=models.CASCADE,
        related_name="fields",
    )
    section = models.ForeignKey(
        "exams.ExamSection",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fields",
    )
    field_key = models.SlugField(max_length=128)
    field_label = models.CharField(max_length=255)
    input_type = models.CharField(max_length=32, choices=ExamFieldInputTypeChoices.choices)
    data_type = models.CharField(max_length=32, choices=ExamFieldDataTypeChoices.choices)
    unit = models.CharField(max_length=64, blank=True)
    required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    default_value = models.CharField(max_length=255, blank=True)
    help_text = models.TextField(blank=True)
    placeholder_text = models.CharField(max_length=255, blank=True)
    reference_text = models.CharField(max_length=255, blank=True)
    supports_attachment = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam_version", "field_key"],
                name="uq_exam_field_key",
            ),
        ]
        indexes = [
            models.Index(fields=["exam_version", "field_key"]),
            models.Index(fields=["input_type"]),
        ]

    def __str__(self):
        return self.field_label


class ExamFieldSelectOption(TimeStampedModel):
    field = models.ForeignKey(
        "exams.ExamField",
        on_delete=models.CASCADE,
        related_name="select_options",
    )
    option_value = models.CharField(max_length=255)
    option_label = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.option_label


class ExamFieldReferenceRange(TimeStampedModel):
    field = models.ForeignKey(
        "exams.ExamField",
        on_delete=models.CASCADE,
        related_name="reference_ranges",
    )
    option_scope = models.ForeignKey(
        "exams.ExamOption",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reference_ranges",
    )
    sex_scope = models.CharField(max_length=16, choices=SexChoices.choices, blank=True)
    range_type = models.CharField(max_length=32)
    min_numeric = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    max_numeric = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    reference_text = models.CharField(max_length=255, blank=True)
    abnormal_rule = models.CharField(max_length=64, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.reference_text or self.range_type


class ExamRule(TimeStampedModel):
    exam_version = models.ForeignKey(
        "exams.ExamDefinitionVersion",
        on_delete=models.CASCADE,
        related_name="rules",
    )
    rule_type = models.CharField(max_length=32, choices=ExamRuleTypeChoices.choices)
    target_type = models.CharField(max_length=32)
    target_id = models.PositiveIntegerField()
    condition_json = models.JSONField(default=dict, blank=True)
    effect_json = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.rule_type} -> {self.target_type}:{self.target_id}"


class ExamRenderProfile(TimeStampedModel):
    exam_version = models.OneToOneField(
        "exams.ExamDefinitionVersion",
        on_delete=models.CASCADE,
        related_name="render_profile",
    )
    layout_type = models.CharField(max_length=32, choices=RenderLayoutTypeChoices.choices)
    config_json = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.exam_version} ({self.layout_type})"
