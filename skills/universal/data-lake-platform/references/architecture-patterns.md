# Data Lake Architecture Patterns

Pick the layering and processing pattern. Default: **medallion layers on a lakehouse (open table format + catalog)**; add mesh ownership as the org scales; add a streaming path only when a real-time requirement is proven.

## Choosing

| Factor | Medallion | Data Mesh | Lambda | Kappa |
|--------|-----------|-----------|--------|-------|
| What it decides | Quality layers | Ownership model | Batch + speed paths | Stream-only path |
| Real-time need | Low-medium | Varies | High, with batch correction | High |
| Operational cost | Low | High (org change) | High (two codebases) | Medium (replayable log required) |
| Governance | Central | Federated | Central | Central |

These are not exclusive: a mesh domain usually runs medallion layers internally, on a lakehouse.

## Medallion (Bronze / Silver / Gold)

| Layer | Contract | Write mode | Retention |
|-------|----------|-----------|-----------|
| Bronze | Raw as received + ingestion metadata (`_ingested_at`, `_source`, `_batch_id`) | Append-only, schema-on-read | Long enough to replay silver from scratch |
| Silver | Deduplicated, typed, validated; schema enforced | Idempotent merge on a business key | Months to years |
| Gold | Business-aligned marts, dimensional or wide tables | Rebuildable from silver | Per consumer need |

Rules:

- Bronze is the replay source: never mutate it in place; partition by ingestion date so late data never rewrites old partitions.
- Silver dedup key and ordering column (e.g. `updated_at`) are explicit; merges must be idempotent so a rerun yields the same table.
- Gold must be fully rebuildable from silver; if it is not, it is silver with another name.
- Quarantine rows that fail validation instead of dropping them silently.
- Blueprint: [template-medallion-architecture.md](../assets/cross-platform/template-medallion-architecture.md).

## Data Mesh

Domain ownership of data products, a self-serve platform, and federated governance. Adopt when a central data team is the bottleneck across several business domains with their own engineers; otherwise it adds coordination cost without payoff. Readiness, product specs, and migration: [data-mesh-patterns.md](data-mesh-patterns.md).

## Lambda

Speed layer (e.g. Kafka -> Flink) serves approximate recent results; batch layer recomputes ground truth and overwrites the speed results; a serving layer merges both.

- Use only when real-time views are required **and** the stream path cannot be made exact (e.g. late data beyond any practical watermark).
- Cost: two implementations of the same logic that drift. Prefer kappa when the log is replayable.

## Kappa

Single stream path: durable log (Kafka) -> stream processor (Flink) -> table format -> serving. Reprocessing = replay the log into a new table version.

- Requires log retention (or tiered storage/lake archive) covering the longest reprocessing window.
- Stream semantics and exactly-once sinks: `data-streaming` skill.

## Lakehouse

Open table format (ACID, schema evolution, time travel) over object storage, one catalog, many engines. It is the storage substrate for all patterns above, not an alternative to them. Format and catalog choice: [storage-formats.md](storage-formats.md), [governance-catalog.md](governance-catalog.md).
