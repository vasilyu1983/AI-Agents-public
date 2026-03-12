# BM25 Configuration Template

A production-ready configuration for lexical BM25 retrieval.

---

## 1. Preprocessing Rules

preprocessing:
lowercase: true
strip_html: true
normalize_unicode: true
remove_punctuation: false
stopwords: "auto" # auto | none | custom_list

---

## 2. BM25 Parameters

bm25:
k1: 1.4
b: 0.65

These values are baseline defaults — tune based on evaluation.

---

## 3. Field Weights

field_boosts:
title: 3.0
subtitle: 1.5
body: 1.0
tags: 2.0

---

## 4. Indexing Settings

index:
store_positions: true
store_offsets: false
store_docvectors: false

---

## 5. Query Configuration

query:
expand_synonyms: true
use_spellcheck: false

---

## 6. Quality Checklist

- [ ] k1 tuned  
- [ ] b tuned  
- [ ] Field boosts validated  
- [ ] Tokenizer consistent across indexing and query  
