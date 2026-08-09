# Agentic Coding Metrics Template

Purpose: measure coding-assistant impact without turning the analysis into a vendor marketing deck.

Use this for:
- pilot evaluations
- team rollout decisions
- workflow comparison across tools or operating modes
- PRDs or decision memos about coding-assistant adoption

## 1. Evaluation Question

- Decision to support: {{DECISION}}
- Team / cohort: {{TEAM}}
- Tool or workflow under test: {{TOOL_OR_WORKFLOW}}
- Time window: {{WINDOW}}
- Primary comparison: {{BASELINE_VS_TREATMENT}}

## 2. Study Design

- Baseline period: {{BASELINE_PERIOD}}
- Treatment period: {{TREATMENT_PERIOD}}
- Comparable task sample: {{TASK_SAMPLE}}
- Exclusions: {{EXCLUSIONS}}
- Known confounders: {{CONFOUNDERS}}

## 3. Outcome Metrics

### Delivery

| Metric | Definition | Baseline | Treatment | Notes |
|--------|------------|----------|-----------|-------|
| Lead time | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Review turnaround | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Tasks completed | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |

### Quality

| Metric | Definition | Baseline | Treatment | Notes |
|--------|------------|----------|-----------|-------|
| Defect escape rate | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Rework rate | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Test coverage or relevant test signal | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Security findings | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |

### Developer Experience

| Metric | Definition | Baseline | Treatment | Notes |
|--------|------------|----------|-----------|-------|
| Self-reported productivity | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Trust in outputs | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Adoption / active usage | {{FORMULA}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |

## 4. Task-Level Evidence

Track a sample of comparable tasks instead of relying only on aggregate impressions.

| Task | Complexity | Baseline time | Treatment time | Outcome quality | Notes |
|------|------------|---------------|----------------|-----------------|-------|
| {{TASK}} | {{L/M/H}} | {{TIME}} | {{TIME}} | {{QUALITY}} | {{NOTES}} |

## 5. Perceived Vs Actual Productivity

| Metric | Perceived | Measured | Gap | Notes |
|--------|-----------|----------|-----|-------|
| Productivity | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Time saved | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |
| Quality impact | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{NOTES}} |

Note:
- Do not use perception alone as the rollout decision.
- Use measured outcomes plus reviewer judgment.

## 6. Adoption And Risk Signals

- Prompt injection or unsafe output incidents: {{COUNT}}
- Security or compliance review exceptions: {{COUNT}}
- Rollback events or reverted changes: {{COUNT}}
- Time spent validating or correcting AI output: {{TIME}}
- Dependencies introduced by AI and later removed: {{COUNT}}

## 7. Decision Summary

- Roll out / expand / limit / stop: {{DECISION}}
- Why: {{RATIONALE}}
- Biggest positive signal: {{BEST_SIGNAL}}
- Biggest caution signal: {{BIGGEST_RISK}}
- Next measurement checkpoint: {{NEXT_CHECKPOINT}}

## Recommended Interpretation Rules

- Prefer matched task comparisons over anecdotal wins.
- Separate throughput gains from quality regressions.
- Treat self-reported productivity as one signal, not the decision.
- Document selection effects and workflow changes that could bias results.

## Suggested Sources

- METR early-2025 developer productivity study
- METR February 2026 uplift update
- Your own review, defect, and deployment telemetry
- Team survey data with named methodology
