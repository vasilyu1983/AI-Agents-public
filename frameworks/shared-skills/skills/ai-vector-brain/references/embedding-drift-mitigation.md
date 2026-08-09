# Embedding Drift Mitigation

How to detect, quantify, and mitigate embedding drift in a production vector brain without paying the full re-embedding cost every time.

## Two distinct drifts

| Drift | Trigger | Detection signal |
|-------|---------|------------------|
| **Model drift** | Provider silently updates the embedding model behind a stable API alias, or your team upgrades to a new model version | Mean cosine similarity between query and top-k results shifts > 2σ from baseline within hours of a deploy or provider release |
| **Corpus drift** | Same model, but new docs added, old docs expired, terminology evolved over months | Held-out labeled eval recall@k decays gradually (weeks/months); no abrupt break |

Treating these as one problem leads to over-reaction (re-embedding the world when only the eval set drifted) or under-reaction (ignoring a silent model swap because the drift is gradual at the corpus level).

## Detection: minimum viable instrumentation

1. **Pin `embedding_model` and `embedding_dim` per row** on ingest. Without this you cannot tell which rows live in which embedding space.
2. **Log query embedding + top-k cosine distribution** for every retrieval. Aggregate as a rolling 7-day mean and stdev.
3. **Maintain a 50–200 query labeled eval set**. Run recall@k and MRR on a weekly cron. Plot trend; alert on > 2σ deviation from rolling baseline.
4. **Tag every batch with `embedding_batch_id` and `created_at`**. When drift fires, you can scope the re-embed to affected batches instead of the whole corpus.

## Mitigation options, in order of cost

| Strategy | Recall recovery | Compute cost vs full re-embed | When |
|----------|-----------------|-------------------------------|------|
| **Drift-Adapter** (lightweight projection learned to map old-space vectors into new-space) | 95–99% | ~1× (≈100× cheaper than re-embed) | Model upgrade on a large corpus where dual-index serving is too costly; arxiv 2509.23471 (EMNLP 2025) |
| **Dual-index serving** (run old + new index in parallel, route by `embedding_model`) | 100% | ~2× storage, ~2× query cost during window | Migration period; combine with phased re-embed |
| **Full re-embedding** | 100% | 1× per-corpus compute (~$12–$40 per 10M vectors at May 2026 rates) | New domain, new modality, or recall recovery < 95% with Drift-Adapter |
| **Incremental re-embed of hot 5%** | Partial — covers the 80% query mass | ~5% of full re-embed | Corpus drift where query concentration is well-known |

## Operational defaults

- Treat re-embedding as a **scheduled FinOps line item**, not an incident. Quarterly is realistic for active products.
- Run the new index against the labeled eval set **before** cutting traffic. Recall on the new index must meet or beat the old index on the same queries — otherwise the re-embed is a regression in disguise.
- Never delete the old index until the new one has served production traffic for at least one full week with parity on recall and latency.
- When using Drift-Adapter, periodically re-validate that the adapter's projection still holds — adapter quality decays as the model continues to evolve.

## Source

- [Drift-Adapter: Near Zero-Downtime Embedding Model Upgrades in Vector Databases](https://arxiv.org/abs/2509.23471) — arxiv 2509.23471, EMNLP 2025.
- [Embedding Models in Production: Versioning and Index Drift](https://tianpan.co/blog/2026-04-09-embedding-models-production-versioning-index-drift) — production embedding-drift writeup, April 2026.
