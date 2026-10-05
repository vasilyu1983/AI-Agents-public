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

## OpenAPI 3.1 / 3.2 Per-Tool Support

OpenAPI 3.2.1 defines the 3.2 feature set; its patch version does not add features. Before selecting a document version, read the published specification at https://spec.openapis.org/oas/latest.html and check each installed tool below. Record its version, accepted document versions, and a fixture using the constructs you need (`itemSchema`, `additionalOperations`, or sequential media types). Parsing a 3.2 header alone does not prove lint, diff, mock, or generator coverage.

| Tool | Support lookup | Required check |
| --- | --- | --- |
| oasdiff | https://github.com/oasdiff/oasdiff/blob/main/docs/OPENAPI-31.md | Diff a changed 3.2-only construct and assert the intended breaking-change exit status |
| Spectral | https://github.com/stoplightio/spectral/releases | Confirm a released ruleset recognizes the declared version and catches an invalid required construct |
| Schemathesis | https://schemathesis.readthedocs.io/en/stable/ | Run a supported schema fixture and confirm tests execute for the required operation/media type |
| Specmatic | https://docs.specmatic.io/supported_protocols | Verify the selected edition and command support the document and required construct |
| Prism | https://github.com/stoplightio/prism | Verify mock/validation behavior for the required construct; add a separate compatibility gate |

Default to OpenAPI 3.1 while any required tool lacks demonstrated support for the 3.2 feature used by the contract.

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
| Executable contracts | Specmatic / Microcks | Check the selected tool/edition supports the protocol, binding, and message schema in use |
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
        oasdiff breaking --fail-on ERR /tmp/api.base.yaml specs/api.yaml
        buf breaking --against ".git#branch=origin/${{ github.base_ref }}"

    - name: Run executable contracts
      run: |
        # Pact / Specmatic / Microcks / Schemathesis as selected
        echo "ERROR: replace this step with the selected contract suite" >&2
        exit 1
```

## AI Tooling

See `../references/ai-contract-testing.md` for the current PactFlow AI, Keploy, and Postman AI (Agent Mode) tooling table and cautions.
