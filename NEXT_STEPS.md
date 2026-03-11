# Next Steps

This file is the working queue for future implementation.

Priority is ordered. Unless the user explicitly redirects, continue from the top.
This queue now follows the phased direction in [STRATEGIC_ROADMAP.md](C:\Users\acer\Desktop\naic-app\STRATEGIC_ROADMAP.md): operations first, controlled configurability second.

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
- exam-specific print refinement completed for `PROTIME/APTT`, `SEMEN`, and `MICROBIOLOGY`
- browser validation completed for `PROTIME/APTT`, `SEMEN`, and `MICROBIOLOGY` in both screen preview and print-media mode
- exam-specific print refinement completed for `CARDIACI`, `BCMALE`, and `BCFEMALE`
- browser validation completed for `CARDIACI`, `BCMALE`, and `BCFEMALE` in both screen preview and print-media mode
- exam-specific print refinement completed for `HBA1C`, `HIV 1 and 2 Testing`, and `COVID 19 Antigen Rapid Test`
- browser validation completed for `HBA1C`, `HIV 1 and 2 Testing`, and `COVID 19 Antigen Rapid Test` in both screen preview and print-media mode
- workbook-driven master-data importer completed for physicians, rooms, and signatories
- custom admin import page completed at `/manage/import-master-data/`
- browser validation completed for the admin master-data import flow
- management command completed: `import_master_data_workbook`
- review/release workflow baseline completed
- admin/system-owner release and reopen actions completed
- released-item read-only behavior completed
- printed timestamp capture from the print action completed
- browser validation completed for encode -> release -> print -> reopen flow

## 1. Clinic Confirmation Pass For Suspicious Source Items

Goal:
- keep a clean boundary between technical assumptions and clinic-confirmed truth

Why:
- importer hardening is now in place
- some workbook items are still intentionally unresolved because they require clinic/lab confirmation, not developer guessing

Starting points:
- [workbook_recalibration_audit.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\workbook_recalibration_audit.md)
- [clinic_confirmation_queue.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\clinic_confirmation_queue.md)
- [client_confirmation_packet.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\client_confirmation_packet.md)
- [client_confirmation_script_taglish.md](C:\Users\acer\Desktop\naic-app\tmp\analysis\client_confirmation_script_taglish.md)

Targets:
- suspicious glucose ranges
- spelling/label confirmation such as `Typhidot`
- unresolved signatory-name note in `FECALYSIS`
- package meaning confirmation for combined exam options

Acceptance criteria:
- the project has a clear clinic-facing queue of items that must be confirmed instead of guessed

## 2. Admin Exam Builder

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

## 3. Search / Reporting

Goal:
- basic operational visibility

Likely first reports:
- request list with filters
- patient result history
- abnormal-result listing
- exam counts by date

Acceptance criteria:
- clinic staff can find prior results without browsing raw admin pages

## 4. Print Parity / Export Follow-Up

Goal:
- keep print output clinic-credible as real client review continues

Why this is not top priority now:
- all current imported exams already have dedicated, browser-validated print variants
- the remaining work here is parity polish and export strategy, not missing core coverage

Targets:
- fix concrete parity issues found during real clinic review
- verify browser print-to-PDF remains acceptable
- decide whether browser print is enough or a PDF/export layer is required

Acceptance criteria:
- no unresolved print gaps block deployment for the clinic's actual workflow

## Operational Rule

If any major direction changes while implementing the above:
- update [PROJECT_CONTEXT.md](C:\Users\acer\Desktop\naic-app\PROJECT_CONTEXT.md)
- update [DECISIONS.md](C:\Users\acer\Desktop\naic-app\DECISIONS.md)
- update this file
