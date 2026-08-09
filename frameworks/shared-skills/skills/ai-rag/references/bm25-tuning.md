# BM25 Tuning Guide

A practical, repeatable process for tuning BM25 lexical search for maximum relevance.

---

## 1. When to Use BM25

Use BM25 when:
- Documents are text-heavy
- Users search using keywords
- High precision for exact matches is required
- Queries contain domain-specific vocabulary

---

## 2. Parameters

### k1 (Term Frequency Saturation)
Controls how term frequency influences relevance.  
**Range:** 1.2–1.8

### b (Length Normalization)
Controls how document length affects scoring.  
**Range:** 0.55–0.75

---

## 3. Optimization Workflow

### Step 1 — Preprocessing
- Remove excessive whitespace  
- Lowercase (if case-insensitive)  
- Strip markup (HTML, markdown)  

**Checklist**
- [ ] Tokenization verified  
- [ ] Stopword removal optional (test both ways)  

---

### Step 2 — Field Weighting
Boost important fields:
- `title`  
- `summary`  
- `h1/h2 headings`  
- metadata fields  

Example:
title^3 summary^1.5 body^1

---

### Step 3 — Query Expansion
Use LLM to:
- Expand synonyms  
- Add domain terms  
- Add abbreviations  

**Example Prompt (LLM Tools)**
Expand this query with synonyms and key domain terms:
<query>

---

### Step 4 — Parameter Tuning

Systematically search:
- k1 = [1.0, 1.2, 1.4, 1.6, 1.8]
- b = [0.45, 0.55, 0.65, 0.75]

Optimize using:
- nDCG@10  
- Recall@10  
- Precision@5  

---

## 4. BM25 Quality Checklist

- [ ] Field boosts applied  
- [ ] Query expansion improves recall  
- [ ] k1 and b tuned  
- [ ] Stopword handling validated  
- [ ] No tokenization inconsistencies  