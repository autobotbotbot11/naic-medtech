# System ERD

This ERD follows the approved direction:
- workbook-first
- fixed clinic core
- configurable exam schema
- versioned exam definitions
- row-based result storage

## ERD

```mermaid
erDiagram
    PATIENTS {
        int id PK
        string patient_code UK
        string full_name
        string sex
        date birth_date
        string contact_no
        string address
        datetime created_at
        datetime updated_at
    }

    PHYSICIANS {
        int id PK
        string physician_code UK
        string display_name
        boolean active
        datetime created_at
        datetime updated_at
    }

    ROOMS {
        int id PK
        string room_code UK
        string display_name
        boolean active
        datetime created_at
        datetime updated_at
    }

    SIGNATORIES {
        int id PK
        string signatory_type
        string display_name
        string license_no
        string signature_image_path
        boolean active
        datetime created_at
        datetime updated_at
    }

    USERS {
        int id PK
        string username UK
        string display_name
        string password_hash
        boolean active
        datetime created_at
        datetime updated_at
    }

    ROLES {
        int id PK
        string role_code UK
        string role_name
    }

    USER_ROLES {
        int id PK
        int user_id FK
        int role_id FK
    }

    LAB_REQUESTS {
        int id PK
        string request_no UK
        string case_number
        int patient_id FK
        string patient_name_snapshot
        string age_snapshot_text
        string sex_snapshot
        datetime request_datetime
        int physician_id FK
        string physician_name_snapshot
        int room_id FK
        string room_name_snapshot
        int created_by_user_id FK
        string status
        string notes
        datetime created_at
        datetime updated_at
    }

    EXAM_DEFINITIONS {
        int id PK
        string exam_code UK
        string exam_name
        string category
        string description
        boolean active
        datetime created_at
        datetime updated_at
    }

    EXAM_DEFINITION_VERSIONS {
        int id PK
        int exam_definition_id FK
        int version_no
        string version_status
        string source_type
        string source_reference
        datetime published_at
        int published_by_user_id FK
        string change_summary
        datetime created_at
    }

    EXAM_OPTIONS {
        int id PK
        int exam_definition_version_id FK
        string option_key
        string option_label
        int sort_order
        boolean active
    }

    EXAM_SECTIONS {
        int id PK
        int exam_definition_version_id FK
        string section_key
        string section_label
        int sort_order
        boolean active
    }

    EXAM_FIELDS {
        int id PK
        int exam_definition_version_id FK
        int section_id FK
        string field_key
        string field_label
        string input_type
        string data_type
        string unit
        boolean required
        int sort_order
        string default_value
        string help_text
        string placeholder_text
        string reference_text
        boolean supports_attachment
        boolean active
    }

    EXAM_FIELD_SELECT_OPTIONS {
        int id PK
        int field_id FK
        string option_value
        string option_label
        int sort_order
        boolean active
    }

    EXAM_FIELD_REFERENCE_RANGES {
        int id PK
        int field_id FK
        int option_scope_id FK
        string sex_scope
        string range_type
        decimal min_numeric
        decimal max_numeric
        string reference_text
        string abnormal_rule
        int sort_order
    }

    EXAM_RULES {
        int id PK
        int exam_definition_version_id FK
        string rule_type
        string target_type
        int target_id
        string condition_json
        string effect_json
        int sort_order
        boolean active
    }

    LAB_REQUEST_ITEMS {
        int id PK
        int lab_request_id FK
        int exam_definition_id FK
        int exam_definition_version_id FK
        int exam_option_id FK
        string item_status
        datetime performed_at
        datetime released_at
        datetime printed_at
        int medtech_signatory_id FK
        int pathologist_signatory_id FK
        int created_by_user_id FK
        int released_by_user_id FK
        string notes
        datetime created_at
        datetime updated_at
    }

    LAB_RESULT_VALUES {
        int id PK
        int lab_request_item_id FK
        int field_id FK
        string field_key_snapshot
        string field_label_snapshot
        string section_key_snapshot
        string input_type_snapshot
        string unit_snapshot
        string value_text
        decimal value_number
        boolean value_boolean
        date value_date
        datetime value_datetime
        string value_json
        string selected_option_value
        string selected_option_label_snapshot
        string reference_text_snapshot
        boolean abnormal_flag
        string abnormal_reason
        int sort_order_snapshot
        datetime created_at
        datetime updated_at
    }

    ATTACHMENTS {
        int id PK
        int lab_request_item_id FK
        string attachment_type
        string file_name
        string storage_path
        string mime_type
        int uploaded_by_user_id FK
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string entity_type
        int entity_id
        string action
        string before_json
        string after_json
        datetime created_at
    }

    PATIENTS ||--o{ LAB_REQUESTS : has
    PHYSICIANS ||--o{ LAB_REQUESTS : requested_by
    ROOMS ||--o{ LAB_REQUESTS : assigned_to
    USERS ||--o{ LAB_REQUESTS : created

    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : grants

    LAB_REQUESTS ||--o{ LAB_REQUEST_ITEMS : contains

    EXAM_DEFINITIONS ||--o{ EXAM_DEFINITION_VERSIONS : versions
    USERS ||--o{ EXAM_DEFINITION_VERSIONS : publishes
    EXAM_DEFINITION_VERSIONS ||--o{ EXAM_OPTIONS : has
    EXAM_DEFINITION_VERSIONS ||--o{ EXAM_SECTIONS : has
    EXAM_DEFINITION_VERSIONS ||--o{ EXAM_FIELDS : has
    EXAM_SECTIONS ||--o{ EXAM_FIELDS : groups
    EXAM_FIELDS ||--o{ EXAM_FIELD_SELECT_OPTIONS : offers
    EXAM_FIELDS ||--o{ EXAM_FIELD_REFERENCE_RANGES : uses
    EXAM_OPTIONS ||--o{ EXAM_FIELD_REFERENCE_RANGES : scopes
    EXAM_DEFINITION_VERSIONS ||--o{ EXAM_RULES : applies

    EXAM_DEFINITIONS ||--o{ LAB_REQUEST_ITEMS : selected_as
    EXAM_DEFINITION_VERSIONS ||--o{ LAB_REQUEST_ITEMS : locked_to
    EXAM_OPTIONS ||--o{ LAB_REQUEST_ITEMS : chosen_as
    SIGNATORIES ||--o{ LAB_REQUEST_ITEMS : medtech_signs
    SIGNATORIES ||--o{ LAB_REQUEST_ITEMS : pathologist_signs
    USERS ||--o{ LAB_REQUEST_ITEMS : creates
    USERS ||--o{ LAB_REQUEST_ITEMS : releases

    LAB_REQUEST_ITEMS ||--o{ LAB_RESULT_VALUES : stores
    EXAM_FIELDS ||--o{ LAB_RESULT_VALUES : records

    LAB_REQUEST_ITEMS ||--o{ ATTACHMENTS : includes
    USERS ||--o{ ATTACHMENTS : uploads

    USERS ||--o{ AUDIT_LOGS : writes
```

## Read This In 3 Layers

### 1. Clinic core
These are the stable operational entities:
- `PATIENTS`
- `PHYSICIANS`
- `ROOMS`
- `SIGNATORIES`
- `USERS`
- `ROLES`
- `USER_ROLES`
- `LAB_REQUESTS`

This layer should remain mostly fixed even if exams change.

### 2. Configurable exam engine
These define what an exam looks like:
- `EXAM_DEFINITIONS`
- `EXAM_DEFINITION_VERSIONS`
- `EXAM_OPTIONS`
- `EXAM_SECTIONS`
- `EXAM_FIELDS`
- `EXAM_FIELD_SELECT_OPTIONS`
- `EXAM_FIELD_REFERENCE_RANGES`
- `EXAM_RULES`

This is where the workbook-driven flexibility lives.

### 3. Saved clinical results
These store the actual encoded result records:
- `LAB_REQUEST_ITEMS`
- `LAB_RESULT_VALUES`
- `ATTACHMENTS`
- `AUDIT_LOGS`

This layer must be historically stable.

## Relationship Notes

### `LAB_REQUESTS` -> `LAB_REQUEST_ITEMS`
One request can contain multiple exam items.

Examples:
- one request with `URINALYSIS`
- one request with `URINALYSIS` plus `PREGNANCY TEST`
- one request with `CBC` plus `HBA1C`

### `EXAM_DEFINITIONS` -> `EXAM_DEFINITION_VERSIONS`
An exam family can have many versions.

Example:
- `OGTT` version 1
- `OGTT` version 2 after admin changes fields/ranges

### `EXAM_DEFINITION_VERSIONS` -> `EXAM_OPTIONS`
A version can expose multiple requestable options/packages.

Examples:
- `50g OGTT`
- `75g OGTT`
- `100g OGTT`

### `EXAM_DEFINITION_VERSIONS` -> `EXAM_SECTIONS`
A version can define logical groups used in UI and future printing.

Examples:
- `MACROSCOPIC FINDING`
- `PRO TIME`
- `APTT`

### `EXAM_DEFINITION_VERSIONS` -> `EXAM_FIELDS`
Each published version owns its exact field list.

This is how we avoid changing database tables whenever a field changes.

### `EXAM_FIELDS` -> `EXAM_FIELD_SELECT_OPTIONS`
Only select/dropdown fields will use child options.

### `EXAM_FIELDS` -> `EXAM_FIELD_REFERENCE_RANGES`
Ranges are stored separately because:
- not all fields have ranges
- some fields have sex-specific ranges
- some fields have option/package-specific ranges

### `LAB_REQUEST_ITEMS` -> `EXAM_DEFINITION_VERSIONS`
This relationship is one of the most important in the system.

Each saved exam item must point to the exact published version that was active when the result was encoded.

That prevents old results from breaking when the admin changes a future version.

### `LAB_RESULT_VALUES` -> `EXAM_FIELDS`
A saved result row points to the field definition it came from, but also stores snapshots such as:
- field key
- field label
- unit
- reference text

This adds historical safety.

## Why `field_key` Matters
The workbook has repeated visible labels such as:
- `IgM`
- `IgG`
- `1ST HOUR`
- `2ND HOUR`
- `TEST`
- `CONTROL`

So visible labels are not reliable identifiers.

Examples of correct internal keys:
- `typhidot_igm`
- `dengue_igm`
- `ogtt_50g_1st_hour`
- `aptt_test`
- `protime_test`

## Why `EXAM_DEFINITION_VERSIONS` Matters
Without versioning:
- old results can become unreadable
- labels can change retroactively
- reference ranges can shift unexpectedly
- audit history becomes weak

With versioning:
- published exam schemas become immutable
- new edits create a new version
- historical requests remain tied to the exact old schema

## Optional Simplification For MVP
If you want a simpler v1, these can be deferred:
- `ROLES` / `USER_ROLES` if using very basic user roles first
- `EXAM_RULES` if you hardcode minimal visibility rules temporarily
- advanced attachment types

But these should stay in the long-term ERD because the workbook suggests they will be needed.

## Recommended Next Step
After you approve this ERD, the best next move is:
- convert this into Django models

Suggested Django app split:
- `core`
- `exams`
- `results`
- `accounts`
