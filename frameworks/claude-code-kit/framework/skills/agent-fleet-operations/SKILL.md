---
name: agent-fleet-operations
description: Managing 50+ AI agents as revenue-generating services, fleet orchestration, monitoring, and scaling
version: "1.0"
---

# Agent Fleet Operations

Framework for operating AI agent fleets at scale as revenue-generating services.

---

## Decision Tree: What Agent Operations Help?

```
AGENT FLEET QUESTION
    │
    ├─► "How to design agent services?" ──► Agent Service Design
    │                                        └─► Productization, packaging
    │
    ├─► "How to orchestrate 50+ agents?" ─► Fleet Orchestration
    │                                        └─► Routing, handoffs, coordination
    │
    ├─► "How to monitor agents?" ─────────► Monitoring & Observability
    │                                        └─► Metrics, alerts, debugging
    │
    ├─► "How to price agent services?" ───► Agent Economics
    │                                        └─► Pricing, unit economics
    │
    ├─► "How to scale operations?" ───────► Scaling Strategy
    │                                        └─► Infrastructure, reliability
    │
    └─► "Full fleet strategy" ────────────► COMPREHENSIVE ANALYSIS
                                             └─► All dimensions
```

---

## Agent Service Categories

### Service Taxonomy

| Category | Agent Types | Revenue Model | Margin |
|----------|-------------|---------------|--------|
| **Validation Services** | Idea validation, market research | Per report | 70-80% |
| **Analysis Services** | Competitive intel, trend analysis | Per analysis | 70-80% |
| **Content Services** | Writing, research, summarization | Per piece/usage | 60-70% |
| **Development Services** | Code review, architecture | Per task/hour | 60-70% |
| **Operations Services** | Monitoring, alerts, automation | Subscription | 75-85% |
| **Specialized Services** | Domain-specific expertise | Premium pricing | 80-90% |

### Agent Service Tiers

| Tier | SLA | Response | Price Multiple |
|------|-----|----------|----------------|
| **Self-Serve** | Best effort | Minutes-hours | 1x |
| **Professional** | 99.5% | <1 hour | 2-3x |
| **Enterprise** | 99.9% | <15 min | 5-10x |
| **Dedicated** | Custom | Real-time | Custom |

---

## Agent Fleet Architecture

### Fleet Topology

```
                    ┌─────────────────────┐
                    │    MEGA ROUTER      │
                    │  (orchestration)    │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────┴────┐          ┌─────┴─────┐         ┌────┴────┐
    │VALIDATION│          │ ANALYSIS │         │EXECUTION│
    │  AGENTS  │          │  AGENTS  │         │ AGENTS  │
    └────┬────┘          └─────┬─────┘         └────┬────┘
         │                     │                     │
    ┌────┼────┐          ┌─────┼─────┐         ┌────┼────┐
    │    │    │          │     │     │         │    │    │
   [A1] [A2] [A3]       [A4]  [A5]  [A6]      [A7] [A8] [A9]
```

### Agent Categories in Fleet

| Category | Count | Purpose | Dependencies |
|----------|-------|---------|--------------|
| **Startup Validation** | 8 | Idea → Market → Business | Mega Router |
| **Research & Analysis** | 12 | Market, competitive, trend | Data sources |
| **Product Development** | 15 | Design, architecture, code | Dev tools |
| **Marketing & Growth** | 10 | Content, social, leads | Marketing tools |
| **Operations** | 5 | Monitoring, automation | Infrastructure |

### Agent Interdependencies

```
idea-validation ──────► review-mining ──────► competitive-analysis
       │                      │                      │
       ▼                      ▼                      ▼
trend-prediction ◄────── mega-router ───────► business-models
       │                      │                      │
       ▼                      ▼                      ▼
go-to-market ◄──────── fundraising ◄─────── ux-research
```

---

## Fleet Orchestration

### Routing Strategies

| Strategy | When to Use | Latency | Cost |
|----------|-------------|---------|------|
| **Direct** | Single agent task | Low | Low |
| **Sequential** | Multi-step workflows | High | Medium |
| **Parallel** | Independent tasks | Low | High |
| **Conditional** | Branch on results | Medium | Variable |
| **Hybrid** | Complex workflows | Medium | Medium |

### Orchestration Patterns

**Sequential Chain**:
```
Request → Agent A → Agent B → Agent C → Response
```

**Parallel Fan-Out**:
```
Request → Router ──┬─► Agent A ──┐
                   ├─► Agent B ──┼─► Aggregator → Response
                   └─► Agent C ──┘
```

**Conditional Branch**:
```
Request → Router ──┬─► [if startup] → Validation Agents
                   ├─► [if research] → Analysis Agents
                   └─► [if build] → Development Agents
```

### Handoff Protocol

| Step | Action | Failure Handling |
|------|--------|------------------|
| 1 | Receive task from router | Retry with backoff |
| 2 | Parse context and parameters | Validate, reject if invalid |
| 3 | Execute task | Timeout, escalate |
| 4 | Package results | Validate output format |
| 5 | Return to router | Confirm delivery |

---

## Agent Service Design

### Productizing Agent Capabilities

| Capability | Service Package | Deliverable | SLA |
|------------|-----------------|-------------|-----|
| Idea validation | "Startup Validator" | 9-dimension scorecard | 24h |
| Competitive analysis | "Competitor Deep Dive" | Full report + battlecard | 48h |
| Review mining | "Voice of Customer" | Pain point analysis | 24h |
| Trend analysis | "Market Foresight" | Trend report + predictions | 48h |
| Full validation | "Startup Complete" | All-in-one assessment | 72h |

### Service Packaging Framework

```markdown
## {{SERVICE_NAME}}

### What You Get
- {{DELIVERABLE_1}}
- {{DELIVERABLE_2}}
- {{DELIVERABLE_3}}

### Process
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

### Timeline
- Standard: {{DAYS}} days
- Rush: {{HOURS}} hours (+{{%}}%)

### Pricing
- Standard: ${{X}}
- Professional: ${{Y}}
- Enterprise: Custom

### Agents Used
- {{AGENT_1}} ({{ROLE}})
- {{AGENT_2}} ({{ROLE}})
```

### Service Composition

| Service | Primary Agents | Support Agents |
|---------|----------------|----------------|
| Startup Validator | idea-validation, mega-router | review-mining, trend-prediction |
| Competitor Intel | competitive-analysis | review-mining, market-mapping |
| Market Research | trend-prediction, review-mining | competitive-analysis |
| GTM Strategy | go-to-market, business-models | competitive-analysis |
| Full Assessment | ALL startup agents | ALL analysis agents |

---

## Monitoring & Observability

### Key Metrics

| Category | Metric | Target | Alert Threshold |
|----------|--------|--------|-----------------|
| **Availability** | Uptime | 99.9% | <99.5% |
| **Performance** | P95 latency | <5s | >10s |
| **Quality** | Task success rate | >95% | <90% |
| **Cost** | Cost per task | ${{X}} | >${{Y}} |
| **Scale** | Tasks/hour | {{N}} | Capacity 80% |

### Monitoring Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ AGENT FLEET DASHBOARD                      [LIVE] 🟢    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FLEET HEALTH        TASK VOLUME         REVENUE        │
│  ███████████ 98%     ████████ 847/hr     $12,450 today │
│                                                         │
├─────────────────┬───────────────────┬───────────────────┤
│ TOP AGENTS      │ QUEUE DEPTH       │ ERROR RATE        │
│ mega-router: 312│ validation: 23    │ 0.3% ✓           │
│ review-mining:98│ analysis: 15      │                   │
│ competitive: 67 │ execution: 8      │                   │
└─────────────────┴───────────────────┴───────────────────┘
```

### Alert Configuration

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High latency | P95 > 10s | Warning | Scale up |
| Task failures | >5% failure | Critical | Investigate |
| Queue backup | >100 pending | Warning | Add capacity |
| Cost spike | >2x average | Warning | Review tasks |
| Agent down | Health check fail | Critical | Failover |

### Logging Strategy

| Log Level | What to Log | Retention |
|-----------|-------------|-----------|
| ERROR | Failures, exceptions | 90 days |
| WARN | Retries, slow tasks | 30 days |
| INFO | Task start/complete | 14 days |
| DEBUG | Full context | 7 days |

---

## Agent Economics

### Unit Economics Model

```
Revenue per Task = ${{PRICE}}
├── LLM API Cost = ${{X}} ({{%}})
├── Compute Cost = ${{X}} ({{%}})
├── Data/Tools Cost = ${{X}} ({{%}})
├── Support Cost = ${{X}} ({{%}})
└── Gross Margin = ${{X}} ({{%}})
```

### Pricing Models

| Model | Best For | Formula |
|-------|----------|---------|
| **Per Task** | Discrete outputs | $X per deliverable |
| **Per Token** | Variable complexity | $X per 1K tokens |
| **Subscription** | Regular users | $X/month for Y tasks |
| **Usage-Based** | Variable usage | $X base + $Y per task |
| **Outcome-Based** | High-value tasks | % of value delivered |

### Cost Optimization

| Strategy | Impact | Implementation |
|----------|--------|----------------|
| Model selection | 50-80% cost reduction | Use Haiku for simple tasks |
| Caching | 30-50% cost reduction | Cache common queries |
| Batching | 20-30% cost reduction | Batch similar requests |
| Prompt optimization | 10-20% cost reduction | Reduce token usage |
| Right-sizing | 20-40% cost reduction | Match model to task |

### Model Selection by Task

| Task Type | Recommended Model | Cost (per 1K tokens) |
|-----------|-------------------|---------------------|
| Routing, classification | Haiku | $0.25 |
| Analysis, writing | Sonnet | $3 |
| Complex reasoning | Opus | $15 |
| Simple extraction | Haiku | $0.25 |
| Code review | Sonnet | $3 |

---

## Scaling Strategy

### Scaling Dimensions

| Dimension | Scale Factor | Approach |
|-----------|--------------|----------|
| **Task Volume** | 10-100x | Horizontal scaling, queues |
| **Agent Count** | 10-50x | Registry, discovery |
| **Complexity** | Variable | Model tiering |
| **Geography** | Global | Regional deployments |

### Capacity Planning

| Metric | Current | 3 Month | 6 Month | 12 Month |
|--------|---------|---------|---------|----------|
| Tasks/day | {{N}} | {{N}} | {{N}} | {{N}} |
| Peak tasks/hour | {{N}} | {{N}} | {{N}} | {{N}} |
| Active agents | {{N}} | {{N}} | {{N}} | {{N}} |
| LLM API budget | ${{X}} | ${{X}} | ${{X}} | ${{X}} |

### Reliability Patterns

| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| **Circuit breaker** | Prevent cascade failures | Stop calls after N failures |
| **Retry with backoff** | Handle transient failures | Exponential backoff |
| **Timeout** | Prevent hanging | Hard limit + graceful shutdown |
| **Fallback** | Graceful degradation | Default response or simpler model |
| **Load balancing** | Distribute load | Round-robin or least-connections |

---

## Quality Assurance

### Agent Quality Framework

| Dimension | Metric | Measurement |
|-----------|--------|-------------|
| **Accuracy** | Correct outputs | Human review sample |
| **Completeness** | All requirements met | Checklist validation |
| **Consistency** | Same input → same output | Regression testing |
| **Latency** | Response time | P50, P95, P99 |
| **Cost efficiency** | Cost per quality output | Cost/accuracy ratio |

### Testing Strategy

| Test Type | Frequency | Coverage |
|-----------|-----------|----------|
| Unit tests | Every deploy | Individual agents |
| Integration tests | Daily | Agent chains |
| Regression tests | Weekly | Known scenarios |
| Load tests | Monthly | Capacity limits |
| Chaos tests | Quarterly | Failure modes |

### Evaluation Pipeline

```
New Agent Version
       │
       ▼
┌──────────────────┐
│   Unit Tests     │──► Fail → Block deploy
└────────┬─────────┘
         │ Pass
         ▼
┌──────────────────┐
│ Integration Tests│──► Fail → Block deploy
└────────┬─────────┘
         │ Pass
         ▼
┌──────────────────┐
│   A/B Test (5%)  │──► Worse → Rollback
└────────┬─────────┘
         │ Better
         ▼
┌──────────────────┐
│  Gradual Rollout │──► Monitor metrics
└────────┬─────────┘
         │ Stable
         ▼
    Full Deploy
```

---

## Customer Operations

### Support Tiers

| Tier | Response | Channels | Escalation |
|------|----------|----------|------------|
| Self-serve | Docs, FAQ | Async | Community |
| Standard | <24h | Email | L2 support |
| Professional | <4h | Email, chat | L2 + engineering |
| Enterprise | <1h | All + phone | Dedicated team |

### SLA Framework

| Service Level | Uptime | Response | Credits |
|---------------|--------|----------|---------|
| Basic | 99% | Best effort | None |
| Standard | 99.5% | 24h | 10% |
| Professional | 99.9% | 4h | 25% |
| Enterprise | 99.95% | 1h | 50% |

---

## Resources

| Resource | Purpose |
|----------|---------|
| [fleet-architecture.md](resources/fleet-architecture.md) | Technical architecture guide |
| [monitoring-playbook.md](resources/monitoring-playbook.md) | Observability setup |
| [cost-optimization.md](resources/cost-optimization.md) | Cost reduction strategies |

## Templates

| Template | Purpose |
|----------|---------|
| [service-design.md](templates/service-design.md) | Agent service definition |
| [operations-dashboard.md](templates/operations-dashboard.md) | Monitoring dashboard |
| [capacity-plan.md](templates/capacity-plan.md) | Scaling planning |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Agent operations resources |
