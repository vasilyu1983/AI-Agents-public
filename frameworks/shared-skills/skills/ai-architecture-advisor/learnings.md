# ai-architecture-advisor — Learnings

## Patterns That Work

- [2026-06-26] Stage a simple→complete plan as independently-shippable end-states (each stoppable and valuable), not % of a system; gate every promotion on a measured failure, not 'nice to have'.
- [2026-06-26] Zero-tolerance entity isolation in RAG: prefer one Bedrock KB per entity (hard physical isolation) over a shared KB with metadata filter; the filter becomes defence-in-depth and per-entity KBs allow per-entity region pinning.
- [2026-06-26] AWS serverless RAG: S3 Vectors behind Bedrock Knowledge Bases is the cost-frugal scale-to-zero vector store (~90% cheaper than OpenSearch Serverless); promote to OpenSearch only for hybrid BM25+semantic or binary vectors.
- [2026-07-11] Fast-moving model/architecture citations decay within one release cycle even when the underlying arXiv ID is real — verified during a currency audit that "NSA in production on DeepSeek-V3.2" was a name collision (V3.2 actually ships DSA, a distinct finer-grained mechanism; NSA is the earlier research precursor) and that "DeepSeek-V3 is the frontier MoE" and "Gemini Diffusion" needed DeepSeek-V4 and DiffusionGemma added as the current examples. Treat any dated model-name + capability claim in this skill as due for a web-search re-check every audit cycle, not just at initial authoring.
## Mistakes to Avoid

## Domain Knowledge

## Open Questions

## Consolidated Principles

