# Brownfield Agent Loop

How to point a coding agent at a large legacy codebase without it drifting, and how to
make the loop's exit condition something other than "the agent says it's done."

This reference owns **setup and loop construction**. It does not re-derive:

- what characterization tests are, or how to write them → [characterization-testing.md](characterization-testing.md)
- seams, sprout/wrap, dependency breaking → [legacy-code-strategies.md](legacy-code-strategies.md#seams-and-breaking-dependencies)
- strangler routing and dual-write → [strangler-fig-migration.md](strangler-fig-migration.md)
- how an agent's "refactor" silently changes behavior, and the merge gate that catches it →
  [`../SKILL.md#llm-agents-and-subtle-behavior-changes-during-refactors`](../SKILL.md)

Read those first. This file is the connective layer: repo → seam → gate → scoped task → loop.

## Contents

- [Why greenfield agent workflows fail here](#why-greenfield-agent-workflows-fail-here)
- [Precondition: the acceptance gate must exist first](#precondition-the-acceptance-gate-must-exist-first)
- [Step 1 — Graph the repo before prompting](#step-1--graph-the-repo-before-prompting)
- [Step 2 — Pick the seam from graph structure](#step-2--pick-the-seam-from-graph-structure)
- [Step 3 — Build the gate around the seam](#step-3--build-the-gate-around-the-seam)
- [Step 4 — Scope one task to one seam](#step-4--scope-one-task-to-one-seam)
- [Step 5 — Run the loop against the gate](#step-5--run-the-loop-against-the-gate)
- [Stop conditions](#stop-conditions)
- [Known traps](#known-traps)
- [Anti-patterns](#anti-patterns)

## Why greenfield agent workflows fail here

The standard agentic-coding loop assumes three things that a legacy repo does not provide:

| Greenfield assumption | Brownfield reality | Consequence |
|---|---|---|
| A test suite exists and encodes intent | Coverage is partial, stale, or absent | "Tests pass" proves nothing; the loop has no true signal |
| The spec is the source of truth | The *running system* is the source of truth, spec is lost | Agent optimizes toward the spec and breaks undocumented behavior real users depend on |
| Context fits: the agent can read what it needs | 200k+ LOC, implicit coupling, no module boundaries | Agent reads a plausible subset, misses the caller that matters |

The failure is not that the agent writes bad code. It is that **the loop has no trustworthy
acceptance signal**, so iteration converges on "looks right" instead of "behaves the same."
Every step below exists to manufacture that signal before the agent starts.

Success rates on agent-driven multi-file legacy work are materially below marketing claims
(see the scope-creep note in the parent skill, flagged unverified). Plan for a scoped,
gated, human-reviewed loop — not an overnight autonomous rewrite.

## Precondition: the acceptance gate must exist first

**Do not start the loop until a behavior-preservation gate exists that the agent did not write.**

This is the single load-bearing rule in this file. An agent-authored test suite passing an
agent-authored refactor is a closed loop with no external reference — it will converge, and
it will converge on the agent's own misunderstanding.

Order matters:

1. Human (or agent under human review) writes characterization tests against **current**
   behavior, on the pre-change code.
2. Those tests are committed and green **before** any refactor prompt is issued.
3. The refactor loop may not modify them. A diff touching them is disqualifying until a
   human justifies it.

If you cannot build a gate for a region of code, that region is not yet eligible for an
agent loop. Shrink the scope until you can, or do it by hand.

## Step 1 — Graph the repo before prompting

Ad hoc file reads on a large legacy repo produce a plausible-but-partial mental model —
the "lost in the middle" failure. Build the graph artifact first and let the agent query it
instead of guessing.

Use [`../../dev-context-code-graph/SKILL.md`](../../dev-context-code-graph/SKILL.md).
Switch to graph-first context when the repo exceeds ~500 source files or ~5k symbol nodes.

```bash
# from dev-context-code-graph/scripts/
python3 scan_code_repo.py     # discover
python3 build_code_graph.py   # emit graphs/code-graph.json
python3 validate_code_graph.py
```

What you need out of it before choosing anything:

| Query | Why it matters in brownfield |
|---|---|
| `--articulation-points` | Nodes whose removal disconnects the graph — the highest-risk things to touch, and often exactly where the seam wants to go |
| `--bridges` | Single edges holding subsystems together; a natural strangler boundary |
| `--cycles` | Cyclic clusters cannot be extracted incrementally without breaking the cycle first — they change the plan |
| `--communities` | Empirical module boundaries in a codebase that has no declared ones |
| test-coverage cone | Where the safety net already exists vs where you must build it |

Recipes: [`../../dev-context-code-graph/references/query-recipes.md`](../../dev-context-code-graph/references/query-recipes.md)
— specifically the refactor-risk packet and test-coverage cone.

**Parse-gap caveat.** The graph's precision is bounded by parser coverage; heuristic parsers
lose precision on dynamic dispatch, reflection, string-keyed lookups, DI containers, and
config-driven wiring — all of which are *more* common in legacy code. Treat blast radius as
a lower bound on what is affected, never as proof that nothing else is.

## Step 2 — Pick the seam from graph structure

Do not let the agent choose what to refactor. Structure chooses; you confirm.

Rank candidate seams by:

1. **Isolability** — bridge or articulation point, few inbound edges, no cycle membership.
2. **Existing coverage** — inside an existing test-coverage cone beats greenfield gate work.
3. **Change pressure** — churn from git history; refactoring frozen code buys nothing.
4. **Blast radius** — smallest reachable set that still delivers the value.

The intersection of *high churn* and *low coverage* is the standard priority target: it is
where defects concentrate and where a gate pays for itself immediately.

Reject a seam if it sits inside a cycle. Break the cycle first as its own gated task
(extract interface / parameterize constructor —
[legacy-code-strategies.md](legacy-code-strategies.md#dependency-breaking-techniques)),
then re-graph. A cycle-spanning "refactor" prompt is how multi-file agent runs go
architecturally inconsistent.

## Step 3 — Build the gate around the seam

The gate is the loop's exit condition. It has three layers; the loop is only as trustworthy
as the weakest one.

| Layer | Purpose | Built by |
|---|---|---|
| Characterization tests on current behavior | Detects behavior change | Human-reviewed, pre-change, immutable during the loop |
| Contract/integration tests at the seam boundary | Detects interface breakage across the strangler edge | Human-reviewed |
| Mutation score on the touched boundary | Detects a gate that passes vacuously | Tooling — [mutation-testing.md](mutation-testing.md#mutation-score-as-the-ai-generated-test-validator) |

Golden-master capture is the fastest way to build layer 1 on code with wide output surface;
see [characterization-testing.md](characterization-testing.md#golden-master-pattern) and the
log-derived generation path
([characterization-testing.md](characterization-testing.md#generating-tests-from-logs))
when production logs can supply realistic inputs.

Pin nondeterminism (clock, RNG, network, ordering, locale) before capture, or the gate will
flake and the loop will "fix" the flake by weakening the assertion.

**Verify the gate can fail.** Before the loop runs, deliberately introduce a small behavior
change and confirm the gate goes red. A gate never observed failing is not known to be a gate.

## Step 4 — Scope one task to one seam

One seam, one task, one PR. The scope-creep failure mode is the dominant one in agent-driven
legacy work, and the countermeasure is task construction, not prompt politeness.

The task handed to the agent should carry:

- the seam boundary, named explicitly (files and symbols it may modify)
- the blast-radius list from the graph — the callers it must not break
- the gate command, verbatim, as the definition of done
- an explicit prohibition on modifying the gate or any test file
- the drift list from the parent skill as things to avoid, not things to fix
- an instruction to stop and report rather than expand if the change does not fit the seam

Anything outside the named seam is a separate task. "While I was in there" is the failure,
and it is cheaper to prevent in scoping than to catch in review.

Pair this with [`../../dev-workflow-planning/SKILL.md`](../../dev-workflow-planning/SKILL.md)
for the plan-document format and per-step verification checks, and with journaling
(same skill) once the work crosses context-compaction boundaries.

## Step 5 — Run the loop against the gate

The loop shape is ordinary; what makes it brownfield-safe is that the acceptance check is
external and immutable:

```text
scoped task + blast radius + gate command
  -> agent proposes change inside the named seam
  -> run the pre-existing gate (not agent-authored tests)
  -> red? feed the failure back, iterate
  -> green? mutation-check the touched boundary
  -> human reads the diff for drift patterns
  -> merge or split
```

Loop mechanics — stagnation detection, iteration caps, budget ceilings, circuit breakers —
are owned by [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md).
Reuse them; do not re-implement. The brownfield-specific additions to that machinery:

- **Gate integrity check each iteration.** Assert the gate files are unmodified (hash them).
  This is the highest-value guard in the whole loop, because test-healing is the agent's
  default escape hatch when it cannot make the change work.
- **Re-graph after structural change.** Once symbols move, the graph is stale and blast
  radius is wrong. Regenerate before the next seam.
- **Cap iterations lower than greenfield.** Repeated failure against a *behavior* gate
  usually means the seam was wrong, not that the agent needs another attempt. Escalate to a
  human re-scope rather than spending the budget.

## Stop conditions

Stop the loop and return to a human when any of these fire:

| Condition | Why |
|---|---|
| Gate files modified | Test-healing; the loop's signal is compromised |
| Same test red 3 iterations running | The seam is wrong, not the attempt |
| Diff extends outside the named seam | Scope creep; split the task |
| Mutation score on touched boundary drops | Gate is now vacuous even if green |
| Agent proposes deleting or skipping a test | Disqualifying without human justification |
| Behavior change is *intended* | This is no longer a refactor; it needs its own spec and review |

## Known traps

- **Treating a green agent-authored suite as behavior preservation.** It is evidence about
  the agent's model of the code, not about the code.
- **Graphing once and trusting it all the way through a multi-seam migration.** Index
  staleness against a moved codebase is a documented cause of agent architectural drift.
- **Choosing the seam by reading code with the agent.** The agent will propose the region it
  understands best, which correlates with well-written code — the region that needed the
  work least.
- **Assuming blast radius is complete.** Parse gaps hide dynamic dispatch, reflection, and
  config-driven wiring. Grep the symbol name as a string before trusting the cone.
- **Running the loop on a cycle.** Extraction cannot be incremental inside a cycle; the agent
  will produce locally-sensible, globally-inconsistent edits.
- **Letting the loop run unattended on its first seam.** Calibrate on one supervised seam
  before trusting the gate to hold unattended.

## Anti-patterns

- pointing an autonomous loop at a legacy repo with no characterization gate and an
  overnight budget
- a single "modernize this module" task spanning many seams and many files
- allowing the same agent run to author both the change and its safety net
- accepting the agent's diff summary in place of reading the diff
- measuring progress in files touched or lines changed rather than seams closed behind a
  passing immutable gate
- re-running a failed seam with a bigger model instead of re-scoping it

## Related

- [`../SKILL.md`](../SKILL.md) — parent skill; drift patterns and the merge gate
- [characterization-testing.md](characterization-testing.md) — gate construction
- [legacy-code-strategies.md](legacy-code-strategies.md) — seams and dependency breaking
- [strangler-fig-migration.md](strangler-fig-migration.md) — incremental replacement routing
- [mutation-testing.md](mutation-testing.md) — validating the gate is not vacuous
- [mikado-method.md](mikado-method.md) — ordering prerequisite changes when a seam needs others first
- [`../../dev-context-code-graph/SKILL.md`](../../dev-context-code-graph/SKILL.md) — graph artifacts and queries
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — loop drivers, budgets, circuit breakers
- [`../../dev-workflow-planning/SKILL.md`](../../dev-workflow-planning/SKILL.md) — task scoping and journaling
