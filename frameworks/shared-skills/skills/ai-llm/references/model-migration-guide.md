# Model Migration Guide

> Operational reference for migrating between LLM providers and models — API differences, prompt adaptation, evaluation methodology, staged rollout, and provider abstraction patterns.

**Freshness anchor:** January 2026 — covers OpenAI GPT-4o/o1/o3-mini, Anthropic Claude 3.5 Sonnet/Opus, Google Gemini 2.0, Mistral Large, LiteLLM 1.x, OpenRouter.

---

## Migration Decision Tree

```
Considering model migration
│
├── Why are you migrating?
│   ├── Cost reduction
│   │   ├── Same provider, smaller model → Low risk, start here
│   │   ├── Different provider, comparable model → Medium risk
│   │   └── Open source / self-hosted → High risk, high reward
│   │
│   ├── Quality improvement
│   │   ├── Same provider, larger model → Low risk
│   │   ├── Different provider, best-in-class → Medium risk
│   │   └── Fine-tuned model → High risk, requires eval infra
│   │
│   ├── Latency improvement
│   │   ├── Smaller model → Check quality tradeoff
│   │   ├── Different provider with faster infra → Benchmark first
│   │   └── Edge deployment → Significant architecture change
│   │
│   ├── Feature requirement
│   │   ├── Structured outputs (strict) → OpenAI or Gemini
│   │   ├── Long context (200K+) → Gemini or Claude
│   │   ├── Vision capabilities → GPT-4o, Claude, Gemini
│   │   └── Reasoning (chain of thought) → o1/o3, Claude
│   │
│   └── Vendor diversification
│       ├── Add fallback provider → Keep primary, add secondary
│       └── Remove single dependency → Abstraction layer required
│
└── Risk assessment
    ├── How many prompts need migration? → 1-5 (low), 5-20 (medium), 20+ (high)
    ├── Do you have eval datasets? → Required before migration
    └── Can you run both in parallel? → Strongly recommended
```

---

## API Differences Quick Reference

### Chat Completions API Mapping

| Feature | OpenAI | Anthropic | Google Gemini | Mistral |
|---|---|---|---|---|
| Endpoint | `/v1/chat/completions` | `/v1/messages` | `generateContent` | `/v1/chat/completions` |
| System prompt | `messages[0].role="system"` | `system` parameter | `system_instruction` | `messages[0].role="system"` |
| Max output tokens | `max_tokens` (required for o1) | `max_tokens` (required) | `max_output_tokens` | `max_tokens` |
| Temperature | `temperature` (0-2) | `temperature` (0-1) | `temperature` (0-2) | `temperature` (0-1) |
| Stop sequences | `stop` | `stop_sequences` | `stop_sequences` | `stop` |
| Streaming | `stream: true` | `stream: true` | `stream: true` | `stream: true` |
| Tool calling | `tools` + `tool_choice` | `tools` + `tool_choice` | `tools` + `tool_config` | `tools` + `tool_choice` |
| JSON mode | `response_format: {type: "json_object"}` | Use tool_use | `response_mime_type` | `response_format` |
| Structured output | `response_format.json_schema` | Not native (use tools) | `response_schema` | Not native |
| Vision | `image_url` in content | `image` content block | `inline_data` | `image_url` in content |

### Authentication

| Provider | Auth Method | Header |
|---|---|---|
| OpenAI | API key | `Authorization: Bearer sk-...` |
| Anthropic | API key | `x-api-key: sk-ant-...` |
| Google | API key or OAuth | `x-goog-api-key: ...` |
| Mistral | API key | `Authorization: Bearer ...` |
| Azure OpenAI | API key or Azure AD | `api-key: ...` |

---

## Prompt Adaptation Strategies

### Strategy 1: Direct Port (Low Effort)

```
Use when: simple prompts, similar model capabilities
Risk: medium — behavior differences may surface in edge cases

Steps:
1. Copy prompt text unchanged
2. Adapt API call format
3. Run eval suite
4. Fix specific failures
```

### Strategy 2: Re-optimization (Medium Effort)

```
Use when: complex prompts, different model strengths
Risk: low — most thorough approach

Steps:
1. Document the intent of each prompt section
2. Rewrite for target model's strengths
3. Adjust few-shot examples (may need different style)
4. Tune parameters (temperature, max_tokens)
5. Run eval suite + manual review
```

### Strategy 3: Model-Specific Variants (High Effort, High Quality)

```
Use when: production-critical prompts, multi-provider setup
Risk: lowest — each model gets optimal prompt

Steps:
1. Maintain separate prompt files per provider
2. Optimize each independently
3. Share eval datasets across variants
4. Track quality metrics per variant
```

### Provider-Specific Prompt Tips

| Aspect | OpenAI GPT-4o | Claude 3.5 Sonnet | Gemini 2.0 | Mistral Large |
|---|---|---|---|---|
| System prompt style | Concise, direct | Detailed, with examples | Concise | Concise |
| Few-shot examples | 2-3 optimal | 3-5 optimal | 2-3 optimal | 2-4 optimal |
| XML tags in prompts | Sometimes helpful | Very effective | Less effective | Sometimes helpful |
| Chain of thought | Explicit request needed | Natural tendency | Explicit request needed | Explicit request needed |
| Long context | Good to 128K | Excellent to 200K | Excellent to 2M | Good to 128K |
| Instruction following | Excellent | Excellent | Good | Good |
| JSON output | Reliable with JSON mode | Reliable with tool_use | Reliable with schema | Good with JSON mode |

---

## Evaluation Comparison Methodology

### Eval Dataset Requirements

| Dataset Type | Minimum Size | Purpose |
|---|---|---|
| Golden set | 50-100 examples | Core functionality verification |
| Edge cases | 20-50 examples | Boundary behavior testing |
| Adversarial | 20-30 examples | Safety and robustness |
| Domain-specific | 50-100 examples | Domain accuracy |
| Regression set | 30-50 examples | Prevent known failures |

### Side-by-Side Evaluation Framework

```python
import asyncio
from dataclasses import dataclass

@dataclass
class EvalResult:
    input_text: str
    model_a_output: str
    model_b_output: str
    model_a_latency_ms: float
    model_b_latency_ms: float
    model_a_tokens: int
    model_b_tokens: int
    model_a_cost: float
    model_b_cost: float
    quality_score_a: float  # from automated eval
    quality_score_b: float

async def run_comparison(
    eval_set: list[dict],
    model_a_client,
    model_b_client,
    evaluator
) -> list[EvalResult]:
    results = []

    for example in eval_set:
        # Run both models in parallel
        result_a, result_b = await asyncio.gather(
            model_a_client.generate(example["input"]),
            model_b_client.generate(example["input"])
        )

        # Score both outputs
        score_a = await evaluator.score(
            input=example["input"],
            output=result_a.text,
            reference=example.get("expected")
        )
        score_b = await evaluator.score(
            input=example["input"],
            output=result_b.text,
            reference=example.get("expected")
        )

        results.append(EvalResult(
            input_text=example["input"],
            model_a_output=result_a.text,
            model_b_output=result_b.text,
            model_a_latency_ms=result_a.latency_ms,
            model_b_latency_ms=result_b.latency_ms,
            model_a_tokens=result_a.total_tokens,
            model_b_tokens=result_b.total_tokens,
            model_a_cost=result_a.cost,
            model_b_cost=result_b.cost,
            quality_score_a=score_a,
            quality_score_b=score_b
        ))

    return results
```

### Regression Detection Criteria

| Metric | Acceptable Regression | Action if Exceeded |
|---|---|---|
| Overall quality score | <2% drop | Investigate failing examples |
| Task completion rate | <1% drop | Block migration |
| Latency p50 | <20% increase | Acceptable if quality improves |
| Latency p99 | <50% increase | Investigate outliers |
| Cost per request | Must meet cost target | Primary metric for cost migration |
| Safety score | 0% regression allowed | Block migration |
| Structured output success | <1% drop | Fix schema handling |

---

## Staged Rollout Plan

### Phase 1: Shadow Mode (1-2 weeks)

| Step | Action | Success Criteria |
|---|---|---|
| 1 | Deploy new model alongside existing | Both models responding |
| 2 | Route 100% traffic to old model | No user impact |
| 3 | Mirror requests to new model (async) | New model responses captured |
| 4 | Compare outputs daily | Quality within 2% of baseline |
| 5 | Analyze edge cases | No new failure categories |

### Phase 2: Canary Release (1-2 weeks)

| Step | Traffic Split | Monitoring |
|---|---|---|
| 1 | 5% to new model | Error rate, latency, user feedback |
| 2 | 10% to new model | Same + quality scores |
| 3 | 25% to new model | Same + cost comparison |
| 4 | 50% to new model | Full metrics comparison |

### Phase 3: Full Migration (1 week)

| Step | Action | Rollback Criteria |
|---|---|---|
| 1 | Route 100% to new model | >1% quality drop → rollback |
| 2 | Keep old model warm for 1 week | >5% error rate increase → rollback |
| 3 | Decommission old model | After 1 week stable |

---

## Provider Abstraction Patterns

### LiteLLM Integration

```python
# Unified API across providers
from litellm import completion

# OpenAI
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# Anthropic (same API)
response = completion(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Hello"}]
)

# Gemini (same API)
response = completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Hello"}]
)

# With fallback
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    fallbacks=["claude-3-5-sonnet-20241022", "gemini/gemini-2.0-flash"]
)
```

### Custom Abstraction Layer

```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    async def generate(self, messages, **kwargs) -> LLMResponse:
        pass

    @abstractmethod
    async def generate_structured(self, messages, schema, **kwargs) -> dict:
        pass

class OpenAIClient(LLMClient):
    async def generate(self, messages, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, **kwargs
        )
        return self._normalize(response)

class AnthropicClient(LLMClient):
    async def generate(self, messages, **kwargs):
        system = self._extract_system(messages)
        user_messages = self._convert_messages(messages)
        response = await self.client.messages.create(
            model=self.model, system=system,
            messages=user_messages, **kwargs
        )
        return self._normalize(response)
```

### OpenRouter for Multi-Provider

```python
# Single API, multiple providers
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-..."
)

# Route to cheapest provider for a model
response = client.chat.completions.create(
    model="openai/gpt-4o",  # or "anthropic/claude-3.5-sonnet"
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers={
        "HTTP-Referer": "https://myapp.com",
        "X-Title": "My App"
    }
)
```

---

## Cost-Quality Tradeoff Analysis

### Migration Cost Calculator

| Factor | Old Model | New Model | Delta |
|---|---|---|---|
| Input token price ($/1M) | _fill_ | _fill_ | _calculate_ |
| Output token price ($/1M) | _fill_ | _fill_ | _calculate_ |
| Avg input tokens per request | _fill_ | _fill_ | _compare_ |
| Avg output tokens per request | _fill_ | _fill_ | _compare_ |
| Cost per request | _calculate_ | _calculate_ | _compare_ |
| Monthly request volume | _fill_ | _same_ | - |
| Monthly cost | _calculate_ | _calculate_ | _savings_ |
| Quality score | _fill_ | _fill_ | _compare_ |
| Migration engineering cost | - | _estimate_ | _one-time_ |
| Break-even point | - | - | _months_ |

### Common Migration Paths (January 2026)

| From | To | Typical Reason | Quality Impact | Cost Impact |
|---|---|---|---|---|
| GPT-4o | GPT-4o-mini | Cost | -5 to -10% | -80% |
| GPT-4o | Claude 3.5 Sonnet | Quality (coding, analysis) | +2 to +5% | Similar |
| GPT-4o | Gemini 2.0 Flash | Cost + speed | -3 to -7% | -70% |
| Claude 3 Opus | Claude 3.5 Sonnet | Cost + speed | Similar or better | -80% |
| Any API | Self-hosted Llama 3.1 70B | Cost at scale | -10 to -20% | -90% at volume |
| GPT-3.5 | GPT-4o-mini | Quality | +15 to +25% | Similar |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Big-bang migration (0% to 100%) | No safety net for quality regression | Staged rollout with canary |
| Migrating without eval dataset | Cannot measure quality impact | Build eval set BEFORE migration |
| Copy-pasting prompts unchanged | Different models need different prompts | Adapt prompts per model |
| Ignoring parameter differences | Temperature 1.0 means different things | Calibrate per provider |
| No rollback plan | Stuck if new model degrades | Keep old model warm for 1+ weeks |
| Optimizing only for cost | Quality drops cause user churn | Set quality floor before optimizing cost |
| Using one test query to evaluate | Not representative | Minimum 50 diverse examples |
| Tight coupling to provider API | Makes future migrations harder | Use abstraction layer |

---

## Cross-References

- `structured-output-patterns.md` — structured output differences by provider
- `multimodal-patterns.md` — vision/audio capability comparison
- `../ai-llm-inference/references/cost-optimization-patterns.md` — cost optimization after migration
- `../ai-llm-inference/references/multi-model-routing.md` — dynamic routing across providers
- `../ai-prompt-engineering/references/prompt-testing-ci-cd.md` — eval infrastructure for migration
