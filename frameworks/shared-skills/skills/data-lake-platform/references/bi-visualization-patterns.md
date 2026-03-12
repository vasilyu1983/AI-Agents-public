# BI & Visualization Patterns

## Overview

Data visualization layer for lakehouse architecture: Metabase, Apache Superset, Grafana.

---

## Tool Selection

| Tool | Best For | Data Source | Self-Hosted | License |
|------|----------|-------------|-------------|---------|
| **Metabase** | Business dashboards, self-serve analytics | SQL databases, BigQuery, Snowflake | Yes | AGPL |
| **Apache Superset** | Advanced analytics, SQL Lab | SQL, Trino, Druid, ClickHouse | Yes | Apache 2.0 |
| **Grafana** | Time-series, infrastructure metrics | Prometheus, InfluxDB, Elasticsearch | Yes | AGPL |

### Decision Tree

```text
Need visualization?
    ├─ Business dashboards for non-technical users?
    │   └─ Metabase (intuitive UI, question builder)
    │
    ├─ Advanced SQL analytics for analysts?
    │   └─ Apache Superset (SQL Lab, custom charts)
    │
    ├─ Time-series and infrastructure metrics?
    │   └─ Grafana (Prometheus, real-time alerting)
    │
    └─ Embedded analytics in product?
        ├─ Metabase (signed embedding)
        └─ Superset (embedded dashboards)
```

---

## Metabase Operations

### Quick Reference

| Task | Action | When to Use |
|------|--------|-------------|
| Add data source | Admin → Databases → Add | New connection |
| Model dataset | Browse → Model → + New Model | Self-serve accuracy |
| Speed up dashboard | Admin → Settings → Performance → Enable caching | Slow dashboards |
| Fix slow query | View SQL → EXPLAIN ANALYZE in DB | High latency |
| Permissions | Admin → Permissions → Groups | Access control |
| Alerts | Question → Alert | KPI notifications |

### Connection Checklist

1. **Pre-connection**
   - Gather credentials (host, port, database, user, password)
   - Verify network access (firewall, VPN)
   - Check SSL certificate requirements

2. **Connection setup**
   - Admin → Databases → Add database
   - Enable SSL if required
   - Set timezone to match database
   - Test connection before saving

3. **Post-connection**
   - Run initial sync
   - Hide sensitive tables/columns
   - Add friendly names and descriptions

### Performance Optimization

```text
Dashboard slow?
    ├─ Enable query caching (Admin → Performance)
    │   └─ Set TTL aligned to data freshness SLA
    │
    ├─ Optimize underlying queries
    │   ├─ Run EXPLAIN ANALYZE in database
    │   ├─ Add missing indexes
    │   └─ Reduce joins, use models
    │
    ├─ Check sync/metadata freshness
    │   └─ Admin → Databases → Sync
    │
    └─ Limit dashboard complexity
        ├─ Max 10-15 cards per dashboard
        └─ Use tabs for complex dashboards
```

### Permissions Model

```text
Groups → Collections → Row-Level Security

Group: "Sales Team"
├─ Collection: "Sales Dashboards" → View
├─ Database: "sales_db" → Read (schema: gold)
└─ Row-level: WHERE region = {{user.region}}
```

---

## Apache Superset Operations

### Quick Reference

| Task | Action | When to Use |
|------|--------|-------------|
| Add database | Settings → Database Connections | New data source |
| Create chart | Charts → + Chart | New visualization |
| SQL exploration | SQL Lab → New Query | Ad-hoc analysis |
| Create dataset | Datasets → + Dataset | Reusable data model |
| Cache results | Dashboard → Edit → Cache timeout | Performance |
| Access control | Security → List Roles | Permissions |

### Connection Configuration

```python
# SQLAlchemy URI examples

# ClickHouse
clickhouse+native://user:pass@host:9000/database

# Trino
trino://user@host:8080/catalog/schema

# PostgreSQL
postgresql://user:pass@host:5432/database

# BigQuery
bigquery://project/dataset
```

### Dataset Best Practices

1. **Virtual datasets** - SQL-based, flexibility
2. **Physical datasets** - Direct table, caching
3. **Calculated columns** - Derived metrics
4. **Semantic layer** - Consistent definitions

### Security Model

```yaml
Roles:
  - Admin: Full access
  - Alpha: Can access SQL Lab, create charts
  - Gamma: Dashboard viewers only
  - Public: Anonymous access (if enabled)

Row-level security:
  - Table: orders
  - Filter: user_id = {{ current_user_id() }}
```

---

## Grafana Operations

### Quick Reference

| Task | Action | When to Use |
|------|--------|-------------|
| Add data source | Configuration → Data sources | Connect Prometheus/InfluxDB |
| Create dashboard | + → Dashboard | New visualization |
| Import dashboard | + → Import → Dashboard ID | Community dashboards |
| Set alert | Panel → Alert → Create alert | Threshold notifications |
| Variables | Dashboard settings → Variables | Dynamic filtering |

### Data Source Configuration

```yaml
# Prometheus
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true

# ClickHouse
  - name: ClickHouse
    type: grafana-clickhouse-datasource
    url: http://clickhouse:8123
    jsonData:
      defaultDatabase: analytics
```

### Dashboard Patterns

**Infrastructure Monitoring:**
- CPU, Memory, Disk usage
- Request latency (p50, p95, p99)
- Error rates and availability
- Queue depths and backlogs

**Data Pipeline Monitoring:**
- Row counts per table/partition
- Pipeline execution times
- Data freshness (time since last update)
- Quality check pass/fail rates

### Alert Configuration

```yaml
# Example: Data freshness alert
alert:
  name: Stale Data Alert
  conditions:
    - query: A
      reducer: last
      evaluator:
        type: gt
        params: [3600]  # > 1 hour
  frequency: 5m
  notifications:
    - slack-alerts
```

---

## Integration Patterns

### Lakehouse → BI Stack

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Bronze    │────→│   Silver    │────→│    Gold     │
│  (Iceberg)  │     │  (Iceberg)  │     │  (Iceberg)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────────────────┤
                    │                         │
              ┌─────▼─────┐           ┌───────▼───────┐
              │ ClickHouse│           │    Metabase   │
              │ (Queries) │───────────│  (Dashboards) │
              └───────────┘           └───────────────┘
```

### Semantic Layer Pattern

```text
dbt/SQLMesh Models → Metabase/Superset Metrics → Dashboards

Benefits:
- Single source of truth for metric definitions
- Consistent calculations across dashboards
- Version-controlled business logic
```

### Embedding Pattern

```python
# Metabase signed embedding
import jwt

payload = {
    "resource": {"dashboard": 123},
    "params": {"customer_id": user.customer_id},
    "exp": time.time() + 600  # 10 minutes
}
token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
iframe_url = f"{METABASE_URL}/embed/dashboard/{token}"
```

---

## Performance Best Practices

### DO

1. **Use materialized views** - Pre-aggregate heavy queries
2. **Enable caching** - TTL based on data freshness
3. **Limit cards per dashboard** - 10-15 max
4. **Create semantic models** - Reduce ad-hoc complexity
5. **Index filter columns** - Speed up WHERE clauses
6. **Use read replicas** - Offload BI queries

### DON'T

1. **Don't SELECT *** - Project only needed columns
2. **Don't skip caching** - Every load hits database
3. **Don't allow unlimited native SQL** - Security risk
4. **Don't ignore slow query logs** - Monitor continuously
5. **Don't embed without row-level security** - Data leakage risk

---

## Templates

- [Metabase connection checklist](../assets/visualization/metabase/connection-checklist.md)
- [Metabase dashboard request](../assets/visualization/metabase/dashboard-request.md)
- [Metabase incident playbook](../assets/visualization/metabase/incident-playbook.md)
