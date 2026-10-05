# Mode-collapse Suite

Detects response convergence across structurally diverse prompts. The
signal is *cross-prompt similarity* — if two unrelated prompts produce
similar responses, the agent is collapsing.

## Run

```bash
ANTHROPIC_API_KEY=... \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/mode_collapse -v -s
```

## Cost guard

The default 12-prompt dataset is one LLM call per prompt — about 12 calls
per full run. With `claude-haiku-4-5` and short responses,
estimate cost as calls × tokens × the model's current price before running.

Override with `MODE_COLLAPSE_MODEL=...` to test a different model.

## Pass criteria (defaults)

- Minimum cross-prompt Jaccard distance ≥ `MODE_COLLAPSE_FLOOR` (default 0.4).
  0.4 is permissive; for production gates, raise it as your dataset grows.
- At least one prompt pair must be evaluated.

## Reading a failure

```
[mode-collapse rollup]
  cross-prompt pairs evaluated: 66
  mean Jaccard distance:         0.71
  min  Jaccard distance:         0.32
  3 flagged pairs (too similar; showing up to 5):
    - d=0.32  'Explain Postgres indexes…'  ↔  'What does this regex do…'
    ...
```

Map the flagged pairs back to causes:

- **Pairs are technical-explanation prompts** — likely the system prompt
  enforces a heavy template. Loosen the structure.
- **Pairs span very different topics** — likely the model is reaching for
  a default phrasing. Check whether you've recently swapped models or
  added a "be helpful and concise" preamble that flattens style.
- **Failure correlates with adding a memory layer** — A26 (mode-collapse
  loop from self-extracted preferences). Audit whether the memory store
  is extracting facts from assistant turns.

## Why no within-prompt-variance test

Same prompt, N runs at temperature > 0 should produce non-identical
responses. That is mostly a temperature configuration check, not a
context-layer regression signal. We test it implicitly: the suite runs
at temperature 0.4, and if the cross-prompt distances are zero, that
implies within-prompt variance is also zero, which would mean the LLM
adapter is sampling deterministically by mistake — a bug worth catching
but not the mode-collapse story.

## Extending the dataset

Each line of `dataset.jsonl` is one prompt:

```json
{"prompt_id": "...", "prompt": "..."}
```

Rules:
- Prompts must be **structurally diverse** — explanation, list, code,
  rewrite, choice, math, etc. The whole point is to make collapse
  visible, which only works if the prompts have nowhere to converge to
  by content.
- Avoid prompts that naturally produce similar outputs (e.g. two
  "explain X" prompts where X is closely related).
- Keep responses short — long responses dominate the Jaccard set with
  filler words and dilute the signal.
