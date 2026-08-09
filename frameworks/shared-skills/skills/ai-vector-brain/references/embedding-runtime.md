# Self-Hosted Embedding Runtime

When data-residency policy, cost at scale, or compliance requirements bar calling a hosted embeddings API, you must run the embedding model yourself. This toolkit covers the **embedding-generation runtime** — the server or process that converts text into vectors. It is orthogonal to the choice of vector store: you can pair any runtime below with any backend in [backend-selection.md](backend-selection.md). This file is NOT a vector-store backend matrix (that lives in [backend-selection.md](backend-selection.md)) and NOT a hosted-API guide (OpenAI, Voyage, Cohere — those providers are handled by the `Embedder` class in `scripts/embed_and_load.py` already). The gap this closes: the skill has always assumed you can swap the `Embedder` class, but gave no recipe for doing so with a self-hosted runtime.

> Verified against primary sources fetched 2026-05-19 (see Verified-against table). Runtime feature claims are volatile — re-verify before production adoption.

## Table of Contents
- [When you need this](#when-you-need-this)
- [Decision](#decision)
- [Worked recipe — TEI behind the Embedder swap contract](#worked-recipe--tei-behind-the-embedder-swap-contract)
- [Per-runtime coverage](#per-runtime-coverage)
- [Anti-patterns](#anti-patterns)
- [Known traps](#known-traps)
- [Verified against](#verified-against)

## When you need this

**Trigger:** A hosted embeddings API (OpenAI, Voyage, Cohere) is barred by:

- **Data-residency / compliance** — vectors of PII or regulated content must not leave your network boundary; a hosted API transmits plaintext to a third party.
- **Cost at scale** — per-token API cost for re-embedding a large corpus (e.g. quarterly drift cycle, full re-embed on model change) exceeds the ops cost of running a GPU inference server. Rule of thumb: above ~50M tokens/month the break-even strongly favours self-hosting on a single A10G.
- **Latency SLA** — cold-start and network round-trips to a hosted API exceed your ingest or query-time latency budget.

**Eval / ops signal to watch:** Embedding API cost line grows faster than corpus line in your FinOps model; or your compliance scan flags plaintext-document egress to a third-party endpoint.

**When you do NOT need this:** A hosted embeddings API is acceptable on cost and residency — then self-hosting is undifferentiated ops burden. The managed-retrieval posture in the `ai-rag` skill covers when "plug in the hosted API and move on" is the right call. Check that boundary before building a runtime.

## Decision

Default to **TEI (text-embeddings-inference)** for production self-hosting:

- Ships as a single Docker image; no compilation steps required.
- Token-based dynamic batching — throughput scales without manual batch-size tuning.
- OpenAI-compatible HTTP endpoint — the TEI adapter below is a drop-in for the existing `Embedder.embed_batch` contract; no other script changes needed.
- Supports the widest range of production embedding architectures (BERT, RoBERTa, GTE, Qwen2, Qwen3, ModernBERT, Gemma3, Jina, MPNet).

This choice is **orthogonal to the vector store / retrieval-leg selection**. Swapping from a hosted API to TEI does not change whether you run a lexical leg, a dense-vector leg, or a hybrid; it does not change your HNSW index or RRF fusion function. For the leg decision, see [lexical-vs-vector-vs-hybrid.md](lexical-vs-vector-vs-hybrid.md).

Use Infinity when you need to serve **multiple embedding models simultaneously** from one process (multi-tenant, mixed-modality). Use vLLM when you are already running vLLM for LLM inference and want to co-locate embeddings on the same GPU fleet. Use Ollama for local dev/eval only — it is not designed for production ingest throughput. Use llama.cpp only when GGUF quantized weights are the requirement and no other runtime is available.

## Worked recipe — TEI behind the Embedder swap contract

The ingest pipeline (`scripts/embed_and_load.py`) isolates all provider calls behind the `Embedder` dataclass. Real interface (from `scripts/embed_and_load.py`, lines 47–59):

```python
@dataclass
class Embedder:
    provider: str   # e.g. "openai", "voyage", "cohere" — or "tei" in your adapter
    model: str      # provider model id; also stored in embeddings.model_id
    dim: int        # expected output dimension; checked after every batch

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        ...
```

Dimension assertion (line 201–202):
```python
if len(vectors) != len(batch) or any(len(v) != args.dim for v in vectors):
    sys.exit(f"embedder returned wrong shape: {len(vectors)} vectors, expected dim {args.dim}")
```

Model-id row-pin (line 190): `model_id = f"{args.provider}:{args.model}"` — this string is stored in `embeddings.model_id` per row, making a model swap detectable via `SELECT DISTINCT model_id FROM embeddings`.

**TEI adapter — add to `scripts/embed_and_load.py`:**

```python
# Add "tei" to the --provider choices in argparse, then add this branch
# in Embedder.embed_batch:

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        if self.provider == "openai":
            return self._openai(texts)
        if self.provider == "voyage":
            return self._voyage(texts)
        if self.provider == "cohere":
            return self._cohere(texts)
        if self.provider == "tei":
            return self._tei(texts)
        raise SystemExit(f"unknown provider: {self.provider}")

    def _tei(self, texts: Sequence[str]) -> list[list[float]]:
        """TEI OpenAI-compatible /v1/embeddings endpoint."""
        import httpx
        # Set TEI_BASE_URL=http://localhost:8080 (or your TEI host)
        base = os.environ.get("TEI_BASE_URL", "http://localhost:8080")
        # Request batching: send all texts in one HTTP call (TEI handles
        # token-based dynamic batching internally — no need to split here).
        payload = {"model": self.model, "input": list(texts)}
        resp = httpx.post(f"{base}/v1/embeddings", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()["data"]
        vectors = [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]
        # Dimension parity assertion: adapter output dim must match schema dim.
        if vectors and len(vectors[0]) != self.dim:
            raise ValueError(
                f"TEI returned dim={len(vectors[0])}, expected {self.dim}. "
                "Check --model and --dim match the model loaded in TEI."
            )
        return vectors
```

**Run TEI:**

```bash
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference:latest \
  --model-id BAAI/bge-m3 --port 80
```

**Invoke the adapter:**

```bash
cat chunks.jsonl | python scripts/embed_and_load.py \
  --provider tei --model BAAI/bge-m3 --dim 1024 \
  --dsn "$DATABASE_URL" --doc-type docs --source-id my-corpus
```

The `model_id` stored per row will be `tei:BAAI/bge-m3`. If you later swap to `tei:Qwen3-Embedding-0.6B`, the old rows remain under the old `model_id` — detectable without a full table scan.

## Per-runtime coverage

> This axis is the embedding **runtime**, orthogonal to the vector store — do not read it as a backend matrix. The 21-backend store matrix lives in [backend-selection.md](backend-selection.md); a runtime row says nothing about which vector store you use.

| Runtime | Verdict | Pointer / caveat |
|---|---|---|
| TEI (text-embeddings-inference) | production-fit | Use `_tei()` adapter above; TEI handles token-based dynamic batching; OpenAI-compatible `/v1/embeddings`; default choice |
| Infinity | production-fit | Use same OpenAI-compat adapter; preferred when serving multiple models simultaneously; "dynamic batching and tokenization dedicated in worker threads" |
| vLLM | works-with-caveat | OpenAI-compat `/v1/embeddings` works; anti-pattern unless you already run vLLM for LLM inference — adding it only for embeddings is excess ops surface |
| Ollama | works-with-caveat | `/api/embed` endpoint works for dev/eval; anti-pattern in production ingest — not designed for high-throughput batch embedding |
| llama.cpp | works-with-caveat | `llama-server --embedding` exposes `/embedding`; use when GGUF quantized weights are the hard requirement; anti-pattern if TEI can serve the model |

Legend: production-fit (adapter pointer) · works-with-caveat (how + "anti-pattern unless X") · not-suitable (use runtime Y) · unverified (not primary-source-confirmed at build)

## Anti-patterns

**Pattern → Anti-pattern → Recipe**

**Pattern: pin the embedding model identity per row from day one.**

- Anti-pattern: embedding model drift unpinned across runtimes — swapping the TEI model without updating `--model` leaves `embeddings.model_id` stale; old and new vectors coexist under the same model string; cosine similarity between query and corpus degrades silently.
- Recipe: always pass `--model <exact-model-id>` matching what TEI loaded; `model_id` is stored as `tei:<model-id>` per row; run `SELECT DISTINCT model_id FROM embeddings` before any swap to confirm which model populated the index; see [embedding-drift-mitigation.md](embedding-drift-mitigation.md).

**Pattern: assert dimension parity before any batch lands in the database.**

- Anti-pattern: dim mismatch between adapter output and schema — the HNSW index on `embeddings.embedding` is created with a fixed dimension; inserting vectors of wrong dim causes a silent pgvector type error or, worse, a silent truncation on some adapters.
- Recipe: the `_tei()` adapter above raises immediately when `len(vectors[0]) != self.dim`; the outer loop in `embed_and_load.py` also calls `sys.exit` on shape mismatch; never bypass `--dim`.

**Pattern: batch all texts into one HTTP call to the runtime.**

- Anti-pattern: no batching — one HTTP call per chunk — kills throughput on any self-hosted runtime; TEI and Infinity handle internal batching server-side, but the client must still send a reasonable input batch (e.g. 64 texts) per call to amortize connection overhead.
- Recipe: the `--batch-size` arg in `embed_and_load.py` (default 64) controls the client-side batch sent per call; keep it at 64 or tune up; never pass one text at a time.

**Pattern: choose the embedding runtime independently of the vector store.**

- Anti-pattern: treating runtime choice as a store choice — e.g. "I'm using Ollama so I should use Chroma" or "I'm using TEI so I need Qdrant." These are fully orthogonal axes.
- Recipe: pick the runtime (this file) then pick the store ([backend-selection.md](backend-selection.md)) independently; the `_tei()` adapter above works with any pgvector, Qdrant, Weaviate, or other store that accepts float vectors.

**Pattern: adopt a self-hosted runtime only when a hosted API is actually barred.**

- Anti-pattern: running a self-hosted runtime when a hosted API was already acceptable on cost and residency — YAGNI; you add GPU ops, model version management, and OOM debugging for zero retrieval benefit.
- Recipe: apply the "When you do NOT need this" gate above before building a runtime; if the hosted API passes compliance and FinOps review, keep it.

## Known traps

- **Tokenizer and pooling differences between runtimes produce different vectors for the "same" model.** A BAAI/bge-m3 checkpoint served via TEI with `cls` pooling vs Ollama with `mean` pooling yields different embeddings; cosine similarity between the two is not 1.0. Never mix vectors from different runtimes (or different pooling configs) in the same HNSW index without a full re-embed.
- **OpenAI-compatible endpoint shape differences.** TEI and vLLM both expose `/v1/embeddings` but TEI's response includes an `index` field on each data object (important for reordering when batching); vLLM may omit it. The `_tei()` adapter above sorts by `index` defensively.
- **GPU vs CPU build divergence.** TEI ships separate Docker images for GPU (CUDA) and CPU. The CPU image is dramatically slower; do not benchmark the CPU image and conclude TEI is slow. Always pin to the GPU image tag for production.
- **`normalize_embeddings` flag differences.** Some TEI model configs normalize embeddings to unit length by default; others do not. The HNSW `cosine` ops in pgvector (`vector_cosine_ops`) assumes unit-length vectors for efficiency. Confirm TEI's normalization setting matches your index ops type; mismatches degrade recall silently.
- **Max-sequence-length truncation silently changes vectors.** TEI truncates inputs that exceed the model's max sequence length (e.g. 512 tokens for BERT-family). A chunk that was embedded at full length when under the limit will be re-embedded at truncated length after a context window shift. Guard chunk size with `--token-count` from `chunk_markdown.py`.
- **Ollama `/api/embeddings` is deprecated.** The current endpoint is `/api/embed`; the old `/api/embeddings` still works but will be removed in a future release. Codebases copied from older examples may use the wrong path.

## Verified against

| Claim | Source id |
|---|---|
| TEI: "A blazing fast inference solution for text embeddings models" | `hf-tei` |
| TEI: "Token based dynamic batching" | `hf-tei` |
| TEI: "OpenAI-compatible endpoints via HTTP" | `hf-tei` |
| Infinity: "Infinity is a high-throughput, low-latency REST API for serving text-embeddings" | `infinity-embeddings` |
| Infinity: "Infinity uses dynamic batching and tokenization dedicated in worker threads" | `infinity-embeddings` |
| Infinity: "Mix-and-match multiple models. Infinity orchestrates them." | `infinity-embeddings` |
| Infinity: "OpenAPI aligned to OpenAI's API specs" | `infinity-embeddings` |
| vLLM: "OpenAI-compatible Embeddings API (`/v1/embeddings`)" | `vllm-embeddings` |
| vLLM: "Converts unstructured data (text, images, audio, etc.) into structured numerical vectors (embeddings)." | `vllm-embeddings` |
| Ollama: `/api/embed` — "Generate embeddings from a model" (current endpoint) | `ollama-embeddings` |
| Ollama: `/api/embeddings` — "this endpoint has been superseded by `/api/embed`" | `ollama-embeddings` |
| llama.cpp: "llama-server -m model.gguf --embedding --pooling cls -ub 8192" | `llama-cpp-embeddings` |
| llama.cpp: "# use the /embedding endpoint" | `llama-cpp-embeddings` |
| llama.cpp: "Serve an embedding model" | `llama-cpp-embeddings` |

## Model selection notes

### gemini-embedding-2 — Google's first natively multimodal embedding model

`gemini-embedding-2` (GA; preview model ID: `gemini-embedding-2-preview`) maps text, images, video, audio, and PDFs into a single 3,072-dimensional vector space. GA announced March 2026 via the Gemini API.

Key specs:
- **Dimensions:** 3,072 (Matryoshka truncation supported)
- **Context:** up to 8,192 text tokens; 6 images, 120 s video, 180 s audio, 6 PDF pages per call
- **Languages:** 100+
- **Model string:** `gemini-embedding-2` (stable) or `gemini-embedding-2-preview` (original preview)

**When to switch from `gemini-embedding-001`:** `gemini-embedding-001` remains the right choice for text-only corpora — it tops MTEB English API-tier as of April 2026. Switch to `gemini-embedding-2` when the corpus is genuinely multimodal (PDFs with embedded figures, slide decks, mixed image/text archives) and cross-modal retrieval is a requirement. Using `gemini-embedding-2` on a text-only corpus adds multimodal overhead for no retrieval benefit.

Use the same `_gemini()` adapter in `scripts/embed_and_load.py` with `--model gemini-embedding-2 --dim 3072`. For query-side use in `scripts/retrieve.py`, add a `gemini` branch to `embed_one()` mirroring the ingest adapter (see Fix 4 in the skill maintenance log). Source: `gemini-embedding-2` in `data/sources.json`.

### Qwen3-Embedding-8B — strong open-weight multilingual embedder

Qwen3-Embedding-8B (Apache-2.0) was a top-ranked open-weight model on MTEB Multilingual v2 through mid-2026, but open-weight multilingual leadership churns fast — NVIDIA's Llama-Embed-Nemotron-8B has since been reported ahead on the multilingual table. Treat "leader" claims as a snapshot, not a fact to hardcode: re-check the live [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) before picking a model on ranking alone. Qwen3-Embedding-8B remains a solid, well-supported default when multilingual retrieval quality matters and you can afford the 8B-parameter serving cost. TEI supports the Qwen3 architecture — serve with `--model-id Qwen/Qwen3-Embedding-8B`. For lighter deployments, Qwen3-Embedding-0.6B covers many multilingual use cases at a fraction of the memory footprint. Source: `qwen3-embedding` in `data/sources.json`.

### MUVERA — fixed-dimensional multi-vector encoding

MUVERA (Dhulipala et al., NeurIPS 2024) encodes multi-vector (late-interaction / ColBERT-style) representations into a single fixed-dimensional vector, enabling approximate MaxSim scoring with a standard ANN index. This removes the need for ColBERT-specific infrastructure. Weaviate 1.31+ supports MUVERA-style fixed-dimensional multi-vector encoding natively. Use MUVERA when you want ColBERT-class retrieval quality but cannot operate a dedicated ColBERT serving stack (RAGatouille). Source: `muvera-paper` in `data/sources.json`.
