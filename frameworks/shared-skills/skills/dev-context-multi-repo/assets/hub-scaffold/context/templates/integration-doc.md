# Integration: &lt;system-a&gt; ↔ &lt;system-b&gt;

> Catalog-page template for a **cross-repo integration**. One edge of the
> knowledge graph, written up. Generated from system-edge evidence.

- **Type:** sync API | async event | shared datastore | batch/ETL
- **Direction:** &lt;a → b&gt;
- **Contract:** &lt;OpenAPI / schema / topic name + version&gt;
- **Confidence:** verified | inferred

## What flows

&lt;The data/commands crossing this boundary.&gt;

## Evidence

| Claim | Source |
|-------|--------|
| &lt;edge exists&gt; | &lt;manifest/schema/code ref&gt; |

## Failure & coupling

&lt;What breaks downstream if the producer changes. Tie to blast-radius
query output.&gt;

## Provenance

- Edge: `context/graphs/system-edges.json`
- Rebuild: see `context/scripts/README.md`
