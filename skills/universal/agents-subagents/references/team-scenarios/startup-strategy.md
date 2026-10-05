---
description: Startup Strategy — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Startup Strategy

**Typical scenario**

You want a cross-functional read on a new B2B SaaS idea before building the first MVP.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "startup-strategy"`.

Scenario: We are evaluating a startup idea for finance teams: an AI copilot that reconciles invoice disputes across email, ERP exports, and payment processors for UK mid-market companies.

Required context:
- Problem statement: finance teams lose time reconciling disputes across multiple systems
- Target customer: UK mid-market finance operations teams with 20-200 people
- Constraint: first version must be lightweight, not an ERP replacement

Instructions:
- marketing-strategist: assess positioning, message clarity, and category framing
- startup-business-developer: assess business model, buyer, partnerships, and willingness to pay
- startup-growth-specialist: assess distribution, acquisition loops, and activation risks
- product-strategist: assess PMF signal, MVP scope, and validation order
- software-ux-designer: assess user journey, first-run flow, and adoption friction
- Work independently first, then challenge each other's assumptions
- product-strategist synthesizes a recommendation with top risks, best wedge, and next 3 validation steps
- Include dissent if there is unresolved disagreement
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn the `startup-strategy` board roster in parallel: marketing_strategist, business_developer, growth_specialist, product_strategist, ux_designer.

Task: Evaluate this startup idea:
- AI copilot for invoice-dispute reconciliation across email, ERP exports, and payment processors
- Target customer: UK mid-market finance operations teams
- Constraint: MVP must be narrow and operationally simple

Rules:
- Each agent works from its own domain lens first
- Ask them to return a short memo with recommendation, top risks, and highest-leverage next step
- Wait for all agents to finish
- Then synthesize a final recommendation with agreement, disagreement, and the single best MVP direction
```

**Debate-first variant**

Use when the core disagreement is "horizontal finance workspace" versus "single workflow wedge for invoice disputes."
