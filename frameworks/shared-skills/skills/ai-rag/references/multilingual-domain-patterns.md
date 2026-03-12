# Multilingual & Domain Alignment Patterns

Operational patterns for search systems handling multiple languages and specialized domains.

---

## When to Use

Apply these patterns when:
- Users search in multiple languages
- Documents span different languages
- Domain-specific vocabulary differs from general embeddings
- Cross-language retrieval needed
- Specialized domains (legal, medical, technical)

---

## Pattern 1: Multilingual Embedding Selection

### Decision Rules

**Single language:**
- Use language-specific model (higher accuracy)
- Examples: CamemBERT (French), BETO (Spanish)

**Multiple languages (cross-lingual retrieval):**
- Use multilingual embeddings
- Examples: multilingual-e5, mBERT, XLM-RoBERTa, LaBSE

**50+ languages:**
- Use LaBSE or LASER (specialized for cross-lingual)

### Evaluation by Language

```python
def evaluate_per_language(results_by_lang, labels_by_lang):
    """
    Evaluate search quality per language slice
    """
    metrics = {}

    for lang in results_by_lang:
        results = results_by_lang[lang]
        labels = labels_by_lang[lang]

        metrics[lang] = {
            'recall@10': compute_recall(results, labels, k=10),
            'ndcg@10': compute_ndcg(results, labels, k=10),
            'num_queries': len(results)
        }

    return metrics
```

**Checklist**
- [ ] Multilingual model chosen based on language coverage
- [ ] Per-language recall tested on eval set
- [ ] Cross-language retrieval accuracy validated
- [ ] Language detection accuracy >95%

---

## Pattern 2: Language Detection & Preprocessing

### Language Detection

```python
from langdetect import detect, LangDetectException

def detect_language(text, default='en'):
    """
    Detect language with fallback
    """
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return default

# Apply per-language preprocessing
def preprocess_by_language(text, lang):
    """
    Language-specific normalization
    """
    if lang == 'de':
        # German: handle compound words
        return german_compound_splitter(text)
    elif lang == 'ar':
        # Arabic: normalize diacritics
        return normalize_arabic(text)
    elif lang == 'ja':
        # Japanese: tokenize with morphological analysis
        return tokenize_japanese(text)
    else:
        # Default: basic normalization
        return text.lower().strip()
```

### Per-Language Tokenization

```python
def tokenize_multilingual(text, lang):
    """
    Use language-appropriate tokenizer
    """
    tokenizers = {
        'en': 'bert-base-uncased',
        'zh': 'bert-base-chinese',
        'ja': 'cl-tohoku/bert-base-japanese',
        'ar': 'aubmindlab/bert-base-arabertv2',
        'de': 'bert-base-german-cased'
    }

    tokenizer_name = tokenizers.get(lang, 'bert-base-multilingual-cased')
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    return tokenizer.tokenize(text)
```

**Checklist**
- [ ] Language detection at query/index time
- [ ] Per-language preprocessing (stemming, normalization)
- [ ] Mixed-script queries handled (Latin + CJK)
- [ ] Fallback to multilingual tokenizer for unsupported languages

---

## Pattern 3: Multilingual Hybrid Search

### Architecture

```python
def multilingual_hybrid_search(query, k=10):
    """
    Combine BM25 (per-language) + multilingual vectors
    """
    # Detect query language
    query_lang = detect_language(query)

    # Per-language BM25 retrieval
    bm25_results = []
    if query_lang in ['en', 'es', 'fr', 'de']:
        # Use language-specific BM25 index
        bm25_results = bm25_indexes[query_lang].search(query, k=k)
    else:
        # Fallback to multilingual BM25
        bm25_results = bm25_multilingual.search(query, k=k)

    # Multilingual vector retrieval
    query_vector = multilingual_encoder.encode(query)
    vector_results = vector_index.search(query_vector, k=k)

    # Weighted fusion
    combined = weighted_fusion(
        bm25_results,
        vector_results,
        alpha=0.3,  # BM25 weight
        beta=0.7    # Vector weight
    )

    return combined[:k]
```

### Cross-Language Retrieval

```python
def cross_language_search(query, query_lang, target_langs, k=10):
    """
    Retrieve documents in different languages than query
    """
    # Encode query with multilingual model
    query_vector = multilingual_encoder.encode(query, lang=query_lang)

    # Search across all language indexes
    results_by_lang = {}
    for lang in target_langs:
        results_by_lang[lang] = vector_indexes[lang].search(
            query_vector,
            k=k,
            filter={'language': lang}
        )

    # Merge results
    all_results = []
    for lang, results in results_by_lang.items():
        all_results.extend(results)

    # Rerank globally
    reranked = multilingual_reranker.rerank(query, all_results, k=k)

    return reranked
```

**Checklist**
- [ ] Per-language BM25 indexes for major languages
- [ ] Multilingual vector embeddings for all languages
- [ ] Fusion strategy tested on multilingual eval set
- [ ] Cross-language retrieval accuracy validated

---

## Pattern 4: Multilingual Reranking

### Cross-Encoder Reranking

```python
from sentence_transformers import CrossEncoder

# Load multilingual cross-encoder
reranker = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')

def multilingual_rerank(query, candidates, query_lang, k=5):
    """
    Rerank candidates using multilingual cross-encoder
    """
    # Prepare query-document pairs
    pairs = [[query, c['text']] for c in candidates]

    # Score with cross-encoder
    scores = reranker.predict(pairs)

    # Sort by score
    for i, c in enumerate(candidates):
        c['rerank_score'] = scores[i]

    reranked = sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)

    return reranked[:k]
```

**Checklist**
- [ ] Multilingual reranker supports target languages
- [ ] Reranking improves cross-language nDCG by ≥10%
- [ ] Latency acceptable (<100ms per query)

---

## Pattern 5: Domain-Specific Embeddings

### When to Use Domain Models

Use domain-specific embeddings when:
- General embeddings show low recall on domain queries
- Domain has specialized vocabulary (legal, medical, finance)
- Documents contain technical jargon
- Domain models available (BioBERT, Legal-BERT, FinBERT)

### Fine-Tuning for Domain

```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Prepare domain-specific training data
train_examples = [
    InputExample(texts=['query 1', 'relevant doc 1'], label=1.0),
    InputExample(texts=['query 1', 'irrelevant doc'], label=0.0),
    # ... more examples
]

# Load base model and fine-tune
model = SentenceTransformer('all-MiniLM-L6-v2')
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Use contrastive loss
train_loss = losses.CosineSimilarityLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100
)

# Save domain-adapted model
model.save('models/domain-embeddings-v1')
```

**Checklist**
- [ ] Domain model available or fine-tuned
- [ ] Recall improvement ≥15% over general embeddings
- [ ] Domain eval set created (50+ queries)
- [ ] Model updated as domain evolves

---

## Pattern 6: Mixed-Language Document Handling

### Chunking Strategy for Mixed-Language Docs

```python
def chunk_mixed_language_doc(doc_text):
    """
    Split document by language boundaries
    """
    chunks = []
    current_chunk = []
    current_lang = None

    sentences = split_sentences(doc_text)

    for sentence in sentences:
        sent_lang = detect_language(sentence)

        if sent_lang != current_lang:
            # Language switch detected
            if current_chunk:
                chunks.append({
                    'text': ' '.join(current_chunk),
                    'language': current_lang
                })
            current_chunk = [sentence]
            current_lang = sent_lang
        else:
            current_chunk.append(sentence)

    # Add final chunk
    if current_chunk:
        chunks.append({
            'text': ' '.join(current_chunk),
            'language': current_lang
        })

    return chunks
```

### Index Mixed-Language Chunks

```python
def index_mixed_language_chunks(chunks):
    """
    Index with language metadata
    """
    for chunk in chunks:
        # Embed with language-appropriate model
        if chunk['language'] in ['en', 'es', 'fr']:
            embedding = language_models[chunk['language']].encode(chunk['text'])
        else:
            embedding = multilingual_model.encode(chunk['text'])

        # Store with language tag
        vector_index.add(
            embedding=embedding,
            metadata={
                'text': chunk['text'],
                'language': chunk['language']
            }
        )
```

**Checklist**
- [ ] Language boundaries detected in mixed documents
- [ ] Chunks tagged with language metadata
- [ ] Retrieval filters by language when needed
- [ ] Cross-language leakage monitored

---

## Pattern 7: Multilingual Evaluation & Monitoring

### Per-Language Dashboards

```python
# Track metrics by language slice
language_metrics = {
    'en': {'recall@10': 0.89, 'ndcg@10': 0.82, 'num_queries': 5000},
    'es': {'recall@10': 0.76, 'ndcg@10': 0.71, 'num_queries': 1200},
    'fr': {'recall@10': 0.78, 'ndcg@10': 0.73, 'num_queries': 800},
    'de': {'recall@10': 0.74, 'ndcg@10': 0.69, 'num_queries': 600},
    'zh': {'recall@10': 0.81, 'ndcg@10': 0.75, 'num_queries': 2000}
}

# Alert on underperforming languages
for lang, metrics in language_metrics.items():
    if metrics['recall@10'] < 0.75:
        alert(f"Low recall for {lang}: {metrics['recall@10']}")
```

### Cross-Language Leakage Detection

```python
def detect_cross_language_leakage(query, results, query_lang):
    """
    Check if results match query language
    """
    for result in results[:5]:
        result_lang = detect_language(result['text'])

        if result_lang != query_lang:
            # Log potential leakage
            log_warning({
                'query': query,
                'query_lang': query_lang,
                'result_lang': result_lang,
                'doc_id': result['doc_id']
            })
```

**Checklist**
- [ ] Per-language dashboards + alerting live
- [ ] Bilingual eval sets for cross-language retrieval
- [ ] Leakage detection monitoring active
- [ ] Language coverage balanced (no language left behind)

---

## Multilingual Quality Checklist

- [ ] Language detection + per-language preprocessing
- [ ] Multilingual embeddings evaluated on target slices
- [ ] Reranker supports languages in scope
- [ ] Per-language dashboards + alerting live
- [ ] Domain-specific models for specialized vocabulary
- [ ] Mixed-language documents handled correctly
- [ ] Cross-language retrieval tested with bilingual eval set
- [ ] Leakage detection monitoring active
