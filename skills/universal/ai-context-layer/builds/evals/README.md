# Eval Harness

Runnable checks for context-layer regressions. Local suites run without
credentials; engine and model suites require their declared dependencies.
A skipped suite is untested, even when pytest exits successfully. A release
claim must name the suites actually executed and their skipped case counts.

## Why a separate harness

Most teams catch context bugs in production. The harness exists to catch them
in CI:

- **F1 (poisoning)** — assert the bundle never contains a fact whose
  `source_episode_id` does not resolve in the episode log.
- **F2 (distraction)** — assert `bundle.token_count_estimate <= projection.max_tokens`
  with a known-bloated input.
- **F3 (clash)** — assert that contradictory inputs produce a single
  reconciled fact, not both.
- **F4 (confusion)** — assert per-surface tool allowlists hold.
- **Context rot** — assert response quality on a fixed needle-in-haystack
  task does not regress past a threshold as input tokens grow (5 tiers).
- **Mode collapse / A26** — assert response variance on a structurally
  diverse prompt set does not collapse below the floor.

## Layout

```
evals/
  README.md           # this file
  harness.py          # runner: load suite, run cases, report pass/fail
  fakes.py            # in-memory adapters used across suites
  metrics/            # rot + variance metrics, callable standalone
  reports/            # grep-friendly text rollups
  suites/
    smoke/            # contract regressions, runs unconditionally
    jit_loading/      # pointer-first runtime ref resolution, no credentials
    managed_boundary/ # hosted-memory boundary rules, no credentials
    state_maintenance/ # duplicate/out-of-order replay, authority, as-of; no credentials
    multimodal/       # typed multimodal projections, no credentials
    postgres/         # gated on POSTGRES_DSN
    context_rot/      # gated on ANTHROPIC_API_KEY (token-spend guard)
    mode_collapse/    # gated on ANTHROPIC_API_KEY
    langgraph_store/  # gated on `langgraph` import (uses InMemoryStore)
    mem0/             # gated on MEM0_API_KEY + `mem0` import
    letta/            # gated on LETTA_BASE_URL + LETTA_AGENT_ID + `letta_client`
    cognee/           # gated on COGNEE_LLM_API_KEY (or OPENAI_API_KEY) + `cognee`
    supermemory/      # gated on SUPERMEMORY_API_KEY + `httpx`
```

## Running

Disk-backed lifecycle tests (stdlib only, run from this skill directory):

```bash
python3 builds/evals/suites/state_maintenance/test_sqlite_lifecycle.py
```

This suite calls the shipped SQLite lifecycle runtime rather than a reducer
implemented inside the test. See [lifecycle contract and limits](../../references/sqlite-memory-lifecycle.md).

The [paired skill comparison](../../../ai-evals/references/memory-skills-ablation.md)
accepts actual external agent outcomes; its development fixtures test the scorer,
not skill effectiveness.


Smoke (no credentials):

```bash
cd builds
pip install -e ./reference_app[dev]
pytest evals/suites/smoke -v
pytest evals/suites/jit_loading evals/suites/managed_boundary evals/suites/multimodal evals/suites/state_maintenance -v
```

Postgres behavioral suite:

```bash
pip install -e ./reference_app[postgres,dev]
POSTGRES_DSN=postgresql://localhost/ctx pytest evals/suites/postgres -v
```

Real-LLM suites (context-rot + mode-collapse):

```bash
pip install -e ./reference_app[anthropic,dev]
ANTHROPIC_API_KEY=sk-ant-... pytest evals/suites/context_rot evals/suites/mode_collapse -v
```

The LLM-backed suites have a built-in token-spend guard, but they are not
free. Run nightly in CI, not per-PR.

Vendor adapter suites (run any combination you have credentials for):

```bash
pip install -e ./reference_app[langgraph,http,dev]    # langgraph + supermemory
pytest evals/suites/langgraph_store -v
SUPERMEMORY_API_KEY=... pytest evals/suites/supermemory -v
MEM0_API_KEY=... pytest evals/suites/mem0 -v          # also `pip install mem0ai`
COGNEE_LLM_API_KEY=... pytest evals/suites/cognee -v  # also `pip install cognee`
LETTA_BASE_URL=... LETTA_AGENT_ID=... pytest evals/suites/letta -v  # also `pip install letta-client`
```

Vendor SDKs are intentionally not in `pyproject.toml` extras — they are
mutually independent and most users only ever wire one. Install whichever
matches your chosen adapter.

## Evidence levels

- **Static:** schema, link, and SQL-text checks establish artifact consistency.
- **Local behavior:** disk-backed SQLite tests establish the implemented local
  lifecycle invariants; fake-store suites establish only their contract examples.
- **Engine integration:** tests against the deployed engine/version and application
  role establish behavior for that configuration. Missing dependencies or credentials
  are `not_run`, never a passing engine result.
- **Agent effectiveness:** paired runs on independently frozen tasks establish
  observed skill benefit. Public development fixtures and authored test expectations
  cannot establish a held-out result or superiority over other systems.

Record code and task hashes, backend/version, executed and skipped counts, and
limitations with each result. A passing lower level cannot substitute for a
missing higher level.

## What the harness does NOT replace

- Your domain-specific golden dataset. Smoke fixtures are synthetic.
- Live production observability. The harness runs offline; F1–F5 detection in
  prod requires tracing.
- Human review of borderline cases. The harness rejects regressions; it does
  not replace judgment on whether an intentional behavior change is good.
