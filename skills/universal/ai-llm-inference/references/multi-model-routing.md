# Multi-Model Routing

> Operational reference for routing LLM requests to different models based on complexity, cost, and latency requirements — classifier-based routing, cascade patterns, A/B routing, router architectures, and evaluation of routing effectiveness.

Use current provider docs, router docs, and eval results before recommending a specific routing stack or savings percentage.

---
## Table of Contents

- [Routing Strategy Decision Tree](#routing-strategy-decision-tree)
- [Routing Patterns](#routing-patterns)
- [Pattern 1: Rule-Based Routing](#pattern-1-rule-based-routing)
- [Pattern 2: Classifier-Based Routing](#pattern-2-classifier-based-routing)
- [Pattern 3: Cascade (Small → Large Fallback)](#pattern-3-cascade-small-→-large-fallback)
- [Escalation Confidence Signals](#escalation-confidence-signals)
- [Pattern 4: A/B Routing](#pattern-4-ab-routing)
- [Router Architecture Comparison](#router-architecture-comparison)
- [LiteLLM Router Configuration](#litellm-router-configuration)
- [Quality-Cost Tradeoff Framework](#quality-cost-tradeoff-framework)
- [Calculating Optimal Routing Split](#calculating-optimal-routing-split)
- [Routing Effectiveness Dashboard](#routing-effectiveness-dashboard)
- [Fallback and Resilience Patterns](#fallback-and-resilience-patterns)
- [Fallback Chain Configuration](#fallback-chain-configuration)
- [Health Check and Circuit Breaker](#health-check-and-circuit-breaker)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


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
│       │   │   ├── Small LLM classifier (small-tier model)
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

Model names in the code below are **tiers** (small, standard, reasoning, code), not products. Map each tier to a current model from the provider's model list, pin the exact model ID in config rather than code, and re-run the routing eval whenever a tier's model changes.

### Pattern 1: Rule-Based Routing

```
Use when: task types are known, limited categories, need zero latency overhead
```

```python
class RuleBasedRouter:
    RULES = {
        # Task type → model
        # Values are tier names; resolve each tier to a pinned model ID in config.
        "greeting": "small-tier",
        "faq": "small-tier",
        "classification": "small-tier",
        "extraction": "small-tier",
        "summarization": "standard-tier",
        "analysis": "standard-tier",
        "creative": "standard-tier",
        "reasoning": "reasoning-tier",
        "math": "reasoning-tier",
        "code": "code-tier",
    }

    def route(self, task_type: str, constraints: dict = None) -> str:
        model = self.RULES.get(task_type, "standard-tier")  # default to standard

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
        0: {"model": "small-tier", "label": "simple"},
        1: {"model": "standard-tier", "label": "standard"},
        2: {"model": "reasoning-tier", "label": "complex"},
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
            {"name": "small-tier", "cost_tier": 1},
            {"name": "standard-tier", "cost_tier": 2},
            {"name": "reasoning-tier", "cost_tier": 3},
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

### Escalation Confidence Signals

The `QualityChecker` above is one escalation gate; it is not the only kind. Pai (*Designing Large Language Model Applications*, O'Reilly 2025, ch. 13, pp. 631–633) catalogs the signals a cascade can use to decide "is this small model's answer good enough, or do I pay for the next tier?" Pick the signal that matches your model type — the wrong one silently escalates everything or nothing.

| Signal | Where it applies | Mechanism | Cost to compute |
|---|---|---|---|
| Calibrated output probabilities | Encoder-style models (e.g. BERT-family classifiers) | Use the output probability score directly as the confidence measure | Free — already in the forward pass |
| Self-consistency | Decoder models | Sample the model n times; high agreement across outputs reads as confidence, disagreement escalates | n× generation cost |
| Margin sampling | Decoder models | Generate the first token; take the probability gap between the most probable and second most probable token as the margin. Escalate below a threshold | ~1 token |

**Calibrated output probabilities.** Pai notes this works for encoder-only models where the output probability scores can serve as the confidence measure — and that it is *a group of well-calibrated models* that enables efficient routing. Calibration is the precondition, not a nicety: an uncalibrated score is a confident-looking number with no relationship to correctness, and a cascade thresholding on it will escalate the wrong requests.

**Self-consistency.** For decoder models Pai describes self-consistency as the popular method: generate multiple times, and if the outputs are mostly consistent with each other, treat the model as confident; if they are not, pass the input down the cascade. Cost is the obvious tension — sampling n times at the small tier can erase the savings the cascade exists to capture, so the n-sample small-model cost has to stay below the single-shot large-model cost for the pattern to pay.

**Margin sampling (Ramirez et al.).** Generate the first token and use the difference between the probability of the most probable token and the second most probable token as the margin. The assumption Pai states is directional: the higher the margin, the more confident the model; below a threshold, the input goes to the next model. The appeal relative to self-consistency is that it reads a single token rather than n full generations. No effect magnitudes are quoted here because the source states the mechanism and direction, not measured escalation rates — tune the threshold on your own eval set.

> **Do not ask the model to grade itself.** Pai's explicit warning: some works propose asking the LLM to state the confidence level of its output, and "this has not been proven to be effective yet. Beware of asking the LLM to verify its own work in any form!" (p. 632). A self-reported confidence score is the cheapest signal to implement and the one with the least evidence behind it — which is exactly why it keeps appearing in cascade implementations. Prefer a signal computed *from* the model's output distribution over one the model asserts about itself.

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
        # Example: {"control": {"model": "provider-a-standard", "weight": 0.8},
        #           "treatment": {"model": "provider-b-standard", "weight": 0.2}}

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
                "model": "<provider-a>/<small-tier-model-id>",
                "api_key": "sk-...",
            },
            "model_info": {"id": "small-tier-a"}
        },
        {
            "model_name": "general",
            "litellm_params": {
                "model": "<provider-b>/<small-tier-model-id>",
                "api_key": "sk-ant-...",
            },
            "model_info": {"id": "small-tier-b"}
        },
    ],
    routing_strategy="least-busy",  # or "simple-shuffle", "latency-based-routing"
    num_retries=2,
    fallbacks=[{"general": ["general-backup"]}],  # "general-backup" is another model_name group
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
    "provider_a": {
        "primary": "provider-a-standard",
        "fallbacks": [
            {"model": "provider-a-small", "condition": "rate_limit"},
            {"model": "provider-b-standard", "condition": "any_error"},
            {"model": "provider-c-small", "condition": "any_error"},
        ]
    },
    "provider_b": {
        "primary": "provider-b-standard",
        "fallbacks": [
            {"model": "provider-b-small", "condition": "rate_limit"},
            {"model": "provider-a-standard", "condition": "any_error"},
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
- `../../ai-mlops/references/model-provider-migration.md` — evaluating models for routing tiers
- `../../ai-prompt-engineering/references/core-patterns.md` — provider-specific output differences
- `../../ai-prompt-engineering/references/prompt-testing-ci-cd.md` — eval infrastructure for routing
