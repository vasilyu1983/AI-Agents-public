# AWS Bedrock AgentCore

Amazon Bedrock AgentCore is AWS's **modular** agent platform: a set of independently composable services for hosting, memorizing, governing, and operating agents at scale. Treat it as the 2026 AWS-native path for code-based agent builds, distinct from the older fully-managed Bedrock Agents (classic).

Use this when the user is building or migrating an agent workload onto AWS and needs more than "Lambda + a Bedrock model call."

Volatile facts (pricing, preview status, session limits) were last checked 2026-07-11 against AWS's AgentCore docs and pricing page; re-verify before quoting hard numbers — see [`../data/sources.json`](../data/sources.json).

---

## Table of Contents

- [Quick decision: AgentCore vs Bedrock Agents (classic) vs roll-your-own](#quick-decision-agentcore-vs-bedrock-agents-classic-vs-roll-your-own)
- [The AgentCore service surface](#the-agentcore-service-surface)
- [Runtime: hosting model](#runtime-hosting-model)
- [Memory: managed conversation + facts](#memory-managed-conversation--facts)
- [Gateway: API/Lambda → MCP tools](#gateway-apilambda--mcp-tools)
- [Identity, Code Interpreter, Browser](#identity-code-interpreter-browser)
- [Observability, Evaluations, Policy](#observability-evaluations-policy)
- [Framework choice](#framework-choice)
- [Multi-tenant pattern](#multi-tenant-pattern)
- [When to pick AgentCore vs Lambda vs Fargate](#when-to-pick-agentcore-vs-lambda-vs-fargate)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

---

## Quick decision: AgentCore vs Bedrock Agents (classic) vs roll-your-own

| Choice | When |
|---|---|
| **AgentCore** | New code-based AWS agent build, want framework freedom (LangGraph / CrewAI / LlamaIndex / OpenAI Agents SDK / Strands / custom), need long sessions (up to 8h), need managed memory + identity + tools without building them. |
| **Bedrock Agents (classic)** | Already on it, locked to Lambda + Bedrock KBs + Bedrock-hosted models, want **zero code** and configuration-only. AWS keeps maintaining it; not the forward path. |
| **Roll your own** (Lambda + Fargate + DynamoDB + custom memory) | You have specific compliance, vendor, or cost constraints that force it. Otherwise AgentCore wins on time-to-production. |

If you're choosing today: prefer **AgentCore** for code-based agents unless the requirement is specifically a configuration-only Bedrock Agent or a short stateless Lambda call.

---

## The AgentCore service surface

Ten capabilities show up across the current AgentCore docs/pricing surface. Pick the ones you need; they compose.

| Service | What it does | Closest non-AWS analog |
|---|---|---|
| **Runtime** | Serverless microVM hosting for agent code; up to 8h sessions; framework-agnostic | Modal, E2B, Daytona, Fly Machines |
| **Memory** | Managed conversation store + automatic fact extraction + semantic retrieval | Letta, mem0, Zep, OpenAI memory |
| **Gateway** | Turn existing APIs/Lambda into MCP tools agents can call | Cloudflare AI Gateway (different focus), Zapier MCP server |
| **Identity** | Agent-aware auth + delegated access to AWS resources | OAuth + per-agent IAM, but managed |
| **Code Interpreter** | Sandboxed Python/code execution per session | E2B, Anthropic code execution, OpenAI code interpreter |
| **Browser** | Managed headless browser per agent session | Browserbase, Hyperbrowser |
| **Observability** | Trace + metrics + replay for agent runs | Langfuse, Arize Phoenix, Helicone |
| **Evaluations** | 13 built-in quality evaluators for agent output | Braintrust, Patronus, Ragas (DIY) |
| **Policy** | Natural-language policy enforcement at runtime | Anthropic constitutional layer, OPA |
| **Registry** | Governed catalog for agents, MCP servers, tools, skills, and custom resources | Internal developer portal, Backstage catalog |

You can adopt any subset. Common minimal start: **Runtime + Memory + Gateway**.

---

## Runtime: hosting model

The unit of execution is a **session** — one user's conversation or one long-running task.

| Property | Value |
|---|---|
| Isolation | Dedicated microVM (Firecracker) per session — CPU, memory, filesystem isolated |
| Max session length | **8 hours** (large compared to Lambda's 15min) |
| Concurrency | Sessions are independent; scale horizontal |
| Cold start | Verify for the target region and deployment mode; AWS abstracts the microVM pool |
| Pricing | Consumption-based: separate per-vCPU-hour and per-GB-memory-hour rates, billed per second with a 1-second minimum; CPU billing pauses during I/O waits (e.g. waiting on an LLM response), so idle-within-session time is largely free — verify current per-unit rates before estimating a workload's cost |
| Persistence | Filesystem state (files, installed packages, build artifacts) can survive session stop/resume cycles without an external store — useful for iterative agent loops that would otherwise re-provision from scratch each run |
| Framework | Any — LangGraph, CrewAI, LlamaIndex, OpenAI Agents SDK, Strands, custom. Bring your own code or container. Protocol support includes MCP and Agent-to-Agent (A2A) |

**Why microVM + 8h matters:** classical Lambda can't host an agent loop that thinks for 30 minutes. Fargate can, but you pre-allocate resources. AgentCore Runtime gives you session isolation, long duration, persistent session state options, and consumption-based active-resource billing.

---

## Memory: managed conversation + facts

AgentCore Memory eliminates the "where do we put the conversation history" problem. It handles:

- **Raw conversation storage** per session and per user
- **Automatic fact extraction** from conversations (background process)
- **Semantic retrieval** of relevant prior context
- **Lifecycle management** — TTL, eviction, archival

It's a managed memory provider for the patterns described in [`ai-context-layer/references/managed-memory-boundaries.md`](../../ai-context-layer/references/managed-memory-boundaries.md) (P13). Treat it as the AWS-native option in that category. Cross-references the patterns there; the boundaries discipline still applies (managed memory is *per-user state*, not corpus retrieval).

Trade-off: lock-in. You own the data but the retrieval shape and fact-extraction prompts are AWS's. If you need exact control, build memory yourself (DynamoDB + embeddings).

---

## Gateway: API/Lambda → MCP tools

Gateway turns OpenAPI specs, Lambda functions, and third-party MCP servers into MCP-compatible tools that any AgentCore-hosted agent can call.

Two concrete consequences:

1. **Existing AWS estates become agent-callable.** A team with existing Lambda functions or OpenAPI-described services can expose them via AgentCore Gateway in a config layer, no rewrite.
2. **Portability.** Tools exposed via Gateway speak MCP. They are callable by Claude (Anthropic MCP), GPT (OpenAI MCP support), Copilot, and other MCP clients — not just Bedrock agents. AWS becomes a tool provider for the whole agent ecosystem.

This is the closest thing 2026 has to "MCP-as-a-service for AWS-shaped enterprises." See `agents-mcp` for the protocol; see [`agents-mcp/SKILL.md`](../../agents-mcp/SKILL.md) for how to consume it from non-AWS agents.

---

## Identity, Code Interpreter, Browser

These are smaller services but worth knowing exist:

- **Identity** — handles per-agent IAM, OAuth-style delegated access to AWS resources, and works with workforce/customer identity providers. Use when an agent needs to act on behalf of a user without you building auth plumbing.
- **Code Interpreter** — sandboxed code execution per session. Equivalent to Anthropic code execution or E2B but inside the AgentCore boundary. Use for analysis, plotting, data transforms inside agent flows.
- **Browser** — managed headless browser per session. Use when the agent's job involves web automation, screenshot capture, or content extraction from sites that don't expose APIs.

---

## Observability, Evaluations, Policy

- **Observability** — agent-shaped traces (turns, tool calls, model calls), metrics, replay. CloudWatch-integrated. Equivalent capability to Langfuse / Phoenix / Helicone but native to the AWS estate.
- **Evaluations** — 13 built-in quality evaluators: faithfulness, answer-relevancy, context-precision, toxicity, refusal correctness, and more. Pluggable for custom evaluators. Use for regression gates in CI/CD.
- **Policy** — natural-language or Cedar policies enforced on tool calls through Gateway. Use for deterministic allow/deny boundaries, not as a replacement for prompt-level safety.
- **Registry** — governed catalog for agents, MCP servers, tools, skills, and custom resources. Use it when many teams need discovery, approval, and reuse across AWS, on-prem, and other clouds.

Eval + Policy together are the AWS answer to "how do we ship an agent that won't embarrass us." Pair with [`ai-coding-agents-observability-evals`](../../ai-coding-agents-observability-evals/SKILL.md) for the cross-platform patterns.

---

## Framework choice

AgentCore Runtime is framework-agnostic. Common pairings:

| Framework | When to pick |
|---|---|
| **Strands Agents** | AWS-native, deep AgentCore integration, smallest plumbing |
| **LangGraph** | Cross-cloud portability, mature ecosystem, complex flows |
| **CrewAI** | Multi-agent role-based workflows |
| **LlamaIndex** | Retrieval-heavy agents, deep RAG integration |
| **OpenAI Agents SDK** | OpenAI-native agent semantics, portable models/tools where AWS hosting is required |
| **Custom Python** | Full control, no framework opinions |

If you have no preference, **Strands** is the lowest-friction AWS-native path. If you may leave AWS, **LangGraph** keeps options open.

---

## Multi-tenant pattern

For SaaS shapes with many customer-tenants:

```text
Session creation
  ├── tenant_id from JWT / IAM context
  ├── Memory scope: per (tenant_id, user_id)
  ├── Gateway scope: tools filtered by tenant entitlement
  ├── Identity: tenant-scoped IAM role assumption
  └── Observability: traces tagged with tenant_id

Per-tenant policies enforced at the Policy layer.
Per-tenant rate limits at API Gateway in front of Runtime.
```

AWS's reference implementation pattern uses session metadata for tenant scoping. See AWS blog "Building multi-tenant agents with AgentCore" for the canonical walkthrough.

---

## When to pick AgentCore vs Lambda vs Fargate

| Need | Pick |
|---|---|
| Agent loop with multi-step reasoning, ~30 min – 8 h sessions | **AgentCore Runtime** |
| Quick agent-as-an-API, < 15 min per call, stateless | **Lambda** (lower complexity if you don't need AgentCore services) |
| Long-running training, batch inference, custom OS deps, > 8 h | **Fargate** or **ECS** or **SageMaker** |
| Need managed Memory + Gateway + Identity together | **AgentCore** — replacing them with DIY is the bulk of platform work |
| Burst from 0 → many concurrent isolated agent sessions | **AgentCore** if session isolation and managed agent services matter; benchmark cold start and quota limits before committing |
| Strict cost control, low volume, you have ops bandwidth | **Lambda + DynamoDB** — cheapest if you can build the missing pieces |

Cost rule of thumb: compare active CPU/memory time, storage, Gateway calls, Memory operations, CloudWatch telemetry, and model inference separately. Do not treat AgentCore as "Lambda pricing with longer duration"; its billing units and bundled capabilities differ.

---

## Anti-patterns

- **A-AC-1 — Pick Bedrock Agents (classic) for a new build because it's "the AWS-managed one."** It's the legacy product. New work should be on AgentCore unless there's a specific reason. Verify before committing.
- **A-AC-2 — Use AgentCore Runtime as a Lambda replacement for stateless API calls.** You pay for the session even if the call is short. Use Lambda for short stateless work, AgentCore for sessions.
- **A-AC-3 — Adopt every AgentCore capability on day one.** Start with Runtime + Memory + Gateway. Add Identity, Browser, Code Interpreter, Observability, Evaluations, Policy, and Registry as the workload demands them.
- **A-AC-4 — Lock framework choice without considering portability.** Strands ties you tightest to AWS. LangGraph keeps multi-cloud options open. Choose deliberately.
- **A-AC-5 — Treat AgentCore Memory as a corpus retrieval system.** It's per-user state. Corpus retrieval is Bedrock Knowledge Bases or self-hosted RAG. Two different patterns; don't conflate.
- **A-AC-6 — Skip Evaluations and Policy because the agent "works in demos."** Demos don't include the regression case where a fine-tuned model update changes refusal behavior. Eval + Policy are the gate, not a nice-to-have.
- **A-AC-7 — Use Gateway as a generic API gateway.** Gateway is specifically for MCP-shaped tool exposure to agents. For non-agent traffic, use Amazon API Gateway.
- **A-AC-8 — Ignore data-use and telemetry boundaries.** Verify content-use terms, CloudWatch log retention, PII masking, and tenant tags before enabling Observability, Evaluations, Memory, or Browser in regulated environments.

---

## Related

- [aws-bedrock-knowledge-bases.md](../../ai-rag/references/aws-bedrock-knowledge-bases.md) — Managed RAG on AWS (composes with AgentCore for the retrieve layer)
- [s3-vectors-backend.md](../../ai-vector-brain/references/s3-vectors-backend.md) — Cheap vector backend for Bedrock KB
- [`agent-hosting-matrix.md`](agent-hosting-matrix.md) — Cross-cloud agent hosting decision
- [`platform-comparison.md`](platform-comparison.md) — Broader PaaS comparison
- [`ai-context-layer/references/managed-memory-boundaries.md`](../../ai-context-layer/references/managed-memory-boundaries.md) — P13 managed-memory boundary discipline (AgentCore Memory is one provider)
- [`agents-mcp/SKILL.md`](../../agents-mcp/SKILL.md) — MCP protocol consumed by Gateway
- [`ai-coding-agents-observability-evals/SKILL.md`](../../ai-coding-agents-observability-evals/SKILL.md) — Cross-platform observability + eval patterns
- AWS docs: [AgentCore overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), [Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html), [pricing](https://aws.amazon.com/bedrock/agentcore/pricing/), [multi-tenant pattern](https://aws.amazon.com/blogs/machine-learning/building-multi-tenant-agents-with-amazon-bedrock-agentcore/)
