# BI and Visualization Patterns

Put a BI layer on the lake without turning it into the metric source of truth. Metabase specifics: `data-metabase` skill and the templates in `../assets/visualization/metabase/`. Metric definitions: `data-analytics-engineering` (semantic layer).

## Tool Selection

| Need | Default |
|------|---------|
| Business dashboards and self-serve questions for non-technical users | Metabase |
| Analyst SQL exploration and custom charts | Apache Superset (SQL Lab) |
| Time-series, infrastructure, and pipeline-health monitoring with alerting | Grafana |
| Embedded analytics in a product | Metabase signed embedding or Superset embedded dashboards |

Check each tool's license and edition terms before embedding it in a commercial product; editions gate features such as row-level permissions and white-labeling.

## Architecture Rules

- BI reads **gold** tables or a serving engine (ClickHouse/StarRocks), never bronze/silver.
- Metrics are defined once, upstream (dbt/SQLMesh semantic layer or BI models built on gold), not re-derived per dashboard.
- Point BI at a read replica or serving engine when dashboard load competes with pipelines.
- Keep native-SQL access restricted to analyst groups; unrestricted native SQL bypasses table/row permissions.

## Performance

1. Pre-aggregate heavy queries (materialized views, rollup tables) before adding caching.
2. Cache with a TTL aligned to the data's freshness SLA — longer TTLs show stale numbers, shorter ones buy nothing.
3. Keep dashboards to roughly 10-15 cards; each card is a query per load. Use tabs for more.
4. Diagnose slow cards with the database's `EXPLAIN` on the generated SQL, not in the BI tool.
5. Project only needed columns; filter on partition/sort columns.

## Security

- Permissions: groups -> collections -> data access (schema-level, gold only) -> row-level filters bound to user attributes.
- **Signed embedding**: sign the token server-side with a short expiry (minutes); lock tenant parameters (e.g. `customer_id`) inside the signed payload so the client cannot change them. Never embed without row-level scoping.
- Hide sensitive tables/columns at sync time, not per dashboard.

## Pipeline-Health Dashboards (Grafana)

Track per table/partition: row counts, pipeline run duration, freshness (time since last successful load), and quality-check pass/fail. Alert on freshness beyond the SLA and on sudden row-count drops, with evaluation frequency well below the SLA.
