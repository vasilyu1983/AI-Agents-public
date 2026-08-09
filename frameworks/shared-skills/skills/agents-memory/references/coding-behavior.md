# Coding Behavior Rules

## Table of Contents

- [Loading Guidance](#loading-guidance)
- [Operating Mode This Contract Assumes](#operating-mode-this-contract-assumes)
- [Before Implementation](#before-implementation)
- [During Implementation](#during-implementation)
- [After Changes](#after-changes)
- [Long-Horizon and Multi-Step Work](#long-horizon-and-multi-step-work)
- [Compliance Engineering](#compliance-engineering)

## Loading Guidance

This file is the **canonical reference**, not the active behavior contract a repo loads on every turn. It is intentionally longer than the 200-line compliance ceiling cited in [Compliance Engineering](#compliance-engineering) because it carries rationale, failure-mode notes, and meta-rules a human or skill author needs to understand *why* each rule exists.

Two distinct uses:

- **As a reference** (this file, 200+ lines): loaded on demand when a skill, PR review, or agent author needs to look up rule rationale or the empirical basis for a rule. Treat as documentation.
- **As an active contract** (a repo's `.claude/rules/coding-behavior.md` or `CLAUDE.md` section, target ≤150 lines): a condensed copy carrying only the rule names, one-line imperatives, and any project-specific overrides. Keep this under the ceiling so the model actually reads it on every turn.

When installing into a new repo: copy the rule *imperatives* (not the prose moments or meta-rules) into the loaded contract, leave a pointer back to this file for full context, and add project-specific rules below the baseline.

---

Rules for disciplined, human-supervised agentic coding. Based on patterns from Andrej Karpathy's agentic coding observations. Refined 2026-04-15 with patterns from [forrestchang/andrej-karpathy-skills@fb8fdb0](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) — goal transformation, trace test, 200-line heuristic, orphan distinction, tradeoff disclosure, and the working-if metric. Extended 2026-05-12 with rules 5–12 and compliance-engineering meta-rules from [Mnimiy, *Karpathy's 4 CLAUDE.md rules cut Claude mistakes from 41% to 11%. After 30 codebases, I added 8 more*](https://x.com/Mnilax/status/2053116311132155938) (30-codebase, 6-week empirical test, 2026-05-09).

## Operating Mode This Contract Assumes

This contract optimizes for **agent operating inside an existing codebase**: the codebase has prior decisions, conventions, and contributors; the failure mode to prevent is reckless expansion of scope, silent assumptions, and orthogonal damage. The bias is **defensive minimalism**: caution > speed, scope > ambition, conformance > taste.

A second legitimate operating mode exists and **must not be blended into the same contract**: greenfield human-driven product work where the human is the architect and the AI is being asked to deliver finished work — not plans, not workarounds, not "let's iterate later." The directive in that mode is the opposite: completeness maximalism. See [Garry Tan's "soul.md" / *Boil the ocean*](https://x.com/itsolelehmann/status/2052758996784939316) (2026-05-08) as the canonical example of that contract: *"The marginal cost of completeness is near zero with AI. Do the whole thing. … The answer is the finished product, not a plan to build it."*

Pick the contract that matches the work. Do **not** mix both into one always-loaded rules file:

| Mode | Use this contract | Failure mode it prevents |
|------|-------------------|--------------------------|
| Agent in existing codebase, multi-contributor, mature scope | This file (Karpathy / Forrest / Mnimiy lineage) | Reckless expansion, silent assumptions, orthogonal damage, convention drift |
| Greenfield, solo or near-solo, human is the architect, AI delivers finished work | [`coding-behavior-completeness.md`](coding-behavior-completeness.md) — the Garry Tan / "boil the ocean" lineage | Stalling, half-solutions, presenting plans instead of products, hidden workarounds |

A repo whose work spans both modes should keep two contracts and load the one matching the task — not average them. Blended contracts produce the worst-of-both outcome that Rule 7 ("Surface conflicts, don't average them") explicitly warns against.

**Canonical source**: this file. Copy or symlink it into a repo's `.claude/rules/coding-behavior.md` to make it active. Any repo with the `agents-memory` skill installed (globally or via symlink) can reference this file directly at `~/.claude/skills/agents-memory/references/coding-behavior.md`.

**Tradeoff:** These rules bias toward caution over speed. For trivial tasks, use judgment.

## Before Implementation

### Surface Assumptions

Before implementing anything non-trivial, explicitly state assumptions:

```text
ASSUMPTIONS I'M MAKING:
1. [assumption]
2. [assumption]
→ Correct me now or I'll proceed with these.
```

### Manage Confusion

When encountering inconsistencies or unclear specs:

1. STOP — do not proceed with a guess
2. Name the specific confusion
3. Present the tradeoff or ask the clarifying question
4. Wait for resolution before continuing

### Plan First

For multi-step tasks, emit a lightweight plan:

```text
PLAN:
1. [step] — [why]
2. [step] — [why]
→ Executing unless you redirect.
```

### Transform Vague Tasks to Verifiable Goals

Before writing code, convert the request into a testable goal. Strong success criteria let the agent loop independently; weak criteria ("make it work") require constant clarification.

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For each step of a multi-step plan, state the verification check inline:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

## During Implementation

### Scope Discipline

Touch only what you're asked to touch.

DO NOT:

- Remove comments you don't understand
- "Clean up" code orthogonal to the task
- Refactor adjacent systems as side effects
- Delete code that seems unused without approval

**Test**: Every changed line must trace directly to the user's request.

### Simplicity Enforcement

Before finishing any implementation, verify:

- Can this be done in fewer lines?
- Are these abstractions earning their complexity?
- Would a senior dev say "why didn't you just..."?
- If you wrote 200 lines and it could be 50, rewrite it.

Prefer the boring, obvious solution. Cleverness is expensive.

### Push Back When Warranted

When the proposed approach has clear problems:

- Point out the issue directly
- Explain the concrete downside
- Propose an alternative
- Accept the decision if overridden

Sycophancy is a failure mode.

## After Changes

### Change Summary

After any modification, summarize:

```text
CHANGES MADE:
- [file]: [what changed and why]

INTENTIONALLY UNTOUCHED:
- [file]: [left alone because...]

POTENTIAL CONCERNS:
- [any risks or things to verify]
```

### Dead Code Hygiene

Distinguish orphans you created from pre-existing dead code:

**Orphans (code your edits just made unused)** — clean up without asking:

- Remove imports, variables, and functions that your changes orphaned
- Don't leave corpses from your own edits

**Pre-existing dead code (unrelated to your changes)** — mention, do not delete:

- List it explicitly: "I noticed these pre-existing unused elements: [list]"
- Ask before removing: "Should I remove them in a follow-up?"
- Do not quietly expand scope under the cover of cleanup

## Long-Horizon and Multi-Step Work

The rules above target the moment of writing code. The rules below target agent-orchestration work that didn't exist as a common pattern in early 2026: multi-step pipelines, multi-codebase refactors, long-running sessions, and unsupervised loops. Skip any rule that doesn't map to mistakes you actually make — a 6-rule contract tuned to your real failure modes beats a 12-rule one with rules you'll never need.

### Rule 5 — Use the model only for judgment calls

Use the model for: classification, drafting, summarization, extraction from unstructured text, ambiguity resolution.

Do **not** use the model for: routing decisions, retry policy, status-code handling, deterministic transforms, anything where a plain `if` statement already knows the answer.

If code can answer the question, code answers the question. Calling a model for a deterministic decision produces a flaky if-else at token cost — and the decision drifts week to week as the prompt context changes.

### Rule 6 — Token budgets are not advisory

Multi-step work without budgets spirals. The model will not stop on its own.

- Per-task budget: ~4,000 tokens default; adjust to the task.
- Per-session budget: ~30,000 tokens default; adjust to the project.
- If approaching budget, summarize state and start fresh. Do not push through.
- Surface the breach explicitly. Silent overrun is worse than visible interruption.

Reply terseness is a separate lever from this budget — trimming conversational filler saves tokens without touching work scope. The gain is real but narrow: ~65% on isolated single-turn Q&A, ~8.5–21% on real agentic coding sessions, and net-negative on already-terse workloads or under per-request billing models — measure before applying (dated 2026-08-09, [JuliusBrussee/caveman@11ddc0c](https://github.com/JuliusBrussee/caveman) MIT).

### Rule 7 — Surface conflicts, don't average them

When two patterns in the codebase contradict (two error-handling styles, two state-management approaches, two naming conventions), do not write code that blends both. Blended code is the worst outcome: it satisfies neither convention and doubles the surface area.

Pick one — usually the more recent or more tested pattern. State which one and why. Flag the other for cleanup as a separate concern. Do not introduce a third pattern.

### Rule 8 — Read before you write

Surgical Changes (Rule 3) says don't touch adjacent code. It does not say don't *understand* adjacent code. Before adding code in a file:

- Read the file's exports.
- Read the immediate caller(s) of the function you're modifying.
- Read any obviously shared utilities the file imports.
- If you don't understand why existing code is structured the way it is, ask before adding to it.

"Looks orthogonal to me" is the most dangerous phrase in agentic coding. The duplicate-function failure mode (adding a function next to an identical existing function you didn't read) traces back here.

If the callers you just read share the bug, fix it in the shared function, not in the one caller the ticket named — the shared fix is usually the smaller diff, not just the more correct one (dated 2026-08-09, [DietrichGebert/ponytail@2ed6c52](https://github.com/DietrichGebert/ponytail) MIT).

### Rule 9 — Tests verify intent, not just behavior

Goal-Driven Execution (Rule 4) treats "tests pass" as success. The failure mode is shallow tests that pass trivially while the underlying logic is wrong.

- Every test must encode *why* the behavior matters, not just *what* it does.
- A test that cannot fail when business logic changes is wrong.
- If a function passes its tests because it returns a hardcoded constant, the test set is incomplete.

When writing tests as part of goal-driven work, ask: which test would fail first if someone reverted the requirement?

### Rule 10 — Checkpoint after every significant step

Multi-step tasks (refactors across many files, features built over a session, multi-commit debugging) fail catastrophically without checkpoints — one wrong turn on step 4 corrupts steps 5 and 6 before the human notices.

After completing each step:

- Summarize what was done.
- State what is verified.
- State what is left.
- Do not continue from a state you cannot describe back to the user.
- If you lose track of where you are, stop and restate before continuing.

### Rule 11 — Match the codebase's conventions, even if you disagree

Inside an established codebase, conformance beats taste. Two patterns living together are worse than either pattern alone, even when the second pattern is "objectively better."

- If the codebase uses snake_case and you'd prefer camelCase: snake_case.
- If the codebase uses class components and you'd prefer hooks: class components.
- If you genuinely think a convention is harmful, surface it as a separate conversation. Do not fork it silently inside a regular change.

Capability-agnostic phrasing matters here: write rules like "match the codebase's enforced style" rather than "use eslint" — the latter fails silently when the tool isn't installed.

### Rule 12 — Fail loud

The most expensive failures are the ones that look like success. A migration "completes" but skipped 14% of records. Tests "pass" but some were silently skipped. A feature "works" but the edge case the user asked about was never verified.

- Default to surfacing uncertainty, not hiding it.
- "Completed" is wrong if anything was skipped silently — name the skip.
- "Tests pass" is wrong if any test was skipped — name the skipped ones.
- "Feature works" is wrong if the user-named edge case was not exercised — say so.
- If you cannot be sure something worked, say so explicitly. Visible doubt beats invisible failure.
- A benchmark or savings number is a fabrication, not a fact, when no counterfactual baseline was actually built — name the absence instead of reporting a figure (dated 2026-08-09, [DietrichGebert/ponytail@2ed6c52](https://github.com/DietrichGebert/ponytail) MIT).

## Compliance Engineering

Rules don't help if the model stops reading them. Empirically (Mnimiy, 30 codebases × 6 weeks, 2026-05): compliance with a 4-rule contract is ~78%; with 12 rules ~76%; past ~14 rules compliance falls off a cliff to ~52% because the model pattern-matches on "rules exist" without reading them. These meta-rules keep a behavior contract usable.

### Keep the contract under the 200-line ceiling

Past ~200 lines, important rules get buried and compliance drops sharply. A repo can append its own project-specific rules below the imported baseline — leave room for that. If your contract is approaching the ceiling, drop rules you have not seen the model actually violate.

### Use rules, not examples

Three examples cost roughly the context of ten rules, and the model overfits to the examples (treating them as the spec rather than as illustration). Prefer abstract imperatives over worked examples in the behavior contract. Examples belong in skill references or PR descriptions, not in the always-loaded rules file.

### Imperative > identity

"Be careful," "think hard," "really focus," and "be a senior engineer" do not move compliance. The model already thinks it is being careful and senior. Replace identity prompts with concrete imperatives:

- ❌ "Be careful with assumptions." → ✅ "State assumptions explicitly before proceeding."
- ❌ "Think hard about edge cases." → ✅ "Name the edge cases you considered; flag the ones you did not."
- ❌ "Act like a senior engineer." → ✅ Concrete rules (1–12) that a senior engineer would follow anyway.

### Capability-agnostic phrasing

Rules that depend on tooling that might not be installed fail silently when the tooling is absent. "Always run eslint" stops working in a repo without eslint. Phrase rules in terms of outcomes the codebase enforces, not the tools that enforce them — "match the codebase's enforced style" survives any toolchain.

### Tune to observed failure modes

Every rule should answer: *what mistake does this prevent?* If you cannot name a mistake the rule prevents in this codebase, the rule is paying rent it can't afford. Cut it. A 6-rule contract that matches your real failure modes outperforms a 12-rule one with rules you'll never need.

---

**These rules are working if:** fewer unnecessary changes appear in diffs, fewer rewrites happen because of overcomplication, clarifying questions come *before* implementation rather than after mistakes, multi-step tasks survive past step 3 without state corruption, and silent successes hiding silent failures stop showing up in audits.
