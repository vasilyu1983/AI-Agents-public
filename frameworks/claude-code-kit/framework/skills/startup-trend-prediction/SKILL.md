---
name: startup-trend-prediction
description: >
  Analyze 2-3 year historical trends in technology, market, and business models to predict 1-2 years ahead.
  Uses pattern recognition, adoption curves, and cycle analysis to identify timing windows and emerging opportunities.
  History is cyclical - products and markets follow predictable patterns.
globs:
  - "**/*.md"
  - "**/research/**"
  - "**/trends/**"
  - "**/analysis/**"
---

# Startup Trend Prediction

Systematic framework for analyzing historical trends to predict future opportunities. Look back 2-3 years to predict 1-2 years ahead.

---

## When to Use This Skill

| Trigger | Action |
|---------|--------|
| "When should I enter this market?" | Run timing analysis |
| "What's trending in [technology/market]?" | Run trend identification |
| "Is this trend rising or peaking?" | Run adoption curve analysis |
| "What comes after [current trend]?" | Run cycle prediction |
| "Historical patterns for [topic]" | Run pattern recognition |
| "2-3 year trends" or "predict 1-2 years" | Full trend prediction workflow |

---

## Quick Reference: Trend Categories

### Technology Trends

| Trend Area | 2022 State | 2023 State | 2024 State | 2025-26 Prediction |
|------------|------------|------------|------------|-------------------|
| **AI/ML** | GPT-3, ChatGPT launch | GPT-4, AI hype peak | Agents, RAG, fine-tuning | Agentic AI mainstream, multi-modal default |
| **Infrastructure** | Cloud-native default | Serverless growth | Edge computing rise | Edge AI, hybrid deployments |
| **Developer Tools** | GitHub Copilot launch | AI assistants proliferate | AI-native IDEs | Autonomous coding, AI PR reviews |
| **Data** | Lakehouse emergence | Real-time analytics | Streaming-first | Embedded analytics, AI-native data |

### Market Trends

| Trend Area | 2022 State | 2023 State | 2024 State | 2025-26 Prediction |
|------------|------------|------------|------------|-------------------|
| **GTM Motion** | PLG dominant | PLG + Sales hybrid | AI-assisted everything | Agent-to-agent sales |
| **Pricing** | Subscription default | Usage-based rise | Hybrid models | Outcome-based pricing |
| **Consolidation** | Point solutions | Platform plays begin | Vertical platforms | Industry-specific AI |
| **Buyer Behavior** | Self-serve preference | Research-heavy buying | AI-assisted procurement | Autonomous buying |

### Business Model Trends

| Trend Area | 2022 State | 2023 State | 2024 State | 2025-26 Prediction |
|------------|------------|------------|------------|-------------------|
| **Revenue** | SaaS dominant | Usage-based growth | Hybrid SaaS + usage | Outcome/success fees |
| **Distribution** | Marketplace growth | Embedded solutions | API-first | Agent marketplaces |
| **Moats** | Data moats | Network effects | Workflow lock-in | Agent ecosystems |
| **Funding** | Peak valuations | Down rounds, efficiency | Recovery, AI focus | AI-native premium |

---

## Adoption Curve Framework

### Rogers Diffusion Model

```
                    ADOPTION CURVE
    │
    │                          ╭────────╮
    │                      ╭───╯Late    │
    │                  ╭───╯Majority    │
    │              ╭───╯Early          │
    │          ╭───╯Majority           │
    │      ╭───╯Early                  │
    │  ╭───╯Adopters                   │
    │──╯Innovators                     ╰──────
    │     │      │      │      │      │
    │   2.5%   13.5%   34%    34%    16%
    └─────────────────────────────────────────▶
                     TIME
```

### Position Identification

| Position | Market Penetration | Characteristics | Strategy |
|----------|-------------------|-----------------|----------|
| **Innovators** | <2.5% | Tech enthusiasts, high risk tolerance | Enter now, shape market |
| **Early Adopters** | 2.5-16% | Visionaries, want competitive edge | Enter now, premium pricing |
| **Early Majority** | 16-50% | Pragmatists, need proof | Enter with differentiation |
| **Late Majority** | 50-84% | Conservatives, follow herd | Compete on price/features |
| **Laggards** | 84-100% | Skeptics, forced adoption | Avoid or disrupt |

### Gartner Hype Cycle Mapping

```
                    HYPE CYCLE
    │
    │        Peak of
    │     Inflated        ╭─────────────
    │   Expectations  ╭───╯ Plateau of
    │            ╭────╯   Productivity
    │       ╭────╯
    │  ╭────╯         Slope of
    │──╯              Enlightenment
    │  Technology    ╲_____╱
    │   Trigger     Trough of
    │              Disillusionment
    └─────────────────────────────────────▶
                     TIME
```

| Phase | Duration | Action |
|-------|----------|--------|
| Technology Trigger | 0-2 years | Monitor, experiment |
| Peak of Inflated Expectations | 1-3 years | Caution, don't overbuild |
| Trough of Disillusionment | 1-3 years | Build foundations |
| Slope of Enlightenment | 2-4 years | Scale solutions |
| Plateau of Productivity | 5+ years | Optimize, commoditize |

---

## Cycle Pattern Library

### Technology Cycles (7-10 years)

| Cycle | Previous Instance | Current Instance | Pattern |
|-------|------------------|------------------|---------|
| Client → Cloud → Edge | Desktop → Web → Mobile | Cloud → Edge → Device AI | Compute moves to data |
| Monolith → Services → Agents | SOA → Microservices | Microservices → AI Agents | Decomposition continues |
| Batch → Stream → Real-time | ETL → Streaming | Streaming → Real-time AI | Latency shrinks |
| Manual → Assisted → Autonomous | IDE → Copilot | Copilot → Autonomous | Automation increases |

### Market Cycles (5-7 years)

| Cycle | Previous Instance | Current Instance | Pattern |
|-------|------------------|------------------|---------|
| Fragmentation → Consolidation | 2015-2020 point solutions | 2020-2025 platforms | Bundling/unbundling |
| Horizontal → Vertical | Horizontal SaaS | Vertical AI platforms | Specialization wins |
| Self-serve → High-touch → Hybrid | PLG pure | PLG + Sales | Motion evolves |

### Business Model Cycles (3-5 years)

| Cycle | Previous Instance | Current Instance | Pattern |
|-------|------------------|------------------|---------|
| Perpetual → Subscription → Usage | License → SaaS | SaaS → Usage-based | Payment follows value |
| Direct → Marketplace → Embedded | Direct sales | Marketplace → Embedded | Distribution evolves |

---

## Signal vs Noise Framework

### Strong Signals (High Confidence)

| Signal Type | Detection Method | Weight |
|-------------|-----------------|--------|
| VC funding patterns | Track quarterly investment | High |
| Big tech acquisitions | Monitor M&A announcements | High |
| Job posting trends | Analyze LinkedIn/Indeed data | High |
| GitHub activity | Stars, forks, contributors | High |
| Enterprise adoption | Gartner/Forrester reports | Very High |

### Moderate Signals (Validate)

| Signal Type | Detection Method | Weight |
|-------------|-----------------|--------|
| Conference talk themes | Track KubeCon, AWS re:Invent | Medium |
| Hacker News sentiment | Algolia search trends | Medium |
| Reddit discussions | Subreddit growth, sentiment | Medium |
| Influencer adoption | Key voices tweeting about | Medium |

### Weak Signals (Monitor)

| Signal Type | Detection Method | Weight |
|-------------|-----------------|--------|
| ProductHunt launches | Daily tracking | Low |
| Blog post frequency | Content analysis | Low |
| Podcast mentions | Episode scanning | Low |
| Media hype | TechCrunch, Wired articles | Low (often lagging) |

### Noise Filters

**Exclude from prediction**:
- Single viral tweet without follow-up
- PR-driven announcements without product
- Predictions from parties with financial interest
- Old data recycled as "new trend"

---

## Prediction Methodology

### Step 1: Define Scope

```markdown
Domain: [Technology / Market / Business Model]
Lookback Period: [2-3 years]
Prediction Horizon: [1-2 years]
Geography: [Global / Region-specific]
Industry: [Horizontal / Specific vertical]
```

### Step 2: Gather Historical Data

| Year | State | Key Events | Metrics |
|------|-------|------------|---------|
| {{YEAR-3}} | | | |
| {{YEAR-2}} | | | |
| {{YEAR-1}} | | | |
| {{NOW}} | | | |

### Step 3: Identify Patterns

- [ ] Linear growth/decline
- [ ] Exponential growth/decline
- [ ] Cyclical pattern
- [ ] S-curve adoption
- [ ] Plateau reached
- [ ] Disruption event

### Step 4: Generate Prediction

```markdown
## Prediction: [TOPIC]

**Thesis**: [1-2 sentence prediction]
**Confidence**: High / Medium / Low
**Timing**: [When this will happen]
**Evidence**: [3-5 supporting data points]
**Counter-evidence**: [What could invalidate]
```

### Step 5: Identify Opportunities

| Opportunity | Timing Window | Competition | Action |
|-------------|---------------|-------------|--------|
| {{OPP_1}} | {{WINDOW}} | Low/Med/High | Build/Watch/Avoid |
| {{OPP_2}} | {{WINDOW}} | | |

---

## Navigation

### Resources (Deep Dives)

| Resource | Purpose |
|----------|---------|
| [technology-cycle-patterns.md](resources/technology-cycle-patterns.md) | Technology adoption curves and cycles |
| [market-cycle-patterns.md](resources/market-cycle-patterns.md) | Market evolution and consolidation patterns |
| [business-model-evolution.md](resources/business-model-evolution.md) | Revenue model cycles and transitions |
| [signal-vs-noise-filtering.md](resources/signal-vs-noise-filtering.md) | Separating hype from substance |
| [prediction-accuracy-tracking.md](resources/prediction-accuracy-tracking.md) | Validating predictions over time |

### Templates (Outputs)

| Template | Use For |
|----------|---------|
| [trend-analysis-report.md](templates/trend-analysis-report.md) | Full trend prediction report |
| [technology-adoption-curve.md](templates/technology-adoption-curve.md) | Adoption stage mapping |
| [market-timing-assessment.md](templates/market-timing-assessment.md) | When to enter decision |
| [cyclical-pattern-map.md](templates/cyclical-pattern-map.md) | Historical pattern matching |
| [prediction-hypothesis.md](templates/prediction-hypothesis.md) | Prediction with evidence |
| [trend-opportunity-matrix.md](templates/trend-opportunity-matrix.md) | Trends → Opportunities |

### Data

| File | Contents |
|------|----------|
| [sources.json](data/sources.json) | Trend data sources (Gartner, CB Insights, State of AI, etc.) |

---

## Key Principles

### History Rhymes

Past patterns repeat with new technology:
- Client-server → Web apps → Mobile → Edge AI
- Mainframe → PC → Cloud → Distributed
- Manual → Automated → AI-assisted → Autonomous

### Timing Beats Being Right

Being right about a trend but wrong about timing = failure:
- Too early: Market not ready, burn runway
- Too late: Established players, commoditized
- Just right: Ride the wave

### Multiple Signals Required

Never bet on single signal:
- Funding + Hiring + GitHub activity = Strong signal
- Just media coverage = Hype, validate further
- Just VC interest = May be speculative

### Update Predictions

Predictions are living documents:
- Revisit quarterly
- Track accuracy over time
- Adjust for new data
- Document what changed and why

---

## Integration Points

### Feeds Into

- [startup-idea-validation](../startup-idea-validation/SKILL.md) - Market timing score
- [startup-mega-router](../startup-mega-router/SKILL.md) - Trend context for analysis
- [product-management](../product-management/SKILL.md) - Roadmap prioritization

### Receives From

- [startup-review-mining](../startup-review-mining/SKILL.md) - Pain point trends over time
- [startup-competitive-analysis](../startup-competitive-analysis/SKILL.md) - Competitor movement patterns
