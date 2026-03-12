# Cost Governance & Capacity Planning

Production-grade cost control for cloud infrastructure, Kubernetes, and DevOps platforms.

---

## Cost Governance Framework

### Cost Visibility Checklist

- [ ] Resource tagging strategy implemented
- [ ] Cost allocation by team/project/environment
- [ ] Budget alerts at 50%, 80%, 100%
- [ ] Anomaly detection enabled
- [ ] Monthly cost review meeting scheduled
- [ ] Chargeback/showback model defined
- [ ] Unused resource detection automated

### Required Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `team` | Cost allocation | `platform`, `backend` |
| `project` | Project tracking | `checkout-v2` |
| `environment` | Env separation | `prod`, `staging`, `dev` |
| `cost-center` | Finance mapping | `engineering-001` |
| `owner` | Accountability | `alice@company.com` |
| `expiry` | Cleanup automation | `2025-03-01` |

### Tagging Enforcement (Terraform)

```hcl
# variables.tf - Required tags
variable "required_tags" {
  type = object({
    team        = string
    project     = string
    environment = string
    cost_center = string
    owner       = string
  })
}

# Validate tags exist
locals {
  common_tags = merge(var.required_tags, {
    managed_by = "terraform"
    created_at = timestamp()
  })
}
```

---

## Cloud Cost Optimization

### Compute Right-Sizing

**AWS EC2:**
```bash
# Find underutilized instances (AWS CLI + CloudWatch)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --start-time $(date -d '7 days ago' --utc +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date --utc +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Average

# Target: <20% avg CPU = downsize candidate
```

**GCP Compute:**
```bash
# Recommender API for right-sizing
gcloud recommender recommendations list \
  --project=my-project \
  --location=us-central1 \
  --recommender=google.compute.instance.MachineTypeRecommender
```

### Storage Optimization

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Lifecycle policies** | 30-60% | S3/GCS tiering to Infrequent/Archive |
| **Compression** | 50-80% | Enable Zstd/LZ4 for data lakes |
| **Deduplication** | 20-50% | Block-level dedup for backups |
| **Snapshot cleanup** | 10-30% | Delete old EBS/disk snapshots |
| **Orphan volume deletion** | 100% of orphans | Find unattached EBS/persistent disks |

```bash
# Find unattached EBS volumes (AWS)
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query 'Volumes[*].[VolumeId,Size,CreateTime]' \
  --output table
```

### Reserved/Committed Capacity

| Option | Discount | Commitment | Best For |
|--------|----------|------------|----------|
| **Savings Plans** (AWS) | 30-70% | 1-3 years | Flexible workloads |
| **Reserved Instances** | 40-75% | 1-3 years | Steady-state |
| **Committed Use** (GCP) | 30-57% | 1-3 years | Predictable compute |
| **Spot/Preemptible** | 60-90% | None | Fault-tolerant workloads |

**Coverage Target:** 60-70% baseline on reservations, 30-40% on-demand/spot.

---

## Kubernetes Cost Control

### Resource Requests & Limits

```yaml
# Good: Explicit requests and limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Golden Rules:**
- Always set requests (enables scheduling efficiency)
- Set limits ≤ 2x requests (prevents runaway pods)
- Review and adjust quarterly based on actual usage

### Namespace Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-backend
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "50"
    persistentvolumeclaims: "10"
```

### Cluster Autoscaler Configuration

```yaml
# Cluster autoscaler optimized for cost
apiVersion: autoscaling.k8s.io/v1
kind: ClusterAutoscaler
spec:
  scaleDownEnabled: true
  scaleDownDelayAfterAdd: 10m
  scaleDownUnneededTime: 10m
  scaleDownUtilizationThreshold: 0.5  # Scale down if <50% utilized
  maxNodeProvisionTime: 15m
  skipNodesWithLocalStorage: false
  expander: least-waste  # Choose node pool with least waste
```

### Pod Disruption Budgets (for scale-down)

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2  # Or use maxUnavailable
  selector:
    matchLabels:
      app: api
```

---

## Capacity Planning

### Capacity Planning Checklist

- [ ] Current utilization baseline established
- [ ] Growth rate calculated (users, traffic, data)
- [ ] Lead time for scaling known (days/weeks)
- [ ] Peak load patterns documented
- [ ] Cost per unit capacity calculated
- [ ] Scaling triggers defined
- [ ] Quarterly capacity review scheduled

### Capacity Model Template

```markdown
## Capacity Model: [Service Name]

### Current State (as of YYYY-MM-DD)
- Active users: X
- Requests/second (p99): X
- CPU utilization (avg): X%
- Memory utilization (avg): X%
- Storage used: X GB
- Monthly cost: $X

### Growth Assumptions
- User growth: X% per month
- Traffic growth: X% per month
- Data growth: X GB/month

### Scaling Triggers
| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU | 60% | 80% | Add replicas |
| Memory | 70% | 85% | Increase limits |
| Storage | 70% | 85% | Expand volume |
| Latency p99 | 500ms | 1000ms | Scale out |

### 6-Month Projection
| Month | Users | RPS | Cost |
|-------|-------|-----|------|
| +1 | | | $ |
| +3 | | | $ |
| +6 | | | $ |

### Recommendations
1. [Action item]
2. [Action item]
```

---

## FinOps Practices

### Monthly Cost Review Agenda

1. **Cost Summary** (5 min)
   - Total spend vs budget
   - Month-over-month change
   - Top 5 cost drivers

2. **Anomalies** (10 min)
   - Unexpected cost spikes
   - New resources without tags
   - Orphaned resources

3. **Optimization Opportunities** (15 min)
   - Right-sizing recommendations
   - Reserved capacity gaps
   - Unused resources to delete

4. **Action Items** (10 min)
   - Assign optimization tasks
   - Update budgets if needed
   - Schedule follow-ups

### Cost Optimization Workflow

```text
Weekly:
├─ Review cost anomaly alerts
├─ Delete unused resources identified by automation
└─ Check for untagged resources

Monthly:
├─ Run right-sizing analysis
├─ Review reserved capacity utilization
├─ Update cost forecasts
└─ Present to stakeholders

Quarterly:
├─ Review tagging strategy
├─ Evaluate new pricing models
├─ Adjust reserved capacity
└─ Capacity planning refresh
```

---

## Alert Configuration

### Budget Alerts (AWS)

```hcl
# Terraform - AWS Budget
resource "aws_budgets_budget" "monthly" {
  name              = "monthly-budget"
  budget_type       = "COST"
  limit_amount      = "10000"
  limit_unit        = "USD"
  time_period_start = "2025-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["finance@company.com"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_email_addresses = ["cto@company.com"]
  }
}
```

### Cost Anomaly Detection (AWS)

```hcl
resource "aws_ce_anomaly_monitor" "service" {
  name              = "service-cost-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "alert" {
  name      = "cost-anomaly-alerts"
  frequency = "DAILY"
  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_PERCENTAGE"
      match_options = ["GREATER_THAN_OR_EQUAL"]
      values        = ["10"]  # Alert if >10% above expected
    }
  }
  subscriber {
    type    = "EMAIL"
    address = "platform-team@company.com"
  }
}
```

---

## Do / Avoid

### GOOD: Do

- Tag all resources at creation time
- Set budget alerts before hitting limits
- Review right-sizing recommendations monthly
- Use spot/preemptible for fault-tolerant workloads
- Set Kubernetes resource requests on all pods
- Enable cluster autoscaler with scale-down
- Document capacity planning assumptions

### BAD: Avoid

- Deploying without cost tags
- Running dev resources 24/7
- Over-provisioning "just in case"
- Ignoring reserved capacity opportunities
- Setting identical requests and limits (no burst)
- Disabling scale-down to "avoid disruption"
- Waiting for bill shock to investigate

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No tagging** | Can't attribute costs | Enforce tags in CI/CD |
| **Dev runs 24/7** | 70% waste | Scheduled shutdown |
| **Over-provisioned** | Paying for unused capacity | Monthly right-sizing |
| **No reservations** | Paying on-demand premium | 60-70% coverage target |
| **Unset K8s requests** | Scheduler can't optimize | Require in admission |
| **No budget alerts** | Bill shock | Alert at 50%, 80%, 100% |
| **Orphan resources** | Paying for nothing | Weekly cleanup automation |

---

## Optional: AI/Automation

> **Note**: AI assists with analysis but cost decisions need human approval.

### Automated Optimization

- Unused resource detection and notification
- Right-sizing recommendation generation
- Anomaly detection and alerting
- Reserved capacity recommendation

### AI-Assisted Analysis

- Cost trend prediction
- Usage pattern identification
- Optimization prioritization

### Bounded Claims

- AI recommendations need validation before action
- Automated deletions require approval workflow
- Cost predictions are estimates, not guarantees

---

## Tools Reference

| Tool | Purpose | Link |
|------|---------|------|
| **Kubecost** | Kubernetes cost monitoring | kubecost.com |
| **Infracost** | Terraform cost estimation | infracost.io |
| **AWS Cost Explorer** | AWS cost analysis | aws.amazon.com |
| **GCP Cloud Billing** | GCP cost management | cloud.google.com |
| **Spot.io** | Spot instance management | spot.io |
| **Vantage** | Multi-cloud cost | vantage.sh |

---

## Related Templates

- [template-aws-terraform.md](../aws/template-aws-terraform.md) — AWS infrastructure
- [template-cost-optimization.md](../aws/template-cost-optimization.md) — AWS-specific optimization
- [template-kubernetes-ops.md](../kubernetes/template-kubernetes-ops.md) — K8s operations

---

**Last Updated**: December 2025
