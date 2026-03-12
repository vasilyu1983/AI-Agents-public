# Agentic Patterns Best Practices

*Purpose: Ready-to-apply design patterns and validation checklists for building, orchestrating, and safely operating agentic AI systems (LLM-based agents, multi-agent workflows, and tool-using LLMs).*

---

## Core Patterns

---

### Pattern 1: Agent Workflow Loop

**Use when:** Designing any LLM-powered agent (single or multi-tool), especially those that must interact with APIs, databases, users, or other agents.

**Structure:**

```
1. Receive mission/task input (user or upstream agent)
2. Perceive (gather info, context, or state)
3. Plan (select tools/steps, break into subtasks)
4. Act (call tools/APIs, make changes, send messages)
5. Observe results (validate, update memory/context)
6. Loop: Replan or finish if task completed/failed
7. Escalate or fallback if goal unreachable or error encountered
```

**Checklist:**

- [ ] Mission/goal always explicit and parsed
- [ ] Perception step: can access latest context/state
- [ ] Plan step decomposes nontrivial tasks, logs plan
- [ ] Action step: every tool/API call logged, has error handling
- [ ] Observations update agent memory/context
- [ ] Loop capped (step limit, time limit, watchdog)
- [ ] Escalation or fallback for dead ends/errors

---

### Pattern 2: Tool Use & Reflection

**Use when:** Your agent needs to interact with external APIs, retrieve data, or perform multi-step reasoning.

**Structure:**

```
1. Recognize when tool/API is needed (tool call trigger)
2. Format inputs (normalize, check for required params)
3. Call tool/API, handle possible errors/timeouts
4. Reflect on results: was the output usable? (if not, replan or escalate)
5. Update memory/log of tool usage for auditability
```

**Checklist:**

- [ ] Tools/API schemas versioned and validated
- [ ] Inputs validated before each call
- [ ] Outputs parsed/validated before use
- [ ] Tool call failures handled (retry, fallback, escalate)
- [ ] Reflection step checks if tool solved subgoal

---

### Pattern 3: Multi-Agent Collaboration

**Use when:** Building systems where multiple agents specialize, collaborate, or compete to solve complex tasks.

**Structure:**

```
1. Assign roles/capabilities to each agent
2. Define hand-off rules (when/how to delegate)
3. Establish communication protocol (messages, APIs, shared memory)
4. Synchronize state as needed (avoid race conditions)
5. Arbitration: resolve conflicting actions or deadlocks
6. Monitor, audit, and escalate when cooperation fails
```

**Checklist:**

- [ ] Roles and responsibilities of each agent defined
- [ ] Hand-off protocols tested for all task boundaries
- [ ] All agent-agent comms logged and auditable
- [ ] Deadlock/loop detection in place
- [ ] Arbitration logic for conflicting outcomes
- [ ] Multi-agent eval test suite (edge, error, and abuse cases)

---

## Decision Matrices

### Agent Type Selection Table

| Need/Scenario                    | Agent Pattern        | Checklist           |
|----------------------------------|---------------------|---------------------|
| Single-step, low risk            | Stateless tool-call  | Pattern 2           |
| Multi-step, open-ended goal      | Workflow loop       | Pattern 1           |
| Cross-domain, multi-tool/task    | Multi-agent collab  | Pattern 3           |
| Untrusted input, risk of abuse   | Guardrail agent     | Add safety checks   |

---

### Step Limit and Escalation Matrix

| Situation         | Limit Type         | Fallback/Escalation             |
|-------------------|-------------------|---------------------------------|
| Infinite loop     | Max steps/timeout | Escalate to human/log event     |
| Tool abuse/failure| Max retries/tool  | Switch tool, escalate, block    |
| Unsolved mission  | Max replans       | Output best effort + escalate   |

---

## Common Mistakes & Anti-Patterns

---

[FAIL] **No step/loop cap:** Agent runs indefinitely, racks up costs, or gets stuck.  
[OK] **Instead:** Always enforce max step/timeout per agent/task; log and abort if limit hit.

[FAIL] **No tool validation:** Assumes API/tool will always return correct/expected data.  
[OK] **Instead:** Always parse and validate tool output before use; retry or escalate on error.

[FAIL] **Agent hand-off chaos:** No clear protocol for when/how agents delegate, causing confusion, missed hand-offs, or data races.  
[OK] **Instead:** Define hand-off conditions and message schemas; log every transfer.

[FAIL] **Memory bleed:** Agents keep growing memory/context unchecked, eventually failing or hallucinating.  
[OK] **Instead:** Use context pruning, summarize memory, enforce hard context/window limits.

[FAIL] **Reflection step missing:** Agent blindly acts without evaluating outcome of tool/API use.  
[OK] **Instead:** After every action, explicitly check if goal was advanced, else replan/escalate.

---

## Quick Reference

### Agentic System Production Checklist

- [ ] Workflow loop (perceive → plan → act → observe → replan) coded and tested
- [ ] Tool/API schema versioning and validation
- [ ] Hand-off and comms protocols documented, tested, and logged
- [ ] All loops/steps capped, watchdog in place
- [ ] All agent actions, plans, and tool calls auditable
- [ ] Reflection and fallback/escalation paths coded
- [ ] Multi-agent eval suite with edge/error/abuse scenarios

---

### Emergency Playbook

- If agent stuck in loop:  
  1. Abort after max step/time, log event  
  2. Output best effort/partial result, escalate for review

- If tool/API fails or abused:  
  1. Retry, fallback to backup tool  
  2. Block tool if abuse detected, alert/triage

- If multi-agent hand-off fails:  
  1. Trigger arbitration/fallback agent  
  2. Escalate to operator if still unresolved

---

## Further Resources

See `data/sources.json` for:

- Agent frameworks: LangChain, LangGraph, CrewAI, Google Agent Developer Kit
- Reference patterns: ReAct, Reflection, Multi-agent, Tool Use, Guardrails

---

**Next:**  
See [references/prompt-engineering-patterns.md](prompt-engineering-patterns.md) for ready-to-use prompt templates, checklists, and validation guides.
