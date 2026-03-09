# XLSX-First Database and Metadata Design

## Goal
Turn the workbook-driven exam requirements into a database design that:
- keeps the clinic core stable
- allows configurable exam definitions
- supports packages/options
- supports sections and repeated labels
- preserves history when exam configs change

This design assumes:
- the workbook is the primary source of truth
- print layout is a separate concern

## Design principle
Do not store each exam as its own SQL table.

Do not store everything as unstructured JSON either.

Use a hybrid model:
- relational core for clinic operations
- relational metadata for configurable exams
- row-based result storage tied to immutable exam versions

## Big picture

### Fixed core
These entities should remain normal application tables:
- patients
- lab_requests
- lab_request_items
- physicians
- rooms
- signatories
- users
- roles
- attachments
- audit_logs

### Dynamic exam engine
These entities define how an exam behaves:
- exam_definitions
- exam_definition_versions
- exam_options
- exam_sections
- exam_fields
- exam_field_select_options
- exam_field_reference_ranges
- exam_rules

### Saved results
These entities store actual patient results:
- lab_request_items
- lab_result_values

## Why this shape fits the workbook
The workbook is not a flat list of fields.

It contains:
- shared patient/request fields
- exam options/packages
- section headers
- field rows
- units
- dropdown values
- normal ranges
- notes

Also, workbook column usage changes by context:
- for dropdown fields, column C usually contains selectable options
- for numeric/manual fields, column C often contains the unit
- column D often contains normal/reference values
- column E sometimes contains behavior notes

So the metadata model must separate:
- field type
- unit
- select options
- reference ranges
- notes/rules

## Recommended tables

## 1. `patients`
Purpose:
- store the patient master record if the clinic wants persistent patient history

Recommended columns:
- `id`
- `patient_code`
- `full_name`
- `sex`
- `birth_date`
- `contact_no`
- `address`
- `created_at`
- `updated_at`

Important note:
- because the workbook only guarantees `Name`, `Age`, and `Sex`, some fields here may stay optional in v1

## 2. `physicians`
Purpose:
- master data for requesting physicians

Recommended columns:
- `id`
- `physician_code`
- `display_name`
- `active`
- `created_at`
- `updated_at`

## 3. `rooms`
Purpose:
- master data for room/location selection

Recommended columns:
- `id`
- `room_code`
- `display_name`
- `active`
- `created_at`
- `updated_at`

## 4. `signatories`
Purpose:
- master list for medtech/pathologist identities shown on results

Recommended columns:
- `id`
- `signatory_type`
- `display_name`
- `license_no`
- `signature_image_path`
- `active`
- `created_at`
- `updated_at`

Suggested values for `signatory_type`:
- `medtech`
- `pathologist`

## 5. `lab_requests`
Purpose:
- one request/encounter from which one or more exam items can exist

Recommended columns:
- `id`
- `request_no`
- `case_number`
- `patient_id` nullable
- `patient_name_snapshot`
- `age_snapshot_text`
- `sex_snapshot`
- `request_datetime`
- `physician_id`
- `physician_name_snapshot`
- `room_id`
- `room_name_snapshot`
- `created_by_user_id`
- `status`
- `notes`
- `created_at`
- `updated_at`

Reason for snapshots:
- printed/result history should remain correct even if master data changes later

Suggested `status` values:
- `draft`
- `in_progress`
- `completed`
- `released`
- `cancelled`

## 6. `lab_request_items`
Purpose:
- one selected exam item under a request

Examples:
- one request can contain `URINALYSIS`
- plus `PREGNANCY TEST`
- plus `HBA1C`

Recommended columns:
- `id`
- `lab_request_id`
- `exam_definition_id`
- `exam_definition_version_id`
- `exam_option_id` nullable
- `item_status`
- `performed_at`
- `released_at`
- `printed_at`
- `medtech_signatory_id` nullable
- `pathologist_signatory_id` nullable
- `created_by_user_id`
- `released_by_user_id` nullable
- `notes`
- `created_at`
- `updated_at`

Suggested `item_status` values:
- `draft`
- `encoding`
- `for_review`
- `released`
- `void`

## 7. `exam_definitions`
Purpose:
- stable exam family record

Examples:
- `URINE`
- `SEROLOGY`
- `OGTT`
- `ABG`

Recommended columns:
- `id`
- `exam_code`
- `exam_name`
- `category`
- `description`
- `active`
- `created_at`
- `updated_at`

Examples:
- `exam_code = OGTT`
- `exam_name = Oral Glucose Tolerance Test`

## 8. `exam_definition_versions`
Purpose:
- immutable published version of an exam definition

This is critical.

If the admin edits an exam later, old results must still point to the old version.

Recommended columns:
- `id`
- `exam_definition_id`
- `version_no`
- `version_status`
- `source_type`
- `source_reference`
- `published_at`
- `published_by_user_id`
- `change_summary`
- `created_at`

Suggested `version_status` values:
- `draft`
- `published`
- `archived`

Suggested `source_type` values:
- `xlsx_import`
- `manual_admin`

Rule:
- published versions must become read-only

## 9. `exam_options`
Purpose:
- requestable package/variant choices under a version

Examples from workbook:
- `50g OGTT`
- `75g OGTT`
- `100g OGTT`
- `CBC, PLATELET COUNT, ESR`
- `PROTIME, APTT`

Recommended columns:
- `id`
- `exam_definition_version_id`
- `option_key`
- `option_label`
- `sort_order`
- `active`

Examples:
- `option_key = ogtt_50g`
- `option_key = ogtt_75g`
- `option_key = hematology_cbc_platelet_esr`

## 10. `exam_sections`
Purpose:
- logical grouping of fields for UI and future print layout

Examples:
- `MACROSCOPIC FINDING`
- `CLINICAL FINDING`
- `MICROSCOPIC FINDING`
- `PRO TIME`
- `APTT`

Recommended columns:
- `id`
- `exam_definition_version_id`
- `section_key`
- `section_label`
- `sort_order`
- `active`

Optional columns:
- `display_style`
- `visibility_mode`

## 11. `exam_fields`
Purpose:
- define the actual input/result fields

This is the most important table in the engine.

Recommended columns:
- `id`
- `exam_definition_version_id`
- `section_id` nullable
- `field_key`
- `field_label`
- `input_type`
- `data_type`
- `unit`
- `required`
- `sort_order`
- `default_value`
- `help_text`
- `placeholder_text`
- `reference_text`
- `supports_attachment`
- `active`

Recommended `input_type` values:
- `text`
- `textarea`
- `number`
- `decimal`
- `select`
- `date`
- `datetime`
- `boolean`
- `attachment`
- `display_note`
- `grouped_measurement`

Recommended `data_type` values:
- `string`
- `int`
- `decimal`
- `date`
- `datetime`
- `boolean`
- `json`

Important rule:
- `field_key` must be stable and unique within a version
- labels can change, keys should remain stable

## 12. `exam_field_select_options`
Purpose:
- selectable options for dropdown fields

Recommended columns:
- `id`
- `field_id`
- `option_value`
- `option_label`
- `sort_order`
- `active`

Examples:
- for `Sex`: `male`, `female`
- for `Pregnancy Test`: `positive`, `negative`
- for `MICROBIOLOGY.RESULT`: `NO FUNGAL ELEMENTS SEEN`, `POSITIVE FOR FUNGAL ELEMENTS`

## 13. `exam_field_reference_ranges`
Purpose:
- store normal/reference ranges separate from field structure

This is needed because some ranges depend on sex or context.

Recommended columns:
- `id`
- `field_id`
- `sex_scope` nullable
- `option_scope` nullable
- `range_type`
- `min_numeric` nullable
- `max_numeric` nullable
- `reference_text`
- `abnormal_rule`
- `sort_order`

Suggested `range_type` values:
- `numeric_between`
- `numeric_less_than`
- `numeric_greater_than`
- `text_reference`

Suggested `sex_scope` values:
- `male`
- `female`
- `all`

Examples:
- `HEMOGLOBIN (M)` range
- `HEMOGLOBIN (F)` range
- `OGTT 50g 1ST HOUR < 200 mg/dl`

## 14. `exam_rules`
Purpose:
- controlled rule table for visibility and requirement logic

Do not allow arbitrary scripts in v1.

Recommended columns:
- `id`
- `exam_definition_version_id`
- `rule_type`
- `target_type`
- `target_id`
- `condition_json`
- `effect_json`
- `sort_order`
- `active`

Suggested `rule_type` values:
- `visibility`
- `requirement`
- `abnormal_flag`
- `attachment_requirement`

Suggested `target_type` values:
- `section`
- `field`

Example rule:
- show `ogtt_100g` section when selected option = `ogtt_100g`

## 15. `attachments`
Purpose:
- store exam-related uploaded files such as result images

Recommended columns:
- `id`
- `lab_request_item_id`
- `attachment_type`
- `file_name`
- `storage_path`
- `mime_type`
- `uploaded_by_user_id`
- `created_at`

This is important for future support of:
- `COVID` result image
- scanned references
- supporting documents

## 16. `lab_result_values`
Purpose:
- store actual encoded result values per field

Recommended columns:
- `id`
- `lab_request_item_id`
- `field_id`
- `field_key_snapshot`
- `field_label_snapshot`
- `section_key_snapshot`
- `input_type_snapshot`
- `unit_snapshot`
- `value_text` nullable
- `value_number` nullable
- `value_boolean` nullable
- `value_date` nullable
- `value_datetime` nullable
- `value_json` nullable
- `selected_option_value` nullable
- `selected_option_label_snapshot` nullable
- `reference_text_snapshot`
- `abnormal_flag`
- `abnormal_reason`
- `sort_order_snapshot`
- `created_at`
- `updated_at`

Why keep snapshots even if `field_id` exists:
- safer reporting/history
- protects old results if labels later change in newer versions

## 17. `users`
Purpose:
- application user accounts

Recommended columns:
- `id`
- `username`
- `display_name`
- `password_hash`
- `active`
- `created_at`
- `updated_at`

## 18. `roles` and `user_roles`
Purpose:
- permission boundaries

Possible roles:
- `admin`
- `encoder`
- `medtech`
- `reviewer`
- `pathologist`

## 19. `audit_logs`
Purpose:
- track who changed what and when

Recommended columns:
- `id`
- `user_id`
- `entity_type`
- `entity_id`
- `action`
- `before_json`
- `after_json`
- `created_at`

This is important because a configurable system is more sensitive to bad edits.

## How workbook rows translate into this model

## General mapping rules

### Shared patient/request rows
Workbook rows like:
- `Name`
- `Age`
- `Sex`
- `Date`
- `Requesting Physician`
- `Room`
- `Case Number`

Map to:
- fixed request-entry UI
- fixed request tables

They do **not** become exam-specific dynamic fields.

### `Examination` row
Workbook row `Examination` usually contains multiple choices.

Map to:
- `exam_options`

### Blank `Input Type` rows
Rows whose field labels are section headings, like:
- `MACROSCOPIC FINDING`
- `PRO TIME`
- `APTT`

Map to:
- `exam_sections`

### `Predefined Selection` rows
Map to:
- `exam_fields` with `input_type = select`
- plus child rows in `exam_field_select_options`

### `Manual Entry` rows with unit text
Map to:
- `exam_fields.unit`

Examples:
- `mg/dl`
- `mmHg`
- `U/L`
- `%`

### Normal value / reference columns
Map to:
- `exam_field_reference_ranges`

### Notes column
Map to:
- `exam_fields.help_text`
- or `exam_rules`
- or feature flags such as attachment support

## Example mappings

## Example 1. `MICROBIOLOGY`
Workbook structure:
- one option: `KOH SMEAR`
- one result field: `RESULT`
- dropdown values: `NO FUNGAL ELEMENTS SEEN`, `POSITIVE FOR FUNGAL ELEMENTS`

Database interpretation:
- one `exam_definition`
- one `exam_definition_version`
- one `exam_option`
- one `exam_field` with `input_type = select`
- two `exam_field_select_options`

This is a very clean low-complexity exam.

## Example 2. `OGTT`
Workbook structure:
- one exam family
- five request options/packages
- repeated labels like `1ST HOUR`, `2ND HOUR`, `FASTING BLOOD SUGAR`
- multiple sections

This must not use visible labels as keys.

Recommended field keys:
- `ogtt_50g_1st_hour`
- `ogtt_50g_2nd_hour`
- `ogtt_75g_fasting_blood_sugar`
- `ogtt_75g_1st_hour`
- `ogtt_75g_2nd_hour`
- `ogtt_100g_fasting_blood_sugar`
- `ogtt_100g_1st_hour`
- `ogtt_100g_2nd_hour`
- `ogtt_100g_3rd_hour`
- `ogtt_2hr_postprandial`
- `ogtt_50g_glucose_challenge`

Visibility rules decide which fields appear when a specific option is chosen.

## Example 3. `SEROLOGY`
Workbook structure:
- repeated `IgM` and `IgG`
- multiple groups: typhidot, dengue, malarial, single-result tests

Recommended field keys:
- `typhidot_igm`
- `typhidot_igg`
- `dengue_ns1ag`
- `dengue_igm`
- `dengue_igg`
- `malarial_antiplasmodium_falciparum`
- `malarial_antiplasmodium_vivax`
- `hbsag_screening`
- `vdrl`
- `anti_hcv`
- `aso_titer`
- `serology_other`

Again, display labels can stay user-friendly, but saved results should link to stable keys.

## Example 4. `BBANK` vital signs
Workbook note suggests `VITAL SIGNS` should not stay as one plain text blob.

Recommended interpretation:
- one section called `vital_signs`
- child fields:
- `vital_bp`
- `vital_pulse_rate`
- `vital_respiratory_rate`
- `vital_temperature`

This can be implemented in two ways:
- as four normal fields
- or as one grouped measurement field backed by JSON

Recommended v1:
- four normal fields

Reason:
- easier validation
- easier printing
- easier reporting

## Example 5. `COVID 19 ANTIGEN`
Workbook note says result needs a picture.

Recommended interpretation:
- one select field for `test_result`
- one attachment requirement rule
- attachment stored in `attachments`

## Versioning workflow

## Draft
- admin creates or edits an exam definition in draft mode

## Publish
- system validates the config
- creates a new immutable `exam_definition_version`
- new requests use this version

## Historical safety
- old `lab_request_items` remain linked to the old version
- their `lab_result_values` remain readable and printable

Rule:
- never edit a published version directly

## Recommended constraints

### Required constraints
- unique `exam_definitions.exam_code`
- unique `exam_definition_versions(exam_definition_id, version_no)`
- unique `exam_options(exam_definition_version_id, option_key)`
- unique `exam_sections(exam_definition_version_id, section_key)`
- unique `exam_fields(exam_definition_version_id, field_key)`

### Validation rules before publish
- no duplicate field keys
- no duplicate option keys
- all required fields have labels
- select fields have options
- numeric range configs are valid
- visibility rules refer to existing fields/options/sections

## Recommended admin restrictions
The admin panel should not allow arbitrary schema hacking.

It should allow only:
- create exam family
- create package/option
- create sections
- create fields using controlled field types
- define ranges
- define dropdown options
- define simple rules
- publish a new version

It should not allow in v1:
- custom executable formulas
- direct SQL-like logic
- editing historical published versions

## MVP recommendation
If you want the design to stay realistic, implement in this order:

### First
- fixed core tables
- exam definitions
- exam versions
- exam options
- exam sections
- exam fields
- select options
- saved result values

### Next
- reference ranges
- abnormal flags
- attachment support
- publish/version workflow

### Later
- richer rule builder
- print profile designer
- advanced reporting

## Final verdict
This workbook-driven database design is compatible with your configurable-exam idea.

It is strong enough for:
- simple exams
- section-based exams
- package-driven exams
- repeated-label exams
- sex-aware ranges
- future field changes

And it avoids the two bad extremes:
- one SQL table per exam
- totally uncontrolled free-form dynamic data
