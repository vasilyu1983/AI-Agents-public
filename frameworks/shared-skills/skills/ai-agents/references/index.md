# AI Agents Reference Index

Use this file as the on-demand map for the `ai-agents` skill. Start with the shortest path that matches the user’s question instead of loading every reference.

## Table Of Contents

- [Fast Paths](#fast-paths)
- [Decision And Economics](#decision-and-economics)
- [Core Architecture](#core-architecture)
- [Graph And Loop Composition](#graph-and-loop-composition)
- [Protocols And Contracts](#protocols-and-contracts)
- [Capability Patterns](#capability-patterns)
- [Engine Layers](#engine-layers)
- [Operations, Safety, And Quality](#operations-safety-and-quality)
- [Templates And Assets](#templates-and-assets)
- [External Verification](#external-verification)

## Fast Paths

- New agent idea:
  [`build-vs-not-decision.md`](build-vs-not-decision.md) ->
  [`protocol-decision-tree.md`](protocol-decision-tree.md) ->
  [`modern-best-practices.md`](modern-best-practices.md) ->
  [`../assets/core/agent-template-standard.md`](../assets/core/agent-template-standard.md)

- Tool-heavy agent:
  [`protocol-decision-tree.md`](protocol-decision-tree.md) ->
  [`mcp-practical-guide.md`](mcp-practical-guide.md) ->
  [`tool-design-specs.md`](tool-design-specs.md) ->
  [`agents-mcp`](../../agents-mcp/SKILL.md)

- Multi-agent system:
  [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) ->
  [`multi-agent-patterns.md`](multi-agent-patterns.md) ->
  [`context-rotation-and-state.md`](context-rotation-and-state.md) ->
  [`agent-operations-best-practices.md`](agent-operations-best-practices.md) ->
  `agents-subagents`

- Knowledge-heavy agent:
  [`rag-patterns.md`](rag-patterns.md) ->
  [`../assets/knowledge-base/kb-architecture.md`](../assets/knowledge-base/kb-architecture.md) ->
  [`memory-systems.md`](memory-systems.md) ->
  [`ai-rag`](../../ai-rag/SKILL.md)

- Rollout and debugging:
  [`evaluation-and-observability.md`](evaluation-and-observability.md) ->
  [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) ->
  [`agent-debugging-patterns.md`](agent-debugging-patterns.md)

- Cost tracking:
  [`agent-economics.md`](agent-economics.md) ->
  [`coding-agent-usage-tracking.md`](coding-agent-usage-tracking.md)

- Framework selection (July 2026):
  [`build-vs-not-decision.md`](build-vs-not-decision.md) ->
  [`framework-landscape.md`](framework-landscape.md) ->
  [`../../ai-bot-builder/references/framework-selection.md`](../../ai-bot-builder/references/framework-selection.md) (for Python/TS bot depth)

- "Graph engineering", "loop engineering", agent workflow graph, improvement loop, or knowledge graph:
  [`graph-and-loop-engineering.md`](graph-and-loop-engineering.md) ->
  choose the graph purpose ->
  the linked specialist skill

## Decision And Economics

- [`build-vs-not-decision.md`](build-vs-not-decision.md) - default "do not build an agent" gate, alternatives, kill triggers
- [`agent-economics.md`](agent-economics.md) - cost, ROI, hallucination impact, payback logic
- [`coding-agent-usage-tracking.md`](coding-agent-usage-tracking.md) - CLI usage tracking for Claude Code and Codex with ccusage tools
- [`agent-maturity-governance.md`](agent-maturity-governance.md) - maturity model, policy, fleet governance

## Core Architecture

- [`modern-best-practices.md`](modern-best-practices.md) - current operating defaults and framework selection guidance (re-verify dates in-file)
- [`framework-landscape.md`](framework-landscape.md) - polyglot framework selection (dated in-file): LangGraph, CrewAI, Pydantic AI, Claude/OpenAI SDKs, Mastra, Spring AI, Microsoft Agent Framework, Semantic Kernel; selection matrix, anti-patterns, migration paths
- [`agent-delivery-methods.md`](agent-delivery-methods.md) - GSD, BMAD, Spec Kit, OpenSpec, MADD, and AI-SDLC as delivery methods
- [`operational-patterns.md`](operational-patterns.md) - agent loop, tool spec, memory, eval, deployment patterns
- [`agent-operations-best-practices.md`](agent-operations-best-practices.md) - execution, verification, action gating
- [`context-engineering.md`](context-engineering.md) - progressive disclosure, retrieval timing, context hygiene
- [`context-rotation-and-state.md`](context-rotation-and-state.md) - fresh-context workers, durable state, and session vs project boundaries
- [`memory-systems.md`](memory-systems.md) - session, episodic, long-term, task memory tradeoffs

## Graph And Loop Composition

- [`graph-and-loop-engineering.md`](graph-and-loop-engineering.md) - disambiguates agent/workflow graphs, networked improvement graphs, and knowledge/context graphs; routes graph and loop requests to the relevant specialist skill

## Protocols And Contracts

- [`protocol-decision-tree.md`](protocol-decision-tree.md) - MCP vs A2A selection
- [`mcp-practical-guide.md`](mcp-practical-guide.md) - MCP integration patterns
- [`mcp-server-builder.md`](mcp-server-builder.md) - MCP server build checklist
- [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) - handoff contracts and coordination patterns
- [`api-contracts-for-agents.md`](api-contracts-for-agents.md) - request/response envelopes, safety and error taxonomy
- [`tool-design-specs.md`](tool-design-specs.md) - tool schemas, validation, side-effect controls

## Capability Patterns

- [`multi-agent-patterns.md`](multi-agent-patterns.md) - manager-worker, sequential, handoff, group chat
- [`rag-patterns.md`](rag-patterns.md) - agentic RAG and hybrid retrieval patterns
- [`os-agent-capabilities.md`](os-agent-capabilities.md) - UI grounding and OS control patterns
- [`code-swe-agents.md`](code-swe-agents.md) - coding-agent operating patterns
- [`voice-multimodal-agents.md`](voice-multimodal-agents.md) - multimodal and voice-first systems
- [`skill-lifecycle.md`](skill-lifecycle.md) - package and share reusable agent skills

## Engine Layers

- [`ai-engine-layers.md`](ai-engine-layers.md) - five-layer system view
- [`context-graph-patterns.md`](context-graph-patterns.md) - graph-based context and memory
- [`inbox-engine-patterns.md`](inbox-engine-patterns.md) - event intake, prioritization, dead-letter handling

## Operations, Safety, And Quality

- [`evaluation-and-observability.md`](evaluation-and-observability.md) - eval design, telemetry, monitoring
- [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) - rollout, HITL, rollback, control gates
- [`guardrails-implementation.md`](guardrails-implementation.md) - layered guardrails and enforcement patterns
- [`escalation-patterns.md`](escalation-patterns.md) - 3-level escalation hierarchy, failure classification, escalation budgets, and hook integration
- [`agent-debugging-patterns.md`](agent-debugging-patterns.md) - trace-based debugging for loops, tools, and state corruption
- [`autonomous-loop-patterns.md`](autonomous-loop-patterns.md) - Shape C autonomous loops: Ralph-Loop class, PRD spec, three driver implementations (Python, Temporal, LangGraph), budgets, drift, circuit breakers
- [`24-7-operating-model.md`](24-7-operating-model.md) - production operating model for agents: SLOs per shape, on-call structure, alert catalog, runbook contract, post-mortem template, operating cadence

## Templates And Assets

- [`../assets/core/agent-template-standard.md`](../assets/core/agent-template-standard.md) - full production spec
- [`../assets/core/agent-template-quick.md`](../assets/core/agent-template-quick.md) - MVP spec
- [`../assets/core/agent-template-specialized.md`](../assets/core/agent-template-specialized.md) - domain-specific spec
- [`../assets/agent-template-ainative-sdlc.md`](../assets/agent-template-ainative-sdlc.md) - delegate-review-own runbook
- [`../assets/checklists/agent-safety-checklist.md`](../assets/checklists/agent-safety-checklist.md) - launch gate
- [`../assets/tools/tool-definition.md`](../assets/tools/tool-definition.md) - tool contract template
- [`../assets/tools/tool-validation-checklist.md`](../assets/tools/tool-validation-checklist.md) - tool readiness checklist
- [`../assets/multi-agent/manager-worker-template.md`](../assets/multi-agent/manager-worker-template.md) - manager-worker starter
- [`../assets/multi-agent/evaluator-router-template.md`](../assets/multi-agent/evaluator-router-template.md) - evaluator-router starter
- [`../assets/rag/rag-basic.md`](../assets/rag/rag-basic.md) - basic RAG template
- [`../assets/rag/rag-advanced.md`](../assets/rag/rag-advanced.md) - advanced RAG template
- [`../assets/rag/hybrid-retrieval.md`](../assets/rag/hybrid-retrieval.md) - hybrid retrieval template
- [`../assets/knowledge-base/kb-architecture.md`](../assets/knowledge-base/kb-architecture.md) - knowledge-base architecture

## External Verification

- [`../data/sources.json`](../data/sources.json) - curated primary sources for fact-checking (see per-entry verification dates)
