# Consolidation Protocol

Promotes entries from raw `learnings.md` → curated `learnings.consolidated.md`. Human-in-the-loop. Run on trigger, not on every session.

## Triggers

- Raw file hits 150 entries (forced).
- Weekly cadence (recommended Friday).
- Before any PR that materially changes the host skill's `SKILL.md` or `references/`.

## Procedure

1. **Read both files.** Raw and consolidated, in full.
2. **Run `python3 scripts/consolidate.py <skill-dir> --dry-run`** — outputs a proposed diff: candidates for promotion, candidates for pruning, candidates for merging.
3. **Apply the *promotion criterion*:** an entry is promotable only if it has triggered behavior change *at least twice*. The operator marks recurrences by re-appending the same insight on a new date; `consolidate.py` clusters near-duplicates and flags clusters of size ≥2.
4. **Apply the *aging criterion*:** any entry older than 90 days with no recurrence is flagged for removal.
5. **Apply the *promotion-out criterion*:** if a consolidated entry has been stable and load-bearing for 3+ cycles, promote it out of the loop entirely — into the host skill's `references/`. This step is **eval-gated** (Layer 3): run `scripts/promote_learning.py <skill-dir> --gate "<entry>"` first; it refuses unless a discriminating regression eval exists. Only after the gate opens do you make the hand edit and delete from consolidated. Full procedure: `promotion-protocol.md`.
6. **Human review.** Operator approves or rejects each proposed change. The script does not commit by default.
7. **Re-date promoted entries** to today's date in consolidated, with a `(seen Nx since YYYY-MM-DD)` annotation. Keeps freshness weighting accurate.

## What the Script Will and Will Not Do

| Action | Script does it | Human does it |
|---|---|---|
| Find near-duplicate clusters | ✅ | |
| Propose promotions | ✅ | |
| Approve promotions | | ✅ |
| Edit `SKILL.md` of host skill | ❌ never | ✅ |
| Move entries to `references/` | ❌ never (but Layer 3 gates the human edit) | ✅ after `promote_learning.py --gate` opens |
| Delete from raw | ✅ after approval | |
| Append to consolidated | ✅ after approval | |

## Why Human-in-the-Loop

Silent self-modification of skills is the exact failure mode this loop exists to prevent. The script makes promotion *cheap*, not *automatic*. A skill that rewrites its own instructions without review will drift, and the drift will be invisible until it produces a bad output. Keep the human gate.

## Stop Conditions

Stop and surface, do not push through, if:

- The consolidated file would exceed 60 entries after this cycle.
- Two entries in different sections describe the same underlying rule (resolve by choosing the right section).
- An entry contradicts the host skill's `SKILL.md` (resolve by editing the skill, not the loop).
- The host skill no longer exists or has been renamed (loop is orphaned — delete it).
