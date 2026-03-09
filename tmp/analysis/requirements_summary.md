# NAIC Medtech Inputs vs Print Templates - Quick Analysis

- XLSX sheets: **16**
- DOTX templates: **18**
- Common physicians listed: **29**
- Common rooms listed: **21**

## Sheet -> Template mapping (best effort)
- URINE- Clinical Microscopy -> URINE
- SEROLOGY -> SEROLOGY
- SEMEN - Clinical Microscopy -> SEMEN
- OGTT - Blood Chemistry -> OGTT
- MICROBIOLOGY -> MICROBIOLOGY
- HEMATOLOGY -> HEMATOLOGY
- HBA1C - Blood Chemistry -> HBA1C
- FECALYSIS - Clinical Microscopy -> FECALYSIS
- CARDIACI - Serology -> CARDIACI
- BCMALE - Blood Chemistry -> BCMALE
- BCFEMALE - Blood Chemistry -> BCFEMALE
- BBANK - Blood Bank -> BBANK
- ABG - Blood Gas Analysis -> ABG
- HIV 1&2 TESTING - Serology -> SEROLOGYI
- COVID 19 ANTIGEN (RAPID TEST) - -> SEROLOGYI
- PROTIME, APTT - Hematology -> COAG

## Templates not clearly mapped from sheet names
- CARDIAC
- HBA1CI
- HSCRP

## Per-sheet data fields count
- URINE- Clinical Microscopy: patient_fields=8, test_fields=21, exam_options=7
- SEROLOGY: patient_fields=8, test_fields=16, exam_options=6
- SEMEN - Clinical Microscopy: patient_fields=8, test_fields=16, exam_options=1
- OGTT - Blood Chemistry: patient_fields=8, test_fields=16, exam_options=5
- MICROBIOLOGY: patient_fields=8, test_fields=5, exam_options=1
- HEMATOLOGY: patient_fields=8, test_fields=23, exam_options=5
- HBA1C - Blood Chemistry: patient_fields=8, test_fields=5, exam_options=1
- FECALYSIS - Clinical Microscopy: patient_fields=8, test_fields=15, exam_options=4
- CARDIACI - Serology: patient_fields=8, test_fields=7, exam_options=1
- BCMALE - Blood Chemistry: patient_fields=8, test_fields=22, exam_options=12
- BCFEMALE - Blood Chemistry: patient_fields=8, test_fields=22, exam_options=12
- BBANK - Blood Bank: patient_fields=9, test_fields=18, exam_options=1
- ABG - Blood Gas Analysis: patient_fields=8, test_fields=13, exam_options=1
- HIV 1&2 TESTING - Serology: patient_fields=8, test_fields=6, exam_options=1
- COVID 19 ANTIGEN (RAPID TEST) -: patient_fields=8, test_fields=5, exam_options=1
- PROTIME, APTT - Hematology: patient_fields=8, test_fields=10, exam_options=3

## DOTX placeholder density
- ABG: R# placeholders=8 (max R8)
- BBANK: R# placeholders=15 (max R15)
- BCFEMALE: R# placeholders=17 (max R17)
- BCMALE: R# placeholders=17 (max R17)
- CARDIAC: R# placeholders=3 (max R3)
- CARDIACI: R# placeholders=3 (max R4)
- COAG: R# placeholders=4 (max R4)
- FECALYSIS: R# placeholders=10 (max R10)
- HBA1C: R# placeholders=1 (max R1)
- HBA1CI: R# placeholders=1 (max R1)
- HEMATOLOGY: R# placeholders=18 (max R18)
- HSCRP: R# placeholders=1 (max R1)
- MICROBIOLOGY: R# placeholders=0 (max R0)
- OGTT: R# placeholders=11 (max R11)
- SEMEN: R# placeholders=12 (max R12)
- SEROLOGY: R# placeholders=11 (max R11)
- SEROLOGYI: R# placeholders=4 (max R4)
- URINE: R# placeholders=16 (max R16)