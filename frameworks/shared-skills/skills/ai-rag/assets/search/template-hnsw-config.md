# HNSW Index Configuration Template

HNSW is the default ANN index for dense vector search.

---

## 1. Index Parameters

hnsw:
M: 32 # graph connectivity
ef_construction: 200 # build-time accuracy
ef_search: 128 # query-time accuracy

---

## 2. Embedding Settings

embedding:
model: "<embedding_model>"
dim: <dimension>
normalize_vectors: true

---

## 3. Metadata

metadata_fields:
"section"
"tags"
"timestamp"

---

## 4. Latency vs Recall Tuning

- Increase `ef_search` → higher recall, slower  
- Decrease `ef_search` → lower recall, faster  

---

## 5. Validation Checklist

- [ ] M tuned  
- [ ] ef_search tuned  
- [ ] Same embedding model for indexing & querying  
- [ ] Metadata filters tested  
