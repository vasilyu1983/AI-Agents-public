# ML/LLM FinOps and Cost Management

> Operational guide for managing costs across ML training, inference, and LLM workloads. Covers cost attribution, budget allocation, GPU optimization, token tracking, and ROI measurement. Focus on actionable cost reduction and governance, not theory.

**Freshness anchor:** January 2026 — AWS/GCP/Azure ML pricing as of Q1 2026, OpenAI/Anthropic/Cohere API pricing current

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

## Quick Reference: GPU Instance Cost Comparison (Q1 2026)

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

```python
import tiktoken
from datetime import datetime

class TokenCostTracker:
    """Track and attribute LLM API costs per request."""

    PRICING = {
        'gpt-4-turbo': {'input': 10.00 / 1_000_000, 'output': 30.00 / 1_000_000},
        'gpt-4o':      {'input': 2.50 / 1_000_000,  'output': 10.00 / 1_000_000},
        'gpt-4o-mini': {'input': 0.15 / 1_000_000,  'output': 0.60 / 1_000_000},
        'claude-3.5-sonnet': {'input': 3.00 / 1_000_000, 'output': 15.00 / 1_000_000},
        'claude-3-haiku':    {'input': 0.25 / 1_000_000, 'output': 1.25 / 1_000_000},
    }

    def log_usage(self, model, input_tokens, output_tokens, metadata=None):
        pricing = self.PRICING.get(model, {'input': 0, 'output': 0})
        cost = (input_tokens * pricing['input']) + (output_tokens * pricing['output'])

        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': round(cost, 6),
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
