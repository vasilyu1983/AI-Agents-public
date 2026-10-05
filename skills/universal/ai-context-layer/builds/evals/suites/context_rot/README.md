# Context-rot Suite

A needle-in-haystack regression detector. For each curated case, builds
prompts at five token tiers (≈300, 2k, 8k, 32k, 96k) and asserts that
instruction-following does not degrade past defined floors.

## Run

```bash
ANTHROPIC_API_KEY=... \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/context_rot -v -s
```

`-s` is recommended — the rollup prints to stdout and is the most useful
artifact when a tier regresses.

## Cost guard

The full suite at the default 16-case dataset and 5 tiers is roughly 80
LLM calls. With the default `claude-haiku-4-5` model and ≤96k-token
prompts at the largest tier, estimate cost before a full run as
calls × tokens × the model's current price; do not reuse a dollar figure
from this file. Override with:

- `CONTEXT_ROT_MODEL=claude-sonnet-4-6` to test against a larger model
- `CONTEXT_ROT_MAX_TOKENS=50000` to abort early once that many input
  tokens have been consumed

## Pass criteria (defaults; see `metrics/rot.py`)

- pass rate at the smallest tier ≥ 0.95
- pass rate at every higher tier ≥ 0.85 × baseline
- degradation curve monotonic non-increasing (±0.05 tolerance)

## Reading a failure

The rollup looks like:

```
[context-rot rollup]
  tier ~   300 tok  100.0%  (16) ####################
  tier ~  2000 tok  100.0%  (16) ####################
  tier ~  8000 tok   93.8%  (16) ##################
  tier ~ 32000 tok   87.5%  (16) #################
  tier ~ 96000 tok   62.5%  (16) ############
  degradation (lowest → highest): -37.50%
  10 failed cases (showing up to 5):
    - case=needle_id_01 tier=96000 expected='SUPPORT-87431' actual='I do not see…'
    ...
```

Map the failing tier back to your assembly layer:

- Failures appear at a tier *smaller* than your projection budget →
  the compress verb is dropping load-bearing content. Inspect what
  `compress(strategy="summarize")` does at that token level.
- Failures appear only past your projection budget → expected; the
  budget is doing its job. Lower the tier set or raise the budget.
- Failures appear at all tiers including the smallest → not a rot bug.
  Check the prompt template, the model id, or the dataset.

## Extending the dataset

Each line of `dataset.jsonl` is one case:

```json
{"case_id": "...", "question": "...", "needle": "...", "expected": "..."}
```

Rules:
- The expected answer must be a substring of the needle.
- The expected answer must be a substring of any reasonable response —
  prefer concrete tokens (names, numbers, IDs) over multi-word phrases
  the model might rephrase.
- Avoid expected answers that appear in the distractor text by accident.
  The current distractors are reviewed for this; new distractors must be
  too.
