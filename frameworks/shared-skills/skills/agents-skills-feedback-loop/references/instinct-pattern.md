# The Instinct Pattern (Cross-Cutting, Atomic Complement)

**Source**: [affaan-m/ECC](https://github.com/affaan-m/ECC), commit `51a6950`, MIT license. Pattern extracted 2026-08-09 via `research-scout`; see `docs/research/2026-08-09-skill-ecc-scan.md` in this repo for the full scan.

## What This Is Not

This is **not** a replacement for the learnings loop above, and it is **not** a second wiring procedure to run alongside it. The base loop already solves "a skill gets better with use" at skill granularity: one `learnings.md` per skill, human-reviewed before anything is promoted. That stays the primary mechanism for anything with an obvious skill home.

The instinct pattern targets a narrower gap: **behavioral observations that don't belong to any one skill.** "Always `grep` before editing a file this large," or "this repo prefers functional style over classes," are true across every skill invocation in a given project — they have no natural `learnings.md` to live in, and under the base loop alone they simply go uncaptured.

## The Pattern

ECC's `continuous-learning-v2` skill defines an **instinct** as a single atomic unit:

| Field | Shape |
|---|---|
| Trigger | One specific situation ("editing a file over 500 lines") |
| Action | One specific behavior ("read the full file first, not just the diff hunk") |
| Confidence | A score in **0.3–0.9**, not binary — reflects how consistently the behavior held |
| Domain tag | What area it applies to (e.g. `editing`, `git`, `testing`) |
| Scope | `project` (default) or `global` |

This is a materially smaller unit than a `learnings.md` bullet: one trigger, one action, nothing else. Where a learnings entry can carry context and rationale in a full sentence, an instinct is closer to a compiled rule — cheap to store, cheap to check against, and cheap to discard if it turns out wrong.

**Capture mechanism**: ECC captures instincts continuously via `PreToolUse`/`PostToolUse` hooks rather than only at session end — every tool call is a potential observation point, not just the closing reflection. A background low-cost model (ECC uses Haiku) does the extraction pass so the main session's context budget isn't spent on introspection. ECC's own docs describe the hook-based capture as "100% reliable" — treat that as a vendor claim from the source repo, not a verified fact; this repo has not independently confirmed it, and `agents-hooks` itself notes reliability gaps exist across runtimes (Codex `hooks.json` in particular; see `agents-hooks/SKILL.md`).

**Promotion**: ECC promotes an instinct from `project` scope to `global` scope automatically once it has been observed in 2+ separate projects.

## Where the Mechanics Live

This reference documents the *shape* of the pattern, not a second hook-wiring guide. For the actual mechanics of writing a `PreToolUse`/`PostToolUse` hook — event syntax, matchers, async vs. blocking, payload mutation — see `agents-hooks` (`references/closed-loop-capture.md` in this skill already uses the same session-end hook surface for Layer 1 capture; the instinct pattern would extend that to per-tool-call events instead of session-end only).

## What This Repo Deliberately Does Not Adopt

Per coding-behavior Rule 7 (surface conflicts, don't average them) and this skill's own stance in `## Anti-Patterns` above:

- **No automatic project → global promotion.** This repo's entire design is human-reviewed consolidation and an eval-gated promotion step (`references/promotion-protocol.md`) before anything touches skill logic. ECC's "observed in 2+ projects, promote automatically" rule conflicts with that gate directly. If this pattern is adopted, promotion to global scope goes through the same human-in-the-loop review as any other consolidated principle — never an automatic count-based trigger.
- **No claim that hook-based capture is "100% reliable."** Restate as: hook-based capture is *more continuous* than session-end-only capture, with the same runtime-reliability caveats already documented in `agents-hooks`.
- **No auto-rewrite of `SKILL.md` or any skill logic from instincts.** Same anti-pattern this skill already forbids for the base loop applies here without exception.

## What Belongs Where (Decision Guide)

| Observation | Home |
|---|---|
| Recurring correction tied to one specific skill's domain | Base loop — that skill's `learnings.md` |
| Recurring behavior that holds across skills, tied to *this project/repo* | Instinct, `project` scope |
| Recurring behavior confirmed across 2+ *unrelated* projects, human-reviewed | Candidate for `agents-memory` or `coding-behavior.md`, promoted by a person — not auto-promoted |
| One-off observation, unlikely to recur | Neither. Discard (same "signal vs. noise" bar as `## Judgment Calls` above) |

## Status of This Addition

This file documents the **scaffold and capture-mechanism concept only**. It does not seed example instinct entries, install a hook, or claim any instinct has been captured — doing so would fabricate field-use evidence that never happened, which this repo treats as a fail-loud violation regardless of intent. A concrete instinct-capture implementation (storage location, script, hook wiring) is a separate, later decision to make only once a real cross-cutting behavioral pattern is actually observed and worth capturing — not something to pre-populate here to make the loop look active.

## Attribution

```json
{
  "name": "ECC (Everything Claude Code) — continuous-learning-v2",
  "url": "https://github.com/affaan-m/ECC",
  "commit_sha": "51a6950bde756fe3ebc8879aa0c8ee49b9c53e78",
  "license": "MIT",
  "extracted_date": "2026-08-09",
  "pattern_used": "confidence-scored-atomic-instincts"
}
```
