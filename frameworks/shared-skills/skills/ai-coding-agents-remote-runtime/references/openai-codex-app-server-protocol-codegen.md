# OpenAI Codex App-Server Protocol Codegen

Sources:
- OpenAI Codex repo, commit `9f42c89c0112771dc29100a6f3fc904049b2655f`
- `codex-rs/app-server-protocol/src/export.rs`
- `codex-rs/app-server-protocol/tests/schema_fixtures.rs`

Use this reference when building a remote runtime, app server, editor bridge, or local daemon with a typed control protocol.

## What To Steal

### Generate protocol artifacts from one source

Codex's app-server protocol exports TypeScript and JSON schema artifacts from protocol definitions. The useful pattern is source-of-truth protocol generation:

- Define protocol types in one owning crate/module.
- Export client-facing artifacts.
- Mark generated files with a clear generated-code header.
- Filter experimental APIs when producing stable public artifacts.

Known trap:
- Handwritten protocol types in CLI, daemon, and UI code drift quickly. The remote runtime then fails at the worst boundary: reconnect, approval, or app update.

### Experimental API filtering

Codex's exporter can distinguish experimental surface from stable surface. Import this into any bridge protocol with third-party clients.

Design rule:
- Stable clients only receive stable method/schema artifacts.
- Experimental artifacts are generated separately or explicitly labeled.
- Runtime rejects unsupported experimental calls with structured errors.

Known trap:
- A single "latest schema" endpoint becomes an accidental compatibility promise for work-in-progress methods.

### Schema fixture tests

Codex tests generated schema fixtures and offers a write/update path for fixtures. The reusable shape:

- Generate schema output in tests.
- Compare against committed fixture.
- Show useful diff on mismatch.
- Provide a deliberate fixture-update command.

This is a strong guard against invisible protocol drift.

Known trap:
- Snapshot tests that silently rewrite generated protocol files in CI are not tests. Schema updates should be explicit review events.

## Portable Remote Runtime Contract

```text
ProtocolDefinition
  stable_methods
  experimental_methods
  request_types
  response_types
  event_types

GeneratedArtifacts
  typescript_client
  json_schema
  generated_header
  fixture_version
```

Bridge clients should validate:

- method exists in the selected protocol tier
- request payload matches schema
- response or error payload matches schema
- reconnect/control events are versioned

## Tests To Require

- Generated TypeScript or client artifact includes a generated-code header.
- Experimental methods are absent from stable schema output.
- Schema fixture diff fails CI when protocol changes.
- Fixture update command is manual and reviewable.
- Unknown method returns structured unsupported-method error.
- Client and daemon versions expose enough metadata to explain compatibility failures.

## Source Links

- [app-server protocol exporter](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/app-server-protocol/src/export.rs)
- [app-server schema fixtures](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/app-server-protocol/tests/schema_fixtures.rs)
