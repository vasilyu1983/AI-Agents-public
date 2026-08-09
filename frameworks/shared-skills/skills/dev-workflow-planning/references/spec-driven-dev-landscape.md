# Spec-Driven Development Landscape

_All facts verified against primary sources. Last verified: 2026-07-11._

## Key Tools and Standards

**GitHub Spec Kit** — Open-source spec-driven development toolkit from GitHub. Announced 2025-09-02; star count is climbing fast (≈92k in early May 2026, ≈111k by mid-June 2026) — treat any fixed number as stale within weeks and check `star-history.com/github/spec-kit` for the current count rather than repeating one. Repo: github.com/github/spec-kit. Docs: github.github.com/spec-kit/. Ships a four-phase pipeline (Spec → Plan → Tasks → Implement), rich Markdown templates, and 30+ AI agent integrations (Copilot, Claude, Codex, Gemini, Windsurf, Kiro, and others). Switch between agents with one command; no lock-in. Provides structured spec templates and EARS notation integration.

**EARS (Easy Approach to Requirements Syntax)** — Established constrained-natural-language requirements notation. Pattern: `When <trigger> the <system> shall <response>`. Variants: Where/If/While/Ubiquitous. Reduces ambiguity in acceptance criteria; used in Spec Kit and AI-agent spec pipelines. Kiro generates `requirements.md` using EARS format natively. Sits alongside Gherkin as a complementary notation (EARS for requirements, Gherkin for executable test scenarios).

**Kiro** — AWS spec-driven AI IDE, launched mid-2025, powered by Claude via Amazon Bedrock. Enforces spec-first pipeline: requirements (`requirements.md`, EARS format) → design (`design.md`) → tasks (`tasks.md`) → implementation. Represents the spec-gated agentic coding category. Adds agent hooks (event-driven background automations on save/create/delete), MCP support, and steering rules. Pricing has shifted from a flat two-tier model to a multi-tier credit system: Free (50 credits/month), Pro ($20/month), plus higher Pro+/Pro Max/Power tiers — verify current tiers and prices at kiro.dev/pricing before quoting a figure, since this has already changed once since launch. Primary docs: kiro.dev.

**BMAD-METHOD** — Open-source agentic spec-driven framework (github.com/bmadcode/BMAD-METHOD). Orchestrates 12+ specialized AI agents: Analyst, PM, Architect, Scrum Master, Developer, QA — each consuming the previous stage's spec output. Relevant as a planning-workflow pattern for multi-agent task decomposition where role separation is required across sessions.

## Landscape Summary (2026-06)

Spec-driven development became the dominant agentic coding methodology in 2025-2026, with every major AI coding tool shipping a variant: GitHub Spec Kit, AWS Kiro, Claude Code (`/plan`, `/ultraplan`), Cursor, OpenSpec, BMAD, and others. The shared pattern: a machine-consumable Markdown spec contract (not just documentation) that agents re-parse across context resets.

## Workflow Implication

Spec-driven tools treat the planning artifact as a machine-consumable contract, not just documentation. When generating work items or acceptance criteria, EARS-formatted requirements reduce LLM reinterpretation variance across agent hand-offs. Each phase produces a Markdown artifact that feeds the next, giving an AI coding agent structured context instead of ad-hoc prompts.

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Platform Workflows](platform-workflows.md) — plan mode entry points per platform
- [Planning Templates](planning-templates.md) — parallel implementation plan template
