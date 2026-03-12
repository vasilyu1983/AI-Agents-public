# Embedding Model Selection Guide

> Operational guide for choosing, deploying, and managing embedding models for RAG and search. Covers model comparison, dimensionality tradeoffs, fine-tuning, batch pipelines, versioning, assessment, and cost analysis. Focus on production decisions, not architecture theory.

**Freshness anchor:** January 2026 — OpenAI text-embedding-3-*, Cohere embed-v3, Voyage AI voyage-3, Jina v3, MTEB leaderboard current

---

## Decision Tree: Choosing an Embedding Model

```
START
│
├─ Budget constraint?
│   ├─ Zero cost (open source only)
│   │   ├─ English only → all-MiniLM-L6-v2 (fast) or gte-large-en-v1.5 (accurate)
│   │   ├─ Multilingual → multilingual-e5-large or BGE-M3
│   │   └─ Domain-specific → Fine-tune sentence-transformers base
│   │
│   └─ API budget available → Continue
│
├─ Latency requirement?
│   ├─ Real-time (< 50ms per query)
│   │   ├─ API → OpenAI text-embedding-3-small (fast, cheap)
│   │   └─ Self-hosted → all-MiniLM-L6-v2 (CPU viable)
│   │
│   └─ Batch / offline → Any model (latency not critical)
│
├─ Quality requirement?
│   ├─ Best available (enterprise search, legal, medical)
│   │   ├─ API → Voyage AI voyage-3 or Cohere embed-v3 (English)
│   │   ├─ API multilingual → Cohere embed-v3 or OpenAI text-embedding-3-large
│   │   └─ Self-hosted → BGE-large-en-v1.5 or NV-Embed-v2
│   │
│   └─ Good enough (chatbot, FAQ, basic search)
│       └─ OpenAI text-embedding-3-small or all-MiniLM-L6-v2
│
├─ Domain-specific needs?
│   ├─ Code → Voyage Code 3 or CodeBERT fine-tune
│   ├─ Legal → Fine-tune on legal corpus
│   ├─ Medical → PubMedBERT fine-tune or Voyage AI
│   └─ General → Standard models
│
└─ Dimensionality constraint?
    ├─ Storage limited → Matryoshka models (truncate to 256-512)
    └─ No constraint → Full dimensions (1024-3072)
```

---

## Quick Reference: Model Comparison (Q1 2026)

| Model | Dims | Max Tokens | MTEB Avg | Cost/1M tokens | Latency | Self-Host |
|-------|------|-----------|----------|-----------------|---------|-----------|
| OpenAI text-embedding-3-small | 1536 | 8191 | 62.3 | $0.02 | ~50ms | No |
| OpenAI text-embedding-3-large | 3072 | 8191 | 64.6 | $0.13 | ~80ms | No |
| Cohere embed-v3 (English) | 1024 | 512 | 64.5 | $0.10 | ~60ms | No |
| Voyage AI voyage-3 | 1024 | 32000 | 67.1 | $0.06 | ~70ms | No |
| Voyage AI voyage-3-lite | 512 | 32000 | 63.5 | $0.02 | ~40ms | No |
| Jina jina-embeddings-v3 | 1024 | 8192 | 65.5 | $0.02 | ~60ms | Yes (license) |
| all-MiniLM-L6-v2 | 384 | 256 | 56.3 | Free | ~5ms | Yes |
| gte-large-en-v1.5 | 1024 | 8192 | 63.1 | Free | ~30ms | Yes |
| BGE-large-en-v1.5 | 1024 | 512 | 63.6 | Free | ~30ms | Yes |
| BGE-M3 (multilingual) | 1024 | 8192 | 61.8 | Free | ~40ms | Yes |
| NV-Embed-v2 | 4096 | 32768 | 69.1 | Free | ~100ms | Yes (GPU) |

- **Prices are per 1M input tokens** — always check current pricing
- **MTEB scores** are approximate averages across retrieval tasks

---

## Operational Patterns

### Pattern 1: Dimensionality Tradeoffs with Matryoshka

- **Use when:** Need to balance storage cost vs retrieval quality
- **Concept:** Matryoshka models produce embeddings where the first N dimensions are independently useful

```python
# OpenAI text-embedding-3 supports dimension reduction natively
from openai import OpenAI
client = OpenAI()

# Full dimensions (best quality)
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="search query",
    dimensions=3072,  # full
)

# Reduced dimensions (cheaper storage, slightly lower quality)
response_small = client.embeddings.create(
    model="text-embedding-3-large",
    input="search query",
    dimensions=256,   # 12x storage savings
)

# For sentence-transformers Matryoshka models:
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")
embeddings_full = model.encode(texts)           # 768 dims
embeddings_256 = embeddings_full[:, :256]        # truncate to 256
# Normalize after truncation
embeddings_256 = embeddings_256 / np.linalg.norm(embeddings_256, axis=1, keepdims=True)
```

- **Dimension vs quality tradeoff (typical):**

| Dimensions | Storage/vector | Quality (relative) | Use Case |
|-----------|----------------|--------------------| ---------|
| 256 | 1 KB | 90-93% | High-volume, cost-sensitive |
| 512 | 2 KB | 95-97% | Good balance |
| 1024 | 4 KB | 98-99% | Standard production |
| 3072 | 12 KB | 100% | Maximum quality |

### Pattern 2: Domain-Specific Fine-Tuning

- **Use when:** General models underperform on domain-specific retrieval
- **Implementation:**

```python
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader

# Step 1: Prepare training data (query, positive_passage, negative_passage)
train_examples = [
    InputExample(texts=["search query", "relevant passage", "irrelevant passage"]),
    # ...
]

# Step 2: Fine-tune with triplet loss
model = SentenceTransformer("BAAI/bge-base-en-v1.5")
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)
train_loss = losses.TripletLoss(model=model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    output_path="./fine-tuned-embeddings",
    show_progress_bar=True,
)

# Step 3: Assess on holdout
from sentence_transformers.evaluation import InformationRetrievalEvaluator
ir_evaluator = InformationRetrievalEvaluator(queries, corpus, relevant_docs)
results = ir_evaluator(model)
```

- **Fine-tuning data requirements:**

| Data Size | Expected Improvement | Approach |
|-----------|---------------------|----------|
| < 100 pairs | Marginal | Use few-shot prompt instead |
| 100-1,000 pairs | 3-8% on domain tasks | Adapter layer (LoRA) |
| 1,000-10,000 pairs | 5-15% on domain tasks | Full fine-tune |
| > 10,000 pairs | 10-20% on domain tasks | Full fine-tune + hard negatives |

- **Hard negative mining (critical for quality):**

```python
def mine_hard_negatives(model, queries, corpus, k=10):
    """Find hard negatives: high similarity but irrelevant."""
    corpus_embeddings = model.encode(list(corpus.values()))
    query_embeddings = model.encode(queries)

    # Top-k most similar but not relevant
    hard_negatives = {}
    for i, query in enumerate(queries):
        scores = cosine_similarity([query_embeddings[i]], corpus_embeddings)[0]
        top_k_indices = np.argsort(scores)[-k:][::-1]
        # Filter out actual positives
        negatives = [idx for idx in top_k_indices if idx not in relevant_docs[query]]
        hard_negatives[query] = negatives

    return hard_negatives
```

### Pattern 3: Batch Embedding Pipeline

- **Use when:** Embedding large corpus (initial indexing or re-indexing)
- **Implementation:**

```python
import asyncio
from openai import AsyncOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt

client = AsyncOpenAI()

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
async def embed_batch(texts, model="text-embedding-3-small"):
    """Embed a batch of texts with retry logic."""
    response = await client.embeddings.create(model=model, input=texts)
    return [e.embedding for e in response.data]

async def embed_corpus(texts, batch_size=100, max_concurrent=10):
    """Embed entire corpus with batching and rate limiting."""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = [None] * len(texts)

    async def process_batch(start_idx, batch):
        async with semaphore:
            embeddings = await embed_batch(batch)
            for i, emb in enumerate(embeddings):
                results[start_idx + i] = emb

    tasks = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        tasks.append(process_batch(i, batch))

    await asyncio.gather(*tasks)
    return results

# Cost estimation before running
def estimate_embedding_cost(texts, model="text-embedding-3-small"):
    import tiktoken
    enc = tiktoken.encoding_for_model(model)
    total_tokens = sum(len(enc.encode(t)) for t in texts)
    cost_per_1m = {'text-embedding-3-small': 0.02, 'text-embedding-3-large': 0.13}
    estimated_cost = (total_tokens / 1_000_000) * cost_per_1m.get(model, 0.10)
    return {'total_tokens': total_tokens, 'estimated_cost_usd': estimated_cost}
```

### Pattern 4: Embedding Versioning and Migration

- **Use when:** Upgrading embedding model in production
- **Migration strategy:**

```
NEVER do a big-bang migration. Use dual-write pattern:

1. Deploy new model alongside old
2. Write new embeddings to separate index
3. A/B test retrieval quality (shadow mode)
4. If quality >= old model: swap primary index
5. Keep old index for 30 days (rollback safety)
6. Delete old index
```

```python
class EmbeddingVersionManager:
    """Manage embedding model versions with zero-downtime migration."""

    def __init__(self):
        self.models = {}
        self.active_version = None

    def register_model(self, version, model_name, index_name):
        self.models[version] = {
            'model': model_name,
            'index': index_name,
            'created': datetime.utcnow(),
        }

    def dual_write(self, text, versions):
        """Write embeddings to multiple indices."""
        for version in versions:
            model = self.models[version]
            embedding = encode(text, model['model'])
            write_to_index(model['index'], embedding)

    def migrate(self, from_version, to_version, corpus):
        """Re-embed entire corpus for new model."""
        new_model = self.models[to_version]
        batch_reindex(corpus, new_model['model'], new_model['index'])
```

### Pattern 5: Quality Assessment (MTEB and Custom)

- **Use when:** Choosing between models or validating fine-tuned model
- **Implementation:**

```python
# Option A: MTEB benchmark (standardized)
# pip install mteb
from mteb import MTEB
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en-v1.5")
benchmark = MTEB(tasks=["NFCorpus", "SciFact", "ArguAna"])
results = benchmark.run(model, output_folder="results/bge-large")

# Option B: Custom domain retrieval assessment
def assess_retrieval_quality(model, queries, corpus, relevant_docs, k=10):
    """Measure retrieval quality on your data."""
    query_embeddings = model.encode(queries)
    corpus_embeddings = model.encode(list(corpus.values()))

    metrics = {'recall@5': [], 'recall@10': [], 'mrr': [], 'ndcg@10': []}

    for i, query in enumerate(queries):
        scores = cosine_similarity([query_embeddings[i]], corpus_embeddings)[0]
        top_k = np.argsort(scores)[-k:][::-1]
        relevant = set(relevant_docs[query])

        # Recall@K
        for cutoff in [5, 10]:
            retrieved = set(top_k[:cutoff])
            metrics[f'recall@{cutoff}'].append(len(retrieved & relevant) / len(relevant))

        # MRR
        for rank, idx in enumerate(top_k, 1):
            if idx in relevant:
                metrics['mrr'].append(1 / rank)
                break
        else:
            metrics['mrr'].append(0)

    return {k: np.mean(v) for k, v in metrics.items()}
```

- **Quality targets:**

| Metric | Good | Acceptable | Needs Fine-Tuning |
|--------|------|-----------|-------------------|
| Recall@10 | > 0.85 | 0.70-0.85 | < 0.70 |
| MRR | > 0.60 | 0.40-0.60 | < 0.40 |
| NDCG@10 | > 0.55 | 0.40-0.55 | < 0.40 |

---

## Cost Comparison Calculator

```python
def compare_embedding_costs(num_documents, avg_tokens_per_doc, models=None):
    """Compare embedding costs across providers."""
    if models is None:
        models = {
            'openai-small': {'cost_per_1m': 0.02, 'dims': 1536},
            'openai-large': {'cost_per_1m': 0.13, 'dims': 3072},
            'cohere-v3': {'cost_per_1m': 0.10, 'dims': 1024},
            'voyage-3': {'cost_per_1m': 0.06, 'dims': 1024},
            'voyage-3-lite': {'cost_per_1m': 0.02, 'dims': 512},
            'self-hosted-bge': {'cost_per_1m': 0.005, 'dims': 1024},  # GPU amortized
        }

    total_tokens = num_documents * avg_tokens_per_doc
    results = []

    for name, info in models.items():
        embed_cost = (total_tokens / 1_000_000) * info['cost_per_1m']
        storage_gb = (num_documents * info['dims'] * 4) / (1024**3)  # float32
        results.append({
            'model': name,
            'embedding_cost': f"${embed_cost:.2f}",
            'storage_gb': f"{storage_gb:.2f}",
            'dimensions': info['dims'],
        })

    return pd.DataFrame(results)
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Choosing model by MTEB score alone | Your domain may differ from benchmarks | Assess on your data (custom retrieval set) |
| Using max dimensions without need | 3x storage cost for marginal improvement | Start at 512-1024, increase only if needed |
| No embedding versioning | Model upgrade requires big-bang reindex | Dual-write migration pattern |
| Embedding once, never updating | Stale embeddings as model improves | Plan for re-embedding cycles (annually min) |
| Mixing embedding models in one index | Embeddings from different models are incompatible | One model per index, strict versioning |
| Not normalizing embeddings | Cosine similarity requires unit vectors | Normalize after generation and after truncation |
| Fine-tuning without hard negatives | Easy negatives don't teach discrimination | Mine hard negatives from initial retrieval |
| Ignoring cost at scale | $0.02/1M seems cheap until you embed 100M docs | Calculate total cost before committing |
| Self-hosting without GPU budget | CPU inference too slow for real-time | Budget GPU or use API for real-time, CPU for batch |
| No fallback for API outages | Embedding API down = search down | Cache hot embeddings, have local fallback model |

---

## Validation Checklist

- [ ] Model assessed on domain-specific data (not just MTEB)
- [ ] Dimensionality chosen based on quality/cost tradeoff
- [ ] Cost estimated for full corpus embedding and ongoing queries
- [ ] Batch pipeline handles retries, rate limits, and progress tracking
- [ ] Embedding versioning strategy defined (dual-write migration)
- [ ] Normalization applied consistently
- [ ] Retrieval metrics tracked (recall@K, MRR, NDCG)
- [ ] Fine-tuning considered if recall@10 < 0.70 on domain data
- [ ] API fallback strategy defined for production
- [ ] Re-embedding schedule planned (model upgrades, corpus growth)

---

## Cross-References

- `ai-rag/references/rag-caching-patterns.md` — caching embeddings to reduce API calls
- `ai-rag/references/graph-rag-patterns.md` — embeddings for hybrid graph+vector search
- `ai-mlops/references/cost-management-finops.md` — tracking embedding costs
- `ai-mlops/references/experiment-tracking-patterns.md` — logging embedding model experiments
