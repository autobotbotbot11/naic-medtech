# R Placeholder Context per DOTX

## ABG.dotx
- Table 1, Row 5: pH | R1 | 7.35-7.45 | sO2 | R4 % | 95-100 %
  - prev: ABG | Result | Normal value | Oximetry | Result | Normal value
  - next: pO2 | R2 mmHg | 80-105 mmHg | Acid Base Status | ? | Normal value
- Table 1, Row 6: pO2 | R2 mmHg | 80-105 mmHg | Acid Base Status | ? | Normal value
  - prev: pH | R1 | 7.35-7.45 | sO2 | R4 % | 95-100 %
  - next: pCO2 | R3 mmHg | 35.0-45.0 mmHg | HCO3 | R5 mmol/L | 22-28 mmol/L
- Table 1, Row 7: pCO2 | R3 mmHg | 35.0-45.0 mmHg | HCO3 | R5 mmol/L | 22-28 mmol/L
  - prev: pO2 | R2 mmHg | 80-105 mmHg | Acid Base Status | ? | Normal value
  - next: NOTE:  O | BE(ecf) | R6 mmol/L | -2 to +2 mmol/L
- Table 1, Row 8: NOTE:  O | BE(ecf) | R6 mmol/L | -2 to +2 mmol/L
  - prev: pCO2 | R3 mmHg | 35.0-45.0 mmHg | HCO3 | R5 mmol/L | 22-28 mmol/L
  - next: ? | pO2(A-a) | R7 mmHg | 5-10 mmHg
- Table 1, Row 9: ? | pO2(A-a) | R7 mmHg | 5-10 mmHg
  - prev: NOTE:  O | BE(ecf) | R6 mmol/L | -2 to +2 mmol/L
  - next: ? | TCO2 | R8 mmol/L | 23-29 mmol/L
- Table 1, Row 10: ? | TCO2 | R8 mmol/L | 23-29 mmol/L
  - prev: ? | pO2(A-a) | R7 mmHg | 5-10 mmHg

## BBANK.dotx
- Table 1, Row 3: PATIENT’S BLOOD TYPE | R1 | BLOOD COMPONENT | R2 | DONOR’S BLOOD TYPE | R3
  - prev: EXAMINATION EXAM | REQUESTING PHYSICIANP | ROOMR
  - next: SOURCE OF BLOOD | R4 | SERIAL NUMBER | R5
- Table 1, Row 4: SOURCE OF BLOOD | R4 | SERIAL NUMBER | R5
  - prev: PATIENT’S BLOOD TYPE | R1 | BLOOD COMPONENT | R2 | DONOR’S BLOOD TYPE | R3
  - next: DATE EXTRACTED | R6 | DATE EXPIRY | R7
- Table 1, Row 5: DATE EXTRACTED | R6 | DATE EXPIRY | R7
  - prev: SOURCE OF BLOOD | R4 | SERIAL NUMBER | R5
  - next: TYPE OF CROSSMATCHING | REMARKSR11
- Table 1, Row 7: IMMEDIATE SPIN/ SALINE PHASE | R8 | ?
  - prev: TYPE OF CROSSMATCHING | REMARKSR11
  - next: ALBUMIN PHASE /37 °C | R9 | VITAL SIGNSR12
- Table 1, Row 8: ALBUMIN PHASE /37 °C | R9 | VITAL SIGNSR12
  - prev: IMMEDIATE SPIN/ SALINE PHASE | R8 | ?
  - next: ANTI HUMAN GLOBILIN PHASE | R10 | ?
- Table 1, Row 9: ANTI HUMAN GLOBILIN PHASE | R10 | ?
  - prev: ALBUMIN PHASE /37 °C | R9 | VITAL SIGNSR12
  - next: RELEASED BYR13 | RELEASED TOR14 | DATE/TIMER15

## BCFEMALE.dotx
- Table 1, Row 4: FASTING BLOOD SUGAR | R1 | 74 - 106mg/dl | CHOLESTEROL | R10 | 0 - 200 mg/dl
  - prev: TEST | RESULT | NORMAL VALUES | TEST | RESULT | NORMAL VALUES
  - next: RANDOM BLOOD SUGAR | R2 | 60 - 140 mg/dl | TRIGLYCERIDE | R11 | 0 - 150 mg/dl
- Table 1, Row 5: RANDOM BLOOD SUGAR | R2 | 60 - 140 mg/dl | TRIGLYCERIDE | R11 | 0 - 150 mg/dl
  - prev: FASTING BLOOD SUGAR | R1 | 74 - 106mg/dl | CHOLESTEROL | R10 | 0 - 200 mg/dl
  - next: HGT | HGT | R3 | 53 - 103 mg/dl | HDL CHOLESTEROL | R12 | 30 - 85 mg/dl
- Table 1, Row 6: HGT | HGT | R3 | 53 - 103 mg/dl | HDL CHOLESTEROL | R12 | 30 - 85 mg/dl
  - prev: RANDOM BLOOD SUGAR | R2 | 60 - 140 mg/dl | TRIGLYCERIDE | R11 | 0 - 150 mg/dl
  - next: BLOOD UREA NITROGEN | R4 | 7.9- 20.2 mg/dl | LDL CHOLESTEROL | R13 | 66 - 178 mg/dl
- Table 1, Row 7: BLOOD UREA NITROGEN | R4 | 7.9- 20.2 mg/dl | LDL CHOLESTEROL | R13 | 66 - 178 mg/dl
  - prev: HGT | HGT | R3 | 53 - 103 mg/dl | HDL CHOLESTEROL | R12 | 30 - 85 mg/dl
  - next: CREATININE | R5 | 0.6 - 1.2 mg/dl | VLDL CHOLESTEROL | R14 | 0-40 mg/dl
- Table 1, Row 8: CREATININE | R5 | 0.6 - 1.2 mg/dl | VLDL CHOLESTEROL | R14 | 0-40 mg/dl
  - prev: BLOOD UREA NITROGEN | R4 | 7.9- 20.2 mg/dl | LDL CHOLESTEROL | R13 | 66 - 178 mg/dl
  - next: BLOOD URIC ACID | R6 | 2.6 - 6.0 mg/dl | SGOT(AST) | R15 | 0 - 31 u/l
- Table 1, Row 9: BLOOD URIC ACID | R6 | 2.6 - 6.0 mg/dl | SGOT(AST) | R15 | 0 - 31 u/l
  - prev: CREATININE | R5 | 0.6 - 1.2 mg/dl | VLDL CHOLESTEROL | R14 | 0-40 mg/dl
  - next: SODIUM | R7 | 135 - 148 meq/l | SGPT(ALT) | R16 | 0 - 34 u/l
- Table 1, Row 10: SODIUM | R7 | 135 - 148 meq/l | SGPT(ALT) | R16 | 0 - 34 u/l
  - prev: BLOOD URIC ACID | R6 | 2.6 - 6.0 mg/dl | SGOT(AST) | R15 | 0 - 31 u/l
  - next: POTASSIUM | R8 | 3.5 - 5.3 meq/l | IONIZED CALCIUM | R17 | 1.13-1.32 meq/l
- Table 1, Row 11: POTASSIUM | R8 | 3.5 - 5.3 meq/l | IONIZED CALCIUM | R17 | 1.13-1.32 meq/l
  - prev: SODIUM | R7 | 135 - 148 meq/l | SGPT(ALT) | R16 | 0 - 34 u/l
  - next: CHLORIDE | R9 | 98 - 107 meq/l | OTHERS | O
- Table 1, Row 12: CHLORIDE | R9 | 98 - 107 meq/l | OTHERS | O
  - prev: POTASSIUM | R8 | 3.5 - 5.3 meq/l | IONIZED CALCIUM | R17 | 1.13-1.32 meq/l

## BCMALE.dotx
- Table 1, Row 4: FASTING BLOOD SUGAR | R1 | 74 - 106mg/dl | CHOLESTEROL | R10 | 0 - 200 mg/dl
  - prev: TEST | RESULT | NORMAL VALUES | TEST | RESULT | NORMAL VALUES
  - next: RANDOM BLOOD SUGAR | R2 | 60 - 140 mg/dl | TRIGLYCERIDE | R11 | 0 - 150 mg/dl
- Table 1, Row 5: RANDOM BLOOD SUGAR | R2 | 60 - 140 mg/dl | TRIGLYCERIDE | R11 | 0 - 150 mg/dl
  - prev: FASTING BLOOD SUGAR | R1 | 74 - 106mg/dl | CHOLESTEROL | R10 | 0 - 200 mg/dl
  - next: HGT | HGT | R3 | 53 - 103 mg/dl | HDL CHOLESTEROL | R12 | 30 - 70 mg/dl
- Table 1, Row 6: HGT | HGT | R3 | 53 - 103 mg/dl | HDL CHOLESTEROL | R12 | 30 - 70 mg/dl
  - prev: RANDOM BLOOD SUGAR | R2 | 60 - 140 mg/dl | TRIGLYCERIDE | R11 | 0 - 150 mg/dl
  - next: BLOOD UREA NITROGEN | R4 | 7.9- 20.2 mg/dl | LDL CHOLESTEROL | R13 | 66 - 178 mg/dl
- Table 1, Row 7: BLOOD UREA NITROGEN | R4 | 7.9- 20.2 mg/dl | LDL CHOLESTEROL | R13 | 66 - 178 mg/dl
  - prev: HGT | HGT | R3 | 53 - 103 mg/dl | HDL CHOLESTEROL | R12 | 30 - 70 mg/dl
  - next: CREATININE | R5 | 0.8 -1.3 mg/dl | VLDL CHOLESTEROL | R14 | 0-40 mg/dl
- Table 1, Row 8: CREATININE | R5 | 0.8 -1.3 mg/dl | VLDL CHOLESTEROL | R14 | 0-40 mg/dl
  - prev: BLOOD UREA NITROGEN | R4 | 7.9- 20.2 mg/dl | LDL CHOLESTEROL | R13 | 66 - 178 mg/dl
  - next: BLOOD URIC ACID | R6 | 3.5 -7.2 mg/dl | SGOT(AST) | R15 | 0 - 35 u/l
- Table 1, Row 9: BLOOD URIC ACID | R6 | 3.5 -7.2 mg/dl | SGOT(AST) | R15 | 0 - 35 u/l
  - prev: CREATININE | R5 | 0.8 -1.3 mg/dl | VLDL CHOLESTEROL | R14 | 0-40 mg/dl
  - next: SODIUM | R7 | 135 - 148 meq/l | SGPT(ALT) | R16 | 0 - 45 u/l
- Table 1, Row 10: SODIUM | R7 | 135 - 148 meq/l | SGPT(ALT) | R16 | 0 - 45 u/l
  - prev: BLOOD URIC ACID | R6 | 3.5 -7.2 mg/dl | SGOT(AST) | R15 | 0 - 35 u/l
  - next: POTASSIUM | R8 | 3.5 - 5.3 meq/l | IONIZED CALCIUM | R17 | 1.13-1.32 meq/l
- Table 1, Row 11: POTASSIUM | R8 | 3.5 - 5.3 meq/l | IONIZED CALCIUM | R17 | 1.13-1.32 meq/l
  - prev: SODIUM | R7 | 135 - 148 meq/l | SGPT(ALT) | R16 | 0 - 45 u/l
  - next: CHLORIDE | R9 | 98 - 107 meq/l | OTHERS | O
- Table 1, Row 12: CHLORIDE | R9 | 98 - 107 meq/l | OTHERS | O
  - prev: POTASSIUM | R8 | 3.5 - 5.3 meq/l | IONIZED CALCIUM | R17 | 1.13-1.32 meq/l

## CARDIAC.dotx
- Table 1, Row 4: TROPONIN I | R1 | TROP I | CK-MB | MYO | INTERPRETATION
  - prev: CARDIAC PANEL TEST | LEGEND
  - next: ? | ? | + | + | + | Myocardial cell necrosis within the past 12 hours
- Table 1, Row 7: CK-MB | R2 | + | + | - | Acute myocardial infarction post 12 hours from the onset of early symptoms.
  - prev: ? | - | + | + | Early muscle or cardiac injury.
  - next: ? | ? | - | + | - | Early muscle or cardiac injury.
- Table 1, Row 10: MYOGLOBULIN | R3 | - | - | + | Early muscle or cardiac injury.
  - prev: ? | + | - | - | Acute myocardial infarction post 24-96 hours
  - next: ? | ? | + | - | + | A very possible myocardial cell necrosis

## CARDIACI.dotx
- Table 1, Row 4: CK-MB | R1 ng/mL | 0.0 - 4.3 ng / mL
  - prev: TEST | RESULT | NORMAL VALUES
  - next: TROPONIN - I | R3 ng/mL | 0.0 - 0.01 ng /mL
- Table 1, Row 5: TROPONIN - I | R3 ng/mL | 0.0 - 0.01 ng /mL
  - prev: CK-MB | R1 ng/mL | 0.0 - 4.3 ng / mL
  - next: BNP | R4 pg/mL | 0.0 - 100 pg / mL
- Table 1, Row 6: BNP | R4 pg/mL | 0.0 - 100 pg / mL
  - prev: TROPONIN - I | R3 ng/mL | 0.0 - 0.01 ng /mL

## COAG.dotx
- Table 1, Row 4: TEST | R1 | TEST | R4
  - prev: PROTHROMBIN TIME | ACTIVATED PARTIAL THROMBOPLASTIN TIME
  - next: INR | R2 | NORMAL VALUE | 22-38 SECONDS
- Table 1, Row 5: INR | R2 | NORMAL VALUE | 22-38 SECONDS
  - prev: TEST | R1 | TEST | R4
  - next: % ACTIVITY | R3 | OTHERSO
- Table 1, Row 6: % ACTIVITY | R3 | OTHERSO
  - prev: INR | R2 | NORMAL VALUE | 22-38 SECONDS
  - next: NORMAL VALUE | 10 - 14 SECONDS | ?

## FECALYSIS.dotx
- Table 1, Row 4: COLOR | R1 | PARASITES  R9
  - prev: MACROSCOPIC FINDING | MICROSCOPIC FINDING
  - next: CONSISTENCY | R2 | ?
- Table 1, Row 5: CONSISTENCY | R2 | ?
  - prev: COLOR | R1 | PARASITES  R9
  - next: FECAL OCCULT BLOODR3 | ?
- Table 1, Row 8: MICROSCOPIC FINDING | AMOEBA  R10
  - next: PUS | R4 / HPF | ?
- Table 1, Row 9: PUS | R4 / HPF | ?
  - prev: MICROSCOPIC FINDING | AMOEBA  R10
  - next: RED BLOOD CELL | R5 / HPF | ?
- Table 1, Row 10: RED BLOOD CELL | R5 / HPF | ?
  - prev: PUS | R4 / HPF | ?
  - next: BUDDING YEAST | R6 | OTHERS  O
- Table 1, Row 11: BUDDING YEAST | R6 | OTHERS  O
  - prev: RED BLOOD CELL | R5 / HPF | ?
  - next: BACTERIA | R7 | ?
- Table 1, Row 12: BACTERIA | R7 | ?
  - prev: BUDDING YEAST | R6 | OTHERS  O
  - next: FAT GLOBULES | R8 | ?
- Table 1, Row 13: FAT GLOBULES | R8 | ?
  - prev: BACTERIA | R7 | ?

## HBA1C.dotx
- Table 1, Row 3: RESULT | R1 % | NORMAL VALUE = 4.0 - 5.6%
  - prev: EXAMINATION E | REQUESTING PHYSICIANR | ROOMR

## HBA1CI.dotx
- Table 1, Row 3: RESULT | R1 % | NORMAL VALUE = 4.0 - 6.0%
  - prev: EXAMINATION E | REQUESTING PHYSICIANR | ROOMR

## HEMATOLOGY.dotx
- Table 1, Row 4: RBC COUNT     (M) | R1 | 4.6 - 6.2 X 1012/L | DIFF COUNT | ? | ?
  - prev: TEST | RESULT | NORMAL VALUES | TEST | RESULT | NORMAL VALUES
  - next: (F) | R2 | 4.2 - 5.4 X 1012/L | SEGMENTERS | R12 | 0.50 - 0.70
- Table 1, Row 5: (F) | R2 | 4.2 - 5.4 X 1012/L | SEGMENTERS | R12 | 0.50 - 0.70
  - prev: RBC COUNT     (M) | R1 | 4.6 - 6.2 X 1012/L | DIFF COUNT | ? | ?
  - next: WBC COUNT | R3 | 5.0 - 10.0 X 109/L | LYMPHOCYTES | R13 | 0.25 - 0.40
- Table 1, Row 6: WBC COUNT | R3 | 5.0 - 10.0 X 109/L | LYMPHOCYTES | R13 | 0.25 - 0.40
  - prev: (F) | R2 | 4.2 - 5.4 X 1012/L | SEGMENTERS | R12 | 0.50 - 0.70
  - next: HEMOGLOBIN (M) | R4 | 140-180 g/L | MONOCYTES | R14 | 0.03 - 0.08
- Table 1, Row 7: HEMOGLOBIN (M) | R4 | 140-180 g/L | MONOCYTES | R14 | 0.03 - 0.08
  - prev: WBC COUNT | R3 | 5.0 - 10.0 X 109/L | LYMPHOCYTES | R13 | 0.25 - 0.40
  - next: (F) | R5 | 120 - 160 g/L | EOSINOPHILS | R15 | 0.01 - 0.04
- Table 1, Row 8: (F) | R5 | 120 - 160 g/L | EOSINOPHILS | R15 | 0.01 - 0.04
  - prev: HEMOGLOBIN (M) | R4 | 140-180 g/L | MONOCYTES | R14 | 0.03 - 0.08
  - next: HEMATOCRIT (M) | R6 | 0.40-0.54 /L | STAB | R16 | 0 - 0.05
- Table 1, Row 9: HEMATOCRIT (M) | R6 | 0.40-0.54 /L | STAB | R16 | 0 - 0.05
  - prev: (F) | R5 | 120 - 160 g/L | EOSINOPHILS | R15 | 0.01 - 0.04
  - next: (F) | R7 | 0.37 - 0.42 /L | E.S.R .     (M) | R17 | 0 - 10 mm/hr
- Table 1, Row 10: (F) | R7 | 0.37 - 0.42 /L | E.S.R .     (M) | R17 | 0 - 10 mm/hr
  - prev: HEMATOCRIT (M) | R6 | 0.40-0.54 /L | STAB | R16 | 0 - 0.05
  - next: PLATELET COUNT | R8 | 150 - 450 X 109/L | (F) | R18 | 0 - 20 mm/hr
- Table 1, Row 11: PLATELET COUNT | R8 | 150 - 450 X 109/L | (F) | R18 | 0 - 20 mm/hr
  - prev: (F) | R7 | 0.37 - 0.42 /L | E.S.R .     (M) | R17 | 0 - 10 mm/hr
  - next: CLOTTING TIME | R9 | 1 - 6 minutes | OTHERSO
- Table 1, Row 12: CLOTTING TIME | R9 | 1 - 6 minutes | OTHERSO
  - prev: PLATELET COUNT | R8 | 150 - 450 X 109/L | (F) | R18 | 0 - 20 mm/hr
  - next: BLEEDING TIME | R10 | 1 - 6 minutes | ?
- Table 1, Row 13: BLEEDING TIME | R10 | 1 - 6 minutes | ?
  - prev: CLOTTING TIME | R9 | 1 - 6 minutes | OTHERSO
  - next: BLOOD TYPING | R11 | A/B/O/AB | ?
- Table 1, Row 14: BLOOD TYPING | R11 | A/B/O/AB | ?
  - prev: BLEEDING TIME | R10 | 1 - 6 minutes | ?

## HSCRP.dotx
- Table 1, Row 4: HsCRP | R1 mg/L | < 1.0 mg / L
  - prev: TEST | RESULT | NORMAL VALUES
  - next: INTERPRETATION:                           LESS THAN 1  mg / L          =   LOW RISK FOR CVD                                                                     1.0 – 2.9 mg / L         =    INTERMEDIATE RISK FOR CVD                                          GREATER THAN 3 mg / L     =   HIGH RISK FOR CVD

## MICROBIOLOGY.dotx
- No R# placeholders found

## OGTT.dotx
- Table 1, Row 5: 1ST HOUR | R1 | < 200 mg/dl | FASTING BLOOD SUGAR | R6 | 70 - 105 mg/dl
  - prev: 50G ORAL GLUCOSE TOLERANCE | ? | 100G ORAL GLUCOSE TOLERANCE | ?
  - next: 2ND HOUR | R2 | < 140 mg/dl | 1ST HOUR | R7 | < 180 mg/dl
- Table 1, Row 6: 2ND HOUR | R2 | < 140 mg/dl | 1ST HOUR | R7 | < 180 mg/dl
  - prev: 1ST HOUR | R1 | < 200 mg/dl | FASTING BLOOD SUGAR | R6 | 70 - 105 mg/dl
  - next: 75 G ORAL GLUCOSE TOLERANCE | ? | 2ND HOUR | R8 | < 155 mg/dl
- Table 1, Row 7: 75 G ORAL GLUCOSE TOLERANCE | ? | 2ND HOUR | R8 | < 155 mg/dl
  - prev: 2ND HOUR | R2 | < 140 mg/dl | 1ST HOUR | R7 | < 180 mg/dl
  - next: FASTING BLOOD SUGAR | R3 | 70 - 105 mg/dl | 3RD HOUR | R9 | < 140 mg/dl
- Table 1, Row 8: FASTING BLOOD SUGAR | R3 | 70 - 105 mg/dl | 3RD HOUR | R9 | < 140 mg/dl
  - prev: 75 G ORAL GLUCOSE TOLERANCE | ? | 2ND HOUR | R8 | < 155 mg/dl
  - next: 1ST HOUR | R4 | < 200 mg/dl | ?
- Table 1, Row 9: 1ST HOUR | R4 | < 200 mg/dl | ?
  - prev: FASTING BLOOD SUGAR | R3 | 70 - 105 mg/dl | 3RD HOUR | R9 | < 140 mg/dl
  - next: 2ND HOUR | R5 | < 140 mg/dl | TEST | RESULT
- Table 1, Row 10: 2ND HOUR | R5 | < 140 mg/dl | TEST | RESULT
  - prev: 1ST HOUR | R4 | < 200 mg/dl | ?
  - next: OTHERSO | 2 HOURS POST PRANDIAL | R10
- Table 1, Row 11: OTHERSO | 2 HOURS POST PRANDIAL | R10
  - prev: 2ND HOUR | R5 | < 140 mg/dl | TEST | RESULT
  - next: ? | 50 G ORAL GLUCOSE CHALLENGE | R11
- Table 1, Row 12: ? | 50 G ORAL GLUCOSE CHALLENGE | R11
  - prev: OTHERSO | 2 HOURS POST PRANDIAL | R10

## SEMEN.dotx
- Table 1, Row 4: TIME COLLECTED: | R1 | NORMAL: | R7 %
  - prev: ? | MORPHOLOGY
  - next: TIME RECEIVED: | R2 | ABNORMAL: | R8 %
- Table 1, Row 5: TIME RECEIVED: | R2 | ABNORMAL: | R8 %
  - prev: TIME COLLECTED: | R1 | NORMAL: | R7 %
  - next: TOTAL VOLUME: | R3 | SPERM COUNT
- Table 1, Row 6: TOTAL VOLUME: | R3 | SPERM COUNT
  - prev: TIME RECEIVED: | R2 | ABNORMAL: | R8 %
  - next: LIQUEFACTION TIME: | R4 | RESULT | R9
- Table 1, Row 7: LIQUEFACTION TIME: | R4 | RESULT | R9
  - prev: TOTAL VOLUME: | R3 | SPERM COUNT
  - next: ? | NORMAL VALUE | 60 – 160 MILLION/L
- Table 1, Row 10: ? | WBC:     R10 /HPF
  - prev: MOTILITY | OTHERS
  - next: MOTILE: | R5 % | RBC:   R11 /HPF
- Table 1, Row 11: MOTILE: | R5 % | RBC:   R11 /HPF
  - prev: ? | WBC:     R10 /HPF
  - next: NON MOTILE: | R6 % | EPITHELIAL CELL:   R12
- Table 1, Row 12: NON MOTILE: | R6 % | EPITHELIAL CELL:   R12
  - prev: MOTILE: | R5 % | RBC:   R11 /HPF

## SEROLOGY.dotx
- Table 1, Row 3: TYPHIDOT | HbsAg SCREENING:R9
  - prev: EXAMINATION EXAM | REQUESTING PHYSICIANP | ROOMR
  - next: lgM | R1 | ?
- Table 1, Row 4: lgM | R1 | ?
  - prev: TYPHIDOT | HbsAg SCREENING:R9
  - next: lgG | R2 | VDRL:R8
- Table 1, Row 5: lgG | R2 | VDRL:R8
  - prev: lgM | R1 | ?
  - next: DENGUE TEST | ?
- Table 1, Row 7: Ns1Ag | R3 | TROPONIN I :R10
  - prev: DENGUE TEST | ?
  - next: lgM | R4 | ?
- Table 1, Row 8: lgM | R4 | ?
  - prev: Ns1Ag | R3 | TROPONIN I :R10
  - next: lgG | R5 | ASO TITER:R11
- Table 1, Row 9: lgG | R5 | ASO TITER:R11
  - prev: lgM | R4 | ?
  - next: MALARIAL TEST | ?
- Table 1, Row 11: ANTI-PLASMODIUM FALCIFARUM | R6 | OTHERSO
  - prev: MALARIAL TEST | ?
  - next: ANTI PLASMODIUM VIVAX | R7 | ?
- Table 1, Row 12: ANTI PLASMODIUM VIVAX | R7 | ?
  - prev: ANTI-PLASMODIUM FALCIFARUM | R6 | OTHERSO

## SEROLOGYI.dotx
- Table 1, Row 4: ASO TITER ( 5YEARS OLD & ABOVE ) | R1 IU/mL | 0 - 200 IU / mL
  - prev: TEST | RESULT | NORMAL VALUES
  - next: ASO TITER ( LESS THAN 5 YEARS OLD ) | R2 IU/mL | 0 - 100 IU / mL
- Table 1, Row 5: ASO TITER ( LESS THAN 5 YEARS OLD ) | R2 IU/mL | 0 - 100 IU / mL
  - prev: ASO TITER ( 5YEARS OLD & ABOVE ) | R1 IU/mL | 0 - 200 IU / mL
  - next: RHEUMATOID FACTOR | R3 IU/mL | 0 - 18 IU / mL
- Table 1, Row 6: RHEUMATOID FACTOR | R3 IU/mL | 0 - 18 IU / mL
  - prev: ASO TITER ( LESS THAN 5 YEARS OLD ) | R2 IU/mL | 0 - 100 IU / mL
  - next: C3 | R4 mg/dL | 90 -180 mg / dL
- Table 1, Row 7: C3 | R4 mg/dL | 90 -180 mg / dL
  - prev: RHEUMATOID FACTOR | R3 IU/mL | 0 - 18 IU / mL

## URINE.dotx
- Table 1, Row 4: COLOR | R1 | WHITE BLOOD CELL | R9 / HPF
  - prev: MACROSCOPIC FINDING | MICROSCOPIC FINDING
  - next: TRANSPARENCY | R2 | RED BLOOD CELL | R8 / HPF
- Table 1, Row 5: TRANSPARENCY | R2 | RED BLOOD CELL | R8 / HPF
  - prev: COLOR | R1 | WHITE BLOOD CELL | R9 / HPF
  - next: REACTION | R3 | EPITHELIAL CELL | R10
- Table 1, Row 6: REACTION | R3 | EPITHELIAL CELL | R10
  - prev: TRANSPARENCY | R2 | RED BLOOD CELL | R8 / HPF
  - next: SPECIFIC GRAVITY | R4 | AMORPHOUS URATES | R11
- Table 1, Row 7: SPECIFIC GRAVITY | R4 | AMORPHOUS URATES | R11
  - prev: REACTION | R3 | EPITHELIAL CELL | R10
  - next: CLINICAL FINDING | AMORPHOUS PHOSPHATE | R12
- Table 1, Row 8: CLINICAL FINDING | AMORPHOUS PHOSPHATE | R12
  - prev: SPECIFIC GRAVITY | R4 | AMORPHOUS URATES | R11
  - next: SUGAR | R5 | CALCIUM OXALATE | R13
- Table 1, Row 9: SUGAR | R5 | CALCIUM OXALATE | R13
  - prev: CLINICAL FINDING | AMORPHOUS PHOSPHATE | R12
  - next: PROTEIN | R6 | URIC ACID CRYSTAL | R14
- Table 1, Row 10: PROTEIN | R6 | URIC ACID CRYSTAL | R14
  - prev: SUGAR | R5 | CALCIUM OXALATE | R13
  - next: PREGNANCY TESTR7 | MUCUS THREAD | R15
- Table 1, Row 11: PREGNANCY TESTR7 | MUCUS THREAD | R15
  - prev: PROTEIN | R6 | URIC ACID CRYSTAL | R14
  - next: ? | BACTERIA | R16
- Table 1, Row 12: ? | BACTERIA | R16
  - prev: PREGNANCY TESTR7 | MUCUS THREAD | R15
  - next: ? | OTHERS        O
