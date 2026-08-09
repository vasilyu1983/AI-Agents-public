# Metabase Remote Sync

> Purpose: Decide when Remote Sync should replace raw API upserts for content promotion and reviewable change management. Freshness anchor: June 2026.

## Remote Sync vs Other Paths

| Need | Preferred path |
|------|----------------|
| Promote reviewed content from Git to Metabase | Remote Sync |
| Move content between Metabase environments with entity IDs | Serialization |
| Make one-off incremental edits at runtime | Classic REST API |
| Update dashboards or cards from a deployment pipeline with code review | Remote Sync |

## What Remote Sync Changes

Remote Sync treats Metabase content as code:

- content is synchronized with a remote Git repository
- diffs are reviewable before they land in the Metabase instance
- the workflow fits dev -> staging -> prod promotion better than ad hoc API upserts

## Use Remote Sync When

- dashboards, models, metrics, or questions are managed by a team
- you need change review and rollback discipline
- multiple environments must stay aligned
- content should live in Git instead of only in the UI

## Use Raw REST Instead When

- the change is runtime-driven or tenant-specific
- you need fast incremental edits to one object
- a deployment repo is not part of the workflow
- you are scripting discovery, exports, or schema refresh

## Recommended Promotion Workflow

1. Keep human-reviewed Metabase content in Git.
2. Use Remote Sync for the primary promotion path.
3. Use classic REST API only for small operational changes or exports.
4. If content must cross environments without Git-backed review, use serialization before inventing custom migration code.

## Guardrails

- Do not use raw API upserts as the default promotion strategy if Remote Sync is available.
- Keep runtime automation and promotion automation separate.
- Preserve exported IDs and mappings when mixing Remote Sync with incremental API edits.
