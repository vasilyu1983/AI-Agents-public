# Spec-Driven Development Landscape (2026-07)

_Verified 2026-07-11. All facts from verified primary and reputable secondary sources; star counts and product-status claims are high-volatility and should be re-checked live before quoting exact numbers._

## Key Tools and Standards

**GitHub Spec Kit** — Announced 2025-09-02 (GitHub Blog). Open-source toolkit for spec-driven AI development. Repo: github.com/github/spec-kit. Docs: github.github.com/spec-kit/. Growth: ~71k★ (Feb 2026) → ~111k★ (Jun 2026) — still growing fast; treat any star count as stale within weeks and re-check the repo directly rather than quoting this figure. Integrates EARS notation into AI-agent requirements workflows.

**EARS (Easy Approach to Requirements Syntax)** — Established constrained-natural-language notation for unambiguous requirements, developed at Rolls-Royce (2009), with adoption across aerospace, defense, and now AI-agent spec tooling. Pattern: `When <trigger> the <system> shall <response>`. Variants: Where/If/While/Ubiquitous. Reduces LLM hallucination risk in spec interpretation by removing prose ambiguity.

**Kiro** — AWS spec-driven AI IDE/agent, publicly announced 2025-07-14 and made generally available internationally in 2026 after an early-access phase. Enforces a spec-first pipeline: requirements → design → tasks → implementation. AWS has positioned Kiro as the successor to Amazon Q Developer (Q Developer end-of-support communicated for April 2027), signaling spec-gated agentic IDEs are becoming a first-class AWS product line, not a side experiment. Verify current pricing, model access, and GA scope at kiro.dev before quoting specifics — this category is moving faster than this reference can track.

**BMAD-METHOD** — Open-source agentic spec-driven framework. Repo moved to github.com/bmad-code-org/BMAD-METHOD (previously bmadcode/BMAD-METHOD — update any saved links). ~37k★ (Feb 2026) → ~50k★ (Jun 2026). Structures delivery into role-gated stages: Analyst → Architect → Developer → QA, plus additional specialized agent roles (PM, UX) in recent releases. Each agent role consumes the spec produced by the previous stage, not raw user intent.

## Pattern Implication for PRD Work

Spec-driven tools shift the PRD from a human-only artifact to a machine-consumable contract. Accept EARS-formatted acceptance criteria as a first-class input format. When generating specs for Kiro, Spec Kit, or BMAD-METHOD pipelines, structure output as: functional spec → technical spec → acceptance criteria → task list (in that order). Whichever tool consumes it, apply the ambiguity-class and testability judgment in the main [SKILL.md](../SKILL.md#expert-judgment-why-specs-fail-coding-agents) — spec-driven tooling enforces structure, not clarity; a well-formatted EARS clause can still contain referential or measurement ambiguity.
