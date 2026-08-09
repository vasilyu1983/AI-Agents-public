# Skill Patterns

Use these patterns to keep skills small, navigable, and scoped to the runtime they actually target.

## Table of Contents

- [Pattern 1: Portable Core Skill](#pattern-1-portable-core-skill)
- [Pattern 2: Runtime-Scoped Skill](#pattern-2-runtime-scoped-skill)
- [Pattern 3: Multi-Variant Skill](#pattern-3-multi-variant-skill)
- [Pattern 4: Workflow Skill](#pattern-4-workflow-skill)
- [Pattern 5: Script-Backed Skill](#pattern-5-script-backed-skill)
- [Pattern 6: Eval-Driven Skill](#pattern-6-eval-driven-skill)
- [Pattern 7: Stateful Skill](#pattern-7-stateful-skill)
- [Pattern 8: Self-Bootstrapping Skill](#pattern-8-self-bootstrapping-skill)
- [Pattern 9: Composable Skill](#pattern-9-composable-skill)
- [Pattern 10: Stage-Based Selection Pipeline](#pattern-10-stage-based-selection-pipeline)
- [Naming Rules](#naming-rules)
- [Anti-Patterns](#anti-patterns)

## Pattern 1: Portable Core Skill

Use when the skill should stay reusable across runtimes.

```text
skill-name/
├── SKILL.md
├── data/
│   └── sources.json
└── references/
    └── workflow.md
```

Characteristics:

- The required portable fields are `name` and `description`
- `license`, `compatibility`, and `metadata` stay available as portable optional fields
- `allowed-tools` can be used when the target runtime supports it
- `SKILL.md` teaches the workflow
- references hold detail without assuming a specific runtime extension model

## Pattern 2: Runtime-Scoped Skill

Use when the skill depends on runtime-specific headers or behavior.

```text
skill-name/
├── SKILL.md
├── references/
│   ├── workflow.md
│   └── runtime-notes.md
└── data/
    └── sources.json
```

Required conventions:

- Add a `compatibility` note naming the target runtime
- Keep the portable core visible first
- Put runtime-specific behavior in a clearly labeled section or reference file

## Pattern 3: Multi-Variant Skill

Use when one skill supports multiple frameworks, stacks, or domains.

```text
software-backend/
├── SKILL.md
├── references/
│   ├── nodejs.md
│   ├── python.md
│   ├── go.md
│   └── rust.md
└── assets/
    ├── nodejs/
    └── python/
```

Keep in `SKILL.md`:

- selection guidance
- decision tree
- shared workflow

Move to references:

- stack-specific setup
- code examples
- migration notes

## Pattern 4: Workflow Skill

Use when consistent sequence matters more than static reference value.

```text
skill-name/
├── SKILL.md
├── references/
│   ├── phase-1.md
│   ├── phase-2.md
│   └── review-checklist.md
└── assets/
    └── template.md
```

Good fit:

- planning workflows
- review workflows
- incident response or rollout checklists

## Pattern 5: Script-Backed Skill

Use when the same deterministic helper would otherwise be rewritten every time.

```text
skill-name/
├── SKILL.md
├── scripts/
│   ├── validate.py
│   └── generate.py
└── references/
    └── script-usage.md
```

Use scripts for:

- validation
- scaffolding
- conversions
- scoring

Rule:

- prefer running a trusted helper over re-describing it in long prose

## Pattern 6: Eval-Driven Skill

Use when trigger quality or navigation behavior matters as much as content.

```text
skill-name/
├── SKILL.md
├── references/
│   └── evaluation.md
└── scripts/
    ├── validate.py
    └── test_validate.py
```

Good fit:

- router skills
- meta skills
- skills with many adjacent trigger domains

If the skill also publishes an effectiveness claim (a "this saves N% tokens" or "this improves quality" line in its own `SKILL.md` or README), that is a different eval axis than trigger/navigation quality — see `skill-validation.md` → [Effectiveness-Claim Eval Design](skill-validation.md#effectiveness-claim-eval-design) for control-arm design and honest-numbers disclosure.

### Adjustable Strictness: One Persistent Dial, Not Many Toggles

**Source**: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), commit `2ed6c52c9d7e5e56942508591085fd45dea277d3`, MIT license. Pattern extracted 2026-08-09; see `docs/research/2026-08-09-skill-ponytail-scan.md` in this repo for the full scan.

If a skill's behavior needs to vary in aggressiveness for the same task (a review skill that can be lenient or strict, a compression skill that can be light or heavy), expose that as **one named, persistent intensity level** — e.g. `lite` / `full` / `ultra` — set once (a slash-command argument or a session-scoped setting) rather than as several independent binary flags or a flag repeated on every invocation. A single ordered dial keeps the skill's behavior space small and lets a worked example show the same request at each level; scattered toggles multiply combinations the author never tested and the user never asked for.

This is a skill-authoring UX pattern, not a coding-behavior rule — it governs how one skill's own strictness surface is exposed, not a cross-skill contract. Do not add an intensity dial to `coding-behavior.md` itself: dials add branching complexity on top of the rule count that file's own compliance-engineering guidance already warns against (see `agents-memory/references/coding-behavior.md` → Compliance Engineering). Keep the dial local to the skill that needs adjustable strictness.

## Naming Rules

Good:

- `software-backend`
- `qa-agent-testing`
- `agents-skills`

Bad:

- `programming`
- `backend-help`
- `express-middleware-error-handling-async`

Practical rules:

- keep names short and specific
- prefer stable names over trend-driven renames
- if the bundle is vendor-specific, say so in the description or compatibility note rather than bloating the name

## Pattern 7: Stateful Skill

Use when a skill needs to remember things across sessions.

```text
skill-name/
├── SKILL.md
├── references/
│   └── state-schema.md
└── scripts/
    └── migrate.sh
```

State storage options (in `${CLAUDE_PLUGIN_DATA}/`):

- **Append-only log** (`.log`): simplest, good for audit trails and usage tracking
- **JSON file** (`.json`): good for configuration and small structured state
- **SQLite** (`.db`): good when you need queries, aggregation, or relational data

Rules:

- always degrade gracefully when state is missing (first run, cleared cache)
- never store secrets in state files — use environment variables
- document the state schema in references so maintainers understand what is persisted
- treat state as cache, not source of truth

## Pattern 8: Self-Bootstrapping Skill

Use when a skill requires one-time setup before it can operate.

```text
skill-name/
├── SKILL.md
├── scripts/
│   └── setup.sh
└── references/
    └── config-schema.md
```

Flow:

1. Skill activates
2. Checks for `${CLAUDE_PLUGIN_DATA}/config.json`
3. If missing → runs setup flow (prompts user for required values)
4. Writes config
5. Subsequent activations read config silently

Good fit:

- skills that need API keys, project IDs, or org-specific defaults
- skills that connect to external services requiring authentication
- skills where sensible defaults vary by team or project

Keep the setup flow short (3-5 questions maximum). Offer sane defaults where possible.

## Pattern 9: Composable Skill

Use when a skill delegates to or sequences other skills.

```text
skill-name/
├── SKILL.md
└── references/
    └── delegation-map.md
```

Composition modes:

- **Delegation**: "For X, invoke skill Y" — the current skill hands off entirely
- **Sequencing**: "After completing A, also run skill B" — ordered pipeline
- **Conditional**: "If the change touches area Z, also load skill W" — context-aware loading

Rules:

- keep composition depth to 1 level (skill A → skill B, never A → B → C)
- document the delegation map explicitly in references
- each composed skill must be independently useful (no circular dependencies)
- the composing skill owns the workflow; composed skills own their domain

## Pattern 10: Stage-Based Selection Pipeline

Use when a skill, router, team guide, or workflow must choose between many possible routes, references, scripts, agents, or outputs.

This pattern is adapted from large recommendation pipelines such as X's open `x-algorithm`: keep candidate generation, enrichment, filtering, scoring, selection, validation, and side effects as separate stages instead of mixing them in one prose decision.

```text
request
  -> query/context hydration
  -> candidate sources
  -> candidate hydration
  -> eligibility filters
  -> independent scoring
  -> selector
  -> post-selection validation
  -> side effects
```

Stage contract:

| Stage | Skill meaning | Rule |
|-------|---------------|------|
| Query/context hydration | Restate goal, constraints, repo, runtime, risk, and available evidence | Add context only; do not choose yet |
| Sources | Generate candidate skills, routes, references, scripts, agents, or teams | Run independent sources in parallel when safe |
| Hydrators | Enrich candidates with metadata, owner, trigger fit, freshness, validation cost, and risk | Hydrators must not drop candidates |
| Filters | Remove ineligible candidates such as wrong domain, project-boundary violations, missing source, unsafe side effect, or stale volatile claim | Every removal needs a named reason |
| Scorers | Score remaining candidates against the request | Score each candidate independently before comparing |
| Selector | Choose the smallest correct route, team, reference, or output shape | Prefer bounded ownership over broad capability |
| Post-selection validation | Re-check isolation, portability, freshness, permissions, and user constraints after the choice | Block or downgrade the choice if a hard rule fails |
| Side effects | Record eval cases, append learnings, update catalogs, or propose memory changes | Side effects must not change the primary answer silently |

Good fits:

- router skills that choose domain ownership
- team-selection guides that choose agent/team/debate modes
- retrieval skills that select context packets
- documentation skills that decide what becomes canonical vs archived
- QA and review skills that triage evidence, risks, and next gates

Invariants:

- **Candidate isolation**: score each candidate against the request before letting alternatives influence the decision.
- **Hydration is non-destructive**: enrichment can add fields, but only filters can remove.
- **Parallel where independent, sequential where order matters**: sources and hydrators can fan out; filters, scorers, and final validation normally run in order.
- **Post-selection gates are real gates**: final selected outputs still need boundary, safety, and evidence checks.
- **Side effects are explicit**: learnings, eval fixtures, logs, and catalog updates happen after the primary decision and are reported separately.

## Real-World Skill Decomposition: career-ops

career-ops (github.com/santifer/career-ops) is a multi-agent job-search system built on Claude Code that uses 14 skill modes. It demonstrates how workflow skills decompose a complex domain.

**Decomposition strategy:** Each skill handles one phase of the job-search pipeline:

| Phase | Skill Responsibilities | Pattern Used |
|-------|----------------------|--------------|
| Discovery | Portal scanning, listing extraction across 45+ company sites | Script-Backed (Pattern 5) |
| Evaluation | A-F grading across 10 weighted dimensions, filtering below 4.0/5.0 | Workflow (Pattern 4) |
| Customization | ATS-optimized CV generation, cover letter tailoring per listing | Composable (Pattern 9) |
| Pipeline | Application tracking, interview prep, salary negotiation | Stateful (Pattern 7) |

**Lessons for skill authors:**

- 14 skills is manageable when each skill is narrowly scoped with clear input/output contracts
- Batch-parallel execution (10+ offers at once) works because skills are independent — no shared mutable state between evaluations
- The Go terminal dashboard acts as an orchestration layer above the skills, not inside them
- Skill count grew organically from 3 to 14 as the domain complexity revealed itself — do not pre-design all skills upfront

---

## Anti-Patterns

### One Big Spec

Bad:

- `SKILL.md` tries to act as the definitive spec for every runtime

Fix:

- portable core in `SKILL.md`
- runtime-specific notes in labeled sections or references

### Hidden Runtime Assumptions

Bad:

- a portable example quietly includes runtime-specific headers

Fix:

- move the example into a runtime-scoped section and add `compatibility`

### Reference Dumping

Bad:

- `references/` exists, but `SKILL.md` never tells the runtime when to read it

Fix:

- tell the runtime exactly which file to load for which task

### No Evals

Bad:

- the skill looks correct on disk but no one tested trigger quality

Fix:

- keep a minimum eval set for trigger, non-trigger, and navigation behavior

### Mixed Selection Stages

Bad:

- a router lists candidate skills, enriches them with context, rejects some, and picks a winner in one untraceable paragraph

Fix:

- use Pattern 10 and keep candidate sources, hydrators, filters, scorers, selector, post-selection validation, and side effects separate

## Related

- [frontmatter-reference.md](frontmatter-reference.md) - Header compatibility rules
- [skill-validation.md](skill-validation.md) - Validation workflow
- [../SKILL.md](../SKILL.md) - Main skill reference
