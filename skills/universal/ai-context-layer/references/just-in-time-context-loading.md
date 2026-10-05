# Just-In-Time Context Loading

P12 is the runtime pattern for surfaces that deal with large docs, screenshots,
tool payloads, or mixed artifacts. The rule is simple: keep **refs** in the
request and **typed projections** in the bundle.

## Core flow

```text
request carries ContextRef / ArtifactRef
  -> select relevant refs for the surface
  -> resolve refs into evidence, live facts, relationship context, or artifact refs
  -> load only the chosen artifacts
  -> format loaded artifacts into compact typed projections
  -> compress / order / bundle
```

## Non-negotiables

- Refs are stable identifiers with owner scope and freshness metadata.
- Artifact loaders reject wrong-scope requests before loading content.
- Loaded artifacts preserve `source_ref_id` and `evidence_id` where available.
- Formatting removes raw payloads such as base64 blobs, HTML dumps, or verbose
  tool JSON.
- Compression happens on typed projections, not on raw artifact payloads.

## Good fit

- Design-review assistants over docs + screenshots
- Coding agents over files, logs, and diffs
- Workspace copilots over dashboards, tickets, and notebook outputs
- File-heavy research tools where only a subset of sources matter per step

## Bad fit

- Tiny single-surface apps where inlining the only source is simpler
- Pure retrieval products where artifacts are already the final answer surface

## Failure checks

- A27 blocked: no eager loading of the whole candidate set
- A29 blocked: no raw artifact stuffing in the bundle
- F4 blocked: per-surface tool allowlists still govern which refs may load

## Primary sources

- `data/sources.json` → OpenAI MCP
- `data/sources.json` → OpenAI Retrieval
- `data/sources.json` → Anthropic effective context engineering
