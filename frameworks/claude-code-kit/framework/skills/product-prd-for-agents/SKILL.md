---
name: product-prd-for-agents
description: Write PRDs and specs optimized for AI coding agents (Claude Code, Cursor, Copilot). Templates, checklists, and patterns for creating product requirements that AI agents can execute effectively with minimal ambiguity.
---

# PRDs for AI Coding Agents — Quick Reference

Write product requirements that AI coding agents can execute effectively. This skill provides **templates, checklists, and workflow patterns** for creating PRDs, specs, and stories optimized for Claude Code, Cursor, Copilot, and other GenAI coding tools.

**Key difference from traditional PRDs**: AI agents need explicit context, clear boundaries, and unambiguous acceptance criteria to produce quality code.

---

## When to Use This Skill

Claude (or other agents) should invoke this skill when a user asks about:

**AI-Assisted Development (Primary):**
- Setting up or running AI/agentic coding workflows
- Creating/validating software with LLM agents (e.g., "How do I plan a GenAI coding session?")
- Productionizing GenAI-assisted code (prompt patterns, QA checklists, reviews)
- Progressive disclosure, test-driven/agentic loops, prompt engineering
- Requesting PRD/spec/story map templates for agentic or AI-driven projects

**Traditional Product Management (New):**
- Learning traditional PRD structure and best practices
- Writing specs for human PM teams (discovery interviews, stakeholder alignment)
- Writing technical specifications for engineering teams
- Cross-functional collaboration (PM, design, engineering, leadership)

**Note**: For API design patterns, use the [foundation-api-design](../foundation-api-design/SKILL.md) skill. For general technical documentation (README, ADRs, changelogs), use the [foundation-documentation](../foundation-documentation/SKILL.md) skill.

---

## Quick Reference

| Task | Template | Tool/Framework | When to Use |
|------|----------|----------------|-------------|
| PRD creation | `prd-template.md` | Standard PRD format | Writing product requirements document |
| Tech spec | `tech-spec-template.md` | Technical specification | Engineering-focused design doc |
| Agentic session | `agentic-session-template.md` | Claude Code, Cursor | Planning AI coding session (>3 files) |
| Planning checklist | `planning-checklist.md` | Pre-flight checklist | Before starting complex feature |
| Prompt playbook | `prompt-playbook.md` | Structured prompts | Repeatable AI-assisted development |
| Story mapping | `story-mapping-template.md` | User journey visualization | Breaking down features into user flows |
| Gherkin/BDD | `gherkin-example-template.md` | Cucumber, SpecFlow | Acceptance criteria for testing |
| Metrics tracking | `agentic-coding-metrics-template.md` | Velocity, ROI, quality | Measuring AI coding effectiveness |

---

## Decision Tree: Choosing Development Workflow

```text
User needs: [Development Task Type]
    ├─ AI-Assisted Coding?
    │   ├─ Non-trivial feature (>3 files)? → Use planning checklist + agentic session template
    │   ├─ Prompt engineering? → Prompt playbook (structured prompts)
    │   ├─ Measuring ROI? → Metrics tracking template
    │   └─ Simple task (<3 files)? → Direct implementation (no planning)
    │
    ├─ Traditional PM Deliverables?
    │   ├─ Product requirements? → PRD template
    │   ├─ Technical design? → Tech spec template
    │   ├─ User stories? → Story mapping template
    │   └─ Acceptance criteria? → Gherkin/BDD template
    │
    ├─ Cross-Domain Needs?
    │   ├─ API design? → Use [foundation-api-design](../foundation-api-design/SKILL.md) skill
    │   ├─ Architecture? → Use [software-architecture-design](../software-architecture-design/SKILL.md) skill
    │   ├─ Testing strategy? → Use [testing-automation](../testing-automation/SKILL.md) skill
    │   └─ Documentation? → Use [foundation-documentation](../foundation-documentation/SKILL.md) skill
    │
    └─ Workflow Phase?
        ├─ Planning → Planning checklist + agentic session
        ├─ Implementation → Structured prompts + self-review QA
        ├─ Validation → Testing + acceptance criteria
        └─ Handoff → Update docs + summarize changes
```

---

## Navigation

**Resources**
- [resources/agentic-coding-best-practices.md](resources/agentic-coding-best-practices.md)
- [resources/vibe-coding-patterns.md](resources/vibe-coding-patterns.md)
- [resources/prompt-engineering-patterns.md](resources/prompt-engineering-patterns.md)
- [resources/requirements-checklists.md](resources/requirements-checklists.md)
- [resources/traditional-prd-writing.md](resources/traditional-prd-writing.md)
- [resources/pm-team-collaboration.md](resources/pm-team-collaboration.md)
- [resources/security-review-checklist.md](resources/security-review-checklist.md) — AI coding security best practices
- [resources/tool-comparison-matrix.md](resources/tool-comparison-matrix.md) — Claude Code vs Copilot vs Cursor comparison
- [resources/operational-guide.md](resources/operational-guide.md) — Deep patterns, QA gates, and external sources
- [data/sources.json](data/sources.json)

**Templates**
- PRD/spec: [templates/prd/prd-template.md](templates/prd/prd-template.md), [templates/spec/tech-spec-template.md](templates/spec/tech-spec-template.md)
- Planning: [templates/planning/planning-checklist.md](templates/planning/planning-checklist.md), [templates/planning/agentic-session-template.md](templates/planning/agentic-session-template.md)
- Prompting: [templates/prompting/prompt-playbook.md](templates/prompting/prompt-playbook.md), [templates/prompting/structured-prompt-examples.md](templates/prompting/structured-prompt-examples.md)
- Stories: [templates/stories/story-mapping-template.md](templates/stories/story-mapping-template.md), [templates/stories/gherkin-example-template.md](templates/stories/gherkin-example-template.md)
- Metrics: [templates/metrics/agentic-coding-metrics-template.md](templates/metrics/agentic-coding-metrics-template.md) — Performance tracking & ROI

**Related Skills**

- [../quality-documentation-audit/SKILL.md](../quality-documentation-audit/SKILL.md) — Audit existing codebases for documentation gaps, generate coverage reports
- [../product-management/SKILL.md](../product-management/SKILL.md) — Broader product strategy, positioning, and leadership templates
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design patterns for specs and PRDs
- [../testing-automation/SKILL.md](../testing-automation/SKILL.md) — Testing strategy for AI-generated code and specs
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Review checklists for AI-assisted changes
- [../foundation-api-design/SKILL.md](../foundation-api-design/SKILL.md) — RESTful API design, OpenAPI specs, and API documentation
- [../foundation-documentation/SKILL.md](../foundation-documentation/SKILL.md) — Technical documentation (README, ADRs, changelogs, runbooks)
- [../foundation-git-workflow/SKILL.md](../foundation-git-workflow/SKILL.md) — Git workflows, branching strategies, and commit conventions
- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) — UI/UX patterns and design system best practices

---

## Operational Guide

See [resources/operational-guide.md](resources/operational-guide.md) for best practices, agentic workflows, prompt hygiene, QA gates, templates, and external sources. Use SKILL.md for navigation; dive into resources/templates for execution details.

---

## When to Use This Skill vs. Related Skills

**Use product-prd-development when:**

- Building features with AI coding agents (Claude Code, Cursor, Copilot)
- Writing PRDs for agentic or traditional development
- Need templates for planning, prompting, or story mapping
- Integrating GenAI into software development workflows

**Use [product-management](../product-management/SKILL.md) when:**

- Defining product strategy, positioning, or go-to-market
- Working on data product frameworks or AI product patterns
- Need broader business and leadership templates

**Use [software-architecture-design](../software-architecture-design/SKILL.md) when:**

- Designing system architecture for specs and PRDs
- Need architectural decision records (ADRs)
- Working on scalability, reliability, or technical design

**Use [foundation-api-design](../foundation-api-design/SKILL.md) when:**

- Designing RESTful APIs or OpenAPI specifications
- Need API documentation templates
- Working on API versioning, authentication, or error handling

**Use [testing-automation](../testing-automation/SKILL.md) when:**

- Creating test strategies for AI-generated code
- Need testing frameworks or automation patterns
- Working on test coverage, CI/CD, or quality gates

---

Use the quick reference and decision tree above, then rely on the operational guide for execution checklists and QA gates.
