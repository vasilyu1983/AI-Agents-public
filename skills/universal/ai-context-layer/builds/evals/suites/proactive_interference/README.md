# Proactive-interference Suite (F5)

A deterministic regression guard on the F5 mitigation invariant
(`references/context-hygiene.md` §F5). Proactive interference: when a
slot's value changes over time, accumulating *sibling* memory rows for
the same semantic key suppress recall of the current value. The
documented defense is **superseding / version-tagged slots** — a new
value invalidates the prior (`forget` + `supersedes_id`) instead of
coexisting with it.

No API key, no LLM, no cost guard — this suite tests the *store
discipline*, not a model. It mirrors the `postgres` / `jit_loading`
invariant suites, not the LLM-driven `context_rot` suite.

## Run

```bash
PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/proactive_interference -v -s
```

`-s` prints the naive-path degradation rollup, which is the useful
artifact when a slot regresses.

## What it asserts

1. **Defended invariant (load-bearing).** Under the superseding
   discipline, `recall` returns exactly one row whose value is the
   current value, at every interference tier (`0, 1, 3, 8, 24` stale
   priors). If supersession logic regresses (priors stop being
   invalidated) this collapses to the naive path and the test fails.
2. **Anti-tautology (Rule 9).** The naive sibling-accumulating store
   must demonstrably degrade — at the highest tier it returns more than
   one live row per slot. If that stops being true (e.g. the store
   starts auto-deduping), the suite would otherwise pass as a no-op;
   this assertion fails loudly instead.

## Pass criteria

- Test 1 passes iff the superseding path is unique-and-current for every
  case at every tier.
- Test 2 passes iff every multi-value slot is ambiguous at tier 24.

## Reading a failure

```
slot=user_current_city tier=8 expected exactly ['Reykjavik'] got ['Berlin','Lisbon',...]
```

- Failure in test 1 → the supersession path is no longer tombstoning
  priors. Inspect `find_contradictions` + `forget` wiring in your
  memory adapter and the P14 consolidation job (it must tombstone
  prior-version rows, not coexist with them).
- Failure in test 2 → `FakeMemoryStore.recall` (or your real adapter
  under test) silently deduped; the suite is not exercising real
  interference. Fix the harness before trusting test 1.

## Extending

Add a line to `CASES` in `test_proactive_interference.py`. Keep each
slot a single `(entity_id, memory_type)` so its values genuinely collide
at recall time; `history` is ordered oldest → newest and the last
element is the current value.
