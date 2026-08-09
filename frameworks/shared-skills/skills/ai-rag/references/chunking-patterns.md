# Chunking Patterns for RAG Systems

Chunking is the primary driver of retrieval quality. These patterns provide
repeatable, production-ready chunk strategies for different data types.

> Decision page (which strategy for which content type) lives in
> [`chunking-strategies.md`](chunking-strategies.md). Markdown / policy /
> ADR / git-anchored shapes live in
> [`../../ai-context-layer/references/markdown-chunking-patterns.md`](../../ai-context-layer/references/markdown-chunking-patterns.md).

---
## Table of Contents

- [1. Core Chunking Principles](#1-core-chunking-principles)
- [2. Standard Sliding-Window Pattern](#2-standard-sliding-window-pattern)
- [Use for:](#use-for)
- [Parameters:](#parameters)
- [Procedure:](#procedure)
- [3. Hierarchical Chunking Pattern](#3-hierarchical-chunking-pattern)
- [Algorithm:](#algorithm)
- [Benefits:](#benefits)
- [4. Code Chunking Pattern (Special Case)](#4-code-chunking-pattern-special-case)
- [Rules:](#rules)
- [Recommended:](#recommended)
- [Add metadata:](#add-metadata)
- [5. Table Chunking Pattern](#5-table-chunking-pattern)
- [Techniques:](#techniques)
- [6. PDF/Scanned Document Chunking](#6-pdfscanned-document-chunking)
- [Steps:](#steps)
- [7. Chunk Quality Control Checklist](#7-chunk-quality-control-checklist)


## 1. Core Chunking Principles

- Preserve **semantic boundaries** (sections, headings, paragraphs)
- Overlap chunks to avoid context cutting
- Avoid overly small chunks (too noisy)
- Avoid overly large chunks (retrieval dilution)
- Always include **metadata** (source, URI, heading, page number)

**Checklist**
- [ ] Chunk size tuned for doc type  
- [ ] Overlap defined  
- [ ] Metadata preserved  
- [ ] No empty/orphaned chunks  

---

## 2. Standard Sliding-Window Pattern

### Use for:
- Blogs  
- Articles  
- Long-form documentation  

### Parameters:
- Chunk size: **500–800 tokens**
- Overlap: **50–150 tokens**

### Procedure:
1. Clean text  
2. Normalize whitespace  
3. Slide window with overlap  
4. Attach metadata  

---

## 3. Hierarchical Chunking Pattern

Use for structured docs:

- Manuals  
- Section-based docs  
- Legal documents  
- Research papers

### Algorithm:
1. Split by top-level headings  
2. Inside each section, chunk using sliding window  
3. Metadata includes section → subsection → paragraph  

### Benefits:
- Section-aware retrieval  
- Better context grouping  

---

## 4. Code Chunking Pattern (Special Case)

Code behaves differently from natural language.

### Rules:
- Chunk by **logical blocks**, not fixed sizes  
- Use syntax-aware splitting:
  - Functions  
  - Classes  
  - Modules  

### Recommended:
- Chunk size: **80–200 tokens**
- Overlap: **0–20 tokens**

### Add metadata:
- Programming language  
- File path  
- Function name  

---

## 5. Table Chunking Pattern

Tables require structural preservation.

### Techniques:
- Convert rows to key-value pairs  
- Pair headers with row values  
- Use **row-wise chunks**, not cell-wise  

**Checklist**
- [ ] All rows retain column names  
- [ ] Numeric fields not concatenated without separators  
- [ ] Provide normalized string + structured version  

---

## 6. PDF/Scanned Document Chunking

### Steps:
1. Extract text with OCR (if needed)  
2. Remove headers/footers  
3. Reconstruct paragraphs using layout metadata  
4. Chunk 700–1200 token windows  

---

## 7. Chunk Quality Control Checklist

- [ ] Random sample of chunks inspected  
- [ ] No broken sentences or stray tokens  
- [ ] Metadata consistently applied  
- [ ] Chunk count reasonable (no explosion)  
