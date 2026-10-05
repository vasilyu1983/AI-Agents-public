# DX Do/Avoid, Anti-Patterns, and Scenarios

Use this file for concrete DX recipes and review checks. The decision core stays in [SKILL.md](../SKILL.md).

## Do / Avoid

**Do**

- Design the common path first; expose advanced controls without requiring them for basic use.
- Write error messages that tell the developer what went wrong, why, and what to do about it.
- Ship shell completions, `--json` output, and `--help` with examples from day one.
- Test your SDK in the same way your consumers will use it — install from the registry, follow the quickstart.
- Run the project's formatter on generated code so it matches the surrounding codebase.
- Measure time-to-first-API-call and set an onboarding budget from observed user friction.
- Publish changelogs and migration guides for every major version.
- Respect `NO_COLOR`, `--quiet`, and `--yes` flags in every CLI tool.

**Avoid**

- Leaking secrets or unstable backend details through SDK errors; preserve safe HTTP status/request IDs for diagnosis.
- Adding dependencies to core packages that consumers do not need — use peer dependencies or plugins.
- Shipping generated code that looks auto-generated (inconsistent formatting, `__generated__` noise, excessive comments).
- Breaking backward compatibility in minor or patch releases.
- Building IDE extensions with heavy activation costs — defer expensive initialization.
- Skipping the pre-publish checklist (bundle size, type correctness, install test).
- Ignoring developer feedback and support ticket patterns as DX signals.
- Porting idioms from one language to another (Java patterns in a Python SDK, Ruby patterns in a Go CLI).

## Common Anti-Patterns

- Exposing every backend feature immediately instead of curating the smallest stable developer surface.
- Using breaking output-format changes in CLIs or generators without versioning, feature flags, or migration notes.
- Building one monolithic package that mixes core runtime, integrations, templates, and experimental features.
- Measuring adoption only by install counts while ignoring time-to-first-success, support load, and version-upgrade pain.
- Designing tools for maintainers who know the internals instead of external developers who only see the docs and errors.

## Scenarios

Recipes keyed to DX or distribution moments. Each lists the shortest path to a ship-ready, consumer-safe outcome.

### S1 — SDK release with semver + changeset

1. Install `changesets` (`@changesets/cli`); run `changeset init` to create the `.changeset/` directory.
2. For each PR, contributors run `changeset` to declare the semver bump level and write a change summary.
3. On merge to `main`, the Changesets GitHub Action opens a "Release PR" that aggregates bumps and updates `CHANGELOG.md`.
4. Merge the Release PR; the action publishes to the registry and creates a Git tag.
5. Verify the published package with `npm pack` + install from tarball before merging the Release PR.
6. For breaking changes: include a migration guide in the changeset body; link it from the npm package README.

### S2 — CLI for AI agent consumption (structured errors, --json)

1. Add `--json` to every subcommand; on success, emit `{ "ok": true, "data": { ... } }`; on error, emit `{ "ok": false, "error": { "code": "...", "message": "..." } }`.
2. Use exit code 0 for success, 1 for runtime errors, 2 for usage errors; document codes in `--help`.
3. Make every required input passable as a flag; never rely on interactive prompts as the only path.
4. Add `--dry-run` to all destructive commands; agents validate the plan before committing.
5. Add `--yes` to skip confirmation prompts; agents pass it in automation contexts.
6. Run the CLI through an agent smoke test: have an LLM issue three chained commands using only `--help` output for discovery.

### S3 — OpenAPI to typed SDK generation pipeline

1. Confirm the OpenAPI spec is the source of truth; set up spec linting in CI. Check the released linter and generator against the exact schema features you use; a draft or development-branch implementation is insufficient.
2. Choose a generator: `openapi-generator-cli` (self-hosted; budget maintenance and compute), or a managed generator such as Stainless, Fern or Speakeasy for idiomatic, low-maintenance SDKs with synced docs. Managed generators cost money and add a vendor dependency — pick them when SDK polish and low upkeep matter more than self-hosting.
3. Run generation in CI on every spec change; commit generated files with `linguist-generated=true` in `.gitattributes`.
4. Add a compile-only test that imports the generated client and calls one method; catches schema drift before release.
5. Run the project formatter on generated output; generated code must match the surrounding codebase style.
6. Version the generated SDK separately from the spec; publish via the changeset flow in S1.

### S4 — LSP for custom DSL: incremental parsing + diagnostics

1. Implement the language server using the LSP SDK for your language (e.g. `vscode-languageserver` for Node.js or `tower-lsp-server` for Rust); check SDK support for the protocol features you need.
2. Use a tree-sitter grammar or hand-written incremental parser; measure whether full parsing fits the document-size/latency budget before adding incremental state.
3. On `textDocument/didChange`, apply incremental edits to the parse tree; publish diagnostics via `textDocument/publishDiagnostics`.
4. Implement `textDocument/completion` and `textDocument/hover` using the AST node at the cursor position.
5. Write protocol-level tests with a mock LSP client; test diagnostics, completions, hover, cancellation and negotiated capabilities independently of any editor. Choose full or incremental synchronization according to the advertised `textDocumentSync` contract.

### S5 — IDE extension auth + token refresh

1. Store tokens in the platform secret store (`vscode.SecretStorage`, not `globalState`); never in `settings.json`.
2. When an authenticated command is invoked, check for a stored token; if absent, open the auth flow via `vscode.env.openExternal` + a local callback server.
3. Before each API call, check token expiry; refresh before expiry using the provider’s documented clock-skew allowance.
4. On `401`, attempt one permitted refresh and retry; [RFC 6750 §3.1](https://www.rfc-editor.org/rfc/rfc6750#section-3.1) distinguishes expired, revoked and otherwise invalid tokens. If refresh fails, clear unusable credentials and re-authenticate. Never loop indefinitely.
5. Keep activation lightweight: defer the auth check and API calls until the user invokes a command, not at `activate()`.
