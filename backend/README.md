# Backend Setup

Read [PROJECT_CONTEXT.md](C:\Users\acer\Desktop\naic-app\PROJECT_CONTEXT.md) first if the original chat history is unavailable.
Then read:
- [AGENTS.md](C:\Users\acer\Desktop\naic-app\AGENTS.md)
- [DECISIONS.md](C:\Users\acer\Desktop\naic-app\DECISIONS.md)
- [NEXT_STEPS.md](C:\Users\acer\Desktop\naic-app\NEXT_STEPS.md)

## Stack
- Django 5.2
- SQLite
- Pillow

## Project structure
- `config/` Django project settings and URLs
- `apps/accounts/` custom user model
- `apps/common/` shared base model, choices, SQLite setup
- `apps/core/` stable clinic entities
- `apps/exams/` configurable exam engine
- `apps/results/` saved results, attachments, audit log

## Local setup

From the repository root:

```powershell
.venv\Scripts\activate
python backend\manage.py runserver
```

Sign in page:
- `http://127.0.0.1:8000/login/`

## Django admin
Create a superuser:

```powershell
.venv\Scripts\activate
python backend\manage.py createsuperuser
```

Open:
- `http://127.0.0.1:8000/admin/`

Notes:
- `createsuperuser` is the bootstrap `system_owner`
- public self-registration is intentionally not implemented
- day-to-day user management should use the custom in-app admin portal, not Django admin

Custom admin portal:
- `http://127.0.0.1:8000/manage/`
- intended for daily company administration
- includes guided setup checklist, searchable/filterable lists, and temporary-password helper tools

## Workbook importer
Import the clinic workbook into configurable exam metadata:

```powershell
.venv\Scripts\activate
python backend\manage.py import_exam_workbook --file "NAIC MEDTECH SYSTEM DATA.xlsx"
```

Useful flags:
- `--draft` creates draft exam versions instead of published ones.
- `--keep-published` leaves older published versions untouched.
- `--force` creates a new version even when the workbook source matches the latest published version.

## Current status
Implemented:
- Django project scaffold
- custom user model
- custom login/logout flow
- forced password-change flow
- authenticated protection on operational pages
- custom admin portal for users and core master data
- admin-portal polish for non-tech staff:
- guided setup checklist
- searchable/filterable management lists
- temporary-password helpers for onboarding/reset flows
- clearer empty states and current-file previews
- fixed core clinic models
- organization/facility branding models with request snapshots
- configurable exam models
- result storage models
- admin registrations
- SQLite pragmas for local development
- workbook importer for the provided `.xlsx`
- basic request intake UI
- request-item creation flow
- dynamic exam-option loading for request-item packages/options
- dynamic result entry UI based on imported exam metadata
- medtech/pathologist selection in result entry
- initial HTML print preview for saved results
- facility-branded print header
- exam-specific print variants for `ABG`, `BBANK`, `SEROLOGY`, `OGTT`, `HEMATOLOGY`, and `PROTIME/APTT`
- microscopy-focused print variant for `URINE` and `FECALYSIS`
- dedicated analysis print variant for `SEMEN`
- single-result focus print variant for `MICROBIOLOGY`
- focused marker-card print variant for `CARDIACI`
- chemistry-panel print variant for `BCMALE` and `BCFEMALE`
- browser validation completed for `SEROLOGY`, `OGTT`, `HEMATOLOGY`, `URINE`, `FECALYSIS`, `PROTIME/APTT`, `SEMEN`, `MICROBIOLOGY`, `CARDIACI`, `BCMALE`, and `BCFEMALE` in both screen preview and print-media mode
- workbook recalibration audit identifying source-data and importer-hardening issues
- importer hardening completed:
- header-aware note/reference mapping
- blank-row-safe source hashing
- workbook re-imported to latest published `v11` versions

Not yet implemented:
- custom admin exam builder UI
- advanced print parity for the remaining exams and any future export flow
- reports/dashboard
- master-data importer for physicians, rooms, and signatories

Important current work item:
- review [workbook_recalibration_audit.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\workbook_recalibration_audit.md) before modifying importer behavior or trusting workbook values blindly
- use [clinic_confirmation_queue.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\clinic_confirmation_queue.md) for the remaining clinic-confirmation items that should not be guessed by the developer
