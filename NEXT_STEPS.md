# Next Steps

This file is the working queue for future implementation.

Priority is ordered. Unless the user explicitly redirects, continue from the top.

## 1. Print / Render Engine Refinement

Goal:
- render saved request-item results into printable clinic reports

Why this is next:
- an initial HTML print-preview layer now exists
- the next work is improving fidelity and coverage for real clinic use
- `ABG` and `BBANK` custom variants are already implemented
- the next refinement targets should extend that pattern only where needed

Starting points:
- [backend/apps/exams/models.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\models.py)
- [backend/apps/results/models.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\models.py)
- [backend/apps/results/services.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\services.py)
- [backend/apps/results/rendering.py](C:\Users\acer\Desktop\naic-app\backend\apps\results\rendering.py)

Implementation targets:
- consume `ExamRenderProfile`
- support:
- label-value list
- sectioned report
- result table
- grouped measurement rendering
- include:
- patient/request header
- exam title and option
- units
- reference ranges
- abnormal highlighting
- attachment-aware handling where needed
- improve clinic-specific print fidelity for real imported exams
- next likely candidates:
- `SEROLOGY`
- `OGTT`
- `HEMATOLOGY`
- decide whether browser print is sufficient or PDF export is required

Acceptance criteria:
- at least one real imported exam can be rendered end-to-end
- result output is based on saved metadata and saved result values

## 2. Master Data Import

Goal:
- populate physicians, rooms, and signatories from known source data

Why:
- request intake and release workflow need real master data

Targets:
- physicians
- rooms
- signatories

Acceptance criteria:
- admin does not need to create all common master data manually

## 3. Admin Exam Builder

Goal:
- allow controlled creation/editing of exam definitions inside the app

Requirements:
- draft version creation
- sections
- fields
- options
- select options
- reference ranges
- rules
- publish validation

Do not build:
- unrestricted free-form scripting
- drag-anywhere page designer as the first version

Acceptance criteria:
- admin can create a new draft exam version and publish it safely

## 4. Review / Release Workflow

Goal:
- move from plain encoding into clinic-ready result release

Requirements:
- medtech signatory selection
- pathologist signatory selection where applicable
- review/release actions
- released timestamps
- printed timestamps

Acceptance criteria:
- request items can move through a controlled status flow

## 5. Search / Reporting

Goal:
- basic operational visibility

Likely first reports:
- request list with filters
- patient result history
- abnormal-result listing
- exam counts by date

Acceptance criteria:
- clinic staff can find prior results without browsing raw admin pages

## Operational Rule

If any major direction changes while implementing the above:
- update [PROJECT_CONTEXT.md](C:\Users\acer\Desktop\naic-app\PROJECT_CONTEXT.md)
- update [DECISIONS.md](C:\Users\acer\Desktop\naic-app\DECISIONS.md)
- update this file
