# Spec-Driven Development Landscape

_Product status, command sets, pricing, and popularity change quickly in this category. Check each project's repo or docs before quoting them._

## Key Tools and Standards

**GitHub Spec Kit** — open-source toolkit for spec-driven AI development, announced 2025-09-02 (GitHub Blog). Repo: github.com/github/spec-kit. Its flow runs constitution → specify → plan → tasks → implement as agent commands. Whether EARS-style requirements are built in or an extension is a lookup in the project's README.

**EARS (Easy Approach to Requirements Syntax)** — constrained-natural-language notation for unambiguous requirements, developed at Rolls-Royce (Mavin et al., 2009) and used across aerospace and defense. Pattern: `When <trigger> the <system> shall <response>`. Variants: Where/If/While/Ubiquitous. Its value for agents is that each clause names a trigger, a system, and a response, which removes prose ambiguity an agent would otherwise resolve by guessing.

**Kiro** — AWS spec-driven AI IDE/agent, announced 2025-07-14. Enforces a spec-first pipeline: requirements → design → tasks → implementation, with `requirements.md` (EARS-style), `design.md`, and `tasks.md` per spec; project-wide steering files and agent hooks carry standing context and automation.

**BMAD-METHOD** — open-source agentic spec-driven framework. Structures delivery into role-gated stages (Analyst → Architect → Developer → QA, plus further specialist roles); each role consumes the spec produced by the previous stage, not raw user intent.

**Lookup step before targeting one of these tools.** Check its repo or docs for the current command set and file layout, availability and pricing, and maintenance activity. Feed the answers into one decision: emit the spec in that tool's file layout, or in the tool-neutral order below.

## Pattern Implication for PRD Work

Spec-driven tools shift the PRD from a human-only artifact to a machine-consumable contract. Accept EARS-formatted acceptance criteria as a first-class input format. When generating specs for Kiro, Spec Kit, or BMAD-METHOD pipelines, structure output as: functional spec → technical spec → acceptance criteria → task list (in that order). Whichever tool consumes it, apply the ambiguity-class and testability judgment in the main [SKILL.md](../SKILL.md#expert-judgment-why-specs-fail-coding-agents) — spec-driven tooling enforces structure, not clarity; a well-formatted EARS clause can still contain referential or measurement ambiguity.
