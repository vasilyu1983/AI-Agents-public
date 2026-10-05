# Core Operational Patterns

## Table of Contents

- [Contents](#contents)
- [1. Structured Output Pattern (JSON)](#1-structured-output-pattern-json)
  - [Schema Design for LLM Output](#schema-design-for-llm-output)
- [2. Deterministic Extractor Pattern](#2-deterministic-extractor-pattern)
- [3. RAG Workflow Pattern](#3-rag-workflow-pattern)
- [4. Private Reasoning Pattern](#4-private-reasoning-pattern)
- [5. Tool / Agent Planner Pattern](#5-tool--agent-planner-pattern)
- [6. Rewrite + Constrain Pattern](#6-rewrite--constrain-pattern)
- [7. Decision Tree Pattern](#7-decision-tree-pattern)
- [Pattern Selection Guide](#pattern-selection-guide)

Production-grade prompt patterns with structures and checklists for common tasks.

## Contents
- Structured output pattern (JSON)
- Deterministic extractor pattern
- RAG workflow pattern
- Private reasoning pattern
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
- [ ] Rationale/evidence fields come before answer and score fields (or native thinking is on and only the answer is constrained)
- [ ] Enums are closed and include `unknown` or `other`
- [ ] Code validator runs on every parsed object; one repair retry, then a degraded path

### Schema Design for LLM Output

This is the structured-output contract. Integration skills bind the schema through their SDK and point here for the design rules.

1. **Field order matters.** Generation runs left to right, so a field can only use reasoning that was generated before it. When the task needs reasoning, put a short `rationale` or `evidence` field before the answer and score fields, or turn on native thinking and constrain only the final answer. A verdict-first schema makes the justification a post-hoc rationalization. This is how to use a strict schema on a reasoning task without the accuracy loss described in [production-guidelines.md](production-guidelines.md#structured-output-considerations-research-based).
2. **Never force a guess.** Use closed enums with an explicit `unknown` or `other` value, and nullable fields instead of required ones when the input may not contain the value.
3. **Use a discriminated union for different kinds of result.** When the output can be an answer, a clarification request or a refusal, key a union on a `type` field. Code branches on `type`, and anything that matches no known type is rejected.
4. **Keep the wire schema simple.** Native strict modes accept only a subset of JSON Schema; look up the supported keywords for the provider and put richer constraints (ranges, cross-field rules, formats) in the code validator.
5. **Strict schema mode vs tool calling.** Use schema-constrained output when there is no decision to make and the final answer must match a shape ("extract these fields"). Use tool calling when the model must decide whether and which action to take, and the schema is that action's arguments. They are not interchangeable. Prefer either over unconstrained JSON mode or regex on prose.
6. **Constrained decoding guarantees syntax, not semantics.** Where supported it removes parse errors; it does not make the values correct. Validate every parsed object in code. On failure, retry at most once and feed back the validator's error text naming the failing field. If the retry fails, route to a degraded path (flagged partial result, human review, or an explicit error), never a silent empty object. Log the raw output and track the schema-failure rate per endpoint.
7. **Version output schemas like public API contracts.** A field rename breaks every consumer and every stored record.

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

## 4. Private Reasoning Pattern

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
| **Private reasoning** | Classification, complex decisions | The user explicitly needs visible steps or teaching output |
| **Tool/Agent Planner** | Multi-step workflows, API calls | Single-step tasks |
| **Rewrite + Constrain** | Content adaptation, summarization | Original structure must be preserved |
| **Decision Tree** | Routing, categorization, triage | Fuzzy or overlapping categories |
