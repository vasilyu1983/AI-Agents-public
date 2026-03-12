# Multi-Model Routing

> Operational reference for routing LLM requests to different models based on complexity, cost, and latency requirements — classifier-based routing, cascade patterns, A/B routing, router architectures, and evaluation of routing effectiveness.

**Freshness anchor:** January 2026 — covers Martian router, OpenRouter, RouteLLM, Unify.ai, and custom routing with LiteLLM.

---

## Routing Strategy Decision Tree

```
Incoming LLM request
│
├── Is the task type known at request time?
│   ├── YES → Rule-Based Routing
│   │   ├── Classification/extraction → Small model
│   │   ├── Summarization → Medium model
│   │   ├── Complex reasoning → Large model
│   │   └── Code generation → Code-specialized model
│   │
│   └── NO → Need to classify first
│       │
│       ├── Can you classify cheaply? (<1ms overhead)
│       │   ├── YES → Classifier-Based Routing
│       │   │   ├── Lightweight classifier (regex, keyword, logistic regression)
│       │   │   ├── Small LLM classifier (GPT-4o-mini)
│       │   │   └── Embedding similarity to task clusters
│       │   │
│       │   └── NO → Cascade Pattern
│       │       ├── Try small model first
│       │       ├── Check confidence/quality
│       │       └── Escalate to larger model if needed
│       │
│       └── Is latency critical?
│           ├── YES → Route to fastest model that meets quality bar
│           └── NO → Route to cheapest model that meets quality bar
│
├── Do you need guaranteed quality?
│   ├── YES → Always use best model (no routing)
│   └── NO → Routing can save 40-70% cost
│
└── Are you A/B testing models?
    ├── YES → Percentage-based routing with eval
    └── NO → Deterministic routing
```

---

## Routing Patterns

### Pattern 1: Rule-Based Routing

```
Use when: task types are known, limited categories, need zero latency overhead
```

```python
class RuleBasedRouter:
    RULES = {
        # Task type → model
        "greeting": "gpt-4o-mini",
        "faq": "gpt-4o-mini",
        "classification": "gpt-4o-mini",
        "extraction": "gpt-4o-mini",
        "summarization": "gpt-4o",
        "analysis": "gpt-4o",
        "creative": "gpt-4o",
        "reasoning": "o3-mini",
        "math": "o3-mini",
        "code": "claude-3-5-sonnet-20241022",
    }

    def route(self, task_type: str, constraints: dict = None) -> str:
        model = self.RULES.get(task_type, "gpt-4o")  # default to standard

        # Apply constraints
        if constraints:
            if constraints.get("max_cost_per_request", float("inf")) < 0.01:
                model = self._downgrade(model)
            if constraints.get("max_latency_ms", float("inf")) < 1000:
                model = self._fastest_alternative(model)

        return model
```

### Pattern 2: Classifier-Based Routing

```
Use when: task types are NOT known upfront, need dynamic classification
Overhead: 5-50ms for lightweight classifier, 200-500ms for LLM classifier
```

```python
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer

class ClassifierRouter:
    """Classify request complexity, route to appropriate model."""

    COMPLEXITY_TIERS = {
        0: {"model": "gpt-4o-mini", "label": "simple"},
        1: {"model": "gpt-4o", "label": "standard"},
        2: {"model": "o3-mini", "label": "complex"},
    }

    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.classifier = LogisticRegression()

    def train(self, labeled_examples: list[dict]):
        """Train on historical requests with labels."""
        texts = [ex["text"] for ex in labeled_examples]
        labels = [ex["complexity_tier"] for ex in labeled_examples]

        embeddings = self.embedder.encode(texts)
        self.classifier.fit(embeddings, labels)

    def route(self, request: str) -> dict:
        embedding = self.embedder.encode([request])
        tier = self.classifier.predict(embedding)[0]
        confidence = max(self.classifier.predict_proba(embedding)[0])

        result = self.COMPLEXITY_TIERS[tier].copy()
        result["confidence"] = confidence

        # Low confidence → route to standard model as safety net
        if confidence < 0.7:
            result["model"] = self.COMPLEXITY_TIERS[1]["model"]
            result["reason"] = "low_confidence_fallback"

        return result
```

### Pattern 3: Cascade (Small → Large Fallback)

```
Use when: want to minimize cost while maintaining quality, latency tolerance exists
Overhead: 1-2x latency on escalated requests, net cost savings 40-60%
```

```python
class CascadeRouter:
    """Try small model first, escalate to larger if quality is insufficient."""

    def __init__(self):
        self.models = [
            {"name": "gpt-4o-mini", "cost_tier": 1},
            {"name": "gpt-4o", "cost_tier": 2},
            {"name": "o3-mini", "cost_tier": 3},
        ]
        self.quality_checker = QualityChecker()

    async def generate(self, messages: list, quality_threshold: float = 0.8) -> dict:
        for i, model in enumerate(self.models):
            response = await llm_call(model["name"], messages)

            # Last model: return regardless
            if i == len(self.models) - 1:
                return {"response": response, "model": model["name"], "escalations": i}

            # Check quality
            quality_score = await self.quality_checker.score(
                input_messages=messages,
                output=response.text
            )

            if quality_score >= quality_threshold:
                return {
                    "response": response,
                    "model": model["name"],
                    "escalations": i,
                    "quality_score": quality_score
                }

            # Escalate to next model
            continue

class QualityChecker:
    """Lightweight quality check for cascade decisions."""

    async def score(self, input_messages, output) -> float:
        checks = {
            "not_empty": len(output.strip()) > 10,
            "not_refusal": not output.startswith("I cannot"),
            "reasonable_length": 50 < len(output) < 10000,
            "no_repetition": self._check_no_repetition(output),
            "addresses_question": await self._relevance_check(input_messages, output),
        }
        return sum(checks.values()) / len(checks)
```

### Pattern 4: A/B Routing

```
Use when: evaluating new models before full migration, measuring quality impact
```

```python
import hashlib
import random

class ABRouter:
    """Route traffic between models for evaluation."""

    def __init__(self, config: dict):
        self.config = config
        # Example: {"control": {"model": "gpt-4o", "weight": 0.8},
        #           "treatment": {"model": "claude-3-5-sonnet", "weight": 0.2}}

    def route(self, session_id: str) -> dict:
        # Deterministic routing based on session (same user always gets same model)
        hash_value = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
        normalized = (hash_value % 1000) / 1000

        cumulative = 0
        for variant_name, variant_config in self.config.items():
            cumulative += variant_config["weight"]
            if normalized < cumulative:
                return {
                    "model": variant_config["model"],
                    "variant": variant_name,
                    "session_id": session_id
                }

        # Fallback
        return {"model": list(self.config.values())[0]["model"], "variant": "control"}
```

---

## Router Architecture Comparison

| Router | Type | How It Works | Latency Overhead | Cost |
|---|---|---|---|---|
| OpenRouter | Proxy | Pass-through to cheapest provider per model | <50ms | Markup on token price |
| Martian | Smart proxy | ML-based routing across providers | <100ms | Usage-based |
| RouteLLM | Library | Open-source classifier routing | <10ms (local) | Self-hosted |
| Unify.ai | Proxy | Optimizes for cost/quality/latency | <50ms | Usage-based |
| LiteLLM | Library | Abstraction + fallback + load balancing | <5ms | Self-hosted |
| Custom | Application | Your own routing logic | Variable | Development cost |

### LiteLLM Router Configuration

```python
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "general",
            "litellm_params": {
                "model": "gpt-4o-mini",
                "api_key": "sk-...",
            },
            "model_info": {"id": "gpt-4o-mini-1"}
        },
        {
            "model_name": "general",
            "litellm_params": {
                "model": "claude-3-haiku-20240307",
                "api_key": "sk-ant-...",
            },
            "model_info": {"id": "claude-haiku-1"}
        },
    ],
    routing_strategy="least-busy",  # or "simple-shuffle", "latency-based-routing"
    num_retries=2,
    fallbacks=[{"gpt-4o-mini": ["claude-3-haiku-20240307"]}],
    set_verbose=False
)

response = await router.acompletion(
    model="general",
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## Quality-Cost Tradeoff Framework

### Calculating Optimal Routing Split

| Metric | How to Measure | Target |
|---|---|---|
| Quality score (per model) | Eval set + automated scoring | Defined per use case |
| Cost per request (per model) | Track actual token usage + pricing | Minimize total |
| Latency p50 (per model) | Request timing | Within SLA |
| Routing accuracy | Correct model for task complexity | >85% |
| Escalation rate (cascade) | % of requests needing fallback | <30% |
| Overall quality | Weighted average across all routes | Within 2% of best model |
| Overall cost savings | Compared to always using best model | Target: 40-60% |

### Routing Effectiveness Dashboard

```
Track these metrics daily:

1. Traffic distribution by model
   - % of requests per model
   - Trend over time (is routing stable?)

2. Quality by route
   - Eval score per model tier
   - Failure rate per model tier

3. Cost by route
   - $/request per model tier
   - Total cost vs "all-best-model" counterfactual

4. Escalation metrics (cascade only)
   - Escalation rate
   - Quality of escalated vs non-escalated
   - Latency impact of escalation

5. Routing decision quality
   - Were requests correctly classified?
   - Sample review of routing decisions
```

---

## Fallback and Resilience Patterns

### Fallback Chain Configuration

```python
FALLBACK_CHAINS = {
    "openai": {
        "primary": "gpt-4o",
        "fallbacks": [
            {"model": "gpt-4o-mini", "condition": "rate_limit"},
            {"model": "claude-3-5-sonnet-20241022", "condition": "any_error"},
            {"model": "gemini-2.0-flash", "condition": "any_error"},
        ]
    },
    "anthropic": {
        "primary": "claude-3-5-sonnet-20241022",
        "fallbacks": [
            {"model": "claude-3-haiku-20240307", "condition": "rate_limit"},
            {"model": "gpt-4o", "condition": "any_error"},
        ]
    }
}
```

### Health Check and Circuit Breaker

| State | Behavior | Transition |
|---|---|---|
| CLOSED (healthy) | Route normally | 5 errors in 60s → OPEN |
| OPEN (unhealthy) | Skip this model, use fallback | After 30s → HALF-OPEN |
| HALF-OPEN (testing) | Send 10% of traffic | 3 successes → CLOSED, 1 error → OPEN |

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Routing without evaluation data | Cannot verify quality by route | Build eval set before implementing routing |
| Over-complex classifier | Routing overhead > cost savings | Start with rules, add ML only if needed |
| No fallback chain | Single provider outage = total outage | Always have 2+ providers configured |
| Cascade with no quality check | Small model failures pass through | Implement quality gate between levels |
| Routing by prompt length only | Long prompts can be simple, short can be complex | Use task type or embedding-based classification |
| Static routing weights | Cannot adapt to model updates or price changes | Review and adjust monthly |
| No monitoring of routing decisions | Drift goes undetected | Dashboard + weekly review |
| Routing to too many models | Operational complexity, hard to debug | Limit to 3-4 models max |

---

## Cross-References

- `cost-optimization-patterns.md` — cost strategies that complement routing
- `streaming-patterns.md` — streaming across routed models
- `../ai-llm/references/model-migration-guide.md` — evaluating models for routing tiers
- `../ai-llm/references/structured-output-patterns.md` — provider-specific output differences
- `../ai-prompt-engineering/references/prompt-testing-ci-cd.md` — eval infrastructure for routing
