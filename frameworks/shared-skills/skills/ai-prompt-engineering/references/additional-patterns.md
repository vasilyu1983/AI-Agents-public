# Additional Operational Patterns

*Purpose: Supplemental operational patterns used in production prompts that do not fall under RAG, extraction, agents, or standard reasoning.*

## Contents
- Multi-intent resolution
- Debounce pattern (clarification before execution)
- Content audit pattern
- Constraint validator pattern
- Style enforcement patterns
- Comparison pattern
- Risk analysis pattern
- Summarization patterns
- Anti-contamination pattern
- Multi-format output pattern
- Rewrite with preservation pattern
- Quick reference table

---

# 1. Multi-Intent Resolution

Use when users ask multiple things in one message.

## 1.1 Intent Extraction Pattern
```

Identify all user intents as a list of short labels.
Do not answer them yet.
Return only the list.

```

Output:
```

["intent_1", "intent_2"]

```

Checklist:
- [ ] No answering  
- [ ] No narrative  
- [ ] Label-only format  

---

## 1.2 Intent Prioritization Pattern
```

Rank intents by:

1. Safety  
2. Required clarification  
3. Feasibility  
4. User priority signals  

```

Output:
```

["primary_intent", "secondary_intent"]

```

Checklist:
- [ ] Deterministic ranking  
- [ ] No speculation about motives  

---

## 1.3 Intent Decomposition Pattern
Use when a single intent contains multiple operations.

Structure:
```

Subtasks:

- task A
- task B
- task C

```

Rules:
- Subtasks atomic  
- No reasoning exposed  

---

# 2. Debounce Pattern (Clarification Before Execution)

Use when user input is incomplete or ambiguous.

## 2.1 Structure
```

Your request is missing required details:

- missing_1
- missing_2

Provide these to continue.

```

Checklist:
- [ ] Enumerate missing items  
- [ ] No assumptions  
- [ ] No answering partial request  

---

# 3. Content Audit Pattern

Use to validate user-supplied text before transformations.

## 3.1 Structure
```

Audit:

- completeness: ok|missing
- contradictions: yes|no
- format_issues: [ ... ]
- prohibited_content: yes|no

```

Rules:
- Deterministic checks  
- No subjective opinions  

---

# 4. Constraint Validator Pattern

Validate prompts, inputs, or candidate outputs before running a flow.

## 4.1 Structure
```

Validation:

- meets_format: true|false
- meets_schema: true|false
- violations: ["rule_1", "rule_2"]

```

Checklist:
- [ ] Fixed keys  
- [ ] No prose aside from short labels  

---

# 5. Style Enforcement Patterns

## 5.1 Fixed-Length Sentence Pattern
```

Rewrite using sentences of 10–14 words.

```

Checklist:
- [ ] Sentence count unchanged unless rule states otherwise  
- [ ] Every sentence meets range  

---

## 5.2 Tone Enforcement Pattern
Allowed tones:
- neutral  
- concise  
- formal  
- instructional  

Structure:
```

Rewrite with TONE = {{tone}} (no other changes).

```

Checklist:
- [ ] No added content  
- [ ] Pure tone shift  

---

# 6. Comparison Pattern

Use for X vs Y comparisons.

## 6.1 Structure
```

Comparison:

- similarities: ["..."]
- differences: ["..."]
- final_choice: "X|Y|tie"

```

Rules:
- Lists must quote explicit attributes  
- final_choice must match criteria  

---

# 7. Risk Analysis Pattern (Operational, Not Speculative)

## 7.1 Structure
```

Risks:

- operational_risk: [ ... ]
- data_risk: [ ... ]
- process_risk: [ ... ]
Mitigations:
- [ ... ]

```

Rules:
- No forecasting  
- All risks must derive from input  

---

# 8. Summarization Patterns

## 8.1 Extractive Summary
```

Return only sentences taken directly from the input.

```

## 8.2 Compressed Summary
```

Shorten the text without adding new information.

```

Checklist:
- [ ] No new facts  
- [ ] No compression beyond user’s instructions  

---

# 9. Anti-Contamination Pattern

Ensure outputs are strictly from allowed sources.

```

Use ONLY the content supplied in:

- user_input
- retrieved_context (if present)

Ignore memory, external knowledge, and training priors.

```

Checklist:
- [ ] No factual claims absent from input  
- [ ] No “world knowledge” leakage  

---

# 10. Multi-Format Output Pattern

Use when output must appear in multiple formats.

## 10.1 Structure
```

JSON:
{ ... }

Markdown:

- item
- item

```

Rules:
- Formats must be independent  
- No cross-format drift  
- JSON block must remain valid  

---

# 11. Rewrite With Preservation Pattern

## 11.1 Structure
```

Rewrite the input with:

- meaning preserved
- structure preserved
- tone changed to {{tone}}
- no added or removed facts

```

Checklist:
- [ ] Semantic fidelity  
- [ ] Matching paragraph count  

---

# 12. Quick Reference Table

| Task | Pattern | Use Case |
|------|---------|----------|
| Multi-intent detection | Intent extraction | Chatbots, assistants |
| Ambiguous input | Debounce pattern | Safety + correctness |
| Audit text | Content audit | Pre-processing |
| Validate constraints | Constraint validator | Complex structured flows |
| Compare two items | Comparison pattern | Decisions, evaluations |
| Risk analysis | Risk pattern | Operational evaluation |
| Summaries | Extractive/compressed | Documentation automation |

