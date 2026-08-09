# Embedding Model Selection Guide

Choose embedding models by fit, not by leaderboard screenshots.

## Selection Criteria

| Criterion | Questions to answer |
|-----------|---------------------|
| Domain fit | Is the corpus general, multilingual, code-heavy, legal, medical, or product-specific? |
| Latency | Is query-time embedding on the critical path? |
| Cost | Can you afford managed APIs for indexing and query traffic? |
| Deployment | Do you need self-hosting, residency, or air-gapped operation? |
| Context length | Do your chunks or queries exceed short-token embedders? |
| Dimensionality | Does storage or index memory pressure require lower dimensions? |

## Durable Heuristics

- Use one document embedding family and one query embedding family unless the provider explicitly supports asymmetric retrieval.
- Reindex whenever embedding model, dimension, or normalization changes.
- Do not choose by benchmark average alone; test on your own retrieval set.
- If storage is tight, use lower dimensions only after measuring recall loss.

## Model Families To Check Live

- Bedrock-hosted (AWS-native): Amazon Nova 2 Multimodal Embeddings [current default, 2026] — Matryoshka dims 3072/1024/384/256, 8192-token context, 200 languages, unified text/doc/image/video/audio; Titan Embeddings [legacy]; verify the current Bedrock embeddings catalog before selecting
- Managed APIs: OpenAI, Cohere, Voyage AI, Jina
- Open-weight or self-hosted: BGE, GTE, E5, NV-Embed, Sentence Transformers families
- Multilingual: BGE-M3, multilingual E5, provider multilingual offerings
- Code retrieval: code-specialized embedders or hybrid lexical + semantic retrieval

## Evaluation Workflow

1. Pick 2-4 candidate embedding families.
2. Keep chunking, filtering, and reranking constant.
3. Reindex a representative slice.
4. Measure recall@k, MRR, nDCG, latency, and cost.
5. Keep the simplest option that meets product targets.

## Matryoshka / Reduced Dimensions

Use dimension reduction only when index size or memory is a real bottleneck. Keep a baseline at full dimension and compare retrieval quality before adopting a smaller shape.

## Anti-Patterns

- Mixing embeddings from different model versions in one index
- Assuming higher dimensions always win
- Hard-coding volatile prices or leaderboard scores into durable docs
- Fine-tuning before proving that chunking, filters, and reranking are already well-tuned

## March 2026 Note

Provider features, prices, context limits, and benchmark standing change frequently. Verify all current model-specific claims from primary docs before recommending a concrete vendor model.

## July 2026 MTEB Leaderboard Note

The MTEB top tier changed materially in H1 2026 and remains contested. As of July 2026 (re-verified):

- **API tier:** Google's Gemini Embedding (`gemini-embedding-001`) leads the MTEB overall leaderboard.
- **Open-weights:** The Qwen3-Embedding family (Apache-2.0 license) trails Gemini Embedding closely and leads the open-weight tier; some third-party trackers report other challengers (e.g., QZhou-Embedding) near the top — treat any single-source ranking claim as provisional.

These standings are volatile — the leaderboard changes with each new model release, and different tracking sites disagree on exact scores. Always re-verify the current MTEB leaderboard at [huggingface.co/spaces/mteb/leaderboard](https://huggingface.co/spaces/mteb/leaderboard) before selecting an embedding model for a new project or benchmark comparison. Do not rely on this note as a current source; it records what was true at the time of writing.

**Judgment call, not just a ranking lookup:** the top MTEB score is rarely the right selection criterion in isolation. Weight it against license (Apache-2.0 vs. proprietary API vs. non-commercial), context length fit for your chunk size, multilingual coverage if the corpus needs it, and reindex cost if you might need to switch later — a Matryoshka-capable model that lets you shrink dimensions without a full reindex is often worth more than 1-2 MTEB points.
