---
name: agents-skills-feedback-loop
description: Adds per-skill learnings loops for dated patterns, mistakes, and domain facts. Use when wiring skill memory, consolidation, or drift audits.
version: "1.6"
last_validated: 2026-09-24
---

# Agent Skills — Feedback Loop

Use this skill to wire a **learnings loop** into another skill so it gets better with use, without rewriting `SKILL.md` automatically.

The loop has four moving parts:

1. **`learnings.md`** — raw, append-only, committed. Shared working memory across machines; created on first append via `append_learning.py`, not seeded empty.
2. **`learnings.consolidated.md`** — pruned, dated, committed. Portfolio-grade institutional memory; seeded at wiring time.
3. **`learnings.local.md`** — machine-specific notes, gitignored. Use for one-operator-on-one-machine context that should not propagate.
4. **`scripts/append_learning.py` + `scripts/consolidate.py`** — keep raw entries well-shaped and redacted, and surface recurring ones for human-reviewed consolidation.

Pattern provenance and the distinction between this reviewed loop and automatic skill rewriting are in `references/evidence-base.md`; load it before attributing the design to an external source.

## Quick Reference

| Task | Read or Run | Outcome |
|------|-------------|---------|
| Wire a skill to use the loop | `references/wiring-protocol.md` | Adds a 4-line addendum to that skill's `SKILL.md`, seeds files |
| Format a new learning entry | `references/learnings-format.md` | Atomic, dated, 5-section schema that survives pruning |
| Promote raw → consolidated | `python3 scripts/consolidate.py <skill-dir>` | Dedup, age out, surface recurring patterns for human review |
| Append a learning safely | `python3 scripts/append_learning.py <skill-dir> --section <name> --text "..."` | Validates shape, dates, refuses to grow past the 150-entry cap |
| Find routing lessons that need review | `python3 scripts/consolidate.py --queue [--days 14]` | Exit 1 for aged open lessons, failed results, or fixes awaiting verification; invalid dates exit 2 |
| Audit drift across skills | `references/audit-checklist.md` | Find stale loops, missing consolidations, oversized files |
| Capture a cross-cutting behavior with no obvious skill home | `references/instinct-pattern.md` | Atomic, confidence-scored complement to the per-skill loop above |

## Workflow

1. Confirm the host skill should have a learnings loop; do not wire routers, one-off scaffolds, or stable skills with no recurring edge cases.
2. Follow `references/wiring-protocol.md` to seed `learnings.consolidated.md`, add the addendum, and verify `.gitignore` coverage.
3. Use `scripts/append_learning.py` for raw entries; do not hand-edit raw `learnings.md` during normal operation.
4. Use `scripts/consolidate.py <skill-dir>` when the raw file hits the cap, before release, or during a scheduled maintenance pass.
5. Move durable lessons into the host skill's `references/` only as a reviewed skill edit (see Promotion Out); never auto-rewrite `SKILL.md`.
6. Close a routing-log lesson only after verification passes. The fix commit ends with `Lesson-Ref: <date> <STALL|MISROUTE> <subject>` in its final trailer block. Add `→ fix <sha9> → result pending` to the log line. Replace `pending` with `WIN <date>` or `verifier passed|failed` once known; failed and pending results stay open. If a lesson needs a user decision, append `{deferred: user-decision YYYY-MM-DD}`. Before closure, read [the receipt contract](references/audit-checklist.md#lesson-receipts) and run `python3 audit/skill-status.py lessons --ref HEAD`. It verifies source and gate digests; an empty receipt set cannot pass.
7. Before appending, search raw and consolidated files for the same claim and its negation. Keep raw `learnings.md` append-only: add a new dated corroboration or conflict through `append_learning.py` and reference the earlier entry or claim. Merge or deduplicate only in the derived `learnings.consolidated.md` during the documented human-reviewed consolidation path, preserving dates and provenance; retain unresolved conflicts as open questions until the scope or runtime difference is resolved.

## When to Use

- A skill is high-traffic and you keep teaching it the same lesson twice
- A skill's domain has emerging edge cases you want captured (e.g. tax rules, payment scheme changes, new API quirks)
- A skill failed and you asked Claude to self-reflect — the reflection needs a home

## When NOT to Use

- One-off skills, internal scaffolding, or skills with stable, well-known surfaces
- Skills whose "learnings" are actually just code conventions — those belong in the repository's `AGENTS.md` or `coding-behavior.md`, not a per-skill loop
- Cross-skill patterns — promote to `references/` of the right skill or to `agents-memory`, not into every learnings file

## Core Contract

Per-skill, the loop lives inside the skill's own directory:

```
<skill>/
├── SKILL.md                       # adds the 4-line Learnings Loop addendum
├── learnings.md                   # committed, append-only, raw (shared across machines)
├── learnings.consolidated.md      # committed, pruned, dated
├── learnings.local.md             # gitignored, machine-specific, optional
└── references/...                 # durable rules move here by reviewed edit
```

Required entry shape (enforced by `append_learning.py`):

- `- [YYYY-MM-DD] <one-sentence atomic insight>`
- One bullet, one insight. No paragraphs.
- Belongs to exactly one section: *Patterns That Work / Mistakes to Avoid / Domain Knowledge / Open Questions / Consolidated Principles*.

Hard limits (refuse rather than truncate):

- Raw `learnings.md` cap: **150 entries** — reaching it blocks further appends. Consolidation does not reduce this append-only count; any capacity change needs an explicit reviewed edit.
- Consolidated file cap: **60 entries** — exceeding means the skill itself needs a `references/` extraction.

- Treat third-party learnings-loop examples as pattern evidence only; review provenance before installing or recommending automation. Graded source provenance for the maturity and design claims is in `references/evidence-base.md`.
- Do not store secrets, PII, customer-specific facts, or unreleased client details in either raw or consolidated learnings files.

Rule: `rules/repo/learnings.md` loads this invariant when Claude edits a learnings file in this library.

## The Addendum

Any skill that opts in adds this block, or a scoped equivalent preserving conditional reads and capture boundaries, near the end of its `SKILL.md`:

```markdown
## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
```

That's it — no other change to the host skill.

## Consolidation Cadence

- **Trigger:** raw file hits the 150-entry cap, OR a weekly cron (recommended: Friday), OR before a release/PR that touches the skill.
- **Protocol:** see `references/consolidation-protocol.md`. Human approves promotions to `learnings.consolidated.md`.
- **Promotion criterion:** an entry must have triggered behavior change *at least twice* (manually noted by the operator) before it is consolidated. Single-occurrence entries older than 90 days are review candidates for exclusion from consolidated memory; raw history is retained.

## Monthly Maintenance Checklist

Run these checks on any skill with an active loop:

- [ ] `python3 scripts/consolidate.py <skill-dir> --audit` — confirm valid dates/sections and raw ≤150 and consolidated ≤60
- [ ] Verify every entry starts with `- [YYYY-MM-DD]` (no undated bullets)
- [ ] Confirm `SKILL.md` still carries the `## Learnings Loop` addendum
- [ ] Scan for entries older than 90 days with no recurrence; flag for exclusion from consolidated memory
- [ ] Check for consolidated entries stable for 3+ cycles; move them out by reviewed skill edit (Promotion Out)
- [ ] Confirm `learnings.md` and `learnings.consolidated.md` are committed, and `learnings.local.md` is the only gitignored learnings file
- [ ] Run the full loop audit across all wired skills (copy the `for` loop from `references/audit-checklist.md`)

## Lint Commands

```bash
# Audit a single wired skill (checks caps, dates, section names)
python3 skills/universal/agents-skills-feedback-loop/scripts/consolidate.py \
  skills/<group>/<skill-name> --audit

# Audit all wired skills at once
for skill in skills/universal/*/ skills/project/*/ skills/client/*/*/; do
  if [ -f "$skill/learnings.consolidated.md" ]; then
    python3 skills/universal/agents-skills-feedback-loop/scripts/consolidate.py \
      "$skill" --audit
  fi
done

# Dry-run consolidation (proposes diffs, does not write)
python3 skills/universal/agents-skills-feedback-loop/scripts/consolidate.py \
  skills/<group>/<skill-name> --dry-run
```

## Closing the Capture Loop (Layer 1)

The base loop above is **open**: without a session-end hook, every append depends on an agent or human calling `append_learning.py`, so capture is uneven — some raw files fill while others stay empty.

The default Layer 1 hook is candidate-only. In this library it is `hooks/capture-learning-candidate.py`, installed by `python3 scripts/setup/agent-config.py install --apply` (Claude `SessionEnd`, Codex `Stop`). It appends `{ts, session_id, runtime, skills_used, transcript_path}` to `~/.agents/hooks/learning-candidates.jsonl`: no transcript text and no model call. A human reviews each candidate and writes the lesson with `append_learning.py`.

The opt-in reflection hook below goes further: it detects which wired
skills a session used, runs one cheap reflection pass, and appends via the
existing `append_learning.py` — no new format, no `SKILL.md` rewrite.

It is **machine-global and portable** (any laptop, any username). The hook
hands the work to a detached worker and exits at once, because session-end
hooks run under a short, runtime-capped time budget. The reflection call runs
with all tools disabled and without persisting a session, since it reads
untrusted transcript text. Every entry passes through `append_learning.py`'s
redaction step.

```bash
# From this skill directory, on any laptop:
python3 scripts/install_capture_hook.py --dry-run   # preview
python3 scripts/install_capture_hook.py             # apply
```

The installer resolves every path from `$HOME` at run time (nothing is
hardcoded), registers Claude Code (`SessionEnd`), registers Codex (`Stop`)
only with `--codex`, and is idempotent. Before adding a per-hook `timeout` or
wiring another runtime, look up that runtime's hooks reference for the
session-end budget, its cap, and the transcript format; a timeout above the cap
is silently clamped, and a transcript the parser cannot read captures nothing.
Full design, guardrails (recursion guard, blast-radius limit,
fail-silent-fail-logged), and verification:
[references/closed-loop-capture.md](references/closed-loop-capture.md).
Consolidation stays manual.

## Promotion Out

Encode a lesson at the strongest layer that fits: make the bad state unrepresentable, then a lint or validator, then a shared helper, then a runtime check, and only then prose. A consolidated entry that can become a check or a guard should leave the loop as one, not as a `references/` sentence.

Moving a consolidated principle into the host skill's `references/` is a normal
skill edit: a human makes it, in a reviewed commit, and deletes the entry from
`learnings.consolidated.md` in the same change. Where an authorized harness
exists for the target runtime, run a regression eval that passes with the rule
and fails if it is reverted; a case that passes either way proves nothing.
Otherwise record the promotion's evidence level as static or routed and make no
task-quality claim. The loop has no automated gate for this step.

## Complementary Pattern: Atomic Instincts

The loop above works at **skill granularity** — one `learnings.md` per skill. It has a gap: behavioral observations that don't belong to any one skill (e.g. "always `grep` before editing a file this large," "this repo prefers functional style") have no natural skill home and go uncaptured. `references/instinct-pattern.md` documents a smaller-granularity complement — a single-trigger, single-action, confidence-scored (0.3–0.9), domain-tagged, project-or-global-scoped unit — adapted from [affaan-m/ECC](https://github.com/affaan-m/ECC) (commit `51a6950`, MIT). It does not replace the loop above, does not adopt ECC's automatic project→global promotion (this repo keeps promotion human-reviewed, per `## Anti-Patterns` and Rule 7 of `coding-behavior.md`), and is documented as a scaffold and capture-mechanism only — no seeded example entries. For hook mechanics, see `agents-hooks`.

## What Counts as a Learning (the filter)

The filter is project-specific. The default filter lives in `references/learnings-format.md` under *Quality Filters*. Override per-skill if your domain needs a sharper bar — e.g. a tax skill should reject anything not anchored to a tax-authority manual reference or a dated statute.

## Judgment Calls (what a non-expert misses)

The mechanics above (caps, dates, dedup ratio) are checkable by script. The following are not, and are where most wired loops actually fail:

- **Silence needs context.** `--audit` establishes file shape, not learning quality or usage. During a feedback-loop audit, compare recurring failures with recorded lessons before diagnosing missed capture. Use `raw=0`, a stale `oldest` date, or extended silence (for example, 60 days) as prompts to inspect authorized usage evidence such as recent transcripts or the Layer 1 log. These are diagnostic cues, not failure thresholds: an empty or unchanged file alone does not justify mandatory pre-reads or prove that the loop failed.
- **`consolidate.py`'s duplicate clustering is syntactic, not semantic.** It clusters near-identical wording (`SequenceMatcher` ratio ≥0.82); it will not notice that "webhook needs HMAC in header" and "signature must be in the request header, not the payload" are the same lesson said twice. Treat the script's promotion proposals as a *first pass*, not the ground truth for "recurred ≥2×" — a human still has to read the raw file once per cycle to catch semantically-duplicate entries the ratio threshold misses, and to catch the reverse: two genuinely different lessons that happen to share vocabulary and get wrongly clustered.
- **Signal vs. noise is a counterfactual test, not a vibe.** Before appending, ask: if the *next* session had read this bullet first, would it have behaved differently? If the answer is no — it's an interesting observation, a diary entry, or something already obvious from reading the skill's `SKILL.md` — reject it. ACE describes loss of domain detail through compression and iterative rewriting; it does not establish that a noisy append-only file has the same failure mechanism (see `references/evidence-base.md`).
- **Recurring entries that never get consolidated are a maintenance failure, not a filter failure.** If the same lesson keeps getting re-appended in raw form across cycles instead of being promoted to consolidated, the operator is skipping consolidation, not writing bad entries. Check the cadence (`## Consolidation Cadence`) before tightening the filter.
- **A loop that never moves anything out of consolidated after many cycles is not necessarily disciplined** — it may mean nobody is running the promotion-out step in `consolidation-protocol.md` step 5. Distinguish "genuinely no principle was load-bearing enough" from "the human-gate step is a dead letter" by checking whether `learnings.consolidated.md` itself is stuck at the same size cycle over cycle.
- **Cross-skill leakage is easiest to miss in shared-vocabulary domains.** A payments skill and a compliance skill both use words like "reconciliation" or "settlement" — a consolidated entry that reads correctly in isolation can still be the wrong skill's fact. When auditing, ask whether the entry is true *because of this skill's domain* or merely *phrased in this skill's vocabulary*.

## Anti-Patterns

- **Auto-rewriting SKILL.md.** The loop never modifies `SKILL.md`. If consolidation produces a durable rule, promote it to `references/` by hand. Silent self-modification of skills is the failure mode this design exists to prevent.
- **One central learnings file across all skills.** Forbidden. A consumer-app project skill's learnings must not leak into `software-payments`; project skills stay independent of the shared library.
- **Learnings that duplicate `AGENTS.md` or `coding-behavior.md`.** General coding rules belong in those files, not in a per-skill loop.
- **Unredacted entries.** Learnings files are committed and some are published. `append_learning.py` redacts API keys, bearer tokens, emails, and home-directory usernames before writing; do not bypass it by hand-editing raw files.
- **Undated entries.** Without a date the entry cannot age, cannot be pruned, and cannot be weighted. Reject on append.

## Compatibility

- Portable across Claude Code and Codex (no runtime-specific frontmatter).
- Scripts are Python 3.10+, stdlib only.
- Hosts skill can be any prefix family (`project-*`, `software-*`, `marketing-*`, etc.).

## Navigation

- [references/wiring-protocol.md](references/wiring-protocol.md) - five-step host-skill wiring procedure
- [references/learnings-format.md](references/learnings-format.md) - entry schema, section names, and quality filters
- [references/consolidation-protocol.md](references/consolidation-protocol.md) - deduplication, pruning, and human-reviewed promotion out
- [references/audit-checklist.md](references/audit-checklist.md) - monthly loop drift checks
- [references/closed-loop-capture.md](references/closed-loop-capture.md) - Layer 1 auto-capture hook design, guardrails, install, and verification (Claude Code; Codex opt-in)
- [references/evidence-base.md](references/evidence-base.md) - graded source provenance for the maturity claims and the Layer 1 design
- [references/instinct-pattern.md](references/instinct-pattern.md) - atomic, confidence-scored instinct pattern (complement to the per-skill loop, adapted from affaan-m/ECC)
- [scripts/append_learning.py](scripts/append_learning.py) - append raw dated entries, redacting secrets and PII
- [scripts/test_append_learning.py](scripts/test_append_learning.py) - redaction and CLI regressions
- [scripts/consolidate.py](scripts/consolidate.py) - validate raw entries and propose consolidation
- [scripts/test_consolidate.py](scripts/test_consolidate.py) - malformed-file and date regressions
- [scripts/test_consolidate_queue.py](scripts/test_consolidate_queue.py) - aged-lesson queue, deferred marker and receipt regressions
- [scripts/bulk_wire.py](scripts/bulk_wire.py) - mechanical loop wiring helper
- [scripts/test_bulk_wire.py](scripts/test_bulk_wire.py) - template parity, dry-run, and preservation regressions
- [scripts/install_capture_hook.py](scripts/install_capture_hook.py) - idempotent installer for the Layer 1 capture hook (Claude `SessionEnd`; Codex `Stop` only with `--codex`)
- [scripts/test_capture_hook.py](scripts/test_capture_hook.py) - detached-worker and tool-free reflection regressions
- [assets/learnings.template.md](assets/learnings.template.md) - starter consolidated file
- [assets/learnings_capture.py](assets/learnings_capture.py) - runtime-neutral Layer 1 capture hook (source of truth; installed to `$HOME/.agents/hooks/`)

## Related Skills

- `agents-skills` — for creating or auditing the host skill itself.
- `agents-memory` — for cross-skill, cross-session memory (the 4-type schema this loop scopes from).
- `agents-hooks` — the session-end-hook mechanism behind Layer 1 auto-capture (see `references/closed-loop-capture.md`).
