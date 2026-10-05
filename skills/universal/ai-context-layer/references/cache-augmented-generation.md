# Cache-Augmented Generation (CAG)

Preload the entire corpus into context once, cache the model's KV state at that prefix, then serve every query against the cached prefix with zero retrieval at runtime.

CAG is the production answer when the corpus is **small, stable, and fits in context**. It eliminates the retrieval failure modes RAG cannot (retrieval errors, reranker drift, embedding model changes, stale indexes) in exchange for a hard ceiling on corpus size.

Originally framed by *"Don't Do RAG: When Cache-Augmented Generation is All You Need for Knowledge Tasks"* (arXiv:2412.15605, late 2024). It is now common for handbook-scale corpora.

---

## Table of Contents

- [When CAG is the right answer](#when-cag-is-the-right-answer)
- [Architecture](#architecture)
- [The KV-cache lifecycle](#the-kv-cache-lifecycle)
- [Decision table](#decision-table)
- [Patterns](#patterns)
- [Anti-patterns](#anti-patterns)
- [Composition](#composition)
- [Related](#related)

---

## When CAG is the right answer

ALL of these must hold:

1. **Corpus fits in context.** Typically ≤ 200K tokens with headroom for query + answer + system prompt. With 1M-token models the ceiling moves but the economics still constrain.
2. **Corpus is stable.** Refresh cadence is weekly or slower; bursts of writes are batchable. If the corpus changes mid-conversation, CAG breaks.
3. **Query volume justifies the cache.** Prompt-cache hit on prefix only pays off if you serve many queries per refresh cycle. A 5-queries-per-day system gains nothing from KV caching.
4. **Retrieval errors are unacceptable.** Compliance, customer-facing answers, support automation where a wrong retrieval hit is worse than slower bootstrapping.

If any of these fails, route back to [retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md).

---

## Architecture

```text
INGEST (once per corpus version)
  Normalize corpus → format → token-count → fit check
  Compose system prompt + corpus + query template
  Prime the prompt cache (1 inference call with no real query)
       └→ provider stores KV state at the corpus prefix
  Persist: corpus_hash, token_count, expiry (and a cache handle only if the provider issues one)

QUERY (every call)
  Resend the byte-identical prefix; the provider matches it to the cached KV state
  Append only: user query + answer instructions
  Inference call → answer
  No vector DB, no reranker, no retrieval
```

Provider support is a lookup, not a constant. Minimum prefix, TTL options and write multipliers differ per model even inside one vendor's lineup and change on releases. Before building, record for each candidate model:

1. **Mechanism** — implicit (automatic prefix cache) or explicit (named cache object / `cache_control` breakpoints).
2. **Minimum cacheable prefix** in tokens for that exact model.
3. **TTL options** and the write-cost multiplier for each (longer TTLs usually cost more to write).
4. **Storage charges** — whether a held cache is billed per hour on top of reads.
5. **Cached-read price** relative to uncached input.

Sources: the provider's own caching and pricing docs, and `ai-coding-agents-provider-runtime/references/provider-capability-matrix.md` for the library's dated snapshot.

---

## The KV-cache lifecycle

Three operations dominate.

### Prime

After every corpus refresh, run one "warming" inference call that includes the full corpus prefix plus a no-op query. This populates the provider's KV cache so the next real query is a cache hit.

```text
prime(corpus_v):
    prompt = system_prompt + corpus_v + "<noop_query>"
    response = llm.invoke(prompt, cache_control="ephemeral")
    store(corpus_hash=hash(corpus_v))
```

Prefix caching is keyed on identical prefix content: Anthropic (`cache_control` breakpoints) and OpenAI (automatic) return no cache handle, so "reuse" means resending the same prefix. Only providers that expose explicit cache objects (for example Gemini context caches) return a named cache to reference. Priming pays the full prefill plus the cache-write premium once; the later hits are what save money.

### Reuse

Every query reuses the prefix. The new tokens (query + answer) are small, fast, and cheap. Token cost: cached input is billed at a fraction of fresh input; take the ratio from the provider's price page (item 5 above).

### Invalidate

When the corpus changes, the cached prefix is wrong. Two strategies:

- **Hard invalidate:** drop the cache, re-prime with new corpus. Simple, predictable. Default.
- **Soft invalidate:** keep both versions briefly, serve in-flight conversations from old cache, route new conversations to new cache. Use when corpus refreshes are frequent and downtime is unacceptable.

Track `corpus_hash` on every cache entry. Mismatch = invalidate.

---

## Decision table

| Decision | Default | Upgrade when |
|---|---|---|
| Corpus size budget | The size at which your eval still passes on the chosen model, with headroom for prompt, history and output | Larger only after re-running the eval at the larger size |
| Refresh cadence | Weekly batch re-prime | On-write re-prime for hourly corpora — check economics first |
| Prompt cache TTL | Provider's default short TTL | Longer TTL when query gaps exceed the default and the extra write cost is below the re-prime cost |
| Cache miss handling | Re-prime synchronously, accept latency hit | Background re-prime + serve from previous version |
| Cache scope | One shared cache per corpus version | Per-tenant cache when corpus is tenant-specific (cost multiplier) |
| Provider | The provider whose cache terms (lookup above) fit your query pattern | Multi-provider only if eval shows quality delta |
| Citation surface | Section heading + line range within preloaded corpus | Use stable anchors (`#section-id`) if corpus is markdown — survives re-prime |
| Eval gate | Per-version eval set runs on every re-prime | Always — corpus changes can break the cache silently |

---

## Patterns

### P-CAG-1 — Single-prefix, many-tenants

When the corpus is the same across tenants, one cached prefix serves everyone. Each query appends `tenant_id + user_query`. Cheapest CAG pattern.

### P-CAG-2 — Per-tenant prefix

When corpus is tenant-scoped (per-customer policy doc, per-team handbook), prime a separate cache per tenant. Cost scales linearly with tenant count; only viable when per-tenant query volume justifies the cache.

### P-CAG-3 — Two-tier prefix

Stable evergreen content (glossary, ontology, role definitions) goes in an inner cached prefix. Volatile-but-still-CAG-eligible content (this month's policies) goes in an outer prefix that re-primes more often. The inner cache survives outer refreshes. Breakpoint placement and invalidation rules: [ai-prompt-engineering → Cache-Aware Prompt Layout](../../ai-prompt-engineering/SKILL.md#cache-aware-prompt-layout).

### P-CAG-4 — Eval-gated re-prime

Every corpus version runs an eval suite before becoming live. If accuracy drops vs prior version, block the re-prime and surface a diff. Prevents silent regressions where one bad doc poisons all answers.

### P-CAG-5 — CAG + retrieval fallback (hybrid)

CAG handles the 95% of queries answerable from the preloaded corpus. A confidence check on the answer triggers retrieval (H1–H7) for the long tail. The fallback layer is rare-but-real-coverage insurance.

---

## Anti-patterns

- **A-CAG-1 — CAG over a corpus that doesn't fit.** Aggressive summarization to "fit" loses information and erodes the citation surface. If it doesn't fit, use RAG. See A-CB-1.
- **A-CAG-2 — No re-prime discipline.** Updates to the corpus that don't trigger a re-prime serve stale answers from cache. Always track `corpus_hash`; always invalidate on mismatch.
- **A-CAG-3 — Ignoring provider cache TTLs.** A cache TTL shorter than the typical gap between queries means full prefill cost every query. Either buy a longer TTL (if the write premium is below the re-prime cost), or accept it's not actually cached.
- **A-CAG-4 — Skipping the prime.** First real query pays full prefill cost. On a 200K-token corpus that is multi-second latency and full-input billing. Always prime after refresh.
- **A-CAG-5 — Pretending CAG doesn't need eval.** "We preloaded the docs, so the answer is grounded." Wrong — long-context models still hallucinate, ignore middle-of-context content (lost-in-the-middle), and reorder claims. Eval is mandatory.
- **A-CAG-6 — Mixing CAG and RAG without a rule.** Both pull context into the prompt; if both fire on the same query you get conflicting citations and prompt bloat. Pick one as primary, the other as gated fallback (P-CAG-5).

---

## Composition

CAG sits in the [retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md) decision and is the canonical preload path.

- **With RAG (H1–H7):** P-CAG-5 hybrid. CAG for stable core, RAG for volatile long tail.
- **With fine-tune (I3):** Fine-tuned base provides behavior; CAG provides the knowledge layer. RA-CB-1 in [retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md).
- **With long-context-first (I2):** Long-context-first is CAG without the cache discipline — just raw whole-corpus prompting. CAG is long-context done right.
- **With managed-memory ([managed-memory-boundaries.md](managed-memory-boundaries.md)):** CAG prefix can sit inside a managed-memory turn. Don't confuse the two — managed memory is per-user; CAG prefix is per-corpus.

---

## Related

- [retrieve-vs-preload-vs-finetune.md](retrieve-vs-preload-vs-finetune.md) — The decision rubric
- [long-context-first-architecture.md](long-context-first-architecture.md) — CAG's sibling for whole-corpus prompting
- [fine-tune-for-behavior-not-facts.md](fine-tune-for-behavior-not-facts.md) — Composes with CAG (behavior + preload)
- [managed-memory-boundaries.md](managed-memory-boundaries.md) — Per-user state alongside corpus prefix
- [knowledge-compilation-and-wiki-pattern.md](knowledge-compilation-and-wiki-pattern.md) — How to assemble the corpus before preloading
- `ai-llm-inference` — KV-cache mechanics and provider-specific prompt caching
- `ai-coding-agents-provider-runtime/references/provider-capability-matrix.md` — Current cache limits by provider
- *"Don't Do RAG"* — [arXiv:2412.15605](https://arxiv.org/abs/2412.15605)
- Reference implementation — [hhhuang/CAG on GitHub](https://github.com/hhhuang/CAG)
