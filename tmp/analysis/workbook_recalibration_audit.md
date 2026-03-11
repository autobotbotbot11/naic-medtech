# Workbook Recalibration Audit

Date: 2026-03-11

Primary workbook audited:
- [NAIC MEDTECH SYSTEM DATA.xlsx](C:\Users\acer\Desktop\naic-app\NAIC%20MEDTECH%20SYSTEM%20DATA.xlsx)

Related importer implementation:
- [workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py#L307)

## Conclusion

The workbook is still the best available seed/source artifact for exam discovery, but it is not clean enough to be treated as unquestionable operational truth.

The current safe interpretation is:
- `xlsx = primary import source`
- `validated app configuration = operational truth`

The workbook contains:
- structural inconsistencies between sheets
- developer-only notes inside data columns
- unresolved human edits/comments
- ambiguous package labels
- at least one confirmed importer misread caused by sheet-structure mismatch

## Hardening Status

Implemented after this audit:
- importer is now header-aware for `reference` vs `notes`
- blank formatted rows are excluded from payload hashing
- workbook was re-imported with `IMPORTER_SIGNATURE_VERSION = 7`
- latest published local exam versions are now `v7`
- the confirmed `BBANK -> VITAL SIGNS` note misread is fixed in the latest published version

## Audit Scope

This audit checked:
- workbook sheet structure and header consistency
- exam option/package formatting
- notes and developer instructions embedded in cells
- repeated or ambiguous labels
- current importer assumptions
- current imported app metadata
- selected clinical plausibility of suspicious glucose-related values using external references

External references used for selected clinical cross-checks:
- NIDDK Diabetes Tests & Diagnosis: https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis
- CDC A1C Test for Diabetes and Prediabetes: https://www.cdc.gov/diabetes/diabetes-testing/prediabetes-a1c-test.html
- NIDDK Gestational Diabetes Tests & Diagnosis: https://www.niddk.nih.gov/health-information/diabetes/overview/what-is-diabetes/gestational/tests-diagnosis
- MedlinePlus Pinworm test: https://medlineplus.gov/ency/article/003452.htm
- PubMed Typhidot test article: https://pubmed.ncbi.nlm.nih.gov/12592993/

## Highest-Priority Findings

### 1. The importer assumes fixed column meanings even though the workbook does not

Current importer behavior:
- `column 4 -> reference/normal value`
- `column 5 -> notes`

See:
- [workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py#L315)
- [workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py#L316)

Problem:
- some sheets use `column 4 = Notes`
- some sheets use `column 4 = Normal Value`
- `PROTIME, APTT` uses `Normal Values`
- `COVID 19 ANTIGEN` has a special text in row 1 column 5 instead of a normal header

Confirmed impact:
- `BBANK -> VITAL SIGNS` currently imports the Tagalog developer note into `reference_text`, which is wrong
- the note should be treated as internal implementation guidance, not a patient-facing reference range

## 2. Source-hash versioning is currently polluted by blank formatted rows

Current implementation:
- `sheet_payload()` stores every row because the row dictionary includes the numeric `row` value
- `if any(row.values())` is therefore always true

See:
- [workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py#L307)
- [workbook_import.py](C:\Users\acer\Desktop\naic-app\backend\apps\exams\services\workbook_import.py#L318)

Observed workbook reality:
- most sheets have `max_row ~= 995 to 1004`
- but the last meaningful non-empty row is usually only around `16 to 36`

Meaning:
- importer versioning is influenced by workbook formatting footprint, not only meaningful content
- this is a correctness and maintainability risk

## 3. The workbook contains unresolved developer comments and human-edit artifacts

Confirmed examples:
- `FECALYSIS -> Pathologist` has note: `Please double check the name`
- `BBANK -> VITAL SIGNS` has note: `dapat meron na dropdownlist sa blood pressure, pulse rate, resparatory rate, temperature then mag iinput na lang ng result`
- `BCMALE -> RANDOM BLOOD SUGAR` has note asking if normal values should be editable
- many sheets contain `NOTE: ALL RESULTS ABOVE OR BELOW NORMAL VALUE MAKE IT RED`

Interpretation:
- these are not patient/report data
- these are implementation or unresolved-review notes
- they should not be treated as final clinical truth

## 4. Some workbook values are ambiguous rather than obviously wrong

Example:
- `FECALYSIS` examination options are currently:
- `FECALYSIS`
- `FOBT`
- `FECALYSIS, FOBT`
- `SCOTCH TAPE METHOD`

Important result:
- the current importer preserved these as four separate options
- this is not a parser bug
- `FECALYSIS, FOBT` is most likely intended as a combined package option, not necessarily a formatting error

Clinical note:
- `Scotch tape method` is a legitimate pinworm-related test term
- it should not be auto-classified as an error based on wording alone

## 5. There are confirmed data-quality and spelling issues in the workbook

Examples:
- `TYHPIDOT` in `SEROLOGY` appears to be a typo for `Typhidot`
- `ANTI HUMAN GLOBILIN PHASE` in `BBANK` appears to be a spelling issue
- `OTHERS  ` appears with trailing spaces in `FECALYSIS`
- several option lists and unit cells contain leading/trailing spaces

These do not all break the system immediately because normalization already trims some spacing, but they are still source-quality issues.

## Medium-Priority Findings

### 6. Repeated labels are legitimate in several sheets and still require stable internal keys

Examples:
- `SEROLOGY`: `IgM`, `IgG`
- `OGTT`: `1ST HOUR`, `2ND HOUR`, `FASTING BLOOD SUGAR`
- `PROTIME, APTT`: `TEST`, `CONTROL`

This confirms the earlier architecture decision:
- labels alone are not enough
- stable internal `field_key` values remain necessary

### 7. Some sheets use placeholder text where a normal range is expected

Confirmed examples from `PROTIME, APTT`:
- `CONTROL -> SECONDS`
- `% ACTIVITY -> % ACTIVITY`

These are not true reference ranges.

Interpretation:
- these rows need sheet-aware normalization rules
- they should not be treated like standard abnormal-evaluation ranges

### 8. Signatory rows are duplicated across most sheets

Observed pattern:
- many sheets have two `Medical Technologist` rows plus one `Pathologist` row

Current impact:
- not harmful to the data-entry engine because signatory rows are skipped during exam-field import
- but this confirms the workbook mixes print-template concerns with data-definition concerns

## Clinical Plausibility Cross-Check

This section is intentionally conservative.

### Clinically suspicious and should be confirmed with the clinic

#### Fasting glucose / fasting blood sugar upper bounds

Workbook examples:
- `OGTT -> FASTING BLOOD SUGAR = 70.27-124.32 mg/dl`
- `BCMALE -> FASTING BLOOD SUGAR = 70.27-124.32 mg/dL`
- `BCFEMALE -> FASTING BLOOD SUGAR = 70.27-124.32 mg/dL`

Why this is suspicious:
- NIDDK guidance for non-pregnant interpretation lists normal fasting plasma glucose as `99 mg/dL or below`
- `100 to 125 mg/dL` is prediabetes range

Interpretation:
- this workbook value may reflect a local analyzer reference interval, or it may simply be wrong for the intended clinical interpretation
- this must be confirmed with the clinic/lab

#### OGTT context needs clarification

Workbook contains:
- `50g OGTT`
- `75g OGTT`
- `100g OGTT`
- `2-HOUR POSTPRANDIAL`
- `50g ORAL GLUCOSE CHALLENGE`

Why this matters:
- the `50 g oral glucose challenge` is commonly used in gestational diabetes screening
- NIDDK states a 1-hour glucose challenge test may trigger further testing at `140 mg/dL or more`, with some practices using `135 mg/dL`

Interpretation:
- the presence of both general OGTT options and gestational screening-like options in one sheet is not automatically wrong
- but the clinic should confirm intended usage and which patient scenarios each option applies to

### Broadly aligned with common diagnostic references

#### HBA1C

Workbook:
- `NORMAL VALUE = 4.0 - 5.6 %`

CDC/NIDDK:
- normal is `below 5.7%`

Interpretation:
- this workbook entry is broadly aligned with common diagnostic guidance

### Lab-specific or analyzer-specific and should not be auto-corrected without confirmation

Examples:
- creatinine ranges
- uric acid ranges
- CK-MB
- Troponin-I
- BNP
- cholesterol/triglyceride limits

Interpretation:
- many of these can vary by analyzer, lab method, or reporting convention
- they should be reviewed, but not silently overwritten by generic internet ranges

## Specific Examples Worth Keeping in Mind

### FECALYSIS example raised by the user

Workbook raw examination options:
- `FECALYSIS`
- `FOBT`
- `FECALYSIS, FOBT`
- `SCOTCH TAPE METHOD`

Current audit conclusion:
- current import preserved all four options correctly
- the confusing part is the business meaning, not the parser
- `FECALYSIS, FOBT` should be treated as a probable combined package until the clinic says otherwise

### BBANK vital signs

Workbook note:
- this row clearly tells the developer to use structured subfields and dropdown/input behavior

Current audit conclusion:
- this is a good example of why workbook notes are implementation hints, not report/reference text
- the importer should store this as internal config guidance, not `reference_text`

## Recommended Next Actions

### Immediate

1. Freeze further metadata-dependent feature work until importer hardening is done.
2. Make the importer header-aware per sheet.
3. Exclude blank formatted rows from payload hashing and source versioning.
4. Reclassify notes based on sheet headers, not fixed column numbers.
5. Re-import the workbook after importer hardening.

### Next audit/review layer

1. Build a clinic-facing confirmation list for:
- suspicious glucose ranges
- `Typhidot` spelling
- `BBANK` wording/spelling cleanup
- signatory master data
- exact meaning of combo exam options like `FECALYSIS, FOBT`

2. Add admin-side correction capability for:
- exam option labels
- field labels
- normal/reference ranges
- print/render labels

## Final Working Rule After This Audit

Keep this rule going forward:

- `The workbook is the primary source artifact for discovery and import.`
- `The workbook is not automatically correct clinical truth.`
- `Validated imported configuration inside the app should become the operational truth.`
