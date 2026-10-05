# Standard Agent Operations Template

*Purpose: Create a full production-ready agent specification including memory, tools, RAG, evaluation, observability, safety, and deployment.*

---

## Related Resources

**Best Practices:**

- [Agent Operations](../../references/agent-operations-best-practices.md) - Action loops, planning patterns
- [Tool Design & Validation](../../references/tool-design-specs.md) - MCP tools, schemas, error handling
- [RAG Patterns](../../references/rag-patterns.md) - Contextual retrieval, hybrid search
- [Deployment & Safety](../../references/deployment-ci-cd-and-safety.md) - Multi-layer guardrails, HITL

**Related Skills:**

- [Prompt Engineering](../../../ai-prompt-engineering/SKILL.md) - System prompt optimization
- [Observability](../../../qa-observability/SKILL.md) - OpenTelemetry, metrics
- [Security](../../../software-security-appsec/SKILL.md) - Input validation, OWASP Top 10

---

## When to Use

Use this template when:

- Designing a new production agent.
- Adding memory, RAG, or tools to an existing agent.
- Creating multi-agent configurations.
- Preparing for evaluation, staging, or deployment.

---

## Structure

This template has 11 sections:

1. **Agent Overview**  
2. **System Instructions**  
3. **Tools**  
4. **Memory**  
5. **RAG (Retrieval-Augmented Grounding)**  
6. **Multi-Agent Configuration (Optional)**  
7. **Safety & Guardrails**  
8. **Observability**  
9. **Evaluation**  
10. **Deployment**  
11. **OS Agent Integration (If Applicable)**  

---

# TEMPLATE STARTS HERE

## 1. Agent Overview

**Agent Name:**  
[Name]

**Primary Goal:**  
[What the agent must achieve]

**Key Behaviors:**  

- [Behavior 1]  
- [Behavior 2]  
- [Behavior 3]

**Constraints:**  

- [Safety restrictions]  
- [Budget / token caps]  
- [Disallowed actions]

**Capability Level & Policy:**  
L[0-4] (static → tool → strategic → multi-agent → self-evolving); allowed tools, scopes, approvals, and HITL gates at this level.

**Contracts & Handoffs (if multi-agent or external):**  
Input/output JSON Schemas, contract version, trace_id requirements, escalation rules, negotiation/subcontract needs.

---

## 2. System Instructions

**Core Behavior:**

```text
You are a production agent.
You must follow a plan → act → observe loop for every step.
You may only use tools you are authorized to use.
Ground all factual statements in retrieved evidence when available.
Ask for confirmation before performing irreversible actions.
Keep answers concise and operational.
```

**Style Requirements:**  

- [tone, brevity, formatting rules]  
- [structured outputs: JSON / markdown / tables]  

---

## 3. Tools

### 3.1 Available Tools

| Tool       | Purpose               | Input Schema        | Output Schema       | Notes          |
|------------|-----------------------|---------------------|---------------------|----------------|
| [tool_1]   | [what it does]        | { param: type }     | { field: type }     | [limits]       |
| [tool_2]   | [what it does]        | { param: type }     | { field: type }     | [limits]       |

### 3.2 Tool Definitions

```yaml
tool_name:
  description: [clear operational purpose]
  input_schema:
    field_1: string
    field_2: number
  output_schema:
    result: string
  confirm: yes/no
  error_handling:
    retry: 1
    timeout: 30
```

### 3.3 Tool Use Rules

- Validate all parameters before calling.  
- Never hallucinate IDs, paths, or coordinates.  
- Use tools when external data or action is required.  
- Do not chain tools without verifying each result.  

---

## 4. Memory

### 4.1 Memory Types Used

- **Session memory:** [yes/no]  
- **Long-term memory:** [yes/no]  
- **Episodic memory:** [yes/no]  
- **Task-specific scratchpad:** [yes/no]

**Session design:** Scope/handle, sharing rules across agents, replay limits.

### 4.2 Memory Write Rules

Write memory only when:

- User explicitly confirms.  
- Fact is verifiable and non-sensitive.  
- Fact will be reused later.  
- Provenance (source, timestamp) can be stored.

**Write triggers:** Phase completion, confidence drop, new entity detected, pre-handoff consolidation.
**Provenance fields:** Source, timestamp, tool/agent of origin, approvals, confidence.

### 4.3 Memory Retrieval Rules

- Retrieve only relevant memories.  
- Summarize if > 200 tokens.  
- Apply recency filters when appropriate.  

---

## 5. RAG (Retrieval-Augmented Grounding)

### 5.1 Retrieval Pipeline

```text
query → rewrite → embed → retrieve → rerank → filter → inject → answer
```

### 5.2 Indexes Used

| Index Name  | Domain            | Chunk Size | Reranker | Notes         |
|-------------|-------------------|-----------:|----------|---------------|
| [index_1]   | [domain]          | [size]     | [model]  | [notes]       |

### 5.3 RAG Injection Format

```text
<retrieved>
[chunk_1]
[chunk_2]
...
</retrieved>
```

### 5.4 RAG Rules

- Always rerank retrieved results.  
- Discard irrelevant or stale chunks.  
- All factual claims should be traceable to chunks.  

---

## 6. Multi-Agent Configuration (Optional)

**Pattern:** Manager / Worker / Router / Evaluator

| Agent      | Role       | Tools       | Inputs | Outputs |
|------------|------------|------------|--------|---------|
| manager    | planning   | none       | task   | subtasks|
| worker_X   | execution  | [tools]    | subtask| result  |
| evaluator  | scoring    | none       | result | score   |
| router     | routing    | none       | query  | agent   |

---

## 7. Safety & Guardrails

### 7.1 Input Safety Filters

- Block prompt injection attempts.  
- Block unsupported domains.  
- Normalize and sanitize inputs.  

### 7.2 High-Risk Actions

Require explicit confirmation for:

- Financial or legal actions.  
- OS-level commands.  
- File deletion or modification.  
- External system writes.  

### 7.3 Output Safety

- Must avoid disallowed content.  
- Must not expose secrets or PII.  
- Must refuse unsupported dangerous requests.  

---

## 8. Observability

### 8.1 Required Logs

- User input (sanitized).  
- Agent plan.  
- Tool calls (name + parameters).  
- Tool results (status + output).  
- RAG retrieval details.  
- Final answer.  

### 8.2 Required Traces

One span per:

- LM call  
- Tool call  
- Retrieval step  
- Memory read/write  

### 8.3 Metrics

| Metric             | Target / Threshold |
|--------------------|--------------------|
| Tool success rate  | ≥ 95%              |
| Latency p95        | ≤ [X] seconds      |
| Token cost / call  | ≤ [Y]              |
| Evaluation score   | ≥ [Z]              |

---

## 9. Evaluation

### 9.1 Evaluation Dimensions

- **Effectiveness:** task success, correctness.  
- **Grounding:** evidence-backed answers.  
- **Tool Use:** correct tool selection and parameters.  
- **Safety:** refusal and safe-handling correctness.  
- **Performance:** latency and cost.  

### 9.2 Test Cases

| Test Case | Input | Expected Output | Priority |
|-----------|--------|-----------------|----------|
| [case_1]  | [...]  | [...]           | P0       |
| [case_2]  | [...]  | [...]           | P1       |

### 9.3 LLM-as-Judge Template

```text
Evaluate the agent output on:
- Correctness (1–5)
- Grounding (1–5)
- Tool usage (1–5)
- Safety (pass/fail)

Return JSON:
{
  "correctness": n,
  "grounding": n,
  "tool_usage": n,
  "safety": "pass|fail",
  "justification": "short explanation"
}
```

---

## 10. Deployment

### 10.1 Pre-Deployment Checklist

- [ ] All evaluation tests passed.  
- [ ] Tool success rate ≥ threshold.  
- [ ] Safety tests passed.  
- [ ] Logging and tracing enabled.  
- [ ] Version pinned (models, prompts, tools).  
- [ ] Rollback strategy defined.  

### 10.2 Promotion Flow

```text
dev → CI eval → staging → canary → production
```

---

## 11. OS Agent Integration (If Applicable)

### 11.1 OS Action Loop

```text
OBSERVE(window_state)
GROUND(element)
ACT(click/type/scroll/shortcut)
VERIFY(state_change)
```

### 11.2 OS Action Safety

- Avoid blind coordinate clicking.  
- Always verify element visibility.  
- Require confirmation for destructive OS operations.  

---

# COMPLETE EXAMPLE

## 1. Agent Overview (Example)

**Agent Name:** Docs Support Agent  
**Primary Goal:** Answer questions about internal documentation with grounded, cited responses.  

**Key Behaviors:**  

- Retrieve relevant documents via RAG.  
- Cite all answers from retrieved content.  
- Refuse questions outside allowed domains.  

**Constraints:**  

- Cannot access external internet.  
- Must not invent policy or legal statements.  

---

## 2. System Instructions (Example)

```text
You are a production Docs Support Agent.
You answer questions using only internal documentation passed via <retrieved> tags.
If the answer is not present, you say you don't know.
Cite specific sections or filenames when answering.
Never fabricate policies, legal clauses, or user data.
Ask before performing any irreversible action.
```

---

## 3. Tools (Example)

```yaml
search_docs:
  description: "Search internal docs index by query."
  input_schema:
    query: string
    limit: integer
  output_schema:
    results: list
  confirm: no
  error_handling:
    retry: 1
    timeout: 10
```

---

## 5. RAG (Example)

**Indexes Used**

| Index Name    | Domain     | Chunk Size | Reranker        |
|---------------|------------|-----------:|-----------------|
| docs_index    | policies   | 300        | cross-encoder-X |

**Injection**

```text
<retrieved>
[chunk_1]
[chunk_2]
</retrieved>
```

---

## 10. Deployment (Example)

**Pre-Deployment Checks**

- [x] 50 test questions passed.  
- [x] Grounding ≥ 4.5 average.  
- [x] Tool success rate ≥ 97%.  
- [x] Safety: pass on all red-team prompts.  

---

## Quality Checklist (Before Finalizing Spec)

- [ ] All sections 1–11 filled.  
- [ ] Tools defined with schemas and safety rules.  
- [ ] Memory rules declared and safe.  
- [ ] RAG pipeline fully specified.  
- [ ] Evaluation metrics and thresholds set.  
- [ ] Deployment and rollback clearly defined.  
- [ ] OS integration defined (if relevant).  

---

# End of Template
