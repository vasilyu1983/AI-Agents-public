# Multi-Agent Patterns — Best Practices 

*Purpose: Provide operational patterns, role structures, coordination rules, and delegation procedures for multi-agent systems with handoff-first orchestration.*

**Modern Update**: Treat handoffs as versioned APIs with strict validation. Most agent failures are handoff/context-transfer issues, not model issues.

---

## Handoff-First Orchestration (Critical Pattern)

### Core Principle

**Most agent failures happen at handoffs, not in individual agents.**

**Old approach**: Ad-hoc context passing between agents
**New approach**: Treat every handoff as a versioned API with JSON Schema validation

### Handoff Payload Standard

```yaml
handoff_payload:
  version: "v1.2"              # Schema version for compatibility
  trace_id: "req-abc-123"      # End-to-end tracing
  timestamp: "2025-11-18T10:30:00Z"
  source_agent: "manager-001"
  target_agent: "worker-research-02"

  task:
    id: "task-456"
    type: "research"           # Enum: research|code|ops|analysis
    instruction: "Find revenue data for ACME Corp Q4 2024"
    expected_output: "Structured JSON with revenue figures and sources"
    constraints:
      max_duration_seconds: 300
      require_citations: true

  context:
    user_query: "Original user question"
    prior_findings: [...]      # Validated JSON only
    domain: "finance"

  validation:
    schema_version: "v1.2"
    required_fields: ["task.instruction", "trace_id"]
    checksum: "sha256-hash"
```

### Handoff Validation Checklist

- [ ] JSON Schema defined for handoff payload
- [ ] Schema version included (for backward compatibility)
- [ ] trace_id propagated across all agents
- [ ] Required fields validated before handoff
- [ ] Context sanitized (no untrusted data)
- [ ] Expected output format specified
- [ ] Timeout/constraints defined
- [ ] Error handling path defined
- [ ] Observability span created for handoff

### Orchestration Pattern Types 

| Pattern | Use Case | Handoff Type | Complexity |
|---------|----------|--------------|------------|
| Sequential | Linear pipeline (A→B→C) | Synchronous | Low |
| Handoff | Dynamic delegation based on context | Conditional | Medium |
| Group Chat | Collaborative multi-agent discussion | Broadcast | High |
| Magentic | Manager coordinates specialized workers | Hub-spoke | High |

### Sequential Orchestration

**Pattern**: A → B → C (linear pipeline)

**Handoff flow**:
```yaml
Agent A completes → Creates handoff payload → Validates schema →
Agent B receives → Validates payload → Executes → Creates next handoff →
Agent C receives → Validates → Completes → Returns to orchestrator
```

**When to use**: Well-defined multi-step processes (data pipeline, document review, code compilation)

**Example**: Code review pipeline
```text
Linter Agent → Security Scanner → Test Runner → Human Reviewer
```

### Dynamic Handoff Orchestration

**Pattern**: Agent decides who to hand off to based on context

**Decision logic**:
```yaml
agent_receives_task()
if complexity > threshold:
  handoff_to(specialist_agent, validated_payload)
elif domain == "research":
  handoff_to(research_agent, validated_payload)
else:
  execute_locally()
```

**When to use**: Customer support, expert routing, context-dependent delegation

**Example**: Customer support
```text
General Agent → Assesses query →
  If billing: Handoff to Billing Specialist
  If technical: Handoff to Tech Support
  If sales: Handoff to Sales Agent
```

### Group Chat Orchestration

**Pattern**: Multiple agents collaborate with optional human participation

**Handoff mechanism**:
- Group Chat Manager coordinates
- Each agent can "speak" when relevant
- Manager decides turn-taking
- Shared context maintained

**When to use**: Brainstorming, multi-perspective analysis, consensus-building

**Example**: Product feature design
```text
PM Agent + Designer Agent + Engineer Agent + User Researcher Agent →
Manager coordinates discussion → Agents contribute expertise →
Consensus emerges → Decision documented
```

### Magentic Pattern (Advanced)

**Pattern**: Manager agent coordinates specialized worker agents

**Architecture**:
```yaml
Magentic Manager:
  - Decomposes complex task into subtasks
  - Selects appropriate worker for each subtask
  - Maintains shared context
  - Tracks progress
  - Integrates results

Workers (Domain-Specific):
  - Execute assigned subtasks
  - Return structured results
  - Request clarification via handoff
  - Report progress to manager
```

**Handoff flow**:
```text
User query → Manager decomposes →
  Worker A: Subtask 1 (with validated handoff payload)
  Worker B: Subtask 2 (parallel, with validated handoff payload)
  Worker C: Subtask 3 (depends on A+B, sequential handoff)
→ Manager integrates results → Validates completeness → Returns answer
```

**When to use**: Complex open-ended tasks, research projects, multi-domain problems

---

## 1. Multi-Agent Architecture (Roles)

### Standard Agent Roles

| Role | Purpose |
|------|----------|
| Manager | Break tasks down, orchestrate flow |
| Worker | Execute steps, use tools |
| Router | Classify and route tasks to correct workers |
| Evaluator | Score outputs for quality/safety |
| Memory Agent | Handle long-term storage & retrieval |
| Reviewer | Validate final draft or output |

---

# 2. Multi-Agent Loop

### Pattern: Manager → Router → Worker → Evaluator → Manager → User

```
manager.decompose()
router.assign(subtask)
worker.execute(subtask)
evaluator.score(result)
manager.integrate(scores)
return final_answer
```

**Checklist**

- [ ] Manager produces atomic tasks.  
- [ ] Router selects correct worker.  
- [ ] Worker produces grounded result.  
- [ ] Evaluator checks correctness/safety.  
- [ ] Manager integrates validated results.  

---

# 3. Manager Pattern

### Purpose: Task decomposition + orchestration

```
manager:
  input: user_query
  output: subtasks[]
```

**Checklist**

- [ ] Subtasks independent.  
- [ ] Each subtask defines expected output.  
- [ ] Order defined when sequential.  
- [ ] Avoid redundant subtasks.  

**Anti-Patterns**

- AVOID: Manager doing worker tasks.  
- AVOID: Producing vague subtasks.  
- AVOID: Producing too many micro-subtasks.  

---

# 4. Router Pattern

### Pattern: Domain Routing

```
router.classify(query)
→ domain
→ select worker(domain)
```

**Routing Table**

| Domain | Worker |
|--------|---------|
| Code | worker_code |
| Research | worker_research |
| Operations | worker_ops |
| RAG/Search | worker_retrieval |
| UI / OS | worker_os |

**Checklist**

- [ ] Classification based on intent.  
- [ ] Confidence threshold enforced.  
- [ ] Ask for clarification if ambiguous.  

---

# 5. Worker Pattern

### Purpose: Execute a well-defined subtask

```
worker:
  read_subtask()
  plan()
  execute_action()
  produce_output()
```

**Checklist**

- [ ] Worker uses tools when required.  
- [ ] Output structured and validated.  
- [ ] No speculation beyond evidence.  

**Anti-Patterns**

- AVOID: Worker modifying task definitions.  
- AVOID: Worker delegating further.  
- AVOID: Worker performing manager duties.  

---

# 6. Evaluator Pattern

### Pattern: Automatic Judging

```
evaluate:
  correctness
  grounding
  safety
  completeness
```

**Checklist**

- [ ] Use deterministic scoring rubric.  
- [ ] Score each worker output separately.  
- [ ] Provide structured JSON scores.  

**Decision Tree**

```
Is result unsafe?
→ Reject
Is score < threshold?
→ Request worker redo
Else:
→ Return approved result
```

---

# 7. Coordinator Pattern

### Pattern: Merge & Integrate

```
collect(worker_outputs)
validate_outputs()
merge_into_single_answer()
```

**Checklist**

- [ ] Deduplicate overlapping content.  
- [ ] Resolve contradictions using evaluator scores.  
- [ ] Ensure final answer grounded.  

---

# 8. Communication Rules

### Allowed Messages

- Subtask allocations  
- Clarification questions  
- Output summaries  
- Structured results  
- Evaluator scores  

### Not Allowed

- Internal reasoning  
- Irrelevant conversation  
- Free-form speculation  

### Pattern: Message Templates

```
task:
  id: ...
  description: ...
  expected_output: ...
```

```
result:
  id: ...
  output: ...
  evidence: [...]
  confidence: ...
```

---

# 9. Delegation Pattern

### Pattern: Controlled Delegation

```
manager → worker
worker → evaluator
evaluator → manager
```

**Checklist**

- [ ] Only manager delegates.  
- [ ] Workers do NOT spawn subtasks.  
- [ ] Evaluators only review, never execute.  

---

# 10. Multi-Agent RAG Pattern

### Pattern: Retrieval Worker + Integration Manager

**Flow**

```
manager identifies retrieval need
router → worker_retrieval
worker_retrieval → retrieve + rerank + summarize
evaluator → score relevance
manager → integrate into context
workers → continue tasks
```

**Checklist**

- [ ] Retrieval worker uses standard RAG patterns.  
- [ ] Summaries ≤ 150 tokens.  
- [ ] Evidence always cited.  

---

# 11. Multi-Agent Memory Pattern

### Pattern: Dedicated Memory Agent

```
memory_agent:
  read_write_memory()
  provide_relevant_entries()
```

**Checklist**

- [ ] Other agents never manipulate memory directly.  
- [ ] Memory agent enforces write rules (non-sensitive, verified).  

---

# 12. Multi-Agent Error Handling

### Pattern: Escalation

```
worker detects failure → evaluator checks → manager replans
```

**Checklist**

- [ ] Workers provide detailed error context.  
- [ ] Evaluators categorize (transient vs fatal).  
- [ ] Manager revises task list or requests clarification.  

**Anti-Patterns**

- AVOID: Allowing workers to silently fail.  
- AVOID: Continuing after inconsistent outputs.  

---

# 13. Multi-Agent Safety Gates

### Safety Checks

- Worker output must pass evaluator safety scan.  
- High-risk actions require explicit manager approval.  
- Disallowed domain → escalation to manager.  

### Pattern: Safety Override

```
if unsafe(step):
    halt
    return safe_alternative
```

---

# 14. Multi-Agent Anti-Patterns (Master List)

- AVOID: Manager performing work.  
- AVOID: Workers delegating tasks.  
- AVOID: Router routing without confidence threshold.  
- AVOID: Evaluator modifying outputs.  
- AVOID: Infinite loops between agents.  
- AVOID: Overlapping worker responsibilities.  
- AVOID: Storing partial outputs as memory.  
- AVOID: Using free-form discussion between agents.  

---

# 15. Quick Reference Tables

### Role Responsibility Table

| Role | Allowed | Not Allowed |
|------|---------|-------------|
| Manager | planning, orchestration | execution |
| Worker | execution, tool use | planning |
| Router | domain classification | execution |
| Evaluator | scoring, safety | modification |
| Memory Agent | storage/retrieval | reasoning |

### Interaction Table

| Step | Agent |
|------|--------|
| Decompose | Manager |
| Route | Router |
| Execute | Worker |
| Score | Evaluator |
| Integrate | Manager |

---

# 16. Copy-Paste Multi-Agent Templates

### Subtask Template

```
subtask:
  id: "task-001"
  description: "Extract financial metrics from retrieved document."
  expected_output:
    - metric_name
    - value
    - evidence_source
```

### Evaluation Template

```
evaluation:
  task_id: "task-001"
  correctness: 1-5
  grounding: 1-5
  safety: "pass|fail"
  notes: "..."
```

### Worker Output Template

```
worker_output:
  id: "task-001"
  output: {...}
  evidence: [...]
  confidence: 0-1
```

---

# End of File
