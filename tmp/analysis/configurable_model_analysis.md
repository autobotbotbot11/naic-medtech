# Configurable Exam Model - Conflict Analysis

## Short answer
Yes, a configurable exam/data model can solve the biggest database-rigidity problem.

But it does **not** eliminate all conflicts.

It only works cleanly if the system is designed as:
- fixed core entities
- configurable exam schema
- configurable validation/rules
- configurable print mapping
- versioned exam definitions

If you only make the fields dynamic without rules, print mapping, and versioning, the project will become more confusing, not less.

## Main conclusion
Your idea is valid.

The correct question is not:
- "Can we make the database customizable?"

The correct question is:
- "Can we build a controlled exam-definition engine that is flexible enough for these lab forms?"

My answer after re-checking the workbook and templates is:
- `Yes, workable`
- but only with guardrails
- and some conflicts will still remain outside the data model

## What the configurable approach really solves

### 1. It solves rigid per-exam database tables
If we create one fixed SQL table per exam, every new exam or field change will require:
- schema changes
- code changes
- UI changes
- print changes

A configurable exam model avoids that.

This is useful because the current source files already show:
- `16` different exam sheets
- `62` distinct exam options
- `149` mapped test fields
- different field types across exams
- likely future additions

### 2. It solves frequent field-level changes
The workbook already suggests that values may change:
- editable normal values were requested in `BCMALE`
- some exams use dropdowns
- some exams use numeric/manual entry
- some have notes and special behavior

A configurable model allows:
- add field
- rename field
- change unit
- change normal range
- change dropdown options
- change display order

without database redesign.

### 3. It helps with male/female or package-based variations
Several exams are not just "one form = one set of fields."

Examples:
- `BCMALE` vs `BCFEMALE`
- `HEMATOLOGY` packages like `CBC, PLATELET COUNT, ESR`
- `OGTT` options like `50g`, `75g`, `100g`, `2-hour postprandial`
- `PROTIME, APTT` with one or both sections active

This means the app must support:
- variant-specific fields
- conditional visibility
- section-based grouping
- possibly template variants

That is easier in a configurable system than in a rigid table-per-exam design.

## What the configurable approach does NOT solve

### 1. It does not solve source-of-truth conflicts
If the workbook says one thing and the print template says another, dynamic fields do not magically tell us which is correct.

Examples already found:
- `SEROLOGY`: workbook has `ANTI-HCV`, template has `TROPONIN I`
- `OGTT`: workbook and template disagree on fasting normal range
- `CARDIACI`: workbook and template disagree on Troponin-I normal range
- `BCMALE` / `BCFEMALE`: workbook and template disagree on several normal values

This is not a database problem.
This is a requirements / source-validation problem.

### 2. It does not solve missing print templates
`HIV` and `COVID` have input definitions in the workbook, but no clear final print template was identified.

Even if the data model is perfect, printing is still blocked until the client confirms:
- actual layout
- required wording
- whether image attachment is needed

### 3. It does not solve ambiguous print placeholders
Some templates are not clean structured tokens.

Examples:
- `MICROBIOLOGY.dotx` uses generic `O`
- `URINE`, `FECALYSIS`, `HEMATOLOGY`, `COAG` mix labels and placeholders in a way that requires context

So the print engine still needs:
- explicit token mapping
- per-template rules
- exceptions for odd templates

### 4. It does not solve bad admin input by itself
If the admin can create anything with no constraints, they can create:
- duplicate fields
- wrong units
- broken normal ranges
- invalid dropdowns
- fields not mapped to print output
- rules that make history inconsistent

So the admin builder must be controlled, not fully free-form.

## New conflicts introduced by a dynamic system

### 1. Historical results can break after config changes
Example:
- today, exam `ABG` has fields `pH`, `pO2`, `pCO2`
- next month, admin renames or deletes a field

Question:
- what happens to old results already saved?

Required answer:
- exam definitions must be versioned

Without versioning:
- old results become unreadable
- print history changes retroactively
- audit trail becomes unreliable

### 2. Reporting becomes harder if fields are too free-form
If admins create fields with inconsistent labels like:
- `pO2`
- `PO2`
- `PaO2`

then reports and searches become messy.

Required answer:
- internal stable field keys
- display labels can change, keys should not

### 3. Repeated labels require scoped identifiers
Some sheets reuse the same visible label multiple times.

Examples:
- `OGTT`: `1ST HOUR`, `2ND HOUR` appear in multiple sections
- `PROTIME, APTT`: `TEST` and `CONTROL` appear for both protime and APTT
- `SEROLOGY`: `IgM` and `IgG` appear under different groups

So a field cannot be identified only by visible label.

You need internal keys like:
- `ogtt_50g_1st_hour`
- `ogtt_75g_1st_hour`
- `protime_test`
- `aptt_test`
- `typhidot_igm`
- `dengue_igm`

### 4. Conditional logic becomes unavoidable
The current files already imply condition-based forms.

Examples:
- show only relevant fields for selected exam package
- choose male/female range or layout
- mark abnormal values red
- show image upload for COVID

This means the builder must support rules such as:
- show field if exam option = X
- use range set A if sex = male
- require attachment if exam type = COVID antigen

If the builder does not support conditions, the dynamic model will still fail.

### 5. Printing can break independently from data entry
A dynamic input form may still store correct data while the print layout is wrong.

Why:
- print layout depends on exact token mapping and ordering
- templates use different conventions
- some templates have generic `other` areas

So "dynamic data entry" and "dynamic printing" are related but not the same feature.

## Re-check of the current files under the configurable-model lens

### A. Data-entry side
The source files strongly support a configurable data-entry engine.

Why:
- many exams are just lists of fields
- field types are mostly predictable
- field metadata already exists in the workbook
- many values are dropdown-driven
- many fields carry normal ranges

So for encoding results, dynamic exam definitions are a good fit.

### B. Print side
The source files only partially support a generic print engine.

Why:
- some templates map cleanly to fields
- some templates are inconsistent
- some templates are missing for workbook exams
- some templates exist without workbook sheets

So printing cannot be "fully generic" on day 1 without risk.

### C. Master data side
The source files support configurable master data, but these should remain separate from exam definitions.

Examples:
- physicians
- rooms
- signatories
- normal ranges

These should be editable, but not mixed into the free-form field builder.

## Minimum metadata the system must support
If you want the configurable approach to actually work, every exam field needs more than just a label.

At minimum each field definition should have:
- internal key
- display label
- section/group
- input type
- unit
- normal range or reference range set
- dropdown options
- required/not required
- sort order
- visibility condition
- print token mapping
- abnormal-highlighting rule
- active/inactive flag
- version id

And each exam definition should have:
- exam code
- exam name
- category
- available request options/packages
- template assignment
- template variant rules
- status
- version

## What should stay fixed
These should **not** be free-form dynamic fields:
- patient identity model
- lab request / case number model
- users / roles / permissions
- audit logs
- release status
- print/release lifecycle
- attachments storage
- physician/room/signatory entities

Reason:
- these are core application entities
- they are used across all exams
- they affect security, reporting, and history

## What should be configurable
These are strong candidates for configuration:
- exam definitions
- exam packages/options
- exam sections
- result fields
- dropdown options
- normal ranges
- abnormal flags
- print token mappings
- exam-template assignment
- attachment requirements

## What should be semi-configurable, not fully free-form
These need admin control with restrictions:
- template editing
- condition rules
- computed values
- release rules
- exam version publishing

Reason:
- these have system-wide impact
- one wrong change can break history or printing

## Safer design decision
Do not build:
- "an admin can invent any structure with no rules"

Build:
- "an admin can define exam schemas within a controlled builder"

Meaning:
- predefined field types
- predefined rule types
- predefined template token mapping workflow
- publish/version process
- validation before an exam config goes live

## Practical verdict for your project

### If you make exam data configurable with guardrails
Result:
- `good direction`
- less database pain
- easier long-term maintenance
- better fit for this clinic's exam diversity

### If you make everything fully dynamic
Result:
- `high risk`
- harder validation
- harder reporting
- harder printing
- more bugs from admin misconfiguration

## Final answer
Yes, the configurable idea still works after re-analysis.

But the correct architecture is not:
- "fully customizable database"

It is:
- "fixed clinic/LIS core + configurable exam-definition engine"

That design removes most of the database rigidity while still respecting the real conflicts that remain:
- source mismatches
- missing templates
- print mapping issues
- versioning
- conditional logic
