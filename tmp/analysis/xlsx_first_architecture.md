# XLSX-First Architecture Brief

## Decision
Use the workbook `NAIC MEDTECH SYSTEM DATA.xlsx` as the primary source of truth for:
- exam definitions
- field lists
- dropdown options
- normal ranges
- section/grouping
- notes and special rules

Treat the current Word print templates as:
- legacy reference only
- optional visual guide
- not the basis of the database design

## Why this is the correct direction
The workbook is the most complete structured source we currently have.

It contains:
- `16` exam sheets
- `62` distinct exam options/packages
- around `149` test-input rows
- common patient/request fields
- common master data lists
- notes about abnormal formatting and special handling

If we design from the old print templates, we inherit outdated layout assumptions.
If we design from the workbook, we design from the actual data-entry requirements.

## What the workbook tells us

### Fixed shared data exists across nearly all exams
These appear repeatedly and should be part of the fixed core:
- Name
- Age
- Sex
- Date or Date/Time
- Examination
- Requesting Physician
- Room
- Case Number
- Medical Technologist
- Pathologist

Common master data visible in the workbook:
- `29` requesting physicians
- `21` rooms
- `6` medtech signatories
- `1` pathologist

### Exam data is variable and should be configurable
Patterns found in the workbook:
- some exams are mostly dropdown-based
- some exams are mostly manual numeric entry
- some have normal ranges
- some have sections
- some have repeated labels
- some depend on selected package
- some depend on patient sex
- some carry special notes

So the exam layer should be configurable.

## The right architecture boundary

### Fixed core
These should remain standard relational entities:
- patients
- lab requests / encounters
- request items
- physicians
- rooms
- signatories
- users
- roles / permissions
- audit logs
- result release status
- attachments/files

### Dynamic exam configuration
These should be configurable by admin or super-admin:
- exam definitions
- exam packages/options
- exam sections
- result fields
- field types
- dropdown options
- units
- normal ranges
- abnormal flagging rules
- visibility rules
- requirement rules
- attachment requirements

## Important correction
Do not think of the system as:
- "custom database fields"

Think of it as:
- "configurable exam schema"

That distinction matters because the workbook does not describe random fields.
It describes structured lab forms with:
- grouped sections
- repeated field labels in different contexts
- package-specific subsets
- domain-specific validation

## Why a simple free-form builder is not enough
The workbook has several patterns that break a naive field-builder approach.

### 1. Repeated labels
Visible labels are not unique.

Examples:
- `SEROLOGY`: `IgM`, `IgG` appear more than once
- `OGTT`: `1ST HOUR`, `2ND HOUR`, `FASTING BLOOD SUGAR` repeat across packages
- `PROTIME, APTT`: `TEST` and `CONTROL` repeat in separate sections

Implication:
- every field needs an internal stable key
- the visible label alone cannot identify a field

### 2. Packages and variants
Some sheets are really one exam family with multiple request options.

Examples:
- `OGTT`: `50g`, `75g`, `100g`, `2-HOUR POSTPRANDIAL`, `50g ORAL GLUCOSE CHALLENGE`
- `HEMATOLOGY`: different bundles such as `CBC, PLATELET COUNT, ESR`
- `PROTIME, APTT`: one or both sections may be active

Implication:
- the system must support exam option/package selection
- fields should show/hide based on the selected option

### 3. Sex-specific behavior
Examples:
- `BCMALE`
- `BCFEMALE`
- `HEMATOLOGY` includes male/female ranges for some fields

Implication:
- the engine must support sex-based range or variant logic

### 4. Composite/special fields
Examples:
- `BBANK` vital signs is not really one simple field
- `COVID` note implies image support
- `ABG` has a `NOTE` row that is not a normal result field

Implication:
- the system must support special field types or grouped subfields

## Minimum capabilities required in the dynamic engine

### Per exam definition
- exam code
- exam name
- category
- active/inactive status
- version

### Per exam option/package
- option code
- option name
- exam reference
- sort order
- active/inactive

### Per section
- section key
- section label
- order
- visibility condition

### Per field
- field key
- display label
- section
- input type
- data type
- unit
- normal range/reference
- required flag
- sort order
- default value
- visibility condition
- abnormal-highlighting rule
- option/package scope
- sex scope if needed
- attachment flag if needed

### Per dropdown option
- field reference
- label
- value
- sort order
- active/inactive

## Recommended controlled field types
Do not allow arbitrary field types on day 1.

Use a controlled set:
- short text
- long text
- number
- decimal number
- dropdown single-select
- dropdown multi-select if truly needed
- date
- datetime
- yes/no
- attachment/image
- grouped measurement

## Recommended rule types
Do not allow arbitrary code-like formulas in v1.

Use controlled rule types:
- show field when exam option = X
- show field when sex = X
- require field when exam option = X
- mark abnormal when value outside normal range
- require attachment when exam = X

## Per-exam behavior summary from the workbook

### Simple configurable exams
These are mostly straightforward:
- `MICROBIOLOGY`
- `HBA1C`
- `CARDIACI`
- `HIV 1&2 TESTING`
- `COVID 19 ANTIGEN`

These are good candidates for first implementation.

### Section-based exams
These need grouped UI sections:
- `URINE`
- `SEROLOGY`
- `SEMEN`
- `OGTT`
- `FECALYSIS`
- `BBANK`
- `ABG`
- `PROTIME, APTT`

### Package/option-driven exams
These need condition-based visibility:
- `URINE`
- `OGTT`
- `HEMATOLOGY`
- `BCMALE`
- `BCFEMALE`
- `PROTIME, APTT`
- `FECALYSIS`
- `SEROLOGY`

### Exams with repeated labels requiring internal keys
- `SEROLOGY`
- `OGTT`
- `PROTIME, APTT`

### Exams with sex-specific logic
- `BCMALE`
- `BCFEMALE`
- `HEMATOLOGY`

### Exams with special handling
- `BBANK` because of grouped vital signs
- `COVID 19 ANTIGEN` because of image note
- `ABG` because of non-standard note row

## What this means for the admin panel
The admin panel should not just ask:
- field name
- input type

It should let the admin define:
- exam
- package/option
- section
- field key
- field label
- field type
- unit
- normal range
- dropdown values
- visibility rules
- special requirements

And it should restrict edits through validation.

## Required safeguards

### 1. Versioning
Every exam definition must be versioned.

Reason:
- if the admin edits `ABG` tomorrow, old saved results must still open correctly

### 2. Publish workflow
Use draft/published states for exam configs.

Reason:
- the admin should not accidentally break live encoding forms

### 3. Stable internal keys
Field labels may change.
Field keys should not.

### 4. Validation before publish
At minimum validate:
- duplicate field keys
- missing labels
- invalid ranges
- invalid dropdown setup
- fields with impossible visibility rules

## Recommended MVP direction
To avoid overbuilding, v1 should support:
- fixed patient/request records
- configurable exam definitions
- configurable packages/options
- configurable sections
- configurable fields
- configurable dropdowns
- configurable normal ranges
- abnormal highlighting
- attachments for selected exams
- exam-definition versioning

Avoid in v1:
- fully visual print-template designer
- arbitrary formulas/scripts in admin panel
- user-generated database structure outside the exam engine

## Practical recommendation
The best next move is not to design final SQL tables yet.

The best next move is:
1. define the fixed core entities
2. define the dynamic exam metadata model
3. define how one workbook sheet translates into exam config records
4. define how saved results reference a specific exam-definition version

## Final verdict
Using the workbook as the main basis makes the project more coherent.

It strengthens your configurable-exam idea.

But the correct implementation is:
- not `free-form everything`
- not `fixed table per exam`
- but `fixed LIS core + controlled configurable exam schema`
