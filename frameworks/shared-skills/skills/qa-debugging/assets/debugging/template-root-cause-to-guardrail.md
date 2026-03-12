# Template: Root Cause to Guardrail

Use this template after incident RCA to convert findings into enforceable prevention mechanisms.

## Incident

- Incident ID: `______________________`
- Date: `YYYY-MM-DD`
- Owner: `______________________`

## Root Cause

- Trigger: `________________________________________`
- Failure class: `logic / env / contract / data / tooling / process`
- Primary root cause: `________________________________`
- Why existing controls missed it: `_____________________`

## Guardrail Design

| Guardrail Type | Concrete Change | Owner | Due Date | Verification |
|---|---|---|---|---|
| Test |  |  |  |  |
| Runtime check |  |  |  |  |
| Alert/monitoring |  |  |  |  |
| Workflow/process |  |  |  |  |
| Documentation |  |  |  |  |

## Regression Proof

- Added test(s): `____________________________________`
- Added alert/query: `__________________________________`
- Validation command(s): `______________________________`
- Result: `pass / fail`

## Closure

- [ ] Guardrail merged
- [ ] Alert/query deployed
- [ ] Owner acknowledged runbook update
- [ ] Follow-up date set
