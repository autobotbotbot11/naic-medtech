# Decisions

This file records the major project decisions so future work does not depend on lost chat history.

## Accepted Decisions

### 2026-03-10: Workbook Is the Primary Source of Truth

Decision:
- Use [NAIC MEDTECH SYSTEM DATA.xlsx](C:\Users\acer\Desktop\naic-app\NAIC%20MEDTECH%20SYSTEM%20DATA.xlsx) as the authoritative source for exam definitions.

Implications:
- field definitions come from the workbook
- options/packages come from the workbook
- reference ranges come from the workbook
- input behavior is derived from workbook structure

Rejected alternative:
- designing primarily from the Word print templates in [Examinations](C:\Users\acer\Desktop\naic-app\Examinations)

Reason:
- templates are outdated and not reliably aligned with the workbook

### 2026-03-10: Use Fixed Core Plus Configurable Exam Schema

Decision:
- Keep clinic/core entities fixed.
- Make exam definitions configurable.

Fixed:
- patients
- lab requests
- request items
- users
- signatories
- attachments
- audit logs

Configurable:
- exam definitions
- versions
- options
- sections
- fields
- field select options
- reference ranges
- rules
- render profiles

Rejected alternative:
- fully dynamic everything

Reason:
- too much risk in validation, reporting, auditing, printing, and maintenance

### 2026-03-10: Keep Versioned Exam Definitions

Decision:
- Every saved request item must point to a specific exam definition version.
- Published versions are immutable.

Reason:
- changing an exam later must not corrupt or reinterpret old results

Resulting rule:
- changes create a new draft/published version, not an in-place edit

### 2026-03-10: Use Django + SQLite + Templates for MVP

Decision:
- Backend: Django
- Database: SQLite
- Frontend: Django templates with vanilla HTML/CSS/JS

Reason:
- fits the current developer skill set
- minimizes framework overhead
- keeps development practical for a local single-computer clinic deployment

Notes:
- SQLite is acceptable for light/local use
- app should remain portable to a server DB later

### 2026-03-10: Print/Render Layer Is Separate From Data Schema

Decision:
- Do not hardcode the data model around existing print layouts.
- Build print/rendering as a separate layer on top of saved metadata and result values.

Reason:
- rendering concerns are real, but they should not dictate storage design

### 2026-03-10: Initial Print Engine Uses HTML Print Preview

Decision:
- the first print implementation is an HTML print-preview page driven by `ExamRenderProfile`

Reason:
- it is faster to validate with real dynamic data
- it avoids premature PDF complexity
- browser print is enough for the first clinic-ready rendering pass

Implication:
- future PDF/export work should build on the same render context, not replace the current data flow

### 2026-03-10: Real Exam Print Refinement Starts With ABG and BBANK

Decision:
- the first exam-specific print refinements are `ABG` and `BBANK`

Reason:
- they represent two materially different real-world layouts
- `ABG` exercises compact numeric result presentation with abnormal highlighting
- `BBANK` exercises form-style general data plus grouped crossmatch/vital-sign content

Implication:
- future print refinement should continue by adding exam-specific variants only when generic rendering is clearly insufficient

### 2026-03-10: Importer Uses Signature-Based Versioning

Decision:
- Import versioning must change not only when workbook content changes, but also when importer logic changes.

Current implementation:
- importer source reference includes `IMPORTER_SIGNATURE_VERSION`

Reason:
- otherwise importer bugs stay frozen in already-imported definitions

### 2026-03-10: Field-Specific Attachments Are Required

Decision:
- Attachments must be tied to a specific exam field, not only to the request item.

Reason:
- configurable exams may eventually contain more than one attachment field
- field-level association avoids ambiguity

### 2026-03-10: Grouped Measurements Need Stored Config Metadata

Decision:
- grouped fields such as blood-bank vital signs must preserve subfield config in `ExamField.config_json`

Reason:
- dynamic UI/rendering cannot infer grouped structure safely from the flattened field alone

## Current Standing Decisions

Do not reverse these without a concrete replacement plan:
- workbook-first modeling
- versioned exam definitions
- fixed core plus configurable exam schema
- render/print as separate layer
- Django + SQLite MVP stack
