# AGENTS.md

Read this file if you are a new agent working in this repository.

This project already has substantial planning and implementation history. Do not start by redesigning the system from scratch.

## First Read Order

1. [PROJECT_CONTEXT.md](C:\Users\acer\Desktop\naic-app\PROJECT_CONTEXT.md)
2. [DECISIONS.md](C:\Users\acer\Desktop\naic-app\DECISIONS.md)
3. [NEXT_STEPS.md](C:\Users\acer\Desktop\naic-app\NEXT_STEPS.md)
4. [backend/README.md](C:\Users\acer\Desktop\naic-app\backend\README.md)

Then inspect these implementation files:
- [backend/apps/core/models.py](C:\Users\acer\Desktop\naic-app\backend\apps\core\models.py)
- [backend/apps/exams/services/workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py)
- [backend/apps/exams/models.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [backend/apps/results/services.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\services.py)
- [backend/apps/core/views.py](C:\Users\acer\Desktop\naic-app\backend\apps\core\views.py)
- [backend/apps/results/views.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\views.py)

## What This App Is

This is a small-clinic laboratory information system.

It is not just:
- a generic patient CRUD app
- a static print-form encoder
- a fixed table-per-exam database

The real system shape is:
- fixed clinic core
- configurable exam-definition engine
- versioned exam metadata
- dynamic result-entry
- future print/release layer on top of saved results

## Source of Truth

Primary source:
- [NAIC MEDTECH SYSTEM DATA.xlsx](C:\Users\acer\Desktop\naic-app\NAIC%20MEDTECH%20SYSTEM%20DATA.xlsx)

Secondary reference only:
- [Examinations](C:\Users\acer\Desktop\naic-app\Examinations)

Do not let the old print templates drive schema decisions.

## Non-Negotiable Architecture Rules

1. The workbook is the schema source of truth.
2. Exam definitions are configurable, but core clinic entities remain fixed.
3. Published exam versions must not be edited in place.
4. Saved results must remain tied to the exact exam version used during encoding.
5. Do not switch to table-per-exam storage.
6. Future print logic must consume exam metadata, not replace it.
7. Workbook notes are internal-only and must not be rendered as patient-facing fields.

## Current Stack

- Django 5.2
- SQLite
- Django templates
- vanilla HTML/CSS/JS

## Current Working State

Already implemented:
- Django project scaffold
- core clinic models
- organization + facility branding models with request snapshots
- configurable exam models
- result models
- workbook importer
- request intake UI
- request-item creation flow
- dynamic exam-option loading in the add-item form
- dynamic result-entry flow
- medtech/pathologist selection in result-entry
- initial print-preview flow
- facility-branded print header
- ABG compact print variant
- BBANK crossmatch print variant

Not yet implemented:
- advanced print fidelity / export flow
- admin exam-builder UI
- master-data importer
- full release workflow
- reports/search

## Required Sanity Checks Before Continuing

From repo root:

```powershell
.venv\Scripts\activate
python backend\manage.py check
python backend\manage.py test apps.core apps.results apps.exams
```

If you are changing exam-import behavior, also run:

```powershell
python backend\manage.py import_exam_workbook --file "NAIC MEDTECH SYSTEM DATA.xlsx"
```

## If You Change the Architecture or Workflow

Update these files in the same turn:
- [PROJECT_CONTEXT.md](C:\Users\acer\Desktop\naic-app\PROJECT_CONTEXT.md)
- [DECISIONS.md](C:\Users\acer\Desktop\naic-app\DECISIONS.md)
- [NEXT_STEPS.md](C:\Users\acer\Desktop\naic-app\NEXT_STEPS.md)

If you do not update the handoff docs, the continuity problem returns.
