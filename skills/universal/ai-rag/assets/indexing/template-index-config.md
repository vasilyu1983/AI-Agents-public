# Vector Index Configuration Template

Defines index parameters for ANN (HNSW, IVF, ScaNN, DiskANN) vector search.

---

## 1. Index Type

index_type: "<flat | hnsw | ivf | scann | diskann>"

Recommended:

- Flat → small datasets  
- HNSW → general purpose  
- IVF → large datasets  
- ScaNN → high-dimensional  
- DiskANN → extremely large corpora  

---

## 2. Embedding Settings

embedding_model: "<model_name>"
embedding_dim: <dimension>
normalize_vectors: true/false

---

## 3. HNSW Parameters

hnsw:
M: 32
ef_construction: 200
ef_search: 128

---

## 4. IVF Parameters

ivf:
nlist: 4096
nprobe: 16

---

## 5. ScaNN Parameters

scann:
training_sample_size: 50000
leaves: 2048
reordering_candidates: 100

---

## 6. Metadata Indexing

metadata_fields:
"section"
"tags"
"timestamp"

---

## 7. Validation Checklist

- [ ] Index type matches data size  
- [ ] ef_search/nprobe tuned  
- [ ] Embedding model consistent  
- [ ] Metadata searchable  
