# Regression Log

Versioned record of reruns, regressions, and recoveries.

## Header

```text
Agent: [Name]
Created: YYYY-MM-DD
Current version: [Version]
Baseline version: [Version]
Last tested: YYYY-MM-DD
```

## Entry Template

```text
## Version [Version] - YYYY-MM-DD

Change type: prompt / tool / model / judge / retrieval / workflow
Description: [what changed]
Risk areas: [what might regress]
Rerun scope: smoke / regression / security / online

Task average: X.X/18
Refusal average: X.X/3
Suite normalized: X.XX
Status: PASS / CONDITIONAL / FAIL
Quality band: Needs work / Review / Strong

Hard fails:
- [none or list]

Notes:
- [regression or improvement]
- [follow-up]
```

## Rebaseline Trigger

Use a new baseline when the model, tool workflow, or prompt architecture changes materially.
