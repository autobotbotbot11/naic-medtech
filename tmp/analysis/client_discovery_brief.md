# NAIC Medtech System - Client Discovery Brief

## Sources reviewed
- `NAIC MEDTECH SYSTEM DATA.xlsx`
- `Examinations/*.dotx`
- Existing intermediate analysis in `tmp/analysis/`

## What the client is actually asking for
This is not just a patient masterlist app. The client is effectively asking for a small Laboratory Information System (LIS) for a clinic / hospital lab workflow:

1. Search or encode a patient / request.
2. Select one or more lab examinations or exam packages.
3. Encode result values using exam-specific fields.
4. Store the results in a database.
5. View previous results.
6. Print a formal result form that matches the current clinic format.
7. Include the proper signatories on the printed output.

The center of the system is not only `Patient`. The real center is a `Lab Request / Encounter` with:
- patient snapshot
- request metadata
- selected examinations
- result values
- signatories
- printable release form

## What is already clear from the files
- Input workbook sheets: `16`
- Print templates: `18`
- Shared physician master list: `29`
- Shared room master list: `21`
- Medtech signatories found: `6`
- Pathologist found: `1`

Shared patient/request fields appear on almost all exam sheets:
- Name
- Age
- Sex
- Date or Date/Time
- Examination
- Requesting Physician
- Room
- Case Number

Shared release/signatory fields:
- Medical Technologist
- Pathologist

## Inferred workflow
The current paper / Excel process appears to be:

1. Staff receives a request for a patient.
2. Staff selects the correct exam or exam package.
3. Staff enters result values based on the exam sheet.
4. Staff chooses the medtech signatory.
5. The system prints a lab result form that matches the current template.
6. The result is later searchable and re-printable.

What this implies for the software:
- patient history is needed
- request history is needed
- print fidelity matters
- exam definitions are not uniform and must be configurable
- some rules depend on sex, age, or selected exam package

## Exam coverage snapshot

| Workbook sheet | Example exam option(s) | Result entry style | Best print template match | Notes |
| --- | --- | --- | --- | --- |
| URINE- Clinical Microscopy | URINALYSIS, PREGNANCY TEST | Mostly dropdown + some manual | `URINE.dotx` | Good overall match |
| SEROLOGY | DENGUE TEST, ASO TITER, VDRL | Mostly dropdown | `SEROLOGY.dotx` | Contains a structural mismatch |
| SEMEN - Clinical Microscopy | SEMEN ANALYSIS | Mostly manual | `SEMEN.dotx` | Good overall match |
| OGTT - Blood Chemistry | 50g OGTT, 75g OGTT, 100g OGTT | Manual numeric | `OGTT.dotx` | Normal value mismatch found |
| MICROBIOLOGY | KOH SMEAR | Dropdown result | `MICROBIOLOGY.dotx` | Template uses generic placeholder only |
| HEMATOLOGY | CBC, PLATELET COUNT, ESR | Manual numeric | `HEMATOLOGY.dotx` | Package logic is important |
| HBA1C - Blood Chemistry | HBA1C (CLOVER) | Single manual result | `HBA1C.dotx` | Good overall match |
| FECALYSIS - Clinical Microscopy | FECALYSIS, FOBT | Mixed dropdown/manual | `FECALYSIS.dotx` | Good overall match |
| CARDIACI - Serology | CK-MB, TNI, BNP | Manual numeric | `CARDIACI.dotx` | Troponin normal value mismatch found |
| BCMALE - Blood Chemistry | CHEM 6, LIPID PROFILE | Manual numeric | `BCMALE.dotx` | Male normal values do not fully match workbook |
| BCFEMALE - Blood Chemistry | CHEM 6, LIPID PROFILE | Manual numeric | `BCFEMALE.dotx` | Female normal values do not fully match workbook |
| BBANK - Blood Bank | CROSSMATCHING | Mixed manual/dropdown | `BBANK.dotx` | Vital signs need structured input |
| ABG - Blood Gas Analysis | ABG | Manual numeric | `ABG.dotx` | Good overall match |
| HIV 1&2 TESTING - Serology | HIV TESTING | Manual lot no + dropdown result | No clear matching template found | Needs client confirmation |
| COVID 19 ANTIGEN (RAPID TEST) - | COVID 19-ANTIGEN TEST | Dropdown result | No clear matching template found | Note says result needs picture |
| PROTIME, APTT - Hematology | PROTIME, APTT | Manual numeric | `COAG.dotx` | Good overall match |

## Templates that are extra or unclear
These print templates exist but do not have a clear input sheet match in the workbook:
- `CARDIAC.dotx`
- `HSCRP.dotx`
- `HBA1CI.dotx`

These workbook sheets exist but do not have a clear print template match:
- `HIV 1&2 TESTING - Serology`
- `COVID 19 ANTIGEN (RAPID TEST) -`

This means the source files are not fully aligned yet. We should not assume the workbook is complete or the template folder is complete.

## Important business rules found in the workbook
- Many exams have fixed dropdown values, not free text.
- Many chemistry / hematology exams contain normal ranges.
- Several sheets contain the rule: `all results above or below normal value make it red`.
- `BCMALE` contains a note asking whether normal values should be editable.
- `BBANK` contains a note asking for structured vital-sign inputs instead of one plain text field.
- `COVID 19 ANTIGEN (RAPID TEST)` contains a note saying the printed result should include a picture.
- Some forms have sex-specific normal ranges.
- Some sheets represent exam packages, not single tests.

## What the system will likely need

### Core modules
- Patient registry
- Lab request / encounter management
- Exam selection
- Exam-specific result entry
- Result viewing / history
- Printing / print preview
- Master data management
- User roles and permissions
- Audit trail

### Master data
- Physicians
- Rooms
- Exam types
- Exam packages
- Field definitions per exam
- Dropdown options per field
- Normal ranges per field
- Signatories
- Print template mappings

### Recommended data model direction
Do not create one rigid database table per exam form. That will become hard to maintain.

Use a hybrid model instead:
- `patients`
- `lab_requests`
- `lab_request_items`
- `exam_types`
- `exam_fields`
- `exam_field_options`
- `exam_templates`
- `result_values`
- `signatories`
- `attachments`
- `users`
- `audit_logs`

Practical meaning:
- common patient/request data stays relational
- exam definitions stay configurable
- result values are stored per field, not hardcoded per form
- print output can be generated from template mappings

## Problems and inconsistencies found in the provided files

### 1. Workbook and print templates are not fully aligned
- Input sheets: `16`
- Templates: `18`
- At least `2` workbook sheets have no clear template.
- At least `3` templates have no clear workbook sheet.

### 2. `SEROLOGY` workbook vs `SEROLOGY.dotx`
Workbook sheet contains:
- DENGUE TEST
- ASO TITER
- TYHPIDOT
- HBSAG SCREENING
- VDRL
- ANTI-HCV

But `SEROLOGY.dotx` contains placeholders for:
- Typhidot
- Dengue
- HbsAg
- VDRL
- Malarial test
- ASO Titer
- `TROPONIN I`

Observation:
- `ANTI-HCV` exists in workbook but is not clearly present in the template.
- `TROPONIN I` exists in template but is not in the workbook sheet.

This is likely a real source inconsistency, not an implementation issue.

### 3. `OGTT` workbook vs `OGTT.dotx`
Workbook fasting blood sugar normal value:
- `70.27-124.32 mg/dl`

Template fasting blood sugar normal value:
- `70 - 105 mg/dl`

This needs client confirmation before hardcoding any validation or print logic.

### 4. `CARDIACI` workbook vs `CARDIACI.dotx`
Workbook Troponin-I normal value:
- `0.0 - 0.02 ng /mL`

Template Troponin-I normal value:
- `0.0 - 0.01 ng /mL`

This is another real discrepancy.

### 5. `BCMALE` and `BCFEMALE` workbook vs templates
The workbook values do not cleanly match the male/female print templates in several fields such as:
- creatinine
- HDL cholesterol
- SGOT / SGPT

This suggests one of the following:
- workbook was updated but templates were not
- templates were updated but workbook was not
- one of the two is simply incorrect

### 6. `MICROBIOLOGY` template is printable but not strongly structured
`MICROBIOLOGY.dotx` uses a generic `O` placeholder for the result area instead of a named `R1` style field.

Implication:
- still implementable
- but the template mapping will need a special case

### 7. HIV and COVID output format is still unclear
The workbook has input definitions for HIV and COVID, but the current template folder does not show an obvious matching print layout.

Implication:
- we can build the data-entry side
- but print/output requirements are still incomplete

## What the client probably expects at company level
Even if they did not list everything yet, a company-level clinic system usually expects:
- secure login
- separate staff roles
- search by patient / case number / date
- edit history
- reprint history
- draft vs released result status
- reliable formatting during printing
- future addition of new exam types without major rework

## Best implementation direction
The safest approach is:

1. Build the system around configurable `exam definitions`.
2. Treat the current workbook as a first-pass source of field metadata.
3. Treat the current templates as first-pass print layouts.
4. Create a validation pass with the client to resolve mismatches before coding every print form.

## Immediate next deliverables we can produce from here
- a clean system scope document
- a normalized exam catalog
- an initial database design
- a screen / workflow plan
- a client question checklist for requirement validation
