# Minimal Setup Guide

4-week implementation plan for building a basic AEO monitoring system.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (or Supabase account)
- API keys for at least 2 platforms (Perplexity + Gemini recommended)

## Week 1: Foundation

### Day 1-2: Environment Setup

**1. Create project structure**

```bash
mkdir aeo-monitor && cd aeo-monitor
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install requests ratelimit psycopg2-binary python-dotenv
pip install google-generativeai anthropic openai  # API clients
```

**2. Create environment file**

```bash
# .env
PERPLEXITY_API_KEY=pplx-xxx
GOOGLE_API_KEY=AIza-xxx
DATABASE_URL=postgresql://user:pass@localhost:5432/aeo_monitor
TARGET_BRAND=YourBrand
COMPETITOR_BRANDS=Competitor1,Competitor2
```

**3. Set up database**

Option A: Local PostgreSQL

```bash
createdb aeo_monitor
psql aeo_monitor < schema.sql
```

Option B: Supabase (recommended for quick start)

1. Create project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Paste schema from `code-templates.md`
4. Run
5. Copy connection string to `.env`

### Day 3-4: Query Bank Creation

**1. Create queries file**

```python
# queries.py
"""Initial query bank for AEO monitoring."""

QUERIES = [
    # Informational queries
    {"text": "What is [your product category]?", "intent": "informational", "priority": 3},
    {"text": "How does [your product category] work?", "intent": "informational", "priority": 3},
    {"text": "[your product category] explained", "intent": "informational", "priority": 2},

    # Commercial queries (high priority)
    {"text": "Best [your product category] tools", "intent": "commercial", "priority": 5},
    {"text": "Top [your product category] software 2026", "intent": "commercial", "priority": 5},
    {"text": "[your product category] comparison", "intent": "commercial", "priority": 5},
    {"text": "[Competitor1] vs [Competitor2]", "intent": "commercial", "priority": 4},
    {"text": "[Competitor1] alternatives", "intent": "commercial", "priority": 5},

    # Transactional queries
    {"text": "[your product category] pricing", "intent": "transactional", "priority": 4},
    {"text": "[your product category] free trial", "intent": "transactional", "priority": 4},

    # Problem-solution queries
    {"text": "How to solve [problem your product solves]", "intent": "informational", "priority": 4},
    {"text": "[problem] solution for [your target audience]", "intent": "commercial", "priority": 4},
]

# Customize with your actual product category and competitors
# Aim for 50-100 queries minimum, 250-500 for comprehensive coverage
```

**2. Load queries to database**

```python
# load_queries.py
import os
import psycopg2
from dotenv import load_dotenv
from queries import QUERIES

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

for q in QUERIES:
    cur.execute("""
        INSERT INTO queries (query_text, intent_category, priority)
        VALUES (%s, %s, %s)
        ON CONFLICT (query_text) DO NOTHING
    """, (q["text"], q["intent"], q["priority"]))

conn.commit()
print(f"Loaded {len(QUERIES)} queries")
conn.close()
```

### Day 5: API Testing

**Test each API individually**

```python
# test_apis.py
import os
from dotenv import load_dotenv

load_dotenv()

TEST_QUERY = "What are the best CRM tools for small businesses?"

# Test Perplexity
def test_perplexity():
    import requests
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": TEST_QUERY}],
            "return_citations": True
        }
    )
    print("Perplexity:", response.status_code)
    if response.ok:
        data = response.json()
        print(f"  Citations: {len(data.get('citations', []))}")
    return response.ok

# Test Gemini
def test_gemini():
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(TEST_QUERY)
    print("Gemini: OK")
    print(f"  Response length: {len(response.text)}")
    return True

if __name__ == "__main__":
    print("Testing APIs...\n")
    test_perplexity()
    test_gemini()
```

## Week 2: Core Pipeline

### Day 1-2: Orchestrator Implementation

Copy the `AEOOrchestrator` class from `code-templates.md` to `orchestrator.py`.

**Test orchestrator**

```python
# test_orchestrator.py
from orchestrator import AEOOrchestrator

orchestrator = AEOOrchestrator()

# Test single platform
response = orchestrator.query_perplexity("Best CRM tools 2026")
print(f"Platform: {response.platform}")
print(f"Citations: {len(response.citations)}")
for cite in response.citations[:3]:
    print(f"  - {cite['url']}")
```

### Day 3-4: Storage Implementation

**Create storage module**

```python
# storage.py
import os
import psycopg2
from psycopg2.extras import execute_values, Json
from dotenv import load_dotenv

load_dotenv()

class AEOStorage:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))

    def get_queries(self, limit=None, priority_min=None):
        """Get active queries."""
        with self.conn.cursor() as cur:
            sql = "SELECT query_id, query_text, intent_category FROM queries WHERE active = TRUE"
            if priority_min:
                sql += f" AND priority >= {priority_min}"
            sql += " ORDER BY priority DESC"
            if limit:
                sql += f" LIMIT {limit}"
            cur.execute(sql)
            return cur.fetchall()

    def store_response(self, query_id, response):
        """Store response and citations."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO responses (query_id, platform, response_text, citations, model_version, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING response_id
            """, (
                query_id,
                response.platform,
                response.response_text,
                Json(response.citations),
                response.model_version,
                response.timestamp
            ))
            response_id = cur.fetchone()[0]

            # Store individual citations
            if response.citations:
                citation_data = [
                    (response_id, c["url"], c.get("domain", ""), c.get("position", 0))
                    for c in response.citations
                ]
                execute_values(cur, """
                    INSERT INTO citations (response_id, url, domain, position)
                    VALUES %s
                """, citation_data)

            self.conn.commit()
            return response_id

    def close(self):
        self.conn.close()
```

### Day 5: Integration Test

```python
# integration_test.py
from orchestrator import AEOOrchestrator
from storage import AEOStorage

def run_integration_test():
    orchestrator = AEOOrchestrator()
    storage = AEOStorage()

    # Get first 5 queries
    queries = storage.get_queries(limit=5)
    print(f"Testing with {len(queries)} queries")

    for query_id, query_text, intent in queries:
        print(f"\nQuery: {query_text[:50]}...")

        # Query Perplexity only for test
        response = orchestrator.query_perplexity(query_text)
        response_id = storage.store_response(query_id, response)

        print(f"  Stored response: {response_id}")
        print(f"  Citations: {len(response.citations)}")

    storage.close()
    print("\nIntegration test complete!")

if __name__ == "__main__":
    run_integration_test()
```

## Week 3: Analysis Layer

### Day 1-2: Brand Detection

```python
# analysis.py
import re
from typing import List, Dict

def detect_brand_mentions(text: str, brands: List[str]) -> List[Dict]:
    """Detect brand mentions in response text."""
    mentions = []
    text_lower = text.lower()

    for brand in brands:
        brand_lower = brand.lower()

        # Find all occurrences
        for match in re.finditer(re.escape(brand_lower), text_lower):
            pos = match.start()

            # Get context
            context_start = max(0, pos - 50)
            context_end = min(len(text), pos + len(brand) + 50)
            context = text[context_start:context_end]

            # Classify mention type
            mention_type = classify_mention(context)

            mentions.append({
                "brand": brand,
                "position": pos,
                "context": context,
                "mention_type": mention_type
            })

    return mentions

def classify_mention(context: str) -> str:
    """Classify the type of mention."""
    context_lower = context.lower()

    if any(w in context_lower for w in ["recommend", "best", "top", "leading", "excellent"]):
        return "recommendation"
    if any(w in context_lower for w in ["vs", "versus", "compared", "alternative", "competitor"]):
        return "comparison"
    if any(w in context_lower for w in ["avoid", "issue", "problem", "poor", "bad"]):
        return "negative"

    return "mention"

def calculate_share_of_model(responses: List[Dict], target_brand: str) -> Dict:
    """Calculate Share of Model metrics."""
    total = len(responses)
    mentioned = sum(1 for r in responses if target_brand.lower() in r.get("response_text", "").lower())

    return {
        "total_responses": total,
        "brand_mentions": mentioned,
        "share_of_model": round(mentioned / total * 100, 2) if total > 0 else 0
    }
```

### Day 3-4: Competitor Tracking

Add competitor tracking to storage:

```python
# Add to storage.py

def store_brand_mentions(self, response_id: str, mentions: List[Dict]):
    """Store brand mentions for a response."""
    if not mentions:
        return

    with self.conn.cursor() as cur:
        mention_data = [
            (response_id, m["brand"], m["mention_type"], m["position"], m["context"])
            for m in mentions
        ]
        execute_values(cur, """
            INSERT INTO brand_mentions (response_id, brand, mention_type, position, context)
            VALUES %s
        """, mention_data)
        self.conn.commit()

def get_share_of_model(self, brand: str, days: int = 7) -> Dict:
    """Get Share of Model for a brand over time period."""
    with self.conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) as total_responses,
                COUNT(*) FILTER (WHERE bm.brand = %s) as brand_mentions
            FROM responses r
            LEFT JOIN brand_mentions bm ON r.response_id = bm.response_id
            WHERE r.timestamp >= NOW() - INTERVAL '%s days'
        """, (brand, days))
        row = cur.fetchone()

        total, mentions = row
        return {
            "total_responses": total,
            "brand_mentions": mentions,
            "share_of_model": round(mentions / total * 100, 2) if total > 0 else 0
        }
```

### Day 5: Full Pipeline Test

```python
# full_pipeline.py
import os
from dotenv import load_dotenv
from orchestrator import AEOOrchestrator
from storage import AEOStorage
from analysis import detect_brand_mentions

load_dotenv()

TARGET_BRAND = os.getenv("TARGET_BRAND")
COMPETITORS = os.getenv("COMPETITOR_BRANDS", "").split(",")
ALL_BRANDS = [TARGET_BRAND] + COMPETITORS

def run_full_pipeline():
    orchestrator = AEOOrchestrator()
    storage = AEOStorage()

    queries = storage.get_queries(priority_min=4)  # High priority only
    print(f"Processing {len(queries)} high-priority queries")

    platforms = ["perplexity", "gemini"]

    for query_id, query_text, intent in queries:
        print(f"\nQuery: {query_text[:40]}...")

        for platform in platforms:
            try:
                query_func = getattr(orchestrator, f"query_{platform}")
                response = query_func(query_text)

                # Store response
                response_id = storage.store_response(query_id, response)

                # Detect and store brand mentions
                mentions = detect_brand_mentions(response.response_text, ALL_BRANDS)
                storage.store_brand_mentions(response_id, mentions)

                print(f"  {platform}: {len(response.citations)} citations, {len(mentions)} mentions")

            except Exception as e:
                print(f"  {platform}: ERROR - {e}")

    # Print SoM summary
    print("\n--- Share of Model Summary ---")
    som = storage.get_share_of_model(TARGET_BRAND, days=1)
    print(f"{TARGET_BRAND}: {som['share_of_model']}%")

    storage.close()

if __name__ == "__main__":
    run_full_pipeline()
```

## Week 4: Reporting & Automation

### Day 1-2: Dashboard Setup

**Option A: Metabase (recommended)**

1. Install: `docker run -d -p 3000:3000 --name metabase metabase/metabase`
2. Connect to your PostgreSQL database
3. Create questions:
   - Share of Model over time
   - Top cited domains
   - Brand mention breakdown
   - Citation count by platform

**Option B: Simple CLI Report**

```python
# report.py
from storage import AEOStorage
from tabulate import tabulate

def generate_report():
    storage = AEOStorage()

    print("\n=== AEO Monitoring Report ===\n")

    # Share of Model
    with storage.conn.cursor() as cur:
        cur.execute("""
            SELECT
                bm.brand,
                COUNT(*) as mentions,
                COUNT(DISTINCT r.response_id) as responses
            FROM brand_mentions bm
            JOIN responses r ON bm.response_id = r.response_id
            WHERE r.timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY bm.brand
            ORDER BY mentions DESC
        """)
        brands = cur.fetchall()

    print("Brand Mentions (Last 7 Days)")
    print(tabulate(brands, headers=["Brand", "Mentions", "Responses"]))

    # Top cited domains
    with storage.conn.cursor() as cur:
        cur.execute("""
            SELECT domain, COUNT(*) as count
            FROM citations
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 10
        """)
        domains = cur.fetchall()

    print("\n\nTop Cited Domains")
    print(tabulate(domains, headers=["Domain", "Citations"]))

    storage.close()

if __name__ == "__main__":
    generate_report()
```

### Day 3-4: Scheduled Automation

**Cron setup (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add daily job at 6 AM
0 6 * * * cd /path/to/aeo-monitor && /path/to/venv/bin/python full_pipeline.py >> /var/log/aeo-monitor.log 2>&1

# Add weekly report on Monday at 9 AM
0 9 * * 1 cd /path/to/aeo-monitor && /path/to/venv/bin/python report.py | mail -s "Weekly AEO Report" you@company.com
```

**GitHub Actions (alternative)**

```yaml
# .github/workflows/daily-monitor.yml
name: Daily AEO Monitor

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python full_pipeline.py
        env:
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          TARGET_BRAND: ${{ vars.TARGET_BRAND }}
          COMPETITOR_BRANDS: ${{ vars.COMPETITOR_BRANDS }}
```

### Day 5: Alerts

```python
# alerts.py
import os
import requests
from storage import AEOStorage

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
ALERT_THRESHOLD = 10  # Alert if SoM drops below 10%

def check_alerts():
    storage = AEOStorage()

    # Get current SoM
    current = storage.get_share_of_model(os.getenv("TARGET_BRAND"), days=1)
    previous = storage.get_share_of_model(os.getenv("TARGET_BRAND"), days=7)

    alerts = []

    # Check if SoM dropped significantly
    if current["share_of_model"] < ALERT_THRESHOLD:
        alerts.append(f"ALERT: Share of Model dropped to {current['share_of_model']}%")

    # Check for significant change
    if previous["share_of_model"] > 0:
        change = current["share_of_model"] - previous["share_of_model"]
        if change < -5:  # More than 5% drop
            alerts.append(f"ALERT: SoM decreased by {abs(change)}% (was {previous['share_of_model']}%)")

    # Send alerts
    if alerts and SLACK_WEBHOOK:
        message = "\n".join(alerts)
        requests.post(SLACK_WEBHOOK, json={"text": f"AEO Alert:\n{message}"})
        print(f"Sent {len(alerts)} alerts to Slack")

    storage.close()

if __name__ == "__main__":
    check_alerts()
```

## Final Checklist

```
Week 1: Foundation
[ ] Project structure created
[ ] Database set up (PostgreSQL/Supabase)
[ ] Environment variables configured
[ ] Query bank created (50+ queries)
[ ] API keys tested

Week 2: Core Pipeline
[ ] Orchestrator implemented
[ ] Rate limiting working
[ ] Response storage working
[ ] Citation extraction working
[ ] Integration test passing

Week 3: Analysis
[ ] Brand detection implemented
[ ] Competitor tracking working
[ ] Share of Model calculation working
[ ] Full pipeline tested

Week 4: Reporting & Automation
[ ] Dashboard created (Metabase or CLI)
[ ] Scheduled jobs configured
[ ] Alerts set up
[ ] Documentation complete
```

## Next Steps

After completing the minimal setup:

1. **Expand query bank** to 250-500 queries
2. **Add more platforms** (Claude, commercial ChatGPT scraper)
3. **Build custom dashboards** for specific stakeholders
4. **Implement A/B testing** for content optimization
5. **Add sentiment analysis** for brand mentions
