# Context-Engineering Framework Selection Matrix (April 2026)

How to pick between the major context-engineering frameworks active in April 2026 — and how they stack without fighting each other.

## Table of Contents

- [The four-layer model](#the-four-layer-model)
- [Decision matrix — pick by symptom](#decision-matrix--pick-by-symptom)
- [Layering matrix — what each replaces vs extends](#layering-matrix--what-each-replaces-vs-extends)
- [Stack recipes](#stack-recipes)
- [Anti-stacks](#anti-stacks)
- [Maturity signals](#maturity-signals)
- [Sources](#sources)

## The four-layer model

The April 2026 landscape resolves cleanly into four layers. A team chooses *one* answer per layer; conflicts within a layer cause drift, but layers stack cleanly.

| Layer | Role | What it produces |
|-------|------|------------------|
| **L0 portable baseline** | Cross-tool conventions every agent reads | A single Markdown file at the repo root that all agents pick up natively |
| **L1 runtime-specific** | Tool-specific extensions for a single CLI/IDE | Per-tool config: `.claude/rules/`, `.codex/agents/`, `.cursor/rules/`, `.github/copilot-instructions.md`, `.clinerules/` |
| **L2 capability / methodology** | On-demand capabilities or enforced workflow discipline | Skills, plugins, hooks — load conditionally and gate behavior |
| **L3 artifact pipeline** | Spec → plan → tasks → code as committed artifacts | A `specs/` or `changes/` directory with structured documents |

L0 is mandatory. L1 is mandatory if a tool refuses to read AGENTS.md. L2 is optional, useful when discipline drift or context rot is the bottleneck. L3 is optional, useful when feature ambiguity is the bottleneck.

## Decision matrix — pick by symptom

Read the left column as "the thing my team is currently failing at." Pick exactly one framework per row.

| Symptom | Pick | Why this and not the others |
|---------|------|----------------------------|
| Conventions drift across Codex / Claude Code / Cursor | **AGENTS.md** | The only L0 artifact all major tools read natively as of April 2026; LF-stewarded |
| Agent ignores TDD, debugs sloppily, skips brainstorming | **superpowers** | Skills *enforce* discipline at runtime (refuse-to-code-until-clarified); AGENTS.md is passive |
| Long sessions degrade — context rot, agent forgets earlier decisions | **GSD (get-shit-done)** | Built specifically for context rot: fresh subagent dispatch + `PROJECT.md` / `ROADMAP.md` / `STATE.md` planning artifacts |
| Feature ambiguity causes drift; specs and code drift apart | **GitHub Spec Kit** | Spec → plan → tasks → code artifact pipeline; `.specify/specs/<feature>/`; most-cited and GitHub-backed |
| Same need as Spec Kit but want lighter / npm-native + ADRs co-located | **OpenSpec** (Fission-AI) | `openspec/changes/`, npm install, integrates ADRs alongside specs |
| Repeated domain expertise (PDF / Excel / internal DSL) bloats AGENTS.md | **Claude Code Skills** | Progressive disclosure: ~100-token metadata always-on, instructions on trigger, scripts on demand |
| GitHub Copilot users need persistent project rules | **`.github/copilot-instructions.md`** | Only instruction layer Copilot reads natively; path-scoped via `.instructions.md` with `applyTo` |
| Cursor IDE users need scoped rules per file/dir | **`.cursor/rules/*.mdc`** | YAML frontmatter activation; legacy `.cursorrules` deprecated |
| Cline (VS Code) workflows | **`.clinerules/`** | Toggle UI per rule; rules-bank pattern |
| Aider pair-programming sessions | **`CONVENTIONS.md`** | Loaded every session via `.aider.conf.yml` |

## Layering matrix — what each replaces vs extends

| Framework | Layer | Repo location | Composes with AGENTS.md | Install path |
|-----------|-------|---------------|-------------------------|--------------|
| **AGENTS.md** | L0 | `/AGENTS.md` (+ subdir overlays) | — *is* the baseline | File only |
| **CLAUDE.md / `.claude/rules/`** | L1 | `/CLAUDE.md`, `.claude/rules/*.md` | Extends (Claude-only behavior) | File only |
| **`.codex/agents/*.toml`** | L1 | `.codex/agents/` | Extends (Codex parallel workers) | File only |
| **`.cursor/rules/*.mdc`** | L1 | `.cursor/rules/` | Parallel — Cursor does not read AGENTS.md | File only |
| **`.github/copilot-instructions.md`** | L1 | `.github/` | Parallel — Copilot does not read AGENTS.md | File only |
| **`.clinerules/`** | L1 | `/.clinerules/` | Parallel | File only |
| **CONVENTIONS.md (Aider)** | L1 | configurable | Parallel | Config flag |
| **Claude Code Skills** | L2 | `~/.claude/skills/` or `.claude/skills/` | Extends (on-demand, doesn't bloat hot layer) | Plugin or filesystem |
| **superpowers** (obra/superpowers) | L2 | `.claude/`, `.cursor/`, `.opencode`, etc. | Extends (multi-runtime via plugin configs) | Anthropic plugin marketplace |
| **GSD** (gsd-build/get-shit-done) | L2 | `~/.claude/` or `./.claude/` | Extends (skills + subagents + git hooks) | `npx get-shit-done-cc@latest` |
| **GitHub Spec Kit** | L3 | `.specify/specs/<feature>/` | Orthogonal — produces docs that feed any agent | `uv tool install specify-cli` |
| **OpenSpec** (Fission-AI) | L3 | `openspec/changes/` | Orthogonal | `npm i -g @fission-ai/openspec` |

## Stack recipes

| Team profile | Recommended stack |
|--------------|-------------------|
| Solo dev, single repo, single tool | AGENTS.md only. Add Spec Kit if features ship with ambiguity. |
| Solo dev, Claude Code primary | AGENTS.md + Claude Code Skills (on-demand) + superpowers if drift recurs |
| Small team, mixed tools (Claude + Codex + Cursor) | AGENTS.md (baseline) + thin runtime layers + Spec Kit for feature work |
| Long-running project / monorepo / multi-phase | AGENTS.md + GSD (context-rot is the bottleneck) + Spec Kit for new features |
| Regulated / enterprise (audit, separation of duties) | AGENTS.md + `.claude/rules/` + Spec Kit (auditable artifacts) + governance gates from this skill's `assets/` directory |
| Cursor-primary IDE shop | `.cursor/rules/*.mdc` + AGENTS.md mirror + Spec Kit |
| GitHub Copilot shop | `.github/copilot-instructions.md` + AGENTS.md mirror + Spec Kit |

## Anti-stacks

Combinations that fight each other and should not be deployed together without explicit scoping.

| Don't | Reason | Mitigation if you must |
|-------|--------|-------------------------|
| superpowers + GSD without scoping | Both ship skills/subagents — overlap on planning, debugging | Namespace via `/sp:` vs `/gsd:` slash prefixes; pick a dominant one for each workflow |
| Spec Kit + OpenSpec on the same repo | Two competing spec stores; agents won't know which is canonical | Pick one; if migrating, archive the other under `.archive/` |
| Conventions duplicated in AGENTS.md + `.cursor/rules` + `.clinerules` + `copilot-instructions.md` | Drift inevitable across four parallel files | Write once in AGENTS.md or `docs/`; tool-specific layers reference, never duplicate |
| Claude Code Skills used for always-on policy | Defeats progressive disclosure — that policy belongs in AGENTS.md / `.claude/rules/` | Move always-on rules to L0/L1; keep skills for capability that *should* load conditionally |
| Hot AGENTS.md carrying methodology enforcement (TDD, debugging discipline) | Passive text doesn't enforce; just bloats the hot layer | Move enforcement to L2 (superpowers or custom skills) |

## Maturity signals

April 2026 snapshot of adoption signals. Stars and adoption are noisy — use as a sanity check, not as a buy decision.

| Framework | Adoption signal | Backing |
|-----------|----------------|---------|
| AGENTS.md | 67% of active repos contain `CLAUDE.md` / `AGENTS.md` / equivalent (Greptile State of AI Coding 2025) | Linux Foundation (Agentic AI Foundation) |
| GitHub Spec Kit | ~92k stars; v0.8.4 May 2026; 30+ supported agents | GitHub official |
| superpowers (obra/superpowers) | ~150–175k stars; v5.0.7 March 2026; 14 documented skills | Anthropic plugin marketplace listed |
| GSD (gsd-build/get-shit-done) | ~59k stars; v1.39.0; 59 skills + 33 subagents in full mode | Independent (`gsd-build` org) |
| Claude Code Skills | Official Anthropic product; reference catalog at `anthropics/skills` | Anthropic |
| OpenSpec (Fission-AI) | Smaller but actively maintained; integrates ADRs; npm package | Fission-AI community |
| Cursor rules `.cursor/rules/*.mdc` | Standardized 2025; widely adopted | Cursor (commercial) |
| Copilot instructions | GA; path-specific instructions added July 2025; agent-specific November 2025 | GitHub official |
| Cline rules | Stable feature; v3.13 toggle UI 2025 | Cline (open source) |
| Aider conventions | Mature, documented behavior change in code output | Aider (open source) |

## Sources

External source mapping for this matrix lives in [data/sources.json](../data/sources.json) under the entries: `agents.md spec`, `GitHub spec-kit`, `obra/superpowers`, `gsd-build/get-shit-done`, `Fission-AI/OpenSpec`, `Anthropic Agent Skills overview`, `cursor.com/docs/rules`, `Cline rules docs`, `Aider conventions docs`.

Use the maturity-signal numbers in this file as a snapshot, not a tracking signal — re-verify before any procurement or migration decision. Star counts and skill counts move month-to-month; the layer model and the decision matrix are the durable parts of this reference.
