# Admin Exam Builder Flow

## Goal
Show how the admin can create and maintain configurable exams without making the system too dangerous or too confusing.

This flow is based on the workbook-first architecture.

## Core idea
The admin does not directly edit the database structure.

The admin uses a controlled builder that creates:
- exam families
- exam packages/options
- sections
- fields
- ranges
- dropdown values
- rules
- versions

## Who should have access
Recommended access:
- `super_admin`
- `lab_admin`

Do not allow ordinary encoders to edit exam definitions.

## Main admin screens

### 1. Exam Catalog
Purpose:
- list all exam families

Columns:
- exam code
- exam name
- category
- latest published version
- status
- last updated

Actions:
- create exam
- edit draft
- clone published version
- archive exam
- view version history

### 2. Exam Definition Editor
Purpose:
- create or edit a draft version

Tabs:
- Basic Info
- Packages/Options
- Sections
- Fields
- Ranges
- Rules
- Preview
- Publish

## Recommended creation flow

### Step 1. Basic Info
Fields:
- exam code
- exam name
- category
- description

Rules:
- exam code must be unique
- code should be stable
- changing exam code after publishing should be disallowed

### Step 2. Packages/Options
Used for exams that have multiple requestable variants.

Examples:
- `URINALYSIS`
- `PREGNANCY TEST`
- `50g OGTT`
- `75g OGTT`
- `PROTIME, APTT`

Fields per option:
- option key
- display label
- order
- active/inactive

Rule:
- option key must be unique within the exam version

### Step 3. Sections
Used to group fields in the UI.

Examples:
- `MACROSCOPIC FINDING`
- `CLINICAL FINDING`
- `MICROSCOPIC FINDING`
- `PRO TIME`
- `APTT`

Fields per section:
- section key
- label
- order

Optional:
- only visible for selected option

### Step 4. Fields
This is the main part of the builder.

Per field, the admin sets:
- field key
- field label
- section
- field type
- unit
- required yes/no
- default value
- order
- active yes/no

Controlled field types:
- short text
- long text
- integer
- decimal
- dropdown
- date
- datetime
- yes/no
- attachment
- display note

Rules:
- field key must be unique
- key must not be auto-regenerated after publish
- label can be edited in future versions

## Important UI rule
The builder should display both:
- `field key`
- `field label`

Reason:
- labels like `IgM` or `TEST` repeat across some exams
- the admin needs to understand that internal identity is not the visible label

## Example
Bad:
- field label = `IgM`
- field key = `igm`

Better:
- field label = `IgM`
- field key = `typhidot_igm`

## Step 5. Dropdown Options
This tab only appears when field type is `dropdown`.

Per option:
- value
- label
- order
- active/inactive

Examples:
- `positive`
- `negative`
- `reactive`
- `non_reactive`

## Step 6. Reference Ranges
Used for numeric/manual result fields.

Per range:
- field
- range type
- min value
- max value
- reference text
- sex scope if needed
- option scope if needed
- abnormal flag rule

Examples:
- `less than 200`
- `between 3.5 and 5.3`
- `male only`
- `for 100g OGTT only`

## Step 7. Rules
Use a controlled rule builder, not free-text code.

Allowed rule templates:
- show section when selected option = X
- show field when selected option = X
- require field when selected option = X
- show range set when sex = X
- require attachment when exam = X

Examples:
- show `APTT` section if option is `APTT` or `PROTIME_APTT`
- show `ogtt_100g_3rd_hour` only if option is `100g OGTT`
- require COVID result image if exam is `COVID 19-ANTIGEN TEST`

## Step 8. Preview
The preview page should show:
- selected exam option
- generated form layout
- visible sections
- visible fields
- validation behavior

This is important so the admin can test the draft before publishing.

## Step 9. Publish
Publishing should:
- validate the draft
- freeze the version
- create a new published version
- keep old versions untouched

After publish:
- no direct field deletion/editing on that version
- future changes must create a new version

## Versioning behavior

### Create new draft from published version
Recommended action:
- `Clone Version`

This copies:
- options
- sections
- fields
- ranges
- rules

Then the admin edits the clone and publishes it as a new version.

### Why this matters
Without this:
- old saved results can break
- old print outputs can change unexpectedly
- audits become hard to trust

## Validation checklist before publish

### Basic validation
- exam code exists
- exam name exists
- version is in draft state

### Key validation
- no duplicate option keys
- no duplicate section keys
- no duplicate field keys

### Field validation
- dropdown fields have at least one option
- numeric fields have valid range config if range checking is enabled
- attachment fields are not combined with invalid data types

### Rule validation
- every rule points to an existing field/section/option
- no circular visibility dependency
- no impossible rule combinations

## Suggested user permissions

### `super_admin`
- full access
- publish exam definitions
- archive versions

### `lab_admin`
- create/edit drafts
- manage dropdowns/ranges
- preview
- maybe publish if approved by policy

### `encoder`
- no access to builder
- can only use published exams during result entry

## What the encoder should experience
The encoder should not feel the complexity of the builder.

The encoder flow should simply be:
1. create/select request
2. choose exam option
3. form auto-adjusts
4. encode values
5. save
6. release/print if allowed

That is the benefit of doing the complexity in admin config.

## Practical examples from the workbook

### `OGTT`
Admin creates:
- exam = `OGTT`
- options = `50g`, `75g`, `100g`, `2-hour postprandial`, `50g challenge`
- sections for each package
- fields scoped to those sections/options

### `SEROLOGY`
Admin creates:
- sections = `TYPHIDOT`, `DENGUE TEST`, `MALARIAL TEST`
- fields with scoped keys like `typhidot_igm`, `dengue_igm`

### `BBANK`
Admin creates:
- result fields
- grouped vital sign fields as separate numeric inputs

### `COVID`
Admin creates:
- result dropdown
- attachment requirement rule

## Recommended implementation strategy

### V1 builder
Support:
- create exam
- create options
- create sections
- create fields
- create dropdown options
- create ranges
- create basic visibility rules
- preview
- publish version

### Later builder improvements
Support later:
- more advanced conditional rules
- richer previews
- print profile mapping
- import from workbook automatically

## Final recommendation
Your idea of an admin-created exam builder is correct.

But the builder must be:
- controlled
- versioned
- validated

not:
- unlimited
- direct-to-production
- free-form with no structure
