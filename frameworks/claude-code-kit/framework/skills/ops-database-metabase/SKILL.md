---
name: ops-database-metabase
description: Metabase administration for secure connections, data modeling, performance tuning, dashboard reliability, alerting, and governance.
---

# Metabase Operations — Quick Reference

Use this skill to stand up and operate Metabase: connect data sources, model datasets, ship reliable dashboards, enforce permissions, and troubleshoot slow queries or broken alerts.

---

## When to Use This Skill

- Connect or audit Metabase data sources (PostgreSQL, MySQL, BigQuery, Snowflake, Redshift)
- Configure groups, collections, and row-level permissions
- Model cleaned datasets, metrics, and segments for self-serve analytics
- Build or triage dashboards (slow loads, stale data, broken filters)
- Configure caching, sync schedules, and background indexing
- Set up subscriptions/alerts and incident playbooks for outages
- Plan migrations, backups, and disaster recovery for the Metabase instance
- Embed dashboards in external applications (signed embedding, JWT)
- Audit query activity and enforce compliance requirements

---

## Quick Reference

| Task | Tool/Path | Action | When to Use |
|------|-----------|--------|-------------|
| Add data source | Admin → Databases | Verify SSL, time zone, "Use server SSL" enabled; click `Test` before Save | New connection or rotating credentials |
| Model a dataset | Browse → Model → + New Model | Define metadata (friendly names/descriptions), map FK relationships, hide PII columns | Improve self-serve accuracy and search |
| Speed up dashboard | Admin → Settings → Performance | Enable Query Caching, set cache TTL; turn on Field/Segment caching; adjust sync schedule | Slow dashboards or expensive queries |
| Fix slow question | Question → View Native Query → database IDE | Run `EXPLAIN ANALYZE` (DB), add indexes, simplify filters; verify timezone/CAST usage | High latency question or timeout |
| Permissions review | Admin → Permissions | Use groups + collections; deny by default; enable row-level filters; audit with Permission Graph | New teams, least-privilege enforcement |
| Alerts & subscriptions | Question → Alert / Dashboard → Subscription | Configure Slack/email cadence; set threshold conditions; include CSV/XLS export | Notify on KPI changes or SLA breaches |
| Audit & logging | Admin → Audit / application logs | Track who ran which queries, dashboard edits, login failures; export audit logs periodically | Compliance reviews, incident analysis |
| Embedding & tokens | Admin → Settings → Embedding / JWT | Use signed embedding; rotate embedding secret; scope collections carefully | External embeds or partner dashboards |
| Backup instance | CLI / API | Export questions/dashboards via API; backup H2 or external app DB | Pre-upgrade, disaster recovery |
| Upgrade Metabase | Admin → About / CLI | Check release notes; backup first; test in staging; use rolling restart for HA | Security patches, new features |

---

## Decision Tree: Dashboard/Question is Slow

```text
Dashboard/question slow?
    ├─ Native SQL?
    │   ├─ Run `EXPLAIN ANALYZE` in DB
    │   ├─ Add missing indexes
    │   ├─ Simplify JOINs or subqueries
    │   └─ Check for implicit type casts
    │
    ├─ GUI question?
    │   ├─ Too many joined tables? → Reduce joins, use models
    │   ├─ Too many columns? → Select only needed fields
    │   ├─ Missing filters? → Add date range / partition filters
    │   └─ Large result set? → Add LIMIT or pagination
    │
    ├─ Cache disabled/expired?
    │   ├─ Enable query caching (Admin → Performance)
    │   ├─ Set appropriate TTL (balance freshness vs. speed)
    │   └─ Consider dashboard-level caching
    │
    ├─ Sync/metadata stale?
    │   ├─ Run manual sync (Admin → Databases → Sync)
    │   ├─ Rebuild Field Values
    │   └─ Check sync schedule frequency
    │
    ├─ Source DB overloaded?
    │   ├─ Check DB metrics (CPU, connections, locks)
    │   ├─ Add read replica for analytics
    │   └─ Limit Metabase concurrency (connection pool)
    │
    └─ Network/region mismatch?
        ├─ Check latency between Metabase and DB
        └─ Deploy Metabase closer to data source
```

## Decision Tree: Permission Denied / Access Issues

```text
User can't see dashboard/question?
    ├─ Check user's group membership (Admin → People)
    │
    ├─ Check collection permissions
    │   ├─ User's group needs "View" or "Curate" on collection
    │   └─ Nested collections inherit unless overridden
    │
    ├─ Check database/schema permissions
    │   ├─ Group needs access to underlying database
    │   └─ Schema-level restrictions may block queries
    │
    ├─ Row-level security active?
    │   ├─ Check sandboxing rules (Admin → Permissions → Data)
    │   └─ Verify user attribute matches sandbox filter
    │
    └─ Question uses restricted model/table?
        └─ Grant group access to underlying data source
```

## Decision Tree: Alerts Not Firing

```text
Alert not triggering?
    ├─ Check alert configuration
    │   ├─ Threshold condition correct?
    │   ├─ Schedule frequency appropriate?
    │   └─ Alert enabled (not paused)?
    │
    ├─ Check delivery channel
    │   ├─ Slack: Webhook URL valid? Channel exists?
    │   ├─ Email: SMTP configured? User email verified?
    │   └─ Test channel independently
    │
    ├─ Question returning expected data?
    │   ├─ Run question manually
    │   ├─ Check for errors in query
    │   └─ Verify data freshness
    │
    └─ Metabase scheduler running?
        ├─ Check application logs for scheduler errors
        └─ Verify background jobs not stuck
```

---

## Core Capabilities

**1. Data Source Management**
- Connect to 20+ databases (PostgreSQL, MySQL, BigQuery, Snowflake, Redshift, etc.)
- SSH tunneling for secure connections
- Read replica routing for analytics workloads
- Connection pooling and timeout configuration

**2. Data Modeling**
- Create reusable models from complex queries
- Define metrics (SUM, AVG, COUNT with filters)
- Create segments (reusable filter conditions)
- Set field semantics (currency, percentage, category)

**3. Permissions & Governance**
- Group-based access control
- Collection hierarchy with inheritance
- Row-level security (sandboxing)
- Audit logging for compliance

**4. Performance Optimization**
- Query caching with configurable TTL
- Database-level query analysis
- Sync scheduling for metadata freshness
- Connection pool tuning

**5. Embedding & Integration**
- Signed static embedding
- Full-app embedding with JWT SSO
- API access for automation
- Webhook integrations

---

## Common Patterns

### New Database Connection Checklist

1. **Pre-connection**
   - Gather credentials (host, port, database, user, password)
   - Verify network access (firewall rules, VPN if needed)
   - Check SSL certificate requirements

2. **Connection setup**
   - Admin → Databases → Add database
   - Select database type
   - Enter connection details
   - Enable SSL if required
   - Set timezone to match database

3. **Post-connection**
   - Click "Test connection"
   - Run initial sync
   - Review discovered tables
   - Hide sensitive tables/columns

### Dashboard Performance Checklist

1. **Question-level**
   - Use models instead of raw tables
   - Add appropriate filters (date ranges)
   - Limit columns to what's displayed
   - Avoid N+1 query patterns

2. **Dashboard-level**
   - Enable dashboard caching
   - Use filter widgets instead of per-card filters
   - Limit cards to 10-15 per dashboard
   - Use tabs for complex dashboards

3. **Infrastructure-level**
   - Configure read replicas
   - Tune connection pool size
   - Set up query timeout limits
   - Monitor slow query logs

---

## Navigation

**Resources**
- [resources/operational-patterns.md](resources/operational-patterns.md) — Setup checklists, modeling standards, permissions matrices, caching strategies, troubleshooting drills, and DR procedures

**Templates**
- [templates/connection-checklist.md](templates/connection-checklist.md) — Database connection setup
- [templates/dashboard-request.md](templates/dashboard-request.md) — Dashboard requirement intake
- [templates/incident-playbook.md](templates/incident-playbook.md) — Outage response procedures

**Data**
- [data/sources.json](data/sources.json) — Curated external references

**Related Skills**
- [../ops-database-sql/SKILL.md](../ops-database-sql/SKILL.md) — Query tuning, indexing, database operations
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Infrastructure, backups, monitoring, and incident response
- [../ai-ml-data-science/SKILL.md](../ai-ml-data-science/SKILL.md) — Metrics definitions, modeling, and analytics workflows
- [../quality-observability-performance/SKILL.md](../quality-observability-performance/SKILL.md) — Monitoring, alerting, and SLO management

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| One giant dashboard | Slow load, overwhelming UX | Split into focused dashboards with tabs |
| Raw table queries everywhere | Inconsistent metrics, slow | Create models for common patterns |
| No caching | Every load hits database | Enable caching with appropriate TTL |
| Admin access for all | Security risk, no audit trail | Use groups with least privilege |
| No row-level security | Data leakage risk | Implement sandboxing for sensitive data |
| Skipping sync schedule | Stale metadata, broken autocomplete | Set sync frequency based on schema change rate |

---

## Operational Guide

See [resources/operational-patterns.md](resources/operational-patterns.md) for:
- Detailed setup checklists by database type
- Modeling standards and naming conventions
- Permissions matrices and governance workflows
- Caching configuration by use case
- Troubleshooting decision trees
- Disaster recovery procedures
- Upgrade and migration playbooks
