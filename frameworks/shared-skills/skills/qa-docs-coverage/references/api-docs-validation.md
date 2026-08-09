# API Documentation Validation

Validate that machine-readable API docs still describe real behavior. Prefer a small, reliable toolchain over many overlapping tools.

## Table of Contents

- [Default toolchain](#default-2026-toolchain)
- [OpenAPI baseline](#openapi-baseline)
- [AsyncAPI baseline](#asyncapi-baseline)
- [Breaking-change detection](#breaking-change-detection)
- [Drift detection](#drift-detection)
- [Endpoint coverage](#endpoint-coverage)
- [Docstring and code-level doc coverage](#docstring-and-code-level-doc-coverage)
- [CI checklist](#ci-checklist)
- [Tool notes](#tool-notes)
- [Related resources](#related-resources)

## Default toolchain

- OpenAPI linting:
  Spectral (also supports Arazzo v1) and Redocly CLI (v2.36.0+, also supports AsyncAPI and Arazzo)
- AsyncAPI validation:
  AsyncAPI CLI and Spectral (AsyncAPI spec currently on the 3.x line; default new documents to `3.0.0` unless a 3.1-only feature is needed)
- Breaking-change detection:
  `oasdiff` (300+ rules, GitHub Action available)
- Runtime or example validation:
  optional, when the service already has stable test environments

Note: Optic's GitHub repo was archived 2026-01-12, following Atlassian's April 2024 acquisition and no Compass integration ever shipping. It is no longer maintained (no security patches, no new rules). Replace Optic-based workflows with `oasdiff` for spec-to-spec diffing.

Legacy or optional coverage tools:
- Swagger Coverage
- `open-api-coverage`

Use those only when they fit the stack and you understand their maintenance tradeoffs.

## OpenAPI baseline

Lint every changed OpenAPI spec with both tools:

```bash
npx @stoplight/spectral-cli lint openapi.yaml
npx @redocly/cli lint openapi.yaml
```

Use Redocly when you also need bundling or local preview:

```bash
npx @redocly/cli bundle openapi.yaml -o bundled-openapi.yaml
npx @redocly/cli preview-docs openapi.yaml
```

Minimum expectations:
- every operation has `operationId`, `summary`, and meaningful descriptions
- request and response payloads use shared schemas where possible
- auth and error responses are documented
- examples exist for externally consumed flows

## AsyncAPI baseline

Validate the spec directly:

```bash
npx @asyncapi/cli validate asyncapi.yaml
npx @stoplight/spectral-cli lint asyncapi.yaml
```

Minimum expectations:
- channels, operations, and messages are named consistently
- payload schemas resolve correctly
- bindings and protocol-specific fields are valid for the transport in use
- examples exist for important producer and consumer flows

## Breaking-change detection

Treat this as the main regression guard for public contracts.

```bash
docker run --rm -v "$PWD:/work" -w /work ghcr.io/oasdiff/oasdiff:latest \
  breaking openapi/base.yaml openapi/openapi.yaml
```

Use it in CI for:
- removed paths
- removed operations
- required request fields added without versioning strategy
- response schema tightening that breaks existing consumers

## Drift detection

Choose one primary drift strategy:

1. Code-generated spec diff
2. Integration tests validating live responses against schemas
3. Contract tests between provider and consumer

Do not adopt all three unless the repo genuinely needs them.

Example code-generated diff:

```bash
npx tsoa spec
diff -u generated/openapi.json docs/openapi.json
```

## Endpoint coverage

Prefer source-of-truth comparison over vanity percentages.

Recommended checks:
- routes discovered in code vs paths in the spec
- changed handlers in the PR vs changed contract/docs files
- public endpoints with no examples or migration notes

Example route-to-spec comparison:

```bash
ROUTES=$(rg --no-filename -o 'app\\.(get|post|put|patch|delete)\\(\"[^\"]+\"' src | sort -u)
SPEC_PATHS=$(yq '.paths | keys | .[]' openapi.yaml | sort -u)

comm -23 <(printf "%s\n" "$ROUTES") <(printf "%s\n" "$SPEC_PATHS")
```

## Docstring and code-level doc coverage

Endpoint and contract coverage (above) tells you whether the external surface is described.
It says nothing about whether the code implementing that surface — request handlers, domain
models, internal helpers — has usable docstrings. Use a dedicated tool for that layer instead
of eyeballing it:

- **interrogate** (Python): reports docstring presence per module/class/function/method and
  can gate CI on a minimum percentage (`interrogate -vv --fail-under=80 src/`).
- **docstr-coverage** (Python): per-file and project-wide docstring statistics; predates and
  partly inspired interrogate.
- For statically typed languages, treat the public-API surface exported from a package/module
  as the P1 layer for docstring coverage; internal-only helpers are P3 at most.

Presence is not quality. A 90% score from either tool is compatible with every docstring being
a restatement of the function name (`"""Get the user."""` on `def get_user(user_id): ...`) with
no mention of what happens on a missing user, what units a numeric argument is in, or whether
the call has side effects. Before reporting a docstring-coverage percentage as a finding:

1. Run the tool to find the raw gap list (functions/classes with zero docstring).
2. Sample 10-15 items marked "covered," weighted toward the highest-traffic or highest-risk
   modules, and judge whether a new contributor could act on the docstring alone.
3. Report both numbers if they diverge: e.g. "94% docstring coverage; ~40% of a 12-item sample
   only restated the signature — treat the raw percentage as a floor, not a quality signal."

This mirrors the mutation-score-vs-line-coverage judgment call this skill already applies to
AI-generated tests: a presence metric is a screening tool for finding candidates to check, not
a verdict on quality by itself.

## CI checklist

- changed OpenAPI specs pass Spectral
- changed OpenAPI specs pass Redocly lint
- changed AsyncAPI specs pass AsyncAPI CLI validation
- public API changes run `oasdiff` against the base spec
- changed routes or handlers have corresponding contract/doc updates
- critical examples are validated or exercised in tests where practical
- public-surface docstring coverage (interrogate or docstr-coverage) has not regressed, and a
  sample of "covered" items was actually spot-checked (see above) rather than trusted blindly

## Tool notes

Prefer these references:
- OpenAPI spec: https://spec.openapis.org/oas/latest.html
- AsyncAPI spec (3.x line; 3.1.0 reference): https://www.asyncapi.com/docs/reference/specification/v3.1.0
- Redocly CLI lint (v2.36.0+, supports OpenAPI, AsyncAPI, Arazzo): https://redocly.com/docs/cli/commands/lint
- Spectral (supports OpenAPI, AsyncAPI, Arazzo v1): https://stoplight.io/open-source/spectral
- AsyncAPI CLI: https://www.asyncapi.com/docs/tools/cli/usage
- oasdiff (replaces Optic, archived 2026-01-12): https://github.com/oasdiff/oasdiff
- interrogate (Python docstring coverage): https://interrogate.readthedocs.io/
- docstr-coverage (Python docstring coverage): https://github.com/HunterMcGushion/docstr_coverage

## Related resources

- [cicd-integration.md](cicd-integration.md)
- [priority-framework.md](priority-framework.md)
- [audit-workflows.md](audit-workflows.md)
