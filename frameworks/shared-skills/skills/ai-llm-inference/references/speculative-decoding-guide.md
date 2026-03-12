# Speculative Decoding Guide

Speculative decoding speeds up inference by pairing a **draft model** with a **target model**.

---

## 1. Architecture Overview

1. Draft model predicts next N tokens  
2. Target model validates predictions  
3. Matching tokens are accepted  
4. Mismatched tokens fall back to target model  
5. Repeat  

Speedups: 2×–5× typical.

---

## 2. Choosing a Draft Model

### Recommended sizes

- 1B–3B model for 7B–13B target  
- 3B–7B model for 30B–70B target  

### Requirements

- Same tokenizer  
- Similar domain training  
- High match rate (>80% ideal)

---

## 3. Configuration Pattern

### Key parameters

- Draft_length (number of speculative tokens)
- Acceptance_threshold  
- Max_accept_length  

### Example

draft_length: 5
acceptance_threshold: 0.80
fallback_policy: "target_only"

---

## 4. Evaluation Guidelines

Evaluate on:

- Long prompts  
- Short prompts  
- Multi-turn conversations  
- RAG queries  

Measure:

- Speedup vs baseline  
- Format stability  
- Error rates in JSON output  

---

## 5. Failure Modes & Fixes

### A. Low match rate (<70%)

- Fix: pick smaller draft window  
- Fix: choose larger draft model  

### B. Output formatting regressions

- Fix: stricter schemas  
- Fix: smaller draft_length  

### C. Quality degradation

- Fix: require higher acceptance threshold  

---

## 6. Speculative Decoding Checklist

- [ ] Draft model validated  
- [ ] Match rate measured  
- [ ] Speedup ≥ 2×  
- [ ] No regressions in evaluation suite  
