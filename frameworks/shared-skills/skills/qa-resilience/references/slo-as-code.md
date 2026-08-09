# SLO-as-Code

Declare SLOs and error budgets in version-controlled YAML so resilience targets, burn-rate alerts, and release gates are reviewed and tested like code — not built by hand in dashboards.

## Table of Contents

- [Why This Matters for Resilience Gates](#why-this-matters-for-resilience-gates)
- [Approach](#approach)
- [OpenSLO Specification](#openslo-specification)
- [Generators](#generators)
- [Integration Patterns](#integration-patterns)
- [Checklist](#checklist)
- [Anti-Patterns](#anti-patterns)
- [Related Resources](#related-resources)

## Why This Matters for Resilience Gates

The SKILL.md workflow step "Gate release on recovery evidence, SLO impact, and rollback path" requires machine-readable SLO targets. When SLOs live only in dashboards:

- targets drift between teams
- burn-rate alerts are inconsistent across services
- PR reviews cannot catch a threshold change
- release gates cannot reference a canonical spec

SLO-as-code closes this gap: the spec is the source of truth, and tooling generates the alert rules from it.

## Approach

1. Declare each SLO in a YAML spec committed alongside the service.
2. Generate Prometheus recording rules and multi-window burn-rate alerts from the spec.
3. Include SLO spec changes in PR review like any other contract change.
4. Gate chaos experiments and releases against burn-rate signals derived from the same spec.

## OpenSLO Specification

OpenSLO (openslo.com, github.com/OpenSLO/OpenSLO) is a vendor-agnostic open specification for expressing SLOs in YAML. It follows Kubernetes API conventions.

**Verified:** apiVersion `openslo/v1` is current at time of writing. A v2 is in progress (hedged — not yet released at time of writing).

Minimal structure:

```yaml
apiVersion: openslo/v1
kind: SLO
metadata:
  name: checkout-availability
  displayName: Checkout Availability
spec:
  service: checkout
  indicator:
    metadata:
      name: checkout-success-rate
    spec:
      ratioMetric:
        counter: true
        good:
          metricSource:
            type: Prometheus
            spec:
              query: sum(rate(http_requests_total{status!~"5.."}[5m]))
        total:
          metricSource:
            type: Prometheus
            spec:
              query: sum(rate(http_requests_total[5m]))
  timeWindow:
    - duration: 28d
      isRolling: true
  objectives:
    - displayName: Good availability
      target: 0.999
  alertPolicies: []
```

Validate with the `oslo` CLI: `oslo validate slos.yaml`.

## Generators

### Sloth (github.com/slok/sloth)

Takes a simple SLO spec and generates Prometheus SLI recording rules, multi-window multi-burn-rate alert rules, and a Grafana dashboard. Supports OpenSLO input. Supports Kubernetes via Prometheus Operator CRDs.

**Verified:** verify current release at the project repo. Actively maintained.

Typical usage:

```bash
# validate and generate from a Sloth spec
sloth generate -i slo.yaml

# validate only (CI gate)
sloth validate -i slo.yaml
```

### Pyrra (github.com/pyrra-dev/pyrra)

Kubernetes-native SLO management: watches SLO CRD resources, generates Prometheus recording rules, provides a UI showing error budgets and burn rates sorted by remaining budget.

**Verified:** verify current release at the project repo. Written in Go + TypeScript. Integrates with Prometheus and Thanos.

## Integration Patterns

### CI validation gate

Add an `oslo validate` or `sloth validate` step to CI. A PR that degrades a target below the agreed floor fails the check.

### Release gate

Block promotion if burn rate over a multi-window window (e.g. 1h / 6h) exceeds a threshold derived from the spec. The spec is the contract; the gate reads from it rather than a dashboard.

### Chaos experiment guard

Before starting a chaos run, read the current burn rate from the SLO spec's derived alerts. If already above threshold, abort. Record burn rate delta after the experiment as the primary success metric.

## Checklist

- [ ] Each service has an SLO spec file committed alongside the code
- [ ] Spec changes require PR review like API contract changes
- [ ] Alert rules are generated from the spec, not hand-authored
- [ ] Release gate reads burn rate; a breach blocks promotion
- [ ] Chaos experiments reference the same SLO targets for abort criteria
- [ ] `oslo validate` or equivalent runs in CI on every spec change

## Anti-Patterns

- SLOs defined only in the dashboard, not in code
- Burn-rate thresholds differing between the spec and the alert rule
- SLO targets set once and never reviewed against observed error budget consumption
- Generating rules locally and committing the generated output without the source spec

## Related Resources

- [resilience-checklists.md](resilience-checklists.md) — Observability for Resilience section
- [resilience-telemetry.md](resilience-telemetry.md) — Burn-rate alert signals
- [chaos-engineering-guide.md](chaos-engineering-guide.md) — Experiment guard and debrief checklist
