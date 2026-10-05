# Lake Publish Gate

Use when a lake write must be validated before readers see a new snapshot. Define the checks, thresholds, and test implementation in `data-analytics-engineering` (`references/data-quality-testing.md`, `references/lake-data-quality-patterns.md`); record the table contract in [quality governance](template-data-quality-governance.md).

1. Write to a staging table or isolated branch. Do not publish an unchecked snapshot.
2. Run the contract checks against the new partition or interval. Also schedule full-table checks for invariants such as global key uniqueness that a slice cannot prove.
3. Publish only after blocking checks pass. Store the result and failing slice for the table owner; warnings follow the agreed contract.
4. Check freshness independently of the write job, so a stopped job still raises an alert.

For merge-on-read tables, count rows through the query engine rather than file metadata; file-level counts can include deleted rows. Rehearse a deliberately failing load and confirm that readers stay on the prior snapshot.
