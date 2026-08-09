# dlt Pipeline Template

*Purpose: Build dlt (data load tool) pipelines with the operational rules that make them safe to re-run, debug, and reset.*

## Installation

```bash
pip install "dlt[postgres]"   # or [snowflake] | [bigquery] | [duckdb]
```

## Project Structure

```
my_pipeline/
├── .dlt/
│   ├── config.toml       # runtime + source config
│   └── secrets.toml      # credentials (gitignored)
├── pipelines/
│   └── github_pipeline.py
└── requirements.txt
```

## Core Mental Model

- **Pipeline** = code + persistent local state (schemas, traces, load artifacts) tied to `pipeline_name`.
- **Resource** = function that yields data; carries hints (`table_name`, `primary_key`, `merge_key`, `write_disposition`, `incremental`).
- **`pipeline_name` is durable identity**. Reusing a name reuses state and schema history. Treat it like a primary key, not a label.

## Basic Pipeline

```python
import dlt
from dlt.sources.rest_api import rest_api_source

pipeline = dlt.pipeline(
    pipeline_name="github_data",   # stateful identity — do not rename casually
    destination="postgres",
    dataset_name="source_github",  # convention: source_*
)

source = rest_api_source({
    "client": {"base_url": "https://api.github.com/repos/dlt-hub/dlt/"},
    "resources": ["issues", "pulls"],
})

load_info = pipeline.run(source)
print(load_info)
```

## Write Disposition — Decision Matrix

Pick *before* writing the resource. Wrong choice = wrong data shape, hard to undo.

| Disposition | Use when | Avoid when |
|---|---|---|
| `merge` | Mutable rows + reliable `primary_key` (and/or `merge_key`) + incremental cursor | No stable key; insert-only stream |
| `append` | Immutable event stream, insert-only | Source emits updates or deletes |
| `replace` | Small dimension tables; one-off backfill; explicit full refresh | Long/large tables on a recurring schedule |

For long or large tables: **default to incremental**, not repeated full replaces.

## Resource Hints — Use `apply_hints`

Prefer explicit hints over custom state management. Set them via `@dlt.resource(...)` args or `resource.apply_hints(...)`:

```python
resource.apply_hints(
    write_disposition="merge",
    primary_key="id",
    merge_key="updated_at",
    incremental=dlt.sources.incremental("updated_at"),
    table_name="issues",
)
```

Avoid hand-rolled state tracking unless the source genuinely needs logic outside `dlt.sources.incremental(...)`.

## Incremental Loading

- Use `dlt.sources.incremental(cursor_column, ...)` when the source has a reliable timestamp / monotonic ID / version cursor.
- Pair `incremental` with `merge` for **mutable** large tables.
- Pair `incremental` with `append` for **insert-only** streams.
- Keep any lookback / lag window small and only when the source needs it.

## Refresh & Reset — Don't Hand-Clean Tables

When a cursor-based load needs a clean replay, use built-in refresh modes; do not delete tables manually.

| Mode | Effect |
|---|---|
| `refresh="drop_sources"` | Reset all source state and drop all related tables |
| `refresh="drop_resources"` | Reset selected resources and drop their tables |
| `refresh="drop_data"` | Truncate selected tables, reset resource state, keep schema |

```python
load_info = pipeline.run(source, refresh="drop_data")
```

## Pipeline Pattern Selection

Classify *before* coding:

- **Full-load script** — small dim-like tables or explicit rebuilds. `replace`.
- **Incremental realtime** — large/mutable tables. `merge` + `incremental`. The default for big sources.
- **Reusable source package** — multiple scripts share extraction logic. Extend the existing package; do not fork it into a standalone script.
- **Custom API source** — needs pagination, lookback, or custom state inspection in addition to `dlt.sources.incremental`.
- **Multi-resource pipeline** — one pipeline orchestrates many resources across endpoints/projects.

## Configuration

```toml
# .dlt/config.toml
[destination.postgres]
credentials = "postgres://user:password@localhost:5432/db"
```

```toml
# .dlt/secrets.toml — gitignored
[sources.github.credentials]
access_token = "ghp_..."
```

## Debugging — Always Suspect State First

When behavior changes unexpectedly across runs, look at pipeline state before changing code:

```bash
dlt pipeline <pipeline_name> run
dlt pipeline <pipeline_name> status
dlt pipeline <pipeline_name> logs
```

If upstream docs and a working local example disagree, follow the local example unless it's clearly broken — `dlt` versions move faster than docs.

## Best Practices

- Lock secrets to `.dlt/secrets.toml`; never commit.
- Treat `pipeline_name` and `dataset_name` as durable identifiers. Renames cause silent state drift.
- Default large/mutable tables to `merge` + incremental.
- Reach for `refresh=` before manual destination cleanup.
- Prefer `apply_hints` over inventing state handling.
- Keep ingestion (`dlt`) scope separate from downstream transformation (SQLMesh / dbt). Don't mix them in one pipeline file.
