# Guardrails Implementation

> Operational reference for building multi-layer guardrails — input validation, output filtering, tool approval gates, content classification, escalation triggers, and defense-in-depth architecture for AI agents.

**Freshness anchor:** January 2026 — covers LlamaGuard 3, NeMo Guardrails 0.10.x, Guardrails AI 0.5.x, OpenAI Moderation API v2.

---

## 5-Layer Defense Architecture

```
┌─────────────────────────────────────────────┐
│ Layer 1: INPUT VALIDATION                    │
│ - Schema validation, length limits            │
│ - PII detection and redaction                 │
│ - Injection pattern detection                 │
├─────────────────────────────────────────────┤
│ Layer 2: CONTENT CLASSIFICATION               │
│ - Topic safety classifier                     │
│ - Intent detection (malicious vs benign)      │
│ - Prompt injection scoring                    │
├─────────────────────────────────────────────┤
│ Layer 3: EXECUTION GUARDRAILS                 │
│ - Tool approval gates                         │
│ - Resource limits (tokens, API calls, time)   │
│ - Sandboxed execution environments            │
├─────────────────────────────────────────────┤
│ Layer 4: OUTPUT FILTERING                     │
│ - Response safety classification              │
│ - Factuality / hallucination checks           │
│ - PII leak detection                          │
│ - Format and schema validation                │
├─────────────────────────────────────────────┤
│ Layer 5: MONITORING & ESCALATION              │
│ - Anomaly detection on usage patterns         │
│ - Human-in-the-loop triggers                  │
│ - Audit logging                               │
│ - Circuit breakers                            │
└─────────────────────────────────────────────┘
```

---

## Layer 1: Input Validation

### Validation Rules Quick Reference

| Check | Implementation | Threshold |
|---|---|---|
| Max input length | Character/token count | 4096 tokens (adjust per use case) |
| Encoding validation | UTF-8 check, reject binary | Reject non-UTF-8 |
| Language detection | fasttext/langdetect | Reject unsupported languages |
| PII detection | Presidio / custom NER | Redact or reject based on policy |
| URL/link scanning | Regex + allowlist | Block unknown domains |
| File upload scanning | ClamAV + type check | Reject executables, limit size |
| Rate limiting | Per-user token bucket | 10 requests/min default |

### Input Validation Code Pattern

```python
from pydantic import BaseModel, validator, Field
from typing import Optional
import re

class AgentInput(BaseModel):
    message: str = Field(max_length=16000)
    session_id: str = Field(pattern=r'^[a-zA-Z0-9\-]{1,64}$')
    attachments: Optional[list[str]] = Field(default=None, max_length=5)

    @validator("message")
    def validate_message(cls, v):
        # Reject null bytes
        if "\x00" in v:
            raise ValueError("Invalid characters in message")

        # Reject excessive repetition (potential DoS)
        if len(set(v.split())) < len(v.split()) * 0.1:
            raise ValueError("Message contains excessive repetition")

        return v.strip()

class InputGuardrail:
    def __init__(self, config):
        self.max_tokens = config.get("max_tokens", 4096)
        self.pii_detector = PIIDetector()
        self.injection_detector = InjectionDetector()

    async def validate(self, input_data: AgentInput) -> GuardrailResult:
        checks = [
            self._check_token_count(input_data.message),
            self._check_pii(input_data.message),
            self._check_injection(input_data.message),
        ]
        results = await asyncio.gather(*checks)
        return self._aggregate_results(results)
```

---

## Layer 2: Content Classification

### Classification Decision Tree

```
Input message received
│
├── Run injection classifier (score 0-1)
│   ├── Score > 0.9 → BLOCK (high confidence injection)
│   ├── Score 0.7-0.9 → FLAG for review + proceed with restrictions
│   └── Score < 0.7 → PASS
│
├── Run topic safety classifier
│   ├── Harmful content detected → BLOCK + log
│   ├── Borderline content → Apply restricted mode
│   └── Safe content → PASS
│
├── Run intent classifier
│   ├── Out-of-scope request → REDIRECT to appropriate channel
│   ├── Sensitive action requested → Require confirmation
│   └── Normal request → PASS
│
└── All checks passed → Forward to agent
```

### LlamaGuard Integration

- Model: `meta-llama/Llama-Guard-3-8B` — classifies across 13 unsafe categories (S1-S13)
- Input: format as conversation (user + optional assistant message)
- Output: "safe" or "unsafe" with category codes
- Use `apply_chat_template()` for proper formatting
- Can classify both user input AND agent output

### NeMo Guardrails Integration

- Configure via YAML: define input rails (jailbreak, toxicity, topic) and output rails (toxicity, factuality, data leakage)
- Usage: `RailsConfig.from_path()` then `LLMRails(config).generate_async(messages=...)`
- Response is automatically filtered through all configured rails
- Supports custom Colang flows for domain-specific rules

---

## Layer 3: Execution Guardrails

### Tool Approval Gate Matrix

| Tool Category | Approval Level | Implementation |
|---|---|---|
| Read-only data retrieval | Auto-approve | No gate needed |
| Internal API calls | Auto-approve with logging | Log all calls |
| External API calls | Require confirmation for new endpoints | Allowlist check |
| Data modification (write) | Require user confirmation | Confirmation prompt |
| Financial transactions | Require explicit user + amount confirmation | Double confirmation |
| File system operations | Restricted paths only | Sandboxed filesystem |
| Code execution | Sandboxed environment only | Docker/gVisor sandbox |
| Email/messaging send | Require user confirmation | Preview before send |
| Database mutations | Require confirmation + dry-run | Show planned changes |

### Tool Gate Implementation

```python
class ToolApprovalGate:
    APPROVAL_LEVELS = {
        "auto": lambda tool, params: True,
        "log": lambda tool, params: True,  # auto-approve but log
        "confirm": None,  # requires user confirmation
        "deny": lambda tool, params: False,
    }

    def __init__(self, policy: dict):
        self.policy = policy  # tool_name -> approval_level mapping
        self.call_counts = defaultdict(int)
        self.max_calls_per_tool = 20

    async def check(self, tool_name: str, params: dict) -> ApprovalResult:
        # Rate limit per tool
        self.call_counts[tool_name] += 1
        if self.call_counts[tool_name] > self.max_calls_per_tool:
            return ApprovalResult(approved=False, reason="Tool call limit exceeded")

        level = self.policy.get(tool_name, "confirm")  # default: require confirmation

        if level == "deny":
            return ApprovalResult(approved=False, reason="Tool blocked by policy")

        if level == "confirm":
            return ApprovalResult(
                approved=False,
                requires_confirmation=True,
                preview=self._format_preview(tool_name, params)
            )

        return ApprovalResult(approved=True, level=level)

    def _format_preview(self, tool_name: str, params: dict) -> str:
        return f"Agent wants to call `{tool_name}` with: {json.dumps(params, indent=2)}"
```

### Resource Limits

| Resource | Default Limit | Escalation |
|---|---|---|
| Total tokens per session | 100,000 | Warn at 80%, hard stop at 100% |
| LLM calls per task | 25 | Warn at 20, hard stop at 25 |
| Tool calls per task | 50 | Warn at 40, hard stop at 50 |
| Execution time per task | 5 minutes | Warn at 4min, hard stop at 5min |
| Concurrent tool calls | 5 | Queue additional calls |
| Output length | 4,096 tokens | Truncate with warning |
| File upload size | 10MB | Reject with message |

---

## Layer 4: Output Filtering

### Output Validation Pipeline

```
LLM response generated
│
├── Step 1: Format validation
│   ├── JSON mode → Validate against schema
│   ├── Tool call → Validate function name + params
│   └── Free text → Check length limits
│
├── Step 2: Safety classification
│   ├── Run LlamaGuard on response
│   ├── Run toxicity classifier
│   └── Check against custom blocklists
│
├── Step 3: PII leak detection
│   ├── Scan for SSN, credit card, phone patterns
│   ├── Check for training data memorization patterns
│   └── Verify no internal system prompts leaked
│
├── Step 4: Factuality check (if applicable)
│   ├── Cross-reference claims against retrieved context
│   ├── Flag unsupported assertions
│   └── Add confidence qualifiers where needed
│
└── Step 5: Final sanitization
    ├── Strip internal reasoning markers
    ├── Remove tool call artifacts
    └── Ensure consistent formatting
```

### PII Leak Detection

```python
import re

PII_PATTERNS = {
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone_us": r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    "api_key": r'\b(?:sk|pk|api[_-]?key)[_-][A-Za-z0-9]{20,}\b',
}

def scan_for_pii(text: str) -> list[dict]:
    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            findings.append({
                "type": pii_type,
                "start": match.start(),
                "end": match.end(),
                "value": "[REDACTED]"
            })
    return findings

def redact_pii(text: str) -> str:
    for pii_type, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", text)
    return text
```

---

## Layer 5: Monitoring and Escalation

### HITL Escalation Triggers

| Trigger | Confidence Threshold | Action |
|---|---|---|
| Safety classifier flags response | Any "unsafe" classification | Block + human review |
| Agent confidence is low | Model reports <0.6 confidence | Present draft to human |
| High-stakes action requested | Financial >$100, data deletion | Require human approval |
| User expresses frustration | Sentiment score <-0.5 twice | Offer human handoff |
| Agent loops (3+ identical steps) | Automatic detection | Pause + notify operator |
| Out-of-scope request detected | Intent classifier: "other" | Route to human |
| User explicitly requests human | Keyword detection | Immediate handoff |
| Error rate spike | >3 errors in 5 minutes | Circuit breaker + alert |

### Confidence Threshold Calibration

```python
class ConfidenceGate:
    """Route to HITL based on model confidence."""

    THRESHOLDS = {
        "auto_approve": 0.85,    # Agent handles autonomously
        "soft_review": 0.60,     # Agent handles, flagged for async review
        "hard_review": 0.40,     # Must be reviewed before sending
        "escalate": 0.0,         # Immediate human handoff
    }

    def evaluate(self, response, confidence: float) -> str:
        if confidence >= self.THRESHOLDS["auto_approve"]:
            return "send"
        elif confidence >= self.THRESHOLDS["soft_review"]:
            self._queue_for_review(response)
            return "send"
        elif confidence >= self.THRESHOLDS["hard_review"]:
            return "hold_for_review"
        else:
            return "escalate_to_human"
```

### Audit Logging Requirements

| Event | Required Fields | Retention |
|---|---|---|
| User input received | session_id, timestamp, input_hash, user_id | 90 days |
| Guardrail triggered | layer, check_name, result, severity | 1 year |
| Tool call executed | tool_name, params_hash, result_status | 90 days |
| Output sent to user | session_id, timestamp, output_hash | 90 days |
| HITL escalation | trigger_reason, response_time, resolution | 1 year |
| Safety incident | full context, all layers' results | 2 years |

---

## Testing Guardrail Effectiveness

### Test Categories

| Category | Purpose | Example Inputs |
|---|---|---|
| Golden path | Verify normal requests pass all layers | Typical user queries |
| Injection probes | Test Layer 1+2 detection | Known injection patterns |
| Adversarial content | Test content classifiers | Borderline harmful content |
| PII probing | Test output filtering | Requests designed to extract PII |
| Resource exhaustion | Test execution limits | Tasks that trigger many tool calls |
| Edge cases | Test boundary conditions | Empty input, max length, unicode |

### Guardrail Effectiveness Metrics

| Metric | Target | Measurement |
|---|---|---|
| True positive rate (harmful blocked) | >99% | Red team testing |
| False positive rate (safe blocked) | <2% | Normal traffic sampling |
| Latency overhead per layer | <50ms | p95 latency measurement |
| Total guardrail latency | <200ms | End-to-end measurement |
| Escalation accuracy | >90% | HITL review of escalated items |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Single-layer defense | One bypass = full compromise | 5-layer defense-in-depth |
| Regex-only injection detection | Easily bypassed with encoding tricks | ML classifier + regex as backup |
| Blocking without logging | Cannot improve, cannot audit | Always log blocks with context |
| Overly strict guardrails | Users frustrated, workarounds emerge | Tune thresholds based on FP rate |
| Guardrails only on input | Hallucinations and leaks pass through | Filter both input AND output |
| Hard-coded thresholds | Cannot adapt to new attack patterns | Configurable + regularly updated |
| No testing of guardrails | Assume they work until breach | Regular red team testing |
| Guardrails as afterthought | Bolted on, incomplete coverage | Design guardrails into architecture |

---

## Cross-References

- `agent-debugging-patterns.md` — debugging guardrail-triggered failures
- `voice-multimodal-agents.md` — modality-specific guardrails
- `../ai-prompt-engineering/references/prompt-security-defense.md` — prompt-level security
- `../ai-llm/references/structured-output-patterns.md` — output validation patterns
