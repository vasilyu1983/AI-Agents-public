# AI Bot Builder — Reference Index

Use this index to navigate to the right reference for your task.

## Bot Architecture

| Reference | Use when |
|-----------|----------|
| [framework-selection.md](framework-selection.md) | Choosing between Pipecat, LiveKit Agents, LangGraph, Claude Agent SDK, Pydantic AI, and Mastra (TypeScript) |
| [conversation-design.md](conversation-design.md) | Designing state machines, fallback trees, slot filling, multi-turn flows |
| [persona-design.md](persona-design.md) | Defining bot personality, tone, brand voice, safety boundaries |

## Bot Domains

| Reference | Use when |
|-----------|----------|
| [support-bot-patterns.md](support-bot-patterns.md) | Integrating with Zendesk/Intercom/Freshdesk, KB grounding, resolution tracking |
| [sales-bot-patterns.md](sales-bot-patterns.md) | CRM integration (HubSpot/Salesforce), lead qualification, demo booking |

## Bot Operations

| Reference | Use when |
|-----------|----------|
| [handoff-to-human.md](handoff-to-human.md) | Escalation triggers, warm handoff, queue routing, context transfer |
| [channel-routing.md](channel-routing.md) | Web chat, WhatsApp, SMS, email, in-app, omnichannel continuity |
| [bot-memory-integration.md](bot-memory-integration.md) | Wiring persistent memory (P2/P4/P6), remember/recall loop, anti-pattern blocks |
| [bot-analytics-improvement.md](bot-analytics-improvement.md) | Funnel metrics, CSAT, containment rate, A/B testing, improvement loops |
| [production-deployment.md](production-deployment.md) | Serving, scaling, canary, cost per conversation, abuse prevention |
| [stateful-rollout-and-blue-green.md](stateful-rollout-and-blue-green.md) | Rolling out new bot versions without dropping in-flight sessions: cohort canary, checkpoint migration, drain, rollback |
| [secret-rotation-and-model-fallback.md](secret-rotation-and-model-fallback.md) | Rotating provider keys without restart, multi-provider fallback chains, circuit breakers, model deprecation handling |

## Bot Safety and Migration

| Reference | Use when |
|-----------|----------|
| [injection-and-jailbreak-defense.md](injection-and-jailbreak-defense.md) | Prompt injection defense — direct, indirect, tool-output poisoning, red-team pack |
| [migration-from-n8n.md](migration-from-n8n.md) | Porting a bot from n8n, Langflow, or Agent Builder to native Python |

## LangGraph Implementation (absorbed from ai-langgraph-bots)

| Reference | Use when |
|-----------|----------|
| [graph-design-patterns.md](graph-design-patterns.md) | Designing graph state, nodes, edges, routers, subgraphs |
| [state-checkpoints-and-hitl.md](state-checkpoints-and-hitl.md) | Adding persistence, replay, approval gates, recovery |
| [testing-and-production.md](testing-and-production.md) | Testing graph transitions, observability, handoff to runtime skills |

## Cross-Skill Navigation

| Need | Skill |
|------|-------|
| Voice pipeline (STT/TTS, telephony) | [`../ai-voice-bots/SKILL.md`](../../ai-voice-bots/SKILL.md) |
| Agent architecture decisions | [`../ai-agents/SKILL.md`](../../ai-agents/SKILL.md) |
| RAG and retrieval for KB bots | [`../ai-rag/SKILL.md`](../../ai-rag/SKILL.md) |
| Prompt engineering for bot responses | [`../ai-prompt-engineering/SKILL.md`](../../ai-prompt-engineering/SKILL.md) |
| MCP tool integration | [`../agents-mcp/SKILL.md`](../../agents-mcp/SKILL.md) |
| Chat UI and streaming UX | [`../software-ai-integration/SKILL.md`](../../software-ai-integration/SKILL.md) |
| Eval harnesses and red-team packs | [`../qa-agent-testing/SKILL.md`](../../qa-agent-testing/SKILL.md) |
