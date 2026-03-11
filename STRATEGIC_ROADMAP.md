# Strategic Roadmap

Date: 2026-03-11

This file defines the wider product direction for the clinic laboratory system.

Use this when deciding what to build next.
Do not treat the app as a random sequence of features.

## Product Framing

This app is not only:
- patient CRUD
- a print encoder
- a form builder

It is really four connected systems:

1. `Operational clinic system`
- patient/request intake
- exam selection
- result encoding
- print/release workflow

2. `Configuration system`
- exam definitions
- fields
- options/packages
- ranges
- render profiles

3. `Governance system`
- authentication
- roles
- user accountability
- signatories
- auditability

4. `Document/report system`
- clinic-branded printable reports
- abnormal highlighting
- attachment-aware rendering
- signatory presentation

## Current Strategic Position

The project is now strong in:
- core architecture
- workbook importer
- configurable metadata model
- authenticated app access
- custom admin portal baseline
- print coverage for all current imported exams

The project is not yet strong enough in:
- clinic-confirmed source truth
- operational release workflow
- master-data setup convenience
- reporting/search
- custom exam-builder UI

## Main Direction

The best organized direction is:

1. `Make current clinic operations deployable`
2. `Confirm risky source-truth items with the clinic`
3. `Strengthen operational workflow and master-data setup`
4. `Only then expand admin configurability with an exam-builder UI`
5. `After that, add reporting and deployment maturity`

## Phased Plan

## Phase 1: Operational Readiness

Goal:
- make the current known clinic workflow stable, understandable, and usable

Focus:
- clinic confirmation packet follow-through
- master-data convenience
- release/review workflow
- small print parity polish based on real clinic review

Why this comes first:
- this is what makes the app actually usable day to day
- this is what the client will judge first
- if this layer is weak, a powerful exam-builder does not help

Exit criteria:
- staff can create requests, encode results, print reports, and understand item status flow
- master data is not painful to maintain
- risky workbook items have a clear clinic-confirmed answer or an explicit temporary decision

## Phase 2: Controlled Configurability

Goal:
- let non-technical admins adjust exam metadata safely without code changes

Focus:
- admin exam-builder UI
- draft version creation
- publish validation
- label/range/package maintenance
- controlled render-profile editing where appropriate

Why this is second:
- it is a force multiplier
- if built too early, it multiplies wrong assumptions
- once Phase 1 is stable, configuration power becomes safe and valuable

Exit criteria:
- admin can create or revise an exam definition without direct developer intervention
- published versions remain immutable
- older saved results stay historically correct

## Phase 3: Operational Maturity

Goal:
- improve visibility, searchability, and deployment readiness

Focus:
- reports/search
- abnormal result views
- patient history
- deployment hardening
- database portability planning for centralized multi-user deployment

Exit criteria:
- staff can find prior results quickly
- management can get basic operational visibility
- deployment path is clear for local office or VPS use

## What Is Core But Not Immediate

`Admin-configurable exams` is still a core product feature.

But it is a `change-management feature`, not the first proof that the clinic can run daily operations.

That means:
- yes, it remains part of the intended system
- no, it should not displace operational readiness work that comes first

## What Should Not Happen

Do not:
- jump into a full exam-builder before operational flow is stable
- let print-template quirks redesign the data model
- let unresolved workbook ambiguity become silent assumptions
- treat every future change as a code change when it should become admin configuration

## Practical Priority Order

If there is no explicit user redirect, prefer this sequence:

1. clinic confirmation pass
2. master data import/setup convenience
3. release workflow
4. admin exam-builder
5. reports/search
6. deployment hardening and DB migration planning

## Decision Rule

When choosing between:
- a feature that helps daily clinic operation now
- and a feature that increases long-term flexibility later

Prefer the first one until Phase 1 exit criteria are met.
