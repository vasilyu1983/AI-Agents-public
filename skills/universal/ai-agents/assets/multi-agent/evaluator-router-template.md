# Evaluator + Router Multi-Agent Template

*Purpose: Define production-grade Evaluator and Router agents used in multi-agent systems for domain routing, scoring, quality control, grounding, and safety enforcement with validated handoffs.*

**Modern Update**: All handoffs between agents must use validated JSON Schema payloads with trace_id propagation.

---

## When to Use

Use this template when:

- You need deterministic **domain routing** across multiple worker agents
- You need an **Evaluator** to score worker outputs
- You must enforce **quality, grounding, and safety** before integration
- Multiple workers require **domain specialization**
- You want a modular routing layer for future expansion
- You need **versioned handoff contracts** for reliability  

---

# TEMPLATE STARTS HERE

# 1. Multi-Agent Overview

**System Name:**  
[Name]

**Roles Included:**  

- **Router Agent** — selects appropriate worker agent  
- **Evaluator Agent** — scores worker outputs  
- Optional: Manager + Workers (covered in other template)

---

# 2. Router Agent Template

## 2.1 Router Role

The Router classifies the user query or subtask, assigns it to the correct Worker, and returns the routing decision to the Manager.

Router **does not**:

- Execute tasks  
- Use tools  
- Modify subtasks  
- Perform planning  

Router **only**:

- Classifies  
- Routes  
- Validates domain  
- Rejects ambiguous mappings  

---

## 2.2 Router System Instructions

```text
You are the Router agent.
Your job is to:
1. Analyze each subtask or query.
2. Classify it into the correct domain.
3. Select the appropriate worker.
4. Request clarification when classification is uncertain.
5. Never execute tasks or call tools.

Output ONLY routing decisions in structured format.
```

---

## 2.3 Routing Table

```yaml
routing_table:
  code:
    keywords: ["function", "compile", "stack trace", "error", "API"]
    worker: worker_code
  research:
    keywords: ["summarize", "explain", "compare", "analyze"]
    worker: worker_research
  operations:
    keywords: ["create ticket", "schedule", "inventory", "order"]
    worker: worker_ops
  rag:
    keywords: ["retrieve", "find", "search", "documents"]
    worker: worker_rag
```

---

## 2.4 Routing Logic Template (Modern Handoff Pattern)

**Validated handoff payload**:

```yaml
handoff_to_worker:
  # Handoff metadata (modern standard)
  version: "v1.2"
  trace_id: "req-abc-123"  # Propagated from original request
  timestamp: "2025-11-18T10:30:00Z"
  source_agent: "router-001"
  target_agent: "[assigned_worker]"

  # Routing decision
  domain: "[classified_domain]"
  worker: "[assigned_worker]"
  confidence: [0.0-1.0]

  # Task definition
  task:
    id: "task-456"
    type: "[domain]"
    instruction: "[original user query or subtask]"
    expected_output: "Structured result with citations"
    constraints:
      max_duration_seconds: 300
      require_citations: true

  # Context
  context:
    user_query: "Original user question"
    prior_findings: []
    domain_specific_data: {}

  # Validation
  validation:
    schema_version: "v1.2"
    required_fields: ["task.instruction", "trace_id", "worker"]
    checksum: "sha256-hash"
```

**Validation checklist before handoff**:
- [ ] JSON Schema validation passed
- [ ] trace_id propagated
- [ ] All required fields present
- [ ] Confidence ≥ threshold (0.65)
- [ ] Worker exists in routing table
- [ ] Task constraints defined

---

## 2.5 Routing Decision Rules

- Minimum confidence threshold: **≥ 0.65**  
- If below threshold → ask user for clarification  
- If multiple domains match → request clarification  
- If domain unknown → fallback to general worker or manager  

---

# 3. Evaluator Agent Template

## 3.1 Evaluator Role

Evaluator **scores Worker outputs** along multiple dimensions:

- Correctness  
- Grounding  
- Completeness  
- Structure  
- Safety  

Evaluator **does NOT**:

- Modify outputs  
- Execute tasks  
- Perform planning  
- Generate new content  

---

## 3.2 Evaluator System Instructions

```text
You are the Evaluator agent.
Your job is to:
1. Score worker outputs for correctness, grounding, structure, and safety.
2. Reject unsafe or incorrect outputs.
3. Request worker redo when scores fall below threshold.
4. Output structured scores only.
```

---

## 3.3 Evaluation Scoring Template

```yaml
evaluation:
  task_id: "task-001"
  correctness: 1-5
  grounding: 1-5
  completeness: 1-5
  structure: 1-5
  safety: "pass" | "fail"
  notes: "short explanation only"
```

---

## 3.4 Evaluation Thresholds

| Metric | Minimum Passing |
|--------|------------------|
| Correctness | ≥ 4 |
| Grounding | ≥ 4 |
| Completeness | ≥ 4 |
| Structure | ≥ 3 |
| Safety | pass |

If any score < threshold → worker redo required.

---

## 3.5 Evaluation Rules

- Evidence must align 1:1 with worker output  
- Citations must match retrieved text  
- No hallucinations allowed  
- No contradictions  
- No safety red flags  
- No unsupported claims  
- All required fields must be present  

---

## 3.6 Safety Scan Pattern

```
scan_for:
  - hallucinated actions/tools
  - unsupported domain instructions
  - sensitive or private data
  - high-risk unconfirmed actions
```

If detected → `safety: fail`.

---

# 4. End-to-End Router + Evaluator Flow

```
Manager → Router → Worker → Evaluator → Manager
```

**Steps**  

1. Manager creates subtask  
2. Router classifies → selects worker  
3. Worker executes subtask  
4. Evaluator scores output  
5. Manager integrates or requests redo  

---

# 5. Validation Checklists

## Router Validation Checklist

- [ ] Domain classification correct  
- [ ] Worker selected from routing table  
- [ ] Confidence ≥ threshold  
- [ ] No ambiguous domains  
- [ ] Request clarification on domain conflict  

## Evaluator Validation Checklist

- [ ] All score fields present  
- [ ] Safety scanned  
- [ ] Grounding validated  
- [ ] Output structure correct  
- [ ] Score thresholds enforced  

---

# 6. Anti-Patterns

### Router Anti-Patterns

- AVOID: Routing without confidence threshold  
- AVOID: Assigning to multiple workers  
- AVOID: Hallucinating unknown domains  
- AVOID: Acting like a Worker  

### Evaluator Anti-Patterns

- AVOID: Changing Worker outputs  
- AVOID: Executing tasks  
- AVOID: Ignoring missing fields  
- AVOID: Accepting unsafe outputs  
- AVOID: Soft-failing without rejecting  

---

# 7. Complete Example (Optional)

## Router Output Example

```yaml
router_output:
  domain: "code"
  worker: "worker_code"
  confidence: 0.82
```

## Evaluator Output Example

```yaml
evaluation:
  task_id: "t003"
  correctness: 5
  grounding: 4
  completeness: 4
  structure: 4
  safety: "pass"
  notes: "Output correctly grounded in provided logs."
```

---

# End of Template
