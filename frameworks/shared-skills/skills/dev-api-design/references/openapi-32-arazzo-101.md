# OpenAPI 3.2.0 and Arazzo 1.1.0

Verified against primary sources 2026-06-09.

## OpenAPI 3.1 -> 3.2.0

OpenAPI 3.2.0 reached GA in September 2025. Most major validators and generators added 3.2 support in Q4 2025 - Q1 2026. Migration from 3.1.x is low-risk; existing 3.1 descriptions remain valid.

### New in 3.2 vs 3.1.x

| Feature | What it enables |
|---------|-----------------|
| Streaming media types | Native SSE (`text/event-stream`), JSON Lines (`application/x-ndjson`), JSON Sequences (`application/json-seq`) — describe streaming responses without hacks |
| QUERY HTTP method | Describes server-driven queries with a request body; avoids GET-with-body ambiguity |
| OAuth 2.0 Device Authorization Flow | First-class security scheme for device-flow in tooling and generated SDKs |
| Structured tag nesting | Hierarchical tag grouping for documentation portals |
| JSON Schema alignment finalized | Closes remaining gaps from 3.1's partial 2020-12 alignment; `$dynamicRef`, `unevaluatedProperties` fully specified |

### Key links

- Spec: https://spec.openapis.org/oas/latest.html
- OpenAPI Initiative: https://www.openapis.org/

## Arazzo 1.1.0

Arazzo is a separate OAI specification (not part of OpenAPI) that adds a multi-step workflow layer on top of OpenAPI descriptions. Arazzo 1.1.0 was published 2026-05-17 — the current stable release.

### Core concepts

- **Workflows**: named sequences of API steps with explicit ordering and conditions
- **Steps**: each step maps to an OpenAPI `operationId` (or external reference) and captures request inputs, expected outputs, and success/failure criteria
- **Runtime expressions**: `$steps.<id>.outputs.<field>` lets later steps consume outputs of earlier steps for dynamic chaining
- **Success criteria**: each step declares pass/fail assertions, making workflows machine-verifiable

### What 1.1.0 adds over 1.0.1

- **AsyncAPI operation references**: workflows can now coordinate sequences that span synchronous HTTP calls and asynchronous event-driven interactions in a single document
- Improved workflow composition and data selection
- Specification precision improvements from the 1.0 lifecycle

### Future roadmap (planned, not released)

Arazzo future versions plan to add step types for: gRPC, GraphQL, SOAP, MCP, and A2A. Verify current status against the OAI repo before design decisions depend on these.

### Key links

- Spec (current): https://spec.openapis.org/arazzo/latest.html
- OAI overview: https://www.openapis.org/arazzo-specification
- Repo and releases: https://github.com/OAI/Arazzo-Specification

## When to use Arazzo

Use Arazzo when:
- You need to describe a multi-step API sequence (auth -> lookup -> act) as a first-class contract artifact
- You want machine-verifiable workflow definitions for testing or documentation
- Your API consumers (including agents) need a structured description of how to chain calls

Do not use Arazzo to replace OpenAPI — it depends on OpenAPI operation IDs and adds a layer above them, not an alternative to them.
