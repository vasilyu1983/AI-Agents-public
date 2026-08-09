# API Versioning and Compatibility Strategies

Use this reference when deciding whether a change needs a version bump, migration plan, or release gate.

## Working Rules

- Treat compatibility policy as a product decision backed by automated checks.
- Use the canonical artifact for diffs: OpenAPI, GraphQL SDL, `.proto`, AsyncAPI, or Arazzo.
- Prefer additive evolution where possible.
- Do not rely on documentation alone; enforce compatibility in CI.

## OpenAPI 4.0 ("Project Moonwalk") — Do Not Plan Around It Yet

As of 2026-07-11, OpenAPI 4.0 (the OAI's "Moonwalk" effort, tracked at github.com/OAI/sig-moonwalk) is still in a design/ADR phase: no stable specification has been published, no production tooling supports it, and there is no committed release date — the SIG's own guidance is to keep using OpenAPI 3.x. OpenAPI 3.2.0 (released September 2025, zero breaking changes from 3.1) is the current stable line; 3.1 remains the safer default until tool support for 3.2-only constructs (structured tags, streaming media types, arbitrary HTTP methods) is confirmed in your specific toolchain. Do not gate contract-testing architecture decisions on anticipated 4.0 features — re-check github.com/OAI/sig-moonwalk before assuming otherwise.

## Versioning Choices

| Surface | Common approach | Notes |
| --- | --- | --- |
| Public REST APIs | URL path or header versioning | Path versioning stays the easiest to reason about operationally |
| Internal REST APIs | Additive evolution with strict diff gates | Works only if breaking changes are rare and controlled |
| GraphQL | Evolve in place with deprecation + registry checks | Breaking changes depend on actual client operations |
| gRPC | Proto compatibility with field-number discipline | Version less often; enforce compatibility with Buf |
| Async/event contracts | Version message schemas and channels intentionally | Consumers may lag for a long time |
| Workflows | Version the workflow artifact when business outcomes change | Structural sameness is not enough |

## Breaking Changes To Treat Seriously

### REST / Webhooks

- Removing fields, endpoints, methods, events, or callback payload properties
- Making previously optional input required
- Tightening validation or auth requirements
- Changing idempotency, pagination, retry, or signature semantics
- Changing the error envelope in ways consumers parse, including RFC 9457 problem responses

### GraphQL

- Removing types, fields, enum values, or arguments in use
- Tightening nullability
- Breaking supergraph composition

### gRPC

- Reusing field numbers
- Incompatible message or service changes
- Removing RPCs without compatibility strategy

### AsyncAPI / Workflows

- Changing message schemas incompatibly
- Changing routing, ordering, correlation, or retry behavior
- Reordering or removing required workflow steps

## Deprecation Pattern

1. Mark the field, operation, message, or workflow step deprecated.
2. Publish a removal date and migration path.
3. Confirm actual consumer usage before removal.
4. Block release if live consumers still depend on the contract being removed.

For HTTP APIs, document deprecation and sunset behavior explicitly when the transport supports it.

## Recommended Compatibility Gates

- REST: lint + diff against the base branch + executable contract tests
- GraphQL: schema diff + GraphOS/Hive operation-aware checks
- gRPC: `buf lint` + `buf breaking`
- CDC: Pact verification + `can-i-deploy`
- Async/workflows: schema diff plus executable workflow tests

## Release Decision Matrix

| Change | Safe to ship without version bump? |
| --- | --- |
| Add optional field | Usually yes |
| Add endpoint / RPC / topic | Usually yes |
| Add enum value | Depends on consumer handling; confirm for GraphQL and events |
| Tighten validation | Usually no |
| Change auth or signing model | Usually no |
| Change required fields or payload shape | No |
| Remove deprecated field still in use | No |

## Rolling Out A Breaking Change Across Independent Teams

A schema diff or lint failure tells you a change is unsafe; it does not tell you how to ship it without breaking someone else's on-call. Sequence the rollout, do not just gate it:

1. **Ship additive first.** Add the new field/endpoint/message alongside the old one so both shapes are simultaneously valid. This buys migration time without a hard cutover date.
2. **Find every real consumer, not the ones you remember.** Use the Pact Broker consumer inventory, GraphOS/Hive operations data, or access logs/traces for REST — "we think nobody uses this" is the single most common cause of an unplanned outage during contract removal.
3. **Gate removal on evidence, not a calendar.** A deprecation date is a target, not a guarantee. Only remove the old shape once `can-i-deploy`, an operations check, or a traffic query shows zero live usage for a sustained window (a single day with zero traffic can hide a monthly batch consumer).
4. **Coordinate the order of deploys, not just the code.** For CDC, the provider must deploy and pass verification before consumers can safely cut over; for schema-registry-based GraphQL, run the check against currently deployed client operations, not just the latest committed ones. Publish a rollout order (provider first, then consumers by risk) rather than assuming everyone deploys atomically.
5. **Keep a rollback path live until the deprecation window closes.** If the old and new shapes cannot coexist behind the same version, you have made rollback impossible the moment you remove the old path — verify this before removal, not after an incident.

## Operational Advice

- Keep a consumer inventory, even if approximate.
- Prefer deploy-time safety checks over spreadsheet-based coordination.
- Record deployments/releases in the broker or registry where the platform supports it.
- Treat webhook receivers and async consumers as first-class consumers, not invisible integrations.
