# AI PRD Template

Purpose: define an AI feature or AI-assisted system with explicit evaluation, rollout, and risk controls.

References:
- NIST AI RMF 1.0
- NIST AI RMF: Generative AI Profile
- ISO/IEC 42001
- EU AI Act
- OpenAI eval guides
- OWASP GenAI security guidance

## Inputs

- User problem and workflow context
- Existing non-AI baseline or manual workflow
- Data inventory, rights, retention, and residency constraints
- Runtime constraints: latency, cost, reliability, regions
- Security, privacy, compliance, and abuse constraints

## Outputs

- AI PRD with success criteria, eval plan, rollout gates, and rollback triggers
- Clear go / beta / no-go decision rules

## 1. Overview

- Problem statement: {{PROBLEM_STATEMENT}}
- Primary user / operator: {{PRIMARY_USER}}
- Job to be done: {{JTBD}}
- Why AI is justified over a simpler alternative: {{WHY_AI}}
- Out of scope: {{NON_GOALS}}

## 2. User Workflow And UX

- Entry point in the product or workflow: {{ENTRY_POINT}}
- User-facing behavior: {{UX_BEHAVIOR}}
- User controls and overrides: {{USER_CONTROLS}}
- Disclosures and transparency notes: {{DISCLOSURES}}
- Human review requirements: {{HITL_REQUIREMENTS}}
- Fallback behavior when AI is unavailable or unsafe: {{FALLBACKS}}

## 3. System Boundaries

- Inputs: {{INPUTS}}
- Outputs: {{OUTPUTS}}
- Runtime location (client / server / vendor): {{RUNTIME}}
- Model routing policy: {{MODEL_ROUTING}}
- Tool and integration permissions: {{TOOLS_AND_PERMISSIONS}}
- Side effects the system may trigger: {{SIDE_EFFECTS}}
- Approval boundaries for side effects: {{APPROVAL_BOUNDARIES}}

## 4. Data, Rights, And Retention

| Data | Source | Fields | Sensitive? | Rights / basis | Retention | Residency | Access controls |
|------|--------|--------|------------|----------------|-----------|-----------|-----------------|
| {{DATASET}} | {{SOURCE}} | {{FIELDS}} | {{YES_NO}} | {{RIGHTS}} | {{RETENTION}} | {{REGION}} | {{ACL}} |

- Data minimization approach: {{MINIMIZATION}}
- Redaction / anonymization: {{REDACTION}}
- Eval dataset ownership and freshness policy: {{EVAL_DATA_POLICY}}
- Training / retention restrictions with vendors: {{VENDOR_DATA_RESTRICTIONS}}

## 5. Baseline And Proposed Approach

- Baseline alternative: {{BASELINE_APPROACH}}
- Proposed AI approach: {{MODEL_APPROACH}}
- Prompt / instruction constraints: {{PROMPTING_CONSTRAINTS}}
- Guardrails at generation time: {{GENERATION_GUARDRAILS}}
- Latency budget: {{LATENCY_BUDGET}}
- Cost budget: {{COST_BUDGET}}
- Reliability target: {{RELIABILITY_TARGET}}

## 6. Evaluation Plan (Required Before Broad Rollout)

### Objective

- Decision the eval must support: {{EVAL_OBJECTIVE}}
- Ship bar: {{SHIP_BAR}}
- Guardrail bar: {{GUARDRAIL_BAR}}

### Offline Evaluation

- Dataset(s): {{DATASETS}}
- Ground truth / labeling method: {{LABELING_METHOD}}
- Quality metrics: {{QUALITY_METRICS}}
- Safety metrics: {{SAFETY_METRICS}}
- Cost / latency metrics: {{PERF_METRICS}}
- Known blind spots: {{EVAL_BLIND_SPOTS}}

### Human Evaluation

- Review rubric: {{HUMAN_RUBRIC}}
- Reviewer sampling and calibration plan: {{REVIEWER_PLAN}}
- Inter-rater agreement target: {{IRA_TARGET}}

### Online Evaluation

- Shadow or canary stage: {{SHADOW_OR_CANARY}}
- Experiment design: {{EXPERIMENT_DESIGN}}
- Success metric: {{SUCCESS_METRIC}}
- Guardrails: {{ONLINE_GUARDRAILS}}
- Stop rules: {{STOP_RULES}}

## 7. Failure Modes And Mitigations

| Failure mode | User / business harm | Likelihood | Detection | Mitigation | Residual risk |
|--------------|----------------------|------------|-----------|------------|---------------|
| Incorrect output | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |
| Prompt injection / tool misuse | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |
| Data exfiltration / leakage | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |
| Bias / disparate impact | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |
| Abuse / policy violations | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |
| Vendor outage / model drift | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |
| Cost explosion / latency breach | {{HARM}} | {{L/M/H}} | {{DETECT}} | {{MITIGATE}} | {{RISK}} |

## 8. Monitoring And Incident Response

- Production quality signals: {{PROD_SIGNALS}}
- Prompt injection or abuse signals: {{ABUSE_SIGNALS}}
- Drift detection plan: {{DRIFT_PLAN}}
- Logging and privacy policy: {{LOGGING_POLICY}}
- Alert thresholds: {{ALERT_THRESHOLDS}}
- Incident severity levels and playbook: {{INCIDENT_PLAYBOOK}}

## 9. Rollout Plan

- Rollout stages: {{ROLLOUT_STAGES}}
- Shadow mode duration: {{SHADOW_WINDOW}}
- Feature flags and kill switch: {{FLAGS}}
- Customer / internal communications: {{COMMS}}
- Rollback triggers: {{ROLLBACK_TRIGGERS}}
- Owner for go / no-go decision: {{GO_LIVE_OWNER}}

## 10. Security, Privacy, And Compliance

- Security review requirements: {{SECURITY_REVIEW}}
- Vendor / DPA requirements: {{DPA_REQUIREMENTS}}
- Applicable regulations and classification: {{REGULATORY_NOTES}}
- Audit trail requirements: {{AUDIT_TRAIL}}
- Approval needed before enabling autonomous side effects: {{AUTONOMY_APPROVALS}}

## Decision Rules

- Do not ship beyond internal use without: baseline comparison, offline eval, failure-mode review, monitoring, and rollback plan.
- Do not enable autonomous side effects without: explicit approval boundaries, auditability, and incident ownership.
- Beta requires: offline metrics at or above {{BETA_BAR}} and no unresolved blocker risks.
- Roll back if: {{ROLLBACK_RULES}}.

## Optional AI / Automation Support

Use only if policy allows it.

- Drafting: generate first-pass sections from source notes; human owns final wording.
- Eval support: generate candidate test cases, but require human review and spot checks.
- Monitoring support: summarize incidents and trends; do not auto-resolve incidents without approval.
