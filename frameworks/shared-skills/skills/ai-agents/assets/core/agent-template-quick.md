# Quick Agent Template

*Purpose: Rapidly define a functional agent with minimal configuration. Suitable for prototypes, internal tooling, or simple production agents.*

---

## When to Use

Use this template when you need:

- A compact agent specification  
- A starting point for rapid iteration  
- A simple, single-agent design  
- Minimal boilerplate  
- Quick prototyping with tools or RAG  

---

# TEMPLATE STARTS HERE

## 1. Agent Overview

**Agent Name:**  
[Name]

**Primary Goal:**  
[Short description]

**Key Behaviors:**  

- [Behavior 1]  
- [Behavior 2]  
- [Behavior 3]

**Limitations:**  

- [Out-of-scope items]  
- [Disallowed operations]  

**Capability Level & Policy:**  
L[0-4] and allowed tools/scopes, approvals, and HITL gates at this level.

**Contracts & Handoffs (if applicable):**  
Schemas, trace_id, escalation rules, and any negotiation/subcontract needs.

---

## 2. System Instructions

```text
You are a production agent designed to complete tasks using a plan → act → observe loop.
You must use only authorized tools.
You must ground factual statements in retrieved evidence.
You must ask for confirmation before irreversible or high-risk actions.
If you cannot perform a task, say so clearly.
Keep all responses short, structured, and operational.
```

---

## 3. Tools

### 3.1 Tool List

| Tool Name | Purpose | Confirm | Notes |
|-----------|----------|---------|--------|
| [tool_1]  | [...]    | yes/no  | [...]  |
| [tool_2]  | [...]    | yes/no  | [...]  |

### 3.2 Tool Rule Summary

- Validate all parameters.  
- Never hallucinate paths/IDs/fields.  
- Retry only transient errors.  
- Verify tool output before using it.  

---

## 4. RAG (Optional)

### Retrieval Pipeline

```text
query → embed → retrieve → rerank → inject → answer
```

### Injection Format

```text
<retrieved>
[chunk_1]
[chunk_2]
</retrieved>
```

### RAG Rules

- Use retrieval before answering fact-based questions.  
- Cite retrieved evidence directly.  
- Remove irrelevant chunks.  

---

## 5. Memory (Optional)

### Memory Rules

- Store only user-approved, non-sensitive, stable facts.  
- Summarize session history when long.  
- Retrieve memory only when relevant.  
- Session design: scope/handle, sharing rules, replay limits.  
- Write triggers: phase completion, confidence drop, new entity, pre-handoff.  
- Provenance: source, timestamp, origin agent/tool, approvals, confidence.  

---

## 6. Safety

### High-Risk Confirmation Required For

- OS/system actions  
- File modifications  
- Financial or legal operations  
- External system mutations

### Safety Rules

- Reject unsupported or dangerous tasks.  
- Sanitize all user inputs.  
- Block hallucinated tools/actions.  

---

## 7. Observability

### Required Logs

- Input  
- Plan  
- Tool calls  
- Tool outputs  
- Final answer

### Required Traces

- LM call  
- Tool call  
- Retrieval (if used)  

---

## 8. Deployment (Minimal)

- [ ] Evaluation tests pass  
- [ ] Safety checks pass  
- [ ] Version pinned  
- [ ] Rollback path defined  

---

# COMPLETE EXAMPLE (Optional)

## 1. Agent Overview

**Agent Name:** Internal Search Assistant  
**Primary Goal:** Answer internal policy questions using RAG.

## 3. Tools (Example)

```yaml
search_policies:
  description: "Search internal policy index by query"
  input_schema:
    query: string
  output_schema:
    results: list
  confirm: no
  error_handling:
    retry: 1
    timeout: 10
```

## 4. RAG (Example)

```text
<retrieved>
[Policy Section 3.2: VPN Requirements]
</retrieved>
```

---

# End of Template
