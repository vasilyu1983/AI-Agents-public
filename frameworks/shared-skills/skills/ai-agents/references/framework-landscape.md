# Agent Framework Landscape — July 2026

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

| Framework | Lang | Stable | Runtime model | State | Eval/Obs | Protocols |
|---|---|---|---|---|---|---|
| **LangGraph** | Python, TS | 1.2.4 / Python 3.10–3.14, TS toolkit (Jun 2026) | Graph (nodes/edges, cycles, HITL) | Checkpointer + Store | LangSmith native | MCP via community; A2A via community |
| **CrewAI** | Python | 1.10.1 (Mar 2026) | Role-based crew + tasks | Flow-level runtime checkpointing (`CheckpointConfig` + `SqliteProvider`, since ~May 2026); crew task outputs otherwise implicit | CrewAI Studio + OpenTelemetry | MCP + A2A native |
| **Pydantic AI** | Python | 1.x (Apr 2026) | Type-first agent + `pydantic-graph` FSM | Pydantic state, graph persistence | Logfire native | MCP native |
| **Claude Agent SDK** | Python, TS | GA | Loop + hooks + subagents | SDK-managed conversation | Anthropic console + traces | MCP native; A2A via subagent contracts |
| **OpenAI Agents SDK** | Python, TS | GA + Apr 2026 harness | Handoffs + guardrails + harness | Session resume, trace bookkeeping | Tracing native | MCP native; native sandbox (E2B/Modal/Cloudflare/etc.) |
| **Mastra** | TypeScript | 1.0 (Jan 2026) | Agent loop + workflow graphs (separate primitives) | Working memory + conversation memory | Built-in evals + tracing | MCP native; Vercel/Cloudflare/Netlify deployers |
| **Spring AI** | Java/Kotlin | 1.1.x → 2.0 (2026) | ChatClient + Advisors + ToolCallback | Memory advisor + vector stores | Micrometer + Spring Boot Actuator | MCP native; A2A blog series Apr 2026 |
| **Microsoft Agent Framework** | .NET, Python | 1.0 GA (Apr 3, 2026) | Agents + graph workflows (AutoGen+SK convergence) | Session state, type-safe middleware | OpenTelemetry native | MCP + A2A native |
| **Semantic Kernel** | .NET, Python, Java | maintenance | Skills + planners | Memory connectors | OpenTelemetry | Migrate to MS Agent Framework |

> **Date stamp:** July 2026. Ecosystem moves fast — verify versions before committing to a stack.

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
| .NET enterprise + multi-agent workflows | **MS Agent Framework** | GA Apr 2026; AutoGen+SK convergence; A2A+MCP native |
| Existing SK codebase | **Migrate → MS Agent Framework** | SK is in maintenance; new features land in MAF |

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
- **Python version**: 3.10–3.14 (confirmed 1.2.4, June 2026). Verify against the [releases page](https://github.com/langchain-ai/langgraph/releases) before unpinning.
- **Streaming**: v3 streaming API.
- **TS specifics**: `@langchain/langgraph-checkpoint` + `@langgraphjs/toolkit` are the current TS install.
- **Pick when**: branching, retries, approval gates, long-running graphs.
- **Avoid when**: linear pipeline (use a function); team is JS-only and prefers higher-level (use Mastra).

### CrewAI (Python)

- **Shape**: `Crew` of `Agent`s with `role` / `goal` / `backstory`, executing `Task`s. `Flow` adds event-driven control (`@start`, `@listen`, `@router`) around crews for deterministic orchestration.
- **State**: Crew task outputs are implicit and brittle for long-running work. Flows now ship `@persist` state persistence plus (since ~May 2026) runtime checkpointing via `CheckpointConfig` + `SqliteProvider` for automatic recovery. Judgment call: this closes most of the resumability gap for Flow-shaped orchestration, but it checkpoints at Flow-method/Crew-task boundaries only — it does not persist or resume mid-ReAct execution (i.e., a crash mid-tool-loop still replays that step from scratch). Verify current persistence guarantees in the docs before promising exactly-once recovery to stakeholders.
- **Protocols**: Native MCP + A2A as of v1.10.
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
- **Apr 2026 update**: Codex-style **harness** wraps model with instructions/tools/approvals/tracing/resume. Native sandbox via E2B, Modal, Cloudflare, Daytona, Runloop, Vercel, Blaxel.
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
- **2026 patterns**: A2A integration (Jan 2026 blog series), `ToolCallAdvisor` for explicit tool-loop control (1.1.0-M4), `AutoMemoryTools` for persistent memory (Apr 2026).
- **Pick when**: existing Spring Boot estate; Java/Kotlin team; DI-driven architecture.
- **Avoid when**: greenfield; non-JVM team.

### Microsoft Agent Framework (.NET + Python)

- **Status**: 1.0 GA on April 3, 2026. Convergence of AutoGen + Semantic Kernel.
- **Shape**: Agents + **graph-based workflows** for explicit multi-agent orchestration.
- **Process Framework**: Q2 2026 — deterministic enterprise workflows with audit trails, low-code visual design, checkpointing, HITL.
- **Standards**: A2A native, MCP native, middleware-first.
- **Pick when**: .NET shop; Azure AI Foundry deploy; need enterprise process compliance.
- **Avoid when**: pure Python team without Azure dependency (MAF Python exists but is 2nd-class to .NET).

### Semantic Kernel (.NET + Python + Java)

- **Status**: maintenance. Critical bugs/security only. New features go to MAF.
- **Action**: existing SK codebases stay on SK for now; greenfield → MAF. Migration guide is published.

## Anti-Patterns

| Anti-pattern | Why it hurts | Fix |
|---|---|---|
| **A1. "Pick the trendiest framework"** | Optimizes for hype, not fit | Decide constraint first (lang, deploy target, state needs), then pick |
| **A2. CrewAI Crews (not Flows) for resumable long-running workflows** | Bare `Crew`/`Task` state is implicit and brittle; only `Flow` + `CheckpointConfig` gets you recovery, and only at method/task boundaries | Use CrewAI `Flow` with checkpointing for CrewAI-native pipelines; use LangGraph or MS Agent Framework when you need sub-step (mid-tool-call) durability |
| **A3. LangGraph for linear pipelines** | 15+ transitive deps, overhead for no win | Plain async function with TypedDict |
| **A4. Conflating LangGraph Checkpointer with Store** | Conversation state and user-level memory have different lifecycles | Separate them; checkpointer is per-thread, store is cross-thread |
| **A5. Mastra workflows used as agents (or vice versa)** | They're separate primitives by design — workflows are deterministic, agents are model-driven | Compose both; use the right tool per step |
| **A6. New SK projects in 2026** | SK is in maintenance | Start on MS Agent Framework |
| **A7. Provider lock for portability claims** | Claude/OpenAI SDKs are *not* provider-portable despite claims | If portability matters, use LangGraph / Pydantic AI / Mastra Router |
| **A8. Skipping eval setup until "later"** | Frameworks with built-in evals (Mastra, MAF, LangSmith) lose their value if you don't wire them on day one | Stand up eval harness in the first commit; see [`evaluation-and-observability.md`](evaluation-and-observability.md) |
| **A9. Custom A2A wire format** | A2A is now native in CrewAI/MAF/Spring AI | Use the protocol; see [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) |
| **A10. Hand-rolled sandbox for code-exec agents** | OpenAI Agents SDK ships sandbox integrations with 7 providers | Use the SDK's sandbox plumbing |

## Migration Paths

- **CrewAI → LangGraph**: gradual, LangChain-compatible. Migrate the parts that need checkpoints/HITL first.
- **Semantic Kernel → MS Agent Framework**: official migration guide; SK supported ≥1 year post-GA.
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
- CrewAI vs LangGraph 2026: <https://gurusup.com/blog/best-multi-agent-frameworks-2026>, <https://redwerk.com/blog/langgraph-vs-crewai/>
- Pydantic AI: <https://ai.pydantic.dev/>, <https://github.com/pydantic/pydantic-ai>
- Mastra 1.0: <https://mastra.ai/>, <https://github.com/mastra-ai/mastra>, <https://www.generative.inc/mastra-ai-the-complete-guide-to-the-typescript-agent-framework-2026>
- Spring AI: <https://docs.spring.io/spring-ai/reference/api/chatclient.html>, <https://spring.io/blog/2026/04/07/spring-ai-agentic-patterns-6-memory-tools/>, <https://spring.io/blog/2026/01/29/spring-ai-agentic-patterns-a2a-integration/>
- MS Agent Framework GA: <https://learn.microsoft.com/en-us/agent-framework/overview/>, <https://techcommunity.microsoft.com/blog/azuredevcommunityblog/the-future-of-agentic-ai-inside-microsoft-agent-framework-1-0/4510698>
- SK migration: <https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/>
- OpenAI Agents SDK Apr 2026 harness: <https://qubittool.com/blog/ai-agent-framework-comparison-2026>, <https://composio.dev/content/claude-agents-sdk-vs-openai-agents-sdk-vs-google-adk>
