# Code Templates

Copy-paste code templates for building AEO monitoring infrastructure.

## TypeScript Reference Implementation (Recommended)

The reference implementation uses TypeScript/Next.js/Supabase. Use these patterns as the primary guide.

### Collector Interface

```typescript
/**
 * Standard interface for all AI platform collectors.
 * Each platform implements this interface for consistent data collection.
 */
export interface AEOCollector {
  platform: string;
  collect(query: string): Promise<AEOResponse>;
  extractCitations(response: unknown): Citation[];
  isAvailable(): Promise<boolean>;
}

export interface AEOResponse {
  platform: string;
  query: string;
  responseText: string;
  citations: Citation[];
  timestamp: Date;
  modelVersion: string;
  rawResponse: unknown;
  tokensUsed?: number;
  latencyMs?: number;
}

export interface Citation {
  url: string;
  title?: string;
  domain: string;
  position: number;
  source: 'native' | 'text_extraction' | 'markdown_link';
}
```

### Perplexity Collector Example

```typescript
import { AEOCollector, AEOResponse, Citation } from './types';

export class PerplexityCollector implements AEOCollector {
  platform = 'perplexity';

  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async collect(query: string): Promise<AEOResponse> {
    const response = await fetch('https://api.perplexity.ai/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sonar',
        messages: [{ role: 'user', content: query }],
        return_citations: true,
      }),
    });

    const data = await response.json();

    return {
      platform: this.platform,
      query,
      responseText: data.choices[0].message.content,
      citations: this.extractCitations(data),
      timestamp: new Date(),
      modelVersion: data.model || 'sonar',
      rawResponse: data,
    };
  }

  extractCitations(response: any): Citation[] {
    if (!response.citations) return [];

    return response.citations.map((url: string, i: number) => ({
      url,
      domain: new URL(url).hostname,
      position: i + 1,
      source: 'native' as const,
    }));
  }

  async isAvailable(): Promise<boolean> {
    return !!this.apiKey;
  }
}
```

### Next.js API Route Pattern

```typescript
// src/app/api/collect/route.ts
import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST(request: Request) {
  const { queryId, platforms } = await request.json();
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  // Fetch query
  const { data: query } = await supabase
    .from('queries')
    .select('*')
    .eq('id', queryId)
    .single();

  if (!query) {
    return NextResponse.json({ error: 'Query not found' }, { status: 404 });
  }

  // Collect from each platform
  const results = await Promise.allSettled(
    platforms.map((platform: string) =>
      collectors[platform].collect(query.text)
    )
  );

  // Store results
  const responses = results
    .filter((r): r is PromiseFulfilledResult<AEOResponse> => r.status === 'fulfilled')
    .map(r => r.value);

  await supabase.from('responses').insert(
    responses.map(r => ({
      query_id: queryId,
      platform: r.platform,
      response_text: r.responseText,
      citations: r.citations,
      model_version: r.modelVersion,
      tokens_used: r.tokensUsed,
      latency_ms: r.latencyMs,
    }))
  );

  return NextResponse.json({ collected: responses.length });
}
```

---

## Python Alternative Implementation

### Python API Orchestrator

#### Main Orchestrator Class

```python
"""
AEO Monitoring Orchestrator
Coordinates API calls across multiple platforms with rate limiting.
"""

import os
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from functools import lru_cache
import logging

import requests
from ratelimit import limits, sleep_and_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AEOResponse:
    """Standardized response format across platforms."""
    platform: str
    query: str
    response_text: str
    citations: List[Dict[str, str]]
    timestamp: datetime
    model_version: str
    raw_response: Dict[str, Any]


class AEOOrchestrator:
    """Orchestrates API calls to multiple AI platforms."""

    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        self._cache = {}
        self._cache_ttl = timedelta(hours=24)

    def _get_cache_key(self, platform: str, query: str) -> str:
        """Generate cache key for query."""
        return hashlib.md5(f"{platform}:{query}".encode()).hexdigest()

    def _check_cache(self, platform: str, query: str) -> Optional[AEOResponse]:
        """Check if response is cached and valid."""
        key = self._get_cache_key(platform, query)
        if key in self._cache:
            cached, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                logger.info(f"Cache hit for {platform}: {query[:50]}...")
                return cached
        return None

    def _set_cache(self, platform: str, query: str, response: AEOResponse):
        """Cache response."""
        key = self._get_cache_key(platform, query)
        self._cache[key] = (response, datetime.now())

    @sleep_and_retry
    @limits(calls=10, period=60)  # 10 calls per minute
    def query_perplexity(self, query: str) -> AEOResponse:
        """Query Perplexity Sonar API."""
        cached = self._check_cache("perplexity", query)
        if cached:
            return cached

        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": query}],
            "return_citations": True
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Extract citations (native in Perplexity)
        citations = []
        if "citations" in data:
            for i, url in enumerate(data["citations"]):
                citations.append({
                    "url": url,
                    "position": i + 1,
                    "source": "perplexity_native"
                })

        result = AEOResponse(
            platform="perplexity",
            query=query,
            response_text=data["choices"][0]["message"]["content"],
            citations=citations,
            timestamp=datetime.now(),
            model_version=data.get("model", "sonar"),
            raw_response=data
        )

        self._set_cache("perplexity", query, result)
        return result

    @sleep_and_retry
    @limits(calls=15, period=60)  # 15 calls per minute (free tier)
    def query_gemini(self, query: str) -> AEOResponse:
        """Query Google Gemini API."""
        cached = self._check_cache("gemini", query)
        if cached:
            return cached

        import google.generativeai as genai
        genai.configure(api_key=self.gemini_key)

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(query)

        # Extract citations from text (not native)
        citations = self._extract_urls_from_text(response.text)

        result = AEOResponse(
            platform="gemini",
            query=query,
            response_text=response.text,
            citations=citations,
            timestamp=datetime.now(),
            model_version="gemini-1.5-flash",
            raw_response={"text": response.text}
        )

        self._set_cache("gemini", query, result)
        return result

    @sleep_and_retry
    @limits(calls=50, period=60)  # 50 calls per minute (Tier 1)
    def query_claude(self, query: str) -> AEOResponse:
        """Query Anthropic Claude API."""
        cached = self._check_cache("claude", query)
        if cached:
            return cached

        import anthropic
        client = anthropic.Anthropic(api_key=self.anthropic_key)

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": query}]
        )

        text = message.content[0].text
        citations = self._extract_urls_from_text(text)

        result = AEOResponse(
            platform="claude",
            query=query,
            response_text=text,
            citations=citations,
            timestamp=datetime.now(),
            model_version="claude-3-5-sonnet",
            raw_response={"text": text, "usage": message.usage}
        )

        self._set_cache("claude", query, result)
        return result

    @sleep_and_retry
    @limits(calls=60, period=60)  # 60 calls per minute (Tier 1)
    def query_openai(self, query: str) -> AEOResponse:
        """Query OpenAI API (baseline; no web-search tooling in this template)."""
        cached = self._check_cache("openai", query)
        if cached:
            return cached

        from openai import OpenAI
        client = OpenAI(api_key=self.openai_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}]
        )

        text = response.choices[0].message.content

        result = AEOResponse(
            platform="openai",
            query=query,
            response_text=text,
            citations=[],  # Baseline call: no official web-search tool used here
            timestamp=datetime.now(),
            model_version="gpt-4o-mini",
            raw_response={"text": text}
        )

        self._set_cache("openai", query, result)
        return result

    def _extract_urls_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract URLs from response text."""
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        citations = []
        for i, url in enumerate(set(urls)):  # Dedupe
            citations.append({
                "url": url,
                "position": i + 1,
                "source": "text_extraction"
            })
        return citations

    def query_all_platforms(self, query: str) -> Dict[str, AEOResponse]:
        """Query all configured platforms."""
        results = {}

        platforms = [
            ("perplexity", self.query_perplexity),
            ("gemini", self.query_gemini),
            ("claude", self.query_claude),
            ("openai", self.query_openai),
        ]

        for name, func in platforms:
            try:
                results[name] = func(query)
                logger.info(f"Success: {name}")
            except Exception as e:
                logger.error(f"Error querying {name}: {e}")
                results[name] = None

        return results


# Usage example
if __name__ == "__main__":
    orchestrator = AEOOrchestrator()

    query = "What are the best CRM tools for small businesses?"
    results = orchestrator.query_all_platforms(query)

    for platform, response in results.items():
        if response:
            print(f"\n{platform.upper()}")
            print(f"Citations: {len(response.citations)}")
            for cite in response.citations[:3]:
                print(f"  - {cite['url']}")
```

### Citation Extraction Functions

```python
"""
Citation extraction utilities for different platforms and response formats.
"""

import re
from typing import List, Dict, Optional
from urllib.parse import urlparse


def extract_perplexity_citations(response: dict) -> List[Dict[str, str]]:
    """Extract citations from Perplexity API response (native format)."""
    citations = []

    # Native citations array
    if "citations" in response:
        for i, url in enumerate(response["citations"]):
            citations.append({
                "url": url,
                "position": i + 1,
                "source": "perplexity_native",
                "domain": urlparse(url).netloc
            })

    return citations


def extract_urls_from_text(text: str) -> List[Dict[str, str]]:
    """Extract URLs from plain text response."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]()]+(?:\([^\s<>"{}|\\^`\[\]()]*\))?[^\s<>"{}|\\^`\[\]().,;:!?\'"]*'

    urls = re.findall(url_pattern, text)

    citations = []
    seen = set()

    for url in urls:
        # Clean trailing punctuation
        url = url.rstrip('.,;:!?\'")]}')

        if url not in seen:
            seen.add(url)
            citations.append({
                "url": url,
                "position": len(citations) + 1,
                "source": "text_extraction",
                "domain": urlparse(url).netloc
            })

    return citations


def extract_markdown_links(text: str) -> List[Dict[str, str]]:
    """Extract markdown-formatted links like [text](https://example.com)."""
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, text)

    citations = []
    for i, (title, url) in enumerate(matches):
        citations.append({
            "url": url,
            "title": title,
            "position": i + 1,
            "source": "markdown_link",
            "domain": urlparse(url).netloc
        })

    return citations


def detect_brand_mentions(text: str, brands: List[str]) -> List[Dict[str, any]]:
    """Detect brand mentions in response text."""
    mentions = []
    text_lower = text.lower()

    for brand in brands:
        brand_lower = brand.lower()

        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(brand_lower, start)
            if pos == -1:
                break

            # Get context (50 chars before and after)
            context_start = max(0, pos - 50)
            context_end = min(len(text), pos + len(brand) + 50)
            context = text[context_start:context_end]

            mentions.append({
                "brand": brand,
                "position": pos,
                "context": context,
                "mention_type": classify_mention_type(context, brand)
            })

            start = pos + 1

    return mentions


def classify_mention_type(context: str, brand: str) -> str:
    """Classify the type of brand mention."""
    context_lower = context.lower()

    # Recommendation patterns
    if any(word in context_lower for word in ["recommend", "best", "top", "leading"]):
        return "recommendation"

    # Comparison patterns
    if any(word in context_lower for word in ["vs", "versus", "compared", "alternative"]):
        return "comparison"

    # Citation patterns
    if any(word in context_lower for word in ["according to", "source:", "from"]):
        return "citation"

    return "mention"


def calculate_share_of_model(
    responses: List[Dict],
    target_brand: str,
    competitor_brands: List[str]
) -> Dict[str, float]:
    """Calculate Share of Model metrics."""
    total_responses = len(responses)

    target_mentions = 0
    competitor_mentions = {brand: 0 for brand in competitor_brands}

    for response in responses:
        text = response.get("response_text", "").lower()

        if target_brand.lower() in text:
            target_mentions += 1

        for brand in competitor_brands:
            if brand.lower() in text:
                competitor_mentions[brand] += 1

    all_brands = [target_brand] + competitor_brands
    total_brand_mentions = target_mentions + sum(competitor_mentions.values())

    return {
        "target_som": (target_mentions / total_responses * 100) if total_responses > 0 else 0,
        "target_mention_rate": (target_mentions / total_responses * 100) if total_responses > 0 else 0,
        "target_share_of_voice": (target_mentions / total_brand_mentions * 100) if total_brand_mentions > 0 else 0,
        "competitor_mentions": competitor_mentions,
        "total_responses": total_responses
    }
```

### PostgreSQL Schema

```sql
-- AEO Monitoring Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Queries table
CREATE TABLE queries (
    query_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    intent_category VARCHAR(50) NOT NULL CHECK (intent_category IN ('informational', 'commercial', 'transactional', 'navigational')),
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE,
    UNIQUE(query_text)
);

-- Responses table
CREATE TABLE responses (
    response_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES queries(query_id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('perplexity', 'gemini', 'claude', 'openai', 'chatgpt_web', 'google_aio')),
    response_text TEXT NOT NULL,
    citations JSONB DEFAULT '[]'::jsonb,
    model_version VARCHAR(100),
    tokens_used INTEGER,
    latency_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_response JSONB
);

-- Brand mentions table
CREATE TABLE brand_mentions (
    mention_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    response_id UUID NOT NULL REFERENCES responses(response_id) ON DELETE CASCADE,
    brand VARCHAR(255) NOT NULL,
    mention_type VARCHAR(50) CHECK (mention_type IN ('recommendation', 'comparison', 'citation', 'mention', 'negative')),
    position INTEGER,
    context TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Citations table (normalized)
CREATE TABLE citations (
    citation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    response_id UUID NOT NULL REFERENCES responses(response_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    domain VARCHAR(255),
    position INTEGER,
    source VARCHAR(50) CHECK (source IN ('perplexity_native', 'text_extraction', 'markdown_link')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_responses_query_id ON responses(query_id);
CREATE INDEX idx_responses_platform ON responses(platform);
CREATE INDEX idx_responses_timestamp ON responses(timestamp);
CREATE INDEX idx_brand_mentions_response_id ON brand_mentions(response_id);
CREATE INDEX idx_brand_mentions_brand ON brand_mentions(brand);
CREATE INDEX idx_citations_response_id ON citations(response_id);
CREATE INDEX idx_citations_domain ON citations(domain);

-- Share of Model materialized view
CREATE MATERIALIZED VIEW share_of_model AS
SELECT
    q.query_id,
    q.query_text,
    q.intent_category,
    r.platform,
    DATE_TRUNC('week', r.timestamp) AS week,
    COUNT(*) AS total_responses,
    COUNT(*) FILTER (WHERE bm.brand IS NOT NULL) AS responses_with_mentions,
    COUNT(DISTINCT bm.brand) AS unique_brands_mentioned,
    jsonb_object_agg(
        COALESCE(bm.brand, 'none'),
        COUNT(*) FILTER (WHERE bm.brand IS NOT NULL)
    ) AS brand_mention_counts
FROM queries q
JOIN responses r ON q.query_id = r.query_id
LEFT JOIN brand_mentions bm ON r.response_id = bm.response_id
GROUP BY q.query_id, q.query_text, q.intent_category, r.platform, DATE_TRUNC('week', r.timestamp);

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX idx_som_unique ON share_of_model(query_id, platform, week);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_share_of_model()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY share_of_model;
END;
$$ LANGUAGE plpgsql;

-- Useful queries

-- Get Share of Model for a specific brand
-- SELECT
--     week,
--     platform,
--     total_responses,
--     (brand_mention_counts->>'YourBrand')::integer AS your_mentions,
--     ROUND(100.0 * (brand_mention_counts->>'YourBrand')::integer / total_responses, 2) AS som_percentage
-- FROM share_of_model
-- WHERE week >= NOW() - INTERVAL '30 days'
-- ORDER BY week DESC, platform;

-- Get top cited domains
-- SELECT
--     domain,
--     COUNT(*) AS citation_count,
--     COUNT(DISTINCT response_id) AS unique_responses
-- FROM citations
-- WHERE created_at >= NOW() - INTERVAL '7 days'
-- GROUP BY domain
-- ORDER BY citation_count DESC
-- LIMIT 20;
```

### Scheduled Job (Python + Cron)

```python
"""
Scheduled job for daily AEO monitoring.
Run via cron: 0 6 * * * /path/to/venv/bin/python /path/to/daily_monitor.py
"""

import os
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

from orchestrator import AEOOrchestrator, AEOResponse
from extraction import extract_perplexity_citations, detect_brand_mentions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
TARGET_BRAND = os.getenv("TARGET_BRAND", "YourBrand")
COMPETITOR_BRANDS = os.getenv("COMPETITOR_BRANDS", "Competitor1,Competitor2").split(",")
PLATFORMS = ["perplexity", "gemini", "claude"]  # Skip OpenAI in this template (baseline only)


def get_active_queries(conn) -> list:
    """Fetch active queries from database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT query_id, query_text, intent_category
            FROM queries
            WHERE active = TRUE
            ORDER BY priority DESC, created_at
        """)
        return cur.fetchall()


def store_response(conn, query_id: str, response: AEOResponse):
    """Store response and extracted data."""
    with conn.cursor() as cur:
        # Insert response
        cur.execute("""
            INSERT INTO responses (query_id, platform, response_text, citations, model_version, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING response_id
        """, (
            query_id,
            response.platform,
            response.response_text,
            psycopg2.extras.Json(response.citations),
            response.model_version,
            response.timestamp
        ))
        response_id = cur.fetchone()[0]

        # Insert citations
        if response.citations:
            citation_data = [
                (response_id, c["url"], c.get("title"), c.get("domain"), c.get("position"), c.get("source"))
                for c in response.citations
            ]
            execute_values(cur, """
                INSERT INTO citations (response_id, url, title, domain, position, source)
                VALUES %s
            """, citation_data)

        # Detect and store brand mentions
        all_brands = [TARGET_BRAND] + COMPETITOR_BRANDS
        mentions = detect_brand_mentions(response.response_text, all_brands)

        if mentions:
            mention_data = [
                (response_id, m["brand"], m["mention_type"], m["position"], m["context"])
                for m in mentions
            ]
            execute_values(cur, """
                INSERT INTO brand_mentions (response_id, brand, mention_type, position, context)
                VALUES %s
            """, mention_data)

        conn.commit()
        return response_id


def run_daily_monitoring():
    """Main monitoring job."""
    logger.info("Starting daily AEO monitoring")

    conn = psycopg2.connect(DATABASE_URL)
    orchestrator = AEOOrchestrator()

    try:
        queries = get_active_queries(conn)
        logger.info(f"Processing {len(queries)} queries")

        stats = {"success": 0, "error": 0, "total_citations": 0}

        for query_id, query_text, intent in queries:
            logger.info(f"Processing: {query_text[:50]}...")

            for platform in PLATFORMS:
                try:
                    # Get appropriate query method
                    query_func = getattr(orchestrator, f"query_{platform}")
                    response = query_func(query_text)

                    store_response(conn, query_id, response)

                    stats["success"] += 1
                    stats["total_citations"] += len(response.citations)

                except Exception as e:
                    logger.error(f"Error {platform} - {query_text[:30]}: {e}")
                    stats["error"] += 1

        # Refresh materialized view
        with conn.cursor() as cur:
            cur.execute("SELECT refresh_share_of_model()")
            conn.commit()

        logger.info(f"Completed: {stats}")

    finally:
        conn.close()


if __name__ == "__main__":
    run_daily_monitoring()
```

### Environment Variables Template

```bash
# .env.template - Copy to .env and fill in values

# API Keys
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database
DATABASE_URL=postgresql://user:password@host:5432/aeo_monitoring

# Brand Configuration
TARGET_BRAND=YourBrand
COMPETITOR_BRANDS=Competitor1,Competitor2,Competitor3

# Optional: Commercial Scraping
OXYLABS_API_KEY=
BRIGHTDATA_API_KEY=

# Alerts
SLACK_WEBHOOK_URL=
ALERT_EMAIL=alerts@yourcompany.com
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: aeo
      POSTGRES_PASSWORD: aeo_password
      POSTGRES_DB: aeo_monitoring
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  worker:
    build: .
    environment:
      DATABASE_URL: postgresql://aeo:aeo_password@db:5432/aeo_monitoring
      PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - db
    command: python daily_monitor.py

  metabase:
    image: metabase/metabase:latest
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: metabase
      MB_DB_PORT: 5432
      MB_DB_USER: aeo
      MB_DB_PASS: aeo_password
      MB_DB_HOST: db
    depends_on:
      - db

volumes:
  postgres_data:
```
