---
description: Payments Platform — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Payments Platform

**Typical scenario**

You are adding or revising billing flows and need product, finance, and risk concerns reviewed together.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "payments-platform"`.

Scenario: Design a new annual-plan checkout flow with invoice support, prorations, retries, and refund handling.

Required context:
- billing model and target customer
- provider and settlement constraints
- finance requirement: reconciliation and close must stay manageable

Instructions:
- software-payments-architect reviews the payment and billing architecture
- software-billing-ops-reviewer reviews invoicing, reconciliation, and operator load
- software-security-reviewer reviews auth, data exposure, and abuse paths
- software-risk-reviewer reviews resilience and operational risk
- Blind memos first, then one chaired synthesis of the production-ready recommendation
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn payments_architect, billing_ops_reviewer, security_reviewer, and risk_reviewer.

Task: review an annual-plan checkout and billing flow with invoice support, prorations, retries, and refunds.

Return:
- recommended architecture
- finance operations concerns
- security and resilience risks
- required controls before rollout
```

**Debate-first variant**

Use when the key tradeoff is "move faster with simpler billing logic" versus "add operational controls before launch."
