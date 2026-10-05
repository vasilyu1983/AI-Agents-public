# IVF Index Configuration Template

Use IVF for large corpora (millions–hundreds of millions of vectors).

---

## 1. IVF Parameters

ivf:
nlist: 4096
nprobe: 16
metric: "cosine" # cosine | l2

---

## 2. Embedding Settings

embedding:
model: "<model_name>"
dim: <dimension>
normalize_vectors: true

---

## 3. Training

training:
sample_size: 100000

---

## 4. Validation Checklist

- [ ] nlist selected based on data size  
- [ ] nprobe tuned for recall  
- [ ] Embedding model consistent  
- [ ] Clustering stable  
