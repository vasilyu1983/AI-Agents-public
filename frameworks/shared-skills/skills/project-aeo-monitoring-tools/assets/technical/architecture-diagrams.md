# Architecture Diagrams

System architecture patterns for AEO monitoring infrastructure.

Note: Diagrams use Mermaid. If Mermaid rendering is unavailable, treat them as conceptual flowcharts.

## Tier 1: API-First Architecture (Recommended)

### Overview

```mermaid
flowchart LR
  QB[Query bank\n250-500 queries\nby intent] --> ORCH[API orchestrator\nrate limiting\nretries + backoff\ncaching]
  ORCH --> STORE[Response store\nPostgreSQL / BigQuery]
  STORE --> ANALYSIS[Analysis layer\ncitation extraction\nbrand mentions\nSoM calculations]
  ANALYSIS --> DASH[Dashboards + alerts\nMetabase/Looker\nSlack/email]

  ORCH <--> APIS[Platform APIs\nPerplexity\nGemini\nClaude\nOpenAI]
```

### Component Details

**Query Bank**

- 250-500 queries organized by intent (informational, commercial, transactional)
- Include brand, competitors, integrations, pricing, and "best/vs" queries
- Refresh quarterly; track additions/removals as a versioned dataset

**API Orchestrator**

- Central coordinator for all platform calls
- Per-platform rate limiting and budgets
- Retries with exponential backoff + jitter
- Caching (24-48 hour TTL) to control costs
- Store full request metadata (model, params, timestamp, prompt version)

**Response Store**

- PostgreSQL for most cases; BigQuery for high volume analytics
- Store raw response, normalized fields, and extracted artifacts (citations, entities)
- Partition by date and platform for fast queries

**Analysis Layer**

- Citation extraction (native where available; otherwise parse/normalize)
- Brand mention detection (exact match + alias map; optional NER/LLM)
- Competitive tracking (brand/citation share per query group)
- Share of Model (SoM) and trend calculations

## Tier 2: Hybrid Architecture (API + Vendor Coverage)

Use when one or more target surfaces are not accessible via official APIs and you have a compliant vendor.

### Overview

```mermaid
flowchart LR
  QB[Query bank] --> ORCH[Orchestrator]
  ORCH <--> APIS[Official APIs]
  ORCH <--> VENDOR[Vendor data source\n(commercial coverage)]
  ORCH --> STORE[Response store]
  STORE --> ANALYSIS[Analysis]
  ANALYSIS --> DASH[Dashboard/alerts]
```

### When to Use

- You need citations from surfaces that do not have an official API
- You have legal/compliance approval for a vendor contract
- You accept dependency risk (vendor changes, coverage changes, pricing changes)

## Data Flow Diagram

### Query Processing Flow

```mermaid
sequenceDiagram
  participant S as Scheduler
  participant O as Orchestrator
  participant P as Platform API
  participant DB as Response Store
  participant A as Analyzer

  S->>O: Start run (run_id, query_set_version)
  O->>DB: Load active queries
  loop For each query (or batch)
    O->>P: Request (prompt, params, model)
    P-->>O: Response (text + citations/metadata)
    O->>DB: Store raw + normalized
    O->>A: Enqueue analysis job (response_id)
  end
  A->>DB: Write derived metrics (citations, mentions, SoM)
  DB-->>O: Run summary (coverage, errors, cost)
```

### Citation Extraction Flow

```mermaid
flowchart TD
  R[Raw response] --> DETECT{Citations available?}
  DETECT -->|Native list| NORM[Normalize URLs\ndedupe + canonicalize]
  DETECT -->|In text| PARSE[Parse URLs from text\nregex + cleanup]
  DETECT -->|None| EMPTY[Empty citations]
  NORM --> OUT[Write citations table + metrics]
  PARSE --> OUT
  EMPTY --> OUT
```

## Database Schema Diagram

### Entity Relationship

```mermaid
erDiagram
  QUERIES ||--o{ RESPONSES : has
  RESPONSES ||--o{ CITATIONS : contains
  RESPONSES ||--o{ BRAND_MENTIONS : contains

  QUERIES {
    int query_id PK
    string query_text
    string intent_category
    int priority
    bool active
    datetime created_at
  }

  RESPONSES {
    int response_id PK
    int query_id FK
    string platform
    string model_version
    json request_params
    text response_text
    json citations_json
    datetime timestamp
    string run_id
  }

  CITATIONS {
    int citation_id PK
    int response_id FK
    string url
    string domain
    int position
  }

  BRAND_MENTIONS {
    int mention_id PK
    int response_id FK
    string brand
    string mention_type
    string sentiment
  }
```

## Deployment Architecture

### Minimal (Serverless)

```mermaid
flowchart LR
  CRON[Scheduler\n(EventBridge/Cloud Scheduler)] --> FN[Serverless job\n(Lambda/Cloud Functions)]
  FN --> DB[(PostgreSQL/Supabase)]
  FN --> LOGS[Logs/metrics\n(CloudWatch/Stackdriver)]
```

### Standard (Container-Based)

```mermaid
flowchart LR
  CRON[Scheduler] --> JOB[Worker container\n(CronJob/Task)]
  JOB --> DB[(PostgreSQL)]
  JOB --> OBJ[(Object storage\nS3/GCS)]
  JOB --> OBS[Observability\nlogs + metrics]
```

### Enterprise (Kubernetes + Queue)

```mermaid
flowchart LR
  CRON[Scheduler] --> Q[(Queue\nSQS/Redis/Kafka)]
  Q --> W1[Worker pods\nN replicas]
  W1 --> DB[(PostgreSQL/BigQuery)]
  W1 --> OBS[Observability\nOpenTelemetry]
  DB --> DASH[BI dashboards]
```

## Integration Patterns

### Webhook Notifications

```mermaid
flowchart LR
  ANALYSIS[SoM + anomaly detection] --> ALERT{Trigger?}
  ALERT -->|Yes| WEBHOOK[Webhook\n(Slack/Teams/email)]
  ALERT -->|No| NOOP[No action]
```

### CRM Integration

```mermaid
flowchart LR
  METRICS[SoM + citation share\nby query group] --> MAP[Map to account/category]
  MAP --> CRM[CRM/RevOps system]
  CRM --> PLAY[Playbook\n(opportunity notes, enablement)]
```

## Scaling Considerations

### Horizontal Scaling

```mermaid
flowchart LR
  Q[(Queue)] --> W[Workers\n(per-platform pools)]
  W --> DB[(Primary store)]
  W --> DLQ[(Dead letter queue)]
```

### Queue-Based Processing

```mermaid
flowchart LR
  SRC[Query source\n(versioned query set)] --> Q[(Queue)]
  Q --> WP[Worker pool]
  WP --> DB[(DB)]
  DB --> ANA[Analysis jobs]
  ANA --> DB
```
