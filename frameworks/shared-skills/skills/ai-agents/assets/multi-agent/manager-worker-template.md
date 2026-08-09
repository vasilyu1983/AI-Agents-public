# Manager–Worker Multi-Agent Template

*Purpose: Provide a production-grade template for building a multi-agent system where a Manager agent delegates tasks to Worker agents and integrates their outputs.*

---

## Related Resources

**Best Practices:**

- [Multi-Agent Patterns](../../references/multi-agent-patterns.md) - Orchestration patterns and coordination
- [A2A Handoff Patterns](../../references/a2a-handoff-patterns.md) - Agent-to-agent communication protocol
- [Evaluation & Observability](../../references/evaluation-and-observability.md) - Multi-agent tracing and metrics

**Protocol Guides:**

- [Protocol Decision Tree](../../references/protocol-decision-tree.md) - MCP vs A2A selection
- [MCP Practical Guide](../../references/mcp-practical-guide.md) - Tool integration for workers

**Related Skills:**

- [LLM Engineering](../../../ai-llm/SKILL.md) - Model selection per agent role
- [Observability](../../../qa-observability/SKILL.md) - Distributed tracing across agents

---

## When to Use

Use this template when:

- Tasks must be decomposed into atomic subtasks
- Workers require specialized tools or domain expertise
- The system needs separation of planning vs execution
- Output must be validated, scored, and integrated
- Multi-agent orchestration is required

---

# TEMPLATE STARTS HERE

# 1. Multi-Agent Overview

**System Name:**  
[Name]

**Architecture:**  
Manager → Worker(s) → Evaluator (optional) → Manager → Final output

**Goals:**  

- Decompose complex tasks  
- Route to correct worker  
- Execute subtasks deterministically  
- Validate and integrate results  

**Agents Involved:**  

- Manager  
- Worker(s): [worker_1, worker_2, …]  
- Evaluator (optional)  

---

# 2. Manager Agent Specification

## 2.1 Role

The Manager **plans, decomposes, orchestrates**, and **integrates**.  
It **never executes tasks** or calls tools.

## 2.2 System Instructions

```text
You are the Manager agent.
Your job is to:
1. Understand the user query.
2. Decompose it into atomic subtasks.
3. Assign each subtask to the correct Worker.
4. Validate Worker outputs.
5. Integrate results into a final answer.
6. Replan when Worker outputs contradict expectations.

Do NOT execute tasks or call tools.
You only plan, delegate, validate, and integrate.
```

## 2.3 Subtask Format

```yaml
subtask:
  id: "task-001"
  description: "[what must be done]"
  expected_output: "[format or fields]"
  worker: "[assigned_worker]"
```

## 2.4 Manager Delegation Rules

- Decompose into **logical, minimal** steps  
- Assign each step to **one worker only**  
- Include **expected output schema**  
- Revise plan if Worker output is invalid  

---

# 3. Worker Agent Specification

## 3.1 Role

Workers **execute** subtasks, using tools, RAG, OS actions, or domain logic.  
Workers do **not** break down tasks or create new tasks.

## 3.2 System Instructions

```text
You are a Worker agent.
Your job is to execute exactly the subtask assigned to you.

You MUST:
- Use tools appropriately.
- Perform retrieval if required.
- Output structured results.
- Stay within the subtask scope.

You MUST NOT:
- Modify or create subtasks.
- Delegate work.
- Perform Manager duties.
```

## 3.3 Output Format

```yaml
worker_output:
  id: "task-001"
  output: {...}
  evidence: [...]
  confidence: 0.0-1.0
```

## 3.4 Worker Execution Pattern

```
plan_step()
if retrieval needed: run RAG
if tools needed: validate → execute → verify
format output
return to Manager
```

---

# 4. Optional: Evaluator Agent Specification

## 4.1 Role

Evaluator scores Worker outputs for:

- Correctness  
- Grounding  
- Safety  
- Structure  

## 4.2 Scoring Template

```yaml
evaluation:
  task_id: "task-001"
  correctness: 1-5
  grounding: 1-5
  safety: "pass|fail"
  notes: "..."
```

## 4.3 Evaluator Rules

- Reject unsafe or incorrect outputs  
- Request Worker redo if score < threshold  

---

# 5. End-to-End Flow

```
User Request
→ Manager decomposes
→ Router (optional) routes subtasks
→ Workers execute
→ Evaluator scores (optional)
→ Manager integrates
→ Final Answer
```

---

# 6. Integration Logic (Manager)

## 6.1 Manager Integration Pattern

```
collect(worker_outputs)
validate_all()
resolve_conflicts()
merge_into_final_answer()
```

## 6.2 Conflict Resolution Rules

- Prefer higher evaluator score  
- Prefer more recent or direct evidence  
- Discard outputs that contradict retrieved evidence  

## 6.3 Final Output Format

```yaml
final_answer:
  summary: "..."
  combined_results: [...]
  evidence: [...]
```

---

# 7. Safety Rules for Multi-Agent Systems

- Manager must confirm high-risk actions  
- Workers must not bypass confirmation logic  
- Evaluator must run safety scan when enabled  
- No Worker can act outside its assigned scope  
- No agent stores sensitive data  

---

# 8. Multi-Agent Validation Checklist

## Manager

- [ ] Subtasks atomic  
- [ ] Correct worker chosen  
- [ ] Expected output defined  

## Workers

- [ ] Tools validated pre-call  
- [ ] Evidence included  
- [ ] Output structured  

## Evaluator (optional)

- [ ] Scored each output  
- [ ] Flagged unsafe items  
- [ ] Requested redo where needed  

## System

- [ ] Conflicts resolved  
- [ ] Final output grounded  
- [ ] No hallucinated subtasks/workers  

---

# COMPLETE EXAMPLE (Optional)

## Example Decomposition (Manager)

```yaml
subtask_1:
  id: "t001"
  description: "Retrieve uptime metrics for service X."
  expected_output: "JSON with metrics + timestamps"
  worker: "worker_metrics"

subtask_2:
  id: "t002"
  description: "Summarize and highlight anomalies."
  expected_output: "Markdown summary + anomalies list"
  worker: "worker_analysis"
```

## Example Worker Output

```yaml
worker_output:
  id: "t001"
  output:
    uptime_percent: 99.2
    outages: ["2024-01-03 03:21 UTC"]
  evidence:
    - "logs/service_x.log: lines 42–55"
  confidence: 0.94
```

## Example Final Answer

```yaml
final_answer:
  summary: "Service X shows strong uptime with one minor outage."
  combined_results:
    - uptime: 99.2
    - outage_events: ["2024-01-03"]
  evidence:
    - "logs/service_x.log"
```

---

# End of Template
