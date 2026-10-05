# Measuring whether memory skills improve an agent

Load for a skills-on versus skills-off comparison. This instrument grades
externally collected exact outputs and exported state; it never runs a model or
supplies observations. The public fixtures are builder-written development
cases. Passing them establishes fixture behavior only.

## Contents

- [Run design](#run-design)
- [Files and contract](#files-and-contract)
- [Reuse the existing analysis](#reuse-the-existing-analysis)

## Run design

Freeze an independent task set and private grader before collecting results.
Keep answer keys outside model inputs, tools, retrieval corpus, and traces the
agent can read. Use the development task JSONL for harness development; only
`payload` and `response_contract` belong in the model input. The separately
stored grader JSONL is for the evaluator. Freeze actual tool-state observers,
including evidence captured from all relevant stores: a model's self-reported
"no leak" or "deleted" claim alone cannot establish those invariants.
The validator recursively rejects structured grader-only keys in task objects
and arrays. Arbitrary answer leakage in prose cannot be detected automatically;
review model-visible payloads independently before freezing the suite.
Both task input fields must be nonempty strings; a manifest must be a JSON
object. Missing model inputs or nonobject manifests produce inconclusive results.

For each case and repeat, reset the same initial memory and tool state. Pin the
same model ID, model settings, tools, corpus, state fingerprint, and resource
budget in both arms. Hash the full skill bundles supplied to skills-on; keep
skills-off hashes empty. Record seed policy in settings; equal seeds do not
ensure hosted-model determinism. Randomize arm execution order independently
within each pair, record that schedule and run timestamps in the external run
ledger, and predeclare repeats and stopping rules. A runtime failure remains a
failed outcome rather than disappearing from coverage.

The public fixtures cover contradiction, read-time expiry, deletion while a
consolidation job is paused, tenant separation, exact identifiers, semantic
queries, and persistence of poisoned derivatives. Expand each with real cases,
benign controls, missing provenance, concurrency and backend failures. The
fixture instructions specify deterministic policy so a disagreement reflects
that declared policy. Keep an independently authored, frozen holdout for claims
about transfer; never tune on it or describe this public development set as
held-out.

## Files and contract

From the skill directory:

```bash
python3 scripts/memory_ablation.py \
  --tasks scripts/fixtures/memory-development-tasks.jsonl \
  --graders scripts/fixtures/memory-development-graders.jsonl
```

This validates suite coverage and prints its canonical SHA-256 fingerprint.
Create an external manifest with `suite_fingerprint`, unique `repeat_ids`, and
`arms.skills_off` / `arms.skills_on`. Each arm contains exactly these pins:

```json
{
  "model": "your pinned model ID",
  "settings": {"temperature": 0, "seed_policy": "recorded by collector"},
  "tools_fingerprint": "your tool bundle hash",
  "corpus_fingerprint": "your corpus hash",
  "initial_state_fingerprint": "your snapshot hash",
  "budget": {"max_tool_calls": 20},
  "skills_hashes": {}
}
```

These are placeholders, not measured settings or vendor recommendations. Use
nonempty skill-name to hash mappings in skills-on. Only `skills_hashes` may
change across the two arm configurations. Pin the suite, tools, state and
skills from actual bytes in the collector; equality of user-supplied strings
cannot prove that the live run used those artifacts.
The validator checks declared parity and basic validity of `max_tool_calls`,
`temperature`, and `seed_policy` when supplied. Provider-specific settings and
budget enforcement remain the collector's responsibility.

Each external outcome JSONL record includes `arm`, `case_id`, `repeat_id`,
`suite_fingerprint`, `config` (the complete matching arm config), `actual`
(the externally observed object), and `telemetry`:

```json
{"latency_ms": null, "input_tokens": null, "output_tokens": null}
```

Null means unknown, never zero. Supply real measured telemetry only. Optional
`cost` requires `currency` and `pricing_fingerprint`; otherwise the report
counts that outcome as unpriced. No provider prices are embedded, no API is
called, and no cost savings can be inferred from unpriced results. Capture
end-to-end latency, retries, background consolidation and token accounting
under the same policy in both arms; document excluded work.

```bash
python3 scripts/memory_ablation.py --tasks tasks.jsonl --graders graders.jsonl \
  --manifest run-manifest.json --outcomes collected-outcomes.jsonl \
  --report descriptive-report.json --paired-csv paired.csv
```

Exit 2 means invalid/incomplete evidence (`inconclusive`); exit 1 means at
least one collected arm outcome failed; exit 0 means every exact assertion
passed. None is a superiority or production-readiness decision. Missing cases,
repeats, hard-negative slices, duplicates, changed pins, malformed/nonfinite
metrics and leaked grader fields block scoring. Reports preserve actual
telemetry and per-case failures. Exact object comparison includes extra keys;
arrays require declared order. `safety_fields` mark safety invariants;
`hard_negative` failures also populate the paired critical-failure columns.
Output paths must differ from inputs and each other. Before a rerun, requested
outputs are marked inconclusive so a failed validation cannot leave a stale
success. Files are staged in temporary siblings; CSV publishes first and the
successful report last. Publication failures invalidate both requested outputs
when filesystem access permits, and inaccessible output paths are reported.
Replacement across two output paths is not a filesystem transaction; consumers
must require the final descriptive report before using the paired CSV.

## Reuse the existing analysis

The export maps skills-off to `baseline`, skills-on to `candidate`, and repeats
to distinct units clustered by case. Predeclare whether the target is the mean
repeat or equal-weighted case; shared scenario/source dependence may require
broader clusters before inference. For an independently sampled frozen set:

```bash
python3 scripts/analyze_paired_results.py paired.csv --estimand cluster_mean
```

Use the existing analyzer's uncertainty and critical-failure reporting; do not
add another statistical implementation. A fixed public development suite gets
exact counts and descriptive differences, regardless of any computed interval.
A safety miss blocks that safety gate even when average quality improves.
Separate quality, latency, token consumption and priced cost; a single weighted
score can hide regressions. Promotion follows a predeclared release rule and
independent holdout evidence in [retrieval-and-memory-eval.md](retrieval-and-memory-eval.md).
