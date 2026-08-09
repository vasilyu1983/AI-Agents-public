# Schema-Driven and Property-Based Testing

Use this reference when the schema or workflow artifact is the source of truth.

## Table of Contents

- [Tool Selection](#tool-selection)
- [Principles](#principles)
- [Schemathesis](#schemathesis)
- [Stable starting point](#stable-starting-point)
- [Specmatic](#specmatic)
- [Microcks](#microcks)
- [What To Validate Beyond Shape](#what-to-validate-beyond-shape)
- [REST / HTTP](#rest-http)
- [GraphQL](#graphql)
- [gRPC](#grpc)
- [AsyncAPI / Events](#asyncapi-events)
- [Arazzo / Workflows](#arazzo-workflows)
- [CI Placement](#ci-placement)
- [Anti-Patterns](#anti-patterns)

## Tool Selection

| Need | Prefer | Why |
| --- | --- | --- |
| HTTP bug discovery and edge cases | Schemathesis | Generates property-based tests from OpenAPI or GraphQL |
| Executable contracts from OpenAPI or GraphQL | Specmatic | Low-code executable contracts and compatibility checks |
| Mixed protocol mocking and contract checks | Microcks | Broad support across REST, GraphQL, gRPC, and AsyncAPI |
| OpenAPI or AsyncAPI style governance | Spectral | Fast linting and rulesets |

## Principles

- The canonical artifact is the source of truth, not the mock server.
- Additive coverage is good, but compatibility gates still need explicit policy.
- Schema validation proves shape, not business correctness.
- Workflow artifacts matter when individual endpoint or message checks miss cross-step breakage.

## Schemathesis

Schemathesis v4.0.0 was released June 2025 with a full engine rewrite. v4 is the current stable line. Notable v4 changes relevant to CI scripts:

- `--hypothesis-max-examples` renamed to `--max-examples` (`-n`)
- `--base-url` flag renamed to `--url` (`-u`)
- v4 runs all checks by default; `--checks all` still accepted explicitly
- New `--phases` option replaces `--stateful` and other phase flags
- `--report` replaces separate cassette/XML options (values: `junit`, `vcr`, `har`, `ndjson`)
- `schemathesis.io` cloud service discontinued; `schemathesis auth` and `upload` commands removed
- 3x faster execution, 15x lower memory than v3

Review the [migration guide](https://schemathesis.readthedocs.io/en/stable/migration/) before upgrading existing v3 CI scripts.

### Stable starting point (v4)

```bash
uvx schemathesis run https://example.schemathesis.io/openapi.json
```

Use Schemathesis when you want to:

- Exercise edge cases that humans do not think to write
- Validate responses against the schema
- Surface 5xx and validation bugs early
- Add HTTP hardening to an existing contract suite

Use it as a layer on top of contract tests, not instead of CDC or release compatibility checks.

## Specmatic

Specmatic 2.0 substantially expanded protocol coverage, confirmed-shipping: OpenAPI (3.0/3.1), GraphQL (SDL), gRPC (proto), and AsyncAPI (2.6/3.0), with Arazzo and Avro schema support reaching GA around Q3 2025. Its own roadmap page also lists WSDL and MCP (Model Context Protocol) testing as shipped — but the exact GA timing for those two is **unverified as of 2026-07-11**; confirm current protocol support at docs.specmatic.io/supported_protocols before committing to them in a delivery pipeline.

Use it for:

- OpenAPI and GraphQL contract execution and backward-compatibility checks
- gRPC contract testing from proto files
- AsyncAPI-based contract testing across message brokers (Kafka with Avro schema support) and WebSockets
- Arazzo-based workflow testing
- Avro schema registry integration for event-driven contracts

An MCP server exposing Specmatic's contract-testing capabilities to AI coding agents is documented on the product roadmap. Check the current docs before pinning CLI commands or exact feature availability, because the product surface includes both OSS and enterprise tracks and ships incrementally by quarter.

## Microcks

Microcks is a good fit when you need a mixed-protocol platform for mocks and tests from contract artifacts.

The current documentation exposes first-class tutorials for:

- REST
- GraphQL
- gRPC
- AsyncAPI

Use it when one team owns several protocol surfaces and wants a consistent artifact-driven test platform.

## What To Validate Beyond Shape

### REST / HTTP

- Status codes and headers
- RFC 9457 problem responses when adopted
- Pagination, idempotency, cache semantics, and auth boundaries

### GraphQL

- Schema changes plus collected-operation impact
- Custom scalars, directives, and federation composition
- Persisted/known-operation flows if used

### gRPC

- Field number safety
- Backward compatibility of request/response messages
- Service and method stability

### AsyncAPI / Events

- Message schema compatibility
- Correlation IDs, ordering, delivery guarantees, and retries
- Request/reply versus fire-and-forget patterns

### Arazzo / Workflows

- Cross-step data dependencies
- Retry, rollback, and partial-failure behavior
- The business outcome of the workflow, not just individual steps

## CI Placement

- Run lint and diff in every PR.
- Run executable contracts for critical paths before merge or before release, depending on cost.
- Run property-based tests on a stable ephemeral environment.
- Publish machine-readable artifacts from the run when the tool supports them.

## Anti-Patterns

- Treating generated mocks as proof that the real provider is compatible
- Running property-based tests only after release
- Validating schema shape but ignoring retries, replay, and ordering
- Using a newer spec version in examples when the selected tool has not documented support for it
