# Chaos Engineering & Resilience Testing

Proactive reliability validation through controlled failure injection. Use chaos engineering to discover weaknesses before they cause production incidents.

## Contents

- When to Use This Reference
- Core Principles
- Chaos Engineering Tools (2026)
- Experiment Categories
- CI/CD Integration
- Compliance: DORA & SOC 2
- Chaos Experiment Report
- Steady State Metrics
- Best Practices
- Quick Start Checklist
- Related References
- External Resources

---

## When to Use This Reference

- Validating system resilience before major releases
- Preparing for compliance audits (DORA, SOC 2)
- Building confidence in disaster recovery plans
- Testing failover mechanisms and circuit breakers
- Validating auto-scaling and self-healing infrastructure

---

## Core Principles

### Build-Measure-Learn Cycle

```text
1. STEADY STATE
   Define normal behavior metrics (latency, error rate, throughput)

2. HYPOTHESIS
   "The system will maintain <metric> within <threshold> when <failure>"

3. EXPERIMENT
   Inject controlled failure in staging/production

4. OBSERVE
   Measure deviation from steady state

5. LEARN
   Fix weaknesses, update runbooks, repeat
```

### Blast Radius Containment

| Environment | Blast Radius | Approval |
|-------------|--------------|----------|
| Development | Full chaos | None |
| Staging | Targeted services | Team lead |
| Production (canary) | 1-5% traffic | SRE + Engineering lead |
| Production (full) | Full system | VP Engineering + SRE |

**Rule:** Start small, expand gradually, always have a kill switch.

---

## Chaos Engineering Tools (2026)

### Tool Comparison

| Tool | Best For | Language | Kubernetes | Cloud |
|------|----------|----------|------------|-------|
| **Gremlin** | Enterprise, SaaS | Any | Yes | AWS, GCP, Azure |
| **LitmusChaos** | Kubernetes-native, OSS | Go | Yes | Any |
| **AWS FIS** | AWS workloads | Any | EKS | AWS only |
| **Chaos Monkey** | Netflix OSS ecosystem | Java | Limited | AWS |
| **Steadybit** | SRE workflows | Any | Yes | Multi-cloud |
| **Chaos Toolkit** | Extensible, CI/CD | Python | Yes | Any |

### LitmusChaos Example

```yaml
# litmus-experiment.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosExperiment
metadata:
  name: pod-delete
spec:
  definition:
    scope: Namespaced
    permissions:
      - apiGroups: [""]
        resources: ["pods"]
        verbs: ["delete", "list", "get"]
    image: litmuschaos/go-runner:latest
    args:
      - -c
      - ./experiments -name pod-delete
    env:
      - name: TOTAL_CHAOS_DURATION
        value: "30"
      - name: CHAOS_INTERVAL
        value: "10"
      - name: FORCE
        value: "false"
```

### Gremlin Attack Types

```text
Resource Attacks:
├── CPU              # Consume CPU cycles
├── Memory           # Consume memory
├── Disk             # Fill disk space
├── IO               # Slow disk I/O
└── Process Killer   # Kill specific processes

Network Attacks:
├── Latency          # Add network delay
├── Packet Loss      # Drop packets
├── Blackhole        # Drop all traffic
├── DNS              # DNS failures
└── Certificate      # TLS/SSL failures

State Attacks:
├── Shutdown         # Graceful shutdown
├── Time Travel      # Change system clock
└── Process Killer   # Kill by name/PID
```

---

## Experiment Categories

### 1. Infrastructure Failures

| Experiment | Validates | Example |
|------------|-----------|---------|
| **Instance termination** | Auto-scaling, failover | Kill 1 of 3 API servers |
| **Zone failure** | Multi-AZ deployment | Blackhole us-east-1a |
| **Disk exhaustion** | Alerting, cleanup jobs | Fill 95% disk |
| **Memory pressure** | OOM handling, graceful degradation | Consume 90% memory |

### 2. Network Failures

| Experiment | Validates | Example |
|------------|-----------|---------|
| **Latency injection** | Timeout handling, SLOs | Add 500ms to database calls |
| **Packet loss** | Retry logic, circuit breakers | 10% packet loss to cache |
| **DNS failure** | Fallback resolution | Block DNS for payment service |
| **Partition** | Split-brain handling | Isolate region from cluster |

### 3. Application Failures

| Experiment | Validates | Example |
|------------|-----------|---------|
| **Dependency failure** | Circuit breakers, fallbacks | Kill Redis |
| **Slow dependency** | Timeout configuration | Add 2s latency to auth service |
| **Error injection** | Error handling, logging | Return 500 from 10% of API calls |
| **Resource exhaustion** | Connection pooling, limits | Exhaust database connections |

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Chaos Testing
on:
  schedule:
    - cron: '0 2 * * 1-5'  # Weekday nights
  workflow_dispatch:
    inputs:
      experiment:
        description: 'Chaos experiment to run'
        required: true
        type: choice
        options:
          - pod-delete
          - network-latency
          - cpu-stress

jobs:
  chaos-test:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3

      - name: Install LitmusChaos
        run: |
          kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-v3.0.0.yaml
          kubectl wait --for=condition=Ready pods -l app=chaos-operator -n litmus

      - name: Run Chaos Experiment
        run: |
          kubectl apply -f chaos-experiments/${{ inputs.experiment }}.yaml
          kubectl wait --for=condition=ChaosResultVerdict=Pass \
            chaosresult/${{ inputs.experiment }}-result -n default --timeout=300s

      - name: Collect Results
        if: always()
        run: |
          kubectl get chaosresult -n default -o yaml > chaos-results.yaml

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: chaos-results
          path: chaos-results.yaml
```

### Game Day Automation

```bash
#!/bin/bash
# game-day-runner.sh

set -euo pipefail

EXPERIMENTS=(
  "pod-delete:api-service"
  "network-latency:database:500ms"
  "cpu-stress:worker:80%"
)

echo "Starting Game Day: $(date)"

for exp in "${EXPERIMENTS[@]}"; do
  IFS=':' read -r type target params <<< "$exp"

  echo "Running: $type on $target with $params"

  # Run experiment
  litmus run --experiment "$type" --target "$target" --params "$params"

  # Collect metrics during experiment
  prometheus-query "rate(http_requests_total{status=~'5..'}[1m])" > "metrics-$type.json"

  # Wait for recovery
  sleep 60

  # Verify steady state restored
  if ! verify-steady-state; then
    echo "ALERT: System did not recover from $type"
    exit 1
  fi
done

echo "Game Day Complete: All experiments passed"
```

---

## Compliance: DORA & SOC 2

### DORA (Digital Operational Resilience Act)

DORA requires financial entities to regularly test ICT resilience. Chaos engineering provides:

| DORA Requirement | Chaos Engineering Practice |
|------------------|---------------------------|
| ICT risk management | Proactive failure discovery |
| ICT-related incident management | Runbook validation |
| Digital operational resilience testing | Chaos experiments |
| Third-party risk management | Dependency failure testing |
| Information sharing | Post-mortem culture |

### SOC 2 Alignment

| SOC 2 Criteria | Chaos Engineering Evidence |
|----------------|---------------------------|
| Availability | Uptime during chaos experiments |
| Processing Integrity | Data consistency after failures |
| Confidentiality | Access controls during incidents |
| Security | Attack surface validation |

### Audit Documentation

```markdown
## Chaos Experiment Report

**Experiment ID:** CHX-2026-001
**Date:** 2026-01-18
**Environment:** Production (5% canary)
**Conducted By:** SRE Team

### Hypothesis
The payment service will maintain <100ms p99 latency when
the primary database fails over to replica.

### Experiment Details
- **Attack Type:** Database primary termination
- **Duration:** 5 minutes
- **Blast Radius:** 5% of production traffic
- **Kill Switch:** Immediate rollback via feature flag

### Results
| Metric | Baseline | During Experiment | Pass/Fail |
|--------|----------|-------------------|-----------|
| p99 Latency | 45ms | 120ms | FAIL |
| Error Rate | 0.01% | 0.8% | FAIL |
| Failover Time | N/A | 45s | N/A |

### Findings
1. Connection pool not warming on failover
2. DNS TTL too high (300s → should be 30s)
3. Health checks not detecting stale connections

### Remediation
- [ ] Implement connection pool pre-warming
- [ ] Reduce DNS TTL to 30s
- [ ] Add active health checks to connection pool

### Sign-off
- Engineering Lead: _____________ Date: _______
- SRE Lead: _____________ Date: _______
```

---

## Steady State Metrics

### Define Before Experimenting

```yaml
steady_state:
  metrics:
    - name: error_rate
      query: "sum(rate(http_requests_total{status=~'5..'}[5m])) / sum(rate(http_requests_total[5m]))"
      threshold: "< 0.01"  # 1%

    - name: p99_latency
      query: "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))"
      threshold: "< 0.2"  # 200ms

    - name: throughput
      query: "sum(rate(http_requests_total[5m]))"
      threshold: "> 1000"  # 1000 RPS

    - name: saturation
      query: "avg(container_memory_usage_bytes / container_spec_memory_limit_bytes)"
      threshold: "< 0.8"  # 80%
```

### SLO-Based Thresholds

| SLI | SLO | Chaos Threshold |
|-----|-----|-----------------|
| Availability | 99.9% | Error rate < 5% during experiment |
| Latency (p99) | < 200ms | < 500ms during experiment |
| Throughput | > 1000 RPS | > 800 RPS during experiment |

---

## Best Practices

### Do

- Start with read-only experiments (latency, not data corruption)
- Run experiments during business hours (team available)
- Have clear rollback procedures before starting
- Document hypotheses and results
- Share learnings across teams
- Automate recurring experiments in CI/CD

### Avoid

- Running in production without staging validation first
- Experiments without clear success criteria
- Chaos without observability (you won't know what happened)
- Skipping post-mortems after failures
- Running during incident response or high-traffic events

---

## Quick Start Checklist

- [ ] Define steady state metrics (error rate, latency, throughput)
- [ ] Choose chaos tool (LitmusChaos for K8s, Gremlin for enterprise)
- [ ] Start in development/staging environment
- [ ] Write first hypothesis: "System X will maintain Y when Z fails"
- [ ] Run experiment with minimal blast radius
- [ ] Document findings and remediation
- [ ] Schedule recurring experiments (weekly/monthly)
- [ ] Integrate with CI/CD for pre-release validation

---

## Related References

- [operational-playbook.md](operational-playbook.md) — Test pyramid and CI gates
- [../SKILL.md](../SKILL.md) — Main testing strategy overview
- [../../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md) — CI/CD and infrastructure
- [../../software-security-appsec/SKILL.md](../../software-security-appsec/SKILL.md) — Security testing

---

## External Resources

- [Gremlin Chaos Engineering](https://www.gremlin.com/chaos-engineering)
- [LitmusChaos](https://litmuschaos.io/)
- [AWS Fault Injection Simulator](https://aws.amazon.com/fis/)
- [Steadybit](https://steadybit.com/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
