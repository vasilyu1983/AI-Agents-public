# Desktop Runtime Landscape

Comparison of the three main desktop / local inference runtimes as of July 2026.
Verify current version numbers and feature availability at the primary sources below before quoting to users.

## Table of Contents

- [At a Glance](#at-a-glance)
- [Ollama](#ollama)
- [LM Studio](#lm-studio)
- [Microsoft Foundry Local](#microsoft-foundry-local)
- [Decision Heuristic](#decision-heuristic)
- [Anti-Patterns](#anti-patterns)

---

## At a Glance

| Runtime | Interface | Primary audience | Model source | API surface |
|---------|-----------|-----------------|--------------|-------------|
| Ollama | CLI daemon + HTTP | Developers, power users | `ollama pull <model>` | OpenAI-compatible REST (`/v1/…`) |
| LM Studio | Desktop GUI + local server | Non-technical users, rapid model switching | HuggingFace Hub browser in-app | OpenAI-compatible REST (optional) |
| Microsoft Foundry Local | SDK + CLI | Windows / enterprise developers, SDK-first workflows | Curated Microsoft model catalog | Python / JS SDK; REST endpoint |

---

## Ollama

**What it is:** A lightweight daemon that serves GGUF models over a local HTTP endpoint. Pull → run flow mirrors Docker's UX.

**When to pick it:**
- Solo developer who wants the shortest path from zero to a working local model.
- Building an app that calls a local model via the OpenAI SDK (point `base_url` at `http://localhost:11434/v1`).
- Running a background model service that other tools (Open WebUI, simonw/llm, etc.) can share.

**When not to pick it:**
- Non-technical users who need a GUI to browse and switch models.
- Environments where a Microsoft-managed SDK or enterprise catalog is required.

**Check current version and capabilities:**
```bash
ollama --version
# See https://github.com/ollama/ollama/releases for current stable
```

> Speculative decoding, KV-cache quantization flags, and other experimental features may be available under environment variables that change between minor versions. Check `ollama help serve` or current docs before relying on them — do not assume any specific env var name is stable.

**`ollama launch`:** Ollama ships an `ollama launch <target>` command that wires up a companion coding tool or desktop app (e.g. `ollama launch codex`, `ollama launch hermes-desktop`) against a local or cloud model with no manual env vars or config files. Useful when the actual need is "point an existing agent/coding tool at a local model" rather than building a custom integration — check `ollama launch --help` for the current list of supported targets before recommending a specific one, since the catalog changes between releases.

**Primary source:** https://github.com/ollama/ollama

---

## LM Studio

**What it is:** A cross-platform (macOS, Windows, Linux) desktop application with a GUI model browser, in-app GGUF downloads from HuggingFace, and a built-in local inference server.

**When to pick it:**
- Non-technical users or team members who want to browse, download, and chat with models without touching a terminal.
- Rapid model comparisons: the GUI makes it easy to switch between quantizations and benchmark them interactively.
- Teams where the local server mode (`lms server start`) is useful but full Ollama setup is too heavy.

**When not to pick it:**
- Headless servers or CI pipelines (Ollama is more scriptable).
- When the model catalog on HuggingFace is too large and you want tighter control.

**MLX note:** LM Studio supports MLX models on Apple Silicon in addition to GGUF. This gives native Apple Neural Engine / Metal performance without running a separate MLX Python environment.

> Version numbers are fast-moving. Check https://lmstudio.ai/docs or release notes before quoting specific feature availability (e.g., MLX model format support, context length limits).

**Primary source:** https://lmstudio.ai

---

## Microsoft Foundry Local

**What it is:** A locally-running runtime from Microsoft that exposes a curated set of models (SLMs and fine-tunes from the Phi, Mistral, and Llama families) via an OpenAI-compatible SDK and a managed local endpoint. Positioned for enterprise-adjacent and Windows-native developer workflows.

**When to pick it:**
- Windows-primary developer environments where Microsoft tooling (Azure SDK, .NET, VS Code extensions) is already in use.
- Projects that want a vetted, Microsoft-signed model catalog rather than arbitrary HuggingFace pulls.
- SDK-first workflows (Python or JS/TS) where the developer prefers not to manage a daemon.

**When not to pick it:**
- macOS or Linux native workflows without Windows requirement (Ollama or MLX are simpler).
- When you need arbitrary models from HuggingFace outside the Microsoft catalog.

> Any specific throughput speedup figures cited by Microsoft (e.g., comparisons to cloud endpoints) are single-vendor benchmarks measured on their reference hardware. Verify against your own workload — do not quote them as neutral fact. See https://learn.microsoft.com/en-us/ai/foundry-local for current docs.

**Primary source:** https://learn.microsoft.com/en-us/ai/foundry-local

---

## Decision Heuristic

```
Who will operate the runtime?
├── Developer, CLI-comfortable → Ollama
│   ├── Apple Silicon, framework-level control → MLX instead
│   └── Windows SDK-first, Microsoft catalog → Foundry Local
└── Non-technical user, GUI needed → LM Studio
    └── Apple Silicon → prefer LM Studio (has MLX support) over Ollama for best Metal perf
```

---

## Anti-Patterns

- Installing more than one of these before deciding which constraint actually matters. Pick one, validate it meets the need, then move on.
- Mixing Ollama and LM Studio's local servers on the same port (both default to 11434 / similar) without explicit port configuration.
- Assuming the Microsoft Foundry Local catalog has the same model selection as the full HuggingFace Hub — it is curated and narrower.
- Citing vendor-provided speedup figures (e.g., "3.9× faster than cloud") without measuring on your own hardware.
