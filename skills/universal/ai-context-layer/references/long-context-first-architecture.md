# Long-Context-First Architecture

Load the whole corpus into a 1M+ token context window every query. No chunking, no retrieval, no vector store. The model reasons over the corpus directly.

This is the brute-force cousin of [cache-augmented-generation.md](cache-augmented-generation.md). They share the "no retrieval" stance, but long-context-first does not necessarily depend on KV caching — sometimes it just leans on the raw window size and pays the prefill cost.

The pattern is viable because million-token-class context windows and prompt caching together make it economically tolerable for the right shape of corpus. Check the current window and cache terms of the models you can use.

---

## Table of Contents

- [When long-context-first is the right answer](#when-long-context-first-is-the-right-answer)
- [Architecture](#architecture)
- [Long-context failure modes](#long-context-failure-modes)
- [Decision table](#decision-table)
- [Patterns](#patterns)
- [Anti-patterns](#anti-patterns)
- [Composition](#composition)
- [Related](#related)

---

## When long-context-first is the right answer

ALL of these:

1. **Corpus fits in window** with headroom. A model's advertised context window (e.g. 1M-token) is not the usable ceiling — reserve headroom for system prompt, retrieved evidence, conversation history, and output, and re-verify the current model's advertised window before budgeting (several current flagship models across vendors, including Anthropic's, now ship 1M-token windows by default — treat the "usable" fraction as an eval question, not a fixed ratio).
2. **Queries need the whole corpus.** Cross-document reasoning, comparison across full documents, "summarize all of X" style queries. If queries only ever need a small slice, RAG is cheaper.
3. **Prompt caching is available and cheap enough.** Without caching, every query pays full prefill on the whole corpus — usually unsustainable.
4. **Eval shows the model handles your corpus size at quality.** Long context is *not* free. Lost-in-the-middle, distractor handling, and order sensitivity get worse with corpus size and vary by model.

If only (1) and (3) hold but (2) doesn't, prefer CAG ([cache-augmented-generation.md](cache-augmented-generation.md)) over long-context-first — the difference is intent: CAG is "I want fast repeat queries on a stable prefix," long-context-first is "I want the model to actually reason over the whole thing."

---

## Architecture

```text
QUERY
  Compose: system_prompt + full_corpus + user_query
  Send to a long-context model (chosen by your eval, see Decision table)
  Model reasons over corpus end-to-end
  Return answer with citations to corpus offsets

(Prompt cache hits the corpus prefix on repeat queries within TTL.
 Without cache, you pay full prefill every time.)
```

Concrete model fits — illustrative shape only, re-verify against live provider docs before budgeting (advertised windows and effective "usable" fractions change with model releases):

| Model class | Usable window | Cost per cached token | Best for |
|---|---|---|---|
| Long-window model family A | Large fraction of advertised window; verify current figure | Very low cached | Multi-doc cross-reference, code-base wide refactors, long-form comparison |
| Long-window model family B | Advertised window from provider docs; effective usable fraction is corpus- and eval-dependent, not a fixed ratio | Low cached | High-quality reasoning on large corpora, subject to lost-in-the-middle eval |
| GPT-class long context | Varies | Provider-dependent | Pattern available; check current pricing |

Always check current provider pricing and context-window figures directly — long-context economics and window sizes shift on every model release, not just quarterly.

---

## Long-context failure modes

Long context does **not** mean unlimited attention. Known failures:

- **Lost-in-the-middle.** Models attend strongest to start and end of context, weakest to the middle. A claim 60% of the way through a 500K-token corpus may be ignored. Mitigate by placing the most important content at start/end and probing with eval queries.
- **Distractor robustness.** With 500K tokens of corpus, the chance some chunk lexically resembles the query but is irrelevant is high. The model may anchor on the distractor.
- **Order sensitivity.** Reordering the corpus changes answers, even when content is identical. A stable, deterministic corpus assembly order is non-negotiable.
- **Latency cliff.** Even with cache, prefill of a 1M-token prefix is not free on cache miss. First query after eviction may be multi-second.
- **Cost cliff on cache miss.** A cache miss on a 1M-token corpus is a full prefill charge: compute it as `corpus_tokens × current uncached input price` from the provider's price page. Budget for it or accept it can't run.

Eval for these explicitly. See [agent-memory-benchmarks.md](agent-memory-benchmarks.md) — LongMemEval and LoCoMo specifically test long-context retrieval quality.

---

## Decision table

| Decision | Default | Upgrade when |
|---|---|---|
| Model choice | The model that passes your lost-in-the-middle eval at your corpus size, at the lowest cached cost | Switch when a re-run of the same eval on a new model beats it on quality or cost |
| Corpus assembly order | Most-authoritative content first, summary first | Reverse when eval shows late-content recall is stronger on your model |
| Caching | Use provider prompt/context cache | Mandatory above ~50K corpus; sub-50K may not benefit |
| Citation surface | Section headings + line offsets from preloaded corpus | Stable anchors (`#id`) so cache survives re-assembly |
| Re-prime cadence | On corpus change | Lazy (first-query prefill) if changes are infrequent and latency is tolerable |
| Eval set | ≥100 queries, ≥20% lost-in-middle probes (claims placed at 40–60% depth) | More if corpus exceeds 500K tokens |
| Cost guard | Per-query token-budget cap; abort on cache miss above threshold | Always budget for miss cost separately from hit cost |

---

## Patterns

### P-LC-1 — Anchor-first assembly

Place the most load-bearing content at the start of the corpus, with a TOC pointing to anchors. Models attend to the start strongly; the TOC primes reasoning over the rest. This mitigates lost-in-the-middle for the most important claims.

### P-LC-2 — Deterministic ordering

Hash and commit the corpus assembly order so repeat queries send a byte-identical prefix; the layout and invalidation rules live in [ai-prompt-engineering → Cache-Aware Prompt Layout](../../ai-prompt-engineering/SKILL.md#cache-aware-prompt-layout).

### P-LC-3 — Tail-pinned query

Always append the user query at the very end of the prefix. Models attend to the tail strongly; "the question goes last" is a real production rule, not a stylistic choice.

### P-LC-4 — Lost-in-middle probes in eval

Plant test claims at depths 10%, 30%, 50%, 70%, 90% of the corpus. Verify retrieval accuracy at each depth. If 50%-depth retrieval drops below 0.7, reduce corpus size or move important content to start/end.

### P-LC-5 — Hybrid with RAG for long-tail

Long-context-first answers most queries directly. The rest (very specific facts, freshness-sensitive) fall back to RAG. This is the same shape as P-CAG-5 in CAG.

---

## Anti-patterns

- **A-LC-1 — "Just send everything."** Loading 500K tokens "because it fits" without checking lost-in-middle quality on your corpus. Without eval, you don't know if the model is actually using it.
- **A-LC-2 — Non-deterministic assembly.** Sorting corpus by `mtime` or any non-stable order means cache misses every query. Pin the order.
- **A-LC-3 — No cache budget for misses.** Building a budget around cache-hit cost only. One cache eviction storm makes the bill 100× expected.
- **A-LC-4 — Skipping eval because "it's all in context."** Lost-in-the-middle is real. Order sensitivity is real. Distractor failure is real. Eval is mandatory.
- **A-LC-5 — Treating long-context as a chunking replacement when corpus exceeds window.** Truncating to fit silently loses content. If it doesn't fit, switch to RAG. Don't downsample.
- **A-LC-6 — Long-context for facts that change hourly.** Each change forces re-assembly + cache invalidation + first-query prefill cost. RAG handles this for less.

---

## Composition

- **With CAG ([cache-augmented-generation.md](cache-augmented-generation.md)):** Long-context-first is CAG without the formal cache lifecycle. Production teams often start with long-context-first, then formalize the cache (priming, hashing, invalidation discipline) — and it becomes CAG.
- **With RAG (H1–H7):** P-LC-5 hybrid for long-tail.
- **With fine-tune (I3):** Fine-tuned behavior + long-context corpus = same RA-CB-1 shape as CAG + fine-tune.
- **With managed-memory ([managed-memory-boundaries.md](managed-memory-boundaries.md)):** Per-user memory turn rides on top of corpus prefix.

---

## Related

- [retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md) — The decision rubric
- [cache-augmented-generation.md](cache-augmented-generation.md) — CAG, the cache-disciplined sibling
- [fine-tune-for-behavior-not-facts.md](fine-tune-for-behavior-not-facts.md) — Composes for behavior layer
- [context-hygiene.md](context-hygiene.md) — F1–F5 runtime failure modes (poisoning, distraction, clash, confusion)
- [agent-memory-benchmarks.md](agent-memory-benchmarks.md) — LongMemEval, LoCoMo for long-context retrieval quality
- `ai-llm-inference` — Prompt-cache and context-cache mechanics
- `ai-coding-agents-provider-runtime/references/provider-capability-matrix.md` — Current window sizes and cache support
