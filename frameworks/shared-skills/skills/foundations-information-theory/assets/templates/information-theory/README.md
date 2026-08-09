# Information Theory Primitives — Composition Guide

11 domain-agnostic information-theory primitives. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-shannon-entropy.md](01-shannon-entropy.md) | Unquantified uncertainty; equal-probability assumptions |
| 2 | [02-mutual-information.md](02-mutual-information.md) | Linear-only dependence detection; biased finite-sample estimates |
| 3 | [03-kl-divergence.md](03-kl-divergence.md) | Symmetric distance misuse; zero-probability singularities |
| 4 | [04-cross-entropy.md](04-cross-entropy.md) | CE-as-similarity confusion; tokenizer-dependent perplexity |
| 5 | [05-channel-capacity.md](05-channel-capacity.md) | Throughput overestimation without noise accounting |
| 6 | [06-rate-distortion.md](06-rate-distortion.md) | Lossless-only thinking when lossy is sufficient |
| 7 | [07-mdl-principle.md](07-mdl-principle.md) | Overfitting; model complexity not penalized |
| 8 | [08-information-bottleneck.md](08-information-bottleneck.md) | Representation retains task-irrelevant information |
| 9 | [09-fano-inequality.md](09-fano-inequality.md) | Optimistic error estimates when residual entropy is high |
| 10 | [10-typical-sets-aep.md](10-typical-sets-aep.md) | Block codes shorter than entropy lower bound |
| 11 | [11-redundancy-compression.md](11-redundancy-compression.md) | Compression without redundancy budget; wrong code family |

---

## Composition Recipes

### Context-Window Budget

- **Objective**: maximize information per token under a fixed context-window budget
- **Stack**: #1 (entropy per segment — information content) + #2 (MI(segment, query) — relevance) + #7 (MDL penalty — description cost vs. gain)
- **Prune when**: L(segment) > I(segment; query) · context_budget / total_segments

### Retrieval Reranking

- **Objective**: select the top-m documents from k candidates that maximize information gain with minimum redundancy
- **Stack**: #2 (MI(query, doc_i) for relevance) + #1 (H(doc_i | doc_j) for pairwise redundancy) + #11 (redundancy budget — total bits available)
- **Add for quality floor**: #9 (Fano's inequality — confirm MI is sufficient to meet target accuracy)

### Prompt Complexity Diagnosis

- **Objective**: diagnose why a prompt produces high-variance outputs
- **Stack**: #1 (H(output | prompt) — output entropy empirically) + #9 (Fano — implied error bound) + #4 (perplexity per span — locate uncertain regions) + #8 (IB framing — is the prompt transmitting relevant information?)

### Lossy Compression Decision

- **Objective**: determine whether lossless compression is necessary or whether lossy saves significant bitrate
- **Stack**: #6 (R(D) — find minimum rate at target distortion) + #11 (redundancy — how far above entropy the source currently codes) + #10 (AEP — minimum block length for near-optimal codes)
- **Add for model selection**: #7 (MDL — choose between codebook variants)

### Distribution Shift Detection

- **Objective**: detect and quantify distribution shift between a reference distribution P and a current distribution Q
- **Stack**: #3 (KL divergence D_KL(P‖Q) — asymmetric measure of shift) + #4 (cross-entropy — decompose into reference entropy + KL) + #2 (MI between feature and label under both distributions — detect feature-label relationship shift)
- **Select JS divergence** from #3 when symmetric comparison is needed (e.g., bidirectional monitoring)

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — anti-patterns by domain, full decision checklist, sources
- [`../../../SKILL.md`](../../../SKILL.md) — skill entry point with quick reference and composition recipes
