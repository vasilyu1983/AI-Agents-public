# Core Operational Patterns

Production-grade prompt patterns with structures and checklists for common tasks.

## Contents
- Structured output pattern (JSON)
- Deterministic extractor pattern
- RAG workflow pattern
- Hidden chain-of-thought pattern
- Tool / agent planner pattern
- Rewrite + constrain pattern
- Decision tree pattern
- Pattern selection guide

---

## 1. Structured Output Pattern (JSON)

**Use when:** Output must be machine-parseable.

**Structure:**
```
You must respond ONLY with valid JSON.
No prose. No comments.

Schema:
{ ... }

Return data for: {{input}}
```

**Checklist:**
- [ ] "JSON-only" stated
- [ ] Schema block included
- [ ] No comments or trailing text
- [ ] All fields present
- [ ] Nulls allowed when missing
- [ ] One top-level object

---

## 2. Deterministic Extractor Pattern

**Use when:** You must extract fields exactly as defined.

**Structure:**
```
Extract ONLY the fields in the schema.

If a field is missing → null.
If multiple candidates → choose clearest or null.
No invented data.

Schema:
{ ... }

Text:
{{input}}
```

**Checklist:**
- [ ] Missing → null
- [ ] Exact schema
- [ ] No transformations unless specified
- [ ] JSON validated

---

## 3. RAG Workflow Pattern

**Use when:** Retrieved context must be used reliably.

**Structure:**
```
You will receive:

- user_query
- retrieved_context

Rules:

1. Use retrieved context ONLY if relevant.
2. Cite chunk IDs with [[chunk-n]].
3. If missing info → state explicitly.
4. Follow the output format.
```

**Checklist:**
- [ ] "Use context only when relevant"
- [ ] Missing → explicit statement
- [ ] Chunk citation format
- [ ] Output shape declared

---

## 4. Hidden Chain-of-Thought Pattern

**Use when:** The task requires reasoning, but the reasoning should NOT be revealed.

**Structure:**
```
Perform reasoning internally.
Return only the final answer in the required format.
```

**Checklist:**
- [ ] No visible reasoning
- [ ] Final answer only
- [ ] Short, deterministic sentences

---

## 5. Tool / Agent Planner Pattern

**Use when:** Claude must decide whether to use tools.

**Structure:**
```
Decide:

1. If a tool is needed → plan then call a single tool.
2. If no tool needed → answer directly.

Output:
{
 "plan": ["step1", "step2"],
 "action": { "tool": "...", "input": {...} } | null,
 "answer": "..." | null
}
```

**Checklist:**
- [ ] One tool call per turn
- [ ] Plan included
- [ ] Answer only if no tool required

---

## 6. Rewrite + Constrain Pattern

**Use when:** You must rewrite text under specific constraints.

**Structure:**
```
Rewrite according to RULES:

- Keep meaning
- Remove filler
- Short sentences
- Target audience: {{audience}}
- Format: {{format}}

Input:
{{text}}
```

**Checklist:**
- [ ] Meaning preserved
- [ ] Style rules followed
- [ ] Output format correct

---

## 7. Decision Tree Pattern

**Use when:** Classification must follow deterministic rules.

**Structure:**
```
Follow this exact decision tree:

1. If A → class = A.
2. Else if B → class = B.
3. Else → class = C.

Return:
{"class": "...", "reason": "..."}
```

**Checklist:**
- [ ] Branch order fixed
- [ ] Conditions mutually exclusive
- [ ] JSON result

---

## Pattern Selection Guide

| Pattern | Best For | Avoid When |
|---------|----------|------------|
| **Structured Output** | APIs, data extraction, integrations | Human-facing prose needed |
| **Deterministic Extractor** | Forms, invoices, exact field matching | Transformations or interpretations required |
| **RAG Workflow** | Knowledge bases, documentation search | Context not needed or always available |
| **Hidden CoT** | Classification, complex decisions | Reasoning must be visible for debugging |
| **Tool/Agent Planner** | Multi-step workflows, API calls | Single-step tasks |
| **Rewrite + Constrain** | Content adaptation, summarization | Original structure must be preserved |
| **Decision Tree** | Routing, categorization, triage | Fuzzy or overlapping categories |
