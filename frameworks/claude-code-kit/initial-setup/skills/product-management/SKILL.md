---
name: product-management
description: >
 A Claude Code skill for executing high-quality product management work end-to-end:
 discovery, strategy, AI/LLM products, roadmaps, metrics, and leadership – using only
 operational templates, checklists, and patterns (no theory).
---

# Product Operations Skill – Quick Reference

This skill turns Claude into an **operator**, not a lecturer.

Everything here is:
- **Executable**: templates, checklists, decision flows
- **Opinionated**: distilled from Torres, Cagan, Ries, Perri, Dunford, Nika, Amazon, etc.
- **Organized**: resources for depth; templates for immediate copy-paste

---

## When to Use This Skill

Claude should invoke this skill when the user asks to **do real product work**, such as:

- “Create / refine a PRD / spec / business case / 1-pager”
- “Turn this idea into a roadmap” / “Outcome roadmap for X”
- “Design a discovery plan / interview script / experiment plan”
- “Define success metrics / OKRs / metric tree”
- “Position this product against competitors”
- “Design an AI-powered feature / GenAI agent / AI PM lifecycle”
- “Run a difficult conversation / feedback / 1:1 / negotiation”
- “Plan a product strategy / vision / opportunity assessment”

Claude should NOT use this skill for:
- Book summaries, philosophy, or general education
- Long case studies or storytelling

---

## Quick Reference

| Task | Template | Domain | Output |
|------|----------|---------|---------|
| Discovery interview | `customer-interview-template.md` | Discovery | Interview script with Mom Test patterns |
| Opportunity mapping | `opportunity-solution-tree.md` | Discovery | OST with outcomes, problems, solutions |
| AI feature spec | `ai-lifecycle-template.md` | AI/Data | AI PM lifecycle doc with data, model, metrics |
| Agentic system design | `agentic-ai-orchestration.md` | AI/Data | Multi-agent workflow with tools, supervision |
| Outcome roadmap | `outcome-roadmap.md` | Roadmap | Now/Next/Later with outcomes and themes |
| OKR definition | `okr-template.md` | Metrics | 1-3 objectives with 2-4 key results each |
| Product positioning | `positioning-template.md` | Strategy | Competitive alternatives → value → segment |
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
    ├─ AI/LLM Product?
    │   ├─ Single AI feature? → AI lifecycle template
    │   ├─ Multi-agent system? → Agentic AI orchestration
    │   └─ Data product? → Data product canvas
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

## Navigation

**Resources**
- [resources/discovery-best-practices.md](resources/discovery-best-practices.md)
- [resources/roadmap-patterns.md](resources/roadmap-patterns.md)
- [resources/delivery-best-practices.md](resources/delivery-best-practices.md)
- [resources/strategy-patterns.md](resources/strategy-patterns.md)
- [resources/positioning-patterns.md](resources/positioning-patterns.md)
- [resources/ai-product-patterns.md](resources/ai-product-patterns.md)
- [resources/data-product-best-practices.md](resources/data-product-best-practices.md)
- [resources/interviewing-patterns.md](resources/interviewing-patterns.md)
- [resources/metrics-best-practices.md](resources/metrics-best-practices.md)
- [resources/leadership-decision-frameworks.md](resources/leadership-decision-frameworks.md)
- [resources/operational-guide.md](resources/operational-guide.md)
- [data/sources.json](data/sources.json)

**Templates**
- Discovery: [templates/discovery/customer-interview-template.md](templates/discovery/customer-interview-template.md), [templates/discovery/assumption-test-template.md](templates/discovery/assumption-test-template.md), [templates/discovery/opportunity-solution-tree.md](templates/discovery/opportunity-solution-tree.md)
- Strategy/Vision: [templates/strategy/product-vision-template.md](templates/strategy/product-vision-template.md), [templates/strategy/opportunity-assessment.md](templates/strategy/opportunity-assessment.md), [templates/strategy/positioning-template.md](templates/strategy/positioning-template.md), [templates/strategy/PRFAQ-template.md](templates/strategy/PRFAQ-template.md)
- AI/Data: [templates/ai/ai-lifecycle-template.md](templates/ai/ai-lifecycle-template.md), [templates/ai/agentic-ai-orchestration.md](templates/ai/agentic-ai-orchestration.md), [templates/data/data-product-canvas.md](templates/data/data-product-canvas.md)
- Roadmaps: [templates/roadmap/outcome-roadmap.md](templates/roadmap/outcome-roadmap.md), [templates/roadmap/theme-roadmap.md](templates/roadmap/theme-roadmap.md)
- Metrics: [templates/metrics/metric-tree.md](templates/metrics/metric-tree.md), [templates/metrics/okr-template.md](templates/metrics/okr-template.md)
- Ops/Leadership: [templates/ops/1-1-template.md](templates/ops/1-1-template.md), [templates/ops/feedback-template.md](templates/ops/feedback-template.md), [templates/ops/a3-debrief.md](templates/ops/a3-debrief.md), [templates/ops/negotiation-one-sheet.md](templates/ops/negotiation-one-sheet.md)

**Related Skills**
- [../product-prd-development/SKILL.md](../product-prd-development/SKILL.md) — PRD, stories, and prompt/playbook templates
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design guidance for specs and PRDs
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — UI implementation considerations for product specs
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Backend/API implications of product decisions

---

## Operational Guide

See [resources/operational-guide.md](resources/operational-guide.md) for detailed patterns, template walkthroughs, example flows, and execution checklists. Keep SKILL.md as the navigation hub; use templates/ when producing artifacts.

---

## External Resources

See [data/sources.json](data/sources.json) for official frameworks (Lean Startup, OST, PR/FAQ, OKRs) and AI/LLM safety references.

---

Use the quick reference and decision tree above to choose a template, then follow the operational guide for depth.
