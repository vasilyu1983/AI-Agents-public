# Skill Validation

Validation is two things:

- static correctness: the bundle is shaped correctly
- behavioral correctness: the runtime actually triggers the skill and navigates it well

## Table of Contents

- [Quick Start](#quick-start)
- [Validation Levels](#validation-levels)
- [Static Checks](#static-checks)
- [Compatibility Checks](#compatibility-checks)
- [Behavioral Evals](#behavioral-evals)
- [Effectiveness-Claim Eval Design](#effectiveness-claim-eval-design)
- [Observation Checklist](#observation-checklist)
- [Output Format](#output-format)

## Quick Start

```bash
# Static validation for one skill
python3 scripts/validate_skill.py .

# Fixture regression checks for the validator itself
python3 scripts/test_validate_skill.py
```

Optional URL checks are network-dependent:

```bash
python3 scripts/validate_skill.py . --check-urls
```

## Validation Levels

| Level | When | Includes |
|------|------|----------|
| Quick | During authoring | Frontmatter, links, TOCs |
| Standard | Before commit | Quick checks plus `sources.json`, freshness, compatibility notes |
| Behavioral | Before release or sync | Trigger evals, non-trigger evals, navigation, runtime-specific checks |

## Static Checks

### 1. Portable Core

Required:

- `SKILL.md` exists
- frontmatter starts and ends correctly
- `name` exists, is kebab-case, and matches the folder name
- `description` exists, is single-line, and stays within the current limit

Recommended:

- description uses third-person phrasing
- description includes clear trigger terms
- `SKILL.md` stays under 500 lines

### 2. Link Integrity

Every local markdown link should resolve:

- links from `SKILL.md`
- links between reference files
- links to local data files or scripts

This is a hard fail for shipping a skill.

### 3. Long Reference Files

If a file in `references/` exceeds 100 lines:

- include `## Table of Contents` near the top
- keep sections scannable
- link to it directly from `SKILL.md`

### 4. `sources.json`

If `data/sources.json` exists:

- JSON must parse
- `metadata.title`, `metadata.description`, `metadata.last_updated`, and `metadata.skill` must exist
- `metadata.skill` must match the folder name
- URLs should use HTTPS
- freshness should be recent enough to trust for volatile platform details

## Compatibility Checks

Portable rule:

- `name` and `description` are the portable required fields.
- `license`, `compatibility`, and `metadata` are portable optional fields.
- `allowed-tools` is part of the open spec, but runtime support may vary.

Extension rule:

- If runtime-specific frontmatter fields are present, add a scoped `compatibility` note.

Hard fail:

- runtime-specific fields plus a claim like `portable`, `cross-platform`, or `all runtimes`

Warning:

- runtime-specific fields without a compatibility note

## Behavioral Evals

Build evals before you polish documentation. The doc is not the source of truth; observed behavior is.

### Risk-Based Eval Set

The full matrix is the release target for a new skill or for an edit that materially broadens a description, changes routing ownership, or adds overlap with adjacent skills. Do not impose it retroactively on every unchanged catalog entry merely because a file crosses a line-count threshold. For established long skills, the deterministic floor is one positive pilot task; add negative controls where the routing boundary is changing or known to be ambiguous.

| Eval Type | Release target | What good looks like |
|----------|---------|----------------------|
| Explicit | 2 prompts | `/skill-name` and direct invocation still resolve after edits |
| Trigger (implicit) | 3 prompts | Skill activates on clear in-scope requests |
| Contextual | 3 prompts | Skill activates on noisy prompts that mix in adjacent-domain language |
| Non-trigger | 3 prompts | Skill stays inactive on adjacent but out-of-scope work |
| Navigation | 2 prompts | Runtime reads the correct supporting file instead of over-reading the bundle |
| Runtime-specific | 1 prompt per target runtime | Extensions are either respected or clearly unnecessary |
| Compaction-resilience | 1 prompt per long-running session | Skill content remains effective after auto-compaction |

The four invocation classes (explicit, implicit, contextual, negative-control) match the OpenAI/Codex eval taxonomy and the Anthropic best-practices guidance. Cover all four for a new skill or materially changed routing surface. A narrow internal edit may reuse existing evidence when it does not alter discovery or navigation.

### Deterministic Pilot Policy

`scripts/validate-eval-manifests.py` enforces two separate claims in `pilot-router-and-long-skills.json`:

- A long skill is covered only by a positive routing or deterministic rubric task. A `not_primary_skill_in` task cannot satisfy positive coverage.
- `scripts/eval-manifest-policy.json` lists skills whose current routing risk requires negative controls and the minimum count for each. Use three distinct adjacent-domain controls for a new or materially broadened description when overlap is plausible. Use a smaller explicit count for a stable surface only when one representative boundary is the actual risk under test.

Each negative task names the skill that must not be primary in `expected_skills`, uses the `not_primary_skill_in` scorer, and carries the `non-trigger` tag. The prompt should have a credible neighboring owner; avoid unrelated novelty prompts that prove only that the router can reject obvious nonsense.

### Edit Gate (regression rule)

Choose the regression gate from the behavior changed, not merely the presence of a diff:

- **Non-semantic prose corrections:** run applicable structure, link, and graph checks. Reuse existing behavioral evidence when triggers, navigation, instructions, and runtime semantics are unchanged; a heading or typo fix does not require a new model run. Changes to factual claims still need applicable source, citation, freshness, and compatibility checks; they are not exempt merely because they are prose.
- **Routing or trigger changes:** compare positive, contextual, and adjacent non-trigger cases before and after the edit.
- **Navigation or workflow changes:** compare relevant file-read and completion cases. Observe tool activity where the runtime exposes it; declared `curated_paths` and candidate-reported reads are not proof of navigation.
- **New skills or materially broadened scope:** use the full risk-based matrix above.

For the affected behavioral cases:

- Score the affected eval set on the skill *before* the edit (baseline) and *after* the edit (candidate), keeping runtime configuration and task conditions comparable. If no comparable live baseline is available, label the current result as candidate evidence and do not claim non-regression.
- Accept the candidate only if it does not regress: trigger, non-trigger, and navigation pass-rates must hold or improve. A higher trigger rate that drags a non-trigger into firing is a regression, not a win.
- If the candidate regresses, reject it and keep the baseline. Do not average the two versions or ship "mostly better" — a blended skill satisfies neither intent (see coding-behavior Rule 7).
- Keep edits bounded. One concern per edit (a sharper trigger phrase, a moved reference link, a tightened scope line), so a rejection points at a single cause instead of a tangled diff.
- Record rejected edits so the same regressing change is not re-proposed next pass; the learnings loop (`learnings.md`) is the place for that note.

Keep fixture/scorer checks, lexical routing probes, observed runtime navigation, and task-quality judgments separate in the report. A passing static or fixture suite cannot substitute for a missing live baseline. See [data/sources.json](../data/sources.json) (`research_and_methods`) for evaluation patterns.

## Effectiveness-Claim Eval Design

The Edit Gate above governs *trigger and navigation* regressions on skill edits. A different claim needs a different eval: when a skill asserts it improves something measurable — token count, latency, output quality, cost — that claim needs its own evidence, not a restatement of the Edit Gate's trigger/nav scores.

**Source**: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman), commit `11ddc0c9813c8f75365cd5be2f753df08712f154`, MIT license. Pattern extracted 2026-08-09; see `docs/research/2026-08-09-skill-caveman-scan.md` in this repo for the full scan.

### Measure Against a Control Arm, Not "Nothing"

Comparing a skill's effect against a no-instruction baseline conflates two different things: what the skill specifically contributes, and what any generic instruction of the same shape would have produced anyway. If the claim is "this skill makes replies more concise," the correct comparison is the skill's system prompt versus a generic "be concise" instruction alone — not versus no instruction at all. The delta between the skill and the generic control is what the skill itself is worth; the delta between the generic control and nothing is a confound that inflates the skill's apparent contribution if left uncontrolled.

Applied here, an effectiveness-claim eval needs at minimum:

- **Treatment arm**: the skill enabled, on the target task set.
- **Control arm**: the same task set, skill disabled — for a narrow claim ("this exact behavior"), a generic version of the instruction is the correct control; for a broad claim ("this skill helps"), no-instruction is acceptable as a floor, but say which one was used.
- **A stats path that can print a negative number.** Do not build only a "savings calculator" that reports gains — build (or reuse) a comparison that computes treatment-minus-control honestly, including the case where the control wins. A measurement that structurally cannot report a negative result is not a measurement, it is a marketing script.

This does not replace `dev-ai-coding-metrics` — that skill owns general A/B, before/after, crossover, and shadow-study design for engineering-productivity claims at team/org scale (`references/benchmarking-methodology.md`, `assets/experiment-design-template.md`). Reuse those designs directly when the claim is about developer productivity. This section is narrower: it is about substantiating a specific skill's or prompt's own effectiveness claim before publishing it in a `SKILL.md` or README, and the control-arm framing (generic-instruction control, not just no-instruction) is the one addition specific to that narrower case.

### Publish the Honest Number Next to the Headline Number

**Source**: same repo, `docs/HONEST-NUMBERS.md` @ `11ddc0c98`, MIT.

If a skill ships a headline effectiveness number (a README line like "cuts 65% of tokens"), publish — in the same PR, not as a follow-up — a short disclosure alongside it that states:

- the exact narrow condition under which the headline number holds (task type, model, measurement method)
- the honest lower number for the general case the reader will actually assume applies
- when the effect goes net-negative, named plainly (not hedged into a footnote)
- how to reproduce or self-measure the number

Do not average the headline and the honest number into one hedged claim — state both, and say which condition each applies to. A skill that only ever reports its best-case number is not lying, but it is letting the reader assume best-case is typical case; the disclosure closes that gap without weakening the real result. This is the same discipline as coding-behavior Rule 12 ("Fail loud") applied to a metrics claim instead of a task-completion claim: "this skill works" is wrong to say unhedged if it only works under the narrow condition you measured.

**What this is not**: a mandate to fabricate a control-arm result or a disclosure doc for a skill that has never actually been measured. If no measurement exists yet, the honest statement is "not yet measured" — do not seed a plausible-looking number to make a skill's claims look substantiated. Document the measurement method here; only a real run produces a number to disclose.

### Trigger Eval Examples

- "Create a new skill for release runbooks"
- "Modernize this skill so it works across runtimes"
- "Add a validator to this skill bundle"

### Non-trigger Eval Examples

- "Review this React component"
- "Fix this SQL query"
- "Create a feature flag in PostHog"

### Navigation Eval Questions

When reviewing logs or traces, ask:

- Did the runtime stop at `SKILL.md`, or did it load the right reference file?
- Did it open only the relevant support file, or did it read everything?
- Did it miss the validator or the compatibility matrix even though they were the right next step?

### Contextual Eval Examples

These are noisy prompts that mention adjacent domains but should still route to the same skill. Without these, you only test the easy case.

- "Our paid ads CAC went up but the real cause is our organic traffic dropped. Search Console shows canonical issues. Affiliate pages also need work later." → should still route to `marketing-seo`, not `marketing-paid-advertising` or `marketing-affiliate-partnerships`.
- "We are designing subscription billing with retries and multi-currency settlement. Compliance is asking about AML thresholds and finance wants better reporting." → should still route to `software-payments`, not `project-acme-aml-financial-crime`.
- "I want a multi-agent review team where agents load shared skills and hooks log activations." → should still route to `agents-subagents`, not `agents-skills` or `agents-hooks`.

Pattern: pack the prompt with tangential domain language, keep the actual ask narrow.

### Compaction-Resilience Check

Anthropic Claude Code re-attaches only the most recent invocation of each skill after auto-compaction, capped at the first 5,000 tokens, sharing a 25,000-token combined budget across all skills. Older skills can disappear silently.

How to test:

1. Invoke the skill in a fresh session.
2. Drive the context past the auto-compaction threshold with unrelated work (or trigger compaction manually).
3. Continue the original task without re-invoking the skill.
4. Check whether the skill's guidance still shapes the output, or whether the model has reverted to default behavior.

Mitigation if the skill collapses after compaction:

- Make the skill's most critical rules early in `SKILL.md` (within the first 5,000 tokens).
- Tell users to re-invoke the skill explicitly after long sessions.
- For absolutely-must-apply rules, move them to `AGENTS.md` / `CLAUDE.md` instead.

### Cross-Model Checks

If the runtime supports model choice, test at least:

- the default model
- one cheaper or faster model if the skill is meant for routine use

This catches descriptions that only work when the model is overly capable.

## Observation Checklist

- Under-triggering: users have to name the skill manually
- Over-triggering: skill activates for neighboring domains
- Navigation failure: runtime reads the wrong file or ignores a key reference
- Contract drift: runtime-specific fields leak into portable examples
- Stale platform assumptions: examples mention behavior no longer present in official docs

## Output Format

Use this shape when reporting validation:

```markdown
## Validation Summary

- Status: PASS | WARN | FAIL
- Skill: `skill-name`
- Errors: X
- Warnings: Y

## Errors
- None

## Warnings
- None

## Behavioral Follow-Up
- Trigger evals still needed
```

## Related

- [frontmatter-reference.md](frontmatter-reference.md) - Portable core vs runtime-specific headers
- [skill-patterns.md](skill-patterns.md) - Bundle organization patterns, including Pattern 6 (Eval-Driven Skill)
- `dev-ai-coding-metrics` (`references/benchmarking-methodology.md`, `assets/experiment-design-template.md`) - general A/B, before/after, crossover, and shadow-study design for developer-productivity claims at team/org scale
- [../SKILL.md](../SKILL.md) - Main skill reference
