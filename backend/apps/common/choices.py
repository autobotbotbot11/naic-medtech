from django.db import models


class SexChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


class SignatoryTypeChoices(models.TextChoices):
    MEDTECH = "medtech", "Medical Technologist"
    PATHOLOGIST = "pathologist", "Pathologist"


class UserRoleChoices(models.TextChoices):
    SYSTEM_OWNER = "system_owner", "System Owner"
    ADMIN = "admin", "Admin"
    ENCODER = "encoder", "Encoder"
    VIEWER = "viewer", "Viewer"


class LabRequestStatusChoices(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    RELEASED = "released", "Released"
    CANCELLED = "cancelled", "Cancelled"


class LabRequestItemStatusChoices(models.TextChoices):
    DRAFT = "draft", "Draft"
    ENCODING = "encoding", "Encoding"
    FOR_REVIEW = "for_review", "For Review"
    RELEASED = "released", "Released"
    VOID = "void", "Void"


class ExamVersionStatusChoices(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class ExamFieldInputTypeChoices(models.TextChoices):
    TEXT = "text", "Text"
    TEXTAREA = "textarea", "Textarea"
    INTEGER = "integer", "Integer"
    DECIMAL = "decimal", "Decimal"
    SELECT = "select", "Select"
    DATE = "date", "Date"
    DATETIME = "datetime", "Datetime"
    BOOLEAN = "boolean", "Boolean"
    ATTACHMENT = "attachment", "Attachment"
    DISPLAY_NOTE = "display_note", "Display Note"
    GROUPED_MEASUREMENT = "grouped_measurement", "Grouped Measurement"


class ExamFieldDataTypeChoices(models.TextChoices):
    STRING = "string", "String"
    INT = "int", "Integer"
    DECIMAL = "decimal", "Decimal"
    DATE = "date", "Date"
    DATETIME = "datetime", "Datetime"
    BOOLEAN = "boolean", "Boolean"
    JSON = "json", "JSON"


class ExamRuleTypeChoices(models.TextChoices):
    VISIBILITY = "visibility", "Visibility"
    REQUIREMENT = "requirement", "Requirement"
    RANGE_SELECTION = "range_selection", "Range Selection"
    ABNORMAL_FLAG = "abnormal_flag", "Abnormal Flag"
    VALIDATION = "validation", "Validation"


class RenderLayoutTypeChoices(models.TextChoices):
    LABEL_VALUE_LIST = "label_value_list", "Label Value List"
    RESULT_TABLE = "result_table", "Result Table"
    SECTIONED_REPORT = "sectioned_report", "Sectioned Report"
    GROUPED_MEASUREMENTS = "grouped_measurements", "Grouped Measurements"
