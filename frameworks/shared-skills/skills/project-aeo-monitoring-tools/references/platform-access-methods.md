# Platform Access Methods

Detailed guide to accessing each AI platform for AEO monitoring.

## Platform Comparison Matrix

| Platform | API Available | Citations in API | Rate Limits | Auth Method | Best For |
| -------- | ------------- | ---------------- | ----------- | ----------- | -------- |
| Perplexity | Yes | Native | Contact sales | API key | Primary monitoring |
| Gemini | Yes | Extract from response | 1,500/day (free) | API key | Cost-effective baseline |
| Claude | Yes | Extract from response | Tier-based | API key | Brand mention analysis |
| OpenAI | Yes | Depends (official web search tools / citations vary) | Tier-based | API key | Baseline and (if enabled) citation tracking |
| ChatGPT Web | Commercial scraper | Yes (in UI) | N/A | Session tokens | Full citation tracking |
| Google AI Overviews | No | N/A | N/A | N/A | Commercial tools only |

## Perplexity API

**Recommended**: Best native support for AEO monitoring.

### Sonar API (Primary)

Returns AI-generated answers with citations included in response.

**Endpoint**: `https://api.perplexity.ai/chat/completions`

**Key features**:

- Native citation URLs in response
- Multiple model options (sonar-small, sonar-medium, sonar-pro)
- Streaming support

**Authentication**:

```bash
export PERPLEXITY_API_KEY="pplx-xxxx"
```

**Example request**:

```python
import os
import requests

headers = {
    "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar",
    "messages": [
        {"role": "user", "content": "What are the best CRM tools for small businesses?"}
    ],
    "return_citations": True
}

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers=headers,
    json=payload
)

data = response.json()
# Citations available in data['citations']
```

**Rate limits**: Contact Perplexity for volume pricing

**Cost**: ~$1/1M tokens input, $1/1M tokens output

**Citation extraction**: Native - `response['citations']` contains URLs

### Search API

Returns raw web search results (not AI-generated answers).

**Use case**: When you need ranked search results, not conversational answers.

## Google Gemini API

**Recommended**: Free tier excellent for baseline monitoring.

### Free Tier

- 1,500 requests/day
- 32,000 tokens/minute
- Sufficient for ~200 queries x 7 variations

**Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`

**Authentication**:

```bash
export GOOGLE_API_KEY="AIza..."
```

**Example request**:

```python
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content(
    "What are the best CRM tools for small businesses?"
)

# Extract citations from response text (not native)
text = response.text
```

**Rate limits**:

| Tier | RPM | TPM | RPD |
| ---- | --- | --- | --- |
| Free | 15 | 1M | 1,500 |
| Pay-as-you-go | 360 | 4M | Unlimited |

**Cost**:

- Free tier: $0
- Gemini 1.5 Flash: $0.075/1M input, $0.30/1M output
- Gemini 1.5 Pro: $1.25/1M input, $5/1M output

**Citation extraction**: Parse URLs from response text (regex or LLM extraction)

## Anthropic Claude API

**Recommended**: Good for brand mention analysis and sentiment.

### API Access

**Endpoint**: `https://api.anthropic.com/v1/messages`

**Authentication**:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Example request**:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What are the best CRM tools for small businesses?"}
    ]
)

text = message.content[0].text
```

**Rate limits**: Tier-based (Tier 1: 50 RPM, Tier 4: 4,000 RPM)

**Cost**:

- Claude 3.5 Sonnet: $3/1M input, $15/1M output
- Claude 3.5 Haiku: $0.25/1M input, $1.25/1M output

**Prompt caching**: 90% discount on cached prompts (use for repeated query patterns)

**Citation extraction**: Parse from response text (Claude doesn't cite external URLs natively)

## OpenAI API

**Note**: OpenAI API capabilities vary by endpoint and plan. If you have official web-search tooling available, use it for citation tracking; otherwise treat OpenAI as a baseline (no citations).

### Chat Completions

**Endpoint**: `https://api.openai.com/v1/chat/completions`

**Authentication**:

```bash
export OPENAI_API_KEY="sk-..."
```

**Example request**:

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What are the best CRM tools for small businesses?"}
    ]
)

text = response.choices[0].message.content
```

**Rate limits**: Tier-based (Tier 1: 500 RPM, Tier 5: 10,000 RPM)

**Cost**:

- GPT-4o: $2.50/1M input, $10/1M output
- GPT-4o-mini: $0.15/1M input, $0.60/1M output

**Limitation**: Without web-search tooling, responses are not grounded in live web results and will not provide reliable citations. For coverage beyond official tools, use a compliance-reviewed vendor (not DIY scraping).

## ChatGPT Web Interface (Commercial Scraping)

**Use case**: When you need actual ChatGPT web search citations.

### Commercial Scraper Options

| Provider | Pricing | Features |
| -------- | ------- | -------- |
| Oxylabs | Custom | Residential proxies, anti-detection |
| BrightData | $500+/mo | Enterprise features, compliance |
| Scrapeless | $3/1K records | Pay-per-use |

### Technical Challenges

1. **Authentication**: Requires session tokens (expire frequently)
2. **Bot detection**: Aggressive CAPTCHA, fingerprinting
3. **Rate limiting**: Unpredictable, account-based
4. **UI changes**: Scrapers break with UI updates

### Recommended Approach

Use commercial scraping service rather than DIY:

```python
# Example with Oxylabs (conceptual)
from oxylabs import ChatGPTScraper

scraper = ChatGPTScraper(api_key="oxylabs-key")

result = scraper.query("What are the best CRM tools?")
# Returns: text, citations, timestamps
```

**Risk level**: Medium (ToS violation risk transferred to provider)

## Google AI Overviews

**Status**: No API available. Commercial tools only.

### Access Options

1. **SERPapi**: Includes AI Overviews in search results
2. **BrightData**: Google SERP scraping with AI Overview extraction
3. **Profound/Goodie AI**: Built-in AI Overview tracking

### Why No DIY

- Google's anti-bot measures are extremely sophisticated
- Account bans are aggressive
- Legal risk is highest among all platforms

**Recommendation**: Use commercial AEO tools (Profound, Semrush) for AI Overviews.

## Rate Limiting Best Practices

### General Guidelines

1. **Implement exponential backoff**:

```python
import time
import random

def api_call_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

2. **Use request queuing**:

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=15, period=60)  # 15 calls per minute
def rate_limited_api_call(query):
    return api.query(query)
```

3. **Cache responses**:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=10000)
def cached_query(query_hash):
    # Only hit API if not in cache
    return api.query(original_query)
```

### Per-Platform Limits

| Platform | Safe Rate | Burst Allowed | Backoff Strategy |
| -------- | --------- | ------------- | ---------------- |
| Perplexity | 10 RPM | Yes | Exponential |
| Gemini Free | 15 RPM | No | Linear |
| Claude | 50 RPM (Tier 1) | Yes | Exponential |
| OpenAI | 60 RPM (Tier 1) | Yes | Exponential |

## Authentication Security

### API Key Management

```bash
# Store in environment variables
export PERPLEXITY_API_KEY="pplx-xxxx"
export GOOGLE_API_KEY="AIza..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Or use secrets manager (AWS, GCP, Vault)
```

### Key Rotation

- Rotate API keys quarterly
- Use separate keys for development/production
- Monitor usage for anomalies

### Never Commit Keys

```gitignore
# .gitignore
.env
*.key
secrets/
```

## Summary: Recommended Stack

| Use Case | Platforms | Monthly Cost |
| -------- | --------- | ------------ |
| Minimal viable | Perplexity + Gemini free | $15-50 |
| Standard coverage | Perplexity + Gemini + Claude | $150-300 |
| Full coverage | All APIs + commercial scraper | $500-1,500 |

**Priority order**: Perplexity (best citations) -> Gemini (free) -> Claude (sentiment) -> Commercial scraper (ChatGPT web)

## Implementation Language Note

The examples in this document use Python for illustration. The reference implementation uses TypeScript/Next.js. See `assets/technical/typescript-patterns.md` for TypeScript equivalents of all patterns shown here.

Both languages work well for AEO monitoring. Choose based on your team's expertise:

| Language | Strengths for AEO |
| -------- | ----------------- |
| TypeScript/Node.js | Natural fit for Next.js dashboards, shared types between frontend/backend, Supabase client library |
| Python | Rich ML/NLP ecosystem, simpler scripting, more API client libraries |
