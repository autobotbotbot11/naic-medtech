# Backend Setup

Read [PROJECT_CONTEXT.md](C:\Users\acer\Desktop\naic-app\PROJECT_CONTEXT.md) first if the original chat history is unavailable.

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
- configurable exam models
- result storage models
- admin registrations
- SQLite pragmas for local development
- workbook importer for the provided `.xlsx`
- basic request intake UI
- request-item creation flow
- dynamic result entry UI based on imported exam metadata

Not yet implemented:
- custom admin exam builder UI
- rendering/print engine
- reports/dashboard
- master-data importer for physicians, rooms, and signatories
