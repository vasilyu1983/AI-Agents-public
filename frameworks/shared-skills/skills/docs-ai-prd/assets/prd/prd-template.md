# PRD Template (Core, Non-AI)

Purpose: write a minimal, actionable Product Requirements Document (PRD) for any product/feature (not AI-specific).

## Inputs

- Problem evidence: quotes, tickets, research notes, logs (sanitized)
- Target users/segments and context of use
- Constraints: timeline, team capacity, dependencies, compliance/security requirements

## Outputs

- PRD with scope, requirements, and measurable success criteria
- Explicit go/no-go decision rules and risks

## Core

### 1) Problem

- Problem statement (1–3 sentences): {{PROBLEM_STATEMENT}}
- Who has the problem: {{PRIMARY_USER}}
- Context: {{WHEN_WHERE}}
- Why now: {{WHY_NOW}}
- Evidence links (docs/tickets/metrics): {{EVIDENCE_LINKS}}

### 2) Goals / Non-Goals

**Goals (outcomes first)**
- {{GOAL_1}}
- {{GOAL_2}}

**Non-goals (explicit exclusions)**
- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

### 3) Users, JTBD, and Success Context

| User/Role | Job to be done | Current workaround | Success looks like |
|----------|-----------------|--------------------|--------------------|
| {{USER}} | {{JTBD}} | {{WORKAROUND}} | {{SUCCESS}} |

### 4) Requirements

**Functional requirements (testable)**
- FR1: {{REQUIREMENT}} (user value + acceptance)
- FR2: {{REQUIREMENT}}

**Non-functional requirements (measurable)**
- Performance: {{SLO_LATENCY_THROUGHPUT}}
- Reliability: {{SLO_UPTIME_ERROR_BUDGET}}
- Security/privacy: {{SECURITY_PRIVACY_REQUIREMENTS}}
- Accessibility: {{ACCESSIBILITY_BAR}}

**Data & analytics**
- Events to instrument: {{EVENTS}}
- Metrics definitions (exact formulas): {{METRIC_DEFS}}
- Guardrails (what must not regress): {{GUARDRAILS}}

**Dependencies & constraints**
- Dependencies: {{DEPENDENCIES}}
- Constraints: {{CONSTRAINTS}}
- Rollout constraints (regions, roles, etc.): {{ROLLOUT_CONSTRAINTS}}

### 5) Scope, Plan, and Open Questions

- Milestones (date + owner): {{MILESTONES}}
- Risks / unknowns: {{RISKS_UNKNOWN}}
- Open questions (owner + due date): {{OPEN_QUESTIONS}}

### 6) Acceptance Criteria & Success Metrics

**Acceptance criteria (binary, testable)**
- [ ] {{ACCEPTANCE_CRITERION_1}}
- [ ] {{ACCEPTANCE_CRITERION_2}}

**Success metrics (measurable)**
- Primary: {{PRIMARY_METRIC}} (baseline {{BASELINE}}, target {{TARGET}}, window {{WINDOW}})
- Inputs: {{INPUT_METRICS}}
- Guardrails: {{GUARDRAIL_METRICS}}

## Decision Rules

- Build only if: evidence is strong enough ({{EVIDENCE_BAR}}) AND success metrics are measurable AND owner is named.
- Stop/pivot if: guardrails regress beyond {{THRESHOLD}} OR success metric misses by {{THRESHOLD}} for {{WINDOW}}.

## Risks

- Mis-scoping: outcome unclear, success metric not attributable
- Data/privacy: PII leakage in analytics or docs
- Delivery: dependency risk, unclear ownership
- Measurement: instrumentation missing, metric definitions inconsistent

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Drafting: generate first-pass PRD sections from notes; human owns decisions and final wording.
- Synthesis: cluster interview notes; include an audit trail (source links + spot-checks).
- QA: scan for missing acceptance criteria, unmeasurable metrics, or ambiguous language; do not fabricate data.
