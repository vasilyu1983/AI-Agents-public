---
name: qa-refactoring
description: "Safe refactoring with behavior preservation. Use when reducing technical debt, planning codemods, applying strangler migrations, or tightening CI guardrails around risky changes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Refactoring

Use this skill to refactor safely: preserve behavior, reduce risk, and keep CI green while improving maintainability and delivery speed.

Defaults: baseline first, smallest safe step next, and proof via tests/contracts/observability instead of intuition.

## Quick Start (10 Minutes)

- If key context is missing, ask for: what must not change (invariants), risk level (money/auth/migrations/concurrency), deployment constraints, and the smallest boundary that can be protected by tests.
- Confirm baseline: `main` green; reproduce the behavior you must preserve.
- Choose a boundary: API surface, module boundary, DB boundary, request handler, or codemod blast radius.
- Add a safety net: characterization/contract/integration tests at that boundary.
- Refactor in micro-steps: one behavior-preserving change per commit/PR chunk.
- Prove: run the smallest relevant suite locally, then full CI; keep failures deterministic and artifact-rich.

## Workflow

1. Establish the safety net, boundaries, and rollback shape.
2. Choose the refactoring strategy and smallest change slice.
3. Make the change, verify behavior, and stop if the safety bar drops below acceptable risk.
4. Capture the next slice instead of expanding scope mid-pass.

## Core QA (Default)

### Safe Refactor Loop (Behavior First)

- Establish baseline: get `main` green; reproduce the behavior you must preserve.
- Define invariants: inputs/outputs, error modes, permissions, data shape, performance budgets.
- Add a safety net: write characterization/contract/integration tests around the boundary you will touch.
- Create seams: introduce injection points/adapters to isolate side effects and external dependencies.
- Refactor in micro-steps: one behavior-preserving change at a time; keep diffs reviewable.
- Prove: run the smallest relevant suite locally, then full CI; keep failures debuggable and deterministic.
- Ship safely: use canary, shadow mode, migration flags, or branch-by-abstraction when refactors touch production-critical paths.

### Risk Levels (Choose Safety Net)

| Risk | Examples | Minimum required safety net |
|------|----------|-----------------------------|
| Low | rename, extract method, formatting-only | unit tests + lint/type checks |
| Medium | moving logic across modules, dependency inversion, codemods with narrow blast radius | unit + integration/contract tests at boundary |
| High | auth/permission paths, concurrency, migrations, money/data-loss paths, large-scale automated rewrites | integration + contract tests, observability checks, rollout + rollback plan |

### Test Strategy for Refactors

- Prefer contract and integration tests around boundaries to preserve behavior.
- Use snapshots/golden masters only when outputs are stable and reviewed (avoid "approve everything" loops).
- For invariants, consider property-based tests or table-driven cases (inputs, edge cases, error modes).
- Avoid making E2E/UI tests the primary safety net for refactors; keep most safety below the UI.
- For flaky areas: fix determinism first (seeds, time, ordering, network) before trusting results.
- For API and service boundaries, prefer explicit contract tests over ad hoc end-to-end coverage.
- For automated rewrites, sample diffs manually before scaling to the full repository.

### CI Economics and Debugging Ergonomics

- Keep refactor PRs small and reviewable; avoid refactor + feature in one PR.
- Require failure artifacts for tests guarding refactors (logs, trace IDs, deterministic seeds, repro steps).
- Reduce diff noise: isolate formatting-only changes (or apply formatting repo-wide once with buy-in).
- Keep `git bisect` viable: avoid mixed "mechanical + semantic" changes unless necessary.
- For codemods, use dry runs first, then batch execution with a stop-on-failure path.

### Do / Avoid

Do:

- Add missing tests before refactoring high-risk areas.
- Add guardrails (linters, type checks, contract checks, static analysis/security checks) so refactors don't silently break interfaces.
- Prefer "branch by abstraction" / adapters when you need to swap implementations safely.
- Prefer compiler-aware and AST-aware refactors over regex edits when touching many files.
- Treat "more than ~500 lines touched by hand" as a second, line-count trigger for the same automate-vs-manual decision the file-count table in [references/automated-refactoring-tools.md](references/automated-refactoring-tools.md#when-ide-refactoring-is-sufficient) already makes on file count — a refactor can cross one threshold without the other (a single 2,000-line file is one file; a 600-file mechanical rename can be a few lines each), so check both axes, not just files.

Avoid:

- Combining large structural refactors with behavior changes.
- Using flaky E2E as the primary safety net for refactors.
- Treating arbitrary size thresholds as rules of nature; use both the file-count and line-count thresholds above only as review heuristics that prompt "should this be a codemod," not as hard gates — the decision is whether automation is safer than hand-editing at this scale, not compliance with a number.

The line-count trigger is adapted from addyosmani/agent-skills (MIT), commit `7676817`, 2026-08-09.

## Expert Judgment: What a Checklist Misses

### When NOT to Refactor

Refactoring is an investment decision, not a moral obligation — weigh it like one.

- Ask what the refactor buys (velocity, defect reduction, unblocking a specific feature) against what it costs (time, review load, regression risk) before starting. "This code is ugly" is not a business case by itself.
- Do not refactor stable, rarely-touched code that is scheduled for retirement or replacement — cleaning up code you are about to delete is waste. Check the migration roadmap before investing.
- Prioritize by hotspot (churn × complexity), not raw LOC or aesthetic discomfort. A messy function nobody touches is lower priority than a merely-average function that changes every sprint.
- Apply Kent Beck's framing from *Tidy First?* (2023): tidy first only when the tidying pays for itself in the change you are about to make — it shrinks the diff, de-risks it, or reveals the real shape of the work. If a tidying does not unlock the change you actually need, defer it to its own reviewed, low-stakes commit rather than bundling it in "while I'm here."
- If a strangler-fig migration will replace this module within the current roadmap horizon, put the investment into seams and characterization tests for the migration, not into deep internal refactors of code that is going away.

### Characterization-Test-First Discipline

- "I understand this code" is not a safety net — write the test, not just the belief. If you cannot state what a function returns for its three trickiest inputs without running it, you do not understand it well enough to skip characterization tests.
- Characterization tests capture behavior *including bugs*. Do not silently fix bugs while characterizing — log discovered bugs separately and let the product owner decide fix timing and sequencing relative to the refactor.
- Chesterton's Fence applies to deletion specifically: before removing code that looks unused or wrong, `git blame`/`git log -p` the lines to find the commit and linked ticket/PR that added them, and check for a comment explaining the rationale. Only delete once you can state why the fence was put up, not just that you can't currently see a reason for it.

### Behavior-Preservation Verification Strategies

- Verify in layers, cheapest first: type check → lint → unit/characterization → contract/integration → mutation-score gate on the touched boundary → canary/shadow for production-critical paths. Stop widening scope the moment a cheaper layer would have caught the same class of regression.
- For a refactor with no intended behavior change, the review question is not "is this good code" but "can I prove nothing observable changed." Golden master, property tests, and contract tests are the proof; code review alone only checks that the change *looks* safe.
- Explicitly test concurrency ordering, floating-point rounding, and error-message text that another system parses — these are the most common sources of invisible behavior change in an otherwise-clean refactor.

### Refactoring Under Deadline Pressure (Triage)

- Under time pressure, shrink scope — do not drop the safety net. A 30-minute characterization test around the touched boundary is cheaper than the incident it prevents.
- If there truly is no time for tests, restrict yourself to the most mechanical change possible (rename, extract-without-changing-logic) and defer anything that changes control flow or data shape to a follow-up ticket. Do not combine "fast" with "risky."
- Record the shortcut in the technical debt register in the same PR — deadline debt that is not written down does not get paid down later.
- Escalate rather than silently absorb: if the deadline forces skipping the safety net on a high-risk path (money, auth, data, migrations), say so explicitly to the reviewer or product owner instead of quietly shipping it.

### Strangler Fig vs. Big-Bang Rewrite

- Default to strangler fig whenever the system has live users or traffic and halting feature delivery for months is unacceptable — the incremental path is usually cheaper than the rewrite ever gets credited for, once you count the risk of a multi-month all-or-nothing cutover.
- Big-bang rewrite is defensible only when: there is no live traffic yet (true greenfield replacement), the domain logic is small enough for one team to hold in their heads, or the legacy system is so broken (unsupported runtime, expired license, unpatchable security hole) that partial operation is not viable.
- Watch for the "we're 80% migrated, let's finish it in one push" trap. The remaining slice is disproportionately the undocumented edge cases; hold the same per-feature discipline (one seam at a time, parity metrics before widening rollout) on the last slice as on the first.
- If a rewrite is genuinely chosen, still slice it: ship the smallest end-to-end vertical slice first and route real (even low-value) traffic through it before building the rest, to get delivery feedback without full big-bang risk.

### LLM Agents and Subtle Behavior Changes During "Refactors"

Prompts framed as "refactor this" fail agents in a specific way: the agent notices a local improvement opportunity and takes it, silently expanding scope from "same behavior, better structure" to "same behavior, better structure, plus a few fixes I noticed along the way." Watch for, and gate against, these failure modes:

- **Error-handling drift** — narrowing/widening an `except`/`catch`, turning a silent failure into a raised exception (or the reverse), or changing a default on an error path. Nearly invisible in review because the "refactored" code reads as cleaner.
- **Boundary drift** — `>` becomes `>=` (or vice versa) while consolidating near-duplicate conditionals.
- **Rounding/precision drift** — a manual accumulation loop replaced by a library call with different floating-point behavior at the margins; high-risk for money and scientific code.
- **Ordering/concurrency drift** — reordering statements that looked independent, or narrowing a lock scope, changes observable ordering or introduces a race that only shows up under load.
- **Test-healing anti-pattern** — when characterization or existing tests fail after an agent's change, the agent's default move is often to loosen the assertion or delete the failing case to turn the suite green. Treat every test-file change inside a "pure refactor" PR as a flag requiring explicit human justification, not a housekeeping detail.
- **Scope creep on multi-file rewrites** — 2026 practitioner write-ups on agent-driven refactors (a single practitioner's analysis, not a peer-reviewed benchmark — treat the exact figures as **unverified as of 2026-07-11**) describe roughly 40% real-world success on enterprise multi-file refactors and roughly a third on legacy codebases, notably below marketing claims, attributed to "lost in the middle" context loss, architectural drift (locally sensible, globally inconsistent decisions), and index staleness against a codebase that moved on after the agent's context was built. Whatever the precise number, scope the blast radius and sample-review real diffs before trusting a multi-file agent pass at scale.

Gate before merging an agent-authored "refactor":

1. Diff the test files first, before the source diff — any weakened, deleted, or newly-skipped assertion is disqualifying until a human explains why.
2. Re-run the pre-existing (not agent-authored) characterization/contract suite; a green agent-authored test suite proves nothing about behavior preservation on its own.
3. Where the agent also generated the safety net, mutation-test the touched boundary before trusting those tests — see [references/mutation-testing.md](references/mutation-testing.md#mutation-score-as-the-ai-generated-test-validator). Line coverage alone is exactly the metric agents learn to game.
4. Sample-review the actual diff for the drift patterns above yourself; do not accept a diff summary from the same agent that wrote the diff as a substitute for reading it.
5. Never let an agent expand scope mid-task ("while I was in there, I also…"); split any such change into its own reviewed PR.

## Quick Reference

| Task | Tool/Pattern | Command/Approach | When to Use |
| ---- | ------------ | ---------------- | ----------- |
| Long or mixed-concern function | Extract Method | Split into smaller functions | Single function mixes validation, orchestration, and side effects |
| Large or low-cohesion class/module | Split Class / Extract Module | Create focused units with narrower responsibilities | One type owns unrelated workflows or too many dependencies |
| Duplicated code | Extract Function/Class | DRY principle | Same logic in multiple places |
| Complex conditionals | Replace Conditional with Polymorphism | Use inheritance/strategy pattern | Switch statements on type |
| Long parameter list | Introduce Parameter Object | Create DTO/config object | Functions with >3 parameters |
| Legacy code modernization | Characterization Tests + Strangler Fig | Write tests first, migrate incrementally | No tests, old codebase |
| Large mechanical rewrite | Codemod / AST transform | Dry-run, sample diff review, staged batch rollout | Renames, API migrations, repetitive edits across many files |
| Java framework migration (Spring Boot, Java version) | OpenRewrite recipe via Moderne CLI or MCP | `mod run . --recipe UpgradeSpringBoot_3_4` | AI agents can invoke 5,000+ OpenRewrite recipes as deterministic tool calls |
| Automated quality gates | Compiler + linter + contract checks | CI pipeline with fail-fast checks and artifacts | Prevent silent regression during refactors |
| Technical debt tracking | Debt register + static analysis | Track trends, hotspots, and owners | Prioritize refactoring work |

## Decision Tree: Refactoring Strategy

```text
Code issue: [Refactoring Scenario]
    ├─ Code Smells Detected?
    │   ├─ Duplicated code? → Extract method/function
    │   ├─ Mixed concerns in one function? → Extract smaller methods
    │   ├─ Low cohesion / too many dependencies? → Split into focused classes or modules
    │   ├─ Long parameter list? → Parameter object
    │   └─ Feature envy? → Move method closer to data
    │
    ├─ Legacy Code (No Tests)?
    │   ├─ High risk? → Write characterization tests first
    │   ├─ Large rewrite needed? → Strangler Fig (incremental migration)
    │   ├─ Unknown behavior? → Characterization tests + small refactors
    │   └─ Production system? → Canary/shadow rollout + monitoring
    │
    ├─ Repetitive Multi-File Edit?
    │   ├─ Compiler/IDE can prove rename? → Use native refactor tooling
    │   ├─ Pattern is syntactic/semantic? → Use codemod or AST rewrite
    │   └─ Blast radius is large? → Dry-run + sample review + batch rollout
    │
    ├─ Quality Standards?
    │   ├─ New project? → Setup compiler/linter/test gates
    │   ├─ Existing project? → Add pre-commit hooks + CI checks
    │   ├─ Complexity hotspots? → Add targeted guardrails and characterization tests
    │   └─ Technical debt? → Track in register with owners and review cadence
```

## ASCII Flow

```text
Refactoring request
  -> State behavior that must not change and rollback boundary
  -> Capture baseline with tests, contracts, metrics, or characterization output
  -> Choose the smallest behavior-preserving step
  -> Apply native refactor tooling, codemod, or manual edit as appropriate
  -> Run targeted verification before widening scope
  -> Retire debt, flags, dead code, or guardrails only with evidence
```

## Navigation

- `## Workflow`, `## Core QA (Default)`, and `## Decision Tree: Refactoring Strategy` for the baseline sequence
- `## Operational Deep Dives`, `## Templates`, and `## Resources` for deeper materials
- `## Related Skills` for testing, architecture, and code-review handoffs

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-debugging](../qa-debugging/SKILL.md) | Debugging production issues and test flakes |
| [software-code-review](../software-code-review/SKILL.md) | Code review process and checklists |
| [software-architecture-design](../software-architecture-design/SKILL.md) | Architecture design and redesign decisions |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Test strategy and coverage planning |
| [data-sql-optimization](../data-sql-optimization/SKILL.md) | Performance tuning, SQL, and query plans |

## Operational Deep Dives

### Shared Foundation

- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) - Canonical clean code rules (`CC-*`) for citation
- Legacy playbook: [../software-clean-code-standard/references/code-quality-operational-playbook.md](../software-clean-code-standard/references/code-quality-operational-playbook.md) - `RULE-01`–`RULE-13`, decision trees, and operational procedures
- [../software-clean-code-standard/references/refactoring-operational-checklist.md](../software-clean-code-standard/references/refactoring-operational-checklist.md) - Refactoring smell-to-action mapping, safe refactoring guardrails
- [../software-clean-code-standard/references/working-effectively-with-legacy-code-operational-checklist.md](../software-clean-code-standard/references/working-effectively-with-legacy-code-operational-checklist.md) - Seams, characterization tests, incremental migration patterns

### Skill-Specific

See [references/operational-patterns.md](references/operational-patterns.md) for detailed refactoring catalogs, codemod rollout patterns, quality gates, technical debt playbooks, and legacy modernization steps.

## Templates

Use copy-paste templates in `assets/` for checklists and quality-gate configs:

- Refactoring: [assets/process/refactoring-checklist.md](assets/process/refactoring-checklist.md), [assets/process/code-review-quality.md](assets/process/code-review-quality.md)
- Technical debt: [assets/tracking/tech-debt-register.md](assets/tracking/tech-debt-register.md)
- Quality gates: [assets/quality-gates/javascript/eslint-config.js](assets/quality-gates/javascript/eslint-config.js), [assets/quality-gates/platform-agnostic/sonarqube-setup.md](assets/quality-gates/platform-agnostic/sonarqube-setup.md)

## Resources

Use deep-dive guides in `references/` (load only what you need):

- **Operational Patterns**: [references/operational-patterns.md](references/operational-patterns.md) - Core refactoring catalogs, quality gates, and legacy modernization
- **Refactoring Catalog**: [references/refactoring-catalog.md](references/refactoring-catalog.md)
- **Code Smells Guide**: [references/code-smells-guide.md](references/code-smells-guide.md)
- **Technical Debt Management**: [references/tech-debt-management.md](references/tech-debt-management.md)
- **Legacy Code Modernization**: [references/legacy-code-strategies.md](references/legacy-code-strategies.md)
- **Characterization Testing**: [references/characterization-testing.md](references/characterization-testing.md) - Golden master and approval testing patterns
- **Strangler Fig Migration**: [references/strangler-fig-migration.md](references/strangler-fig-migration.md) - Incremental legacy migration strategies (includes expand-contract / parallel change callout)
- **Automated Refactoring Tools**: [references/automated-refactoring-tools.md](references/automated-refactoring-tools.md) - Codemods, AST transforms, recipe testing, and IDE refactoring
- **Mikado Method**: [references/mikado-method.md](references/mikado-method.md) - Prerequisite tree for entangled legacy changes; leaf-first execution
- **Mutation Testing**: [references/mutation-testing.md](references/mutation-testing.md) - Stryker/mutmut/cosmic-ray/PIT; mutation score, CI thresholds, incremental runs
- **Feature Flag Retirement**: [references/feature-flag-retirement.md](references/feature-flag-retirement.md) - Step-by-step recipe: identify references, remove dead branch, delete definition last

## Optional: AI / Automation

Do:

- Use AI to propose mechanical refactors (rename/extract/move) only when you can prove behavior preservation via tests and contracts.
- Use AI to summarize diffs and risk hotspots; verify by running targeted characterization tests.
- Prefer tool-assisted refactors (IDE/compiler-aware, codemods) over freeform text edits when available.
- Treat agent-generated refactors as draft patches until a human reviews representative diffs and the safety net is green.
- For Java projects, prefer OpenRewrite recipes (via `mod` CLI or MCP server) over hand-written codemods — recipes are deterministic and version-aware; AI agents can invoke them directly as tool calls.
- Validate AI-generated characterization tests with mutation testing before treating them as a refactor safety net; line coverage alone does not prove test quality. See [references/mutation-testing.md](references/mutation-testing.md#mutation-score-as-the-ai-generated-test-validator).
- For large multi-file agent refactors, scope the blast radius before execution: a single 2026 practitioner report (not a peer-reviewed benchmark — treat the exact figures as unverified as of 2026-07-11) put AI agent success at roughly 40% on enterprise multi-file refactors and roughly a third on legacy codebases; whatever the true number, scope and review discipline are essential. See "LLM Agents and Subtle Behavior Changes During 'Refactors'" above.

Avoid:

- Accepting refactors that change behavior without an explicit requirement and regression tests.
- Letting AI "fix tests" by weakening assertions to make CI green.
- Rolling out AI-generated multi-file edits repo-wide without a dry run and sample review.
- Letting agents expand scope autonomously mid-refactor; define the boundary and blast radius before the agent starts.

See [data/sources.json](data/sources.json) for curated external references.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

