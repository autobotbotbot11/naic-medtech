# Backend Setup

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

## Current status
Implemented:
- Django project scaffold
- custom user model
- fixed core clinic models
- configurable exam models
- result storage models
- admin registrations
- SQLite pragmas for local development

Not yet implemented:
- workbook importer
- encoder UI
- custom admin exam builder UI
- rendering/print engine
- reports/dashboard
