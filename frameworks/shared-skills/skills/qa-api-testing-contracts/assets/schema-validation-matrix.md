# Schema Validation Matrix

Map your APIs to validation tools and CI stages.

## API Inventory

| API Name | Type | Schema Source | Schema Location | Owner |
| --- | --- | --- | --- | --- |
| User Service | REST | OpenAPI 3.1 | /specs/user-api.yaml | Team A |
| Order Service | GraphQL | SDL | /specs/order.graphql | Team B |
| Payment Service | gRPC | Proto3 | /protos/payment.proto | Team C |

## Validation Levels

| Level | What It Checks | Tool | When |
| --- | --- | --- | --- |
| 1. Syntax | Valid YAML/JSON/Proto | yamllint, buf lint | Pre-commit |
| 2. Schema | Follows spec rules | Spectral, graphql-inspector | Pre-commit |
| 3. Semantic | Makes logical sense | Custom rules, Spectral | PR check |
| 4. Design | Best practices | Spectral ruleset, Zally | PR check |

## Tool Configuration

### REST (OpenAPI)

| Tool | Purpose | Install | CI Command |
| --- | --- | --- | --- |
| Spectral | Linting + rules | `npm i @stoplight/spectral-cli` | `spectral lint openapi.yaml` |
| Prism | Mock + validate | `npm i @stoplight/prism-cli` | `prism mock openapi.yaml` |
| Schemathesis | Property testing | `pip install schemathesis` | `schemathesis run openapi.yaml --base-url $API_URL` |
| oasdiff | Breaking changes | `brew install oasdiff` or `go install github.com/tufin/oasdiff@latest` | `oasdiff breaking old.yaml new.yaml` |

### GraphQL (SDL)

| Tool | Purpose | Install | CI Command |
| --- | --- | --- | --- |
| GraphQL Inspector | Schema diff + breaking changes | `npm i @graphql-inspector/cli` | `graphql-inspector diff old.graphql new.graphql` |
| Apollo Rover | Schema checks + composition | `npm i -g @apollo/rover` | `rover graph check` |
| Apollo GraphOS | Build + operations checks | Cloud service | `rover subgraph check` |
| graphql-eslint | Linting | `npm i @graphql-eslint/eslint-plugin` | `eslint --ext .graphql` |
| Specmatic | Contract testing | `npm i -g specmatic` | `specmatic test --contract schema.graphql` |

If you need mocked GraphQL responses in tests, prefer schema-aware mocks (for example, `@graphql-tools/mock`) or request-level mocking (for example, `msw`) so the mock stays aligned with the SDL.

### gRPC (Proto)

| Tool | Purpose | Install | CI Command |
| --- | --- | --- | --- |
| buf | Lint + breaking | `brew install bufbuild/buf/buf` | `buf lint && buf breaking` |
| protolint | Style linting | `go install github.com/yoheimuta/protolint` | `protolint .` |
| grpcurl | Testing | `brew install grpcurl` | `grpcurl -d '{}' host:port Service/Method` |

## CI Pipeline Stages

```yaml
# Example GitHub Actions
validate-api:
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Materialize base spec
      run: git show "origin/${{ github.base_ref }}:specs/api.yaml" > /tmp/api.base.yaml

    - name: Lint OpenAPI
      run: spectral lint specs/*.yaml --ruleset .spectral.yaml

    - name: Check breaking changes
      run: oasdiff breaking /tmp/api.base.yaml specs/api.yaml

    - name: Contract tests
      run: pact-verifier --provider-base-url=$API_URL

    - name: Property tests
      run: schemathesis run specs/api.yaml --base-url=$API_URL
```

## Ruleset Examples

### Spectral (.spectral.yaml)

```yaml
extends: ["spectral:oas", "spectral:asyncapi"]
rules:
  operation-operationId: error
  operation-description: warn
  info-contact: warn
```

### Buf (buf.yaml)

```yaml
version: v1
breaking:
  use:
    - FILE
lint:
  use:
    - DEFAULT
```

## AI-Powered Validation (2026)

| Tool | Capability | Best For |
| --- | --- | --- |
| Keploy | Generate tests from traffic | Legacy APIs |
| Specmatic | Schema → contract tests | OpenAPI/GraphQL-first |
| PactFlow AI | Review + improve Pact tests | Existing Pact users |
| Postman Postbot | AI test suggestions | Manual testing |

See `../references/ai-contract-testing.md` for setup guides.
