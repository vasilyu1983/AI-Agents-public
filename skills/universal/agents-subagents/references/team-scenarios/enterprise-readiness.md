---
description: Enterprise Readiness — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Enterprise Readiness

**Typical scenario**

You need a readiness view before selling to larger customers or answering security reviews.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "enterprise-readiness"`.

Scenario: We need to prepare for a large enterprise prospect that will send a security questionnaire and expects stronger onboarding and support readiness.

Required context:
- Customer requirements, trust posture, and operating constraints
- Optional context: security docs, support workflows, finance ops notes

Instructions:
- startup-compliance-readiness-lead owns the final readiness plan
- software-security-reviewer identifies security and trust gaps that will block procurement
- startup-growth-execution-operator identifies onboarding, support, and handoff gaps
- startup-operating-system-reviewer identifies commercial, invoicing, or operational maturity gaps
- Run the first analysis round in parallel
- startup-compliance-readiness-lead synthesizes a readiness plan with critical blockers, fast wins, and sequencing
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for compliance readiness, security, customer operations, and startup operations in parallel.

Task: assess readiness for a large enterprise prospect that is likely to send a security questionnaire and expect stronger onboarding/support maturity.

Deliverable from each worker:
- blockers
- near-term improvements
- what evidence would satisfy the customer fastest

Wait for all outputs, then synthesize:
- current readiness level
- top blocker list
- 30-day readiness plan
```

**Debate-first variant**

Use debate when the real choice is "close the sales process now with workarounds" versus "delay and fix readiness gaps first."
