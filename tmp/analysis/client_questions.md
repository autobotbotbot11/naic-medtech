# NAIC Medtech System - Client Questions

## Priority 1 - confirm before system design

1. Kapag may patient request, pwede bang maraming exam sa iisang request / iisang case number?
2. Gusto ba nila ng tunay na `patient master record` na may permanent history, o sapat na ang patient snapshot per lab request?
3. Bukod sa `Name, Age, Sex`, ano pa ang official patient data na kailangan i-store?
   Example: date of birth, address, contact number, patient ID, admission date.
4. Sa printout, kailangan bang exact replica ng current forms, o okay lang basta same content?
5. Para sa `HIV` at `COVID`, ano ang actual na printable result form? Wala kasing malinaw na matching template sa folder.
6. Yung extra templates na `CARDIAC`, `HSCRP`, at `HBA1CI`, kasama ba talaga sa project scope ngayon?
7. Kapag abnormal ang result, automatic bang red text dapat based on normal range?
8. Editable ba ng admin ang `normal values`, units, dropdown options, physicians, rooms, and signatories?

## Priority 2 - workflow and permissions

9. Sino-sino ang gagamit ng system?
   Example: encoder, medtech, pathologist, admin, cashier, front desk.
10. Kailangan ba ng approval flow bago ma-print o ma-release ang result?
11. Sino ang may permission mag-edit ng released result?
12. Kailangan ba ng audit log na kita kung sino ang nag-create, nag-edit, nag-print, at kailan?
13. Kailangan ba ng draft / final / released / printed status sa bawat result?

## Priority 3 - exam behavior

14. Sa exam packages tulad ng `CBC, PLATELET COUNT, ESR`, dapat bang auto-show lang ang relevant fields batay sa napiling package?
15. Sa sex-specific forms tulad ng `BCMALE` at `BCFEMALE`, automatic bang pipili ang system base sa sex ng patient?
16. Sa `BBANK`, gusto ba nila ng hiwalay na structured inputs para sa:
- blood pressure
- pulse rate
- respiratory rate
- temperature
17. Sa `COVID 19 ANTIGEN`, anong ibig sabihin ng note na `kelangan may picture sa result`?
   Example: upload ng test-kit photo, attachment sa result, o image sa printout mismo.
18. Sa `MICROBIOLOGY`, sapat ba ang isang result field lang, o may additional remarks / organism details pa?

## Priority 4 - operations and reporting

19. Kailangan ba ng patient search by name, date, case number, physician, or room?
20. Kailangan ba ng daily / weekly reports per exam type, per physician, or per room?
21. Kailangan ba ng export to Excel or PDF aside from printing?
22. Kailangan ba ng backup / restore feature?
23. Kailangan ba ng offline use inside the clinic network?
24. May integration ba sa billing, cashiering, HIS, or barcode printer?

## Priority 5 - data cleanup from provided files

25. Alin ang mas pagbabasehan natin kapag may conflict: workbook o print template?
26. Sa `SEROLOGY`, alin ang tama:
- `ANTI-HCV` from workbook
- or `TROPONIN I` from the current template
27. Sa `OGTT`, alin ang tamang fasting normal value:
- `70.27-124.32 mg/dl` from workbook
- or `70 - 105 mg/dl` from template
28. Sa `CARDIACI`, alin ang tamang Troponin-I normal value:
- `0.0 - 0.02 ng/mL` from workbook
- or `0.0 - 0.01 ng/mL` from template
29. Sa `BCMALE` at `BCFEMALE`, alin ang official normal values for creatinine, HDL, SGOT, and SGPT?
30. Sa `FECALYSIS`, tama ba ang current pathologist name? May note kasi na `Please double check the name`.

## Minimum requirement for the next client meeting
If time is limited, at least these 8 should be answered:
- P1-Q1
- P1-Q4
- P1-Q5
- P1-Q6
- P1-Q8
- P2-Q10
- P3-Q14
- P5-Q25
