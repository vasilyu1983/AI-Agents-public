---
name: product-management
description: "Operational product management skill: discovery, strategy, roadmaps, metrics, and leadership - using templates, checklists, and patterns (no theory)."
---

# Product Management (Jan 2026)

This skill turns the assistant into an operator, not a lecturer.

Everything here is:
- **Executable**: templates, checklists, decision flows
- **Decision-first**: measurable outcomes, explicit trade-offs, clear ownership
- **Organized**: resources for depth; templates for immediate copy-paste

---

**Modern Best Practices (Jan 2026)**:
- Evidence quality beats confidence: label signals strong/medium/weak; write what would change your mind.
- Outcomes > output: roadmaps are bets with measurable impact and guardrails, not feature inventories.
- Metrics must be defined (formula + timeframe + data source) to be actionable.
- Privacy, security, and accessibility are requirements, not afterthoughts.
- Hybrid decision loops: AI surfaces anomalies, patterns, and forecasts; humans apply context, ethics, and long-term strategy.
- Accountability: product is often held responsible for business outcomes; confirm the operating model in your org and validate benchmarks with current sources.
- Portfolio diversification: a common heuristic is 70% core, 20% adjacent, 10% transformational; adapt to strategy and constraints.

## When to Use This Skill

Use this skill when the user asks to do real product work, such as:

- “Create / refine a PRD / spec / business case / 1-pager”
- “Turn this idea into a roadmap” / “Outcome roadmap for X”
- “Design a discovery plan / interview script / experiment plan”
- “Define success metrics / OKRs / metric tree”
- “Position this product against competitors”
- “Run a difficult conversation / feedback / 1:1 / negotiation”
- “Plan a product strategy / vision / opportunity assessment”

Do not use this skill for:
- Book summaries, philosophy, or general education
- Long case studies or storytelling

---

## Quick Reference

| Task | Template | Domain | Output |
|------|----------|---------|---------|
| Discovery interview | `customer-interview-template.md` | Discovery | Interview script with Mom Test patterns |
| Opportunity mapping | `opportunity-solution-tree.md` | Discovery | OST with outcomes, problems, solutions |
| Outcome roadmap | `outcome-roadmap.md` | Roadmap | Now/Next/Later with outcomes and themes |
| OKR definition | `okr-template.md` | Metrics | 1-3 objectives with 2-4 key results each |
| Product positioning | `positioning-template.md` | Strategy | Competitive alternatives -> value -> segment |
| Product vision | `product-vision-template.md` | Strategy | From→To narrative with 3-5 year horizon |
| 1:1 meeting | `1-1-template.md` | Leadership | Check-in, progress, blockers, growth |
| Post-incident debrief | `a3-debrief.md` | Leadership | Intent vs actual, root cause, action items |

---

## Decision Tree: Choosing the Right Workflow

```text
User needs: [Product Work Type]
    ├─ Discovery / Validation?
    │   ├─ Customer insights? → Customer interview template
    │   ├─ Hypothesis testing? → Assumption test template
    │   └─ Opportunity mapping? → Opportunity Solution Tree
    │
    ├─ Strategy / Vision?
    │   ├─ Long-term direction? → Product vision template
    │   ├─ Market positioning? → Positioning template (Dunford)
    │   ├─ Big opportunity? → Opportunity assessment
    │   └─ Amazon-style spec? → PR/FAQ template
    │
    ├─ Planning / Roadmap?
    │   ├─ Outcome-driven? → Outcome roadmap (Now/Next/Later)
    │   ├─ Theme-based? → Theme roadmap
    │   └─ Metrics / OKRs? → Metric tree + OKR template
    │
    └─ Leadership / Team Ops?
        ├─ 1:1 meeting? → 1-1 template
        ├─ Giving feedback? → Feedback template (SBI model)
        ├─ Post-incident? → A3 debrief
        └─ Negotiation? → Negotiation one-sheet (Voss)
```

---

## Do / Avoid (Jan 2026)

### Do

- Start from the decision: what are we deciding, by when, and with what evidence.
- Define metrics precisely (formula + timeframe + data source) and add guardrails.
- Use discovery to de-risk value before building; prioritize by evidence, not opinions.
- Write “match vs ignore” competitive decisions, not feature grids.

### Avoid

- Roadmap theater (shipping lists) without outcomes and learning loops.
- Vanity KPIs (raw signups, impressions) without activation/retention definitions.
- “Build-first validation” (shipping MVPs without falsifiable hypotheses).
- Collecting customer data without purpose limitation, retention, and access controls.

## What Good Looks Like

- Evidence: 5–10 real user touchpoints or equivalent primary data for material bets.
- Scope: clear non-goals and acceptance criteria that can be tested.
- Learning: post-launch review with metric deltas, guardrail impact, and next decision.

## PRDs and Specs

For PRDs/specs and writing-quality requirements, use the templates in `../docs-ai-prd/`:

- PRD templates: [../docs-ai-prd/assets/prd/prd-template.md](../docs-ai-prd/assets/prd/prd-template.md) and [../docs-ai-prd/assets/prd/ai-prd-template.md](../docs-ai-prd/assets/prd/ai-prd-template.md)

## Optional: AI / Automation

Use only when explicitly requested and policy-compliant.

- AI system lifecycle: [assets/ai/ai-lifecycle-template.md](assets/ai/ai-lifecycle-template.md)
- Agentic workflow docs: [assets/ai/agentic-ai-orchestration.md](assets/ai/agentic-ai-orchestration.md)
- AI product patterns: [references/ai-product-patterns.md](references/ai-product-patterns.md)

## Navigation

**Resources**
- [references/discovery-best-practices.md](references/discovery-best-practices.md)
- [references/roadmap-patterns.md](references/roadmap-patterns.md)
- [references/delivery-best-practices.md](references/delivery-best-practices.md)
- [references/strategy-patterns.md](references/strategy-patterns.md)
- [references/positioning-patterns.md](references/positioning-patterns.md)
- [references/data-product-best-practices.md](references/data-product-best-practices.md)
- [references/interviewing-patterns.md](references/interviewing-patterns.md)
- [references/metrics-best-practices.md](references/metrics-best-practices.md)
- [references/leadership-decision-frameworks.md](references/leadership-decision-frameworks.md)
- [references/operational-guide.md](references/operational-guide.md)
- [data/sources.json](data/sources.json)

**Templates**
- Discovery: [assets/discovery/customer-interview-template.md](assets/discovery/customer-interview-template.md), [assets/discovery/assumption-test-template.md](assets/discovery/assumption-test-template.md), [assets/discovery/opportunity-solution-tree.md](assets/discovery/opportunity-solution-tree.md)
- Strategy/Vision: [assets/strategy/product-vision-template.md](assets/strategy/product-vision-template.md), [assets/strategy/opportunity-assessment.md](assets/strategy/opportunity-assessment.md), [assets/strategy/positioning-template.md](assets/strategy/positioning-template.md), [assets/strategy/PRFAQ-template.md](assets/strategy/PRFAQ-template.md)
- Data: [assets/data/data-product-canvas.md](assets/data/data-product-canvas.md)
- Roadmaps: [assets/roadmap/outcome-roadmap.md](assets/roadmap/outcome-roadmap.md), [assets/roadmap/theme-roadmap.md](assets/roadmap/theme-roadmap.md)
- Metrics: [assets/metrics/metric-tree.md](assets/metrics/metric-tree.md), [assets/metrics/okr-template.md](assets/metrics/okr-template.md)
- Ops/Leadership: [assets/ops/1-1-template.md](assets/ops/1-1-template.md), [assets/ops/feedback-template.md](assets/ops/feedback-template.md), [assets/ops/a3-debrief.md](assets/ops/a3-debrief.md), [assets/ops/negotiation-one-sheet.md](assets/ops/negotiation-one-sheet.md)

**Related Skills**
- [../docs-ai-prd/SKILL.md](../docs-ai-prd/SKILL.md) — PRD, stories, and prompt/playbook templates
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design guidance for specs and PRDs
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — UI implementation considerations for product specs
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Backend/API implications of product decisions

---

## Operational Guide

See [references/operational-guide.md](references/operational-guide.md) for detailed patterns, template walkthroughs, example flows, and execution checklists. Keep SKILL.md as the navigation hub; use assets/ when producing artifacts.

---

## External Resources

See [data/sources.json](data/sources.json) for official frameworks (Lean Startup, OST, PR/FAQ, OKRs) and AI/LLM safety references.

---

Use the quick reference and decision tree above to choose a template, then follow the operational guide for depth.

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about product management tools, frameworks, or practices, use a web search tool to check current trends before answering. If web search is unavailable, use `data/sources.json` and state clearly what you verified vs assumed.

### Trigger Conditions

- "What's the best tool for [roadmapping/product analytics/discovery]?"
- "What should I use for [OKRs/metrics/customer feedback]?"
- "What's the latest in product management?"
- "Current best practices for [discovery/roadmaps/prioritization]?"
- "Is [framework/tool] still relevant in 2026?"
- "[Linear] vs [Jira] vs [other]?" or "[Amplitude] vs [Mixpanel]?"
- "Best approach for [AI product management/agentic products]?"

### Required Searches

1. Search: `"product management best practices 2026"`
2. Search: `"[specific tool] vs alternatives 2026"`
3. Search: `"product management trends January 2026"`
4. Search: `"[discovery/roadmap/OKR] frameworks 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What PM tools/frameworks are popular NOW
- **Emerging trends**: New tools, methods, or patterns gaining traction
- **Deprecated/declining**: Frameworks/tools losing relevance
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- Product management tools (Linear, Productboard, Notion, Coda)
- Analytics platforms (Amplitude, Mixpanel, PostHog)
- Discovery and research tools (Maze, UserTesting, Dovetail)
- Roadmapping approaches (outcome-based, theme-based, now/next/later)
- AI product management patterns
- Prioritization frameworks (RICE, ICE, opportunity scoring)
- OKR and metrics tools
