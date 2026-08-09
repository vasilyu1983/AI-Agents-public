# ML/LLM FinOps and Cost Management

> Operational guide for managing costs across ML training, inference, and LLM workloads. Covers cost attribution, budget allocation, GPU optimization, token tracking, and ROI measurement. Focus on actionable cost reduction and governance, not theory.

**Freshness note:** Cloud GPU and API pricing move frequently. Verify current prices and SKU availability before making budgeting recommendations.

Use this when the user needs spend diagnosis, token/GPU budget controls, or ROI framing for AI operations.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [Decision Tree: Cost Optimization Priority](#decision-tree-cost-optimization-priority)
- [Quick Reference: GPU Instance Cost Comparison (Illustrative, Verify Current Pricing)](#quick-reference-gpu-instance-cost-comparison-illustrative-verify-current-pricing)
- [Operational Patterns](#operational-patterns)
- [Pattern 1: Cost Attribution and Tagging](#pattern-1-cost-attribution-and-tagging)
- [Mandatory tags for every ML resource](#mandatory-tags-for-every-ml-resource)
- [AWS example: enforce tagging via SCP](#aws-example-enforce-tagging-via-scp)
- [GCP example: enforce via organization policy](#gcp-example-enforce-via-organization-policy)
- [Azure example: enforce via Azure Policy](#azure-example-enforce-via-azure-policy)
- [Pattern 2: Training Cost Optimization](#pattern-2-training-cost-optimization)
- [Training script with automatic checkpointing for spot instances](#training-script-with-automatic-checkpointing-for-spot-instances)
- [Handle spot termination signal](#handle-spot-termination-signal)
- [Checkpoint every N minutes regardless](#checkpoint-every-n-minutes-regardless)
- [Pattern 3: LLM Token Cost Tracking](#pattern-3-llm-token-cost-tracking)
- [Pattern 4: Inference Cost Optimization](#pattern-4-inference-cost-optimization)
- [Autoscaling configuration (Kubernetes HPA example)](#autoscaling-configuration-kubernetes-hpa-example)
- [Pattern 5: Budget Allocation and Alerts](#pattern-5-budget-allocation-and-alerts)
- [Budget configuration](#budget-configuration)
- [Alert channels by severity](#alert-channels-by-severity)
- [Pattern 6: ROI Tracking for ML Projects](#pattern-6-roi-tracking-for-ml-projects)
- [ML Project ROI Template](#ml-project-roi-template)
- [Costs (Monthly)](#costs-monthly)
- [Value Generated (Monthly)](#value-generated-monthly)
- [ROI Calculation](#roi-calculation)
- [Cost Anomaly Detection](#cost-anomaly-detection)
- [Common cost spikes:](#common-cost-spikes)
- [- Forgotten dev instances (check env=dev resources weekly)](#forgotten-dev-instances-check-env=dev-resources-weekly)
- [- Hyperparameter search without budget limits](#hyperparameter-search-without-budget-limits)
- [- LLM prompt bugs generating huge outputs](#llm-prompt-bugs-generating-huge-outputs)
- [- Autoscaler stuck at max replicas](#autoscaler-stuck-at-max-replicas)
- [- Data pipeline reprocessing (re-embedding entire corpus)](#data-pipeline-reprocessing-re-embedding-entire-corpus)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

## Quick Navigation

- [Decision Tree: Cost Optimization Priority](#decision-tree-cost-optimization-priority)
- [Quick Reference: GPU Instance Cost Comparison](#quick-reference-gpu-instance-cost-comparison-illustrative-verify-current-pricing)
- [Operational Patterns](#operational-patterns)
- [ML Project ROI Template](#ml-project-roi-template)
- [Cost Anomaly Detection](#cost-anomaly-detection)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)

---

## Decision Tree: Cost Optimization Priority

```
START
│
├─ Where is most spend?
│   ├─ Training (GPU hours)
│   │   ├─ Spot/preemptible available?
│   │   │   ├─ YES → Spot instances + checkpointing (60-80% savings)
│   │   │   └─ NO  → Right-size GPU, reduce epochs, prune early
│   │   └─ Training >24 hours?
│   │       ├─ YES → Mixed precision, gradient accumulation, distributed
│   │       └─ NO  → Optimize data loading, batch size first
│   │
│   ├─ Inference (serving)
│   │   ├─ Latency requirement?
│   │   │   ├─ Real-time (<100ms) → GPU serving, optimize batch, autoscale
│   │   │   ├─ Near real-time (<1s) → CPU possible, smaller model, distillation
│   │   │   └─ Batch → Spot instances, queue-based, off-peak scheduling
│   │   └─ Traffic pattern?
│   │       ├─ Spiky → Aggressive autoscaling, scale-to-zero
│   │       └─ Steady → Reserved capacity (1-3 year commit)
│   │
│   ├─ LLM API calls
│   │   ├─ Token volume > 10M/month?
│   │   │   ├─ YES → Caching, prompt optimization, smaller model routing
│   │   │   └─ NO  → Monitor, optimize prompts
│   │   └─ Response caching viable?
│   │       ├─ YES → Semantic cache (50-80% savings on repeated queries)
│   │       └─ NO  → Prompt compression, model routing
│   │
│   └─ Storage (data + artifacts)
│       └─ Lifecycle policies, tiered storage, artifact cleanup
│
└─ No visibility yet?
    └─ Step 1: Instrument cost attribution → then optimize
```

---

## Quick Reference: GPU Instance Cost Comparison (Illustrative, Verify Current Pricing)

| Instance Type | GPU | On-Demand/hr | Spot/hr | Reserved/hr (1yr) | Best For |
|---|---|---|---|---|---|
| AWS p4d.24xlarge | 8x A100 | ~$32 | ~$10 | ~$20 | Large training |
| AWS g5.xlarge | 1x A10G | ~$1.00 | ~$0.35 | ~$0.63 | Inference |
| AWS p5.48xlarge | 8x H100 | ~$98 | ~$35 | ~$62 | LLM fine-tuning |
| GCP a2-highgpu-1g | 1x A100 | ~$3.67 | ~$1.10 | ~$2.30 | Training |
| GCP g2-standard-4 | 1x L4 | ~$0.70 | ~$0.21 | ~$0.44 | Inference |
| Azure NC24ads_A100 | 1x A100 | ~$3.67 | ~$1.10 | ~$2.20 | Training |

- **Rule of thumb:** Spot = 60-70% savings; Reserved (1yr) = 35-40% savings
- **Always check current pricing** — GPU prices change quarterly

---

## Operational Patterns

### Pattern 1: Cost Attribution and Tagging

- **Use when:** First step — you cannot optimize what you cannot measure
- **Implementation:**

```yaml
# Mandatory tags for every ML resource
tags:
  team: "ml-platform"
  project: "recommendation-engine"
  environment: "production"        # dev/staging/production
  model: "user-embeddings-v3"
  cost_center: "CC-4521"
  owner: "jane.doe@company.com"

# AWS example: enforce tagging via SCP
# GCP example: enforce via organization policy
# Azure example: enforce via Azure Policy
```

- **Attribution granularity:**

| Level | Tag | Example | Purpose |
|-------|-----|---------|---------|
| Team | `team` | ml-platform | Chargeback |
| Project | `project` | rec-engine | Budget tracking |
| Model | `model` | user-embed-v3 | Per-model ROI |
| Environment | `env` | production | Dev waste detection |
| Experiment | `experiment_id` | exp-2026-01-15 | Training cost per run |

### Pattern 2: Training Cost Optimization

- **Use when:** Training costs exceed budget or are growing
- **Checklist (in priority order):**

```
1. [ ] Spot/preemptible instances with checkpointing
       → Savings: 60-80%
       → Requirement: Checkpoint every 30 min

2. [ ] Mixed precision training (fp16/bf16)
       → Savings: 30-50% (faster + fits larger batch)
       → Code: torch.cuda.amp.autocast()

3. [ ] Right-size GPU (don't use A100 for fine-tuning small models)
       → Check GPU utilization: nvidia-smi
       → Target: >70% GPU utilization

4. [ ] Early stopping / pruning (Optuna MedianPruner)
       → Savings: 40-60% of wasted trials

5. [ ] Data loading optimization
       → Num workers, prefetch, pin_memory
       → GPU should never wait for data

6. [ ] Gradient accumulation instead of larger GPU
       → Effective batch size = micro_batch * accumulation_steps
       → Can use smaller (cheaper) GPU
```

- **Spot instance pattern:**

```python
# Training script with automatic checkpointing for spot instances
import signal
import torch

def save_checkpoint(model, optimizer, epoch, path):
    torch.save({
        'epoch': epoch,
        'model_state': model.state_dict(),
        'optimizer_state': optimizer.state_dict(),
    }, path)

# Handle spot termination signal
def signal_handler(signum, frame):
    save_checkpoint(model, optimizer, current_epoch, 's3://bucket/checkpoint.pt')
    raise SystemExit("Spot instance termination — checkpoint saved")

signal.signal(signal.SIGTERM, signal_handler)

# Checkpoint every N minutes regardless
CHECKPOINT_INTERVAL_MINUTES = 30
```

### Pattern 3: LLM Token Cost Tracking

- **Use when:** Using LLM APIs (OpenAI, Anthropic, Cohere, etc.)
- **Implementation:**

> **Pricing caveat:** LLM API prices change frequently and vary by tier, region, and negotiated contract. The hardcoded pricing table has been removed to avoid stale numbers. **Always verify current pricing at the provider before budgeting:**
> - OpenAI: https://openai.com/api/pricing/
> - Anthropic: https://www.anthropic.com/pricing (verify at provider; as of early 2026)
> - Google Gemini: https://ai.google.dev/pricing
> - Other providers: check their official pricing pages
>
> For **Claude 4 models** (Opus 4.7 / Sonnet 4.6 / Haiku 4.5): note that the tokenizer changed with Claude 4 — expect ~1.0–1.35× token count vs earlier models on equivalent prompts. Factor this into budget estimates.

```python
from datetime import datetime

class TokenCostTracker:
    """
    Track and attribute LLM API costs per request.

    IMPORTANT: Do not hardcode pricing here. Fetch current prices from
    your provider's pricing API or maintain a config file updated by the
    team. Hardcoded prices become stale within weeks.
    """

    def __init__(self, pricing_config: dict):
        """
        pricing_config: {'model_id': {'input_per_mtok': float, 'output_per_mtok': float}}
        Load from a versioned config file, not from code constants.
        Example: {'claude-sonnet-4-6': {'input_per_mtok': X, 'output_per_mtok': Y}}
        Verify current values at your provider before populating.
        """
        self.pricing = pricing_config

    def log_usage(self, model, input_tokens, output_tokens, metadata=None):
        p = self.pricing.get(model, {'input_per_mtok': 0, 'output_per_mtok': 0})
        cost = (input_tokens * p['input_per_mtok'] / 1_000_000 +
                output_tokens * p['output_per_mtok'] / 1_000_000)

        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': round(cost, 6),
            'pricing_config_version': metadata.get('pricing_version', 'unknown'),
            'metadata': metadata or {},
        }
        # Write to logging pipeline (BigQuery, Datadog, etc.)
        return record
```

- **Cost optimization levers for LLMs:**

| Lever | Savings | Effort | Tradeoff |
|-------|---------|--------|----------|
| Semantic caching | 50-80% for repeated queries | Medium | Staleness risk |
| Prompt compression | 20-40% on input tokens | Low | Slight quality loss |
| Model routing (small → large fallback) | 40-60% | Medium | Latency on fallback |
| Batch API (where available) | 50% | Low | Higher latency (24hr) |
| Response length limits | 10-30% | Low | May truncate useful output |
| Fine-tuned smaller model | 70-90% | High | Maintenance burden |

### Pattern 4: Inference Cost Optimization

- **Use when:** Serving costs dominate (production models)

```yaml
# Autoscaling configuration (Kubernetes HPA example)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1        # scale to zero with KEDA if possible
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: inference_queue_depth
        target:
          type: AverageValue
          averageValue: "5"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300    # avoid thrashing
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
```

- **Model optimization for serving:**

| Technique | Latency Reduction | Cost Reduction | Quality Impact |
|-----------|-------------------|----------------|----------------|
| Quantization (INT8) | 2-3x | 2-3x | < 1% accuracy loss |
| Distillation | 5-10x | 5-10x | 1-3% accuracy loss |
| Pruning | 2-4x | 2-4x | < 1% accuracy loss |
| ONNX Runtime | 1.5-2x | 1.5-2x | None |
| Batching requests | 2-5x throughput | 2-5x | Adds latency |

### Pattern 5: Budget Allocation and Alerts

- **Use when:** Operating any ML workload with budget constraints

```python
# Budget configuration
MONTHLY_BUDGETS = {
    'training': {
        'total_usd': 10000,
        'alert_threshold_pct': [50, 75, 90, 100],
        'hard_stop_pct': 120,
    },
    'inference': {
        'total_usd': 5000,
        'alert_threshold_pct': [75, 90, 100],
        'hard_stop_pct': 150,  # never stop serving
    },
    'llm_api': {
        'total_usd': 3000,
        'alert_threshold_pct': [50, 75, 90],
        'hard_stop_pct': 100,  # hard stop — costs can spike fast
    },
}

# Alert channels by severity
ALERT_ROUTING = {
    50: ['slack:#ml-costs'],
    75: ['slack:#ml-costs', 'email:ml-lead@company.com'],
    90: ['slack:#ml-costs', 'email:ml-lead@company.com', 'pagerduty:ml-oncall'],
    100: ['pagerduty:ml-oncall', 'email:finance@company.com'],
}
```

### Pattern 6: ROI Tracking for ML Projects

- **Use when:** Justifying ML spend to leadership

```markdown
## ML Project ROI Template

### Costs (Monthly)
| Item | Amount |
|------|--------|
| Training compute | $X |
| Inference serving | $X |
| LLM API calls | $X |
| Data storage | $X |
| Engineering time (loaded cost) | $X |
| **Total** | **$X** |

### Value Generated (Monthly)
| Metric | Before ML | After ML | Delta |
|--------|-----------|----------|-------|
| Revenue from recommendations | $X | $X | +$X |
| Fraud prevented | $X | $X | +$X |
| Support tickets deflected | X/month | X/month | -X ($Y saved) |

### ROI Calculation
- Monthly net value: $[value] - $[cost]
- Payback period: [months]
- Annual ROI: [percentage]
```

---

## Cost Anomaly Detection

```python
def detect_cost_anomaly(daily_costs, window=14, threshold=2.5):
    """Flag days where cost exceeds rolling average by threshold."""
    rolling_mean = daily_costs.rolling(window).mean()
    rolling_std = daily_costs.rolling(window).std()
    zscore = (daily_costs - rolling_mean) / (rolling_std + 0.01)
    anomalies = zscore > threshold
    return anomalies

# Common cost spikes:
# - Forgotten dev instances (check env=dev resources weekly)
# - Hyperparameter search without budget limits
# - LLM prompt bugs generating huge outputs
# - Autoscaler stuck at max replicas
# - Data pipeline reprocessing (re-embedding entire corpus)
```

---

## Pattern 7: Chargeback and Showback Per Team or Per Model

- **Use when:** Multiple teams share GPU clusters, LLM API budgets, or inference serving infrastructure
- **Chargeback**: teams are billed for their actual consumption (financial accountability)
- **Showback**: teams see their consumption but are not billed (visibility without friction)

### Implementation Steps

**1. Tag every resource** (see Pattern 1) — `team`, `model`, `environment`, `cost_center` are the minimum required tags.

**2. Build a cost rollup pipeline:**

```python
def build_cost_report(billing_data, period='month'):
    """
    Aggregate cloud + LLM API costs by team and model.
    Returns a DataFrame with columns: team, model, environment, cost_usd
    """
    df = billing_data.copy()

    # Normalize tags
    df['team'] = df['tags'].apply(lambda t: t.get('team', 'untagged'))
    df['model'] = df['tags'].apply(lambda t: t.get('model', 'untagged'))
    df['env'] = df['tags'].apply(lambda t: t.get('environment', 'untagged'))

    summary = df.groupby(['team', 'model', 'env'])['cost_usd'].sum().reset_index()
    summary = summary.sort_values('cost_usd', ascending=False)
    return summary

# Emit to Grafana, Metabase, or Datadog cost dashboard
# Schedule daily or weekly — daily for fast-burning LLM API budgets
```

**3. Per-model cost allocation for LLM APIs:**

Track token usage per model version per team. Each `log_usage` call (Pattern 3) should carry `team` and `model_version` metadata so the pipeline can roll up LLM API cost by team without manual reconciliation.

**4. Governance cadence:**
- Weekly: automated showback report per team (Slack or email digest)
- Monthly: chargeback reconciliation with finance
- Quarterly: per-model ROI review (cost vs. business value generated)

### Validation Checklist

- [ ] All resources tagged with `team`, `model`, `environment`, `cost_center`
- [ ] Untagged resource spend tracked and owned (alert if >5% of total)
- [ ] Weekly showback report automated
- [ ] Monthly chargeback reconciliation process defined
- [ ] Per-model LLM API cost visible in real-time dashboard

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No resource tagging | Cannot attribute costs to teams/projects | Enforce tags via cloud policy |
| Using on-demand for training | 2-3x more expensive than spot | Spot + checkpointing for all training |
| Over-provisioned GPU for inference | Paying for unused compute | Monitor GPU util, right-size |
| No LLM token tracking | API costs invisible until bill arrives | Log every API call with token counts |
| Same model for all queries | Expensive model for simple tasks | Route simple queries to cheaper model |
| No autoscaling for serving | Paying for idle capacity overnight/weekends | Implement HPA or scale-to-zero |
| Storing all experiment artifacts forever | Storage grows unbounded | Lifecycle policies, delete failed runs after 30 days |
| No cost anomaly alerting | Surprise bills | Daily cost checks with anomaly detection |
| Using A100 for fine-tuning small models | Over-provisioned | A10G or L4 sufficient for models < 3B params |
| Not using reserved instances for steady workloads | Missing guaranteed savings | Commit to 1yr RI for baseline load |

---

## Validation Checklist

- [ ] All ML resources tagged (team, project, model, environment)
- [ ] Cost dashboard operational with daily/weekly/monthly views
- [ ] Budget alerts configured at 50%, 75%, 90%, 100% thresholds
- [ ] Spot instances used for all training (with checkpointing)
- [ ] GPU utilization monitored (target >70%)
- [ ] LLM token costs tracked per model, per use case
- [ ] Autoscaling configured for inference endpoints
- [ ] Cost anomaly detection running daily
- [ ] ROI tracked for each ML project
- [ ] Monthly cost review meeting scheduled

---

## Cross-References

- `ai-mlops/references/experiment-tracking-patterns.md` — tracking cost per experiment
- `ai-mlops/references/automated-retraining-patterns.md` — cost-aware retraining schedules
- `ai-rag/references/rag-caching-patterns.md` — caching to reduce LLM API costs
- `ai-rag/references/embedding-model-guide.md` — embedding cost comparison
