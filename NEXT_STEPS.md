# Next Steps

This file is the working queue for future implementation.

Priority is ordered. Unless the user explicitly redirects, continue from the top.

Recently completed:
- admin portal polish baseline
- guided setup checklist on the admin home page
- searchable/filterable user and master-data lists
- temporary-password helper tools for onboarding/reset pages
- clearer empty states, help text, and current-file previews
- workbook recalibration audit completed
- importer hardening completed
- clinic confirmation queue documented
- workbook re-imported under hardened importer
- exam-specific print variants completed for `SEROLOGY` and `OGTT`
- browser validation completed for `SEROLOGY` and `OGTT` in both screen preview and print-media mode
- exam-specific print refinement completed for `HEMATOLOGY`, `URINE`, and `FECALYSIS`
- browser validation completed for `HEMATOLOGY`, `URINE`, and `FECALYSIS` in both screen preview and print-media mode

## 1. Print / Render Engine Refinement

Goal:
- render saved request-item results into printable clinic reports

Why this is next:
- an initial HTML print-preview layer now exists
- organization/facility branding headers are now in the print flow
- the next work is improving fidelity and coverage for real clinic use
- `ABG`, `BBANK`, `SEROLOGY`, `OGTT`, `HEMATOLOGY`, `URINE`, and `FECALYSIS` custom variants are already implemented
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
- `PROTIME/APTT`
- `SEMEN`
- `MICROBIOLOGY`
- verify browser print-to-PDF keeps the same compact layout as on-screen preview
- decide whether browser print is sufficient or PDF export is required

Acceptance criteria:
- multiple real imported exams can be rendered end-to-end
- result output is based on saved metadata and saved result values

## 2. Clinic Confirmation Pass For Suspicious Source Items

Goal:
- keep a clean boundary between technical assumptions and clinic-confirmed truth

Why:
- importer hardening is now in place
- some workbook items are still intentionally unresolved because they require clinic/lab confirmation, not developer guessing

Starting points:
- [workbook_recalibration_audit.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\workbook_recalibration_audit.md)
- [clinic_confirmation_queue.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\clinic_confirmation_queue.md)

Targets:
- suspicious glucose ranges
- spelling/label confirmation such as `Typhidot`
- unresolved signatory-name note in `FECALYSIS`
- package meaning confirmation for combined exam options

Acceptance criteria:
- the project has a clear clinic-facing queue of items that must be confirmed instead of guessed

## 3. Master Data Import

Goal:
- populate physicians, rooms, and signatories from known source data

Why:
- request intake and release workflow need real master data
- organization/facility branding is now admin-manageable, but the rest of the master data is still mostly manual

Targets:
- physicians
- rooms
- signatories

Acceptance criteria:
- admin does not need to create all common master data manually

## 4. Admin Exam Builder

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

## 5. Review / Release Workflow

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

## 6. Search / Reporting

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
