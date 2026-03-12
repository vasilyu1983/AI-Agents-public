# Operational Patterns and Standards

Actionable patterns, checklists, and safety gates for platform engineering, GitOps, CI/CD, observability, and reliability.

---

## Platform Engineering Pattern
- **Self-Service Platform:**
 - [ ] Internal developer portal with service catalog
 - [ ] Golden paths for common workflows (deploy, scale, monitor)
 - [ ] Abstraction layer over Kubernetes complexity
 - [ ] Integrated monitoring, logging, tracing (Prometheus, Grafana, Jaeger)
 - [ ] Policy enforcement with OPA/Gatekeeper
- **Outcome:** Paved paths reduce toil, standardize security, and make delivery repeatable at scale

---

## GitOps Continuous Reconciliation
- **Pattern:**
 - Git repository is single source of truth for cluster state
 - Controllers (ArgoCD, FluxCD) continuously reconcile live vs. desired state
 - Automated drift detection and alerting
 - Rollback via git revert (auditable, version-controlled)
- **Checklist:**
 - [ ] All manifests in Git (no manual kubectl apply)
 - [ ] Drift detection enabled with alerts
 - [ ] RBAC limits manual cluster changes
 - [ ] GitOps controller monitors every 30-60s

---

## DevSecOps CI/CD Pipeline
- **Security-First Automation:**
 - [ ] SAST (static analysis) scans code for vulnerabilities
 - [ ] DAST (dynamic analysis) tests running application
 - [ ] SCA (software composition analysis) checks dependencies
 - [ ] Secrets detection prevents credential leaks
 - [ ] Container image signing with Cosign/Sigstore
 - [ ] SBOM generation (Syft) for supply chain visibility
- **Outcome:** Secure-by-default delivery with auditable artifacts and clear rollback paths

---

## eBPF-Based Observability
- **Kernel-Level Insights:**
 - Use Cilium + Hubble for service-to-service network visibility
 - eBPF agents provide sidecarless telemetry (no proxy overhead)
 - Capture HTTP, DNS, TCP metrics without code changes
 - Cross-cluster observability with centralized pipelines
- **Trade-offs:** Kernel compatibility, privilege boundaries, and careful rollout/testing are required

---

## Optional: AI/Automation (Incident Triage)

- **Correlation/summarization**: group related alerts and produce an incident brief.
- **Runbook routing**: suggest the top 1-3 runbooks based on service + symptom tags.
- **Anomaly detection**: detect metric shifts, but page only on SLO impact.

### Bounded Claims

- Automation can be wrong; treat as hypothesis generation.
- Do not auto-remediate from summaries without explicit approval.
- Invest in alert hygiene first (dedupe, routing, SLO-based paging).

---

## IaC Safety Pattern
- **Checklist:**
 - [ ] Code in version control with branch protection
 - [ ] PR review + automated testing before apply
 - [ ] Terraform plan validated and approved
 - [ ] State is remote (S3, GCS) and locked (DynamoDB, GCS)
 - [ ] Secrets stored via vault/provider (never hardcoded)
 - [ ] Policy as code enforced (OPA, Sentinel, Checkov)

---

## Progressive Deployment (Blue-Green & Canary)
- **Pattern:**
 - Deploy new version in parallel to old version
 - Route small % of traffic to canary (5-10%)
 - Monitor golden signals (latency, errors, saturation, traffic)
 - Automated rollback if error rate >1% or latency >P99 threshold
 - Gradual promotion: 5% → 25% → 50% → 100%
- **Kubernetes:** Use Flagger with Istio/Linkerd for automated canary analysis

---

## SLO/SLI Operational Pattern
- **SLO Example (Modern Standards):**
 - API latency <500ms for 99.9% of requests
 - Uptime 99.95% (21.6 min downtime/month)
 - Error rate <0.1%
 - Time to recovery (MTTR) <15 minutes
- **Error Budget Policy:**
 - [ ] SLI metrics defined and observable (Prometheus queries)
 - [ ] SLO error budgets calculated and tracked
 - [ ] Alerting rules fire when error budget burn rate is high
 - [ ] Feature freeze if error budget exhausted

---

## Kubernetes Rollout Verification
- **Checklist:**
 - [ ] `kubectl rollout status deployment/app` is green
 - [ ] Liveness/readiness probes passing for all replicas
 - [ ] No crash loops or image pull errors in logs
 - [ ] Pre-deployment smoke tests passed
 - [ ] Post-deployment health checks validated
 - [ ] Metrics show no latency regression or error spike

---

## Continuous Improvement (DevOps Handbook)
- **Flow/Feedback/Experimentation:**
 - [ ] Map value streams and remove handoffs/WIP (limit work per lane)
 - [ ] Build fast feedback loops (automated tests, deployment health, customer signals)
 - [ ] Run blameless post-incident/retro with one concrete experiment per cycle
 - [ ] Make work visible (boards, DORA metrics) and pair changes with hypothesis + success metric
- **Outcome:** Higher deployment throughput with lower change failure via small batch, fast learn cycles

---

## IaC Testing & Drift Control (Infrastructure as Code 2nd Ed.)
- **Pre-merge:**
 - [ ] Unit/contract tests for modules (Terratest/Kitchen)
 - [ ] Policy-as-code tests (OPA/Checkov/Sentinel) gated in CI
 - [ ] `terraform plan` diff artifact stored + reviewed
- **Post-merge:**
 - [ ] Drift detection scheduled (terraform plan/infra controller) with alerting
 - [ ] Sandboxed applies for module upgrades before prod promotion
 - [ ] Break-glass path documented, audited, and expired after use

---

## Data-Intensive & Reliability Patterns (DIA + DBRE)
- **Backpressure & Idempotency:**
 - [ ] Producers respect consumer lag (rate limits, bounded retries, DLQ)
 - [ ] Idempotent consumers (dedupe keys, exactly-once not assumed)
- **Schema Evolution:**
 - [ ] Contracts enforced (protobuf/Avro/JSON schema) with compatibility tests in CI
 - [ ] Versioned topics/APIs; rolling upgrades with dual-write/dual-read when needed
- **Resilience & DR:**
 - [ ] RPO/RTO defined per service with tested restore drills
 - [ ] Capacity models for hot paths; load-shed and backoff patterns in place
 - [ ] Observability covers ingestion lag, retry storms, and storage saturation

---

This resource consolidates operational detail referenced by `SKILL.md`.
