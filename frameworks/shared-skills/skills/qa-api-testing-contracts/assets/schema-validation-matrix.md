# Schema Validation Matrix

Map each contract surface to its artifact, validation method, and CI gate.

## Contract Inventory

| System | Surface | Canonical artifact | Owner | Primary gate |
| --- | --- | --- | --- | --- |
| User service | REST | OpenAPI 3.1 / 3.2 | Team A | Lint + diff + contract |
| Product graph | GraphQL | SDL + registry | Team B | Schema + operations checks |
| Payment service | gRPC | Proto + Buf | Team C | Buf lint + breaking |
| Order events | AsyncAPI | AsyncAPI 3.x | Team D | Schema + executable contracts |
| Billing callbacks | Webhooks | OpenAPI webhooks / AsyncAPI | Team E | Signature + replay + payload validation |
| Checkout journey | Workflow | Arazzo 1.x | Team F | Workflow contract tests |

## Validation Levels

| Level | What it checks | Typical tools | Stage |
| --- | --- | --- | --- |
| Syntax | Valid YAML / JSON / Proto / SDL | parser, buf lint | Pre-commit |
| Schema | Spec compliance and style | Spectral, GraphQL Inspector, Buf | PR |
| Compatibility | Unsafe diffs and client impact | oasdiff, GraphOS, Hive, buf breaking | PR / Release |
| Execution | Real provider, mock, or workflow behavior | Pact, Specmatic, Microcks, Schemathesis | PR / Release |
| Promotion | Safe to release/deploy | Pact Broker, registry checks | Release / Deploy |

## Recommended Tool Map

### REST / Webhooks

| Need | Tool | Notes |
| --- | --- | --- |
| Linting | Spectral | Confirm tool support before using OpenAPI 3.2-specific constructs |
| Mocking / validation | Prism | Good for request/response validation, not full compatibility authority |
| Breaking diff | oasdiff | Compare base branch artifact to proposed artifact |
| Executable contracts | Specmatic / Microcks / Pact | Pick based on consumer model |
| Hardening | Schemathesis | HTTP bug discovery and edge cases |

### GraphQL

| Need | Tool | Notes |
| --- | --- | --- |
| Local diff / lint | GraphQL Inspector | Fast local feedback |
| Registry checks | Apollo GraphOS / GraphQL Hive | Use collected operations when available |
| Executable contracts | Specmatic / Microcks | Useful when SDL is the source of truth |

### gRPC

| Need | Tool | Notes |
| --- | --- | --- |
| Lint + breaking | Buf | Default choice |
| Request testing | grpcurl | Good for smoke and repro flows |

### AsyncAPI / Workflows

| Need | Tool | Notes |
| --- | --- | --- |
| Linting | Spectral | Built-in rulesets for AsyncAPI v2 and v3, and Arazzo v1.0; add `spectral:asyncapi` or `spectral:arazzo` to your ruleset |
| Executable contracts | Specmatic / Microcks | Broad async support; Specmatic 2.0 adds Avro and Kafka support |
| Workflow contracts | Specmatic / custom workflow runner | Use Arazzo when step sequencing matters |

## CI Example

```yaml
validate-contracts:
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Materialize base artifacts
      run: |
        git show "origin/${{ github.base_ref }}:specs/api.yaml" > /tmp/api.base.yaml

    - name: Lint artifacts
      run: |
        spectral lint specs/api.yaml
        buf lint

    - name: Diff compatibility
      run: |
        oasdiff breaking /tmp/api.base.yaml specs/api.yaml
        buf breaking

    - name: Run executable contracts
      run: |
        # Pact / Specmatic / Microcks / Schemathesis as selected
        echo "Run protocol-specific contract suite here"
```

## AI Tooling Notes

| Tool | Role | Keep it scoped |
| --- | --- | --- |
| PactFlow AI | Improve Pact suites | Optional vendor layer |
| Keploy | Bootstrap from traffic | Review and sanitize generated cases |
| Postman AI (Agent Mode, formerly Postbot) | Suggest assertions; can now act on collections/tests/mocks | Functional helper, not contract authority — review agent edits before merge |
