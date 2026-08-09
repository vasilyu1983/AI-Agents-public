# A2A + MCP Integration Patterns

Five integration patterns for combining Agent-to-Agent (A2A) and Model Context Protocol (MCP) in multi-agent systems. A2A handles agent-to-agent communication; MCP handles agent-to-tool communication.

Source: Google Cloud Tech (@addyosmani, @Saboo_Shubham_), 2026-04-24 — <https://x.com/GoogleCloudTech/status/2047567704807346675>

Cross-link: [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md).

## Table of Contents

- [Pattern 1: Agent Card Discovery](#pattern-1-agent-card-discovery)
- [Pattern 2: Delegated Specialization](#pattern-2-delegated-specialization)
- [Pattern 3: Tool Bridge (MCP)](#pattern-3-tool-bridge-mcp)
- [Pattern 4: Cross-Organization Federation](#pattern-4-cross-organization-federation)
- [Pattern 5: Ambient Event Mesh](#pattern-5-ambient-event-mesh)
- [Stack Surfaces](#stack-surfaces)

## Pattern 1: Agent Card Discovery

- Each A2A-compatible agent publishes a JSON **Agent Card** at a well-known URL describing capabilities, auth requirements, and rate limits — like an OpenAPI spec for agent-to-agent.
- ADK auto-generates the Agent Card from the agent definition; consuming a remote agent uses the `RemoteA2aAgent` component (handles auth, serialization, error handling, result streaming).
- An **Agent Registry** lets agents discover each other across an organization without hardcoded URLs — the service mesh for the agent ecosystem.

## Pattern 2: Delegated Specialization

Coordinator-Dispatcher across team and framework boundaries. Specialist does **not** need the same framework, language, or owner — only A2A.

Example workflow (customer onboarding) crossing 5 teams / 4 languages:

| Role | Owner | Language |
|---|---|---|
| Coordinator | your team | Python |
| Identity verification | security team | Go |
| Credit assessment | risk team | Java |
| Account provisioning | platform team | Go |
| Compliance docs | legal team | Python |
| Welcome comms | marketing team | TypeScript |

Coordinator only knows each specialist's Agent Card and the A2A protocol — internal updates ship without coordinator changes.

## Pattern 3: Tool Bridge (MCP)

Single protocol replaces N custom connectors:

- ADK ships **60+ ready-to-use MCP integrations** (GitHub, Notion, Hugging Face, AgentOps, Stripe, …).
- **MCP Toolbox for Databases** connects 30+ data sources through one MCP interface.
- **Apigee API Hub** turns existing REST APIs documented in Apigee into agent-accessible tools — same governance layer (rate limit, auth, logging, ACL) that already manages API traffic.
- From the agent's perspective, an MCP tool through Stripe and an MCP tool through BigQuery look identical — the protocol is the interface, the backend is interchangeable.

## Pattern 4: Cross-Organization Federation

Each org maintains its own governance while collaborating on shared tasks via A2A:

- **Agent Gallery** in Gemini Enterprise: 100+ partner agents (Adobe, ServiceNow, Workday, Salesforce, …) validated by Google Cloud for security and interoperability.
- Your **Agent Gateway** policies control what data your agents share with external agents and what actions they can take on returned data.
- The partner agent runs under its own security model; both sides enforce boundaries independently.

Surface area saved: your agent never has to model Salesforce data internals or ServiceNow architecture — the partner agent does.

## Pattern 5: Ambient Event Mesh

A2A combined with event-driven architecture for continuous-background agents:

- **Batch and Event-Driven Agents** in Gemini Enterprise Agent Platform connect to BigQuery tables and Pub/Sub streams.
- Receiving agent decides per-event: handle locally, delegate to specialist via A2A, or escalate to human via Mission Control.
- Self-organizing — adding a fraud-detection specialist requires only registering it in Agent Registry and updating routing logic in the relevant ambient agents.
- Governance: every agent has identity via Agent Identity, every tool access governed by Agent Gateway, every interaction traced via Agent Observability — the mesh is fully observable.

## Stack Surfaces

- **A2A protocol**: ADK across Python, TypeScript, Go, Java.
- **MCP**: native ADK support; managed support for GCP databases.
- **Agent Gallery**: 100+ validated partner agents in Gemini Enterprise.
- **Codelab**: <https://codelabs.developers.google.com/instavibe-adk-multi-agents>
- **Samples**: <https://github.com/google/adk-samples>
- **Platform**: <https://cloud.google.com/products/gemini-enterprise-agent-platform> · <https://adk.dev>
