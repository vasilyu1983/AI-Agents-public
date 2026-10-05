# Build Tutorial — Shipping a Context Layer (RA1)

A zero-to-shipped walkthrough for building the most common context-layer
shape: a SaaS app that needs typed memory, evidence-bearing retrieval, and
per-surface context assembly, backed by your own Postgres + pgvector by
default.

This is the *build* companion to the architect-grade references. The
references answer *what should this layer look like*; this walkthrough
answers *what do I do on Monday morning*.

## Audience

A backend engineer who has built CRUD APIs and shipped one feature against
an LLM provider, but has not yet built a durable memory + retrieval +
assembly pipeline. You should be comfortable reading Python, running
Postgres locally, and reasoning about ACL boundaries in your own product.

## Prerequisites

- Python 3.11+
- Postgres 15+ with the `pgvector` extension installed
- An LLM provider (Anthropic SDK is the default in `adapters/anthropic_llm.py`)
- An embedding provider (any OpenAI-compatible endpoint, or local BGE/Nomic)
- The build kit copied or vendored: `builds/reference_app/` is your starting tree

The whole pipeline runs in-memory with the fakes in `evals/fakes.py`, so
you can complete steps 1–7 without provisioning anything. Steps 8 onward
need real services.

---

## Step 1 — Frame the surface

Pick *one* user-visible surface and write its job-to-be-done in a single
sentence. Everything downstream — token budgets, memory types, eval cases —
derives from this.

A useful template:

> *On the **{surface}** when **{actor}** does **{action}**, the system
> should produce **{output}** using **{evidence sources}**, within
> **{latency budget}**.*

Concrete example for a customer-support assistant:

> *On the **agent inbox** when a **support agent** **opens a ticket**, the
> system should produce a **reply draft + cited KB articles** using
> **prior tickets, KB, account state**, within **800ms TTFT**.*

If you cannot fill in every blank, you do not have a surface yet — you
have a wish. Stop and clarify with whoever owns the product. The
single-sentence brief is what makes step 10 (anti-pattern sweep) tractable;
without it, you cannot tell whether `assemble()` is over- or under-fitting.

## Step 2 — Identify operational truth (P1)

For every entity that will appear in the context bundle (`user`, `org`,
`project`, `account`, …), confirm there is already a system of record
that owns the canonical state. Operational truth is *fetched live* via
the `OperationalToolkit` adapter — it is never copied into the memory
layer (that is anti-pattern A2).

Audit checklist for each entity:

- [ ] There is a single SQL row (or service endpoint) that is the source
      of truth for the entity's name, status, plan, ACL, etc.
- [ ] You can fetch it in <50ms p95 from the assembly path.
- [ ] You have a per-actor read API (the toolkit cannot be a service
      account that reads everything — A12).

If any of these is missing, **stop and build it first**. Layering memory
and retrieval on top of broken operational truth produces a beautiful
hallucination machine.

In the reference app, this is the `OperationalToolkit` Protocol in
`adapters/base.py`. Implement one method (`fetch_live_facts`) and you are
done with P1.

## Step 3 — Define the canonical contracts

Copy `reference_app/contracts/` into your project (or vendor it as a
package). The contracts are the single most important thing in this kit:
they encode the anti-patterns at the *type* level, so invalid records
cannot be constructed.

Things you will be tempted to do — and shouldn't:

- **Add a new top-level entity.** Don't. Extend `EntityProfile.attributes`
  with a JSON-shaped dict. New entities mean new ACL surfaces; the kit's
  guarantees assume the existing scope model.
- **Make `source_episode_id` optional.** It's required because A13
  (orphan memories) is the most common F1 vector. If a memory cannot
  cite its source episode, it cannot defend itself in an audit.
- **Skip the `inferred` flag.** A26 (mode-collapse loops) requires
  honest tagging of inferred-vs-stated. A backfilled memory is always
  inferred=True; an explicit user statement is inferred=False.

Every domain extension should land in `EntityProfile.attributes` or in
new `MemoryType` values added to the enum. If you find yourself adding
columns to `LearnedMemory`, ask whether the field belongs in metadata
instead — most do.

## Step 4 — Choose adapter backings

For v1, default to the Postgres adapters in `reference_app/adapters/postgres_*.py`.
The single-vendor path keeps the operational story simple: backups,
migrations, and incident response are all *Postgres operations* you
already know how to run.

The decision matrix in `cookbooks/` covers when to swap:

| You need | Reach for |
|----------|-----------|
| Fast time-to-value, managed extraction | `mem0_adapter.py` (cookbook: `mem0.md`) |
| OS-style core/archival memory tiers | `letta_adapter.py` |
| Graph + vector hybrid retrieval | `cognee_adapter.py` |
| LangGraph-native agent integration | `langgraph_store_adapter.py` |
| Cross-app universal memory | `supermemory_adapter.py` |

The Protocol abstraction means switching is a config change, not a code
change. **Resist switching for v1.** Vendor evaluation is itself a
project; do it once you have a working baseline and an eval suite that
can A/B fairly.

Apply the migration in `adapters/migrations/0001_initial.sql` to your
Postgres database. The schema is bi-temporal (`created_at`,
`invalidated_at`, `supersedes_id`) — non-destructive by construction.

## Step 5 — Wire the ingest pipeline

The shape: **episode → extraction → typed memory write**.

```python
from reference_app.runtime import write
from reference_app.contracts import LearnedMemory, MemoryType

# 1. Persist the episode (raw turns, tool calls, system events).
episode_id = episode_log.append(episode)

# 2. Extract typed facts. This is your domain code — usually a small LLM
#    call with a structured-output schema. Keep it bounded; extract one
#    "thing" per call, not "everything."
facts = your_extractor(episode.text)

# 3. Write each fact through the runtime verb (not directly to the store).
#    The verb enforces the contract (A13/A14/A10) and emits feedback.
for fact in facts:
    write(
        fact=LearnedMemory(
            id="",
            entity_id=episode.user_id,
            entity_type="user",
            memory_type=MemoryType(fact["type"]),
            value=fact["value"],
            source="extractor:v1",
            source_episode_id=episode_id,        # A13: required
            confidence=fact["confidence"],       # A14: required
            created_at=now(),
            updated_at=now(),
            owner_scope=request.owner_scope,     # A10: required
            inferred=True,                       # A26: extractor output is always inferred
        ),
        memory_store=memory,
    )
```

Three things to get right early:

- **Bound extraction.** One extraction call per episode at most. If you
  loop over chunks and re-extract, you will flood the contradiction queue
  (T6 in the traps appendix).
- **Cap inferred confidence.** Extractor output should max out at ~0.7.
  User-stated facts can go higher.
- **Pass `owner_scope` from the request.** Never let extraction code
  invent a scope; cross-tenant leakage (A10) almost always starts with
  a default-scope shortcut in an extractor.

## Step 6 — Wire the retrieval pipeline

The shape: **document → chunk → embed → index → rerank → evidence-bearing result**.

The `RetrievalStore` Protocol (`adapters/postgres_retrieval.py`) handles
the index/rerank end. You own the chunking and the embedding call. Two
choices that bite later if you get them wrong:

- **Chunk size.** Default to 600–800 tokens with 80–120 overlap. Smaller
  chunks improve recall precision but multiply embedding cost; larger
  chunks defeat the reranker.
- **Embedding model commitment.** Switching embedding models later is
  expensive (T3 in the traps appendix). Pick one, write it down, and
  treat changes as a migration project.

Every `RetrievalResult` has an `evidence_id`. That ID is what flows into
the bundle, what the model is asked to cite, and what `isolate()`
validates against on the way back. **Never strip the `evidence_id`** —
A18 (citationless evidence) is what makes F1 detection possible.

## Step 7 — Build the per-surface bundle

`runtime/verbs.py::assemble()` is the central function. It composes the
six verbs (`write`, `select`, `compress`, `isolate`, `order`, `format`)
into a single bundle for one assembly request.

```python
from reference_app.runtime import assemble
from reference_app.contracts import ContextAssemblyRequest, Guardrails

bundle = assemble(
    request=ContextAssemblyRequest(
        surface="agent_inbox",
        actor=current_actor,
        owner_scope={"org_id": org_id},
        entity_id=user_id,
        query=user_query,
        guardrails=Guardrails(
            token_budget=8_000,
            memory_budget=1_500,
            evidence_budget=2_000,
            min_memory_confidence=0.5,
        ),
    ),
    memory_store=memory,
    retrieval=retrieval,
    toolkit=toolkit,
    llm=llm,  # used only if compress(strategy="summarize") fires
)
```

Two non-obvious things `assemble()` does for you:

1. **`order()` enforces a cache-friendly layout** — system prompt and
   tool defs first, then memory, then evidence, then history. The
   reference app keeps the front of the prompt invariant across turns
   so your provider's KV cache hits (see `cookbooks/latency_cost.md`).
2. **`compress()` is lazy** — it fires only if the assembled bundle
   exceeds the budget. Most surfaces should never trip it; if yours
   does on >50% of requests, your budgets are wrong.

For long-horizon background work, dispatch a sub-task with `isolate()`.
The sub-agent runs against a frozen snapshot of the parent bundle and
its `cited_evidence_ids` are validated on return (`rejected_ids` is the
F1 detector — see step 11).

## Step 8 — Add the feedback loop

Without feedback, the memory layer is write-only and quality cannot
improve. Two channels are enough for v1:

- **Inline reactions** (👍 / 👎 on a generated reply). On 👍, call
  `memory.improve(memory_id, confidence_delta=+0.05, reason="user_thumbs_up")`
  for the memory IDs cited in the bundle. On 👎, do the inverse.
- **Corrections** ("actually, my preferred timezone is UTC"). Treat
  these as a `write()` of a new memory with `supersedes_id` pointing at
  the old one. The contradiction detector will route any unrelated
  conflicts to your review queue (P4).

Feedback is the single largest source of poisoning (F1) if mishandled.
Two rules:

- Never let feedback bypass `owner_scope` validation. A reaction from
  user A can only adjust memories scoped to user A.
- Cap `confidence_delta` per call (±0.1). Compound increments will
  saturate your confidence floor in days; the goal is gradual
  reinforcement, not racing to 1.0.

## Step 9 — Run the eval harness

`evals/harness.py` is the runnable spine. The smoke suite is the
day-one gate; the substantive suites land progressively as you wire
real services.

```bash
# Day 1: smoke (no credentials required).
pytest builds/evals/suites/smoke -v

# Once Postgres is wired:
POSTGRES_DSN=postgresql://localhost/ctx pytest builds/evals/suites/postgres -v

# Once the LLM is wired (gated on ANTHROPIC_API_KEY):
pytest builds/evals/suites/context_rot -v
pytest builds/evals/suites/mode_collapse -v
```

Every PR should run the smoke suite. The substantive suites run on a
nightly cadence in CI — they cost real tokens and have a built-in spend
guard, but they are still not free.

The reports in `evals/reports/rollup.py` are intentionally grep-friendly:
plain text, one metric per line, easy to diff across runs. Wire the
output into your CI summary; visual dashboards come later.

## Step 10 — Run the anti-pattern sweep

Before any release, score the implementation against
`references/anti-patterns-catalog.md`. For every applicable A entry,
write down either `BLOCKED` (with the mechanism — schema constraint,
contract field, runtime check) or `NOT BLOCKED (accepted: …)` with the
reason and the operator who accepted the risk.

The point of the sweep is not to score 100%. The point is to make the
*accepted* risks legible. A surface with three accepted A entries and a
clear reason for each is shipping. A surface with "blocked / blocked /
???" is not — the unknown rows are where incidents live.

The sweep takes ~30 minutes the first time and ~5 minutes thereafter
(most rows are still blocked from last release). Skipping it is the
single most common path to F1 in production.

## Step 11 — Ship behind a flag, watch the dashboards

Wire the kill switch from `cookbooks/ops_runbook.md` at the *assembly*
layer (not the adapter layer) and route all production traffic through
it. The flag should default off for new tenants and roll out tier by
tier as you validate.

Day-one dashboards:

| Metric | Why |
|--------|-----|
| Bundle p95 token count | Bundle bloat (F2) detection |
| TTFT p50 per surface | KV-cache health |
| `compress` invocation rate | Budget calibration |
| Sub-agent dispatch rate | F2 escape hatch usage |
| Sub-agent `rejected_ids` non-empty | F1 detector — must be 0 |
| `find_contradictions` returns >0 rate | Ingest pipeline regression |
| Mode-collapse self-similarity (sampled) | T5 — slow drift detection |

If `rejected_ids` is non-zero on any request, page someone. That is
the single most important alert in the layer; everything else is a
budget conversation.

---

## Common detours

- **"We don't need memory yet."** Often true. Skip P2/P5 and ship P1 + P8.
  Add memory when you have a concrete behavior change you want it to drive.
- **"Just use a vector DB for everything."** Anti-pattern A2. Operational
  truth in SQL/tools, derived prose in the index.
- **"Let's add a graph."** Anti-pattern A9. Add P4 only when relationship
  traversal changes the answer; never as a default.
- **"Memory is just chat history."** Anti-pattern A1. Extract typed facts
  at write time; never search raw turns.
- **"We'll add the eval suite later."** Don't. The smoke suite costs
  nothing and catches the contract regressions that bite hardest. The
  substantive suites can wait; the smoke gate cannot.

## Where to go next

- `cookbooks/latency_cost.md` for budget tuning and KV-cache layout.
- `cookbooks/ops_runbook.md` for migrations, A/B switching, and incidents.
- `cookbooks/traps.md` for failure modes seen in production context
  layers — read once before launch, re-read quarterly.
- `../references/anti-patterns-catalog.md` for the full A-catalog and the
  scorecard template.

The kit's job ends here. The hard part — the domain extraction logic,
the eval cases that reflect *your* users, the ops cadence — is yours to
own. The kit just removes the well-known traps from the path.
