# ML Cost Levers

The cost levers that exist only because the workload is machine learning. General cloud and AI cost management is owned by [ops-cost-optimization](../../ops-cost-optimization/SKILL.md):

| Need | Owner |
|------|-------|
| Commitments (Savings Plans, CUDs, reserved GPU), Kubernetes cost allocation, chargeback and showback | [cloud-commitment-and-k8s-cost-guide](../../ops-cost-optimization/references/cloud-commitment-and-k8s-cost-guide.md) |
| Budgets, alerts, anomaly detection, FOCUS-normalized billing data | [cost-monitoring-setup](../../ops-cost-optimization/references/cost-monitoring-setup.md) |
| LLM API cost levers, per-trace attribution, API vs self-host breakeven | [ai-api-cost-guide](../../ops-cost-optimization/references/ai-api-cost-guide.md) |
| Unit economics and ROI per product or model | [unit-economics-guide](../../ops-cost-optimization/references/unit-economics-guide.md) |
| Serving efficiency (batching, quantization, KV cache) | [ai-llm-inference](../../ai-llm-inference/SKILL.md) |

Prices and discounts change often and differ by contract: read them from the provider's pricing page or your billing export at decision time, never from a table in a skill.

## Contents

- [Tag Every ML Workload For Rollup](#tag-every-ml-workload-for-rollup)
- [Spot Training Needs Checkpoint-Resume](#spot-training-needs-checkpoint-resume)
- [Retraining Cadence Is A Cost Decision](#retraining-cadence-is-a-cost-decision)
- [Bound Experiment And Tuning Spend](#bound-experiment-and-tuning-spend)
- [Fill The GPU Before Buying A Bigger One](#fill-the-gpu-before-buying-a-bigger-one)
- [ML-Specific Cost Spikes](#ml-specific-cost-spikes)
- [Checklist](#checklist)

## Tag Every ML Workload For Rollup

Tag training jobs, tuning sweeps, batch scoring and serving with `team`, `model`, `model_version`, `environment` and `cost_center`, and put the same fields on every LLM API usage log. That is what lets ops-cost-optimization's chargeback roll cost up per model version (training plus serving) without manual reconciliation, and what lets you compare a model's cost with the value in its ROI review.

## Spot Training Needs Checkpoint-Resume

- Run interruptible training, tuning and offline scoring on spot or preemptible capacity only if the job can resume: handle the termination signal, write the checkpoint (model, optimizer, scheduler, data-loader position, RNG state) to durable storage, and test resume in CI. For synchronous serving, use Spot only when the fleet can tolerate interrupted instances and unavailable capacity; check the provider's [current interruption guidance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html) before choosing the capacity mix.
- Choose the checkpoint interval from two measured numbers: checkpoint write time C and mean time between reclaims M. A standard first-order choice (Young's approximation) is interval ≈ √(2·C·M). Example: C = 2 min, M = 6 h gives ≈ 38 min; overhead is about 10%, rising to about 18% at a 2-hour interval and 21% at 10 minutes.
- Re-measure M per region and instance type; reclaim rates change with market demand.

## Retraining Cadence Is A Cost Decision

- Retrain when the value of the accuracy you recover exceeds the retrain cost (compute, labelling, validation, rollout risk). Measure how error grows with model age in backtests, price that error, and pick the cadence where the next retrain pays for itself.
- Drift alone is not a reason to spend a training run; confirm it is above the noise floor and moves a performance proxy first ([drift-detection-guide](drift-detection-guide.md), [automated-retraining-patterns](automated-retraining-patterns.md)).
- Changing the embedding model means re-embedding the whole corpus: budget that as a project, not a routine job.

## Bound Experiment And Tuning Spend

- Give every hyperparameter sweep a budget (trials, GPU-hours) and an early-stopping pruner; an unbounded sweep can cause a large bill surprise.
- Log cost per run in experiment tracking next to the metric, so "better" is judged per unit of spend ([experiment-tracking-patterns](experiment-tracking-patterns.md)).
- Apply artifact lifecycle rules: keep promoted and audited runs, expire failed and superseded artifacts.

## Fill The GPU Before Buying A Bigger One

- Measure GPU utilization first. A data-loader-bound job wastes any GPU; fix loading (workers, prefetch, pinned memory) before resizing.
- Use mixed precision and gradient accumulation to fit a job on a smaller accelerator; right-size to the model rather than defaulting to the largest instance.
- For serving, evaluate batching and quantization against the quality gate before adding capacity; the saving is only real if the gate still passes.

## ML-Specific Cost Spikes

Hyperparameter search without a cap; a full-corpus re-embed; autoscaler stuck at maximum replicas after a traffic spike; a prompt or decoding bug that inflates output length; forgotten development GPUs. Route these to the anomaly alerts ops-cost-optimization sets up, with the ML tags above so the owner is obvious.

## Checklist

- [ ] Every training, tuning, scoring and serving workload tagged with team, model, model_version, environment, cost_center
- [ ] Spot jobs resume from checkpoints; interval set from measured write time and reclaim rate; resume tested
- [ ] Retraining cadence justified by measured error decay versus retrain cost
- [ ] Sweeps capped and pruned; cost logged per run
- [ ] GPU utilization checked before resizing; serving optimizations pass the quality gate
