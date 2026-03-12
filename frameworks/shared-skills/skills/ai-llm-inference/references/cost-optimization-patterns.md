# Inference Cost Optimization Patterns

> Operational reference for managing LLM inference costs — token economics, prompt caching, model routing, GPU strategies, cost monitoring, and FinOps practices for AI workloads.

**Freshness anchor:** January 2026 — covers OpenAI Batch API, Anthropic prompt caching, Google context caching, AWS Bedrock pricing, and current token pricing across all major providers.

---

## Token Pricing Quick Reference (January 2026)

### API Providers

| Provider | Model | Input ($/1M tokens) | Output ($/1M tokens) | Context Window |
|---|---|---|---|---|
| OpenAI | GPT-4o | $2.50 | $10.00 | 128K |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | 128K |
| OpenAI | o1 | $15.00 | $60.00 | 200K |
| OpenAI | o3-mini | $1.10 | $4.40 | 200K |
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 | 200K |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 | 200K |
| Google | Gemini 2.0 Flash | $0.10 | $0.40 | 1M |
| Google | Gemini 2.0 Pro | $1.25 | $5.00 | 2M |
| Mistral | Mistral Large | $2.00 | $6.00 | 128K |
| Mistral | Mistral Small | $0.20 | $0.60 | 128K |

### Self-Hosted (GPU Cost Basis)

| GPU | $/hour (on-demand) | $/hour (spot) | Suitable Models | Throughput (tok/s) |
|---|---|---|---|---|
| NVIDIA A100 80GB | $3.50 | $1.20 | Up to 70B | ~100 |
| NVIDIA H100 80GB | $5.50 | $2.50 | Up to 70B (fast) | ~200 |
| NVIDIA A10G 24GB | $1.20 | $0.40 | Up to 13B | ~60 |
| NVIDIA L4 24GB | $0.80 | $0.30 | Up to 13B | ~50 |
| AMD MI300X 192GB | $4.50 | $2.00 | Up to 70B | ~180 |

---

## Cost Optimization Decision Tree

```
Monthly inference spend analysis
│
├── >80% of cost is one use case?
│   ├── YES → Optimize that use case specifically
│   │   ├── Can a smaller model handle it? → Model downgrade
│   │   ├── Are prompts repetitive? → Prompt caching
│   │   ├── Is it latency-insensitive? → Batch API
│   │   └── High volume? → Self-hosted or reserved capacity
│   └── NO → Broad optimization
│       ├── Implement model routing (simple→small, complex→large)
│       ├── Add prompt caching across all endpoints
│       └── Audit for wasted tokens (verbose prompts, unused context)
│
├── Cost growing faster than usage?
│   ├── Context window bloat → Implement conversation summarization
│   ├── Retry storms → Fix error handling, add circuit breakers
│   ├── Unnecessary re-processing → Add response caching
│   └── Image/multimodal costs → Resize images, batch processing
│
└── Need to hit specific cost target?
    ├── Calculate current $/request
    ├── Identify cheapest model that meets quality bar
    ├── Apply caching (typically 30-50% reduction)
    ├── Apply routing (typically 40-60% reduction)
    └── Consider self-hosted at >$10K/month
```

---

## Prompt Caching ROI

### Provider Caching Features

| Provider | Feature | Cache Hit Discount | Min Cache Size | TTL |
|---|---|---|---|---|
| OpenAI | Automatic prompt caching | 50% off input | 1024 tokens | ~5-10 min |
| Anthropic | Explicit prompt caching | 90% off cached portion | 1024 tokens (Sonnet) | 5 min (auto-extend on hit) |
| Google | Context caching | 75% off cached portion | 32K tokens | Configurable (min 1 min) |
| Self-hosted | KV cache (vLLM prefix) | ~80% latency reduction | Any | Session lifetime |

### Anthropic Prompt Caching Implementation

```python
import anthropic

client = anthropic.Anthropic()

# Mark the system prompt for caching (one-time write cost, then 90% off)
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LARGE_SYSTEM_PROMPT,  # Must be >1024 tokens
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": user_message}]
)

# Check caching effectiveness
print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
print(f"Cache write tokens: {response.usage.cache_creation_input_tokens}")
```

### Caching ROI Calculator

| Variable | Formula |
|---|---|
| Cache hit rate | hits / (hits + misses) |
| Cost without caching | requests * input_tokens * input_price |
| Cost with caching | (cache_writes * write_price) + (cache_hits * cached_price) + (misses * input_price) |
| Savings | cost_without - cost_with |
| Break-even hits | cache_write_cost / (normal_price - cached_price) per token |

### When Caching Is Worth It

| Scenario | Expected Hit Rate | ROI |
|---|---|---|
| Fixed system prompt, many users | >95% | Excellent (save 40-85%) |
| RAG with common documents | 30-60% | Good (save 15-40%) |
| Unique prompts per request | <5% | Not worth it (write cost > savings) |
| Chatbot with session context | 70-90% | Good (save 30-70%) |
| Batch processing same template | >99% | Excellent (save 45-89%) |

---

## Model Routing for Cost

### Simple Routing Strategy

```python
class CostOptimizedRouter:
    """Route requests to cheapest model that meets quality requirements."""

    MODELS = {
        "simple": {
            "model": "gpt-4o-mini",
            "cost_per_1k_input": 0.00015,
            "cost_per_1k_output": 0.0006
        },
        "standard": {
            "model": "gpt-4o",
            "cost_per_1k_input": 0.0025,
            "cost_per_1k_output": 0.01
        },
        "complex": {
            "model": "o3-mini",
            "cost_per_1k_input": 0.0011,
            "cost_per_1k_output": 0.0044
        }
    }

    def route(self, request: str, task_type: str = None) -> str:
        if task_type:
            return self._route_by_task(task_type)
        return self._route_by_complexity(request)

    def _route_by_task(self, task_type: str) -> str:
        TASK_ROUTING = {
            "classification": "simple",
            "extraction": "simple",
            "summarization": "standard",
            "analysis": "standard",
            "reasoning": "complex",
            "code_generation": "standard",
            "creative_writing": "standard",
        }
        tier = TASK_ROUTING.get(task_type, "standard")
        return self.MODELS[tier]["model"]

    def _route_by_complexity(self, request: str) -> str:
        # Quick heuristics
        token_count = len(request.split())
        if token_count < 50:
            return self.MODELS["simple"]["model"]
        elif token_count < 500:
            return self.MODELS["standard"]["model"]
        else:
            return self.MODELS["complex"]["model"]
```

---

## Batch vs Real-Time Cost Tradeoffs

### OpenAI Batch API

| Feature | Real-Time | Batch API |
|---|---|---|
| Pricing | Standard | 50% discount |
| Latency | <5s | Up to 24 hours |
| Rate limits | Standard | Higher limits |
| Use cases | User-facing | Analytics, eval, bulk processing |
| Max batch size | N/A | 50,000 requests |
| Error handling | Immediate retry | Retry within batch window |

### Batch API Implementation

```python
import json
from openai import OpenAI

client = OpenAI()

# Step 1: Create JSONL batch file
requests = []
for i, item in enumerate(data_to_process):
    requests.append({
        "custom_id": f"request-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Extract entities."},
                {"role": "user", "content": item["text"]}
            ],
            "max_tokens": 500
        }
    })

# Write to JSONL
with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Step 2: Upload and create batch
batch_file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch = client.batches.create(input_file_id=batch_file.id, endpoint="/v1/chat/completions", completion_window="24h")

# Step 3: Poll for completion
# batch.status: "validating" → "in_progress" → "completed"
```

### When to Use Batch

| Criteria | Batch | Real-Time |
|---|---|---|
| User waiting for response | No | Yes |
| Processing >1000 items | Yes | No |
| Daily analytics/reports | Yes | No |
| Eval suite execution | Yes | No |
| Interactive chat | No | Yes |
| Webhook-triggered processing | Depends on SLA | Yes if <1min SLA |

---

## GPU Strategy: Spot vs On-Demand vs Reserved

### Decision Matrix

| Factor | Spot/Preemptible | On-Demand | Reserved (1yr) | Reserved (3yr) |
|---|---|---|---|---|
| Discount vs on-demand | 60-70% off | Baseline | 30-40% off | 50-60% off |
| Availability guarantee | None | Immediate | Guaranteed | Guaranteed |
| Interruption risk | Yes (2-min warning) | None | None | None |
| Commitment | None | None | 1 year | 3 years |
| Best for | Batch, eval, dev | Spiky workloads | Steady baseline | Mature production |

### Spot Instance Strategy for Inference

```
Spot Checklist:
- [ ] Implement graceful shutdown (save state on 2-min warning)
- [ ] Use spot fleet across multiple instance types (A100, H100, A10G)
- [ ] Implement request queuing (drain queue before shutdown)
- [ ] Set up automatic failover to on-demand
- [ ] Use in regions with lower spot prices (us-east-2, eu-west-1)
- [ ] Never use spot for latency-sensitive, user-facing inference
- [ ] Ideal for: batch processing, eval runs, fine-tuning, dev/staging
```

---

## Cost Monitoring and Alerting

### Dashboard Metrics

| Metric | Granularity | Alert Threshold |
|---|---|---|
| Total spend (daily) | Per day | >120% of daily average |
| Cost per request | Per endpoint | >200% of baseline |
| Token usage (input) | Per model | >150% of expected |
| Token usage (output) | Per model | >150% of expected |
| Cache hit rate | Per endpoint | <50% (if caching enabled) |
| Error rate (wasted tokens) | Per model | >5% |
| Cost per user | Per user cohort | Top 1% users (abuse detection) |

### Budget Alert Implementation

```python
class CostMonitor:
    def __init__(self, daily_budget: float, alert_callback):
        self.daily_budget = daily_budget
        self.alert_callback = alert_callback
        self.daily_spend = 0.0
        self.alert_thresholds = [0.5, 0.8, 0.95, 1.0]
        self.alerts_sent = set()

    def record_cost(self, cost: float, metadata: dict):
        self.daily_spend += cost

        for threshold in self.alert_thresholds:
            if self.daily_spend >= self.daily_budget * threshold:
                if threshold not in self.alerts_sent:
                    self.alerts_sent.add(threshold)
                    self.alert_callback(
                        level="warning" if threshold < 1.0 else "critical",
                        message=f"Daily budget {threshold*100:.0f}% consumed: "
                                f"${self.daily_spend:.2f} / ${self.daily_budget:.2f}",
                        metadata=metadata
                    )

        # Hard stop at 120% of budget
        if self.daily_spend >= self.daily_budget * 1.2:
            raise BudgetExceededError(f"Hard budget limit reached: ${self.daily_spend:.2f}")
```

---

## Token Reduction Techniques

| Technique | Effort | Typical Savings | When to Use |
|---|---|---|---|
| Remove verbose instructions | Low | 10-20% | Prompt has redundant text |
| Shorten few-shot examples | Low | 15-30% | Examples are too detailed |
| Conversation summarization | Medium | 40-60% | Multi-turn conversations |
| Selective context inclusion | Medium | 30-50% | RAG with large context |
| System prompt compression | Low | 10-15% | Long system prompts |
| Output length limits | Low | 20-40% | Model generates too much |
| Response caching (semantic) | Medium | 50-80% | Repetitive questions |
| Prompt compilation (DSPy) | High | 20-40% | Optimizable pipelines |

### Conversation Summarization Pattern

```python
async def manage_conversation_context(messages: list, max_tokens: int = 4000):
    """Summarize old messages to stay within token budget."""
    total_tokens = count_tokens(messages)

    if total_tokens <= max_tokens:
        return messages

    # Keep system message and last 4 turns
    system = messages[0]
    recent = messages[-8:]  # last 4 turns (user + assistant)
    old = messages[1:-8]

    if not old:
        return messages

    # Summarize old messages
    summary = await llm.generate(
        model="gpt-4o-mini",  # cheap model for summarization
        messages=[{
            "role": "user",
            "content": f"Summarize this conversation concisely:\n{format_messages(old)}"
        }]
    )

    return [
        system,
        {"role": "user", "content": f"[Previous conversation summary: {summary}]"},
        {"role": "assistant", "content": "Understood, I have the context."},
        *recent
    ]
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| No cost monitoring | Surprise bills, no optimization data | Dashboard + daily alerts |
| Using largest model for everything | 10-50x cost for marginal quality | Route by complexity |
| Ignoring prompt caching | Missing 50-90% savings on repetitive prompts | Enable caching for system prompts |
| Unlimited context windows | Cost grows linearly with conversation | Summarize or truncate old context |
| Retrying without backoff | Multiplies cost on transient failures | Exponential backoff + circuit breaker |
| Self-hosting at low volume | GPU cost > API cost below ~$5K/month | Use APIs until volume justifies GPUs |
| No output token limits | Model generates 4K tokens when 500 suffice | Set `max_tokens` appropriately |
| Paying on-demand for stable load | 30-60% more than reserved | Reserve capacity for baseline load |

---

## Cross-References

- `multi-model-routing.md` — detailed routing architectures for cost optimization
- `streaming-patterns.md` — streaming to reduce perceived latency (not cost, but UX)
- `../ai-llm/references/model-migration-guide.md` — migrating to cheaper models
- `../ai-llm/references/structured-output-patterns.md` — reduce retries with structured output
- `../ai-prompt-engineering/references/prompt-testing-ci-cd.md` — evaluate quality after cost optimization
