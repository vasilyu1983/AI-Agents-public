# Agent Operations — Best Practices

*Purpose: Provide operational guidance for designing and running single-agent and tool-using agents.*

---

# 1. Core Agent Loop

### Pattern: Plan → Act → Observe → Update → Repeat

**Use when:** The agent must execute multi-step tasks with tools or external systems.

**Structure**

```
1. PLAN
2. ACT (tool or internal step)
3. OBSERVE (tool output or environment)
4. UPDATE (context, state, memory)
5. LOOP or FINAL ANSWER
```

**Checklist**

- [ ] Plan decomposes task into atomic steps.  
- [ ] Each step declares expected evidence.  
- [ ] Tool calls use validated parameters.  
- [ ] Observation evaluates success/failure.  
- [ ] Update revises plan when environment changes.  
- [ ] Loop halts when criteria met.

**Anti-Patterns**

- AVOID: Planning all steps upfront without recalculating after each observation.  
- AVOID: Ignoring tool output errors.  
- AVOID: Continuing loops without state change detection.

---

# 2. Action Execution

### Pattern: Validated Action

**Use when:** Agent performs irreversible or high-impact operations.

**Structure**

```
validate_input()
confirm_if_high_risk()
execute()
verify_result()
```

**Checklist**

- [ ] Input sanitized.  
- [ ] Action matches authorized scope.  
- [ ] Confirmation required for destructive steps.  
- [ ] Verification explicitly checks expected state.  
- [ ] Retry logic configured (1–2 retries max).  

**Decision Tree**

```
Is action irreversible?
→ Yes → Require confirmation → Execute → Verify
→ No → Execute → Verify
```

---

# 3. Retrieval & Grounding

### Pattern: Evidence-First Reasoning

**Use when:** The agent must reference external data or use RAG.

**Structure**

```
retrieve()
validate_source()
inject_into_plan()
reason_from_evidence()
```

**Checklist**

- [ ] Retrieval precedes reasoning.  
- [ ] All factual claims cite retrieved text.  
- [ ] Only relevant chunks injected.  
- [ ] No unsupported assumptions.  

**Anti-Patterns**

- AVOID: Reasoning before evidence.  
- AVOID: Unsupported facts in final answer.

---

# 4. Tool Use

### Pattern: Safe Tool Invocation

**Use when:** Using MCP tools, APIs, or custom functions.

**Structure**

```
choose_tool()
prepare_parameters()
call_tool()
evaluate_output()
```

**Checklist**

- [ ] Tool selected intentionally.  
- [ ] Parameters validated (types, ranges, formats).  
- [ ] Tool errors parsed and retried when transient.  
- [ ] Output grounded before use.  

**Decision Tree**

```
Does the step require external data or action?
→ Yes → Use tool
→ No → Internal reasoning
```

**Anti-Patterns**

- AVOID: Hallucinating tool names or parameters.  
- AVOID: Chaining multiple tool calls without checking outputs.

---

# 5. Planning & Replanning

### Pattern: Dynamic Planning

**Use when:** The agent faces uncertainty or multi-step tasks.

**Structure**

```
initial_plan()
for each step:
    observe -> revise_plan -> continue
```

**Checklist**

- [ ] Plan expressed as numbered steps.  
- [ ] Each step references expected input/output.  
- [ ] Replanning triggered by mismatched observations.  

**Trigger Conditions for Replanning**

- Unexpected tool output  
- Missing required evidence  
- Contradictory or invalid state  

---

# 6. State & Context Management

### Pattern: Minimal Context Window

**Use when:** The agent operates in long tasks or multi-turn sessions.

**Structure**

```
preserve(relevant_history)
summarize(excess_history)
inject(context)
```

**Checklist**

- [ ] Only relevant history retained.  
- [ ] Summaries replace long transcripts.  
- [ ] Context injected before plan generation.  

**Anti-Patterns**

- AVOID: Passing full transcripts into every step.  
- AVOID: Mixing unrelated conversation segments.

---

# 7. Error Handling

### Pattern: Typed Failures

**Use when:** Tool output or steps may fail.

**Structure**

```
if transient_error:
    retry
elif fatal_error:
    report and halt
else:
    continue
```

**Checklist**

- [ ] Categorize errors (transient/fatal).  
- [ ] Retry only transient cases.  
- [ ] Produce human-readable error summaries.  
- [ ] Never mask failures by improvising actions.  

**Quick Reference Table**

| Error Type       | Examples                | Response            |
|------------------|--------------------------|----------------------|
| Transient        | network timeout, rate limit | retry once          |
| Soft failure     | missing field, bad input | request clarification |
| Fatal            | auth failure, invalid tool | halt + report       |

---

# 8. Verification & Success Criteria

### Pattern: Step-by-Step Verification

**Use when:** Agent performs multi-step work.

**Verification Points**

- After tool call  
- After navigation step  
- After each plan iteration  
- Before final answer  

**Checklist**

- [ ] Output matches expected structure.  
- [ ] Data types validated.  
- [ ] Business rules satisfied.  
- [ ] Final answer derived only from verified steps.  

---

# 9. Safety Operations

### Pattern: Action Gating

**Use when:** Action could affect systems, data, or user environment.

**Checklist**

- [ ] Identify high-risk actions.  
- [ ] Provide natural language confirmation step.  
- [ ] Reject ambiguous or unspecified requests.  
- [ ] Block unsupported or dangerous operations.  

**High-Risk Examples**

- File deletion  
- OS-level command  
- External system mutation  
- Financial transactions  

---

# 10. Operational Anti-Patterns (Master List)

- AVOID: Using reasoning to “fill in” missing tool outputs  
- AVOID: Planning long sequences without checkpoints  
- AVOID: Ignoring verification on tool calls  
- AVOID: Acting without grounding  
- AVOID: Overwriting state without confirmation  
- AVOID: Passing hallucinated IDs/paths  
- AVOID: Treating every error as retryable  

---

# 11. Quick Reference Tables

### Agent Loop Summary

| Stage     | What Happens                       | Outputs Needed     |
|-----------|-------------------------------------|--------------------|
| Plan      | Steps, tool choices                 | step list          |
| Act       | Tool execution or reasoning          | tool result        |
| Observe   | Inspect outputs                     | validated data     |
| Update    | Update plan/context                 | new plan           |
| Final     | Produce grounded answer             | final response     |

### Tool Call Checklist

| Item                     | Requirement                    |
|--------------------------|--------------------------------|
| Parameter validation     | types, format, ranges          |
| Tool name                | must be declared & available   |
| Error handling           | retry on transient             |
| Output grounding         | mandatory                      |
| Confirmation             | for high-risk actions          |

---

# 12. Decision Trees (Condensed)

### Choosing Action vs. Tool

```
Does the step require external data?
→ Yes → Tool
→ No → Reason internally
```

### Handling Failures

```
Is error transient?
→ Yes → Retry once
→ No → Summarize + Halt
```

### Loop Continuation

```
Did state change after last action?
→ Yes → Continue loop
→ No → Revise plan or halt
```

---

# End of File
