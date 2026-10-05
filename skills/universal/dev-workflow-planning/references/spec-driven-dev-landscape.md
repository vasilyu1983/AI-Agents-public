# Spec-Driven Development Landscape

_Tool status, integrations, and pricing change often; check each tool's own docs before recommending one._

## Key Tools and Standards

**GitHub Spec Kit** — Open-source spec-driven development toolkit from GitHub. Announced 2025-09-02. Repo: github.com/github/spec-kit. Docs: github.github.com/spec-kit/. Ships a four-phase pipeline (Spec → Plan → Tasks → Implement), rich Markdown templates, and integrations for many AI coding agents (check the repo for the current list); switching agents does not lock in the spec. Provides structured spec templates and EARS notation integration.

**EARS (Easy Approach to Requirements Syntax)** — Established constrained-natural-language requirements notation. Pattern: `When <trigger> the <system> shall <response>`. Variants: Where/If/While/Ubiquitous. Reduces ambiguity in acceptance criteria; used in Spec Kit and AI-agent spec pipelines. Kiro generates `requirements.md` using EARS format natively. Sits alongside Gherkin as a complementary notation (EARS for requirements, Gherkin for executable test scenarios).

**Kiro** — AWS spec-driven AI IDE, launched mid-2025. Enforces spec-first pipeline: requirements (`requirements.md`, EARS format) → design (`design.md`) → tasks (`tasks.md`) → implementation. Represents the spec-gated agentic coding category. Adds agent hooks (event-driven background automations on save/create/delete), MCP support, and steering rules. Check kiro.dev/pricing for current tiers before quoting a price. Primary docs: kiro.dev.

**BMAD-METHOD** — Open-source agentic spec-driven framework (github.com/bmadcode/BMAD-METHOD). Orchestrates specialized AI agent roles such as Analyst, PM, Architect, Scrum Master, Developer, QA — each consuming the previous stage's spec output. Relevant as a planning-workflow pattern for multi-agent task decomposition where role separation is required across sessions.

## Landscape Summary

Many AI coding tools ship a spec-driven variant (examples: GitHub Spec Kit, AWS Kiro, Claude Code plan mode, OpenSpec, BMAD). The shared pattern: a machine-consumable Markdown spec contract (not just documentation) that agents re-parse across context resets.

## Workflow Implication

Spec-driven tools treat the planning artifact as a machine-consumable contract, not just documentation. When generating work items or acceptance criteria, EARS-formatted requirements reduce LLM reinterpretation variance across agent hand-offs. Each phase produces a Markdown artifact that feeds the next, giving an AI coding agent structured context instead of ad-hoc prompts.

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Platform Workflows](platform-workflows.md) — plan mode entry points per platform
- [Planning Templates](planning-templates.md) — parallel implementation plan template
