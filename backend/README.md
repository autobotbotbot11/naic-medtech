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

## Django admin
Create a superuser:

```powershell
.venv\Scripts\activate
python backend\manage.py createsuperuser
```

Open:
- `http://127.0.0.1:8000/admin/`

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
- exam-specific print variants for `ABG` and `BBANK`

Not yet implemented:
- custom admin exam builder UI
- advanced print fidelity / export flow
- reports/dashboard
- master-data importer for physicians, rooms, and signatories
