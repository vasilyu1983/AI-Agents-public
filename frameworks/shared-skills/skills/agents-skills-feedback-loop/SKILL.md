---
name: agents-skills-feedback-loop
description: Adds per-skill learnings loops for dated patterns, mistakes, and domain facts. Use when wiring skill memory, consolidation, or drift audits.
version: "1.1"
last_validated: 2026-07-11
---

# Agent Skills — Feedback Loop

Use this skill to wire a **learnings loop** into another skill so it gets better with use, without rewriting `SKILL.md` automatically.

The loop has four moving parts:

1. **`learnings.md`** — raw, append-only, committed. Shared working memory across machines; created on first append via `append_learning.py`, not seeded empty.
2. **`learnings.consolidated.md`** — pruned, dated, committed. Portfolio-grade institutional memory; seeded at wiring time.
3. **`learnings.local.md`** — machine-specific notes, gitignored. Use for one-operator-on-one-machine context that should not propagate.
4. **`scripts/append_learning.py` + `scripts/consolidate.py`** — keep raw entries well-shaped and promote durable ones to consolidated.

The name is borrowed from the 2026 "learnings loop" pattern (MindStudio) and Anthropic's own skill-authoring guidance to ask Claude to self-reflect on what went wrong and fold it back into reusable context. **The mechanism deliberately does not match MindStudio's**: MindStudio's loop has the model rewrite the skill's persistent instructions directly from user corrections — that is the exact auto-rewrite this design forbids (see Anti-Patterns). This skill keeps the same "accumulate corrections across sessions" shape but routes it through append-only raw entries, human-reviewed consolidation, and an eval-gated promotion step before anything touches skill logic — mapped onto this repo's existing 4-type memory schema (see `agents-memory`).

## Quick Reference

| Task | Read or Run | Outcome |
|------|-------------|---------|
| Wire a skill to use the loop | `references/wiring-protocol.md` | Adds a 4-line addendum to that skill's `SKILL.md`, seeds files |
| Format a new learning entry | `references/learnings-format.md` | Atomic, dated, 5-section schema that survives pruning |
| Promote raw → consolidated | `python3 scripts/consolidate.py <skill-dir>` | Dedup, age out, surface recurring patterns for human review |
| Append a learning safely | `python3 scripts/append_learning.py <skill-dir> --section <name> --text "..."` | Validates shape, dates, refuses to grow past the 150-entry cap |
| Audit drift across skills | `references/audit-checklist.md` | Find stale loops, missing consolidations, oversized files |
| Capture a cross-cutting behavior with no obvious skill home | `references/instinct-pattern.md` | Atomic, confidence-scored complement to the per-skill loop above |

## Workflow

1. Confirm the host skill should have a learnings loop; do not wire routers, one-off scaffolds, or stable skills with no recurring edge cases.
2. Follow `references/wiring-protocol.md` to seed `learnings.consolidated.md`, add the addendum, and verify `.gitignore` coverage.
3. Use `scripts/append_learning.py` for raw entries; do not hand-edit raw `learnings.md` during normal operation.
4. Use `scripts/consolidate.py <skill-dir>` when the raw file hits the cap, before release, or during a scheduled maintenance pass.
5. Promote durable lessons into the host skill's `references/` only after human review; never auto-rewrite `SKILL.md`.

## ASCII Flow

```text
Learning-loop request
  -> Check host skill fit
     +-- router/one-off/stable surface -> do not wire
     +-- recurring edge cases          -> seed consolidated file and addendum
  -> Append raw dated bullets via script
  -> Consolidate when capped, stale, or release-bound
  -> Promote durable rules by human-reviewed reference edits
```

## When to Use

- A skill is high-traffic and you keep teaching it the same lesson twice
- A skill's domain has emerging edge cases you want captured (e.g. tax rules, payment scheme changes, new API quirks)
- A skill failed and you asked Claude to self-reflect — the reflection needs a home

## When NOT to Use

- One-off skills, internal scaffolding, or skills with stable, well-known surfaces
- Skills whose "learnings" are actually just code conventions — those belong in `CLAUDE.md` or `coding-behavior.md`, not a per-skill loop
- Cross-skill patterns — promote to `references/` of the right skill or to `agents-memory`, not into every learnings file

## Typical Scenarios

End-to-end recipes. Each maps to the machinery below — no new commands.

**1. Wire a high-traffic domain skill for the first time.**
You keep re-teaching `project-taxation` the same HMRC quirks. Seed the loop, add
the addendum, smoke-test:
```bash
cp frameworks/shared-skills/skills/agents-skills-feedback-loop/assets/learnings.template.md \
   frameworks/shared-skills/skills/project-taxation/learnings.consolidated.md
# add the ## Learnings Loop addendum to project-taxation/SKILL.md (verbatim, see The Addendum)
python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/append_learning.py \
   frameworks/shared-skills/skills/project-taxation --section "Domain Knowledge" \
   --text "MTD quarterly update deadline is 1 month + 7 days after period end."
```
Full procedure: `references/wiring-protocol.md`. Add a per-skill filter override
if the domain needs a sharper bar (HMRC-anchored only, etc.).

**2. A skill just failed — capture the lesson before it evaporates.**
The session hit a non-obvious bug. Append one dated bullet to the right section;
do not edit `SKILL.md`:
```bash
python3 .../append_learning.py frameworks/shared-skills/skills/<skill> \
   --section "Mistakes to Avoid" \
   --text "Webhook needs HMAC in the header, not the body — body-signed requests 401."
```
If you wired Layer 1 (scenario 5), this happens automatically at session end.

**3. The raw file is full / weekly maintenance.**
`append_learning.py` refused at 150 entries, or it's your Friday cadence. Dry-run,
review, consolidate:
```bash
python3 .../consolidate.py frameworks/shared-skills/skills/<skill> --dry-run   # propose
python3 .../consolidate.py frameworks/shared-skills/skills/<skill>             # apply after review
```
Promotion criterion: an insight must have recurred ≥2× before it consolidates.
Full protocol: `references/consolidation-protocol.md`.

**4. Promote a battle-tested principle into the host skill (Layer 3).**
A consolidated entry has been load-bearing for 3+ cycles. It cannot enter skill
logic without a *discriminating* regression eval:
```bash
# author <slug>.json from assets/promotion-eval.template.md, then:
python3 .../promote_learning.py frameworks/shared-skills/skills/<skill> --check <slug>.json
python3 .../promote_learning.py frameworks/shared-skills/skills/<skill> --gate "<principle text>"
```
On a pass it prints the exact hand edit and logs to `learnings.promotions.jsonl`;
it never edits `SKILL.md`. Full protocol: `references/promotion-protocol.md`.

**5. Onboard a new laptop — close the capture loop automatically (Layer 1).**
Stop relying on humans to remember to append. Install the portable session-end
hook (registers Claude Code `SessionEnd` + Codex if present):
```bash
cd frameworks/shared-skills/skills/agents-skills-feedback-loop
python3 scripts/install_capture_hook.py --dry-run   # preview
python3 scripts/install_capture_hook.py             # apply
cat ~/.agents/hooks/learnings_capture.log           # capture-rate gauge
```
Caveat: confirm your runtime's hook event actually fires before trusting capture
(see `references/closed-loop-capture.md` → Verifying it works). Codex hook
support is newer and less stable than Claude's — treat the log as the source of
truth, not the design doc.

**6. Monthly drift audit across every wired skill.**
Catch orphaned loops, oversized files, undated entries in one pass:
```bash
for skill in frameworks/shared-skills/skills/*/; do
  [ -f "$skill/learnings.consolidated.md" ] && \
    python3 .../consolidate.py "$skill" --audit
done
```
Anything not `status=ok` needs a human pass. Full checklist:
`references/audit-checklist.md`.

## Core Contract

Per-skill, the loop lives inside the skill's own directory:

```
<skill>/
├── SKILL.md                       # adds the 4-line Learnings Loop addendum
├── learnings.md                   # committed, append-only, raw (shared across machines)
├── learnings.consolidated.md      # committed, pruned, dated
├── learnings.local.md             # gitignored, machine-specific, optional
└── references/...                 # consolidation can promote durable rules here
```

Required entry shape (enforced by `append_learning.py`):

- `- [YYYY-MM-DD] <one-sentence atomic insight>`
- One bullet, one insight. No paragraphs.
- Belongs to exactly one section: *Patterns That Work / Mistakes to Avoid / Domain Knowledge / Open Questions / Consolidated Principles*.

Hard limits (refuse rather than truncate):

- Raw `learnings.md` cap: **150 entries** — exceeding triggers a forced consolidation pass.
- Consolidated file cap: **60 entries** — exceeding means the skill itself needs a `references/` extraction.

## The Addendum

Any skill that opts in adds this block, verbatim, near the end of its `SKILL.md`:

```markdown
## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
```

That's it — no other change to the host skill.

## Consolidation Cadence

- **Trigger:** raw file hits the 150-entry cap, OR a weekly cron (recommended: Friday), OR before a release/PR that touches the skill.
- **Protocol:** see `references/consolidation-protocol.md`. Human approves promotions to `learnings.consolidated.md`.
- **Promotion criterion:** an entry must have triggered behavior change *at least twice* (manually noted by the operator) before it is consolidated. Single-occurrence entries age out after 90 days.

## Monthly Maintenance Checklist

Run these checks on any skill with an active loop:

- [ ] `python3 scripts/consolidate.py <skill-dir> --audit` — confirm raw ≤150 and consolidated ≤60
- [ ] Verify every entry starts with `- [YYYY-MM-DD]` (no undated bullets)
- [ ] Confirm `SKILL.md` still carries the `## Learnings Loop` addendum
- [ ] Scan for entries older than 90 days with no recurrence; flag for pruning
- [ ] Check for consolidated entries stable for 3+ cycles; run `scripts/promote_learning.py --gate` before promoting
- [ ] Confirm `learnings.md` and `learnings.consolidated.md` are committed, and `learnings.local.md` is the only gitignored learnings file
- [ ] Run the full loop audit across all wired skills (copy the `for` loop from `references/audit-checklist.md`)

## Lint Commands

```bash
# Audit a single wired skill (checks caps, dates, section names)
python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/consolidate.py \
  frameworks/shared-skills/skills/<skill-name> --audit

# Audit all wired skills at once
for skill in frameworks/shared-skills/skills/*/; do
  if [ -f "$skill/learnings.consolidated.md" ]; then
    python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/consolidate.py \
      "$skill" --audit
  fi
done

# Dry-run consolidation (proposes diffs, does not write)
python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/consolidate.py \
  frameworks/shared-skills/skills/<skill-name> --dry-run

# Check Layer 3 promotion gate for a specific principle
python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/promote_learning.py \
  frameworks/shared-skills/skills/<skill-name> --gate "<principle text>"
```

## Closing the Capture Loop (Layer 1)

The base loop above is **open**: without a session-end hook, every append requires a human to manually call `append_learning.py`. In practice raw files stay near-empty. Layer 1 closes the
*capture* half with a runtime-neutral session-end hook that detects which wired
skills a session used, runs one cheap reflection pass, and appends via the
existing `append_learning.py` — no new format, no `SKILL.md` rewrite.

It is **machine-global and portable** (any laptop, any username) and covers
**both Claude Code and Codex** from one script:

```bash
# From this skill directory, on any laptop:
python3 scripts/install_capture_hook.py --dry-run   # preview
python3 scripts/install_capture_hook.py             # apply
```

The installer resolves every path from `$HOME` at run time (nothing is
hardcoded), registers Claude Code (`SessionEnd`) and Codex (`Stop`, only if
Codex is present), and is idempotent. Full design, guardrails (recursion guard,
blast-radius limit, fail-silent-fail-logged), and verification:
[references/closed-loop-capture.md](references/closed-loop-capture.md).
Layers 2 (scheduled consolidation) and 3 (eval-gated promotion) remain manual.

## Eval-Gated Promotion (Layer 3)

Consolidation (Layer 2) ends at `learnings.consolidated.md`. The *next* step —
baking a load-bearing principle into the host skill's `references/` — was a
pure human judgment call with no objective backstop. Layer 3 closes the
*promotion* half with a **gate**, not an automator:

```bash
python3 scripts/promote_learning.py <skill-dir> --gate "<principle text>"
```

A principle cannot be promoted unless it has a registered regression eval that
is **discriminating** — it passes with the principle applied *and* fails
without it. An eval that cannot fail when the principle is reverted is invalid
(coding-behavior Rule 9). Grading is **deterministic and zero model cost** by
default (capability-agnostic; `PROMOTION_EVAL_CMD` opt-in for model grading,
which fails loud rather than silently passing if unset).

The gate **never edits `SKILL.md` or `references/`** — like `consolidate.py`,
promotion-out stays a human edit; the gate only decides whether the human is
*allowed* to make it, prints the exact edit on a pass, and logs to
`learnings.promotions.jsonl`. Re-run `--audit` before any PR touching the skill;
a promoted principle's eval is now a permanent regression test. Full protocol:
[references/promotion-protocol.md](references/promotion-protocol.md).

## Complementary Pattern: Atomic Instincts

The loop above works at **skill granularity** — one `learnings.md` per skill. It has a gap: behavioral observations that don't belong to any one skill (e.g. "always `grep` before editing a file this large," "this repo prefers functional style") have no natural skill home and go uncaptured. `references/instinct-pattern.md` documents a smaller-granularity complement — a single-trigger, single-action, confidence-scored (0.3–0.9), domain-tagged, project-or-global-scoped unit — adapted from [affaan-m/ECC](https://github.com/affaan-m/ECC) (commit `51a6950`, MIT). It does not replace the loop above, does not adopt ECC's automatic project→global promotion (this repo keeps promotion human-gated, per `## Anti-Patterns` and Rule 7 of `coding-behavior.md`), and is documented as a scaffold and capture-mechanism only — no seeded example entries. For hook mechanics, see `agents-hooks`.

## What Counts as a Learning (the filter)

The filter is project-specific. The default filter lives in `references/learnings-format.md` under *Quality Filters*. Override per-skill if your domain needs a sharper bar — e.g. `project-taxation` should reject anything not anchored to an HMRC manual reference or a dated statute.

## Judgment Calls (what a non-expert misses)

The mechanics above (caps, dates, dedup ratio) are checkable by script. The following are not, and are where most wired loops actually fail:

- **A quiet loop is not a healthy loop.** `--audit` reporting `status=ok` only means the files are in shape — it does not mean the loop is being used. Cross-check `raw=0` or a stale `oldest` date against how often the host skill is actually invoked (check recent transcripts or the Layer 1 log). A high-traffic skill with zero raw entries after 60+ days almost always means the addendum stopped firing (someone edited it out, or nobody reads `learnings.consolidated.md` before applying the skill) — not that nothing went wrong. Silence is a signal, not an all-clear.
- **`consolidate.py`'s duplicate clustering is syntactic, not semantic.** It clusters near-identical wording (`SequenceMatcher` ratio ≥0.82); it will not notice that "webhook needs HMAC in header" and "signature must be in the request header, not the payload" are the same lesson said twice. Treat the script's promotion proposals as a *first pass*, not the ground truth for "recurred ≥2×" — a human still has to read the raw file once per cycle to catch semantically-duplicate entries the ratio threshold misses, and to catch the reverse: two genuinely different lessons that happen to share vocabulary and get wrongly clustered.
- **Signal vs. noise is a counterfactual test, not a vibe.** Before appending, ask: if the *next* session had read this bullet first, would it have behaved differently? If the answer is no — it's an interesting observation, a diary entry, or something already obvious from reading the skill's `SKILL.md` — it's noise. Reject it even if it feels insightful; a loop that accepts "interesting" over "load-bearing" degrades into the exact ACE-paper failure mode ("context collapse" / "brevity bias" per `references/evidence-base.md`) where volume drowns out the few entries that matter.
- **Recurring entries that never get consolidated are a maintenance failure, not a filter failure.** If the same lesson keeps getting re-appended in raw form across cycles instead of being promoted to consolidated, the operator is skipping consolidation, not writing bad entries. Check the cadence (`## Consolidation Cadence`) before tightening the filter.
- **A loop that never nominates anything for Layer 3 promotion after 6+ months is not necessarily disciplined** — it may mean nobody is running the promotion-out step in `consolidation-protocol.md` step 5. Distinguish "genuinely no principle was load-bearing enough" from "the human-gate step is a dead letter" by checking whether `learnings.consolidated.md` itself is stuck at the same size cycle over cycle.
- **Cross-skill leakage is easiest to miss in shared-vocabulary domains.** A payments skill and a compliance skill both use words like "reconciliation" or "settlement" — a consolidated entry that reads correctly in isolation can still be the wrong skill's fact. When auditing, ask whether the entry is true *because of this skill's domain* or merely *phrased in this skill's vocabulary*.

## Anti-Patterns

- **Auto-rewriting SKILL.md.** The loop never modifies `SKILL.md`. If consolidation produces a durable rule, promote it to `references/` by hand. Silent self-modification of skills is the failure mode this design exists to prevent.
- **One central learnings file across all skills.** Forbidden. `project-cosmic-tarot` learnings must not leak into `software-payments`. See `feedback_project_skills_independent`.
- **Learnings that duplicate `CLAUDE.md` or `coding-behavior.md`.** General coding rules belong in those files, not in a per-skill loop.
- **Undated entries.** Without a date the entry cannot age, cannot be pruned, and cannot be weighted. Reject on append.

## Compatibility

- Portable across Claude Code and Codex (no runtime-specific frontmatter).
- Scripts are Python 3.10+, stdlib only.
- Hosts skill can be any prefix family (`project-*`, `software-*`, `marketing-*`, etc.).

## Navigation

- [references/wiring-protocol.md](references/wiring-protocol.md) - five-step host-skill wiring procedure
- [references/learnings-format.md](references/learnings-format.md) - entry schema, section names, and quality filters
- [references/consolidation-protocol.md](references/consolidation-protocol.md) - deduplication, pruning, and human-review promotion path
- [references/audit-checklist.md](references/audit-checklist.md) - monthly loop drift checks
- [references/closed-loop-capture.md](references/closed-loop-capture.md) - Layer 1 auto-capture hook design, guardrails, install, and verification (Claude Code + Codex, portable)
- [references/promotion-protocol.md](references/promotion-protocol.md) - Layer 3 eval-gated promotion: gate rule, falsifiability requirement, human edit path
- [references/evidence-base.md](references/evidence-base.md) - graded May-2026 source provenance for the maturity claims and the Layer 1/3 designs
- [references/instinct-pattern.md](references/instinct-pattern.md) - atomic, confidence-scored instinct pattern (complement to the per-skill loop, adapted from affaan-m/ECC)
- [scripts/append_learning.py](scripts/append_learning.py) - append raw dated entries
- [scripts/consolidate.py](scripts/consolidate.py) - audit and consolidate raw entries
- [scripts/promote_learning.py](scripts/promote_learning.py) - Layer 3 eval gate; refuses promotion without a discriminating regression eval (never edits SKILL.md)
- [scripts/bulk_wire.py](scripts/bulk_wire.py) - mechanical loop wiring helper
- [scripts/install_capture_hook.py](scripts/install_capture_hook.py) - idempotent installer for the Layer 1 capture hook (registers Claude `SessionEnd` + Codex `Stop`)
- [assets/learnings.template.md](assets/learnings.template.md) - starter consolidated file
- [assets/learnings_capture.py](assets/learnings_capture.py) - runtime-neutral Layer 1 capture hook (source of truth; installed to `$HOME/.agents/hooks/`)
- [assets/promotion-eval.template.md](assets/promotion-eval.template.md) - Layer 3 regression-eval case schema + worked example and anti-patterns

## Fact-Checking

- Verify current Claude Code, Codex, and skill-runtime behavior against official docs before making claims about automatic reflection, hooks, compaction, or skill invocation semantics.
- Treat third-party learnings-loop examples as pattern evidence only; review provenance before installing or recommending automation. Graded source provenance for the maturity and design claims is in `references/evidence-base.md`.
- Do not store secrets, PII, customer-specific facts, or unreleased client details in either raw or consolidated learnings files.

## Related Skills

- `agents-skills` — for creating or auditing the host skill itself.
- `agents-memory` — for cross-skill, cross-session memory (the 4-type schema this loop scopes from).
- `agents-hooks` — the session-end-hook mechanism behind Layer 1 auto-capture (see `references/closed-loop-capture.md`).
