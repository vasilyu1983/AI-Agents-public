# Agent Memory Benchmarks

What public memory benchmarks measure, what they miss, and the rules for
trusting any memory number, including a vendor's. Run them beside the
skill's own scorecard (`assets/eval/context-layer-scorecard.md`) and the
deterministic suites under `builds/evals/`. Pick the benchmark that maps to
the responsibility you are changing; do not run them all for completeness.

Scores are never recorded here. A paper is cited for the direction of a
result in the authors' setup; look up the paper for magnitudes.

## Table of Contents

- [Rules before you trust a memory number](#rules-before-you-trust-a-memory-number)
- [What each benchmark measures, by responsibility](#what-each-benchmark-measures-by-responsibility)
- [Known flaws](#known-flaws)
- [What no public benchmark tests](#what-no-public-benchmark-tests)
- [Internal complement: the evals the skill ships](#internal-complement-the-evals-the-skill-ships)
- [Gates and thresholds](#gates-and-thresholds)
- [Provider compaction primitives](#provider-compaction-primitives)
- [Primary sources](#primary-sources)

## Rules before you trust a memory number

1. **Run two baselines on the same questions.** A no-memory baseline shows
   whether memory helps at all; a full-context baseline shows whether a
   memory layer beats putting the history in the window. On benchmarks whose
   histories fit the window, full context has matched or beaten memory on
   accuracy: the Mem0 authors' own LoCoMo table (arXiv 2504.19413) puts full
   context highest on the LLM judge, and the Zep paper (arXiv 2501.13956)
   reports assistant-side recall regressing against full context on
   LongMemEval. A memory win on a short benchmark is usually a cost and
   latency win; say so (A48).
2. **Configure every engine, not just yours.** Parity means each system
   gets the same domain help: a schema, an ontology, custom extraction
   instructions, or tuned retrieval, wherever it supports one. Worked
   example: a schema-first vendor's published benchmark gave its own engine
   hand-written domain schemas while the baselines received raw text,
   although several baselines accept custom ontologies or instructions; the
   questions were written by the vendor for those schemas; n was small, no
   intervals or run counts were reported, and the runner and baseline
   adapters were not public. What that design can show is that a curated
   schema plus text-to-SQL beats unconfigured extraction on questions written
   for that schema. It is not an engine ranking. The same lesson from the
   other side: two memory vendors have published different LoCoMo scores for
   the same competitor system, because each ran its own implementation of it.
3. **Report n, intervals, and runs.** Give the question count per category,
   a Wilson interval (or bootstrap) per reported rate, the number of seeds or
   runs, the judge model and its prompt, and the answering model. Small
   per-category n makes most category-level differences noise.
4. **Publish the runner.** A result counts as reproducible when the harness,
   the baseline adapters, the prompts, and the dataset revision are public.
   A vendor number without a runnable harness is a claim, not evidence;
   label it unverified.
5. **Score deterministically where you can.** Use exact match, set overlap,
   or nugget checks for fields and IDs. When a model judge is unavoidable,
   calibrate it on a labelled sample and report agreement; a lenient judge
   inflates every system equally and hides regressions.
6. **Re-test after every model upgrade.** Memory quality depends on the
   extraction, tool-calling, and answering models. MemGPT (arXiv 2310.08560)
   degraded with a weaker function-calling model, and EnterpriseMem-Bench
   (arXiv 2605.26394) reports a newer model regressing against its
   predecessor. A model swap is a memory change; rerun the gate.
7. **Re-run on your own workload before adopting.** A public benchmark
   tells you which engines to shortlist. Your gate is your traffic, your
   update patterns, and your deletion requests.

## What each benchmark measures, by responsibility

Responsibility numbers follow
[memory-responsibilities-audit](memory-responsibilities-audit.md):
1 admission, 2 encoding, 3 persistence, 4 maintenance, 5 retrieval,
6 post-retrieval, 7 materialisation.

| Benchmark | What it actually measures | Responsibilities exercised | Use it for |
|---|---|---|---|
| LongMemEval (arXiv 2410.10813) | Chat-assistant recall across five abilities: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention. A small variant fits in the window; a large variant forces a memory layer | 2, 4 (updates), 5, 6 (abstention) | The knowledge-update and abstention categories are its most useful signals |
| LoCoMo (arXiv 2402.17753) | QA, event summarisation, and multimodal dialogue generation over very long two-speaker conversations | 2, 5 | Multi-session recall; cheap smoke test |
| MemoryAgentBench (arXiv 2507.05257) | Four competencies for agents fed incrementally: accurate retrieval, test-time learning, long-range understanding, selective forgetting | 4, 5 | The only widely used benchmark with a forgetting category |
| MSC / DMR (arXiv 2107.07567; DMR from MemGPT, arXiv 2310.08560) | Retrieval of a fact stated in an earlier session | 5 | Regression floor only |
| BEAM (arXiv 2510.27246) | Ten memory abilities over conversations far longer than any context window, scored by nuggets | 2, 4, 5, 6 | Stress-testing scale where full context is impossible |
| HaluMem (arXiv 2511.03506), MemOps (arXiv 2607.12893) | Operation-level checks: whether extraction, update, and retrieval each did the right thing, not only the final answer | 2, 4, 5 | Locating which stage failed |
| PersistBench (arXiv 2602.01146) | Long-term-memory risks: cross-domain leakage of stored facts and memory-induced sycophancy | 5, 6 | Safety gate for personal memory |
| OP-Bench (arXiv 2601.13722) | Over-personalisation: memory applied where it should not be | 6 | Checking that retrieval respects relevance, not just similarity |
| PASB (arXiv 2607.10526); MemSyco-Bench (arXiv 2607.01071) | Sycophancy amplified by saved user claims; PASB reports agents rewriting claims as stable facts | 1, 2, 6 | Gate for anything that stores user statements (A49) |
| EnterpriseMem-Bench (arXiv 2605.26394) | Multi-turn text-to-SQL over enterprise data, with and without memory of earlier turns | 5, 7 | Structured-memory and text-to-SQL agents |
| MemBench (arXiv 2506.21605) | Factual vs reflective memory across participation and observation scenarios | 2, 5 | Tiebreaker |
| GraphRAG-Bench (arXiv 2506.02404) | Graph-augmented retrieval by question type | 5 | Deciding whether a graph layer earns its cost (A33) |
| MemTier (arXiv 2605.03675) | Tiered memory and retrieval bottlenecks under long-horizon load | 3, 5 | Architecture analysis, not quality |

## Known flaws

- **LongMemEval.** Histories are padded with synthetic filler sessions, so
  distractors are easier than real traffic. There is no deletion operator, so
  it says nothing about erasure. Answers are graded by a model judge. The
  small variant fits in a long window, so it does not force a memory layer.
  The paper also reports that storing only extracted facts as values loses
  information against keeping the original rounds (A47).
- **LoCoMo.** The public release is far smaller than the paper's described
  set. The adversarial category ships without gold answers, so systems score
  it inconsistently. A third-party audit claims some gold answers are wrong
  and that the common judge is lenient (unverified). There is no
  knowledge-update category, and conversations fit in a long window.
- **MemoryAgentBench.** Its forgetting task tells the agent that facts with
  larger serial numbers are newer, which hands the system the ordering rule
  that real updates never carry. Passing it does not prove ingestion-order
  or backfill handling (A39).
- **MSC / DMR.** Single-turn fact retrieval only; full context scores near
  the ceiling, so it cannot separate good memory designs.
- **BEAM.** Synthetic conversations; few questions per ability, so
  per-ability comparisons carry wide intervals.
- **HaluMem, MemOps.** Both come from memory-vendor groups; HaluMem's authors
  build MemOS and compare against it. Check the harness for home-engine
  advantages before citing comparisons.
- **Personalisation-risk benches.** Young datasets with little external
  replication; use them as safety gates, not leaderboards.
- **EnterpriseMem-Bench.** Its stateless multi-turn setting collapses within
  a few turns by design; it shows the need for turn memory, not which store
  to use.
- **GraphRAG-Bench.** Measures retrieval quality with the answer in context;
  hallucination downstream of retrieval is not captured.
- **All of them.** Consolidation can raise utility and then fall below the
  no-memory baseline as rewrites accumulate, while an episodic-only control
  stays competitive (arXiv 2605.12978). A single snapshot score hides that
  drift; rerun after N consolidation cycles.

## What no public benchmark tests

Build these as your own slices; they are where production memory fails.

- **Multi-tenant leakage**: a planted canary per tenant, queried from every
  other tenant (`tenant-isolation-patterns.md`).
- **Erasure proof**: a planted sentinel fact, erased, then probed across every
  derived store and retrieval path
  ([managed-memory-boundaries](managed-memory-boundaries.md#erasure-across-derived-stores)).
- **Point-in-time queries**: "what did we believe on date D", including
  out-of-order backfills ([evals-and-operations](evals-and-operations.md#state-maintenance-eval)).
- **Write-path poisoning**: injected instructions or false facts arriving
  through tools, documents, or other users (`security-threat-model.md` T2).
- **Source-authority conflict**: a lower-authority source contradicting a
  higher one (P22).
- **Cost and latency under load**, at your concurrency and memory size.

## Internal complement: the evals the skill ships

External benchmarks measure capability on synthetic data. The suites under
`builds/evals/suites/` measure architectural discipline on deterministic
fixtures, mostly without an API key:

- `postgres/` — A3, A7, A10, A11, A13 invariants on a real Postgres path,
  including DSAR deletion that preserves unrelated audit rows and
  supersession-chain reconstruction.
- `state_maintenance/` — update, supersession, and contradiction categories.
- `context_rot/` — poisoning surfacing as citation drift.
- `mode_collapse/` — A26; re-run after any P14 cadence change to catch A31.
- `proactive_interference/` — the superseding-slot invariant; re-run after
  any change to supersession or `forget` wiring.
- `managed_boundary/` — A28 and A30 invariants for hosted memory paths.
- Vendor adapters (`mem0/`, `letta/`, `cognee/`, `supermemory/`,
  `langgraph_store/`) — the same checks against each engine.

A passing benchmark with a failing internal eval is a traffic-distribution or
architecture problem, not a capability problem. Both are necessary.

## Gates and thresholds

No universal threshold is defensible; set each one against your own
baselines and record why.

- **Gate on deltas, not absolutes.** Block a deploy when a category falls
  below the no-memory baseline, or when its interval no longer overlaps the
  previous release's.
- **One gate per responsibility you changed.** A new extraction prompt gates
  on encoding and update categories; a new index gates on retrieval and the
  tenant canary; a consolidation change gates on drift across cycles.
- **Graph layers must earn their place.** Keep one only if it beats plain
  retrieval on multi-hop questions without losing single-hop ones; otherwise
  route single-hop around it (A33).
- **Safety gates are zero-tolerance.** Tenant canary leaks and sentinel
  recoveries after erasure must be zero, not a rate.
- **ACE-style playbooks** (arXiv 2510.04618): reproduce a gain over the
  no-playbook baseline on your tasks before adopting; the paper credits delta
  updates, not whole-context rewrites, which is what blocks A35. Reported
  gains live once, in P18 of `patterns-catalog.md`.

## Provider compaction primitives

- Defaults (trigger thresholds, how many recent tool results are kept,
  exemptions, custom summarisation instructions, pause-for-review) differ per
  provider and change between API versions. Look them up in the provider's
  context-management docs; do not hard-code them.
- Use custom summarisation instructions, where offered, to enforce P20
  anchoring, and exempt the memory tool from clearing.
- Decide when to trigger with `context-hygiene.md` §Context mutation
  economics; verify each compaction with §Compaction verification.

## Primary sources

URLs and verification dates are in `data/sources.json`.

- LongMemEval — arXiv 2410.10813
- LoCoMo — arXiv 2402.17753; dataset at `https://snap-research.github.io/locomo/`
- MemoryAgentBench — arXiv 2507.05257 (ICLR 2026)
- MSC — arXiv 2107.07567; DMR — MemGPT, arXiv 2310.08560
- BEAM — arXiv 2510.27246 (ICLR 2026)
- HaluMem — arXiv 2511.03506; MemOps — arXiv 2607.12893
- PersistBench — arXiv 2602.01146; OP-Bench — arXiv 2601.13722; PASB — arXiv
  2607.10526; MemSyco-Bench — arXiv 2607.01071
- EnterpriseMem-Bench — arXiv 2605.26394
- Consolidation drift — arXiv 2605.12978
- Mem0 — arXiv 2504.19413; Zep — arXiv 2501.13956
- MemBench — arXiv 2506.21605 (not 2507.05257, which is MemoryAgentBench)
- GraphRAG-Bench — arXiv 2506.02404; MemTier — arXiv 2605.03675
- LongMemEval-V2 — arXiv 2605.12493 (preprint; web-agent framing; labelled
  work in progress by its authors)
- ACE — arXiv 2510.04618
- Surveys for vocabulary, not claims: arXiv 2603.07670, arXiv 2602.19320

Thank you to arXiv for use of its open access interoperability.
