# Promotion Protocol (Layer 3 — eval-gated)

Promotes a load-bearing entry from `learnings.consolidated.md` → the host
skill's `references/` (or, rarely, a hand edit to `SKILL.md`). This is the
*promotion-out* step from `consolidation-protocol.md` step 5. Layer 3 adds the
objective gate that step never had: **no promotion without a passing,
falsifiable regression eval.**

Human-in-the-loop and human-triggered. There is no hook and no schedule — like
consolidation, promotion is a deliberate maintenance action.

## Why this layer exists

Without it, "this principle is durable enough to change the skill" is pure
operator judgment with no backstop. The established state of practice for skill quality (see `references/evidence-base.md`) is eval-gated promotion: a candidate change must pass a regression eval
before it enters skill logic. This layer is the conservative, zero-cost form of
that: the human still writes and approves everything; the script only refuses
promotions whose claimed benefit cannot be demonstrated.

## Triggers

- A consolidated entry has been stable and load-bearing for 3+ cycles
  (consolidation-protocol.md step 5 flags it).
- Before a PR that intentionally bakes a learning into the host skill.
- Never automatically. Promotion is opt-in per principle.

## Procedure

1. **Pick the consolidated entry** you believe should become skill logic.
2. **Author the eval.** Copy `assets/promotion-eval.template.md` into
   `<host-skill>/promotion-evals/<slug>.json`. Capture a *real* behavior sample
   with the principle applied and the *real* pre-principle baseline.
3. **Self-check it:**
   `python3 scripts/promote_learning.py <skill-dir> --check <slug>.json`.
   Fix until it reports *discriminating*.
4. **Run the gate:**
   `python3 scripts/promote_learning.py <skill-dir> --gate "<principle text>"`.
   - Pass → it prints the exact manual edit and logs to
     `learnings.promotions.jsonl`.
   - Refuse → it names why (missing / non-falsifiable / broken / inverted).
     Do not promote. Fix the eval or abandon the promotion.
5. **Do the edit by hand** as printed: add to `references/`, delete from
   `learnings.consolidated.md`. The script will not touch either file.
6. **Keep the eval forever.** It is now a regression eval. Add
   `python3 scripts/promote_learning.py <skill-dir> --audit` to the pre-PR
   checks for that skill so a later change cannot silently regress it.

## What the script will and will not do

| Action | Script does it | Human does it |
|---|---|---|
| Validate eval structure | ✅ | |
| Verify the eval is falsifiable (discriminating) | ✅ | |
| Run the eval (deterministic, zero cost) | ✅ | |
| Decide promotion is *allowed* | ✅ (gate) | |
| Author the eval + capture real samples | | ✅ |
| Edit host skill `references/` or `SKILL.md` | ❌ never | ✅ |
| Delete from `learnings.consolidated.md` | ❌ never | ✅ |
| Append to the promotion ledger on a pass | ✅ | |

## Grading: deterministic by default

The gate uses substring / regex / equality / json-path assertions — no model,
no cost, capability-agnostic. Use `grader: "model"` only when the behavior
genuinely needs judgment, and then `PROMOTION_EVAL_CMD` must be set; the gate
**refuses rather than silently passing** if a model grader is declared with no
command (fail loud — coding-behavior Rule 12).

## Stop conditions

Stop and surface, do not push through, if:

- The eval passes only because the assertion restates the principle text rather
  than checking an observable behavior — that is non-discriminating in spirit
  even if the script's mechanical check passes; rewrite the assertion.
- You cannot produce a real `without_principle` baseline (you have no evidence
  the skill ever behaved worse) — then the principle is unproven; keep it in
  consolidated, do not promote.
- The principle contradicts the host skill's current `SKILL.md` — resolve by a
  reviewed skill edit, not by promoting a contradiction.
- The host skill was renamed or removed — the loop and its evals are orphaned;
  delete them.

## Anti-patterns

- **Promoting without an eval.** The whole point. `--gate` refuses; do not
  hand-edit around it.
- **Auto-editing `SKILL.md`.** Still forbidden at Layer 3. The gate authorizes a
  human edit; it never performs one. Silent self-modification is the failure
  mode the entire loop exists to prevent.
- **Deleting a promotion eval to "clean up".** It is a permanent regression
  test. Removing it un-gates a future regression.
- **Model grader for a check a regex can make.** Pay nothing for deterministic
  decisions (coding-behavior Rule 5).
