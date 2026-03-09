# Django Models Design

## Context
There is no existing Django project yet in the workspace.

So this document converts the approved system design into:
- Django app split
- Django model list
- Django-specific implementation choices
- MVP-safe simplifications

This is the direct bridge between:
- ERD
- actual `models.py`

## Main recommendation
Use:
- `Django`
- `SQLite` for local MVP
- built-in Django auth where possible

## Important Django-specific adjustment
In the ERD, we had:
- `USERS`
- `ROLES`
- `USER_ROLES`

For Django, the practical implementation is:
- custom `User` model extending `AbstractUser`
- Django `Group` and `Permission` for roles/permissions

This is better than building a custom role engine from scratch in v1.

So for actual Django implementation:
- keep custom `User`
- use built-in `Group`
- do not create a custom `Role` model yet unless needed later

## Proposed Django app split

### `accounts`
Purpose:
- user authentication
- role/group assignment

Models:
- `User`

### `core`
Purpose:
- stable clinic entities

Models:
- `Patient`
- `Physician`
- `Room`
- `Signatory`
- `LabRequest`

### `exams`
Purpose:
- configurable exam engine

Models:
- `ExamDefinition`
- `ExamDefinitionVersion`
- `ExamOption`
- `ExamSection`
- `ExamField`
- `ExamFieldSelectOption`
- `ExamFieldReferenceRange`
- `ExamRule`
- `ExamRenderProfile`

### `results`
Purpose:
- saved exam records and outputs

Models:
- `LabRequestItem`
- `LabResultValue`
- `Attachment`
- `AuditLog`

## Shared base model
Recommended:
- one abstract timestamp base model

Example:

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

## Enums / choices to define centrally

Recommended Django `TextChoices`:
- `SexChoices`
- `SignatoryTypeChoices`
- `LabRequestStatusChoices`
- `LabRequestItemStatusChoices`
- `ExamVersionStatusChoices`
- `ExamFieldInputTypeChoices`
- `ExamFieldDataTypeChoices`
- `ExamRuleTypeChoices`
- `RenderLayoutTypeChoices`

This keeps logic cleaner than using raw strings everywhere.

## Accounts app

## `accounts.User`
Recommended implementation:
- extend `AbstractUser`

Suggested fields:
- `display_name`
- `is_active`
- `created_at`
- `updated_at`

Possible model:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    display_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.username
```

Important setting:

```python
AUTH_USER_MODEL = "accounts.User"
```

## Core app

## `core.Patient`
Purpose:
- persistent patient record if the clinic wants patient history

Recommended fields:
- `patient_code`
- `full_name`
- `sex`
- `birth_date`
- `contact_no`
- `address`

Suggested model:

```python
class Patient(TimeStampedModel):
    patient_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=16, choices=SexChoices.choices, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    contact_no = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]
```

## `core.Physician`

```python
class Physician(TimeStampedModel):
    physician_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    display_name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_name"]
```

## `core.Room`

```python
class Room(TimeStampedModel):
    room_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    display_name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_name"]
```

## `core.Signatory`

```python
class Signatory(TimeStampedModel):
    signatory_type = models.CharField(max_length=32, choices=SignatoryTypeChoices.choices)
    display_name = models.CharField(max_length=255)
    license_no = models.CharField(max_length=128, blank=True)
    signature_image = models.ImageField(upload_to="signatures/", blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["signatory_type", "display_name"]
```

## `core.LabRequest`
Purpose:
- the operational request/encounter

Important:
- keep snapshots even if foreign keys exist

```python
class LabRequest(TimeStampedModel):
    request_no = models.CharField(max_length=64, unique=True)
    case_number = models.CharField(max_length=64, blank=True)

    patient = models.ForeignKey(
        "core.Patient",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    patient_name_snapshot = models.CharField(max_length=255)
    age_snapshot_text = models.CharField(max_length=64, blank=True)
    sex_snapshot = models.CharField(max_length=16, choices=SexChoices.choices, blank=True)

    request_datetime = models.DateTimeField()

    physician = models.ForeignKey(
        "core.Physician",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    physician_name_snapshot = models.CharField(max_length=255, blank=True)

    room = models.ForeignKey(
        "core.Room",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lab_requests",
    )
    room_name_snapshot = models.CharField(max_length=255, blank=True)

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_lab_requests",
    )

    status = models.CharField(max_length=32, choices=LabRequestStatusChoices.choices, default=LabRequestStatusChoices.DRAFT)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-request_datetime", "-id"]
        indexes = [
            models.Index(fields=["request_no"]),
            models.Index(fields=["case_number"]),
            models.Index(fields=["request_datetime"]),
            models.Index(fields=["status"]),
        ]
```

## Exams app

## `exams.ExamDefinition`

```python
class ExamDefinition(TimeStampedModel):
    exam_code = models.SlugField(max_length=64, unique=True)
    exam_name = models.CharField(max_length=255)
    category = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["exam_name"]
```

## `exams.ExamDefinitionVersion`
Critical model for historical safety.

```python
class ExamDefinitionVersion(models.Model):
    exam_definition = models.ForeignKey(
        "exams.ExamDefinition",
        on_delete=models.PROTECT,
        related_name="versions",
    )
    version_no = models.PositiveIntegerField()
    version_status = models.CharField(max_length=32, choices=ExamVersionStatusChoices.choices, default=ExamVersionStatusChoices.DRAFT)
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
            models.UniqueConstraint(fields=["exam_definition", "version_no"], name="uq_exam_version_number"),
        ]
```

## `exams.ExamOption`

```python
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
            models.UniqueConstraint(fields=["exam_version", "option_key"], name="uq_exam_option_key"),
        ]
```

## `exams.ExamSection`

```python
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
            models.UniqueConstraint(fields=["exam_version", "section_key"], name="uq_exam_section_key"),
        ]
```

## `exams.ExamField`
Most important metadata table.

```python
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
            models.UniqueConstraint(fields=["exam_version", "field_key"], name="uq_exam_field_key"),
        ]
        indexes = [
            models.Index(fields=["exam_version", "field_key"]),
            models.Index(fields=["input_type"]),
        ]
```

## `exams.ExamFieldSelectOption`

```python
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
```

## `exams.ExamFieldReferenceRange`

```python
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
```

## `exams.ExamRule`
Use declarative rules, not scripts.

```python
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
```

## `exams.ExamRenderProfile`
This is the Django-side answer to the configurable rendering discussion.

For MVP, keep it controlled:
- one profile per exam version
- layout type + config JSON

```python
class ExamRenderProfile(TimeStampedModel):
    exam_version = models.OneToOneField(
        "exams.ExamDefinitionVersion",
        on_delete=models.CASCADE,
        related_name="render_profile",
    )
    layout_type = models.CharField(max_length=32, choices=RenderLayoutTypeChoices.choices)
    config_json = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
```

## Results app

## `results.LabRequestItem`
This locks a performed exam to a specific exam-definition version.

```python
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
    item_status = models.CharField(max_length=32, choices=LabRequestItemStatusChoices.choices, default=LabRequestItemStatusChoices.DRAFT)
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
```

## `results.LabResultValue`
Result storage is row-based and version-safe.

```python
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
```

## `results.Attachment`

```python
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
```

## `results.AuditLog`
For MVP, keep this generic.

```python
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
```

## Django implementation notes

## 1. Use `PROTECT` on version-sensitive metadata
Recommended for:
- `exam_definition`
- `exam_definition_version`
- `exam_field`

Reason:
- old result history must not break due to accidental deletes

## 2. Use snapshots in `LabResultValue`
Even though the row points to `field`, keep snapshots for:
- label
- key
- unit
- reference text

Reason:
- safer historical viewing/printing

## 3. Keep rules/render configs in `JSONField`
For MVP, JSON is acceptable here because:
- rules are structured but flexible
- rendering config is structured but variable

But avoid storing the actual clinical results in one giant JSON blob.

## 4. Add workbook import later
This model design is compatible with a later importer that will create:
- `ExamDefinition`
- `ExamDefinitionVersion`
- `ExamOption`
- `ExamSection`
- `ExamField`
- range rows
- dropdown option rows

from the workbook.

## 5. SQLite is acceptable for MVP
For local single-computer usage:
- acceptable
- simpler setup

Just keep the design database-agnostic so migration to MySQL/Postgres later is easier.

## Suggested build order

### First
- `accounts.User`
- `core.Patient`
- `core.Physician`
- `core.Room`
- `core.Signatory`
- `core.LabRequest`

### Second
- `exams.ExamDefinition`
- `exams.ExamDefinitionVersion`
- `exams.ExamOption`
- `exams.ExamSection`
- `exams.ExamField`
- `exams.ExamFieldSelectOption`
- `exams.ExamFieldReferenceRange`
- `exams.ExamRule`
- `exams.ExamRenderProfile`

### Third
- `results.LabRequestItem`
- `results.LabResultValue`
- `results.Attachment`
- `results.AuditLog`

## Final recommendation
After this document, the most natural next move is:
- scaffold the Django project
- create the four apps
- implement these models
- run migrations

That would be the first real code step from all the planning work.
