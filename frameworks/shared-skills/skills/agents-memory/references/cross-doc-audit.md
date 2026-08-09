# Cross-Doc Audit & Hallucination-Bait Taxonomy

When `AGENTS.md` is the always-loaded layer and other docs (`README.md`, `docs/README.md`, build plans, decision logs, runbooks) are the canonical truth, the two layers drift. The drift becomes hallucination — the agent follows AGENTS.md, the build fails, the wrong file gets edited, or worse, a check passes that wasn't actually run. This page documents the patterns and a repeatable audit recipe.

## Table of Contents

- [Hallucination-bait patterns](#hallucination-bait-patterns)
- [Pre-Code Caveat](#pre-code-caveat)
- [Audit recipe](#audit-recipe)
- [Source-of-truth / exporter pattern (multi-repo portfolios)](#source-of-truth--exporter-pattern-multi-repo-portfolios)
- ["When-X-lands-update-Y" anti-staleness pointer](#when-x-lands-update-y-anti-staleness-pointer)
- [When to run the audit](#when-to-run-the-audit)

## Hallucination-bait patterns

These are the specific shapes of AGENTS.md text that turn into agent failures, observed across real repos. They generalize past "vague instructions" — each is a *concrete* statement that causes a *specific* wrong action.

### 1. Wrong identifier (scheme, function, flag, file path)

> "Run the repo gate locally: `xcodebuild -scheme **ExampleAppLegacy** -destination ... build`."

Real scheme is `ExampleApp`. Agent runs the command verbatim, build fails. Worst because the failure is downstream — the agent thinks it's been given a working command.

**Fix**: every named identifier in AGENTS.md must round-trip with the actual project. Treat AGENTS.md commands as a contract; copy them from the real run, don't re-type from memory.

### 2. Naming the wrong layer

> "Runtime model routing is **authoritative in `policy.ts`**." (Actually `policy.ts` reads from `model-policy.json`; the JSON is authoritative.)

Agent told to "change the model" edits `policy.ts` instead of the JSON. Silent regression — both files exist, both compile, only one is right.

**Fix**: distinguish *config* from *logic* explicitly. "Names live in X.json; Y.ts reads them. Change X to change behavior."

### 3. False-positive gates

> "Run `npm run test:analytics-gate` before opening a PR." (The script is actually `lint && build` with no analytics assertions.)

Agent runs it, sees green, claims analytics is verified. False confidence — worse than no check.

**Fix**: when describing a gate, name what it actually verifies. If a script's name oversells its scope, either rename the script or add a one-liner: "currently aliases X; treat green as 'X passes', not 'analytics is verified'."

### 4. Multi-doc contradictions

> AGENTS.md mandates JSON catalogs. `docs/build-plan.md` (older) shows `res/values/strings.xml` as the structural default.

Agent reads both, flips a coin. Often picks the older/longer doc because it has more "authority" weight.

**Fix**: when AGENTS.md takes a position, sweep canonical docs for outdated phrasing. Either align them or add an explicit "supersedes" pointer in the older doc. Two truths is worse than no doc at all.

### 5. Scaffold-tense claims

> "All user-facing strings must come from JSON catalogs via `l10n.text(...)`." (No Kotlin code exists yet.)

Agent in present tense reads the rule as enforcement obligation, tries to grep for non-existent composables, hallucinates context.

**Fix**: scaffold-stage repos need a **Pre-Code Caveat** at the top:

```markdown
## Pre-Code Caveat

This repo is scaffold-stage. Sections below describe the **target contract**
the agent should produce when scaffolding M0 — not enforcement obligations
on existing code. Specifically:
- `./scripts/git/*.sh` does not exist yet; do not invoke.
- The Localization section describes what the first composables must do.
- The Verification gate is documentation-only.

Once code lands, remove this caveat and update the affected sections.
```

### 6. Generic "Agent Execution Style" platitudes

> "1. Read first then implement. 2. Make minimal scoped changes. 3. Preserve existing structure. 4. Summarize touched files."

Copy-paste artifact across repos. Consumes budget, prevents nothing the agent wouldn't already do (or wouldn't be told via better-targeted rules).

**Fix**: delete. If a specific behavior actually keeps slipping, write the specific rule that catches it.

### 7. Self-referential "config lives elsewhere" with broken target

> "Concrete model/effort values live in `.claude/agents/*.md` and `.codex/agents/*.toml`, not here." (Neither directory exists.)

Soft hallucination — agent looks for the config, finds nothing, may invent reasonable values to "fill the gap."

**Fix**: when redirecting to another file, verify it exists or qualify with "if present." Better: don't redirect at all — keep the values inline if they're genuinely needed at session start.

### 8. Pre-mature claims about future tooling

> "Run the repo gate from the worktree: `../../scripts/git/feature-workflow.sh gate`." (The `scripts/` directory hasn't been created yet.)

Common in stub repos that copy AGENTS.md from a sibling repo to "start consistent." Agent fails at the first command.

**Fix**: same Pre-Code Caveat pattern as #5. If commands aren't real yet, say so.

## Audit recipe

A repeatable cross-doc audit for any single repo or a portfolio. Parallel-friendly across repos (each repo is independent), so dispatch one subagent per repo when working at portfolio scale.

### Inputs

- The `AGENTS.md` (and `CLAUDE.md` if not symlinked).
- Top-level `README.md` if present.
- `docs/README.md` if present.
- Any canonical doc the AGENTS.md links as authoritative (build plan, decision log, system map source-of-truth, pricing matrix, etc.).
- The actual filesystem — must list the directories AGENTS.md references.

### Per-repo subagent prompt template

```
Cross-doc consistency audit for <repo>. Reduce hallucination risk by
checking AGENTS.md (always-loaded by Claude/Codex) against
README/docs/canonical-docs and verifying paths/commands exist.

Read in full:
1. <repo>/AGENTS.md
2. <repo>/README.md (or docs/README.md if no top-level)
3. <canonical doc 1>
4. <canonical doc 2 if relevant>

Verify by listing/reading:
- <every directory AGENTS.md names a file in>
- <package.json or equivalent — confirm runbook commands exist>
- <key config file — confirm it has the structure AGENTS.md describes>

Audit:
A. Contradictions — AGENTS.md vs canonical docs (commands, versions,
   policies, code locations, supported lists).
B. Stale or invented paths/commands — does each path resolve? Does each
   command exist as described?
C. Missing back-links — does the canonical doc point at AGENTS.md as
   the agent-context entry?
D. Hallucination-bait — vague language inviting fill-in from training.

Report (under 300 words):
- 5-row table: section/line in AGENTS.md → issue → severity (high/med/low)
  → suggested fix
- One-paragraph verdict
- Say "clean" for any category with no issues

Don't write code. Just report.
```

### Severity ladder

- **High** — agent will fail or take a destructive wrong action on the next session (wrong identifier, missing referenced file the agent will invoke, multi-doc contradiction on a foundational decision).
- **Medium** — agent will get a wrong-but-recoverable result (wrong-layer edit, false-positive gate, ambiguous claim).
- **Low** — cosmetic / hygiene (missing back-link, minor mismatch between README and AGENTS.md on optional commands).

Fix high+medium immediately. Bundle low into a follow-up pass.

### Verification before closing the audit

- All paths in AGENTS.md resolve (`ls` each one).
- All commands in AGENTS.md run (or are explicitly marked as "future").
- Every "X is authoritative in Y" claim is true after reading Y.
- No section uses present-tense enforcement for non-existent code.

## Source-of-truth / exporter pattern (multi-repo portfolios)

When one repo owns a shared resource (e.g. locale catalogs in `web-app/src/messages/`) and other repos consume it via export, all consumer AGENTS.md files must:

1. Name the upstream path explicitly: "Catalog source of truth: `<upstream-path>`."
2. State the export is read-only locally: "Edit upstream, not the export."
3. Forbid divergent local mirrors: "Do not default to `<platform-native-store>` (e.g. `res/values/strings.xml` on Android) — that splits the source of truth."

Without (3), the consumer repo's platform-native default beats the cross-portfolio convention. Codex on Android will generate `<string name="..."/>` because that's the platform idiom — not because anyone decided it.

## "When-X-lands-update-Y" anti-staleness pointer

Pre-mature repos rot fastest because there's no code to anchor docs against. Add a single section that names what to update later:

```markdown
- Once `gradlew` and the Android module are added, update:
  (a) **Repo Layout** — add module map
  (b) **Verification** — replace placeholder with `./gradlew lintDebug testDebugUnitTest`
  (c) **Key Commands** — add the new section with build/install commands
  (d) **Localization** — confirm the JSON loader helper exists
```

Specific section names beat "update the rest." Future-you (or the next agent) has a punch list.

## When to run the audit

- After a significant edit to AGENTS.md (≥ one new section).
- After the canonical doc(s) change.
- Before onboarding a new agent runtime (Claude Code, Codex, Cursor, etc.) — drift is cheaper to fix before a fresh agent starts citing the wrong thing.
- On a low cadence (e.g. monthly) for portfolios with multiple living repos.

A clean audit doesn't mean "no edits" — a "clean" verdict in the report is itself the deliverable.
