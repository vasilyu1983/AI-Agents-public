# Dataset Formatting Guide (Instruction, Chat, Transformation)

Templates and rules for building clean, consistent datasets for SFT and instruction tuning.

---

## 1. Instruction Format (Recommended)

Each example:

{
"instruction": "<what user wants>",
"input": "<optional context>",
"output": "<ideal response>"
}

**Rules**

- Use empty string for missing inputs  
- Keep outputs concise  
- Avoid multi-step reasoning unless required  

---

## 2. Chat Format (Multi-Turn)

{
"messages": [
{"role": "system", "content": "<policy/role>"},
{"role": "user", "content": "<query>"},
{"role": "assistant", "content": "<ideal reply>"}
]
}

**Rules**

- No overlapping roles  
- Ensure each conversation is self-contained  
- Avoid leaking system prompts in assistant outputs  

---

## 3. Transformation Format (Simple I/O)

{
"input": "<raw text>",
"output": "<transformed text>"
}

Use for:

- Rewriting  
- Summarization  
- Classification  
- Extraction  

---

## 4. Dataset Hygiene Rules

### A. No Leakage

- Do not include system prompts in model outputs  
- Do not include personal info  
- Remove timestamps or IDs that encode answers  

### B. Deduplication

- Remove near-duplicate samples  
- Deduplicate across categories  

### C. Quality Enforcement

- Each output = ideal model response  
- Avoid ambiguous tasks  
- Avoid mixed languages unless intentional  

---

## 5. Formatting Deliverables Checklist

- [ ] JSONL validated with `jq`  
- [ ] UTF-8 encoded  
- [ ] No trailing commas  
- [ ] Uniform field names  
- [ ] Balanced sample distribution  
- [ ] Full dataset documented in README  
