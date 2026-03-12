# Runbook Testing

Systematic approaches to testing operational runbooks for accuracy, completeness, and incident readiness. Ensures runbooks work when needed most.

## Contents

- [Runbook Anatomy](#runbook-anatomy)
- [Dry-Run Testing Patterns](#dry-run-testing-patterns)
- [Automated Runbook Execution](#automated-runbook-execution)
- [Runbook-as-Code Patterns](#runbook-as-code-patterns)
- [Incident Simulation Testing](#incident-simulation-testing)
- [Time-to-Resolution Benchmarking](#time-to-resolution-benchmarking)
- [Common Runbook Failures](#common-runbook-failures)
- [Review Cadence](#review-cadence)
- [Runbook Coverage Matrix](#runbook-coverage-matrix)
- [Related Resources](#related-resources)

---

## Runbook Anatomy

Every production-ready runbook must contain these sections. Missing any of them is a test failure.

### Required Sections

```markdown
# Runbook: [Service] - [Failure Mode]

## Trigger
- Alert name: `HighErrorRate_OrderService`
- Threshold: Error rate > 5% for 5 minutes
- Dashboard: [link to Grafana dashboard]
- PagerDuty service: order-service-oncall

## Prerequisites
- VPN access to production network
- kubectl configured for prod cluster
- Access to AWS console (IAM role: oncall-engineer)
- Read access to Datadog logs

## Diagnosis Steps
1. Check error rate dashboard: [link]
2. Check recent deployments: `kubectl rollout history deployment/order-service -n prod`
3. Check dependent service health: [link to dependency dashboard]
4. Check database connection pool: [link to metrics]

## Resolution Steps
1. If caused by bad deployment:
   `kubectl rollout undo deployment/order-service -n prod`
2. If caused by database saturation:
   `kubectl scale deployment/order-service --replicas=2 -n prod`
3. If caused by external dependency:
   Enable circuit breaker: [link to feature flag]

## Verification
- [ ] Error rate returned below 1% within 10 minutes
- [ ] No customer-facing errors in last 5 minutes
- [ ] All health checks passing: `curl https://api.example.com/health`

## Rollback
- Revert feature flag: [link]
- Rollback deployment: `kubectl rollout undo deployment/order-service -n prod`
- Restore database snapshot: [link to procedure]

## Escalation
- L2: @platform-team (Slack) / PagerDuty escalation policy
- L3: @database-team for DB-related issues
- Management: @engineering-manager if customer impact > 30 minutes
```

### Runbook Section Validation Checklist

| Section | Required | Validation Criteria |
|---------|----------|-------------------|
| Trigger | Yes | Alert name matches PagerDuty config |
| Prerequisites | Yes | All tools/access listed and testable |
| Diagnosis | Yes | Steps are numbered and sequential |
| Resolution | Yes | Commands are copy-pasteable |
| Verification | Yes | Success criteria are measurable |
| Rollback | Yes | Rollback tested independently |
| Escalation | Yes | Contacts are current (verified quarterly) |
| Last Tested | Yes | Date within review cadence window |
| Owner | Yes | Named individual or team |

---

## Dry-Run Testing Patterns

Dry-run testing validates that runbook steps are accurate without causing production impact.

### Manual Dry-Run Protocol

```markdown
## Dry-Run Test Report

**Runbook**: Order Service High Error Rate
**Tester**: [name]
**Environment**: staging
**Date**: 2026-01-15

### Pre-Flight
- [ ] Staging environment matches prod topology
- [ ] Test user credentials work
- [ ] All prerequisite tools installed and accessible

### Step-by-Step Results

| Step | Command / Action | Expected | Actual | Pass? |
|------|-----------------|----------|--------|-------|
| 1 | Check dashboard link | Dashboard loads | Dashboard loads | PASS |
| 2 | `kubectl rollout history...` | Shows deployment history | Shows history | PASS |
| 3 | Check dependency dashboard | Dashboard loads | 404 - link stale | FAIL |
| 4 | Rollback command | Rolls back to previous | Rolls back OK | PASS |

### Issues Found
- Step 3: Dashboard URL changed after Grafana migration
- Step 5: Verification curl uses wrong hostname

### Remediation
- Updated dashboard link to new Grafana URL
- Fixed verification hostname
```

### Automated Dry-Run Script

```bash
#!/bin/bash
# dry-run-runbook.sh: Validate runbook commands without executing destructive actions

set -euo pipefail

RUNBOOK_FILE="$1"
ENVIRONMENT="${2:-staging}"
RESULTS_FILE="dry-run-results-$(date +%Y%m%d-%H%M%S).md"

echo "# Dry-Run Results: $(basename "$RUNBOOK_FILE")" > "$RESULTS_FILE"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RESULTS_FILE"
echo "Environment: $ENVIRONMENT" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Extract and validate URLs
echo "## URL Validation" >> "$RESULTS_FILE"
grep -oE 'https?://[^ )]+' "$RUNBOOK_FILE" | while read -r url; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "TIMEOUT")
    if [[ "$status" == "200" || "$status" == "301" || "$status" == "302" ]]; then
        echo "- [PASS] $url ($status)" >> "$RESULTS_FILE"
    else
        echo "- [FAIL] $url ($status)" >> "$RESULTS_FILE"
    fi
done

# Validate kubectl contexts exist
echo "" >> "$RESULTS_FILE"
echo "## kubectl Validation" >> "$RESULTS_FILE"
grep -oE 'kubectl [a-z]+ [^ ]+' "$RUNBOOK_FILE" | head -5 | while read -r cmd; do
    # Dry-run kubectl commands
    dry_cmd="${cmd} --dry-run=client"
    if eval "$dry_cmd" 2>/dev/null; then
        echo "- [PASS] $cmd" >> "$RESULTS_FILE"
    else
        echo "- [FAIL] $cmd (dry-run failed)" >> "$RESULTS_FILE"
    fi
done

echo ""
echo "Results written to $RESULTS_FILE"
```

---

## Automated Runbook Execution

### Rundeck

Rundeck turns runbooks into executable workflows with audit trails and approval gates.

```yaml
# rundeck-job.yaml
- project: incident-response
  loglevel: INFO
  sequence:
    keepgoing: false
    strategy: node-first
    commands:
      - description: "Check service health"
        exec: curl -sf https://api.example.com/health || echo "UNHEALTHY"

      - description: "Check error rate"
        script: |
          ERROR_RATE=$(curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_errors_total[5m])' \
            | jq '.data.result[0].value[1]')
          echo "Current error rate: $ERROR_RATE"
          if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
            echo "ERROR RATE HIGH - proceeding with remediation"
          else
            echo "Error rate normal - no action needed"
            exit 0
          fi

      - description: "Rollback deployment (requires approval)"
        exec: kubectl rollout undo deployment/order-service -n prod
        plugins:
          approval:
            type: manual
            approvers: oncall-leads

      - description: "Verify recovery"
        script: |
          for i in $(seq 1 12); do
            HEALTH=$(curl -sf https://api.example.com/health | jq -r '.status')
            if [ "$HEALTH" = "ok" ]; then
              echo "Service recovered after $((i * 10)) seconds"
              exit 0
            fi
            sleep 10
          done
          echo "Service did not recover within 2 minutes"
          exit 1
```

### Ansible Playbook

```yaml
# runbook-high-error-rate.yaml
---
- name: "Runbook: High Error Rate Remediation"
  hosts: localhost
  gather_facts: false
  vars:
    namespace: prod
    service: order-service
    error_threshold: 0.05
    slack_channel: "#incidents"

  tasks:
    - name: Check current error rate
      uri:
        url: "http://prometheus:9090/api/v1/query"
        body_format: form-urlencoded
        body:
          query: "rate(http_errors_total{service='{{ service }}'}[5m])"
      register: error_rate_response

    - name: Parse error rate
      set_fact:
        current_error_rate: "{{ error_rate_response.json.data.result[0].value[1] | float }}"

    - name: Notify Slack - investigation started
      community.general.slack:
        token: "{{ lookup('env', 'SLACK_TOKEN') }}"
        channel: "{{ slack_channel }}"
        msg: "Runbook triggered: {{ service }} error rate at {{ current_error_rate }}"

    - name: Check recent deployments
      kubernetes.core.k8s_info:
        kind: ReplicaSet
        namespace: "{{ namespace }}"
        label_selectors:
          - "app={{ service }}"
      register: replicasets

    - name: Rollback if recent deployment
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: "{{ service }}"
            namespace: "{{ namespace }}"
            annotations:
              kubernetes.io/change-cause: "Runbook rollback - high error rate"
      when: current_error_rate | float > error_threshold

    - name: Wait for rollback to complete
      kubernetes.core.k8s_info:
        kind: Deployment
        name: "{{ service }}"
        namespace: "{{ namespace }}"
      register: deployment
      until: deployment.resources[0].status.readyReplicas == deployment.resources[0].status.replicas
      retries: 12
      delay: 10
```

---

## Runbook-as-Code Patterns

Store runbooks as executable code alongside the services they support.

### Directory Structure

```
services/
  order-service/
    src/
    runbooks/
      high-error-rate.yaml       # Ansible playbook
      database-failover.yaml
      scale-up.yaml
      README.md                  # Index of all runbooks
    alerts/
      high-error-rate.yaml       # Prometheus alert rule
    tests/
      runbook_test.py            # Runbook dry-run tests
```

### Runbook Test Suite

```python
"""
Test suite for validating runbook correctness.
Run in CI on every change to runbooks/ directory.
"""
import yaml
import subprocess
import pytest
import requests
from pathlib import Path

RUNBOOK_DIR = Path("runbooks/")

def get_all_runbooks():
    return list(RUNBOOK_DIR.glob("*.yaml"))

@pytest.mark.parametrize("runbook_path", get_all_runbooks())
def test_runbook_has_required_sections(runbook_path):
    """Every runbook must have trigger, steps, verification, rollback."""
    with open(runbook_path) as f:
        content = f.read()

    required_sections = ["trigger", "verification", "rollback", "escalation"]
    for section in required_sections:
        assert section.lower() in content.lower(), (
            f"Runbook {runbook_path.name} missing required section: {section}"
        )

@pytest.mark.parametrize("runbook_path", get_all_runbooks())
def test_runbook_urls_are_valid(runbook_path):
    """All URLs in runbooks must return 2xx or 3xx."""
    with open(runbook_path) as f:
        content = f.read()

    import re
    urls = re.findall(r'https?://[^\s\'"]+', content)
    for url in urls:
        url = url.rstrip(")")
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            assert resp.status_code < 400, (
                f"URL {url} in {runbook_path.name} returned {resp.status_code}"
            )
        except requests.exceptions.ConnectionError:
            pytest.fail(f"URL unreachable: {url} in {runbook_path.name}")

@pytest.mark.parametrize("runbook_path", get_all_runbooks())
def test_ansible_syntax(runbook_path):
    """All Ansible runbooks must pass syntax check."""
    result = subprocess.run(
        ["ansible-playbook", "--syntax-check", str(runbook_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"Syntax error in {runbook_path.name}: {result.stderr}"
    )
```

---

## Incident Simulation Testing

### Gameday Protocol

```markdown
## Gameday: Order Service Failure

### Preparation (1 week before)
- [ ] Select runbook to test: `high-error-rate.yaml`
- [ ] Identify participants: on-call engineer, incident commander, observer
- [ ] Prepare staging environment that mirrors prod
- [ ] Create fault injection plan (Chaos Monkey, Litmus, Gremlin)
- [ ] Brief participants (do NOT reveal specific failure mode)

### Execution (2 hours)
1. Inject fault at T+0 (kill 50% of pods)
2. Observer records:
   - T+?? Alert fires
   - T+?? On-call acknowledges
   - T+?? Runbook opened
   - T+?? First diagnosis step completed
   - T+?? Root cause identified
   - T+?? Resolution applied
   - T+?? Service verified healthy
3. Incident commander facilitates, does not help

### Scoring

| Metric | Target | Actual |
|--------|--------|--------|
| Time to alert | < 5 min | |
| Time to acknowledge | < 5 min | |
| Time to diagnosis | < 15 min | |
| Time to resolution | < 30 min | |
| Runbook followed | Yes/No | |
| Runbook accurate | Yes/No | |
| Escalation needed | -- | |

### Post-Gameday
- [ ] Document runbook gaps found
- [ ] Fix stale commands or links
- [ ] Update runbook with lessons learned
- [ ] Schedule next gameday (quarterly)
```

---

## Time-to-Resolution Benchmarking

### MTTR by Runbook Quality

| Runbook Quality | Avg MTTR | Characteristics |
|----------------|----------|-----------------|
| **No runbook** | 90+ min | Ad-hoc debugging, tribal knowledge |
| **Stale runbook** | 60 min | Outdated commands, wrong links, missing steps |
| **Basic runbook** | 30 min | Accurate steps but manual execution |
| **Tested runbook** | 15 min | Recently dry-run tested, all links verified |
| **Automated runbook** | 5 min | Executable playbook with approval gates |

### Tracking MTTR Over Time

```python
"""
Track and visualize MTTR by runbook status.
Feed into documentation quality dashboard.
"""
import json
from datetime import datetime

def record_incident_resolution(
    service: str,
    runbook_used: bool,
    runbook_accurate: bool,
    time_to_detect_min: float,
    time_to_resolve_min: float,
):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "runbook_used": runbook_used,
        "runbook_accurate": runbook_accurate,
        "ttd_minutes": time_to_detect_min,
        "ttr_minutes": time_to_resolve_min,
        "total_mttr": time_to_detect_min + time_to_resolve_min,
    }

    # Append to metrics log
    with open("incident_metrics.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")

    return record
```

---

## Common Runbook Failures

| Failure Mode | Frequency | Impact | Prevention |
|-------------|-----------|--------|------------|
| **Stale commands** | Very common | Commands fail, wastes time | Automated dry-run tests in CI |
| **Wrong credentials** | Common | Cannot access systems | Test prerequisites quarterly |
| **Missing permissions** | Common | Blocked at critical step | IAM audit as part of dry-run |
| **Broken dashboard links** | Very common | Cannot diagnose | URL validation in CI |
| **Outdated escalation contacts** | Common | Wrong person paged | Quarterly contact review |
| **Assumes wrong environment** | Occasional | Runs against wrong cluster | Explicit env variable checks |
| **Missing rollback steps** | Occasional | Cannot undo failed fix | Require rollback section |
| **Untested in staging** | Common | Steps don't work as expected | Mandatory gameday testing |

### Prevention Automation

```bash
#!/bin/bash
# runbook-health-check.sh: Run weekly via cron

RUNBOOK_DIR="runbooks/"
REPORT_FILE="runbook-health-$(date +%Y-%m-%d).md"

echo "# Weekly Runbook Health Check" > "$REPORT_FILE"
echo "Date: $(date -u)" >> "$REPORT_FILE"

TOTAL=0
PASS=0
FAIL=0

for runbook in "$RUNBOOK_DIR"/*.yaml; do
    TOTAL=$((TOTAL + 1))
    name=$(basename "$runbook")

    # Check required sections
    has_rollback=$(grep -c -i "rollback" "$runbook" || true)
    has_verify=$(grep -c -i "verification\|verify" "$runbook" || true)
    has_escalation=$(grep -c -i "escalation\|escalate" "$runbook" || true)

    if [[ $has_rollback -gt 0 && $has_verify -gt 0 && $has_escalation -gt 0 ]]; then
        echo "- [PASS] $name" >> "$REPORT_FILE"
        PASS=$((PASS + 1))
    else
        echo "- [FAIL] $name (missing:" >> "$REPORT_FILE"
        [[ $has_rollback -eq 0 ]] && echo "    rollback" >> "$REPORT_FILE"
        [[ $has_verify -eq 0 ]] && echo "    verification" >> "$REPORT_FILE"
        [[ $has_escalation -eq 0 ]] && echo "    escalation" >> "$REPORT_FILE"
        echo "  )" >> "$REPORT_FILE"
        FAIL=$((FAIL + 1))
    fi
done

echo "" >> "$REPORT_FILE"
echo "## Summary: $PASS/$TOTAL passing ($((PASS * 100 / TOTAL))%)" >> "$REPORT_FILE"
```

---

## Review Cadence

| Trigger | Action | Owner |
|---------|--------|-------|
| Every incident | Update runbook with lessons learned | Incident responder |
| Monthly | Verify all dashboard/tool links | Service owner |
| Quarterly | Full dry-run test in staging | On-call team |
| Quarterly | Review and update escalation contacts | Engineering manager |
| After infrastructure change | Re-test affected runbooks | Platform team |
| After major deploy | Spot-check critical runbooks | Release engineer |
| Annually | Full gameday exercise per service | SRE lead |

### Review Tracking

- [ ] Assign each runbook an owner (individual or team)
- [ ] Record last-tested date in runbook metadata
- [ ] Automate staleness alerts (no test in 90 days = warning)
- [ ] Include runbook review in sprint planning
- [ ] Track runbook test coverage in documentation dashboard

---

## Runbook Coverage Matrix

Map services to failure modes and track which have tested runbooks.

| Service | High Error Rate | High Latency | OOM / Crash | DB Failover | Dependency Down | Cert Expiry |
|---------|:-:|:-:|:-:|:-:|:-:|:-:|
| Order API | Tested | Tested | Draft | Tested | -- | Tested |
| Payment Service | Tested | Tested | Tested | Tested | Tested | Tested |
| Auth Service | Tested | Draft | -- | Tested | Draft | Tested |
| Notification | Draft | -- | -- | -- | Draft | -- |
| Search | Tested | Tested | Draft | -- | Tested | -- |

**Coverage legend:**
- **Tested** = Runbook exists and was dry-run tested within cadence window
- **Draft** = Runbook exists but not recently tested
- **--** = No runbook exists (gap)

### Coverage Target

- Tier 1 services (revenue-critical): 100% coverage, all tested
- Tier 2 services (internal): 80% coverage, critical paths tested
- Tier 3 services (non-critical): 60% coverage, at least drafted

---

## Related Resources

- [API Docs Validation](./api-docs-validation.md) - Validating API documentation accuracy
- [Documentation Quality Metrics](./documentation-quality-metrics.md) - Measuring doc health KPIs
- [Freshness Tracking](./freshness-tracking.md) - Detecting stale documentation
- [Audit Workflows](./audit-workflows.md) - Discovery and audit procedures
- [Alerting Strategies](../../qa-observability/references/alerting-strategies.md) - Alert design for runbook triggers
- [SKILL.md](../SKILL.md) - Parent skill overview
