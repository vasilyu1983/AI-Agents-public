# Backlog Status Sync Pattern

Use this pattern to keep implementation status accurate across canonical documentation after feature delivery waves.

## Canonical-First Model

1. Choose one canonical status source (for example feature matrix or roadmap doc).
2. Apply status update there first with date + owner.
3. Update dependent docs by linking to canonical source instead of duplicating status text.

## Required Metadata for Temporary Reports

Include in dated report files:
- `Status`: `pending-integration | integrated | superseded`
- `Integrates-into`: canonical path
- `Owner`
- `Delete-by`

## Sync Audit Steps

- grep for stale status phrases in docs
- reconcile conflicts against canonical source
- verify moved paths, renamed files, and canonical links after restructures
- re-count filesystem-backed totals when docs mention file counts, repo counts, or matrix dimensions
- check `full inventory` and `complete map` claims against source-of-truth artifacts
- label partial examples as examples instead of full coverage
- mark integrated reports and schedule deletion

## Failure Modes Prevented

- docs claiming old backlog state after implementation
- duplicate contradictory status statements in multiple files
- LLM agents consuming stale report snapshots as truth
