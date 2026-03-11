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

### 2026-03-11: Extend Print Refinement To SEROLOGY and OGTT

Decision:
- add dedicated print variants for `SEROLOGY` and `OGTT`
- validate them with browser-level checks in both normal preview mode and print-media mode

Reason:
- both exams contain real option-specific branches that are not represented cleanly by the generic renderer alone
- they are strong tests of whether the workbook-driven metadata model can support both section-based and field-based print flows

Implementation rule:
- option-specific print variants must only use explicit section mappings
- a missing section mapping must not silently fall back to the general section, because that leaks unrelated empty tests into the printed report

### 2026-03-11: Extend Print Refinement To HEMATOLOGY, URINE, and FECALYSIS

Decision:
- add a dedicated panel-style print variant for `HEMATOLOGY`
- add a dedicated microscopy-focused print variant for `URINE` and `FECALYSIS`
- validate all three in both screen preview and print-media mode

Reason:
- these exams cover remaining high-value layout shapes that the generic renderer does not express cleanly
- `HEMATOLOGY` needs option-aware grouping plus sex-specific field selection
- `URINE` and `FECALYSIS` need a mixed model that can handle either section-based prints or single-field package prints without leaking unrelated values

Implementation rules:
- microscopy field-only packages must not render empty unrelated sections
- duplicate microscopy section labels from the workbook may be disambiguated in the renderer with stable numbering like `(1)` and `(2)` for print clarity

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

### 2026-03-11: Workbook Notes Are Internal-Only

Decision:
- workbook `Notes` content is for developers/configuration only
- workbook rows labeled `NOTE` are not patient-facing fields

Implications:
- importer must not map workbook notes into user-facing field help text
- note rows must not appear in encoder forms
- note rows must not appear in printed reports
- internal instructions may still be preserved in config metadata for future admin tooling

Reason:
- the client uses these notes as implementation instructions, not as report content

### 2026-03-11: Use Organization + Facility With Request Branding Snapshots

Decision:
- organization/company identity and facility/branch identity are fixed admin-managed models
- each `LabRequest` should point to a `Facility`
- request records capture text branding snapshots and a copied facility header image snapshot for historical print stability

Reason:
- branding data must be editable in admin
- future multi-branch deployment should not require redesign
- old printed requests should not silently change when facility branding is edited later

### 2026-03-11: Signatories Belong to the Request-Item Encoding Flow

Decision:
- medtech and pathologist selection is part of the request-item/result-entry workflow

Reason:
- signatories apply to a specific lab report, not only to the patient or request shell

### 2026-03-11: Exam Option Selection Must Be Dynamic in the Form

Decision:
- request-item exam options/packages are loaded immediately after exam selection via a small JSON endpoint and vanilla JS

Reason:
- the previous submit-then-error pattern was poor UX and caused avoidable confusion

### 2026-03-11: Use Controlled Login, Not Public Registration

Decision:
- the app requires authenticated users
- use custom login/logout flow inside the app
- do not add open public self-registration

Reason:
- this is an internal clinic system with patient/laboratory data
- public registration adds complexity and weakens control without meaningful benefit for this use case

### 2026-03-11: Small-Clinic Role Baseline

Decision:
- current baseline app roles are:
- `system_owner`
- `admin`
- `encoder`
- `viewer`

Reason:
- the clinic is small enough that more granular roles would add complexity too early
- medtech/pathologist remain signatory records for now and can become full app roles later only if actual usage requires it

### 2026-03-11: Use Admin-Created Accounts With Temporary Passwords

Decision:
- accounts should be created by a trusted admin/system owner
- temporary-password onboarding is supported with `must_change_password`

Rejected alternatives:
- public self-registration
- self-registration with approval queue as the default flow

Reason:
- simpler for a small clinic
- stronger accountability
- avoids duplicate/unverified accounts and extra approval workflow

### 2026-03-11: Use a Custom Admin Portal for Daily Company Administration

Decision:
- Django admin is only a bootstrap/backoffice tool
- day-to-day clinic administration should happen in a custom in-app admin portal

Current custom admin portal scope:
- users
- organizations
- facilities
- physicians
- rooms
- signatories

Reason:
- the clinic admin is not expected to be comfortable using Django admin
- guided forms and limited actions reduce mistakes and make the system easier to operate

### 2026-03-11: Admin Portal UX Should Favor Guided, Low-Overwhelm Operations

Decision:
- the custom admin portal should prefer:
- setup-order guidance
- search/filter on management lists
- clear empty states
- non-destructive wording such as deactivate instead of delete
- temporary-password helper tools for onboarding/reset flows

Reason:
- the target users are non-technical clinic staff
- operational admin pages should reduce confusion, not expose raw system complexity

### 2026-03-11: Treat the Workbook as a Primary Import Source, Not Unquestionable Truth

Decision:
- keep the workbook as the primary discovery/import source
- do not assume every workbook value is already clean, final, or clinically validated
- imported admin-correctable configuration inside the app should become the operational truth after review

Reason:
- the workbook contains developer notes, unresolved comments, spacing/label inconsistencies, and at least some structurally ambiguous data
- relying on it blindly would push source errors directly into the live system

### 2026-03-11: Make the Workbook Importer Header-Aware and Ignore Blank Formatting Noise

Decision:
- importer payload extraction must use sheet headers to determine which column means `reference` and which means `notes`
- blank formatted/padded rows must not affect source hashing or versioning

Reason:
- the workbook does not use one universal sheet schema for columns 4 and 5
- otherwise developer notes can be misread as patient-facing reference text
- otherwise workbook formatting noise can create meaningless import-version churn

## Current Standing Decisions

Do not reverse these without a concrete replacement plan:
- workbook-first modeling
- versioned exam definitions
- fixed core plus configurable exam schema
- render/print as separate layer
- Django + SQLite MVP stack
