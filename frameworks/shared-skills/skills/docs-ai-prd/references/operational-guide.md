# Operational Guide

Operational patterns, checklists, and reference material for agentic coding and PRD development.

---

## Resources (Best Practices)

### AI-Assisted Development
- **Agentic Coding**: [agentic-coding-best-practices.md](agentic-coding-best-practices.md)
- **Vibe Coding Patterns**: [vibe-coding-patterns.md](vibe-coding-patterns.md)
- **Prompt Engineering**: [prompt-engineering-patterns.md](prompt-engineering-patterns.md)
- **Requirements & Validation**: [requirements-checklists.md](requirements-checklists.md)
- **Security Review**: [security-review-checklist.md](security-review-checklist.md) - AI coding security (prompt injection, code gen, dependencies)
- **Tool Comparison Matrix**: [tool-comparison-matrix.md](tool-comparison-matrix.md) - Claude Code vs Copilot vs Cursor vs Windsurf (2025)

### Traditional Product Management
- **Traditional PRD Writing**: [traditional-prd-writing.md](traditional-prd-writing.md) - Comprehensive guide for writing PRDs for human teams
- **PM Team Collaboration**: [pm-team-collaboration.md](pm-team-collaboration.md) - Discovery interviews, stakeholder alignment, cross-functional workflows

**AI-Assisted Development Resources** contain step-by-step workflows, planning/QA/self-review checklists, collaboration patterns, decision matrices (prompt vs plan, agent vs manual), and anti-patterns.

**Traditional PM Resources** cover PRD structure, discovery interview scripts, user personas, requirements writing, metrics frameworks, and quality checklists.

---

## Core Operational Patterns

### Agentic Coding Four-Phase Workflow
1. **Planning** — Enter planning mode for non-trivial features (>3 files or >2 unknowns); capture goal, phases, tasks, risks, metrics. See `agentic-coding-best-practices.md#planning-readiness-checklist`.
2. **Implementation** — Work in increments; update task list; self-review after each phase (`agentic-coding-best-practices.md#agentic-coding-qa-checklist`).
3. **Validation** — Run tests; validate against acceptance criteria; multi-layer review (agent + human).
4. **Handoff** — Summarize changes, flag risks, suggest next steps; update docs when architecture shifts.

### Prompt Engineering Hygiene
- [ ] Use structured prompts for repeatable results
- [ ] Provide relevant context beyond code
- [ ] Limit each prompt to a single task
- [ ] Make instructions specific and clear
- [ ] Keep prompts concise
- [ ] Validate model output before copy-paste

### QA Gates for AI-Generated Code

| Phase | Checklist | Owner |
|-------------------|---------------------------------------------------------------------|---------------|
| Planning | All tasks/risks/acceptance criteria specified? | Human/Agent |
| Implementation | Code runs/tests locally? Self-review for edge cases? | Agent |
| Validation | All acceptance criteria met? No security/test regressions? | Agent/Human |
| Handoff | Changes summarized, docs updated, next steps documented? | Agent/Human |

### Quick Reference: Common Patterns
- **Agentic Loop**: Plan → Tool call → Output → Feedback → Refine (repeat)
- **Story Mapping**: Big steps left–right, details top–bottom. Use as backlog for agentic workflows.
- **Specification by Example**: Use Given-When-Then for requirements and tests; automate where possible.
- **Progressive Disclosure**: Start with SKILL.md overview, drill into references/ only when needed
- **Test-Driven Agentic**: Write tests first, let agent implement, validate against acceptance criteria
- **Anti-Patterns**: Copy-pasting output without validation; skipping planning; mixing theory with operational checklists; no acceptance criteria; over-engineering

---

## Templates (Copy-Paste Ready)

- **PRD & Tech Specs**: `assets/prd/prd-template.md`, `assets/spec/tech-spec-template.md`
- **Planning & Checklist**: `assets/planning/planning-checklist.md`, `assets/planning/agentic-session-template.md`
- **Prompt Engineering**: `assets/prompting/prompt-playbook.md`, `assets/prompting/structured-prompt-examples.md`
- **User Stories & Story Maps**: `assets/stories/story-mapping-template.md`, `assets/stories/gherkin-example-template.md`
- **Performance Metrics & ROI**: `assets/metrics/agentic-coding-metrics-template.md`

---

## External Resources

See `../data/sources.json` for curated sources:
- Agentic coding & AI tools: Claude Code, Cursor, Copilot documentation; vibe coding guides (2024-2025); JetBrains AI agent patterns
- PRD frameworks: Product School, Atlassian, DigitalOcean guides; Aha!, Leanware templates
- Prompt engineering: OpenAI, Anthropic official guides; GPT-4.1/GPT-5 prompting cookbooks; developer playbooks
- Product management communities: Product Hunt, Mind the Product
- Research tools: Anthropic/OpenAI playgrounds, Cursor telemetry dashboard
- Learning paths: FreeCodeCamp AI engineering, Coursera AI PM specialization

---

## Success Criteria

- Code or doc can be copy-pasted and executed/applied as-is
- All checklists are actionable, not descriptive
- Every pattern includes a quick "when-to-use" or decision rule
- Resources focus on operational content, not theory
- Templates are organized by domain and technology stack

> All theory/explanations must be converted into actionable patterns, templates, or checklists.
