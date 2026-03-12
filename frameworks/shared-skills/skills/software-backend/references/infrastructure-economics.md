# Infrastructure Economics and Business Impact Guide

Backend engineering decisions have direct revenue impact. This guide provides frameworks for cost modeling, performance-to-revenue mapping, and FinOps practices.

## Contents

- [Cost Modeling Frameworks](#cost-modeling-frameworks)
- [Performance SLA -> Revenue Mapping](#performance-sla---revenue-mapping)
- [Infrastructure Unit Economics](#infrastructure-unit-economics)
- [Architecture Decisions: Cost vs. Revenue Trade-offs](#architecture-decisions-cost-vs-revenue-trade-offs)
- [FinOps Best Practices](#finops-best-practices)
- [Revenue Attribution Models](#revenue-attribution-models)
- [Cloud Cost Optimization Checklist](#cloud-cost-optimization-checklist)
- [Resources](#resources)

---

## Cost Modeling Frameworks

### Total Cost of Ownership (TCO) Components

```text
TCO = Compute + Storage + Network + Operations + Opportunity Cost

Compute:
- CPU/Memory hours (VMs, containers, serverless)
- GPU hours (ML inference)
- Reserved capacity vs. on-demand premium

Storage:
- Block storage (EBS, Persistent Disks)
- Object storage (S3, GCS, R2)
- Database storage (RDS, Cloud SQL)
- Backup/snapshot costs

Network:
- Data transfer out (egress) - often the surprise cost
- Inter-region transfer
- CDN bandwidth
- Load balancer hours

Operations:
- Monitoring/observability tools
- Incident response tooling
- CI/CD pipeline costs
- Engineer time for maintenance

Opportunity Cost:
- Time-to-market delays from complex architecture
- Developer productivity lost to infra management
- Customer churn from performance issues
```

### Cloud Provider Cost Comparison (January 2026)

| Service Type | AWS | GCP | Azure | Cloudflare |
|--------------|-----|-----|-------|------------|
| Compute (per vCPU-hr) | $0.0416 | $0.0335 | $0.0384 | N/A |
| Serverless (per 1M invocations) | $0.20 | $0.40 | $0.20 | $0.50 |
| Egress (per GB, first 10TB) | $0.09 | $0.12 | $0.087 | $0.00* |
| Object Storage (per GB/mo) | $0.023 | $0.020 | $0.018 | $0.015 |
| Managed PostgreSQL (db.m6g.large equiv) | $0.146/hr | $0.125/hr | $0.134/hr | N/A |

*Cloudflare R2 has zero egress fees - significant for data-heavy workloads.

**Key insight**: Egress costs often exceed compute costs at scale. Design for minimal data transfer.

### Serverless vs. Containers vs. VMs Decision Matrix

| Factor | Serverless | Containers (K8s) | VMs |
|--------|------------|------------------|-----|
| **Best for** | Spiky traffic, <100ms responses | Steady traffic, complex apps | Legacy, compliance, bare metal |
| **Cost at 0 traffic** | $0 | $50-200/mo minimum | $20-100/mo minimum |
| **Cost at 1M req/day** | $50-150 | $100-300 | $150-400 |
| **Cost at 100M req/day** | $5,000-15,000 | $2,000-5,000 | $3,000-8,000 |
| **Cold start impact** | 100-500ms | 0ms | 0ms |
| **Max request duration** | 15-30 min | Unlimited | Unlimited |
| **Operational overhead** | Low | High | Medium |

**Rule of thumb**: Serverless wins below ~1M requests/day or with highly variable traffic. Containers win at scale with steady traffic.

---

## Performance SLA -> Revenue Mapping

### Latency Impact on Conversion

Research-backed correlations (Google, Amazon, Akamai studies):

| Latency Increase | Conversion Impact | Page Views Impact |
|------------------|-------------------|-------------------|
| +100ms | -1% conversions | -0.5% page views |
| +500ms | -7% conversions | -3% page views |
| +1000ms | -11% conversions | -7% page views |
| +2000ms | -16% conversions | -11% page views |

**Calculation example**:
```
Current state: 100ms P50 latency, 1M visitors/month, 3% conversion, $50 AOV
Monthly revenue: 1M x 3% x $50 = $1,500,000

If latency increases to 600ms (+500ms):
New conversion rate: 3% x (1 - 0.07) = 2.79%
New monthly revenue: 1M x 2.79% x $50 = $1,395,000
Revenue loss: $105,000/month

Investment justified: Up to $105,000/month in infrastructure to maintain 100ms latency
```

### Uptime SLA Tiers and Business Impact

| SLA | Monthly Downtime | Annual Downtime | Typical Use Case | Cost Premium |
|-----|------------------|-----------------|------------------|--------------|
| 99% | 7.3 hours | 3.65 days | Internal tools, dev environments | Baseline |
| 99.9% | 43.8 minutes | 8.76 hours | Standard SaaS, most web apps | +20-30% |
| 99.95% | 21.9 minutes | 4.38 hours | E-commerce, financial apps | +40-60% |
| 99.99% | 4.4 minutes | 52.6 minutes | Enterprise SLA requirements | +100-200% |
| 99.999% | 26 seconds | 5.26 minutes | Mission-critical (healthcare, trading) | +300-500% |

**SLA penalty calculation**:
```typescript
interface SLAConfig {
  targetUptime: number;       // e.g., 0.999
  monthlyRevenue: number;     // Revenue at risk
  penaltyPercentPerPoint: number; // e.g., 10% penalty per 0.1% missed
}

const calculateSLAPenalty = (config: SLAConfig, actualUptime: number): number => {
  if (actualUptime >= config.targetUptime) return 0;

  const missedPoints = (config.targetUptime - actualUptime) * 1000; // Convert to basis points
  const penaltyPercent = Math.min(missedPoints * config.penaltyPercentPerPoint, 100);

  return config.monthlyRevenue * (penaltyPercent / 100);
};

// Example: 99.9% SLA, $100k monthly, 10% penalty per 0.1% missed
// Actual uptime: 99.5% (missed by 0.4%)
// Penalty: $100k x (4 x 10%) = $40,000
```

---

## Infrastructure Unit Economics

### Cost Per Request (CPR) Calculation

```typescript
interface ServiceMetrics {
  monthlyRequests: number;
  computeCost: number;      // EC2, Lambda, etc.
  databaseCost: number;     // RDS, DynamoDB, etc.
  storageCost: number;      // S3, EBS, etc.
  networkCost: number;      // Data transfer, CDN
  operationsCost: number;   // Monitoring, logging, CI/CD
}

const calculateCPR = (metrics: ServiceMetrics): number => {
  const totalCost = metrics.computeCost +
                    metrics.databaseCost +
                    metrics.storageCost +
                    metrics.networkCost +
                    metrics.operationsCost;

  return totalCost / metrics.monthlyRequests;
};

// Target CPRs by service type:
// - Static content: < $0.00001 per request
// - Simple API: < $0.0001 per request
// - Complex API with DB: < $0.001 per request
// - ML inference: < $0.01 per request
```

### Cost Per User (CPU) Benchmarks

| Product Type | Monthly Cost Per Active User | Target Margin |
|--------------|------------------------------|---------------|
| Consumer social | $0.05 - $0.20 | 70-80% gross margin |
| SaaS (SMB) | $0.50 - $2.00 | 75-85% gross margin |
| SaaS (Enterprise) | $2.00 - $10.00 | 80-90% gross margin |
| Developer tools | $0.20 - $1.00 | 70-80% gross margin |
| E-commerce | $0.10 - $0.50 per transaction | 60-70% gross margin |

### Scaling Economics Analysis

```typescript
interface ScalingAnalysis {
  currentCost: number;
  currentTraffic: number;
  projectedTraffic: number;
  scalingFactor: 'linear' | 'sublinear' | 'superlinear';
}

const projectCostAtScale = (analysis: ScalingAnalysis): number => {
  const trafficMultiplier = analysis.projectedTraffic / analysis.currentTraffic;

  switch (analysis.scalingFactor) {
    case 'linear':
      // Cost grows 1:1 with traffic (bad for margins)
      return analysis.currentCost * trafficMultiplier;

    case 'sublinear':
      // Cost grows slower than traffic (good economies of scale)
      // Typical for well-architected systems with caching, CDN
      return analysis.currentCost * Math.pow(trafficMultiplier, 0.7);

    case 'superlinear':
      // Cost grows faster than traffic (architectural problem)
      // Common with N+1 queries, poor caching, monoliths
      return analysis.currentCost * Math.pow(trafficMultiplier, 1.3);
  }
};

// Example: $10k/month at 1M requests
// At 10M requests:
// - Linear: $100k/month (bad)
// - Sublinear: $50k/month (good)
// - Superlinear: $200k/month (architectural debt)
```

---

## Architecture Decisions: Cost vs. Revenue Trade-offs

### Edge Computing ROI

**Investment**: CDN + Edge functions
**Typical cost**: $500-5,000/month depending on traffic

| Metric | Before Edge | After Edge | Impact |
|--------|-------------|------------|--------|
| P50 latency | 200ms | 50ms | -75% |
| TTFB | 400ms | 80ms | -80% |
| Conversion rate | 3.0% | 3.15% | +5% |
| SEO ranking | Position 5 | Position 3 | +40% organic traffic |
| Origin requests | 100% | 15% | -85% compute costs |

**ROI calculation**:
```
Monthly traffic: 500,000 visitors
Conversion improvement: 0.15% (3.0% -> 3.15%)
Additional conversions: 500,000 x 0.15% = 750
Average order value: $80
Additional revenue: 750 x $80 = $60,000/month

Edge infrastructure cost: $2,000/month
Origin cost savings: $3,000/month

Net benefit: $60,000 + $3,000 - $2,000 = $61,000/month
ROI: 3,050%
```

### Database Architecture ROI

| Architecture | Monthly Cost | Max RPS | Latency P99 | Best For |
|--------------|--------------|---------|-------------|----------|
| Single PostgreSQL | $200-500 | 1,000 | 50ms | MVPs, <10k DAU |
| PostgreSQL + Read Replicas | $600-1,500 | 10,000 | 30ms | Growing apps |
| PostgreSQL + PgBouncer + Replicas | $800-2,000 | 50,000 | 20ms | High-read apps |
| Distributed (CockroachDB/Spanner) | $2,000-10,000 | 100,000+ | 10ms | Global, multi-region |

### Caching Layer ROI

**Investment**: Redis cluster
**Typical cost**: $200-2,000/month

```
Without caching:
- Database queries per request: 5
- Database cost per query: $0.00001
- Monthly requests: 10M
- Database cost: 10M x 5 x $0.00001 = $500/month

With Redis caching (90% hit rate):
- Database queries: 10M x 5 x 10% = 5M
- Database cost: 5M x $0.00001 = $50/month
- Redis cost: $200/month
- Total: $250/month

Savings: $250/month (50% reduction)
Additional benefit: 10x lower latency for cached requests
```

---

## FinOps Best Practices

### Resource Tagging Strategy

Every cloud resource must be tagged:

```yaml
# Required tags (enforce via policy)
tags:
  team: backend-platform           # Cost allocation
  service: user-api                # Service mapping
  environment: production          # Env separation
  cost-center: CC-1234             # Finance tracking
  owner: john.doe@company.com      # Accountability

# Recommended tags
  created-by: terraform            # Audit trail
  expires: 2026-03-01              # Cleanup automation
  criticality: high                # Incident priority
```

### Budget Alerts Configuration

```typescript
interface BudgetAlert {
  threshold: number;        // Percentage of budget
  action: 'notify' | 'warn' | 'escalate' | 'auto-scale-down';
  recipients: string[];
}

const budgetAlerts: BudgetAlert[] = [
  { threshold: 50, action: 'notify', recipients: ['team-slack'] },
  { threshold: 80, action: 'warn', recipients: ['team-slack', 'tech-lead'] },
  { threshold: 100, action: 'escalate', recipients: ['team-slack', 'tech-lead', 'finance'] },
  { threshold: 120, action: 'auto-scale-down', recipients: ['all'] },
];
```

### Weekly Cost Review Checklist

```markdown
## Weekly Cost Review (15 minutes)

### 1. Top-Line Metrics
- [ ] Total spend vs. budget: ____% of monthly budget
- [ ] Week-over-week change: ____% (flag if >10%)
- [ ] Anomalies detected: Yes/No

### 2. Top 5 Cost Drivers
| Service | This Week | Last Week | Change |
|---------|-----------|-----------|--------|
| 1.      |           |           |        |
| 2.      |           |           |        |
| 3.      |           |           |        |
| 4.      |           |           |        |
| 5.      |           |           |        |

### 3. Quick Wins Identified
- [ ] Idle resources to terminate: ________________
- [ ] Over-provisioned instances: ________________
- [ ] Unattached volumes/IPs: ________________

### 4. Action Items
- [ ] ________________________________
- [ ] ________________________________
```

### Right-Sizing Automation

```typescript
interface RightSizingRule {
  metric: 'cpu_avg' | 'memory_avg' | 'network_avg';
  threshold: number;        // Percentage
  period: number;           // Days to analyze
  action: 'downsize' | 'alert' | 'terminate';
}

const rightSizingRules: RightSizingRule[] = [
  // CPU consistently under 20% for 7 days -> downsize
  { metric: 'cpu_avg', threshold: 20, period: 7, action: 'downsize' },

  // Memory consistently under 30% for 7 days -> downsize
  { metric: 'memory_avg', threshold: 30, period: 7, action: 'downsize' },

  // CPU under 5% for 30 days -> likely unused, alert
  { metric: 'cpu_avg', threshold: 5, period: 30, action: 'alert' },
];

// Implementation: Run weekly via cron, generate recommendations
// Tools: AWS Compute Optimizer, GCP Recommender, Azure Advisor
```

### Reserved Capacity Strategy

| Workload Pattern | Recommendation | Savings |
|------------------|----------------|---------|
| Steady 24/7 | 3-year reserved | 60-72% |
| Business hours only | 1-year reserved + auto-scaling | 40-50% |
| Spiky/unpredictable | On-demand + spot for bursts | 20-30% |
| Dev/staging | Spot/preemptible instances | 60-90% |
| Batch processing | Spot instances with checkpointing | 70-90% |

---

## Revenue Attribution Models

### Infrastructure Cost -> Feature Attribution

```typescript
interface FeatureCostAttribution {
  feature: string;
  requestShare: number;       // % of total requests
  computeWeight: number;      // CPU intensity multiplier
  storageWeight: number;      // Storage intensity multiplier
  attributedCost: number;     // Calculated monthly cost
}

const attributeCosts = (
  features: Omit<FeatureCostAttribution, 'attributedCost'>[],
  totalMonthlyCost: number
): FeatureCostAttribution[] => {
  // Calculate weighted shares
  const totalWeight = features.reduce((sum, f) =>
    sum + (f.requestShare * f.computeWeight * f.storageWeight), 0);

  return features.map(f => ({
    ...f,
    attributedCost: totalMonthlyCost *
      (f.requestShare * f.computeWeight * f.storageWeight) / totalWeight,
  }));
};

// Example output:
// User API: 40% requests, 1.0 compute, 1.0 storage -> $4,000/month
// Search: 20% requests, 3.0 compute, 0.5 storage -> $3,000/month
// Analytics: 10% requests, 2.0 compute, 5.0 storage -> $5,000/month
```

### Gross Margin by Product Line

```typescript
interface ProductLineEconomics {
  product: string;
  monthlyRevenue: number;
  infraCost: number;
  supportCost: number;
  grossMargin: number;        // Calculated
  grossMarginPercent: number; // Calculated
}

const calculateGrossMargins = (
  products: Omit<ProductLineEconomics, 'grossMargin' | 'grossMarginPercent'>[]
): ProductLineEconomics[] => {
  return products.map(p => {
    const totalCost = p.infraCost + p.supportCost;
    const grossMargin = p.monthlyRevenue - totalCost;
    const grossMarginPercent = (grossMargin / p.monthlyRevenue) * 100;

    return { ...p, grossMargin, grossMarginPercent };
  });
};

// Target gross margins by business model:
// SaaS: 75-85%
// Marketplace: 60-70%
// E-commerce: 40-50%
// Fintech: 70-80%
```

---

## Cloud Cost Optimization Checklist

### Immediate Wins (< 1 day effort)

- [ ] Delete unattached EBS volumes, unused elastic IPs
- [ ] Terminate stopped instances older than 7 days
- [ ] Enable S3 Intelligent-Tiering for infrequently accessed data
- [ ] Enable auto-shutdown for dev/staging environments
- [ ] Review and delete old snapshots (>90 days)

### Quick Wins (1-3 days effort)

- [ ] Right-size over-provisioned instances (use Compute Optimizer)
- [ ] Convert on-demand to reserved for steady workloads
- [ ] Enable gzip/brotli compression (reduce transfer costs)
- [ ] Implement CloudFront/CDN for static assets
- [ ] Move logs to cheaper storage tiers after 30 days

### Strategic Optimizations (1-4 weeks)

- [ ] Implement query result caching (Redis/Memcached)
- [ ] Add read replicas to reduce primary DB load
- [ ] Migrate to ARM-based instances (20-40% savings)
- [ ] Implement connection pooling (PgBouncer, ProxySQL)
- [ ] Review and optimize data transfer architecture

### Architecture Improvements (1-3 months)

- [ ] Evaluate serverless for variable workloads
- [ ] Implement event-driven architecture (reduce always-on compute)
- [ ] Multi-region deployment with traffic-based routing
- [ ] Database sharding for horizontal scale
- [ ] Migrate to managed services where TCO is lower

---

## Resources

**FinOps Foundation**:
- [FinOps Framework](https://www.finops.org/framework/) - Industry-standard cloud cost management
- [FinOps Capabilities](https://www.finops.org/framework/capabilities/) - Maturity model

**Cloud Provider Cost Tools**:
- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)
- [GCP Cost Management](https://cloud.google.com/cost-management)
- [Azure Cost Management](https://azure.microsoft.com/en-us/products/cost-management)

**Performance -> Revenue Research**:
- [Google Web Vitals](https://web.dev/vitals/) - Core metrics and impact studies
- [Akamai Performance Research](https://www.akamai.com/resources) - Latency impact studies

---

# END
