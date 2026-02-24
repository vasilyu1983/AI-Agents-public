# Cost Estimation for AEO Monitoring

Detailed pricing breakdown for building and operating AEO monitoring infrastructure.

## Cost Tiers Overview

| Tier | Monthly Cost | Coverage | Best For |
| ---- | ------------ | -------- | -------- |
| Minimal | $15-50 | Perplexity + Gemini | Startups, testing |
| Standard | $150-300 | Multi-platform APIs | Growing companies |
| Comprehensive | $500-1,500 | APIs + commercial scraping | Established businesses |
| Enterprise | $2,000+ | Full coverage + dedicated infra | Large organizations |

## API Costs (January 2026)

### Perplexity

| Model | Input | Output | Notes |
| ----- | ----- | ------ | ----- |
| sonar-small | $1/1M tokens | $1/1M tokens | Basic queries |
| sonar-medium | $1/1M tokens | $1/1M tokens | Standard |
| sonar-pro | Contact | Contact | High volume |

**Estimated monthly cost** (500 queries/day):

- ~15,000 queries/month
- ~500 tokens/query average
- **$15-30/month**

### Google Gemini

| Model | Input | Output | Notes |
| ----- | ----- | ------ | ----- |
| gemini-1.5-flash | Free (1,500/day) | Free | Best value |
| gemini-1.5-flash | $0.075/1M | $0.30/1M | Pay-as-you-go |
| gemini-1.5-pro | $1.25/1M | $5.00/1M | Complex analysis |

**Estimated monthly cost** (500 queries/day):

- Free tier: **$0** (covers ~1,500 queries/day)
- Paid tier: **$5-20/month**

### Anthropic Claude

| Model | Input | Output | Notes |
| ----- | ----- | ------ | ----- |
| claude-3.5-sonnet | $3.00/1M | $15.00/1M | Best quality |
| claude-3.5-haiku | $0.25/1M | $1.25/1M | Fast, cheap |

**Prompt caching**: 90% discount on cached prompts

**Estimated monthly cost** (500 queries/day):

- Haiku: **$10-25/month**
- Sonnet: **$75-150/month**
- With caching: **30-50% reduction**

### OpenAI

| Model | Input | Output | Notes |
| ----- | ----- | ------ | ----- |
| gpt-4o | $2.50/1M | $10.00/1M | Best quality |
| gpt-4o-mini | $0.15/1M | $0.60/1M | Fast, cheap |

**Estimated monthly cost** (500 queries/day):

- GPT-4o-mini: **$5-15/month**
- GPT-4o: **$60-120/month**

## Commercial Scraping Costs

### ChatGPT Web Scraping

| Provider | Pricing Model | Estimated Monthly |
| -------- | ------------- | ----------------- |
| BrightData | $500/mo base + usage | $500-1,500 |
| Oxylabs | Custom pricing | $300-1,000 |
| Scrapeless | $3/1,000 records | $45-150 |

### Google AI Overviews

Only available through enterprise tools:

| Tool | Pricing | Notes |
| ---- | ------- | ----- |
| Profound | $499/mo | Full AEO suite |
| Semrush One | $199+/mo | Part of SEO suite |
| Goodie AI | $495+/mo | Enterprise features |

## Infrastructure Costs

### Database

| Option | Monthly Cost | Best For |
| ------ | ------------ | -------- |
| Supabase Free | $0 | <500MB, testing |
| Supabase Pro | $25 | <8GB, standard |
| PostgreSQL (self-hosted) | $20-50 | Full control |
| BigQuery | $5/TB processed | Large scale |

### Compute

| Option | Monthly Cost | Notes |
| ------ | ------------ | ----- |
| AWS Lambda | $0-20 | Serverless, pay-per-use |
| Cloud Functions | $0-20 | Serverless |
| EC2/Compute Engine | $20-100 | Dedicated |
| Railway/Render | $5-25 | Easy deployment |

### Storage

| Option | Monthly Cost | Notes |
| ------ | ------------ | ----- |
| S3/GCS | $0.02/GB | Long-term storage |
| Included in Supabase | $0 | Up to limits |

### Orchestration

| Option | Monthly Cost | Notes |
| ------ | ------------ | ----- |
| Cron job (self-hosted) | $0 | Simple scheduling |
| GitHub Actions | $0-20 | CI/CD integration |
| Temporal Cloud | $25-200 | Complex workflows |

## Tier Breakdowns

### Tier 1: Minimal ($15-50/month)

**Use case**: Testing, proof of concept, small query volume

| Component | Service | Cost |
| --------- | ------- | ---- |
| Perplexity API | 500 queries/day | $15-30 |
| Gemini API | Free tier | $0 |
| Database | Supabase Free | $0 |
| Compute | Lambda/Cloud Functions | $0-5 |
| **Total** | | **$15-50** |

**Coverage**: Perplexity (citations), Gemini (baseline)

**Limitations**: No ChatGPT web, no Google AI Overviews

### Tier 2: Standard ($150-300/month)

**Use case**: Growing company, competitive monitoring

| Component | Service | Cost |
| --------- | ------- | ---- |
| Perplexity API | 1,000 queries/day | $30-60 |
| Gemini API | Pay-as-you-go | $10-20 |
| Claude API | Haiku | $15-30 |
| OpenAI API | GPT-4o-mini | $10-20 |
| Database | Supabase Pro | $25 |
| Compute | Railway | $10-20 |
| Orchestration | GitHub Actions | $0-10 |
| **Total** | | **$150-300** |

**Coverage**: All API-accessible platforms

**Limitations**: No ChatGPT web citations, no AI Overviews

### Tier 3: Comprehensive ($500-1,500/month)

**Use case**: Established business, full competitive intelligence

| Component | Service | Cost |
| --------- | ------- | ---- |
| Perplexity API | High volume | $50-100 |
| Gemini API | Pro tier | $30-50 |
| Claude API | Sonnet | $75-150 |
| OpenAI API | GPT-4o | $60-120 |
| ChatGPT Scraping | Scrapeless/Oxylabs | $150-500 |
| Database | PostgreSQL managed | $50-100 |
| Compute | Dedicated | $50-100 |
| Analytics | Metabase Cloud | $0-85 |
| **Total** | | **$500-1,500** |

**Coverage**: All platforms including ChatGPT web

**Still missing**: Google AI Overviews (use Profound/Semrush)

### Tier 4: Enterprise ($2,000+/month)

**Use case**: Large organization, full coverage

| Component | Service | Cost |
| --------- | ------- | ---- |
| All APIs | High volume | $300-500 |
| Commercial scraping | BrightData Enterprise | $500-1,000 |
| Profound/Goodie AI | AI Overviews | $499-500 |
| Database | PostgreSQL HA | $200-500 |
| Compute | Kubernetes | $200-500 |
| Monitoring | Datadog/New Relic | $100-300 |
| **Total** | | **$2,000-4,000** |

**Coverage**: Full platform coverage

## ROI Calculation

### Value Metrics

| Metric | Potential Value |
| ------ | --------------- |
| Organic traffic from AI | 5-15% of total traffic |
| Lead generation improvement | 10-30% lift |
| Brand visibility increase | Measurable SoM growth |
| Competitive intelligence | Priceless |

### Breakeven Analysis

**If AI-driven traffic = 10% of total, and each visitor worth $10:**

- 1,000 monthly visitors from AI = $10,000 value
- $500/month monitoring cost = 5% of value
- ROI = 20:1

### When to Build vs. Buy

**Build custom if**:

- Tool costs > $2,000/month
- Need > 2,000 queries/week
- Require deep custom integration
- Have 1+ dedicated engineer

**Use commercial tools if**:

- Tool costs < $500/month
- Query volume < 500/week
- Standard features sufficient
- No dedicated engineering

## Cost Optimization Tips

### API Costs

1. **Use caching**: Cache responses for 24-48 hours
2. **Batch queries**: Combine related queries
3. **Use cheaper models**: Haiku/GPT-4o-mini for volume
4. **Prompt caching**: 90% savings on Claude

### Infrastructure

1. **Start serverless**: Lambda/Cloud Functions scale to zero
2. **Use free tiers**: Supabase, Gemini, GitHub Actions
3. **Optimize storage**: Archive old data to S3

### Scraping

1. **Prioritize queries**: Only scrape high-value queries
2. **Reduce frequency**: Weekly instead of daily for low-priority
3. **Use APIs first**: Scraping is expensive, APIs are cheap

## Cost Transparency Pattern

The reference implementation includes real-time cost display so users always know what they're spending.

### Implementation

```typescript
// Show cost breakdown in the UI after each collection run
interface CollectionCostSummary {
  totalCost: number;
  breakdown: {
    platform: string;
    queries: number;
    inputTokens: number;
    outputTokens: number;
    cost: number;
  }[];
  budgetRemaining: number;
  projectedMonthlyCost: number;
}
```

### UI Pattern

Display a cost widget in the dashboard showing:

- **Per-run cost**: "This collection run cost $0.42 across 4 platforms"
- **Daily spend**: Running total with budget comparison
- **Monthly projection**: Based on current usage patterns
- **Per-query breakdown**: Which platforms cost most per query

### Budget Controls

```typescript
// Configurable budget limits
const BUDGET_CONFIG = {
  dailyLimit: 10.00,      // Stop collection if exceeded
  monthlyLimit: 200.00,   // Alert at 80%, stop at 100%
  alertThreshold: 0.80,   // Alert at 80% of limit
  platforms: {
    perplexity: { enabled: true, maxDailySpend: 3.00 },
    gemini: { enabled: true, maxDailySpend: 1.00 },
    claude: { enabled: true, maxDailySpend: 4.00 },
    openai: { enabled: true, maxDailySpend: 2.00 },
  },
};
```

**Why this matters**: Cost transparency builds trust and prevents bill shock, especially when scaling from 30 to 500 queries.

## Cost Monitoring

### Set Alerts

```python
# Example: Alert if daily cost exceeds threshold
if daily_api_cost > 20:
    send_alert("API costs exceeded $20/day")
```

### Track Metrics

| Metric | Target |
| ------ | ------ |
| Cost per query | <$0.01 |
| API error rate | <1% |
| Cache hit rate | >70% |
| Cost vs. budget | <100% |

## Summary

| Budget | Recommended Tier | Coverage |
| ------ | ---------------- | -------- |
| <$50/mo | Minimal | Perplexity + Gemini |
| $150-300/mo | Standard | All APIs |
| $500-1,500/mo | Comprehensive | APIs + ChatGPT web |
| $2,000+/mo | Enterprise | Full coverage |

**Start minimal, scale based on value demonstrated.**
