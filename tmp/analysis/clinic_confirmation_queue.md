# Clinic Confirmation Queue

Date: 2026-03-11

Purpose:
- list the workbook items that should be confirmed with the clinic/lab before being treated as final operational truth

This is not a bug list only.
Some items here may be valid local lab policy, analyzer-specific configuration, or intended package structure.

## High Priority

### 1. Fasting Blood Sugar normal range values

Affected sheets:
- `OGTT - Blood Chemistry`
- `BCMALE - Blood Chemistry`
- `BCFEMALE - Blood Chemistry`

Workbook value:
- `70.27-124.32 mg/dL`

Why confirm:
- this is clinically suspicious versus common diagnostic interpretation thresholds
- but it could still be a local analyzer reference interval

What to ask:
- Is `70.27-124.32 mg/dL` the intended lab reference range?
- If yes, is it analyzer/method-specific and should it stay as-is?
- If no, what exact fasting normal range should appear in the system?

### 2. `TYHPIDOT` spelling in Serology

Affected sheet:
- `SEROLOGY`

Workbook value:
- `TYHPIDOT`

Why confirm:
- likely typo for `Typhidot`
- should not be silently corrected without clinic confirmation

What to ask:
- Should the exam/package label be `Typhidot`?
- If yes, do they want title case or uppercase on screen/print?

### 3. FECALYSIS pathologist name note

Affected sheet:
- `FECALYSIS - Clinical Microscopy`

Workbook note:
- `Please double check the name`

Why confirm:
- unresolved source note indicates possible wrong pathologist/signatory name

What to ask:
- Is the pathologist record on this sheet correct?
- If not, what exact display name and license details should be used?

### 4. BBANK terminology / spelling cleanup

Affected sheet:
- `BBANK - Blood Bank`

Examples:
- `ANTI HUMAN GLOBILIN PHASE`
- developer note on `VITAL SIGNS`

Why confirm:
- wording/spelling likely needs normalization
- this affects credibility of printed lab reports

What to ask:
- What exact labels should appear on screen and print for blood-bank phases?
- Do they prefer `Anti-Human Globulin Phase` or another local wording?

## Medium Priority

### 5. Meaning of combined exam/package options

Affected sheets and examples:
- `FECALYSIS - Clinical Microscopy` -> `FECALYSIS, FOBT`
- `URINE- Clinical Microscopy` -> `URINALYSIS, URINE KETONE`, `URINALYSIS, PREGNANCY TEST`
- `HEMATOLOGY` -> `CBC, PLATELET COUNT, BLOOD TYPING`, `CBC, PLATELET COUNT, ESR`
- `BCMALE` / `BCFEMALE` -> multi-test chemistry packages
- `PROTIME, APTT - Hematology` -> `PROTIME, APTT`

Why confirm:
- these look like combined packages, not formatting mistakes
- the system can support them, but their intended behavior should be confirmed

What to ask:
- Are these true package options that should remain selectable as one exam option?
- If selected, should all related sections/fields appear automatically?

### 6. PROTIME / APTT field interpretation

Affected sheet:
- `PROTIME, APTT - Hematology`

Workbook values include:
- `CONTROL -> SECONDS`
- `% ACTIVITY -> % ACTIVITY`

Why confirm:
- these appear to be labels/placeholders, not real numeric normal ranges
- the current system can store them, but abnormal evaluation should not guess their meaning

What to ask:
- Should `CONTROL` and `% ACTIVITY` have true reference ranges?
- Or should they be treated as unit/display-only fields?

### 7. Duplicate signatory rows

Affected pattern:
- many sheets contain two `Medical Technologist` rows plus one `Pathologist` row

Why confirm:
- likely print-template legacy rather than actual data-entry requirement
- currently safe because the importer skips signatory rows as exam fields

What to ask:
- Are duplicate medtech rows intentional for print layout only?
- Is one medtech selection per report enough for actual workflow?

## Low Priority / Cosmetic But Worth Cleaning

### 8. Trailing spaces and inconsistent capitalization

Examples:
- `OTHERS  `
- units with leading spaces
- mixed `mEq/L` vs `mEq/l`

Why confirm:
- mostly cosmetic
- still worth normalizing for professional output

What to ask:
- Do they want screen/print labels normalized consistently?

### 9. Uppercase vs title-case naming

Examples:
- many package labels are all-uppercase
- some tests may read better in title case on screen/print

Why confirm:
- current system can preserve source labels, but polished output may benefit from controlled display naming

What to ask:
- Should internal/source labels stay uppercase while print labels are cleaned up?

## Recommendation For Client Discussion

Do not ask everything at once in a vague way.

Recommended order:
1. confirm suspicious clinical ranges first
2. confirm names/spelling that affect report credibility
3. confirm package meanings
4. confirm cosmetic label cleanup preferences

## Current System Status Relative To This Queue

Already safe after importer hardening:
- workbook notes no longer need to be treated as patient-facing content
- `BBANK` vital-signs developer note is now internal-only in the latest imported version
- blank formatting rows no longer drive importer versioning

Still intentionally unresolved until clinic confirmation:
- suspicious glucose ranges
- typo/casing/wording cleanup
- ambiguous package intent
- unresolved signatory naming note in `FECALYSIS`
