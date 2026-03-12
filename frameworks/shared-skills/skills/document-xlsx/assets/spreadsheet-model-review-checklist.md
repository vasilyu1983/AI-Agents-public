# Spreadsheet Model Review Checklist (Core, Non-AI)

Purpose: review a spreadsheet model for correctness, traceability, and decision usefulness.

## Inputs

- Spreadsheet file + change log (who changed what, when)
- Source data references (exports, databases, reports)
- Business question the model supports (decision + timeline)

## Outputs

- Review findings (issues, severity, owner, fix-by date)
- “Ship/No-ship” decision for using the model in decisions

## Core

### A) Structure and Readability

- [ ] Clear separation: Inputs / Calculations / Outputs (tabs or sections)
- [ ] Consistent units and time granularity (daily/weekly/monthly)
- [ ] Named ranges or clearly labeled tables (avoid magic cells)
- [ ] No hidden rows/columns that change meaning (or documented if used)

### B) Inputs and Assumptions

- [ ] Every assumption is explicit (value + unit + source + date)
- [ ] Assumptions are grouped in one place (single “Inputs” area)
- [ ] Scenario controls are obvious (base/best/worst) and not duplicated

### C) Formula Integrity

- [ ] No hardcoded constants inside formulas where an input should exist
- [ ] No inconsistent formulas across a range (spot-check rows/columns)
- [ ] Avoid volatile functions unless justified (INDIRECT, OFFSET, TODAY, RAND)
- [ ] Error handling is intentional (IFERROR used only with a documented fallback)

### D) Traceability and Auditability

- [ ] Key outputs can be traced to inputs in ≤ 3 clicks
- [ ] Source links/notes exist for imported data (file, query, timestamp)
- [ ] Complex logic has a short explanation (“why”, not “what”)

### E) Data Quality Checks

- [ ] Totals reconcile to known sources (control totals)
- [ ] Duplicate/blank/outlier checks exist for key fields
- [ ] Date ranges and filters are explicit (no silent exclusions)

### F) Charts and Outputs

- [ ] Each chart has: title, units, timeframe, and data source note
- [ ] Avoid misleading scales (truncated axes, mixed units)
- [ ] Executive summary tab answers the decision question in 60 seconds

### G) Versioning and Change Control

- [ ] File naming includes date/version (e.g., `Model_2025-12-18_v3.xlsx`)
- [ ] Change log tab exists for material edits (assumptions, formulas, structure)
- [ ] Review/approval owner is named

### H) Accessibility (baseline)

- [ ] Meaning is not color-only (labels/legends present)
- [ ] Sufficient contrast for key charts/tables
- [ ] Sheet/tab names are descriptive

## Decision Rules

- No-ship if: key outputs are not traceable, assumptions are implicit, or formulas are inconsistent.
- Re-review after: changing inputs structure, adding new tabs, or altering core logic.

## Risks

- Silent errors (range drift, broken links, copy/paste mistakes)
- Untraceable logic leads to unreviewable decisions
- Data leakage (customer PII embedded in shared files)

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Generate a “model audit summary” (tabs, key formulas, dependencies); human spot-checks.
- Suggest tests (control totals, anomaly checks); do not auto-fix formulas without review.
