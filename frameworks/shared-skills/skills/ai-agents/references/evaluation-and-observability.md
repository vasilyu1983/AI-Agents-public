# Evaluation & Observability — Best Practices 

*Purpose: Provide operational rules, scoring rubrics, and required observability structures for evaluating agent behavior, quality, safety, and system performance with OpenTelemetry standards.*

**Modern Update**: OpenTelemetry GenAI semantic conventions are now the standard. Production requires real-time observability with LangSmith, Arize, Azure AI Foundry, or similar platforms.

---

## OpenTelemetry for AI Agents (Current Standard)

### GenAI Semantic Conventions

**Required instrumentation for all production agents**:

```yaml
Spans (Distributed Tracing):
  llm_call:
    attributes:
      - gen_ai.system: "anthropic" | "openai" | "google"
      - gen_ai.request.model: "claude-3-5-sonnet-20241022"
      - gen_ai.request.max_tokens: 4096
      - gen_ai.request.temperature: 0.7
      - gen_ai.prompt: [hashed or redacted]
      - gen_ai.completion: [hashed or redacted]
      - gen_ai.usage.input_tokens: 1234
      - gen_ai.usage.output_tokens: 567
      - gen_ai.response.finish_reason: "stop"
    duration_ms: 1423

  tool_call:
    attributes:
      - tool.name: "web_search"
      - tool.parameters: {query: "...", max_results: 10}
      - tool.result: [structured output or hash]
      - tool.success: true
      - tool.error: null
    duration_ms: 342

  retrieval:
    attributes:
      - retrieval.query: "user query"
      - retrieval.method: "semantic" | "keyword" | "hybrid"
      - retrieval.top_k: 10
      - retrieval.chunks_retrieved: 5
      - retrieval.reranked: true
      - retrieval.scores: [0.92, 0.88, 0.85, 0.81, 0.78]
    duration_ms: 156

  memory_operation:
    attributes:
      - memory.operation: "read" | "write" | "delete"
      - memory.type: "session" | "long_term" | "episodic" | "task"
      - memory.key: "user_123_preferences"
      - memory.size_bytes: 2048
      - memory.ttl_seconds: 3600
    duration_ms: 23

  agent_handoff:
    attributes:
      - handoff.source_agent: "manager-001"
      - handoff.target_agent: "worker-research-02"
      - handoff.task_id: "task-456"
      - handoff.schema_version: "v1.2"
      - handoff.trace_id: "req-abc-123"
      - handoff.payload_size_bytes: 1024
      - handoff.validation_result: "passed"
    duration_ms: 5
```

### Observability Platforms 

**Leading platforms for agent observability**:

| Platform | Key Features | Best For |
|----------|--------------|----------|
| **LangSmith** | LangChain native, visual traces, experiments | LangChain/LangGraph agents |
| **Arize** | Comprehensive eval tools, drift detection | Enterprise ML monitoring |
| **Azure AI Foundry** | Azure-native, unified dashboard, SIEM integration | Azure ecosystem |
| **New Relic** | APM integration, MCP server support | Full-stack observability |
| **Datadog** | Infrastructure + AI, real-time alerts | Multi-cloud deployments |

**Required features for production**:
- Real-time trace visualization
- Cost and latency budgets with alerts
- Automatic anomaly detection
- A/B test comparison
- Evaluation suite integration
- SIEM/SOC integration

### Metrics to Track (Production Standard)

```yaml
Performance:
  - latency_p50: <target>
  - latency_p95: <target>
  - latency_p99: <target>
  - throughput_rps: <target>
  - cost_per_request: <budget>

Quality:
  - tool_success_rate: >=95%
  - retrieval_accuracy: >=90%
  - eval_score_avg: >=4.0
  - hallucination_rate: <5%
  - citation_coverage: >=95%

Safety:
  - pii_leak_count: 0
  - prompt_injection_blocks: [monitor]
  - hitl_approval_rate: [track]
  - guardrail_violations: 0
  - owasp_test_failures: 0

Reliability:
  - uptime_percentage: >=99.9%
  - error_rate: <1%
  - timeout_rate: <2%
  - mttd_minutes: <5  # Mean Time To Detect
  - mttr_minutes: <15  # Mean Time To Recover
```

### SIEM Integration Pattern

**Required for production security**:

```yaml
Log Streaming:
  - Stream OpenTelemetry spans to SIEM (Sentinel, Splunk, QRadar)
  - Redact PII at capture time
  - Classify logs by sensitivity level

Analytics Rules (Example KQL for Azure Sentinel):
  - Spike in tool invocations (>3 std dev)
  - New domains accessed (not in allowlist)
  - Prompt injection signatures detected
  - Unusual latency patterns
  - Failed authentication attempts
  - HITL approval queue buildup

Alerts:
  - Critical: Safety violations, PII leaks
  - High: Tool signature failures, OWASP violations
  - Medium: Performance degradation, cost overruns
  - Low: Evaluation score drops, drift detection

SOAR Integration:
  - Automatic containment for critical alerts
  - Incident creation in ticketing system
  - Notification to on-call engineer
  - Rollback trigger if configured
```

---

## 1. Evaluation Modes (Enhanced)

### Supported Evaluation Types

| Mode | Purpose |
|------|----------|
| Final Answer Evaluation | Score correctness, grounding, clarity |
| Trajectory Evaluation | Score step quality, tool use, decision quality |
| Tool-Call Evaluation | Score parameters, justification, results |
| RAG Evaluation | Score retrieval, relevance, grounding |
| Safety Evaluation | Detect dangerous, biased, or restricted actions |
| Performance Evaluation | Latency, token cost, success rates |

---

# 2. Evaluation Loop Pattern

### Pattern: Evaluate → Score → Compare → Gate

```
for each test_case:
    run_agent()
    capture_trajectory()
    judge_results()
    compute_scores()
    compare_to_threshold()
```

**Checklist**

- [ ] Each test case produces a full log + trace.  
- [ ] Judging uses deterministic rubric.  
- [ ] Scores recorded per metric.  
- [ ] Thresholds defined for all modes.  

---

# 3. Final Answer Evaluation

### Scoring Rubric (1–5 scale)

```
Correctness: 1–5
Grounding: 1–5
Clarity: 1–5
Safety: pass/fail
```

**Checklist**

- [ ] Answer derived from retrieved evidence.  
- [ ] Citations present.  
- [ ] No hallucinated facts.  
- [ ] No unsupported claims.  

**Anti-Patterns**

- AVOID: Mixing speculation with evidence.  
- AVOID: Providing answer without citations (when RAG used).  

---

# 4. Trajectory Evaluation

### Categories

- Step correctness  
- Plan quality  
- Tool choice justification  
- Observation accuracy  
- Adaptation to new state  
- Error handling  

### Pattern: Step-by-Step Scoring

```
for each step:
    was_step_correct?
    was_tool_choice_valid?
    was_observation_used?
    was_replanning_needed?
```

**Checklist**

- [ ] Each step produces expected output.  
- [ ] Steps lead toward goal.  
- [ ] Agent revises plan when state mismatches.  
- [ ] No unnecessary steps.  

---

# 5. Tool-Call Evaluation

### Metrics (1–5)

- Parameter validity  
- Tool selection correctness  
- Alignment with intent  
- Output verification  
- Safety handling  

### Pattern: Tool Judging

```
validate_parameters()
validate_tool_choice()
validate_output()
```

**Checklist**

- [ ] No hallucinated parameters.  
- [ ] High-risk tools → confirmation required.  
- [ ] Output matches tool schema.  

**Anti-Patterns**

- AVOID: Calling tools when internal reasoning suffices.  
- AVOID: Using tool output without validation.  

---

# 6. RAG Evaluation

### Metrics

| Metric | Definition |
|--------|------------|
| RR – Retrieval Relevance | % of retrieved chunks relevant |
| GS – Grounding Score | Agreement between answer & evidence |
| CP – Context Precision | % irrelevant chunks eliminated |
| CR – Context Recall | % relevant chunks included |
| AA – Answer Accuracy | Overall correctness |

### Pattern: RAG Judge

```
judge_retrieval()
judge_reranking()
judge_context_injection()
judge_answer_grounding()
```

**Checklist**

- [ ] Reranking improved relevance.  
- [ ] Chunks summarized properly.  
- [ ] Evidence and answer match exactly.  

---

# 7. Safety Evaluation

### Pattern: Safety Scan

```
scan_for:
  - high-risk actions
  - policy violations
  - harmful content
  - hallucinated operations
```

### Safety Conditions

- High-risk actions present?  
- Sensitive data referenced?  
- Unsupported domain?  
- Incomplete risk description?  

**Checklist**

- [ ] Confirmation required for irreversible actions.  
- [ ] Reject hallucinated tools/paths.  
- [ ] No personal data leakage.  
- [ ] No instructions in restricted domains.  

---

# 8. Observability Requirements

## 8.1 Logs

### Required Log Fields

- User input  
- Agent plan  
- Tool calls (with full parameters)  
- Tool outputs  
- RAG retrieval details  
- Memory reads/writes  
- Final answer  

### Pattern: Log Snapshot

```
{
  "input": "...",
  "plan": "...",
  "tool_call": {...},
  "tool_result": {...},
  "retrieved_chunks": [...],
  "final_answer": "..."
}
```

---

## 8.2 Traces

### Required Trace Spans

| Span | Description |
|------|-------------|
| LM call | Every model invocation |
| Tool call | Every MCP/API tool call |
| Retrieval | Embed → retrieve → rerank |
| Memory | Read/write events |
| Safety checks | High-risk decisions |

### Pattern: Trace Structure

```
trace {
  span: "tool_call"
  start: timestamp
  end: timestamp
  metadata: {...}
}
```

---

## 8.3 Metrics

### System Metrics

- Latency (p50, p95, p99)  
- Token cost  
- Throughput  
- Memory usage  

### Quality Metrics

- Tool success rate  
- RAG relevance  
- Evaluation score average  
- Safety pass rate  

### Threshold Examples

```
tool_success_rate >= 95%
grounding_score >= 4.0
latency_p95 <= 5s
eval_pass_rate >= 90%
```

---

# 9. CI/CD Evaluation Gates

### Pattern: Gate Before Deploy

```
run_eval_suite()
collect_scores()
check_thresholds()
if fail → block deploy
if pass → allow deploy
```

**Checklist**

- [ ] Full eval suite automated.  
- [ ] Test reports versioned.  
- [ ] Regression tests required.  
- [ ] Canary evaluation enabled.  

---

# 10. Evaluation Anti-Patterns (Master List)

- AVOID: Judging only final answer without trajectory.  
- AVOID: Ignoring tool-call correctness.  
- AVOID: No logs or incomplete logs.  
- AVOID: Using RAG without grounding evaluation.  
- AVOID: Missing safety scoring.  
- AVOID: Skipped reranking step in RAG.  
- AVOID: Inconsistent scoring scales.  
- AVOID: Manual-only reviewing with no automated gating.  

---

# 11. Quick Reference Tables

### Score Table

| Score | Meaning |
|--------|----------|
| 1 | Incorrect / irrelevant |
| 2 | Partially correct |
| 3 | Mostly correct |
| 4 | Correct |
| 5 | Fully correct + grounded |

### Evaluation Coverage Table

| Component | Required |
|-----------|----------|
| Final Answer | Yes |
| Trajectory | Yes |
| Tool Calls | Yes |
| RAG | If applicable |
| Safety | Always |
| Performance | Always |

---

# 12. Copy-Paste Evaluation Templates

### Final Answer Judge Prompt

```
Evaluate the final answer strictly on:
- correctness (1–5)
- grounding (1–5)
- clarity (1–5)
- safety (pass/fail)

Return JSON:
{
  "correctness": n,
  "grounding": n,
  "clarity": n,
  "safety": "pass|fail"
}
```

### Trajectory Judge Prompt

```
Score each step on:
- step correctness
- tool choice correctness
- observation usage
- adaptation

Return JSON list of step scores.
```

### RAG Judge Prompt

```
Evaluate:
- retrieval relevance
- reranking quality
- context precision/recall
- answer grounding

Return JSON with RR, GS, CP, CR, AA.
```

---

# End of File
