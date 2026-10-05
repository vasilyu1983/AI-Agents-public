---
description: AI Knowledge Bot Builder — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## AI Knowledge Bot Builder

**Typical scenario**

You need to build a conversational bot (support, sales, or knowledge) that persists user context across sessions, grounds answers in a knowledge base, and handles contradictions and stale facts instead of hallucinating.

**When this is the right team:** the task is building or redesigning a bot with persistent memory and knowledge-base integration. If the question is pure architecture or eval design without building, use `ai-systems` instead. If the question is one-off retrieval tuning, use `ai-retrieval-architect` as a single specialist.

**Claude prompt**

```text
Create an agent team using the installed `ai-knowledge-bot-builder` members.

Scenario: Build a customer support bot for a B2B SaaS product that remembers customer preferences across sessions, grounds answers in the help center, tracks how customer configurations change over time, and escalates to human agents with full context.

Required context:
- Bot type: support bot
- Integrations: Zendesk ticketing, internal KB (Notion), customer account API
- Regulatory: no special compliance, but PII must be scrubbed before storage
- Target: web chat + Slack

Instructions:
- Stage 1: ai-agent-architect decides the agent topology and build-vs-not gate
- Stage 2: ai-context-architect selects memory patterns (P2/P4/P6) and runs the anti-pattern sweep; ai-retrieval-architect designs KB grounding with evidence and citation strategy
- Stage 3: ai-bot-builder-lead wires the remember/recall loop, implements the conversation flow in LangGraph, adds guardrails and compliance filter, builds eval suite
- Debate on: memory pattern choice (P2 vs P4 vs P6), framework selection, whether to add knowledge compilation (P7)
- Synthesize one bot specification with implementation code, memory wiring, and eval plan
- Clean up the team when done
```

**Codex prompt**

```text
Spawn agent_architect, context_architect, retrieval_architect, and bot_builder_lead.

Task: build a customer support bot with persistent memory and KB grounding.

Context:
- bot type: support
- integrations: Zendesk, Notion KB, account API
- channels: web chat + Slack
- PII scrubbing required

Stage 1 (agent_architect): agent topology and tool boundaries
Stage 2 (context_architect + retrieval_architect): memory patterns, retrieval design, anti-pattern sweep
Stage 3 (bot_builder_lead): conversation flow, remember/recall wiring, guardrails, eval plan

Return:
- bot specification with pattern IDs (P-IDs) and anti-patterns blocked (A-IDs)
- implementation code (LangGraph or Claude SDK)
- memory wiring and vendor recommendation
- eval plan with multi-turn test cases
```

**Debate-first variant**

Use when the key disagreement is "structured memory (P2) vs temporal knowledge graph (P4)" — the support bot might need temporal tracking for evolving customer configs, or simple structured memory might be enough. Also use debate when the question is "pure RAG (P8) vs knowledge compilation (P7)" — if recurring queries dominate, P7 saves cost and latency.
