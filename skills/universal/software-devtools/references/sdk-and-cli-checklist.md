# SDK And CLI Checklist

Use this file when reviewing an SDK, CLI, or code generator.

## SDK

- Optimize for the common path first.
- Keep transport details behind typed abstractions.
- Version the public surface deliberately and document breaking changes.
- Include install, auth, pagination, retries, and error handling in the quickstart.

## CLI

- Support `--help`, `--version`, and machine-readable output.
- Keep flags consistent across subcommands.
- Make failure messages actionable.
- Honor non-interactive execution and shell-completion needs.

## Terminal Dashboards

When a CLI tool manages a pipeline with multiple items in flight, a terminal dashboard provides real-time status without requiring a web UI.

Design checklist:

- Show pipeline state at a glance (items in progress, completed, failed).
- Support keyboard navigation for item selection and detail drilldown.
- Update in place — do not scroll the terminal with repeated output.
- Keep the dashboard read-only; use separate commands or modes for mutations.
- Degrade gracefully in narrow terminals and non-interactive sessions.

Framework choices by language:

| Language | Library | Notes |
|----------|---------|-------|
| Go | Bubble Tea (charmbracelet/bubbletea) | Elm-style architecture, rich component ecosystem |
| Rust | Ratatui | Immediate-mode rendering, cross-platform |
| Node.js | Ink (React for CLI) | Component model familiar to React developers |
| Python | Textual (Textualize) | CSS-like styling, widget library |

**Reference:** use the upstream [Charm Bubble Tea examples](https://github.com/charmbracelet/bubbletea/tree/main/examples) for terminal UI patterns; select an example compatible with the project’s installed module version.

## SDK Runtime Contract

Before generating or releasing a client, specify and test:

- Supported runtimes and module entry points; browser versus server behavior, fetch/HTTP transport injection and proxy/TLS configuration.
- Timeout scope, caller cancellation, retryable failures, retry budget and backoff. Retry a mutation only when its idempotency contract makes that safe; avoid multiplying SDK retries with application retries.
- Pagination and streaming termination/error behavior; permit callers to stop iteration without leaking connections.
- Typed domain errors plus safe transport diagnostics (HTTP status and request ID); redact tokens and sensitive response fields. Preserve useful HTTP context rather than hiding it.
- Auth refresh ownership, concurrency safety and default telemetry policy. Test from the packed package on the lowest supported runtime.

For OpenAPI generation, start self-hosted when template/control ownership matters. Compare [Stainless](https://www.stainless.com/docs/), Fern and Speakeasy when maintaining several idiomatic SDKs is the main burden. Generate a representative fixture with nullable/union types, pagination, streaming and errors before choosing; vendor feature/language support and pricing are lookup inputs, not stored rankings.

## CLI Distribution

| Product | Default distribution path | Release check |
|---|---|---|
| Go binary | [GoReleaser](https://goreleaser.com/) | Build the declared OS/architecture matrix; verify archives, signing and installer channels |
| Rust binary | [cargo-dist](https://axodotdev.github.io/cargo-dist/book/) | Inspect generated CI/installers and test clean-machine installation plus upgrade |
| Python command | Wheel with console-script entry point; document [uvx / uv tool run](https://docs.astral.sh/uv/guides/tools/) for isolated execution | Test command versus package-name differences and explicit version selection; use `uv tool install` for persistent installation |
| Homebrew audience | Formula for suitable open-source CLI software; publisher tap when core acceptance does not fit | Read [Homebrew’s packaging and acceptance rules](https://docs.brew.sh/Adding-Software-to-Homebrew), use immutable downloads, audit and run a meaningful formula test |

Keep the support matrix and installation commands in the release project. A successful cross-build does not prove that signing, dependencies or runtime startup work on each target. Custom installers follow [publisher verification and rollback checks](publishing-and-support.md#installers-and-self-update).

## Agent-Readable Documentation

Publish concise install, auth, error, retry and migration examples in Markdown. If the docs host supports it, add an [llms.txt](https://llmstxt.org/) index covering its documented path; check the proposal’s current format and verify the linked pages. It is a discovery aid, not an authorization mechanism or proof that a host will load the docs.

## Code Generation

- Generate deterministic output.
- Allow safe regeneration without clobbering handwritten code.
- Format generated code with the host ecosystem’s formatter.

### Code-Generation Patterns

- **Schema-driven**: OpenAPI spec to typed client, GraphQL schema to types and hooks, Protobuf to service stubs. Treat the schema as source of truth; CI regeneration and diff checks detect drift.
- **Template-based**: Handlebars, EJS, or custom template engines for project scaffolding and boilerplate generation. Templates should be overridable by consumers.
- **AST-based transforms**: [jscodeshift](https://github.com/facebook/jscodeshift) for syntax-oriented JavaScript/TypeScript codemods, [ts-morph](https://ts-morph.com/) when TypeScript symbols/types matter, [LibCST](https://github.com/Instagram/LibCST) for Python transforms that preserve formatting. Dry-run a fixture corpus, compile/test transformed output, and require a second pass to produce no changes.
- **Golden rule**: generated code should look like human-written code. Run the project's formatter and linter on output. Mark generated files clearly and use `.gitattributes` with `linguist-generated=true` for review; the GitHub annotation does not prevent overwriting handwritten edits.
- **Regeneration safety**: mark generated files clearly. Provide `--dry-run` to preview changes. Support partial regeneration (only changed schemas).
- **Custom generators**: when off-the-shelf generators do not fit, build custom ones. Parse the schema, walk the AST, emit code through templates. Test generated output by compiling and running it.

## IDE Extension Development

- **VS Code extension lifecycle**: `activate()` on first use of a contribution point, `deactivate()` for cleanup. Keep activation lightweight — defer heavy work.
- **Contribution points**: commands (command palette), views (sidebar panels, tree views), language features (syntax highlighting, snippets, hover info), debugging.
- **Language Server Protocol**: implement LSP for multi-editor support. One server, many clients (VS Code, Neovim, Emacs, Helix). Handles completions, diagnostics, go-to-definition, hover, formatting.
- **Webview panels**: for rich UIs inside the editor. Use message passing between extension and webview. Avoid heavy frameworks — keep webview bundles small.
- **Testing extensions**: use `@vscode/test-cli` (the official quick-setup runner, which wraps `@vscode/test-electron`) for integration tests; drop to `@vscode/test-electron` directly only for advanced setups. Mock VS Code APIs for unit tests. Test LSP servers independently with protocol-level tests.
- **Distribution**: VS Code Marketplace (`.vsix` packages) remains the default for VS Code-proper users; Open VSX (Eclipse Foundation, vendor-neutral) is the registry for VS Code forks — Cursor, VSCodium, Windsurf, and others that cannot use Microsoft's marketplace terms. Publish to both when the extension should reach fork users. JetBrains Marketplace for IntelliJ plugins.
