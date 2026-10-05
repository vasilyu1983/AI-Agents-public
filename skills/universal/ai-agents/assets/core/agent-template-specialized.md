# Specialized Agent Template

*Purpose: Provide a structured template for designing **specialized** agents with domain-specific rules, advanced RAG, complex tool use, multi-agent roles, OS automation, or high-risk operational constraints.*

---

## When to Use

Use this template when:

- The agent performs **complex retrieval**, **multiple tools**, or **multi-step reasoning**.  
- The agent operates in **regulated**, **sensitive**, or **high-risk** domains.  
- The agent integrates with **OS**, **browser**, or **external systems**.  
- The agent is part of a **multi-agent orchestration**.  
- The agent requires **strict safety**, **advanced evaluation**, or **custom workflows**.

---

## Structure

This template contains 14 specialized sections:

1. **Specialization Summary**  
2. **System Instructions (Specialized Form)**  
3. **Operational Scope & Boundaries**  
4. **Domain Rules & Constraints**  
5. **Advanced Tools & Execution Rules**  
6. **Advanced RAG (Domain-Aware)**  
7. **Memory Strategy (Domain-Specific)**  
8. **Multi-Agent Role Definition (If Used)**  
9. **Planning Framework (Custom)**  
10. **Safety Enforcement Layer**  
11. **Validation Layer**  
12. **Observability (Deep Mode)**  
13. **Evaluation Framework (Domain-Specific)**  
14. **Deployment Requirements**  

---

# TEMPLATE STARTS HERE

## 1. Specialization Summary

**Agent Name:**  
[Name]

**Domain:**  
[e.g., legal QA, financial modeling, clinical data extraction, OS automation]

**Primary Functions:**  

- [Function 1]  
- [Function 2]  
- [Function 3]

**Special Notes:**  

- [High-risk constraints, compliance rules, tool limitations, etc.]

**Capability Level & Policy:**  
L[0-4]; allowed scopes/tools, approvals, HITL gates, and audit requirements for this level.

**Contracts & Handoffs (if multi-agent/external):**  
Input/output Schemas, contract version, trace_id requirements, escalation rules, negotiation/subcontract handling.

---

## 2. System Instructions (Specialized)

```text
You are a specialized agent operating in the [domain] domain.
You must perform all tasks using a strict plan → act → observe → update loop.

You MUST:
- Use only approved tools.
- Ground all facts in retrieved evidence.
- Adhere to domain-specific rules and constraints.
- Ask for confirmation before high-risk actions.
- Produce structured outputs as required.

You MUST NOT:
- Invent facts, policies, legal interpretations, numbers, or system paths.
- Perform disallowed or irreversible actions without explicit confirmation.
- Use tools not listed in the Tools section.
```

**Output Format Requirements:**  

- JSON  
- Markdown tables  
- Action blocks  
- RAG evidence sections  

---

## 3. Operational Scope & Boundaries

**Allowed Tasks:**  

- [Explicit task types]

**Out-of-Scope Tasks:**  

- [Must decline or redirect]

**Authority Level:**  

- [read-only? modify? execute?]

**Escalation Rules:**  

- [When to ask for confirmation or clarification]  
- [When to escalate to human/manager agent]  

---

## 4. Domain Rules & Constraints

**Domain Standards:**  

- [e.g., legal citations, medical terminology, finance accuracy]

**Regulatory Requirements:**  

- [HIPAA / GDPR / SOC2 / internal policies]

**Accuracy Requirements:**  

- [Zero hallucination allowed?]  
- [Evidence-backed answers required?]

**Forbidden Behaviors:**  

- [Domain-specific limitations]

---

## 5. Advanced Tools & Execution Rules

### 5.1 Tool List (Specialized)

| Tool       | Purpose               | Confirm | Risks | Notes |
|------------|------------------------|---------|--------|-------|
| [tool_1]   | [...]                  | yes/no  | [list] | [...] |
| [tool_2]   | [...]                  | yes/no  | [list] | [...] |

### 5.2 Tool Definition (Example)

```yaml
tool_name:
  description: [operational purpose]
  input_schema:
    param_a: string
    param_b: integer
  output_schema:
    result: object
  confirm: [yes/no]
  error_handling:
    retry: 1
    timeout: 20
```

### 5.3 Tool Execution Rules

- Validate all parameters.  
- Reject hallucinated IDs / paths / fields.  
- Use high-risk confirmation logic.  
- Retry only transient errors (e.g., timeouts).  
- Verify output fields before plan continues.  

---

## 6. Advanced RAG (Domain-Aware)

### 6.1 RAG Pipeline

```text
query → rewrite → embed → retrieve → rerank → filter → enrich → inject → answer
```

### 6.2 Index Specifications

| Index | Domain | Chunk Size | Reranker | Notes |
|-------|--------|-----------:|----------|-------|
| [...] | [...]  | [...]      | [...]    | [...] |

### 6.3 Evidence Injection

```text
<retrieved>
[chunk_1]
[chunk_2]
</retrieved>
```

### 6.4 Domain Filters

- Enforce domain matching.  
- Remove irrelevant or conflicting chunks.  
- Require citations for all factual claims.  

---

## 7. Memory Strategy (Domain-Specific)

**Memory Types Enabled:**  

- Session memory  
- Long-term preferences  
- Episodic events  
- Domain knowledge only when safe  

### Write Rules

Write memory only if:

- User explicitly confirms  
- Information is non-sensitive  
- Information is verifiable  
- Information is stable over time  

**Write triggers:** Phase completion, confidence drop, new entities, pre-handoff consolidation.  
**Provenance:** Source, timestamp, originating agent/tool, approvals, confidence.  
**Session design:** Scope/handle, sharing across agents, replay limits.

### Retrieval Rules

- Retrieve only relevant entries  
- Summaries required >150 tokens  
- Apply domain filters  

---

## 8. Multi-Agent Role Definition (Optional)

### Example Roles

**Manager:** Decompose tasks.  
**Worker-Research:** Perform RAG + summaries.  
**Worker-Execution:** Execute tool operations.  
**Evaluator:** Score correctness / grounding / safety.  
**Router:** Domain routing.  

### Optional Multi-Agent Structure

```yaml
roles:
  manager:
    responsibilities: [planning, coordination]
  worker_research:
    responsibilities: [retrieval, summarization]
  worker_execution:
    responsibilities: [tool-use, OS actions]
  evaluator:
    responsibilities: [scoring, verification]
```

---

## 9. Planning Framework (Custom)

### Planning Pattern (Specialized)

```
1. analyze(query)
2. retrieve / collect needed context
3. produce plan (atomic steps)
4. execute each step:
      observe → ground → act → verify
5. consolidate results
6. produce final output
```

### Plan Requirements

- Each step explicit  
- Each step lists expected outputs  
- No speculative steps  
- Revise plan after each observation  

---

## 10. Safety Enforcement Layer

### Safety Checks

- Domain restrictions  
- High-risk action detection  
- Data sensitivity detection  
- Tool misuse prevention  
- OS-action constraints  

### Safety Gates

```
check_domain()
check_action_risk()
check_tool_scope()
sanitize_inputs()
```

### Confirmation Prompts

Include exact parameters:

```
You requested a high-risk operation:
Action: [...]
Parameters: [...]
Please confirm "yes" to proceed.
```

---

## 11. Validation Layer

### Validation Pattern

```
validate_input()
validate_tool_params()
validate_rag_chunks()
validate_memory()
validate_output()
```

### Required Validations

- Type checking  
- Range checking  
- Domain consistency  
- Evidence alignment  

---

## 12. Observability (Deep Mode)

### Required Logs

- Input  
- Plan  
- Tool calls  
- Tool results  
- RAG retrieval  
- Memory reads/writes  
- Evaluator scores  
- Final answer  

### Required Traces

- LM spans  
- Tool spans  
- Retrieval spans  
- Memory spans  
- Safety spans  

### Metrics

| Metric | Threshold |
|--------|-----------|
| Tool Success Rate | ≥ 95% |
| Grounding Score | ≥ 4.0 |
| Accuracy | ≥ 4.0 |
| Safety | 100% pass |
| Latency p95 | ≤ [X] |

---

## 13. Evaluation Framework (Domain-Specific)

### Evaluation Categories

- Correctness  
- Grounding  
- Domain compliance  
- Safety performance  
- Tool execution accuracy  
- OS action accuracy (if used)  

### LLM-as-Judge Template

```json
{
  "correctness": 1-5,
  "grounding": 1-5,
  "domain_accuracy": 1-5,
  "tool_usage": 1-5,
  "safety": "pass|fail",
  "notes": "..."
}
```

---

## 14. Deployment Requirements

### Pre-Deployment Checklist

- [ ] All evaluation tests passed  
- [ ] RAG pipeline validated  
- [ ] Tool-call tests validated  
- [ ] Safety tests passed  
- [ ] Version pinned  
- [ ] Canary rollout configured  
- [ ] Rollback plan ready  

### Deployment Flow

```
dev → CI → staging → canary (1%) → expand (25%) → full production
```

---

# COMPLETE EXAMPLE (Optional)

## 1. Specialization Summary

**Agent Name:** Medical Safety Summarizer  
**Domain:** Clinical documentation (read-only)  
**Primary Functions:**  

- Extract key information  
- Detect unsafe statements  
- Summarize with evidence  
**Constraints:**  
- No diagnosis generation  
- Must cite sections  

## 6. Advanced RAG (Example)

**Injection Format**

```text
<retrieved>
[Section 2.3: Symptoms]
[Section 4.0: Contraindications]
</retrieved>
```

---

# End of Template
