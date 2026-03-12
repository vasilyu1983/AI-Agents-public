# Operational Guide

Operational notes, patterns, and usage flows that support the lightweight `SKILL.md`.

---

## Resources (Operational Best Practices)

Use these when the user needs **depth + variation of patterns**.

- **Discovery**
 - `references/discovery-best-practices.md`
 - Continuous interviews cadence checklist (Torres)
 - Opportunity Solution Tree (OST) pattern
 - Problem exploration & assumption mapping (Perri, Cagan)
 - Experiment types and test-card formats (Torres, Ries)

- **Delivery & Roadmapping**
 - `references/roadmap-patterns.md`
 - Outcome- and theme-based roadmaps (Lombardo et al.)
 - Prioritization filters & scorecards (RICE, impact/effort)
 - Roadmap communication / stakeholder buy-in checklists
 - `references/delivery-best-practices.md`
 - Discovery → delivery handoff
 - Definition of “high-integrity commitments” (Cagan)
 - After Action Review template (Extreme Ownership)

- **Strategy & Positioning**
 - `references/strategy-patterns.md`
 - Good strategy kernel (diagnosis → guiding policy → actions)
 - Product strategy via focus & strategic bets (Rumelt, Cagan)
 - OKR patterns rooted in outcomes (Doerr, Perri, EMPOWERED)
 - `references/positioning-patterns.md`
 - 10-step positioning process (Dunford)
 - Competitive alternatives / value mapping tables
 - Trend layering & segmentation (“who cares most?”)

- **AI & Data Products**
 - `references/ai-product-patterns.md`
 - AI Product Development Lifecycle (Nika, Milhomem, Parikh)
 - Agentic AI orchestration patterns (multi-agent workflows)
 - AI risk & governance checklist (data, fairness, safety)
 - `references/data-product-best-practices.md`
 - Data product canvas (Milhomem)
 - Golden Data Platform requirements
 - Metrics for data quality / AI performance

- **Interviewing & Validation**
 - `references/interviewing-patterns.md`
 - The Mom Test question patterns (Fitzpatrick)
 - Customer commitment ladder
 - Signal strength scoring for insights

- **Metrics & Experimentation**
 - `references/metrics-best-practices.md`
 - Metric tree: inputs → leading indicators → lagging outcomes
 - Lean Startup innovation accounting templates
 - Cohort & retention analysis patterns

- **Leadership & Team Ops**
 - `references/leadership-decision-frameworks.md`
 - After Action Review / debrief templates
 - Extreme Ownership checklists
 - Manager workflows (1:1s, feedback, delegation, hiring)
 - Negotiation patterns (Voss) & decision frameworks

Each resource file contains:
- **Patterns** with inline examples
- **Checklists** for “Definition of done”
- **Decision flows** where applicable

---

## Templates (Copy-Paste Ready)

Use these when the user wants to **produce a concrete artifact**.

### 1. Discovery

- `assets/discovery/customer-interview-template.md`
 - Script structure:
 - Warm-up & context
 - Past behavior focus (Mom Test)
 - Problem walkthrough
 - Commitment test & next steps

- `assets/discovery/opportunity-solution-tree.md`
 - Sections:
 - Outcome (metric)
 - Opportunities (problem statements)
 - Solution ideas
 - Experiments & status

- `assets/discovery/assumption-test-template.md`
 - Hypothesis
 - Risk type (value / usability / feasibility / viability)
 - Test design
 - Success criteria
 - What we’ll do if validated / invalidated

### 2. Strategy & Vision

- `assets/strategy/product-vision-template.md`
 - From → To narrative
 - Target user & key problems
 - Guiding principles
 - 3–5 year horizon + non-goals

- `assets/strategy/opportunity-assessment.md`
 - Problem, evidence, target customer
 - TAM/SAM/SOM (lightweight)
 - Alternatives & differentiation
 - Risks & assumptions

- `assets/strategy/positioning-template.md`
 - Competitive alternatives
 - Differentiated attributes → value themes
 - Target segment (“who cares most?”)
 - Market frame of reference
 - Positioning statement

- `assets/strategy/PRFAQ-template.md`
 - 1-page press release
 - FAQ: customers, business, tech, risks

### 3. AI & Data Products

- `assets/ai/ai-lifecycle-template.md`
 - Problem framing & value
 - Data readiness checklist
 - Model approach (predictive / generative / agentic)
 - Evaluation metrics (offline & online)
 - Risk & governance

- `assets/ai/agentic-ai-orchestration.md`
 - Goals & constraints
 - Agent roles & capabilities
 - Tools / APIs available
 - Coordination pattern (planner–executor, multi-agent, etc.)
 - Supervision & human-in-the-loop points

- `assets/data/data-product-canvas.md`
 - Data domain & consumer
 - Inputs / transformations / outputs
 - SLAs (freshness, quality)
 - Ownership & governance

### 4. Roadmaps & Planning

- `assets/roadmap/outcome-roadmap.md`
 - Time horizon (e.g. Now / Next / Later)
 - Outcomes (metrics) per horizon
 - Themes (problem spaces)
 - Example initiatives (non-committal)

- `assets/roadmap/theme-roadmap.md`
 - Theme name & problem statement
 - Related OKRs
 - Bets / experiments
 - Dependencies & risks

### 5. Metrics & Goals

- `assets/metrics/metric-tree.md`
 - Company North Star
 - Product-level outcomes
 - Team-level input metrics

- `assets/metrics/okr-template.md`
 - 1–3 Objectives per team
 - 2–4 Key Results per Objective
 - Leading vs lagging indicators tagged

### 6. Team Operations & Leadership

- `assets/ops/1-1-template.md`
 - Check-in (energy, stress, wins)
 - Progress since last time
 - Blockers & support needed
 - Growth & feedback

- `assets/ops/feedback-template.md`
 - Situation → Behavior → Impact → Next steps
 - Checklist for “clear, kind, specific, actionable”

- `assets/ops/a3-debrief.md`
 - What did we intend?
 - What actually happened?
 - Why? (root cause)
 - What will we change?

- `assets/ops/negotiation-one-sheet.md`
 - Desired outcome
 - BATNA
 - Calibrated questions
 - Accusation audit
 - Bargain ranges

---

## How to Use This Skill

### 1. Always Anchor in a Template or Pattern

When user asks:
> “Help me write a PRD / spec / plan / roadmap / KPI tree / interview guide…”

The assistant should:
1. Pick the closest template from `/assets/…`
2. Fill it **with the user’s context**
3. Highlight any blanks the user must fill (e.g. metrics, dates)

Example triggers → templates:

- “Discovery plan / interview script” → `customer-interview-template.md`, `assumption-test-template.md`
- “Positioning for our new product” → `positioning-template.md`
- “AI feature spec / AI PM workflow” → `ai-lifecycle-template.md`, `agentic-ai-orchestration.md`
- “Roadmap for next 6–12 months” → `outcome-roadmap.md`, `theme-roadmap.md`
- “Define OKRs / metrics” → `okr-template.md`, `metric-tree.md`

### 2. Use Resources to Choose or Adapt Patterns

When user is unsure *how* to approach a problem:

> “We’re stuck in build trap.”
> “We ship a lot but don’t move metrics.”
> “We don’t know which ideas to test.”

The assistant should:
- Pull from `references/discovery-best-practices.md`, `references/strategy-patterns.md`, etc.
- Propose **1–2 concrete patterns** and then produce a filled template.

### 3. Keep Everything Operational

The assistant must:
- Avoid book summaries, quotes, and abstract explanation
- Instead output:
 - Checklists
 - Bullet-point steps
 - Tables for decision-making
 - Filled templates

### 4. Prioritize Outcomes and Problems

Across all responses:
- Frame work as **“problem → outcome → options → experiments”**
- Avoid blindly listing features; instead:
 - Re-express features as **hypotheses** and **experiments**
 - Tie actions to specific **metrics / OKRs**

---

## Example Flows to Execute

### A. Turn a vague idea into a discovery plan

1. Use `opportunity-assessment.md` to clarify the problem.
2. Map an Opportunity Solution Tree.
3. Design 3–5 assumption tests (value, usability, feasibility, viability).
4. Produce:
 - Customer interview guide
 - Experiment test cards
 - Draft outcomes & metrics

### B. Design an AI-powered feature (agentic)

1. Use `ai-lifecycle-template.md` to frame problem, data, model, metrics.
2. Use `agentic-ai-orchestration.md` to define agents, tools, and supervision.
3. Add risk & governance checklist.
4. Output a spec ready for Eng/DS review.

### C. Build an outcome-based roadmap

1. Define product vision & strategy using `product-vision-template.md` and strategy patterns.
2. Build an `outcome-roadmap.md` across Now / Next / Later.
3. Attach team OKRs using `okr-template.md`.
4. Produce an exec-facing version and a team-facing version.

---

## Recap

This guide keeps the SKILL.md lightweight while preserving the operational detail and execution flows for product management work.
