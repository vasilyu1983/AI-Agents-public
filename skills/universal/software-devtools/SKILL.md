---
name: software-devtools
description: "Builds developer tools. Use when writing a codemod, SDK, CLI, language server (LSP), IDE extension, or package distribution; dependency audits go to dev-dependency-management."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Developer Experience & SDK Engineering

## Quick Reference

| Concern | Defaults |
|---|---|
| CLI framework (Node.js) | Commander.js, oclif, Ink (React for CLI) |
| CLI framework (Go) | Cobra + Viper |
| CLI framework (Rust) | clap + dialoguer |
| CLI framework (Python) | Click / Typer |
| SDK design | Typed clients, builder pattern, progressive disclosure |
| Code generation | OpenAPI Generator (self-hosted), Stainless/Fern/Speakeasy (managed; compare generated runtime contracts), GraphQL Codegen, Protobuf/Connect, custom AST transforms |
| IDE extensions | VS Code Extension API, JetBrains Plugin SDK, LSP (Language Server Protocol) |
| Package publishing | npm, PyPI, crates.io, NuGet, Maven Central |
| Developer docs | Mintlify, Docusaurus, Starlight, ReadMe, Fern |
| DX metrics | Time-to-first-API-call, SDK adoption, error rate, support tickets |

## When to Use This Skill

- Building a CLI tool for developers (argument parsing, subcommands, interactive prompts)
- Designing and implementing an SDK or client library for an API
- Creating code generators from OpenAPI, GraphQL, or Protobuf schemas
- Building VS Code extensions, JetBrains plugins, or Language Server Protocol implementations
- Publishing packages to registries (npm, PyPI, crates.io, NuGet)
- Measuring and improving developer experience metrics
- Building codemods or AST-based code transformation tools

## When NOT to Use This Skill

- **Building user-facing web or mobile apps** → [software-frontend](../software-frontend/SKILL.md), [software-mobile](../software-mobile/SKILL.md)
- **API design principles (not SDK implementation)** → [dev-api-design](../dev-api-design/SKILL.md)
- **Backend service implementation** → [software-backend](../software-backend/SKILL.md)
- **CI/CD pipeline and platform engineering** → [ops-devops-platform](../ops-devops-platform/SKILL.md)
- **Agent and skill development** → [agents-skills](../agents-skills/SKILL.md), [agents-mcp](../agents-mcp/SKILL.md)
- **Dependency auditing and upgrade strategy** → [dev-dependency-management](../dev-dependency-management/SKILL.md)

## Workflow

1. Classify the tool surface: CLI, SDK, code generator, editor extension, or codemod.
2. Route user-facing app work, backend services, or dependency-policy questions to the adjacent skill when appropriate.
3. Choose the implementation pattern from the decision tree and make the output contract explicit.
4. Apply the relevant guidance for packaging, DX, code generation, or editor integration.
5. Re-check registry, tooling, and platform specifics through the navigation references before final recommendations.

## Decision Tree

```text
What kind of developer tool?
├─ Interactive terminal tool
│  └─ CLI framework per language (Commander.js / Cobra / clap / Typer)
│     ├─ Needs interactive prompts? → Ink, dialoguer, Typer, survey
│     └─ Needs scriptable output? → --json flag, structured stdout
├─ Library other devs import
│  └─ SDK with typed API, clear errors, minimal dependencies
│     ├─ Wrapping a REST API? → Typed client from OpenAPI spec
│     ├─ Wrapping a GraphQL API? → Codegen typed operations
│     └─ General-purpose library? → Builder pattern, progressive disclosure
├─ Editor integration
│  ├─ VS Code only? → VS Code Extension API
│  ├─ Multiple editors? → Language Server Protocol (LSP)
│  └─ JetBrains only? → IntelliJ Plugin SDK
├─ Generate code from schema
│  ├─ OpenAPI → OpenAPI Generator or custom templates
│  ├─ GraphQL → GraphQL Codegen with typed plugins
│  └─ Protobuf → buf + Connect or gRPC codegen
├─ Transform existing code
│  ├─ JavaScript/TypeScript → jscodeshift or ts-morph
│  ├─ Python → libcst
│  └─ Multi-language → custom AST tooling per parser
└─ Developer documentation portal
   ├─ Fast setup, good defaults → Mintlify or Starlight
   └─ Full React flexibility → Docusaurus
```

## SDK Design Principles

Keep the API surface small. Every public method is a commitment.

- **Progressive disclosure**: simple default usage with zero config, advanced options available but not required. `client.send(message)` works out of the box; `client.send(message, { retries: 3, timeout: 5000 })` is there when needed.
- **Builder / fluent pattern**: use for complex configuration — `new ClientBuilder().withAuth(token).withRetries(3).build()`. Avoid deep option objects with 20 fields.
- **Error messages that help**: include what went wrong, why, and how to fix it. Add docs links for common errors. Preserve safe HTTP status/request IDs with context; redact sensitive response fields.
- **Typed responses**: return strongly typed objects, not raw JSON. Union types for error states. Discriminated unions over catch-all error types.
- **Semantic versioning**: truly breaking changes are major bumps. Additive features are minor. Bug fixes are patch. Document migration paths for every major version.
- **Minimal dependencies for core**: zero runtime dependencies is the goal. Use peer dependencies for optional integrations. Separate core from plugins.
- **Idiomatic per language**: a Python SDK should feel Pythonic, a Go SDK should feel like Go. Do not port Java patterns to JavaScript.

## CLI Development Patterns

**Automation contract.**

Treat exit codes, stdout, stderr, and machine-readable output as a public API. Human progress belongs on stderr; requested data belongs on stdout; `--json` must remain parseable with no banners or color. Use one documented scheme: 0 = complete success, 1 = execution failure (including validation, transient dependency failure, and partial completion), 2 = invalid invocation. Put distinct error codes, retryability, and completed/failed item lists in JSON rather than inventing extra process statuses. Test under pipes, non-interactive CI, and cancellation; document signal-exit behavior separately.

- **Argument parsing**: positional args for required inputs, flags for options, subcommands for distinct operations. `tool <command> [args] [--flags]` is the universal pattern.
- **Subcommand structure**: group related operations. `tool auth login`, `tool auth logout`, `tool config set`. Keep depth to two levels maximum.
- **Interactive prompts**: offer explicit confirmation for destructive actions and optional input selection. In non-interactive mode, missing required values fail with exit 2; do not open a prompt. Make every input available as a flag and document what `--yes` approves.
- **Progress indicators**: spinners for indeterminate work, progress bars for known-length operations. Always provide a `--quiet` / `--silent` flag.
- **Colored output**: use color for emphasis and status (green=success, red=error, yellow=warning). Respect `NO_COLOR` environment variable and `--no-color` flag.
- **Config file discovery**: `~/.config/toolname/config.yaml`, `.toolnamerc`, `toolname.config.js` — support a sensible hierarchy with local overrides.
- **Exit codes**: 0 for success, 1 for general errors, 2 for usage errors. Document non-zero codes in help text.
- **Shell completions**: generate completions for bash, zsh, fish. Ship them or provide `tool completions <shell>` command.
- **`--json` flag**: every command that produces output should support `--json` for machine-readable structured output. Scriptability is not optional.
- **Installers and self-update**: verify a signature against a key pinned out of band, never a same-origin checksum alone. Keep the previous binary until the new one passes a self-check. Ship `sh` and `ps1` install scripts, and set halt criteria before a rollout. Checklist: [references/publishing-and-support.md](references/publishing-and-support.md#installers-and-self-update).

## Agent-Friendly CLI Patterns

Agents are now primary CLI consumers alongside humans. Design for both.

- **Non-interactive first**: every input passable as a flag. If your CLI drops into a prompt mid-execution, an agent is stuck. Interactive mode is the fallback when flags are missing, not the primary path.
- **Progressive `--help` discovery**: don't dump all docs upfront. An agent runs `mycli`, sees subcommands, picks one, runs `mycli deploy --help`, gets what it needs. No wasted context on commands it won't use.
- **Examples in every `--help`**: agents pattern-match off `mycli deploy --env staging --tag v1.2.3` faster than they read a description. Every subcommand's help should include at least two usage examples.
- **Flags and stdin for everything**: agents think in pipelines. Accept `--stdin` for config import, support `--output tag-only` for chaining. Don't require positional args in unusual orders.
- **Fail fast with actionable errors**: if a required flag is missing, error immediately and show the correct invocation. Include a "did you mean?" or "available values" hint. Agents self-correct when given something to work with.
- **Idempotent commands**: agents retry constantly (network timeouts, context loss). Running the same deploy twice should return "already deployed, no-op", not create a duplicate.
- **`--dry-run` for destructive actions**: agents should preview what a deploy or deletion would do before committing. Let them validate the plan, then run it for real.
- **Separate confirmation from force**: `--yes` approves the stated plan; `--force` may change overwrite policy. Neither may disable credential checks, signature validation, or authorization.
- **Predictable command structure**: if an agent learns `mycli service list`, it should be able to guess `mycli deploy list` and `mycli config list`. Pick a pattern (resource + verb or verb + resource) and use it everywhere.
- **Return data on success**: show the deployment ID, URL, and duration — not just a success emoji. Machine-parseable output lets agents chain results into subsequent commands.

## Code Generation

Load [sdk-and-cli-checklist.md](references/sdk-and-cli-checklist.md#sdk-runtime-contract) before selecting a generator or shipping a client; define its runtime, cancellation and retry contract. Treat generated code as a product surface: schema-driven (OpenAPI/GraphQL/Protobuf) where a schema exists, AST-based transforms instead of fragile regex, output run through the project's formatter, clear generated-file markers plus `linguist-generated=true` for review, and safe `--dry-run`/partial regeneration. Patterns: [references/sdk-and-cli-checklist.md](references/sdk-and-cli-checklist.md#code-generation-patterns).

## IDE Extension Development

Keep `activate()` lightweight, prefer LSP for multi-editor language features, keep webview bundles small, test LSP servers at the protocol level, and publish to both the VS Code Marketplace and Open VSX when fork users matter. Details: [references/sdk-and-cli-checklist.md](references/sdk-and-cli-checklist.md#ide-extension-development).

## Package Publishing Best Practices

- **Semantic versioning**: the version number is a contract. Truly breaking changes require a major bump — not just a changelog note.
- **Changelogs**: use conventional commits (`feat:`, `fix:`; mark breaking changes with `!` before the colon, e.g. `feat!:`, or a `BREAKING CHANGE:` footer — `breaking:` is not a spec type and will not trigger a major bump) and auto-generate changelogs. Keep a human-readable `CHANGELOG.md` for significant releases.
- **Provenance and trusted publishing**: prefer registry OIDC over static publish tokens. For npm, look up supported CI providers, CLI requirements, allowed publish actions and provenance eligibility at [trusted-publishers](https://docs.npmjs.com/trusted-publishers/). Automatic provenance requires an eligible provider and public repository/package; verify the resulting attestation rather than assuming OIDC implies it. Check each other registry’s own setup before wiring a release.
- **Module format for Node.js**: `require(esm)` is unflagged in Node v20.19 / v22.12 / v23+, so CommonJS consumers can `require()` an ESM-only package. If your supported Node floor is `^20.19 || >=22.12`, ship ESM-only (declare it in `engines`) and avoid the dual-package hazard; only synchronous ESM can be `require()`d, so keep top-level `await` out of the entry graph. Ship dual CJS/ESM (conditional `exports`, test both entry points) only when you must support older runtimes or tooling that cannot load ESM.
- **Tree-shaking support**: declare `sideEffects: false` only when imports have no required side effects; preserve CSS/polyfill initialization in explicit entries ([webpack guidance](https://webpack.js.org/guides/tree-shaking/)). Test consumer bundling and export granularly.
- **Deprecation strategy**: deprecate old versions with `npm deprecate` or equivalent. Provide migration guides. Declare which previous majors receive security fixes and for how long; make that support commitment match maintenance capacity.

### Pre-Publish Checklist and Supply-Chain Hardening

Before release, test the packed artifact, every supported entry point and runtime, and the publishing identity. Publisher hardening: [references/publishing-and-support.md](references/publishing-and-support.md#pre-publish-checklist).

## Tool-Adoption Boundary

Toolchain selection, dependency audits and upgrade policy use [dev-dependency-management](../dev-dependency-management/SKILL.md).
Here, measure the tool you publish: feedback-loop time, compatibility failures and migration effort.

## DX Metrics

Measure local feedback-loop time, time-to-first-API-call, onboarding drop-off per step, latest-major adoption, error rate by method, support-ticket clustering, and developer satisfaction. Targets and off-signals: [references/publishing-and-support.md](references/publishing-and-support.md#dx-metrics).

## Known Traps

- Letting the public SDK or CLI surface leak internal transport quirks, unstable IDs, or backend-specific retry semantics.
- Treating code generation as a one-time scaffolding concern instead of a product surface with readability, compatibility, and regeneration guarantees.
- Verifying a package only from the source tree rather than from the packed artifact consumers actually install.
- Building an IDE extension with heavy startup work in the activation path, then discovering the tool feels broken before it does anything useful.
- Shipping human-friendly output only, then discovering automation and agent workflows have no stable machine-readable contract.

## Do / Avoid, Anti-Patterns, and Scenarios

The Do/Avoid list, common anti-patterns, and step-by-step recipes (S1 SDK release with changesets, S2 agent-consumable CLI, S3 OpenAPI-to-SDK pipeline, S4 LSP for a custom DSL, S5 IDE-extension auth and token refresh) live in [references/dx-scenarios-and-antipatterns.md](references/dx-scenarios-and-antipatterns.md).

## Navigation

### References
- [references/sdk-and-cli-checklist.md](references/sdk-and-cli-checklist.md) — SDK runtime contract, CLI distribution, codemod tools, and editor-integration checklist
- [references/publishing-and-support.md](references/publishing-and-support.md) — release, package-signing, docs, support, and deprecation workflow
- [references/dx-scenarios-and-antipatterns.md](references/dx-scenarios-and-antipatterns.md) — Do/Avoid list, common anti-patterns, and S1–S5 DX and distribution recipes
- [references/mcp-server-development.md](references/mcp-server-development.md) — when and how to expose a developer tool as an MCP server; tool/resource/prompt design; testing and distribution. SDK setup, transports, auth, and client config live in [agents-mcp](../agents-mcp/references/mcp-custom.md)
- [data/sources.json](data/sources.json) — official docs for SDK, CLI, IDE, and package-publishing ecosystems

### Related Skills

- [dev-api-design](../dev-api-design/SKILL.md) — API design principles and REST/GraphQL conventions
- [software-backend](../software-backend/SKILL.md) — General backend service patterns
- [software-frontend](../software-frontend/SKILL.md) — Frontend application development
- [ops-devops-platform](../ops-devops-platform/SKILL.md) — CI/CD pipeline and platform engineering
- [dev-dependency-management](../dev-dependency-management/SKILL.md) — Dependency auditing and upgrade strategy
- [docs-codebase](../docs-codebase/SKILL.md) — Codebase documentation standards

## Tooling and Registry Lookup

Before selecting a generator, check its supported schema features and languages at the vendor docs linked in [data/sources.json](data/sources.json).
Before publishing, look up registry identity/provenance requirements and test the CLI’s target OS/runtime installation matrix using [publishing-and-support.md](references/publishing-and-support.md).
For editor integrations, check the selected host API and LSP capability support; retain the tested version in the project’s release configuration.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
