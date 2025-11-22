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

---

## Decision Tree: Dashboard/Question is Slow

```text
Dashboard/question slow?
    ├─ Native SQL? → Run `EXPLAIN ANALYZE`; add index or simplify query
    ├─ GUI question? → Check joined tables count; reduce columns; add filters
    ├─ Cache disabled/expired? → Enable caching; lower TTL for fresher data
    ├─ Sync/metadata stale? → Run manual sync + analyze; rebuild Field Values
    ├─ Source DB overloaded? → Check DB metrics; add read replica or limit concurrency
    └─ Network/region mismatch? → Align Metabase region with database region
```

---

## Navigation

**Resources**
- [resources/operational-patterns.md](resources/operational-patterns.md)

**Templates**
- [templates/connection-checklist.md](templates/connection-checklist.md)
- [templates/dashboard-request.md](templates/dashboard-request.md)
- [templates/incident-playbook.md](templates/incident-playbook.md)

**Related Skills**
- [../ops-database-sql/SKILL.md](../ops-database-sql/SKILL.md) — Query tuning, indexing, database operations
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Infrastructure, backups, monitoring, and incident response
- [../ai-ml-data-science/SKILL.md](../ai-ml-data-science/SKILL.md) — Metrics definitions, modeling, and analytics workflows

---

## Operational Guide

See [resources/operational-patterns.md](resources/operational-patterns.md) for setup checklists, modeling standards, permissions matrices, caching strategies, troubleshooting drills, and DR procedures.
