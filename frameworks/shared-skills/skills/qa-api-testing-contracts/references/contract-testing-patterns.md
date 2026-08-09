# Contract Testing Patterns

Use this reference when deciding how to detect unsafe API changes and where to place gates in delivery.

## Table of Contents

- [Pick The Enforcement Model](#pick-the-enforcement-model)
- [Breaking vs Non-Breaking By Surface](#breaking-vs-non-breaking-by-surface)
- [REST / OpenAPI](#rest-openapi)
- [GraphQL](#graphql)
- [gRPC / Protobuf](#grpc-protobuf)
- [AsyncAPI / Event Contracts](#asyncapi-event-contracts)
- [Webhooks](#webhooks)
- [Workflow Contracts (Arazzo)](#workflow-contracts-arazzo)
- [Release Gate Patterns](#release-gate-patterns)
- [Pact / Broker Pattern](#pact-broker-pattern)
- [GraphQL Registry Pattern](#graphql-registry-pattern)
- [gRPC Pattern](#grpc-pattern)
- [Mixed-Protocol Schema-Driven Pattern](#mixed-protocol-schema-driven-pattern)
- [Suggested CI Order](#suggested-ci-order)
- [Common Failure Modes](#common-failure-modes)
- [When Contract Testing Is Overkill vs Essential](#when-contract-testing-is-overkill-vs-essential)

## Pick The Enforcement Model

| Model | Best for | Primary tools |
| --- | --- | --- |
| CDC | Many independent consumers; provider behavior matters beyond schema shape | Pact, PactFlow |
| Schema-driven | A canonical schema is already maintained and teams want broad coverage fast | Specmatic, Microcks |
| Property-based hardening | HTTP APIs that need systematic edge-case discovery | Schemathesis |
| Registry checks | GraphQL teams with collected client operations | GraphOS, Hive, GraphQL Inspector |

Use more than one model when needed. The common mixed stack is:

- Diff and lint for every change
- CDC for consumer/provider compatibility
- Schema-driven contracts for breadth
- Property-based tests for HTTP hardening

## Breaking vs Non-Breaking By Surface

### REST / OpenAPI

Breaking changes usually include:

- Removing endpoints, methods, fields, or webhook payload fields
- Tightening request validation or making a previously optional field required
- Changing types, enums, auth requirements, pagination contracts, or idempotency semantics
- Changing the error envelope when clients parse it, including an RFC 9457 problem shape

Usually non-breaking:

- Adding optional response fields
- Adding endpoints, optional query parameters, or additive webhook fields
- Loosening validation rules

### GraphQL

Breaking changes usually include:

- Removing a field, type, enum value, or argument in active use
- Tightening nullability
- Adding a required argument to an existing field
- Federation changes that break supergraph composition

Usually non-breaking:

- Adding fields
- Adding optional arguments
- Deprecating fields with a published removal plan

Registry checks matter here. A schema diff alone is not enough when collected operations are available.

### gRPC / Protobuf

Breaking changes usually include:

- Reusing or renumbering field numbers
- Incompatible field type changes
- Removing RPCs or changing streaming semantics
- Renaming packages or services without compatibility shims

Usually non-breaking:

- Adding new fields with new numbers
- Adding new RPCs
- Reserving removed field numbers and names instead of reusing them

### AsyncAPI / Event Contracts

Breaking changes usually include:

- Changing message schemas incompatibly
- Changing topics/channels, routing keys, or correlation semantics
- Changing required headers/metadata or retry expectations
- Reordering events when consumers rely on order

Usually non-breaking:

- Additive message fields with consumer-safe defaults
- New channels or topics
- New optional metadata

### Webhooks

Treat these as contracts, not “just integrations”.

Breaking changes usually include:

- Changing payload shape, signing scheme, timestamp tolerance, delivery rules, or retry semantics
- Changing callback URLs, auth expectations, or event names without migration support

Always test:

- Signature verification
- Replay protection
- Duplicate delivery handling
- Out-of-order or delayed delivery

### Workflow Contracts (Arazzo)

Structural diffs are useful, but not sufficient.

Breaking changes usually include:

- Removing or reordering required workflow steps
- Changing data dependencies between steps
- Changing retry/rollback expectations
- Changing success criteria for a business outcome

Back these with executable end-to-end workflow tests.

## Release Gate Patterns

### Pact / Broker Pattern

Use broker-backed compatibility, not tribal knowledge.

Pre-deploy:

- `pact-broker can-i-deploy --pacticipant ... --version ... --to-environment ...`

Post-deploy:

- `pact-broker record-deployment ...`
- `pact-broker record-release ...` when appropriate

Prefer environments, branches, and deployment/release records over the legacy tag-based workflow (tags are still supported but no longer receive new features; the Pact Broker's own guidance is to model branches with the `branch` property and environments with `record-deployment`/`record-release` instead of tagging with branch or environment names). `can-i-deploy` only answers "has every pairing currently deployed to this environment verified compatibility with this version?" — it is a query against the deployment record, not a live check of what is actually running. If `record-deployment` is skipped or run outside the real deploy pipeline (e.g., only on success, or from a separate manual step that drifts out of sync), `can-i-deploy` will silently pass against a stale picture of what is deployed. Wire `record-deployment` into the same automation that performs the deploy, not as an optional follow-up step.

### GraphQL Registry Pattern

For GraphOS or Hive:

- Run local diff checks in PRs
- Run schema/build/composition checks in CI
- Run operations checks against collected client traffic before release

This is the safest pattern for active GraphQL clients because it catches “breaking on paper” versus “breaking in production use”.

### gRPC Pattern

- `buf lint` in every PR
- `buf breaking` against the base branch or mainline artifact
- Reserve removed fields instead of reusing numbers

### Mixed-Protocol Schema-Driven Pattern

Use Specmatic or Microcks when:

- You have OpenAPI, GraphQL, AsyncAPI, or workflow artifacts already
- You need fast executable coverage across multiple protocols
- You want mocking and verification from the same artifact set

## Suggested CI Order

1. Lint artifacts
2. Diff against the base branch
3. Build/composition checks where relevant
4. Execute contracts for critical operations and workflows
5. Run property-based hardening for HTTP APIs
6. Run release/promotion gate checks

## Common Failure Modes

- Generated specs drift from runtime behavior
- Teams treat mock success as proof of provider compatibility
- **Contract tests that mirror the mock and verify nothing:** the consumer expectation is written against the mock's own canned fixture (a hardcoded ID, a fixed timestamp) rather than the provider's actual behavior. Provider verification then replays the same fixture and passes trivially — the test suite grows without any corresponding growth in real coverage. Catch this in review by asking "would this matcher fail if the provider changed this field's real value?"
- **Provider-state drift:** state-setup handlers (the code that seeds "user has a pending order" or similar preconditions before provider verification) are written once and rarely revisited. As the provider's schema or business logic evolves, state handlers silently stop creating a state that matches production reality, so verification keeps passing against stale state while the real deployed behavior has diverged. Review state-handler code on every provider-side schema change, not just when a consumer pact changes.
- Webhook retries and duplicate delivery are never tested
- GraphQL schema diffs are run without collected operation checks
- Async/event contracts validate payload shape but not ordering or replay semantics

## When Contract Testing Is Overkill vs Essential

Not every integration needs a broker, CDC suite, or workflow runner. Match the investment to the actual coordination risk:

| Situation | Recommendation |
| --- | --- |
| One consumer and one provider, same team, same deploy | Lint + diff is usually enough; CDC infrastructure adds coordination overhead with no independent party to coordinate with |
| Prototype or internal tool with a defined sunset date | Skip contract tooling; rely on integration/e2e tests until the surface stabilizes |
| 3+ independent consumer teams, or any third-party/public consumer | CDC or schema-driven contracts are close to mandatory — nobody can informally track every consumer's assumptions at that scale |
| Async/event contracts where producer and consumer deploy independently | Executable contracts plus replay/ordering tests are essential; a passing schema diff cannot prove a consumer will handle real message timing |
| Webhook receivers you do not control | Treat the payload/signature/retry contract as the primary risk surface; the receiver cannot coordinate a synchronized deploy with you |

The judgment call is coordination cost, not company size: a two-person startup with one public webhook consumer needs contract discipline; a 200-engineer org with one internal consumer talking to one internal provider on a shared release train may not.
