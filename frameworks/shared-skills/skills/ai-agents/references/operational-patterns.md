# Operational Patterns — Core Primitives for Agent Construction

**Purpose**: Inline executable patterns Claude can use directly without consulting deeper files. These represent the fundamental building blocks for agent implementation.

---

## 1. Agent Loop Pattern (Single-Agent)

```
PLAN → ACT → OBSERVE → UPDATE → REPEAT → FINAL ANSWER
```

**Plan Rules**

- Decompose into atomic steps.
- Select tools intentionally.
- Validate input parameters.

**Act Rules**

- Never guess IDs/paths—retrieve them.
- Confirm before irreversible actions.
- Retry on transient failures.

**Observe Rules**

- Inspect tool outputs.
- Check for contradictions.
- Detect stuck loops.

**Update Rules**

- Append retrieved evidence.
- Adjust plan if environment changes.

---

## 2. OS Agent Action Loop (Desktop / Web / Mobile)

```
OBSERVE(window_state)
GROUND(element)
ACT(click/type/scroll/shortcut)
VERIFY(state_changed)
```

**Constraints**

- Never click blind coordinates if an element is detectable.
- Halt if UI layout diverges.
- Log all observations and verifications.

**Related Resources**: See [`os-agent-capabilities.md`](os-agent-capabilities.md) for desktop automation details.

---

## 3. RAG Pipeline Pattern (Full)

```
query
→ rewrite (if ambiguous)
→ embed
→ retrieve (semantic + keyword if hybrid)
→ rerank (mandatory)
→ filter
→ inject context
→ answer with citations
```

**Injection Format**

```
<retrieved>
[chunk_1]
[chunk_2]
</retrieved>
```

**Chunk Guidance**

- 200–400 tokens each.
- Avoid mixing domains; route queries first.

**Related Resources**: See [`rag-patterns.md`](rag-patterns.md) for contextual retrieval implementation.

---

## 4. Tool Specification Pattern

**Definition Template**

```yaml
tool_name:
  description: [operational purpose]
  input_schema:
    field1: type
    field2: type
  output_schema:
    result: type
  confirm: yes/no
  error_handling:
    retry: [count]
    timeout: [seconds]
```

**Tool Use Rules**

- Validate parameters before execution.
- Sanitize inputs.
- Retry network/timeouts once or twice.
- Reject hallucinated tool names.

**Related Resources**:
- [`tool-design-specs.md`](tool-design-specs.md) for MCP implementation patterns
- [`../assets/tools/tool-definition.md`](../assets/tools/tool-definition.md) for copy-paste templates

---

## 5. Memory System Pattern

**Four Types**

- **Session memory**: Conversation context within a single session
- **Long-term memory**: Persistent facts and preferences across sessions
- **Episodic memory**: Historical interactions and task outcomes
- **Task memory**: Scratchpad for current task execution

**Memory Write Conditions**

- Explicit user confirmation.
- Non-sensitive data only.
- Verifiable fact.
- Must have provenance.

**Retrieval Rules**

- Filter by relevance.
- Summarize >2000 tokens.
- Enforce recency if applicable.

**Related Resources**: See [`memory-systems.md`](memory-systems.md) for architecture details.

---

## 6. Multi-Agent Workflow Pattern

**Roles**

- **Manager** → decomposes task
- **Worker_X** → executes actions
- **Router** → routes domain-specific tasks
- **Evaluator** → scores accuracy + safety

**Manager Rules**

- Never perform work.
- Only produce subtask specifications.
- Collect worker results → integrate → validate.

```yaml
manager:
  tasks: [decompose, orchestrate]
worker_A:
  tasks: [tool-use, research]
evaluator:
  tasks: [score correctness, safety]
router:
  tasks: [domain classification]
```

**Additional Patterns**

- **Diamond**: Parallel specialists → aggregator → final decision.
- **Collaborative**: Agents debate then reconcile with a mixer.
- **Response mixer**: Blend tool-grounded and generative responses with explicit weighting.
- **Contracts**: Treat handoffs as contracts; version JSON Schemas; include negotiation and subcontracts when chaining vendors/teams.
- **Simulation**: Use sandbox/gym loops for policy testing and self-evolution; gate promotions with eval + safety thresholds.

**Related Resources**:
- [`multi-agent-patterns.md`](multi-agent-patterns.md) for orchestration templates
- [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) for delegation protocols
- [`../assets/multi-agent/`](../assets/multi-agent/) for copy-paste templates

---

## 7. Safety & Guardrails Pattern

**Block**

- High-risk actions without confirmation.
- Undeclared tool calls.
- Missing grounding.
- Unsupported domains.

**Require Confirmation For**

- File deletion or overwrite.
- Financial or legal actions.
- OS-level execution.
- External system modifications.

**Related Resources**: See [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) for multi-layer guardrails.

---

## 8. Observability Pattern

**Logs Must Include**

- Input
- Plan
- Tool calls
- Tool results
- Retrieved chunks
- Final output

**Traces**

One span per:
- LM call
- Tool call
- Retrieval step
- Memory write/read

**Metrics**

- Tool success rate ≥95%
- Avg latency < target
- Token cost < budget
- Evaluation score ≥ threshold
- Task success/containment rate ≥ target; escalation rate within budget
- User satisfaction or reviewer score tracked; flag drift in response quality
- Instrument like A/B experiments: track goal completion time, cost, and quality deltas across variants

**Related Resources**: See [`evaluation-and-observability.md`](evaluation-and-observability.md) for OpenTelemetry implementation.

---

## 9. Evaluation Patterns

**Approach**: Use outside-in (end-to-end) plus inside-out (trajectory) evaluation to catch process errors, not just final answers.

### Final Answer Evaluation

```yaml
Correctness: 1–5
Grounding: 1–5
Tool Use: 1–5
Safety: pass/fail
```

### Trajectory Evaluation

- Was the plan valid?
- Did the agent adapt to new state?
- Were tool parameters justified?
- Was retrieval grounded?
- Did handoffs respect contracts? Were schema violations caught?
- Were escalations/HITL gates triggered correctly?

### Evaluators

- Mix LM-judge, agent-judge, and human review for high-risk actions.
- Provide reviewer UI with trace, inputs, tool calls, outputs, and policy checks.
- Score safety (RAI), grounding, determinism, and tool correctness separately.

**Related Resources**: See [`evaluation-and-observability.md`](evaluation-and-observability.md) for LLM-as-judge patterns.

---

## 10. Deployment & CI/CD Pattern (Modern Production Standards)

**Pipeline**

```text
dev → CI eval → staging → canary → production
```

**Pre-deployment Checklist (NIST AI RMF Aligned)**

Safety & Security:
- [ ] Multi-layer guardrails configured (input validation, RBAC, output filtering)
- [ ] PII redaction verified with test cases
- [ ] Tool signature verification enabled (Sigstore/Cosign)
- [ ] HITL (Human-in-the-Loop) gates configured for high-risk operations
- [ ] OWASP GenAI Top 10 vulnerabilities tested
- [ ] Prompt injection defenses validated
- [ ] Roles/runbooks assigned (oncall, SecOps, SRE); incident response playbook tested
- [ ] Safe rollout plan defined (canary %, kill switch, rollback drills)
- [ ] Kill switch and rollback drills exercised this sprint

Observability & Monitoring:
- [ ] OpenTelemetry GenAI spans instrumented
- [ ] SIEM integration configured with alerting rules
- [ ] Cost and latency budgets set
- [ ] MTTD (Mean Time To Detect) baseline established
- [ ] LangSmith/Arize/Azure AI Foundry observability enabled

Evaluation & Quality:
- [ ] Evaluation score ≥ threshold on test suite
- [ ] Tool success rate ≥95%
- [ ] Hijacking scenarios tested
- [ ] Regression gate passed
- [ ] A/B test plan ready (if applicable)

Infrastructure:
- [ ] Rollback path tested
- [ ] Version pinned (model, dependencies, tools)
- [ ] Canary monitoring configured (5-10% traffic)
- [ ] Rate limiting configured
- [ ] Short-lived secrets rotation enabled
- [ ] SBOMs and SLSA attestations attached

Handoffs & Orchestration (Multi-Agent):
- [ ] Handoff payloads validated with JSON Schema
- [ ] trace_id propagation verified
- [ ] Context-transfer tested across agents
- [ ] Manager-worker contracts documented

**Weekly Production Tasks**:
- Run evaluation suite with new production data
- Review SIEM alerts and incident taxonomy
- Check for model/tool drift
- Audit HITL approval queue metrics
- Update cost/latency budgets if needed

**Related Resources**: See [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) for complete production guide.

---

## Shared Utilities (Implementation Patterns)

For cross-cutting implementation concerns in agent development, reference these centralized utilities:

- [llm-utilities.md](../../software-clean-code-standard/utilities/llm-utilities.md) — Token counting, streaming, cost estimation for LLM calls
- [error-handling.md](../../software-clean-code-standard/utilities/error-handling.md) — Effect Result types, correlation IDs for agent error handling
- [resilience-utilities.md](../../software-clean-code-standard/utilities/resilience-utilities.md) — p-retry v6, circuit breaker for LLM API calls
- [logging-utilities.md](../../software-clean-code-standard/utilities/logging-utilities.md) — pino v9 + OpenTelemetry for agent logging
- [observability-utilities.md](../../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing spans per tool/LLM call
- [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) — Vitest, MSW v2 for mocking agent APIs

---

## Usage Notes

- **Prefer inline patterns** for simple, well-understood tasks
- **Reference deeper resources** when guidance or examples needed
- **Use templates** when structured artifacts required
- **Never include theory** — only operational steps
