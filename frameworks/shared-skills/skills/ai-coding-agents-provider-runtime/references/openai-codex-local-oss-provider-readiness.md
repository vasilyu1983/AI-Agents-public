# OpenAI Codex Local OSS Provider Readiness

Sources:
- OpenAI Codex repo, commit `9f42c89c0112771dc29100a6f3fc904049b2655f`
- `codex-rs/model-provider/src/`
- `codex-rs/ollama/src/lib.rs`
- `codex-rs/lmstudio/src/lib.rs`

Use this reference when adding local model providers, provider health checks, model download flows, or provider capability gates.

## Table of Contents

- [What To Steal](#what-to-steal)
- [Portable Provider Contract](#portable-provider-contract)
- [Tests To Require](#tests-to-require)
- [Source Links](#source-links)

## What To Steal

### Provider readiness is a runtime workflow

Codex has provider-specific readiness flows for local OSS providers such as Ollama and LM Studio. The reusable pattern:

- Check whether the local provider server is reachable.
- Check provider version when a minimum behavior is required.
- Check whether the expected model is present.
- Offer or trigger model fetch/load behavior.
- Treat fetch/load failures as distinct from provider unavailability.

This is stronger than a static provider row in a config file.

Known trap:
- Marking a local provider "configured" because a base URL exists. Local providers also need server liveness, model availability, and protocol capability checks.

### Capability gates beat brand checks

Codex gates local-provider behavior on facts such as server availability, model presence, and API support. Import that as capability checks:

- supports responses-style API
- supports streaming
- supports native tool calls
- supports model pull/load
- has requested model available
- meets minimum version

Known trap:
- `provider == "ollama"` is not enough. Different versions can have different APIs and model-loading behavior.

### Warn-not-fatal fetch errors

For local providers, download or fetch can fail for reasons unrelated to model inference once the server is otherwise healthy. Treat fetch/load problems as actionable diagnostics, not generic provider failure.

Recommended result classes:

- `ready`
- `server_unreachable`
- `version_too_old`
- `model_missing`
- `model_fetch_failed`
- `model_loading`
- `protocol_unsupported`

Known trap:
- Collapsing missing model and provider offline into the same error sends users to the wrong fix.

### Defaults are bootstraps, not policy

Codex carries sensible defaults for local OSS providers, but the reusable pattern is to keep defaults in provider registration and still let runtime policy decide whether to use them.

Design rule:
- Provider registration declares default endpoint/model.
- Readiness check validates current machine state.
- Provider selection policy decides whether local inference is acceptable for the task.

Known trap:
- Automatically falling back to a local model when cloud auth fails can change privacy, quality, and tool-call semantics. That fallback must be visible.

## Portable Provider Contract

```text
ProviderRegistration
  id
  default_endpoint?
  default_model?
  capabilities
  readiness_check()

ProviderReadiness
  status
  provider_version?
  selected_model
  model_present
  minimum_version_met?
  remediation?
```

## Tests To Require

- Provider unavailable gives a different diagnostic from model missing.
- Old provider version fails a version-gated feature.
- Missing model can be fetched or produces a model-specific remediation.
- Fetch failure does not masquerade as auth or transport failure.
- Provider selection logs visible fallback when local provider replaces cloud provider.
- Cross-provider tests cover tool-call behavior for local models, not only chat completion.

## Source Links

- [model-provider crate](https://github.com/openai/codex/tree/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/model-provider/src)
- [Ollama provider readiness](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/ollama/src/lib.rs)
- [LM Studio provider readiness](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/lmstudio/src/lib.rs)
