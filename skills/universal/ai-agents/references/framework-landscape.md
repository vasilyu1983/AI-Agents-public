# Agent Framework Landscape

Generative selection toolkit for choosing an agent framework. Pair this with [`build-vs-not-decision.md`](build-vs-not-decision.md) (decide *if* you should build) and [`protocol-decision-tree.md`](protocol-decision-tree.md) (decide MCP vs A2A) before reading this file.

This is a polyglot reference. For Python+TS bot implementation depth, route to [`../../ai-bot-builder/references/framework-selection.md`](../../ai-bot-builder/references/framework-selection.md).

## Table of Contents

- [Snapshot](#snapshot)
- [Selection Matrix](#selection-matrix)
- [By Language](#by-language)
- [By Cloud Marketplace Target](#by-cloud-marketplace-target)
- [Frameworks](#frameworks)
- [Anti-Patterns](#anti-patterns)
- [Migration Paths](#migration-paths)

## Snapshot

| Framework | Lang | Runtime model | State | Eval/Obs | Protocols |
|---|---|---|---|---|---|
| **LangGraph** | Python, TS | Graph (nodes/edges, cycles, HITL) | Checkpointer + Store | LangSmith native | MCP via community; A2A via community |
| **CrewAI** | Python | Role-based crew + tasks | Flow-level runtime checkpointing (`CheckpointConfig` + `SqliteProvider`); crew task outputs otherwise implicit | CrewAI Studio + OpenTelemetry | MCP + A2A native |
| **Pydantic AI** | Python | Type-first agent + `pydantic-graph` FSM | Pydantic state, graph persistence | Logfire native | MCP native |
| **Claude Agent SDK** | Python, TS | Loop + hooks + subagents | SDK-managed conversation | Anthropic console + traces | MCP native; A2A via subagent contracts |
| **OpenAI Agents SDK** | Python, TS | Handoffs + guardrails + harness | Session resume, trace bookkeeping | Tracing native | MCP native; native sandbox (E2B/Modal/Cloudflare/etc.) |
| **Mastra** | TypeScript | Agent loop + workflow graphs (separate primitives) | Working memory + conversation memory | Built-in evals + tracing | MCP native; Vercel/Cloudflare/Netlify deployers |
| **Spring AI** | Java/Kotlin | ChatClient + Advisors + ToolCallback | Memory advisor + vector stores | Micrometer + Spring Boot Actuator | MCP native; A2A blog series Apr 2026 |
| **Microsoft Agent Framework** | .NET, Python | Agents + graph workflows (AutoGen+SK convergence) | Session state, type-safe middleware | OpenTelemetry native | MCP + A2A native |
| **Semantic Kernel** | .NET, Python, Java | Skills + planners | Memory connectors | OpenTelemetry | Migrate to MS Agent Framework |

> Before committing to a stack, check each framework's release page and changelog for the current major version and its support status (active, maintenance, or deprecated). A framework in maintenance mode is a migration cost, not a default.

## Selection Matrix

Pick the row that matches the load-bearing constraint.

| If the constraint is… | Pick | Why |
|---|---|---|
| Branching workflow with checkpoints + HITL | **LangGraph** | Only framework with first-class checkpointer + Store + interrupt/resume |
| Role-based crew, fastest time-to-prototype | **CrewAI** | Highest-level abstraction; native MCP+A2A; weak at long-running state |
| Type-safe Python with FastAPI shop | **Pydantic AI** | Pydantic-native, Logfire-native, `pydantic-graph` for FSM cases |
| Anthropic-first, deep OS access, computer use | **Claude Agent SDK** | Hooks + subagents + extended thinking + computer use |
| OpenAI-first, voice + handoffs | **OpenAI Agents SDK** | Handoffs idiom, voice support, Codex harness, sandbox providers |
| TypeScript shop, ship to Vercel/CF/Netlify | **Mastra** | TS-first, Zod tool schemas, built-in evals, scale-to-zero deployers |
| Spring/Boot enterprise app | **Spring AI** | DI-native, Advisors chain, Java/Kotlin idiom, MCP native |
| .NET enterprise + multi-agent workflows | **MS Agent Framework** | AutoGen+SK successor; A2A+MCP native; check package stability per language (Go is preview, some .NET packages still ship prerelease) |
| Existing SK codebase | **Migrate → MS Agent Framework** | Microsoft names MAF the direct successor of SK and AutoGen; confirm SK's support window on its repo before scheduling the migration |
| Gemini / Vertex AI environment | **Google ADK** | Code-first framework with strong Google ecosystem alignment; not profiled below |
| Managed AWS agent platform, lock-in acceptable | **Bedrock Agents** | Managed infra, action groups, AWS-native deployment; not profiled below |
| Retrieval quality is the primary constraint | **LlamaIndex Workflows** or **Haystack** | Retrieval and pipeline depth are first-class; not profiled below |
| Lightweight research or code-as-tools loops | **SmolAgents** or **DSPy** | Minimal or optimization-oriented; not profiled below |

Stable guidance across releases: favor workflow runtimes when you need auditability, resumability, and explicit failure handling; tool-centric SDKs when control flow is simple and the value is fast iteration; RAG-native frameworks only when retrieval quality is the primary constraint; managed platforms only when infrastructure ownership is the bottleneck and lock-in is acceptable. Verify exact language support, transport support, lifecycle, and pricing on the vendor's docs before a final recommendation.

## By Language

- **Python**: LangGraph, CrewAI, Pydantic AI, Claude Agent SDK, OpenAI Agents SDK, MS Agent Framework, Semantic Kernel
- **TypeScript**: LangGraph.js (with Store), Mastra, Claude Agent SDK, OpenAI Agents SDK
- **Java/Kotlin**: Spring AI, Semantic Kernel (limited)
- **.NET**: MS Agent Framework, Semantic Kernel

## By Cloud Marketplace Target

| Cloud | Native distribution path | Compatible frameworks |
|---|---|---|
| **AWS Marketplace / Bedrock** | Bedrock AgentCore, container deploy | Any (LangGraph, CrewAI, Mastra deployer, Pydantic AI common) |
| **Azure AI Foundry** | First-class for MS stack | MS Agent Framework, Semantic Kernel, Spring AI (Azure OpenAI) |
| **Google Cloud Model Garden / Vertex** | Agent Builder + ADK | Google ADK (not in this list), LangGraph, Pydantic AI |

If the deployment target is a marketplace listing, framework choice is shaped less by capability than by **packaging + observability fit**: MAF for Azure, Bedrock-native for AWS, ADK/LangGraph for GCP. Mastra wins TS-on-edge.

## Frameworks

### LangGraph (Python + TypeScript)

- **Shape**: Directed graph of nodes; edges may be conditional. Compiled graph is the agent.
- **State**: Two layers — `Checkpointer` (short-term, per-thread) and `Store` (long-term, cross-thread). **Keep them separate**; conflating them is the most common LG anti-pattern.
- **HITL**: First-class via `interrupt()` + resume tokens.
- **Python version**: read the classifiers on the [releases page](https://github.com/langchain-ai/langgraph/releases) or `pip index versions langgraph` before pinning; do not copy a range from prose.
- **Streaming**: v3 streaming API.
- **TS specifics**: `@langchain/langgraph-checkpoint` + `@langgraphjs/toolkit` are the current TS install.
- **Pick when**: branching, retries, approval gates, long-running graphs.
- **Avoid when**: linear pipeline (use a function); team is JS-only and prefers higher-level (use Mastra).

### CrewAI (Python)

- **Shape**: `Crew` of `Agent`s with `role` / `goal` / `backstory`, executing `Task`s. `Flow` adds event-driven control (`@start`, `@listen`, `@router`) around crews for deterministic orchestration.
- **State**: Crew task outputs are implicit and brittle for long-running work. Flows ship `@persist` state persistence plus runtime checkpointing via `CheckpointConfig` + `SqliteProvider` for automatic recovery. Judgment call: this closes most of the resumability gap for Flow-shaped orchestration, but it checkpoints at Flow-method/Crew-task boundaries only — it does not persist or resume mid-ReAct execution (i.e., a crash mid-tool-loop still replays that step from scratch). Verify current persistence guarantees in the docs before promising exactly-once recovery to stakeholders.
- **Protocols**: MCP and A2A support ship in current releases; confirm the minimum version in the CrewAI changelog before depending on either.
- **Pick when**: prototype multi-role research/content/ops crews fast; use Flows (not bare Crews) once the pipeline needs resumability or branching.
- **Avoid when**: workflow needs sub-step (mid-tool-call) durability or direct agent-to-agent messaging without Flow wrapping.
- **Migration**: CrewAI → LangGraph is gradual (LangChain-compatible), not a rewrite.

### Pydantic AI (Python)

- **Shape**: `Agent` with typed `deps_type` + `output_type`. Graphs via `pydantic-graph` (generic FSM library).
- **State**: Pydantic models all the way down. Logfire is the default observability.
- **Pick when**: FastAPI shop, type safety matters, you want LangGraph-style FSM without LangChain.
- **Avoid when**: team prefers untyped speed; non-Pydantic Python ecosystem.

### Claude Agent SDK (Python + TypeScript)

- **Shape**: Loop + hooks + subagents. Hooks intercept lifecycle points; subagents delegate.
- **Pick when**: Anthropic-only, computer use, deep OS access, safety-first audit trail.
- **Avoid when**: model portability matters. Locked to Claude.

### OpenAI Agents SDK (Python + TypeScript)

- **Shape**: Handoffs (transfer between specialized agents) + guardrails (input/output validation).
- **Harness**: a Codex-style harness wraps the model with instructions/tools/approvals/tracing/resume, with pluggable sandbox providers. Check the SDK docs for the current provider list before promising one.
- **Pick when**: OpenAI-first, voice support, multi-domain handoffs, sandboxed code exec.
- **Avoid when**: you need provider portability (it's opinionated toward OpenAI).

### Mastra (TypeScript)

- **Shape**: Agents (model-driven loop) and workflows (deterministic step graphs) are **separate primitives** — compose both.
- **State**: Working memory + conversation memory are first-class.
- **Tools**: Zod schemas — schema doubles as the prompt-facing description.
- **Deployment**: Deployers for Vercel, Cloudflare Workers, Netlify; Mastra Cloud for managed.
- **Provider**: Mastra Model Router — thousands of models across ~100+ providers via one API, automatic fallback. The exact count is a live, dynamically-updated catalog (fed from models.dev/OpenRouter/gateways) — don't quote a specific figure from memory; check `mastra.ai/models` at decision time.
- **Pick when**: TS-first stack, edge deploy, you want one framework instead of LangGraph.js + extras.
- **Avoid when**: Python ecosystem; need LangSmith.

### Spring AI (Java/Kotlin)

- **Core**: `ChatClient` (sync + streaming), `Advisors` chain, `@Tool` + `ToolCallback`, `ToolCallingManager`.
- **Agentic patterns**: A2A integration, `ToolCallAdvisor` for explicit tool-loop control, and memory tools are covered in the Spring AI blog series; check the reference docs for which release each landed in.
- **Pick when**: existing Spring Boot estate; Java/Kotlin team; DI-driven architecture.
- **Avoid when**: greenfield; non-JVM team.

### Microsoft Agent Framework (.NET + Python)

- **Status**: Microsoft's stated successor to both AutoGen and Semantic Kernel (.NET, Python, Go; Go in public preview). Confirm GA status per package on NuGet/PyPI before a production commitment; the overview still installs the .NET Foundry package with `--prerelease`.
- **Shape**: Agents + **graph-based workflows** for explicit multi-agent orchestration, plus an opinionated **Harness Agent** for long multi-step tasks (planning, compaction, file access, tool approval).
- **Standards**: A2A native, MCP native, middleware-first.
- **Pick when**: .NET shop; Azure AI Foundry deploy; need enterprise process compliance.
- **Avoid when**: pure Python team without Azure dependency (MAF Python exists but is 2nd-class to .NET).

### Semantic Kernel (.NET + Python + Java)

- **Status**: superseded by MAF per Microsoft's docs; the migration guide and an `as_agent_framework_tool` compatibility shim exist. Microsoft's docs do not state an SK end-of-support date — read the SK repo before telling stakeholders it is frozen.
- **Action**: existing SK codebases stay on SK for now; greenfield → MAF.

## Anti-Patterns

| Anti-pattern | Why it hurts | Fix |
|---|---|---|
| **A1. "Pick the trendiest framework"** | Optimizes for hype, not fit | Decide constraint first (lang, deploy target, state needs), then pick |
| **A2. CrewAI Crews (not Flows) for resumable long-running workflows** | Bare `Crew`/`Task` state is implicit and brittle; only `Flow` + `CheckpointConfig` gets you recovery, and only at method/task boundaries | Use CrewAI `Flow` with checkpointing for CrewAI-native pipelines; use LangGraph or MS Agent Framework when you need sub-step (mid-tool-call) durability |
| **A3. LangGraph for linear pipelines** | 15+ transitive deps, overhead for no win | Plain async function with TypedDict |
| **A4. Conflating LangGraph Checkpointer with Store** | Conversation state and user-level memory have different lifecycles | Separate them; checkpointer is per-thread, store is cross-thread |
| **A5. Mastra workflows used as agents (or vice versa)** | They're separate primitives by design — workflows are deterministic, agents are model-driven | Compose both; use the right tool per step |
| **A6. New SK projects** | SK is superseded; new features land in MAF | Start on MS Agent Framework |
| **A7. Provider lock for portability claims** | Claude/OpenAI SDKs are *not* provider-portable despite claims | If portability matters, use LangGraph / Pydantic AI / Mastra Router |
| **A8. Skipping eval setup until "later"** | Frameworks with built-in evals (Mastra, MAF, LangSmith) lose their value if you don't wire them on day one | Stand up eval harness in the first commit; see [`evaluation-and-observability.md`](evaluation-and-observability.md) |
| **A9. Custom A2A wire format** | A2A is now native in CrewAI/MAF/Spring AI | Use the protocol; see [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) |
| **A10. Hand-rolled sandbox for code-exec agents** | OpenAI Agents SDK and Claude Agent SDK ship sandbox plumbing | Use the SDK's sandbox integration; see [`../../ai-coding-agents-safety-envelope/SKILL.md`](../../ai-coding-agents-safety-envelope/SKILL.md) |

## Migration Paths

- **CrewAI → LangGraph**: gradual, LangChain-compatible. Migrate the parts that need checkpoints/HITL first.
- **Semantic Kernel → MS Agent Framework**: official migration guide; SK support window unsourced — verify on the SK repo.
- **AutoGen → MS Agent Framework**: same convergence; AutoGen idioms preserved in MAF agent abstractions.
- **n8n / Langflow → code-first**: see [`../../ai-bot-builder/references/migration-from-n8n.md`](../../ai-bot-builder/references/migration-from-n8n.md).
- **LangGraph.js + custom store → LangGraph Store**: collapse hand-rolled persistence into the new Store primitive.

## Verification Checklist Before Committing

Before writing the first node/agent/crew:

- [ ] Constraint matrix scored (lang × deploy target × state needs × team profile)
- [ ] Eval harness path identified (LangSmith / Logfire / Mastra evals / OTEL)
- [ ] Provider portability decision logged (locked-in vs router)
- [ ] HITL and approval policy mapped to framework primitives (interrupt vs middleware vs handoff)
- [ ] Cloud marketplace listing fit checked if relevant (AWS / Azure Foundry / GCP Model Garden)

## Sources

Verify before quoting in production decisions:

- LangGraph: <https://docs.langchain.com/oss/javascript/langgraph/persistence>, <https://langchain-ai.github.io/langgraphjs/reference/modules/langgraph-checkpoint.html>
- CrewAI: <https://docs.crewai.com/>, <https://github.com/crewAIInc/crewAI/releases>
- Pydantic AI: <https://ai.pydantic.dev/>, <https://github.com/pydantic/pydantic-ai>
- Mastra: <https://mastra.ai/>, <https://github.com/mastra-ai/mastra>
- Spring AI: <https://docs.spring.io/spring-ai/reference/api/chatclient.html>, <https://spring.io/blog/2026/04/07/spring-ai-agentic-patterns-6-memory-tools/>, <https://spring.io/blog/2026/01/29/spring-ai-agentic-patterns-a2a-integration/>
- MS Agent Framework: <https://learn.microsoft.com/en-us/agent-framework/overview/> (read 2026-09-27: successor to SK and AutoGen; .NET, Python, Go)
- SK migration: <https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/>
- OpenAI Agents SDK: <https://openai.github.io/openai-agents-python/>, <https://github.com/openai/openai-agents-python/releases>
- Claude Agent SDK: <https://code.claude.com/docs/en/agent-sdk/overview>

Third-party comparison blogs were removed as sources: they are not primary and several cited release dates we could not confirm on the vendors' own pages.
