# ClickHouse Materialized Views

Use when pre-aggregating or transforming data inside ClickHouse for serving. Most MV bugs come from treating an incremental MV as a stored query. It is an insert trigger.

## Semantics You Must Design For

An incremental materialized view runs its `SELECT` **over each inserted block only**, then inserts the result into its target table. Consequences:

1. **It never sees existing data.** Rows already in the source at creation time are not processed, so backfill is always a separate step (below).
2. **`GROUP BY` aggregates one insert block at a time.** The target therefore holds many partial rows per key. The target engine must finish the aggregation at merge time (`SummingMergeTree` / `AggregatingMergeTree`), and every read must re-aggregate (`sum()`, `-Merge` + `GROUP BY`) because merges may not have run.
3. **Only inserts into the `FROM` table trigger it.** In a join, the right-hand table is read in full on every insert, which is slow, and changes to the right-hand table never update the target.
4. **Mutations and merges do not propagate.** `ALTER ... DELETE/UPDATE`, lightweight deletes, TTL drops and `ReplacingMergeTree` dedup on the source leave the target untouched. An MV over a CDC/`ReplacingMergeTree` source counts **every version** of a row, so sums and counts are overstated. Aggregate CDC data with a refreshable MV or a scheduled rebuild instead.
5. **Insert failures are partial.** If an MV fails, the client sees an error, but the source block and earlier MVs may already be written. A client retry can double-count targets. Make retries idempotent with insert deduplication, including for dependent views (`deduplicate_blocks_in_dependent_materialized_views`; confirm the setting and its default for your version), or with an `insert_deduplication_token`.

Always use `TO <target_table>`. With an implicit inner table, dropping the MV drops the data, and you cannot `ALTER` or backfill the storage directly.

## Distinct Counts and Non-Additive Metrics

`uniq()`, averages and quantiles cannot be summed across partial rows. Storing `uniq(user_id)` in a `SummingMergeTree` and reading it back with `sum()` or `max()` gives wrong answers, and the error grows with every insert. Store aggregate **states**:

```sql
CREATE TABLE gold.hourly_events (
    hour         DateTime,
    event_type   LowCardinality(String),
    events       SimpleAggregateFunction(sum, UInt64),
    users        AggregateFunction(uniq, UInt64),
    amount_p95   AggregateFunction(quantile(0.95), Decimal(18, 2))
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(hour)
ORDER BY (event_type, hour);

CREATE MATERIALIZED VIEW gold.hourly_events_mv TO gold.hourly_events AS
SELECT toStartOfHour(created_at) AS hour, event_type,
       count() AS events, uniqState(user_id) AS users,
       quantileState(0.95)(amount) AS amount_p95
FROM silver.events
GROUP BY hour, event_type;

-- Every read re-aggregates:
SELECT hour, event_type, sum(events), uniqMerge(users), quantileMerge(0.95)(amount_p95)
FROM gold.hourly_events
WHERE hour >= now() - INTERVAL 1 DAY
GROUP BY hour, event_type;
```

Rolling hourly states up to daily works by merging states (`uniqMergeState(users)` into a daily `AggregatingMergeTree`). Taking `max()` of hourly distinct counts undercounts.

## Backfill Without Gaps or Double Counts

`POPULATE` is a trap: rows inserted into the source while it runs are lost, and it cannot be resumed. Use a cutover boundary instead:

1. Choose a boundary `T` slightly in the future, e.g. the next hour start.
2. Create the MV with `WHERE created_at >= T` so it only handles data from `T` onward.
3. After `T` has passed, backfill `created_at < T` with `INSERT INTO target SELECT ... WHERE created_at < T`, one partition at a time. For restartable, atomic backfills, load each partition into a staging table and `ALTER TABLE target REPLACE PARTITION ... FROM staging`.
4. Late rows with `created_at < T` that arrive after the backfill are missed. Either keep a late-data window and re-backfill it, or choose `T` on ingest time instead of event time.

Recreating or changing an MV follows the same rule. Between `DROP VIEW` and `CREATE`, inserts are not captured, so create the new MV first (with a boundary), then drop the old one.

## Refreshable Materialized Views

A refreshable MV (`REFRESH EVERY ...`) re-runs the full query on a schedule and replaces the target, or appends to it in append mode. Choose it over an incremental MV when:

- the source is updated or deleted in place (CDC, `ReplacingMergeTree`), or the logic needs joins where either side changes;
- the result is small relative to the scan and minutes of staleness are acceptable.

Check that your release treats refreshable MVs as production-ready (release notes). Monitor them in `system.view_refreshes`: last success, last exception, next run. A failed refresh keeps serving the previous result, so alert on staleness, not only on errors.

## Chains and Fan-Out

- Several MVs on one source each run on every insert. Insert latency and failure surface grow with each one, so keep the count small and drop unused views.
- Chains (MV -> table -> MV) work because each stage triggers on blocks inserted into its own source, not on merged data. Every stage must still re-aggregate on read. Keep chains to two or three stages; debugging a wrong number through five stages is expensive.
- Do not use `FINAL` inside an MV's `SELECT`: it applies only to the inserted block and does nothing useful there.

## Verify

- Reconcile each MV target against a direct query on the source for a closed time window (for example yesterday): the counts, sums and `uniqExact` spot checks must match within the approximation error of `uniq`.
- After a backfill, check there is no gap and no overlap at boundary `T`: compare per-hour counts across `T` with the source.
- Retry one ingestion batch on purpose and confirm the target totals do not change.
- List views and their targets with `SELECT name, as_select FROM system.tables WHERE engine = 'MaterializedView'`, and check that every view writes `TO` an explicit table.
