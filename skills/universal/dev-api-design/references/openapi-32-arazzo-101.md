# OpenAPI 3.2 and Arazzo

## OpenAPI 3.1 -> 3.2

Before migrating, confirm that every validator, linter, and generator in your pipeline supports 3.2; one unsupported tool blocks the move. Migration from 3.1.x is low-risk: existing 3.1 descriptions remain valid. Check the OpenAPI Initiative site for whether a newer minor exists before pinning.

### New in 3.2 vs 3.1.x

| Feature | What it enables |
|---------|-----------------|
| Streaming media types | Native SSE (`text/event-stream`), JSON Lines (`application/x-ndjson`), JSON Sequences (`application/json-seq`) — describe streaming responses without hacks |
| QUERY HTTP method | Describes server-driven queries with a request body; avoids GET-with-body ambiguity |
| OAuth 2.0 Device Authorization Flow | First-class security scheme for device-flow in tooling and generated SDKs |
| Structured tag nesting | Hierarchical tag grouping for documentation portals (tag `parent` and `kind`) |
| `additionalOperations` | Describe HTTP methods beyond the fixed set on a path item |
| `querystring` parameter location | Describe the whole query string as one schema-typed parameter |
| `itemSchema` | Schema for each item of a streamed/sequential media type |
| `oauth2MetadataUrl` | Point an OAuth2 security scheme at the authorization server metadata document |

### Key links

- Spec: https://spec.openapis.org/oas/latest.html
- OpenAPI Initiative: https://www.openapis.org/

## Arazzo

Arazzo is a separate OAI specification (not part of OpenAPI) that adds a multi-step workflow layer on top of OpenAPI descriptions. Check the [OAI Arazzo releases](https://github.com/OAI/Arazzo-Specification/releases) for the current version and confirm your tooling supports it.

### Core concepts

- **Workflows**: named sequences of API steps with explicit ordering and conditions
- **Steps**: each step maps to an OpenAPI `operationId` (or external reference) and captures request inputs, expected outputs, and success/failure criteria
- **Runtime expressions**: `$steps.<id>.outputs.<field>` lets later steps consume outputs of earlier steps for dynamic chaining
- **Success criteria**: each step declares pass/fail assertions, making workflows machine-verifiable

### What 1.1.0 added over 1.0.1

- **AsyncAPI operation references**: workflows can coordinate sequences that span synchronous HTTP calls and asynchronous event-driven interactions in a single document
- Improved workflow composition and data selection
- Specification precision improvements from the 1.0 lifecycle

### Non-HTTP step types

If a workflow needs gRPC, GraphQL, MCP, or other non-HTTP steps, check the OAI Arazzo repo for whether a released version supports that step type. Do not design around roadmap items.

### Key links

- Spec: https://spec.openapis.org/arazzo/latest.html
- OAI overview: https://www.openapis.org/arazzo-specification
- Repo and releases: https://github.com/OAI/Arazzo-Specification

## When to use Arazzo

Use Arazzo when:
- You need to describe a multi-step API sequence (auth -> lookup -> act) as a first-class contract artifact
- You want machine-verifiable workflow definitions for testing or documentation
- Your API consumers (including agents) need a structured description of how to chain calls

Do not use Arazzo to replace OpenAPI — it depends on OpenAPI operation IDs and adds a layer above them, not an alternative to them.
