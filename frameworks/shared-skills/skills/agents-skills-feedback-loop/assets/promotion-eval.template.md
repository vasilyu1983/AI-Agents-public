# Promotion Eval Case — Authoring Template (Layer 3)

A promotion eval is the regression test that **gates** moving a consolidated
principle into a skill's `references/`. One JSON file per principle, stored at:

```
<host-skill>/promotion-evals/<short-slug>.json
```

`scripts/promote_learning.py` runs it. The gate opens **only** if the eval is
*discriminating*: the behavior sample **with** the principle applied satisfies
the assertion, and the sample **without** it does not. An eval that passes even
without the principle proves nothing and is rejected (coding-behavior Rule 9 —
a test that cannot fail when the requirement is reverted is invalid).

## Schema

```json
{
  "skill": "<host-skill-name>",
  "principle": "<the consolidated.md line being promoted, verbatim, no date prefix>",
  "scenario": "<the concrete task/input that exercises this principle>",
  "grader": "deterministic",
  "assertion": { "type": "contains", "pattern": "<substring|regex|a.b==v>" },
  "samples": {
    "with_principle": "<observed skill behavior WITH the principle — must satisfy the assertion>",
    "without_principle": "<baseline behavior WITHOUT it — must violate the assertion>"
  },
  "recorded_by": "<operator>",
  "date": "<YYYY-MM-DD>",
  "verdict": null
}
```

| Field | Rule |
|---|---|
| `principle` | Exact text of the consolidated entry (whitespace-normalized match is how the gate finds this eval). |
| `grader` | `deterministic` (default, zero model cost) or `model`. `model` needs `PROMOTION_EVAL_CMD` set or the gate refuses — it never silently passes. |
| `assertion.type` | One of: `contains`, `not_contains`, `regex`, `equals`, `json_path`. `json_path` pattern is `dotted.path==expected` over a JSON sample. Ignored when `grader=="model"`. |
| `samples.with_principle` | A *real* captured behavior sample from a run where the principle was applied. Not aspirational prose. |
| `samples.without_principle` | The pre-principle baseline — the actual wrong/worse behavior the principle prevents. This is the falsifiability anchor. |

## Worked example (real principle from research-scout)

```json
{
  "skill": "research-scout",
  "principle": "Discard a vendor 'Nx speedup' claim unless an independent source reproduces it; keep only the architectural shape.",
  "scenario": "Skill evaluates a paper whose only evidence is a vendor blog claiming a 6x speedup, no third-party reproduction.",
  "grader": "deterministic",
  "assertion": { "type": "contains", "pattern": "trap" },
  "samples": {
    "with_principle": "Tagged trap 11 (vendor-claim, unreproduced); evidence grade C; gate=validate, not promote. Architectural shape retained as a candidate.",
    "without_principle": "Strong result — 6x speedup reported. Recommend promote and adopt now."
  },
  "recorded_by": "operator",
  "date": "2026-05-17"
}
```

Here `without_principle` does not contain "trap" → assertion fails without the
principle; `with_principle` does → passes with it. Discriminating ⇒ gate opens.

## Anti-patterns (the gate or review will reject these)

- **Aspirational samples.** Writing what you *hope* the skill says instead of a
  real captured run. The eval then tests your prose, not the skill.
- **Non-falsifiable assertion.** A pattern both samples satisfy. Proves nothing.
- **Restating the principle as the assertion.** The assertion must check an
  *observable behavior*, not whether the principle text appears.
- **Model grader for a deterministic check.** If a substring/regex decides it,
  use `deterministic` — never pay a model for an `if`.
- **Deleting the eval after promotion.** It becomes a permanent regression eval;
  `promote_learning.py <skill> --audit` must keep passing on every later PR.
