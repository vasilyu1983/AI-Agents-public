# dlt Incremental and Merge Template

Use when a dlt resource loads only new or changed rows. This file owns the dlt rules for cursors, merge keys, deletes, late data, and backfill; other dlt templates link here. Engine-agnostic strategy (CDC vs cursor vs snapshot diff) is in [template-incremental-loading.md](../../cross-platform/template-incremental-loading.md).

## Cursor Rules

- Declare the incremental as a **default argument** of the resource function. Created inside the body, it is not bound to pipeline state and every run starts from `initial_value`.
- Filter the source with `start_value` (the cursor at run start). dlt also filters yielded rows itself, but pushing the filter to the source is what saves the scan.
- A usable cursor is non-null, never moves backwards for a row, and is set by the source system (not by a client clock). If rows can be committed with an older timestamp than rows already read (long transactions, replicas, batch back-dating), a pure cursor will skip them: add a lookback window or use CDC.
- `initial_value` is where history starts: use a placeholder (`"<history_start>"`) or a relative expression, never a literal copied from an example.
- Null cursors: decide explicitly (include, exclude, or fail). Check the incremental options in the dlt docs for the default; do not let nulls vanish silently.

```python
@dlt.resource(primary_key="id", write_disposition="merge")
def orders(
    updated_at=dlt.sources.incremental("updated_at", initial_value="<history_start>"),
):
    yield from fetch_orders(updated_since=updated_at.start_value)  # push filter to source
```

## Boundary Rows and Duplicates

- dlt compares with `>=` by default, so rows equal to the last cursor value are read again. It de-duplicates those boundary rows using the resource `primary_key` (or a row hash when there is none). Setting the incremental's `primary_key=()` disables that de-duplication.
- With `append`, anything re-read outside the boundary (lookback windows, replays) becomes a duplicate row. Use `merge` with a `primary_key` whenever the window can overlap.

## Merge Strategies

| Strategy | Behaviour | Use when |
|---|---|---|
| `delete-insert` (default) | Deletes destination rows whose `primary_key` or `merge_key` appears in the load, then inserts | General upserts; replacing whole partitions |
| `upsert` | Row-level update-or-insert on `primary_key` | Destinations that support it; large tables where delete-insert is costly |
| `scd2` | Keeps history with validity columns | You need past versions of a row |

```python
@dlt.resource(write_disposition={"disposition": "merge", "strategy": "scd2"}, primary_key="id")
```

- `primary_key` identifies a row. `merge_key` identifies a **slice to replace**: every destination row whose `merge_key` value appears in the load is deleted first. Use it for "reload this day/partition" (`merge_key="event_date"`).
- Trap: `merge_key="updated_at"` (a change timestamp) is wrong. It deletes unrelated rows that share a timestamp and does nothing to track changes; the cursor does that.
- Several versions of one key in a single load: `delete-insert` keeps one per `primary_key`. Set the `dedup_sort` column hint on the version column so it keeps the newest, not an arbitrary one.

## Deletes

- A cursor never sees hard deletes: the row is gone from the source. Options, in order of preference: CDC (see [database sources](template-dlt-database-source.md)), a source soft-delete flag, or a periodic full snapshot compared with the destination.
- Soft-delete flag propagated as a real delete: mark the column with the `hard_delete` hint on a `merge` resource, and rows with a true value are removed from the destination instead of loaded.
- Keep a soft-delete column as data (no hint) when consumers need deletion history.

## Late Data and Lookback

- Size the lookback from measured lateness (max or high percentile of commit time minus cursor time), not a guess. Too small skips rows; too large re-reads cost.
- Implement it with the incremental's lag option if your dlt version has one (check the docs), otherwise subtract the window from `start_value` in the source query. Either way the resource must be `merge`, because the window re-reads rows.

## Backfill and Replay

- Backfill a bounded range with `initial_value` + `end_value`. When `end_value` is set, dlt does not advance the stored cursor, so backfill chunks can run beside the scheduled incremental without corrupting it.
- Split long histories into chunks (for example per month) so a failure repeats one chunk, not the whole history.
- Full replay: `refresh="drop_data"` for the affected resources (see [template-dlt-pipeline.md](template-dlt-pipeline.md#refresh-and-reset-do-not-hand-clean-tables)). Do not edit or delete state by hand.
- `row_order` (`"asc"` or `"desc"`) lets dlt stop reading once rows leave the range; set it only when the source really returns rows ordered by the cursor, or the read stops early and loses rows.

## Parent-Child Resources

A child resource driven by a parent (transformer) does not inherit the parent's cursor. Either give the child its own incremental on its own cursor, or make it `merge` and accept re-reading children of every changed parent.

## Verify

- [ ] Run twice with no source changes: the second run loads zero rows.
- [ ] Source count for the window equals destination count; `SELECT key, count(*) ... HAVING count(*) > 1` returns nothing on the merge table.
- [ ] `max(cursor)` in the destination matches the stored cursor (`dlt pipeline <name> info`), and lags the source by no more than the schedule plus lookback.
- [ ] A deleted source row disappears (or is flagged) after the next run, if deletes are in scope.
- [ ] Alert when the cursor has not advanced for longer than the expected update interval (stalled source or stuck state).
