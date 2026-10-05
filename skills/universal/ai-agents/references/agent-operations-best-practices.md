# Agent Operations — Best Practices

*Purpose: Provide operational guidance for designing and running single-agent and tool-using agents.*

---
## Table of Contents

- [Pattern: Plan → Act → Observe → Update → Repeat](#pattern-plan-→-act-→-observe-→-update-→-repeat)
- [2. Action Execution](#2-action-execution)
- [Pattern: Validated Action](#pattern-validated-action)
- [3. Retrieval & Grounding](#3-retrieval--grounding)
- [Pattern: Evidence-First Reasoning](#pattern-evidence-first-reasoning)
- [4. Tool Use](#4-tool-use)
- [Pattern: Safe Tool Invocation](#pattern-safe-tool-invocation)
- [5. Planning & Replanning](#5-planning--replanning)
- [Pattern: Dynamic Planning](#pattern-dynamic-planning)
- [6. State & Context Management](#6-state--context-management)
- [Pattern: Minimal Context Window](#pattern-minimal-context-window)
- [7. Error Handling](#7-error-handling)
- [Pattern: Typed Failures](#pattern-typed-failures)
- [8. Verification & Success Criteria](#8-verification--success-criteria)
- [Pattern: Step-by-Step Verification](#pattern-step-by-step-verification)
- [9. Safety Operations](#9-safety-operations)
- [Pattern: Action Gating](#pattern-action-gating)
- [10. Operational Anti-Patterns (Master List)](#10-operational-anti-patterns-master-list)
- [11. Quick Reference Tables](#11-quick-reference-tables)
- [Agent Loop Summary](#agent-loop-summary)
- [Tool Call Checklist](#tool-call-checklist)
- [12. Decision Trees (Condensed)](#12-decision-trees-condensed)
- [Choosing Action vs. Tool](#choosing-action-vs-tool)
- [Handling Failures](#handling-failures)
- [Loop Continuation](#loop-continuation)
- [13. Cross-Cutting Primitives (Pointers)](#13-cross-cutting-primitives-pointers)
- [End of File](#end-of-file)


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

# 13. Cross-Cutting Primitives (Pointers)

Condensed primitives that used to live in a separate operational-patterns file. Each links to its owner.

- **OS agent action loop** — `OBSERVE(window_state) → GROUND(element) → ACT → VERIFY(state_changed)`; never click blind coordinates when an element is detectable, halt if the UI layout diverges: [`os-agent-capabilities.md`](os-agent-capabilities.md).
- **Tool specification** — one YAML block per tool (`description`, `input_schema`, `output_schema`, `confirm`, `error_handling.retry/timeout`); reject hallucinated tool names: [`tool-design-specs.md`](tool-design-specs.md), template in [`../assets/tools/tool-definition.md`](../assets/tools/tool-definition.md).
- **Memory write conditions** — explicit user confirmation, non-sensitive, verifiable, with provenance; summarize retrievals over ~2000 tokens: [`memory-systems.md`](memory-systems.md).
- **Multi-agent roles and extra shapes** — manager never performs work; diamond (parallel specialists → aggregator), collaborative (debate then reconcile), response mixer (tool-grounded plus generative with explicit weighting), contracts (versioned handoff schemas, subcontracts across vendors), simulation (sandbox loops gated by eval and safety thresholds): [`multi-agent-patterns.md`](multi-agent-patterns.md), [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md).
- **Observability floor** — log input, plan, tool calls, tool results, retrieved chunks, final output; one span per LM call, tool call, retrieval step, memory read/write; metrics: tool success rate ≥95%, latency and token cost under budget, eval score ≥ threshold, task success/containment and escalation rate within budget, reviewer or satisfaction score tracked for drift; instrument variants like A/B experiments (goal completion time, cost, quality deltas): [`evaluation-and-observability.md`](evaluation-and-observability.md).
- **Evaluation** — outside-in (final answer: correctness, grounding, tool use 1-5, safety pass/fail) plus inside-out (trajectory: plan valid, adapted to new state, tool parameters justified, handoffs respected contracts, HITL gates fired); mix LM-judge, agent-judge, and human review for high-risk actions, and give reviewers a UI with trace, inputs, tool calls, outputs, and policy checks: [`evaluation-and-observability.md`](evaluation-and-observability.md).
- **Deployment pipeline** — `dev → CI eval → staging → canary → production`; pre-deployment gate covers guardrails, PII redaction tests, tool signature verification, HITL gates, OWASP GenAI Top 10 and prompt-injection tests, incident roles and runbooks, kill switch and rollback drills, OTel GenAI spans, SIEM alerting, cost and latency budgets, MTTD baseline, version pinning, canary at 5-10% traffic, rate limits, short-lived secrets, SBOM and SLSA attestations, and validated handoff payloads with `trace_id` propagation. Weekly: rerun the eval suite on fresh production data, review SIEM alerts and incident taxonomy, check model and tool drift, audit the HITL approval queue, revisit budgets: [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md).
- **Shared implementation utilities** — token counting and cost estimation, Result types and correlation IDs, retry and circuit breaker, structured logging, OpenTelemetry SDK setup, and API mocking for tests: [`../../software-clean-code-standard/references/llm-utilities.md`](../../software-clean-code-standard/references/llm-utilities.md), [`error-handling.md`](../../software-clean-code-standard/references/error-handling.md), [`resilience-utilities.md`](../../software-clean-code-standard/references/resilience-utilities.md), [`logging-utilities.md`](../../software-clean-code-standard/references/logging-utilities.md), [`observability-utilities.md`](../../software-clean-code-standard/references/observability-utilities.md), [`testing-utilities.md`](../../software-clean-code-standard/references/testing-utilities.md).

---

# End of File
