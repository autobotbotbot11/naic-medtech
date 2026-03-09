# XLSX Exam Behavior Matrix

This matrix is based on the workbook only.
It is intended to show what the dynamic exam engine must support per exam family.

| Workbook sheet | Exam options/packages | Key behaviors needed | Complexity |
| --- | --- | --- | --- |
| `URINE- Clinical Microscopy` | 7 options including `URINALYSIS`, `PREGNANCY TEST` combinations | sections, dropdowns, manual fields, option-based visibility | Medium |
| `SEROLOGY` | 6 options | sections, repeated labels (`IgM`, `IgG`), dropdowns, grouped interpretation | High |
| `SEMEN - Clinical Microscopy` | 1 option | sections, manual fields, some dropdowns, mixed measurements | Medium |
| `OGTT - Blood Chemistry` | 5 options | repeated labels, section variants, package-based visibility, numeric ranges | High |
| `MICROBIOLOGY` | 1 option | single dropdown result | Low |
| `HEMATOLOGY` | 5 bundled options | package visibility, male/female ranges, many numeric fields | High |
| `HBA1C - Blood Chemistry` | 1 option | single numeric result, normal range, abnormal highlight | Low |
| `FECALYSIS - Clinical Microscopy` | 4 options | sections, mixed dropdown/manual, option-based visibility | Medium |
| `CARDIACI - Serology` | 1 option | few numeric fields, normal ranges | Low |
| `BCMALE - Blood Chemistry` | 12 options | package visibility, numeric fields, range-based alerts | High |
| `BCFEMALE - Blood Chemistry` | 12 options | package visibility, numeric fields, range-based alerts | High |
| `BBANK - Blood Bank` | 1 option | sections, mixed field types, grouped vital signs, release metadata | High |
| `ABG - Blood Gas Analysis` | 1 option | sections, numeric values, ranges, note row | Medium |
| `HIV 1&2 TESTING - Serology` | 1 option | lot number + dropdown result | Low |
| `COVID 19 ANTIGEN (RAPID TEST) -` | 1 option | dropdown result, likely attachment/image requirement | Medium |
| `PROTIME, APTT - Hematology` | 3 options | repeated labels (`TEST`, `CONTROL`), section visibility, numeric ranges | High |

## Engine features that appear necessary

### Core capabilities used by many exams
- package/option selection
- section grouping
- manual numeric entry
- dropdown options
- normal range metadata
- abnormal flagging

### Special capabilities only needed for some exams
- repeated-label internal keys
- sex-based range logic
- grouped subfields
- attachment/image support
- note/non-result rows

## Good phased rollout order

### Phase 1 - simplest exams
- `MICROBIOLOGY`
- `HBA1C`
- `CARDIACI`
- `HIV 1&2 TESTING`

### Phase 2 - moderate structured exams
- `URINE`
- `SEMEN`
- `FECALYSIS`
- `ABG`

### Phase 3 - rule-heavy exams
- `SEROLOGY`
- `OGTT`
- `HEMATOLOGY`
- `BCMALE`
- `BCFEMALE`
- `BBANK`
- `PROTIME, APTT`
- `COVID 19 ANTIGEN`

## Main takeaway
Not all exams have the same difficulty.

This is another reason a controlled configurable engine is better than fixed per-exam tables:
- the simple exams can go live earlier
- the heavy exams can be supported by the same engine after rule support is added
