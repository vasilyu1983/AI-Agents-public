# Production Gotchas Documentation Guide

How to document platform-specific issues, known limitations, and production quirks that developers need to know.

---

## What Are Production Gotchas?

Production gotchas are:
- Platform-specific behaviors that differ from documentation
- Known limitations or edge cases
- Environment-specific configuration requirements
- "Tribal knowledge" that causes production incidents when forgotten

---

## Why Document Gotchas?

| Problem | Cost | Prevention |
|---------|------|------------|
| Repeated incidents | Hours of debugging | Document once, reference forever |
| Onboarding delays | Days of context-building | New devs find answers in docs |
| Knowledge silos | Single point of failure | Shared documentation |
| Post-incident amnesia | Same bugs recur | Permanent record |

---

## Gotcha Documentation Template

```markdown
## [Short Title]

**Severity**: Critical / High / Medium / Low
**Affects**: [service/component/environment]
**Last Verified**: YYYY-MM-DD

### The Problem

[Clear description of the unexpected behavior]

### Why It Happens

[Root cause explanation]

### The Fix / Workaround

[Step-by-step solution]

### How to Detect

[Symptoms, error messages, monitoring alerts]

### References

- [Link to related incident]
- [Link to upstream issue]
- [Link to documentation]
```

---

## Categories of Gotchas

### 1. Infrastructure Gotchas

```markdown
## AWS RDS Connection Limits

**Severity**: High
**Affects**: All services using RDS

### The Problem

RDS `db.t3.medium` has max 90 connections. With 3 replicas × 20 pool size = 60 connections per service. Two services = 120 connections → connection refused errors.

### The Fix

- Use `db.t3.large` (145 max connections) OR
- Reduce pool size to 15 per service OR
- Use RDS Proxy for connection pooling

### How to Detect

- Error: `FATAL: too many connections for role`
- CloudWatch: `DatabaseConnections` > 85
```

### 2. Third-Party API Gotchas

```markdown
## Stripe Webhook Retry Behavior

**Severity**: Medium
**Affects**: Payment processing

### The Problem

Stripe retries failed webhooks for up to 3 days with exponential backoff. If your endpoint returns 500 during deployment, you'll get duplicate events hours later.

### The Fix

1. Implement idempotency using `event.id`
2. Store processed event IDs in Redis (TTL: 72 hours)
3. Return 200 immediately, process async

### How to Detect

- Duplicate `payment_intent.succeeded` events
- Customer charged multiple times
```

### 3. Language/Framework Gotchas

```markdown
## Node.js Event Loop Blocking

**Severity**: High
**Affects**: API response times

### The Problem

Synchronous operations (JSON.parse on large payloads, crypto operations) block the event loop. A 50MB JSON parse blocks ALL requests for 200ms+.

### The Fix

- Stream large JSON with `JSONStream`
- Use worker threads for crypto
- Set payload limits: `express.json({ limit: '1mb' })`

### How to Detect

- P99 latency spikes
- Event loop lag > 100ms (measure with `perf_hooks`)
```

### 4. Database Gotchas

```markdown
## PostgreSQL VACUUM Not Running

**Severity**: Critical
**Affects**: Database performance

### The Problem

Autovacuum disabled on high-write tables causes table bloat. 10GB table becomes 100GB, queries slow 10x.

### The Fix

1. Enable autovacuum (never disable in prod)
2. Tune: `autovacuum_vacuum_scale_factor = 0.05`
3. Monitor: `pg_stat_user_tables.n_dead_tup`

### How to Detect

- Table size growing without data growth
- `SELECT pg_size_pretty(pg_total_relation_size('table_name'))`
```

### 5. Environment Gotchas

```markdown
## Docker DNS Resolution Delay

**Severity**: Medium
**Affects**: Container startup

### The Problem

First DNS lookup in container takes 5+ seconds if Docker's DNS isn't configured. Causes health check failures during deployment.

### The Fix

Add to `docker-compose.yml`:
```yaml
dns:
  - 8.8.8.8
  - 8.8.4.4
```

Or in Dockerfile:
```dockerfile
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### How to Detect

- Health checks fail on first attempt only
- `dig` shows 5+ second response times
```

---

## Where to Store Gotchas

### Option 1: Dedicated Gotchas File

```text
docs/
└── gotchas/
    ├── README.md           # Index of all gotchas
    ├── infrastructure.md   # AWS, GCP, infra gotchas
    ├── third-party.md      # API integrations
    ├── database.md         # DB-specific issues
    └── deployment.md       # CI/CD, container gotchas
```

### Option 2: Inline with Related Docs

```markdown
# Payment Service

## API Reference
...

## Known Issues & Gotchas

### Stripe Webhook Retries
[gotcha content]

### Currency Rounding
[gotcha content]
```

### Option 3: In CLAUDE.md

For critical gotchas that affect daily development:

```markdown
# Project CLAUDE.md

## Critical Gotchas

1. **RDS Connections**: Max 90 on t3.medium. Don't exceed 15 pool size.
2. **Stripe Webhooks**: Always idempotent. Check Redis before processing.
3. **Large JSON**: Never parse >1MB synchronously.
```

---

## Gotcha Review Process

### When to Add

- After every production incident
- When onboarding reveals undocumented behavior
- When code review catches a gotcha

### Review Checklist

- [ ] Clear, specific title
- [ ] Severity assigned
- [ ] Root cause explained
- [ ] Solution provided
- [ ] Detection method documented
- [ ] Last verified date set

### Maintenance

- Review quarterly: Are gotchas still relevant?
- Remove fixed issues (but keep in git history)
- Update when workarounds become permanent fixes

---

## Integration with Incident Management

### Post-Incident Template Addition

```markdown
## Incident Retro: [INC-123]

### Gotcha Documentation

**Should this be documented?** Yes / No

If yes:
- **Category**: Infrastructure / API / Framework / Database / Environment
- **Severity**: Critical / High / Medium / Low
- **Owner**: [who will write it]
- **Deadline**: [when]
```

### Link to Incidents

```markdown
## Memory Leak in Image Processing

**Related Incidents**:
- INC-456 (2024-03-15) - Initial discovery
- INC-489 (2024-04-02) - Recurrence, fix verified
```

---

## Anti-Patterns

### Don't Do This

```markdown
## Database Issues

Sometimes the database is slow. Check connections.
```

### Do This Instead

```markdown
## PostgreSQL Slow Queries After Bulk Insert

**Severity**: Medium
**Affects**: Reporting queries after ETL

### The Problem

After inserting 100K+ rows, queries using indexes on that table run 10x slower until autovacuum runs (can take hours).

### The Fix

Run `ANALYZE table_name` immediately after bulk insert:

```sql
INSERT INTO events SELECT ... FROM staging_events;
ANALYZE events;
```

### How to Detect

- Query times spike after ETL jobs
- `EXPLAIN ANALYZE` shows index scan with high row estimates
```

---

## Related Resources

- [writing-best-practices.md](writing-best-practices.md) - General documentation standards
- [changelog-best-practices.md](changelog-best-practices.md) - Tracking changes
- [adr-writing-guide.md](adr-writing-guide.md) - Architecture decisions
