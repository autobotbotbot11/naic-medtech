# Remaining Problems After Configurable Rendering

## Context
Assume these are already accepted:
- workbook-first design
- fixed clinic core
- configurable exam schema
- configurable rendering/print profile

Even after that, there are still hard problems.

This document ranks them from most critical to least critical.

## Priority ranking

### 1. Versioning and historical safety
This is the most dangerous problem.

Why:
- the admin will eventually edit exam fields
- normal ranges may change
- labels may change
- rendering layout may change

Without versioning:
- old saved results can become unreadable
- old printed results can change retroactively
- audit history becomes unreliable
- search/reporting can break

Typical failure example:
- admin renames `dengue_igm` to `igm_dengue`
- old results no longer map correctly

Verdict:
- must be solved before production use

## 2. Conditional logic / rules
This is the second hardest problem.

Why:
- many workbook sheets are not flat forms
- fields depend on selected exam option/package
- some ranges depend on sex
- some attachments depend on exam type

Without controlled rules:
- wrong fields will show
- required fields will be skipped
- forms will become cluttered
- saved data may be incomplete

Typical failure example:
- `100g OGTT` fields show even when `50g OGTT` was chosen

Verdict:
- must be solved in a controlled way

## 3. Data integrity of the admin builder
If the exam builder is too free-form, the app becomes unstable.

Why:
- admins may create duplicate keys
- invalid dropdowns
- broken range configs
- inconsistent labels
- impossible rules

Without strong validation:
- the system becomes fragile
- debugging becomes hard
- reports become unreliable

Verdict:
- must be controlled by draft/publish + validation

## 4. Field identity and naming discipline
Visible labels in the workbook are not enough.

Examples:
- `IgM`
- `1ST HOUR`
- `TEST`
- `CONTROL`

Why this matters:
- storage keys
- filtering
- search
- reporting
- rendering

Without stable internal keys:
- dynamic schema becomes chaotic

Verdict:
- must be solved at the metadata level

## 5. Validation and abnormal-flag rules
The system needs to know more than just field type.

It must also know:
- valid input format
- reference range
- option scope
- sex scope
- abnormal highlight behavior

Without this:
- the form may save invalid data
- abnormal highlighting becomes unreliable
- users may not trust the system

Verdict:
- important for medical workflow accuracy

## 6. Reporting and search over dynamic data
This becomes harder once results are stored dynamically.

Examples:
- search all abnormal `HBA1C`
- report all `COVID` positives this week
- search all results for one patient

This is still solvable, but it requires:
- stable keys
- exam metadata
- field snapshots
- indexed storage

Verdict:
- important, but manageable if earlier layers are designed correctly

## 7. Special field types
Some workbook items are not normal scalar fields.

Examples:
- image attachment for `COVID`
- grouped vital signs in `BBANK`
- non-result note rows

These are not the biggest risk, but they must be modeled intentionally.

Verdict:
- manageable with a controlled field-type list

## 8. Rendering/print layout
This is still important, but once rendering becomes configurable and version-aware, it is no longer the hardest part.

Rendering becomes easier if:
- fields have stable keys
- sections are structured
- rules are explicit
- versions are immutable

Verdict:
- important, but downstream of the core metadata design

## Real conclusion
After configurable rendering, the hardest remaining problems are:

1. versioning
2. conditional logic
3. admin safety / data integrity

These three are the real backbone of the system.

If they are solved well, the rest becomes manageable.

## Recommended order of solution

### First
- stable internal keys
- published exam versions
- result records tied to exact version

### Second
- controlled rule engine for show/hide/require behavior

### Third
- admin validation before publish

### Fourth
- reporting/search optimization

### Fifth
- richer rendering features

## What this means for implementation
Do not jump straight to:
- print designer
- fancy UI builder
- reporting dashboard

First solve:
- identity
- versioning
- rules

That is the safer engineering order.
