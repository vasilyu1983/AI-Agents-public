# AI Skill Map — All Supporting Deep Skills

*Purpose: the complete catalog of `ai-*` shared skills this advisor routes to, grouped by
decision lane. Once an approach is chosen, hand off to the primary skill for the lane; the
supporting skills cover adjacent depth. Every `ai-*` skill in the library appears here.*

## Table of Contents

- [How to Use This Map](#how-to-use-this-map)
- [Lane 1 — Choose the Approach](#lane-1--choose-the-approach)
- [Lane 2 — Classical ML / Data Science](#lane-2--classical-ml--data-science)
- [Lane 3 — LLM Lifecycle & Adaptation](#lane-3--llm-lifecycle--adaptation)
- [Lane 4 — Retrieval & Context](#lane-4--retrieval--context)
- [Lane 5 — Agents](#lane-5--agents)
- [Lane 6 — Applied Bots (Chat / Voice)](#lane-6--applied-bots-chat--voice)
- [Lane 7 — Pre-Training the Model](#lane-7--pre-training-the-model)
- [Lane 8 — Serving, Inference & Local](#lane-8--serving-inference--local)
- [Lane 9 — Evals & Quality](#lane-9--evals--quality)
- [Lane 10 — Production Ops & Operating Model](#lane-10--production-ops--operating-model)
- [Lane 11 — Build a Coding Agent (sub-family)](#lane-11--build-a-coding-agent-sub-family)
- [Coverage Note](#coverage-note)

---

## How to Use This Map

1. Use the advisor's decision tree to pick a **lane**.
2. Go to that lane below and start with the **primary** skill (bold).
3. Pull a **supporting** skill only when its specific concern appears.

Do not load every skill — load the primary for the chosen lane, then the smallest set of
supporting skills the task actually needs.

## Lane 1 — Choose the Approach

| Skill | Role |
|---|---|
| **[ai-architecture-advisor](../SKILL.md)** | This skill — decide which approach/lane before building |

## Lane 2 — Classical ML / Data Science

| Skill | Role |
|---|---|
| **[ai-ml-data-science](../../ai-ml-data-science/SKILL.md)** | EDA, feature engineering, GBDT family, modelling, evaluation, handoff |
| [ai-ml-timeseries](../../ai-ml-timeseries/SKILL.md) | Ordered observations: temporal validation, panel models, probabilistic + TS foundation models |

## Lane 3 — LLM Lifecycle & Adaptation

| Skill | Role |
|---|---|
| **[ai-llm](../../ai-llm/SKILL.md)** | Lifecycle umbrella: architecture, fine-tuning, migration, model selection, governance |
| [ai-prompt-engineering](../../ai-prompt-engineering/SKILL.md) | Prompt design, structured outputs, tool workflows, multimodal, safety |
| [ai-post-training](../../ai-post-training/SKILL.md) | Post-training & alignment: reward models, RLHF/PPO, DPO/DAAs, GRPO, RLVR, rejection sampling, RLAIF/CAI, over-optimization |

## Lane 4 — Retrieval & Context

| Skill | Role |
|---|---|
| **[ai-rag](../../ai-rag/SKILL.md)** | Retrieval design: chunking, hybrid search, reranking, grounding, RAG eval |
| `ai-context-layer` | App context assembly: profiles, memory, grounding, tenant-safe boundaries |
| [ai-vector-brain](../../ai-vector-brain/SKILL.md) | Concrete pgvector retrieval brains: scripts, SQL, manifests, evals |

## Lane 5 — Agents

| Skill | Role |
|---|---|
| **[ai-agents](../../ai-agents/SKILL.md)** | Agent architecture, protocol choice, observability, build-vs-not |

## Lane 6 — Applied Bots (Chat / Voice)

| Skill | Role |
|---|---|
| **`ai-bot-builder`** | Production chat bots: conversation flows, personas, escalation, LangGraph state |
| [ai-voice-bots](../../ai-voice-bots/SKILL.md) | Voice/IVR: telephony, STT/TTS pipelines, latency budgets, voice quality |

## Lane 7 — Pre-Training the Model

| Skill | Role |
|---|---|
| **[ai-pretraining](../../ai-pretraining/SKILL.md)** | Build transformer/GPT + BPE tokenizer from first principles |
| [ai-distributed-training](../../ai-distributed-training/SKILL.md) | Multi-GPU: FSDP, ZeRO, tensor/pipeline parallelism, reproduce GPT-2 |
| [ai-scaling-laws](../../ai-scaling-laws/SKILL.md) | Compute-optimal sizing: Kaplan, Chinchilla, token/param budget |
| [ai-data-curation-pretraining](../../ai-data-curation-pretraining/SKILL.md) | Web-scale + synthetic corpus curation, dedup, decontamination, data ablations |

## Lane 8 — Serving, Inference & Local

| Skill | Role |
|---|---|
| **[ai-llm-inference](../../ai-llm-inference/SKILL.md)** | Latency, batching, caching, quantization, routing, serving stacks |
| [ai-local-model-ops](../../ai-local-model-ops/SKILL.md) | Local/self-hosted stacks: Ollama, LM Studio, MLX, Open WebUI, llamafile |

## Lane 9 — Evals & Quality

| Skill | Role |
|---|---|
| **[ai-evals](../../ai-evals/SKILL.md)** | Graders, judge calibration, thresholds, eval/fine-tune method choice |
| [ai-deep-research](../../ai-deep-research/SKILL.md) | Verified multi-source synthesis: briefs, comparisons, research pipelines |

## Lane 10 — Production Ops & Operating Model

| Skill | Role |
|---|---|
| **[ai-mlops](../../ai-mlops/SKILL.md)** | Deployment, monitoring, retraining, incident response, GenAI security |
| [ai-product-operating-model](../../ai-product-operating-model/SKILL.md) | Platform ownership, provider strategy, data boundaries, sensitive-data controls |

## Lane 11 — Build a Coding Agent (sub-family)

When the task is *building a coding-agent runtime* (not choosing a modeling approach), start
at the umbrella and pull the component skill for the concern:

| Skill | Role |
|---|---|
| **[ai-coding-agents](../../ai-coding-agents/SKILL.md)** | Umbrella: define review/test/refactor/team coding agents |
| [ai-coding-agents-command-runtime](../../ai-coding-agents-command-runtime/SKILL.md) | Slash-command registries, lazy loading, dispatch |
| [ai-coding-agents-execution-sandbox](../../ai-coding-agents-execution-sandbox/SKILL.md) | Process isolation, filesystem/network policy, destructive-command boundaries |
| [ai-coding-agents-observability-evals](../../ai-coding-agents-observability-evals/SKILL.md) | Traces, replay, regression suites, tool-call grading, cost accounting |
| [ai-coding-agents-permissions](../../ai-coding-agents-permissions/SKILL.md) | Tool approvals, plan-mode transitions, worker permission handoffs |
| [ai-coding-agents-plugins](../../ai-coding-agents-plugins/SKILL.md) | Plugin manifests, extension points, reloadable integrations |
| [ai-coding-agents-provider-runtime](../../ai-coding-agents-provider-runtime/SKILL.md) | Model abstraction, streaming, tool-call normalization, fallback routing |
| [ai-coding-agents-release-distribution](../../ai-coding-agents-release-distribution/SKILL.md) | Packaging, auto-update channels, plugin compatibility, install footprint |
| [ai-coding-agents-remote-runtime](../../ai-coding-agents-remote-runtime/SKILL.md) | Remote sessions, local-UI remote execution, reconnect, permission bridging |
| [ai-coding-agents-sessions](../../ai-coding-agents-sessions/SKILL.md) | Resume, transcript restoration, cross-worktree recovery, session persistence |
| [ai-coding-agents-settings-policy](../../ai-coding-agents-settings-policy/SKILL.md) | Source precedence, managed policy, env controls, settings validation |
| [ai-coding-agents-tasks](../../ai-coding-agents-tasks/SKILL.md) | Task lists, worker/background execution, cancellation, teammate coordination |
| [ai-coding-agents-terminal-ui](../../ai-coding-agents-terminal-ui/SKILL.md) | REPL message flows, prompt input, virtual scroll, notifications |
| [ai-coding-agents-tools](../../ai-coding-agents-tools/SKILL.md) | Tool registries, deferred loading, permission-aware execution, tool search |

## Coverage Note

This map lists **all 36 `ai-*` skills** in `frameworks/shared-skills/skills/`. If a new
`ai-*` skill is added, add it to the matching lane here and regenerate the shared-skills
graph (`scripts/graph-export.py`). Keep "primary" to one skill per lane so the front door
stays scannable.
