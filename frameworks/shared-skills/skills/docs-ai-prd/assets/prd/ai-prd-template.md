# AI PRD Template (AI Feature / AI System)

Purpose: define an AI-powered feature/system with an explicit evaluation plan, risk controls, and monitoring/rollback.

References (non-exhaustive):
- NIST AI RMF 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- ISO/IEC 42001 overview: https://www.iso.org/standard/42001
- EU AI Act (Regulation (EU) 2024/1689): https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng

## Inputs

- User problem + workflow context (who, when, why now)
- Data inventory: sources, rights, retention, PII classification
- Baseline solution (non-AI or simpler AI) for comparison
- Constraints: latency/cost budget, safety/compliance requirements, regions

## Outputs

- AI PRD with acceptance criteria, eval plan, risk controls, and incident playbook
- Go/no-go criteria and rollout plan with rollback triggers

## Core

### 1) Overview

- Problem statement: {{PROBLEM_STATEMENT}}
- Primary user: {{PRIMARY_USER}}
- Primary job to be done: {{JTBD}}
- Why AI (vs rules/workflow change): {{WHY_AI}}
- Out of scope: {{NON_GOALS}}

### 2) User Experience + Transparency

- User-facing behavior: {{UX_BEHAVIOR}}
- User controls: {{USER_CONTROLS}}
- Disclosures (what the system is/does): {{DISCLOSURES}}
- Human-in-the-loop requirements (if any): {{HITL_REQUIREMENTS}}

### 3) System Description

- Inputs: {{INPUTS}}
- Outputs: {{OUTPUTS}}
- Where the AI runs (client/server/vendor): {{RUNTIME}}
- Tool use / integrations: {{TOOLS_INTEGRATIONS}}
- Fallback behavior: {{FALLBACKS}}

### 4) Data Plan (Privacy, Rights, Retention)

| Data | Source | Fields | PII? | Rights/License | Retention | Access controls |
|------|--------|--------|------|----------------|-----------|-----------------|
| {{DATASET}} | {{SOURCE}} | {{FIELDS}} | {{YES_NO}} | {{RIGHTS}} | {{RETENTION}} | {{ACL}} |

- Data minimization: {{MINIMIZATION}}
- Redaction/anonymization: {{REDACTION}}
- Consent/notice requirements: {{CONSENT_NOTICE}}
- Cross-border constraints: {{DATA_RESIDENCY}}

### 5) Model/Approach Plan

- Baseline (required): {{BASELINE_APPROACH}}
- Proposed approach: {{MODEL_APPROACH}}
- Prompting/tooling constraints (if LLM): {{PROMPTING_CONSTRAINTS}}
- Safety controls at generation time: {{GENERATION_CONTROLS}}
- Cost/latency budget: {{BUDGETS}}

### 6) Evaluation Plan (REQUIRED)

**Define what “good” means before building.**

#### Offline evaluation

- Test sets: {{DATA_SPLITS_AND_GOLDEN_SET}}
- Labeling/ground truth method: {{LABELING_METHOD}}
- Quality metrics: {{QUALITY_METRICS}}
- Safety metrics: {{SAFETY_METRICS}}
- Performance metrics (latency/cost): {{PERF_METRICS}}

#### Human evaluation

- Rubric (1–5) with definitions: {{HUMAN_RUBRIC}}
- Reviewer sampling + calibration plan: {{REVIEWER_PLAN}}
- Inter-rater agreement target: {{IRA_TARGET}}

#### Online evaluation (if applicable)

- Experiment design: {{EXPERIMENT_DESIGN}}
- Success metric + guardrails: {{SUCCESS_AND_GUARDRAILS}}
- Stop rules: {{STOP_RULES}}

### 7) Failure Modes + Mitigations

| Failure mode | User harm | Likelihood | Detection | Mitigation | Residual risk |
|--------------|-----------|------------|-----------|------------|---------------|
| {{MODE}} | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |

Include at minimum:
- Incorrect output / hallucination
- Prompt injection / tool misuse (if tool-using)
- Data leakage / memorization risk
- Bias / disparate impact risk
- Abuse and policy violations

### 8) Monitoring + Incident Response

- Production quality signals: {{PROD_SIGNALS}}
- Drift monitoring: {{DRIFT_PLAN}}
- Logging policy (privacy): {{LOGGING_POLICY}}
- Alerting thresholds: {{ALERT_THRESHOLDS}}
- Incident severity levels + playbook: {{INCIDENT_PLAYBOOK}}

### 9) Rollout Plan

- Rollout stages: internal → beta → GA (or your plan)
- Feature flags + kill switch: {{FLAGS}}
- Rollback triggers: {{ROLLBACK_TRIGGERS}}
- Customer comms plan: {{COMMS}}

### 10) Security, Privacy, and Compliance

- Security review requirements: {{SECURITY_REVIEW}}
- Data processing agreements (if vendors): {{DPA}}
- Applicable regulations and classification: {{REGULATORY_NOTES}}
- Audit trail requirements: {{AUDIT_TRAIL}}

## Decision Rules

- Do not ship without: baseline comparison + offline eval + explicit safety controls + rollback plan.
- Ship to beta only if: offline metrics meet {{BETA_BAR}} AND failure modes have mitigations and monitoring.
- Stop/rollback if: guardrails regress beyond {{THRESHOLD}} OR incident severity ≥ {{SEVERITY}}.

## Risks

- Evaluation gaps: metrics don’t reflect real user value; weak test sets
- Data risks: unclear rights, PII exposure, retention violations
- Compliance risk: misclassification or missing transparency obligations
- Operational risk: cost/latency overruns, unreliable vendor dependencies

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- PRD drafting: generate first-pass sections from notes; require citation links and human edits.
- Evaluation support: auto-generate test cases, but require human review and spot-checking.
- Monitoring support: summarize incidents and trend alerts; do not auto-resolve without review.
