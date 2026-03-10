# Project Context

Read this file first if you are a new agent or if the original chat history is unavailable.

This document is intended to be a self-contained handoff for the clinic/laboratory app in this repository. A new agent should be able to continue the project from this file plus the codebase, without needing the old conversation.

Companion continuity files:
- [AGENTS.md](C:\Users\acer\Desktop\naic-app\AGENTS.md)
- [DECISIONS.md](C:\Users\acer\Desktop\naic-app\DECISIONS.md)
- [NEXT_STEPS.md](C:\Users\acer\Desktop\naic-app\NEXT_STEPS.md)

## 1. What This App Is

This project is a small-clinic laboratory information system, not just a generic patient record app.

The core business flow is:
- create a lab request for a patient
- choose one or more laboratory exams
- encode exam-specific result values
- save them to the database
- view them later
- eventually print/release them in the clinic's required format

Example used during planning:
- a patient gets `ABG (Blood Gas Analysis)`
- staff encode values like `pH`, `pO2`, `pCO2`
- values are stored and later viewed or printed

That example is only the simplest case. The real system must support multiple exam types with different fields, options, ranges, and layout rules.

## 2. Original Client Reality

The client provided two main sources:
- [NAIC MEDTECH SYSTEM DATA.xlsx](C:\Users\acer\Desktop\naic-app\NAIC%20MEDTECH%20SYSTEM%20DATA.xlsx)
- [Examinations](C:\Users\acer\Desktop\naic-app\Examinations)

Important interpretation:
- the `.xlsx` workbook is the primary source of truth for exam definitions
- the Word print templates inside `Examinations/` are only secondary reference material
- template mismatches should not drive the database design

Reason:
- the workbook is more complete for fields, options, and expected input
- the print templates are outdated and not fully aligned

## 3. Key Product Decision

The original design problem was that exam attributes vary a lot, which makes a fixed table-per-exam database messy.

The approved architectural direction is:
- `fixed clinic core + configurable exam schema`

This means:

Fixed data:
- patients
- lab requests
- request items
- users
- roles
- audit logs
- signatories
- attachments

Configurable data:
- exam definitions
- exam definition versions
- exam options/packages
- exam sections
- exam fields
- field select options
- reference ranges
- rules/conditional logic
- render profiles

Rejected idea:
- do not make the entire system fully dynamic

Reason:
- fully dynamic everything creates avoidable complexity in validation, auditing, reporting, printing, and maintenance

## 4. Why `xlsx-first`

The app design is intentionally based on the workbook first.

That means:
- exam metadata should come from the workbook
- dynamic input behavior should be derived from the workbook
- print behavior will be built later on top of the imported exam metadata

The print templates are not ignored, but they are not authoritative for schema design.

## 5. Hard Problems Already Identified

These were the major design risks discovered during analysis:

1. `Field identity`
- labels repeat across sheets and sections
- examples: `IgM`, `1ST HOUR`, `TEST`, `CONTROL`
- solution: internal stable `field_key`

2. `Versioning`
- published exam definitions must not be edited in place
- old saved results must remain tied to the exact exam version used when they were encoded

3. `Conditional logic`
- some fields/sections are only visible for certain options/packages/sex
- examples: OGTT variants, male/female ranges, COVID attachment requirement

4. `Rendering/printing`
- dynamic exam data needs a separate rendering strategy
- this is not yet fully implemented

5. `Admin safety`
- future admin exam-builder must validate configurations before publish

## 6. Stack Decision

Current stack:
- Python
- Django 5.2
- SQLite
- Django templates
- vanilla HTML/CSS/JS

Why:
- matches the developer's current skill set closely
- Django gives auth/admin/ORM/migrations quickly
- SQLite is acceptable for local single-computer MVP use

Important SQLite note:
- acceptable for local/light use
- not ideal for heavy concurrent multi-user write traffic
- app should remain portable to a server DB later

## 7. Current Repository State

Codebase root:
- [backend](C:\Users\acer\Desktop\naic-app\backend)

Main implemented app modules:
- [accounts](C:\Users\acer\Desktop\naic-app\backend\apps\accounts)
- [common](C:\Users\acer\Desktop\naic-app\backend\apps\common)
- [core](C:\Users\acer\Desktop\naic-app\backend\apps\core)
- [exams](C:\Users\acer\Desktop\naic-app\backend\apps\exams)
- [results](C:\Users\acer\Desktop\naic-app\backend\apps\results)

Current implementation status:
- Django project scaffold exists
- custom user model exists
- fixed clinic core models exist
- configurable exam engine models exist
- result storage models exist
- Django admin registrations exist
- workbook importer exists
- basic request intake UI exists
- request-item creation flow exists
- dynamic result-entry UI exists
- initial print preview/render layer exists

Not yet implemented:
- advanced print layout parity and export flow
- configurable admin exam-builder UI
- master-data importer for physicians/rooms/signatories
- release/approval workflow beyond basic statuses
- reporting/dashboard beyond minimal request listing

## 8. Current Database / Metadata Model

The main model structure is already implemented in Django.

Core models:
- [Patient](C:\Users\acer\Desktop\naic-app\backend\apps\core\models.py)
- [Physician](C:\Users\acer\Desktop\naic-app\backend\apps\core\models.py)
- [Room](C:\Users\acer\Desktop\naic-app\backend\apps\core\models.py)
- [Signatory](C:\Users\acer\Desktop\naic-app\backend\apps\core\models.py)
- [LabRequest](C:\Users\acer\Desktop\naic-app\backend\apps\core\models.py)

Configurable exam models:
- [ExamDefinition](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamDefinitionVersion](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamOption](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamSection](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamField](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamFieldSelectOption](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamFieldReferenceRange](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamRule](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [ExamRenderProfile](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)

Operational result models:
- [LabRequestItem](C:\Users\acer\Desktop\naic-app\backend\apps\results\models.py)
- [LabResultValue](C:\Users\acer\Desktop\naic-app\backend\apps\results\models.py)
- [Attachment](C:\Users\acer\Desktop\naic-app\backend\apps\results\models.py)
- [AuditLog](C:\Users\acer\Desktop\naic-app\backend\apps\results\models.py)

Important implemented constraints:
- one published-or-archived exam version is kept historically per definition version number
- `LabResultValue` is unique per `lab_request_item + field`
- attachments can be tied to a specific exam field

## 9. Workbook Importer

Importer entry point:
- [import_exam_workbook.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\management\commands\import_exam_workbook.py)

Importer service:
- [workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py)

What it currently does:
- reads workbook sheets with `openpyxl`
- maps each sheet to a stable exam code/name/category
- creates or updates `ExamDefinition`
- creates new `ExamDefinitionVersion`
- imports options/packages
- imports sections
- imports fields
- imports select options
- imports reference ranges
- builds a default render profile
- adds a limited safe set of visibility/requirement rules

Important importer behavior:
- source versioning uses an importer signature, not just raw workbook content
- this allows re-importing a new published version when importer logic changes

Current importer signature:
- `IMPORTER_SIGNATURE_VERSION = 5`

Special handling already implemented:
- `SEROLOGY` and `OGTT` unscoped fields are fixed
- `COVID` gets an attachment field for result image
- `BBANK` grouped `VITAL SIGNS` preserves subfield config in `ExamField.config_json`
- `ABG` note fields are imported as display-only notes
- `ABG` gets a dedicated compact print variant
- `BBANK` gets a dedicated crossmatch print variant

## 10. Current Local Data State

As of the last verified state in this repository:
- `16` exam definitions exist
- `16` published exam versions exist
- the current published versions in the local database are `v5` for all imported exams

Published exam codes in local DB:
- `abg:v5`
- `bbank:v5`
- `bcfemale:v5`
- `bcmale:v5`
- `cardiaci:v5`
- `covid-19-antigen-rapid-test:v5`
- `fecalysis:v5`
- `hba1c:v5`
- `hematology:v5`
- `hiv-1-2-testing:v5`
- `microbiology:v5`
- `ogtt:v5`
- `protime-aptt:v5`
- `semen:v5`
- `serology:v5`
- `urine:v5`

Important note:
- these version numbers reflect repeated local imports during development
- on a fresh database, the first import will start at `v1`

## 11. Current User-Facing Flow

Minimal working flow:

1. create lab request
- view: [request_create](C:\Users\acer\Desktop\naic-app\backend\apps\core\views.py)
- template: [request_form.html](C:\Users\acer\Desktop\naic-app\backend\templates\clinic\request_form.html)

2. open request detail
- view: [request_detail](C:\Users\acer\Desktop\naic-app\backend\apps\core\views.py)
- template: [request_detail.html](C:\Users\acer\Desktop\naic-app\backend\templates\clinic\request_detail.html)

3. add exam item
- form: [LabRequestItemCreateForm](C:\Users\acer\Desktop\naic-app\backend\apps\results\forms.py)

4. encode results dynamically
- view: [item_result_entry](C:\Users\acer\Desktop\naic-app\backend\apps\results\views.py)
- service: [results/services.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\services.py)
- template: [result_entry.html](C:\Users\acer\Desktop\naic-app\backend\templates\clinic\result_entry.html)

5. preview printable result output
- view: [item_result_print](C:\Users\acer\Desktop\naic-app\backend\apps\results\views.py)
- service: [rendering.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\rendering.py)
- template: [result_print.html](C:\Users\acer\Desktop\naic-app\backend\templates\clinic\result_print.html)

Supported saved input types in the MVP:
- text
- textarea
- decimal
- integer
- select
- date
- datetime
- boolean
- attachment
- grouped measurement
- display note

## 12. Commands a New Agent Should Know

Activate virtualenv:

```powershell
.venv\Scripts\activate
```

Run server:

```powershell
python backend\manage.py runserver
```

Run checks:

```powershell
python backend\manage.py check
```

Run tests:

```powershell
python backend\manage.py test apps.core apps.results apps.exams
```

Import workbook into exam metadata:

```powershell
python backend\manage.py import_exam_workbook --file "NAIC MEDTECH SYSTEM DATA.xlsx"
```

Useful importer flags:
- `--draft`
- `--keep-published`
- `--force`

Create superuser:

```powershell
python backend\manage.py createsuperuser
```

## 13. Important Design Rules That Should Not Be Broken

1. The workbook is the schema source of truth.
2. Print templates are secondary reference only.
3. Do not convert this into a fixed table-per-exam design.
4. Do not remove exam versioning.
5. Do not edit old published versions in place.
6. Results must stay tied to the exact exam version used for encoding.
7. Dynamic exam data is allowed, but core clinic entities stay fixed.
8. Future print/render work should sit on top of exam metadata, not replace it.

## 14. Recommended Next Steps

Recommended next implementation order:

1. print/render engine refinement
- initial HTML print preview is already implemented
- continue from `ExamRenderProfile`
- improve layout fidelity for real clinic output
- decide whether PDF generation is needed or browser-print is enough

2. master-data import
- physicians
- rooms
- signatories

3. admin exam-builder UI
- create draft exam versions
- add fields/options/sections/rules
- validate before publish

4. release workflow
- medtech/pathologist assignment
- review/release actions
- printed/released timestamps

5. reports/search
- abnormal results
- per-exam daily counts
- patient result history

## 15. Reference Analysis Docs

Detailed planning and analysis docs are here:
- [tmp/analysis](C:\Users\acer\Desktop\naic-app\tmp\analysis)

Most useful ones:
- [client_discovery_brief.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\client_discovery_brief.md)
- [xlsx_first_architecture.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\xlsx_first_architecture.md)
- [xlsx_first_database_design.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\xlsx_first_database_design.md)
- [system_erd.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\system_erd.md)
- [versioning_and_rules_design.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\versioning_and_rules_design.md)
- [admin_exam_builder_flow.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\admin_exam_builder_flow.md)

## 16. Fast Onboarding For a New Agent

If you are a new agent and need to continue quickly:

1. read this file completely
2. read [backend/README.md](C:\Users\acer\Desktop\naic-app\backend\README.md)
3. inspect:
- [backend/apps/exams/services/workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py)
- [backend/apps/exams/models.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [backend/apps/results/services.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\services.py)
- [backend/apps/core/views.py](C:\Users\acer\Desktop\naic-app\backend\apps\core\views.py)
- [backend/apps/results/views.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\views.py)
4. run:

```powershell
.venv\Scripts\activate
python backend\manage.py check
python backend\manage.py test apps.core apps.results apps.exams
```

5. only then continue implementation

This file is intended to replace the need for the lost chat history.
