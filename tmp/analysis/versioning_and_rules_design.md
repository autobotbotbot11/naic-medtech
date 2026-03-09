# Versioning and Rules Design

## Goal
Define how the system stays safe when:
- admins change exam definitions
- exams have package-based fields
- fields have sex-specific behavior
- some exams need special requirements like attachments

This document focuses on two hard problems:
- versioning
- conditional logic

## Part 1. Versioning

## Why versioning is mandatory
In a configurable exam system, configuration changes are not small cosmetic edits.
They can change:
- field keys
- field labels
- ranges
- dropdown options
- visibility
- rendering behavior

If the system edits a live schema in place, old records become unsafe.

So the rule must be:
- published exam definitions are immutable

## Versioning model

### Entity flow
- `exam_definition`
- `exam_definition_version`
- `lab_request_item`
- `lab_result_value`

### Meaning
- `exam_definition` = stable exam family like `OGTT`
- `exam_definition_version` = exact published structure of that exam at a point in time
- `lab_request_item` = one performed exam for a patient/request
- `lab_result_value` = saved values based on fields from that exact version

## Lifecycle

### 1. Create exam family
Example:
- `OGTT`

This creates:
- one `exam_definition`

### 2. Create draft version
Admin edits:
- options
- sections
- fields
- ranges
- rules
- rendering profile

This stays in:
- `draft`

### 3. Publish version
After validation:
- system marks version as `published`
- version becomes read-only

Example:
- `OGTT v1`

### 4. Use version in live requests
When a new lab request item is created:
- it links to `OGTT v1`

### 5. Future change
If admin later modifies OGTT:
- do not edit `v1`
- create `v2 draft`
- publish `v2`

Old requests remain linked to `v1`.
New requests use `v2`.

## Rules of historical safety

### Rule 1
Never edit a published version directly.

### Rule 2
Every saved exam result must reference:
- `exam_definition_id`
- `exam_definition_version_id`

### Rule 3
Result rows should store snapshots of:
- field key
- field label
- unit
- reference text
- sort order

### Rule 4
Rendering/print profile must also be version-aware.

Reason:
- the old result should render according to the old published exam structure

## Safe change examples

### Safe
- create `ABG v2`
- add `base_excess_note`
- publish
- future requests use `v2`

### Unsafe
- directly rename a field in `ABG v1`
- old results now point to something that no longer matches

## What should trigger a new version
Any change to these should create a new version:
- exam option list
- section list
- field keys
- field labels
- input type
- unit
- dropdown options
- reference ranges
- rules
- rendering/print profile

## What may not require a new version
Usually master data edits such as:
- physician list
- room list
- user list
- signatory availability

But if a signatory is embedded in old released results, snapshotting still helps.

## Version states
Recommended states:
- `draft`
- `published`
- `archived`

### `draft`
- editable
- not usable for result entry

### `published`
- read-only
- usable for result entry

### `archived`
- not used for new requests
- still used for historical viewing

## Versioning summary
The core safety rule is:

`results must belong to an immutable exam-definition version`

That is the foundation of the whole system.

## Part 2. Conditional Logic

## Why a rule system is needed
The workbook already shows that many exams are conditional.

Examples:
- `OGTT`: fields depend on selected package
- `PROTIME, APTT`: sections depend on selected option
- `HEMATOLOGY`: some ranges depend on sex
- `COVID`: may require image attachment

So fields cannot all be blindly shown all the time.

## Do not use a free-form formula engine in v1
That would be too risky and too hard to maintain.

Instead, use a controlled rule system with predefined rule types.

## Recommended rule categories

### 1. Visibility rules
Control whether a section or field should appear.

Examples:
- show `ogtt_100g_section` if selected option = `ogtt_100g`
- show `aptt_section` if option = `aptt` or `protime_aptt`

### 2. Requirement rules
Control whether a field becomes required.

Examples:
- require `covid_result_image` if exam = `covid_antigen`
- require `lot_number` if exam = `hiv_testing`

### 3. Range-selection rules
Choose which reference range applies.

Examples:
- use male range if sex = `male`
- use female range if sex = `female`
- use option-specific range for `ogtt_50g`

### 4. Abnormal-flag rules
Decide whether a value is normal or abnormal.

Examples:
- abnormal if result > max
- abnormal if result < min
- abnormal if result not in allowed values

## Recommended condition model
Keep conditions declarative.

Examples of condition inputs:
- selected exam option
- patient sex
- field value

Avoid arbitrary scripting in v1.

## Practical rule structure
Each rule can be thought of as:

- `target`
- `when`
- `effect`

Example:
- target: field `ogtt_100g_3rd_hour`
- when: selected option = `ogtt_100g`
- effect: visible = true

Another example:
- target: field `covid_result_image`
- when: exam code = `covid_antigen`
- effect: required = true

## Suggested rule types for MVP

### Visibility
- `show_if_option_in`
- `show_if_sex_is`

### Requirement
- `require_if_option_in`
- `require_if_exam_code_is`

### Range
- `use_range_if_sex_is`
- `use_range_if_option_is`

### Validation
- `numeric_min_max`
- `allowed_select_values`

## Example workbook mappings

## `OGTT`
Rules:
- show only `50g` fields if option is `50g OGTT`
- show only `75g` fields if option is `75g OGTT`
- show only `100g` fields if option is `100g OGTT`

## `PROTIME, APTT`
Rules:
- show `protime_section` if option is `PROTIME` or `PROTIME_APTT`
- show `aptt_section` if option is `APTT` or `PROTIME_APTT`

## `HEMATOLOGY`
Rules:
- if field is sex-specific, choose reference range by patient sex

## `COVID`
Rules:
- require image attachment when saving released result

## Rule engine boundaries
The rule engine should affect:
- what fields are shown
- what fields are required
- what ranges are used
- how abnormal flags are computed

The rule engine should not affect in v1:
- arbitrary calculations
- custom scripts
- unrestricted cross-field programming

## Admin safety recommendations

### Before publish, validate:
- all rules point to real fields/sections/options
- no duplicate targets with contradictory effects
- no impossible conditions
- no section hidden while required child fields remain active

### In the builder UI:
- let admin choose from controlled dropdown conditions
- do not expose raw JSON editing in normal UI

## MVP-safe implementation

### Must support in MVP
- immutable published versions
- field snapshots in saved results
- option-based visibility
- sex-based range selection
- attachment requirement flag
- abnormal flag evaluation

### Can wait until later
- highly advanced rule combinations
- formula language
- user-authored scripting

## Final conclusion
If rendering is handled, the real architectural backbone becomes:
- immutable versioning
- controlled conditional rules

If these two are done properly, the configurable exam system remains stable even as the clinic changes exam definitions over time.
