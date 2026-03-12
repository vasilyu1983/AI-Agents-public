# AI Coding Impact Experiment Design Template

**Last Updated**: {{DATE}}
**Owner**: {{NAME}}
**Version**: {{VERSION}}

---

Purpose: plan a controlled experiment to measure the causal impact of AI coding tools on developer productivity, quality, or satisfaction. Fill in all sections before starting the experiment. This template ensures statistical rigor and ethical handling of developer data.

## How to Use

1. Complete the **Experiment Metadata** section to define what you are testing.
2. Define **Population** with treatment and control groups.
3. Choose a **Design** type and document the approach.
4. Build the **Measurement Plan** table with baseline values.
5. Pre-register the **Analysis Plan** before collecting data (prevents p-hacking).
6. Review **Threats to Validity** and document mitigations.
7. Get sign-off on **Ethics and Communication** before launch.

---

## Experiment Metadata

| Field | Value |
|-------|-------|
| Experiment name | {{EXPERIMENT_NAME}} |
| Hypothesis | {{SPECIFIC_TESTABLE_HYPOTHESIS — e.g., "Developers using AI coding tools will have 15% shorter cycle times compared to those without, measured over 10 weeks."}} |
| Primary metric | {{PRIMARY_METRIC — e.g., cycle time in hours}} |
| Secondary metrics | {{METRIC_1}}, {{METRIC_2}}, {{METRIC_3}} |
| Duration | {{WEEKS}} weeks (minimum 8 recommended) |
| Start date | {{START_DATE}} |
| End date | {{END_DATE}} |
| Experiment owner | {{OWNER}} |
| Sponsor | {{SPONSOR}} |
| Status | {{PLANNED / RUNNING / COMPLETED / CANCELLED}} |

---

## Population

### Treatment Group (with AI tools)

| Field | Value |
|-------|-------|
| Teams / developers | {{TEAM_NAMES_OR_IDS}} |
| Count (n) | {{COUNT}} |
| Selection criteria | {{HOW_SELECTED — e.g., "Teams working on backend services, matched by size and tech stack"}} |

### Control Group (without AI tools / status quo)

| Field | Value |
|-------|-------|
| Teams / developers | {{TEAM_NAMES_OR_IDS}} |
| Count (n) | {{COUNT}} |
| Selection criteria | {{HOW_SELECTED}} |

### Minimum Sample Size Justification

```
Power analysis parameters:
- Expected effect size (Cohen's d): {{EFFECT_SIZE — e.g., 0.5 (medium)}}
- Significance level (alpha):        0.05
- Statistical power (1 - beta):      0.80
- Test type:                          {{TWO_SIDED / ONE_SIDED}}
- Minimum n per group:                {{CALCULATED_N}}
- Tool used for calculation:          {{G*Power / statsmodels / other}}
```

Actual n per group ({{COUNT}}) {{MEETS / DOES NOT MEET}} the minimum sample size requirement.

---

## Design

| Field | Value |
|-------|-------|
| Design type | {{A/B / BEFORE_AFTER / CROSSOVER / MULTIPLE_BASELINE}} |
| Randomization method | {{METHOD — e.g., "Stratified random assignment by team size and tech stack"}} |
| Blinding | {{SINGLE_BLIND (evaluators don't know group) / DOUBLE_BLIND / NONE}} |
| Washout period (crossover only) | {{WEEKS — if applicable}} |

### Design Rationale

{{EXPLAIN_WHY_THIS_DESIGN — e.g., "A/B chosen because crossover is impractical (can't un-learn tool usage). Stratified randomization ensures comparable groups."}}

### Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Baseline measurement | {{WEEKS}} weeks | Collect pre-experiment metrics for all groups |
| Intervention | {{WEEKS}} weeks | Treatment group receives AI tools + onboarding |
| Measurement | {{WEEKS}} weeks | Collect metrics from both groups |
| Analysis | {{WEEKS}} weeks | Statistical analysis and report |
| Debrief | {{WEEKS}} week(s) | Share results, decide on rollout |

---

## Measurement Plan

| Metric | Data Source | Collection Frequency | Baseline (Treatment) | Baseline (Control) | Expected Effect Size |
|--------|-----------|---------------------|---------------------|--------------------|---------------------|
| {{PRIMARY_METRIC}} | {{SOURCE}} | {{FREQUENCY}} | {{VALUE}} | {{VALUE}} | {{EFFECT}} |
| {{SECONDARY_METRIC_1}} | {{SOURCE}} | {{FREQUENCY}} | {{VALUE}} | {{VALUE}} | {{EFFECT}} |
| {{SECONDARY_METRIC_2}} | {{SOURCE}} | {{FREQUENCY}} | {{VALUE}} | {{VALUE}} | {{EFFECT}} |
| {{SECONDARY_METRIC_3}} | {{SOURCE}} | {{FREQUENCY}} | {{VALUE}} | {{VALUE}} | {{EFFECT}} |

### Data Collection Checklist

- [ ] Baseline metrics collected for at least {{WEEKS}} weeks before intervention
- [ ] Automated data pipelines tested and validated
- [ ] Manual data collection procedures documented
- [ ] Data storage location: {{LOCATION}}
- [ ] Access restricted to: {{PEOPLE_OR_ROLES}}

---

## Analysis Plan

Pre-register this section before data collection begins.

| Field | Value |
|-------|-------|
| Primary statistical test | {{TEST — e.g., independent samples t-test / Mann-Whitney U / mixed-effects model}} |
| Significance level (alpha) | 0.05 |
| Statistical power (1 - beta) | >= 0.80 |
| Minimum detectable effect | {{VALUE — e.g., "15% reduction in cycle time"}} |
| Multiple comparison correction | {{METHOD — Bonferroni / Holm / Benjamini-Hochberg FDR / none if single primary}} |
| Software / tool for analysis | {{R / Python / SPSS / other}} |

### Decision Criteria

| Outcome | Definition | Action |
|---------|-----------|--------|
| Clear positive | Primary metric significant (p < 0.05) with meaningful effect size | Roll out to all teams |
| Positive trend | Primary metric trends positive but not significant | Extend experiment or expand sample |
| No effect | No significant difference | Investigate barriers; consider tool/process changes |
| Negative | Significant negative impact | Stop rollout; diagnose root cause |

### Interim Analysis (Optional)

- Check at experiment midpoint (week {{MIDPOINT}})
- Stop early only if: {{STOPPING_CRITERIA — e.g., "clear harm detected (p < 0.01 negative effect)"}}
- Adjust alpha for interim look: {{ADJUSTED_ALPHA}}

---

## Threats to Validity

### Internal Validity

| Threat | Risk Level | Mitigation |
|--------|-----------|------------|
| Selection bias | {{H/M/L}} | {{MITIGATION — e.g., "Stratified randomization by team size and stack"}} |
| Hawthorne effect | {{H/M/L}} | {{MITIGATION — e.g., "Both groups told they are being studied"}} |
| Novelty effect | {{H/M/L}} | {{MITIGATION — e.g., "Minimum 8-week duration to let novelty wear off"}} |
| Contamination (control uses tools informally) | {{H/M/L}} | {{MITIGATION — e.g., "License enforcement; periodic compliance check"}} |
| Attrition (developers leave during experiment) | {{H/M/L}} | {{MITIGATION — e.g., "Intent-to-treat analysis"}} |
| History (external events affect one group) | {{H/M/L}} | {{MITIGATION — e.g., "Avoid major release cycles during experiment"}} |

### External Validity

| Threat | Risk Level | Mitigation |
|--------|-----------|------------|
| Generalizability to other teams | {{H/M/L}} | {{MITIGATION — e.g., "Include diverse tech stacks in sample"}} |
| Generalizability to other tools | {{H/M/L}} | {{MITIGATION — e.g., "Document tool-specific features used"}} |
| Time-bound effects | {{H/M/L}} | {{MITIGATION — e.g., "Note tool version; results may not hold as tools evolve"}} |

### Construct Validity

| Question | Assessment |
|----------|-----------|
| Does the primary metric actually measure what we intend? | {{ASSESSMENT}} |
| Could improvements come from something other than AI tools? | {{ASSESSMENT}} |
| Are self-reported metrics (surveys) consistent with observed metrics? | {{ASSESSMENT}} |

---

## Ethics and Communication

### Developer Consent

| Field | Value |
|-------|-------|
| Consent approach | {{APPROACH — e.g., "Opt-in with written consent form"}} |
| Right to withdraw | {{Yes — developers can leave the experiment at any time without penalty}} |
| Impact on performance reviews | {{None — experiment participation and metrics will not be used in reviews}} |

### Data Anonymization

| Field | Value |
|-------|-------|
| Individual data access | {{WHO — e.g., "Experiment owner only; all reports use team-level aggregates"}} |
| Anonymization method | {{METHOD — e.g., "Developer IDs replaced with random codes before analysis"}} |
| Data retention | {{PERIOD — e.g., "Raw data deleted 90 days after experiment concludes"}} |

### Results Sharing

| Audience | Format | Timing |
|----------|--------|--------|
| Participating developers | Full results + Q&A session | Within 2 weeks of completion |
| Engineering leadership | Executive summary (use executive-report-template) | Within 3 weeks of completion |
| Wider organization | Blog post or all-hands summary | Within 4 weeks of completion |

---

## Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| Experiment owner | {{NAME}} | {{DATE}} | {{YES/NO}} |
| Engineering sponsor | {{NAME}} | {{DATE}} | {{YES/NO}} |
| Data/privacy lead | {{NAME}} | {{DATE}} | {{YES/NO}} |
| HR (if required) | {{NAME}} | {{DATE}} | {{YES/NO}} |
