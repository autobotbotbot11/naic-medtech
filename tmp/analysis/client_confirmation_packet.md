# Client Confirmation Packet

Date: 2026-03-11

Purpose:
- give the clinic a short, focused confirmation list
- avoid asking them to review the whole workbook blindly
- separate true clinic decisions from developer-only technical cleanup

Current system state:
- workbook import is already hardened
- all `16` imported exams now render correctly in the app and print preview
- the items below are the remaining source-of-truth questions that should be confirmed by the clinic/lab

Working rule:
- do not ask the client to review everything
- ask only the items below
- if they confirm an item, that confirmed value becomes the app's operational truth

## Recommended Meeting Order

1. confirm values that affect clinical interpretation
2. confirm package meanings that affect workflow/display
3. confirm labels/spelling that affect report credibility
4. confirm signatory/master-data details

## Decision List

### 1. Fasting Blood Sugar normal range

Affected exams:
- `OGTT`
- `BCMALE`
- `BCFEMALE`

Current workbook value:
- `70.27-124.32 mg/dL`

Why this needs confirmation:
- this looks suspicious compared with common diagnostic interpretation
- but it may still be the clinic's analyzer/method-specific reference interval

Current system assumption:
- keep the workbook value as-is until the clinic confirms otherwise

Need from clinic:
- confirm whether `70.27-124.32 mg/dL` is the intended printed/displayed reference range
- if not, provide the exact replacement range
- if yes, confirm whether it is analyzer-specific and should remain exactly as written

System impact if changed:
- update reference ranges in imported exam config
- affects abnormal highlighting and printed reference text

Blocker level:
- high

### 2. Meaning of combined package options

Affected examples:
- `FECALYSIS, FOBT`
- `URINALYSIS, URINE KETONE`
- `URINALYSIS, PREGNANCY TEST`
- `CBC, PLATELET COUNT, BLOOD TYPING`
- `CBC, PLATELET COUNT, ESR`
- `PROTIME, APTT`

Why this needs confirmation:
- these look like real package options, not parser mistakes
- the app can support them either way, but the clinic should confirm intended behavior

Current system assumption:
- treat them as true combined selectable packages

Need from clinic:
- confirm whether these are real package choices
- if yes, confirm that selecting one package should automatically show all included fields/sections
- if no, identify which options should be split or renamed

System impact if changed:
- affects exam-option labels, encoder visibility rules, and print grouping

Blocker level:
- high

### 3. PROTIME / APTT control and percent-activity meaning

Affected exam:
- `PROTIME, APTT`

Current workbook values:
- `CONTROL -> SECONDS`
- `% ACTIVITY -> % ACTIVITY`

Why this needs confirmation:
- these look more like display/unit placeholders than true reference ranges
- the system currently stores them safely, but should not guess abnormal logic

Current system assumption:
- preserve them as-is without inventing clinical range logic

Need from clinic:
- confirm whether `CONTROL` and `% ACTIVITY` should have real reference ranges
- if not, confirm they should remain display-only or unit-style labels

System impact if changed:
- affects future abnormal logic and print reference display

Blocker level:
- medium

### 4. `TYHPIDOT` spelling in Serology

Affected exam:
- `SEROLOGY`

Current workbook option:
- `TYHPIDOT`

Why this needs confirmation:
- likely typo for `Typhidot`
- it directly affects screen/print credibility

Current system assumption:
- preserve workbook spelling until the clinic confirms a correction

Need from clinic:
- confirm the correct label
- confirm preferred display style: uppercase or title case

System impact if changed:
- affects exam-option label on screen and printed reports

Blocker level:
- medium

### 5. Blood-bank wording cleanup

Affected exam:
- `BBANK`

Current workbook example:
- `ANTI HUMAN GLOBILIN PHASE`

Why this needs confirmation:
- wording/spelling appears likely wrong or inconsistent
- this affects professional report credibility more than system behavior

Current system assumption:
- preserve current wording until confirmed

Need from clinic:
- confirm the exact preferred wording for blood-bank phase labels
- confirm whether they want title case or uppercase on reports

System impact if changed:
- affects printed labels and possibly encoder labels

Blocker level:
- medium

### 6. Signatory details and duplicate medtech rows

Affected workbook pattern:
- many sheets show two `Medical Technologist` rows plus one `Pathologist` row
- `FECALYSIS` contains note: `Please double check the name`

Why this needs confirmation:
- the workbook mixes print-template layout with actual master data
- the app currently uses one medtech selection and one pathologist selection per report

Current system assumption:
- one medtech and one pathologist per report is enough operationally
- duplicate medtech rows are treated as print-layout legacy, not workflow requirements

Need from clinic:
- confirm final signatory master data
- confirm whether one medtech selection per report is sufficient
- confirm the correct pathologist details where the workbook note says to double-check

System impact if changed:
- affects master data and report signatures, not exam schema

Blocker level:
- medium

## Questions To Avoid Asking Right Now

Do not ask the client to re-review:
- every unit in every sheet
- every capitalization preference
- every analyzer-specific chemistry range
- every print-layout detail all at once

Reason:
- that would overwhelm the client and reduce response quality

## Recommended Output From The Client

Best-case response format:
- one answer per numbered item above
- exact corrected wording/range where needed
- explicit yes/no for package behavior questions

Example:
- `1. Keep 70.27-124.32 mg/dL as analyzer-specific`
- `2. Yes, FECALYSIS, FOBT is a combined package`
- `4. Change TYHPIDOT to Typhidot`

## What Happens After Confirmation

After the clinic answers:
1. update the corresponding exam metadata
2. keep the confirmed values as the new operational truth
3. leave the workbook as historical import source, not unquestionable truth
