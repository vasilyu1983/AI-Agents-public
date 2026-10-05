---
name: ai-agents
description: AI agent architecture, graph and loop composition, protocol choice, evaluation, and observability. Use when scoping or reviewing systems before implementation.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-27
---

# AI Agents Development — Architecture Hub

Use this skill to decide whether a workflow should be an agent, which agent shape fits, which protocol boundary to use, and what production controls must exist before rollout.

Default posture: explicit control flow, bounded tools, typed contracts, auditable state, human approval for high-risk actions, and telemetry from day one.

Keep this file lean. Load detail from [references/index.md](references/index.md), `assets/`, and sibling skills only when needed.

## When to Use This Skill

Use this skill when the user asks for:

- agent architecture or operating-model decisions
- build-vs-not-agent assessment
- MCP vs A2A protocol choice
- production readiness review for an existing agent system
- evaluation, observability, rollout, or safety planning
- framework selection after requirements are already clear
- a starting template for a new agent spec
- graph engineering, agent/workflow graphs, state-machine orchestration, cyclic graphs, or DAG-versus-loop design
- loop engineering, run-until-done coding agents, self-improving workflows, evaluator feedback loops, or bounded autonomous iteration
- uncertainty over whether a "graph" means execution control flow, an improvement network, or a knowledge/context graph

## Use Other Skills for Depth

- Prompt contracts and structured outputs → [`../ai-prompt-engineering/SKILL.md`](../ai-prompt-engineering/SKILL.md)
- Retrieval, chunking, reranking, search quality → [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md)
- Vector-brain implementation, schemas, ingest scripts, manifests, and retrieval tool contracts → [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md)
- Bot building (support, sales, conversation design, LangGraph) → [`../ai-bot-builder/SKILL.md`](../ai-bot-builder/SKILL.md)
- Voice bots (STT/TTS pipeline, telephony, latency) → [`../ai-voice-bots/SKILL.md`](../ai-voice-bots/SKILL.md)
- MCP server setup, transports, server builds → [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md)
- Subagents, delegation contracts, least-privilege tools → [`../agents-subagents/SKILL.md`](../agents-subagents/SKILL.md)
- CLI-based tools (non-interactive, idempotent, agent-friendly patterns) → [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md)
- Evaluation harnesses, attack suites, regression gates → [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md)
- Deployment guardrails and model operations → [`../ai-mlops/SKILL.md`](../ai-mlops/SKILL.md)
- Application security and high-risk controls → [`../software-security-appsec/SKILL.md`](../software-security-appsec/SKILL.md)
- Model and inference cost tuning → [`../ops-cost-optimization/references/ai-api-cost-guide.md`](../ops-cost-optimization/references/ai-api-cost-guide.md), [`../ai-llm-inference/SKILL.md`](../ai-llm-inference/SKILL.md)
- Knowledge/context graphs, retrieval architecture, and graph-backed memory → [`../ai-context-layer/SKILL.md`](../ai-context-layer/SKILL.md), [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md), [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md)

## Default Workflow

1. Run the build-vs-not decision gate: if a simpler workflow, form, or tool fits, do not build an agent; proceed only when autonomy is justified.
2. Define the task environment: performance measure, environment, percepts/sensors, actions/tools, observability, determinism, time horizon, and single-agent vs multi-agent interaction.
3. Choose control flow; default to workflow/FSM/DAG for production.
4. Choose protocol boundaries: MCP for tools/data, A2A for agent handoffs.
5. Define contracts: tool schemas, handoff payloads (with a delegation depth cap: [references/multi-agent-patterns.md](references/multi-agent-patterns.md#handoff-payload-standard)), state model, success criteria.
6. Add evaluation and telemetry before shipping.
7. Add human approval, rollback, and kill-switches for irreversible actions.
8. Start from templates, then route to specialized skills for implementation depth.

## Topology Promotion Gate

Start with one bounded workflow or agent and keep it as the control. Promote to multiple agents only when the work has independently executable branches, materially different tool permissions, or a verifier that must be isolated from the producer. Before promotion, record the single-agent failure, the proposed handoff contract, and the extra latency and cost budget. Accept the topology only if the same task set improves the target outcome without increasing unresolved handoff failures; otherwise keep the simpler control.

Measure the cost before promoting: run the same task set both ways and record the token and latency multiplier next to the outcome delta. Promote only if the outcome gain is worth that multiplier at your prices; take prices from the current provider pricing page (see [`../ops-cost-optimization/references/ai-api-cost-guide.md`](../ops-cost-optimization/references/ai-api-cost-guide.md)), never from memory.

## Known Traps

- treating "agent" as the default interaction pattern when a workflow, form, or plain tool call would be simpler
- using MCP as the overall agent architecture instead of the tool and resource integration layer
- adding long-term memory without provenance (A13), retention policy, correction flow (A11 — forget path), and user-value proof. Use [`ai-context-layer/patterns-catalog.md`](../ai-context-layer/references/patterns-catalog.md) to pick a named pattern and [`ai-context-layer/anti-patterns-catalog.md`](../ai-context-layer/references/anti-patterns-catalog.md) for the sweep
- letting planner loops recurse without explicit step, budget, and escalation limits. A step cap misses oscillation and fabricated observations; diagnose loop failures with [references/agent-debugging-patterns.md](references/agent-debugging-patterns.md#quick-reference-failure-modes-and-fixes)
- shipping autonomous actions before evaluator coverage, rollback controls, and human approval paths exist
- defaulting to a multi-agent topology for reasoning-heavy work when a single strong agent at an equal token budget may match or beat it. Confirm the task is genuinely parallelizable or tool/role-diverse before fanning out; evidence and scope limits live in [`../agents-subagents/SKILL.md` § When a Single Strong Agent Beats a Team](../agents-subagents/SKILL.md#when-a-single-strong-agent-beats-a-team)

## Common Anti-Patterns

- chat-first agent design with no state model, contract, or action boundary
- multi-agent topologies introduced before single-agent failure modes are understood
- tool surfaces defined by convenience rather than least privilege
- evaluation added after launch as observability theater instead of a release gate
- provider or framework selection driven by hype, benchmark screenshots, or marketing taxonomy alone

## Quick Reference

| Question | Default |
| --- | --- |
| Should this be an agent? | Start with [references/build-vs-not-decision.md](references/build-vs-not-decision.md); default answer is "no" until volume, ambiguity, and value justify autonomy. |
| What is the task environment? | State the performance measure, environment, percepts/sensors, actions/tools, observability, determinism, horizon, and other agents before choosing a framework. |
| Which control flow fits? | Prefer workflow/FSM/DAG; use planner/executor only when branching cannot be modeled explicitly. |
| MCP or A2A? | MCP for external tools/data, A2A for agent-to-agent coordination, both when a multi-agent system also needs tools. |
| When to use multi-agent? | Only when roles, handoff contracts, and verifier responsibilities are explicit. |
| When to add long-term memory? | Only with provenance, retention rules, user consent, and clear value. Pick a named pattern from [`ai-context-layer/patterns-catalog.md`](../ai-context-layer/references/patterns-catalog.md) (P2 for app-orchestrated, P3 for self-editing, P4 for temporal, P6 for conversational). Run the anti-pattern sweep — A1 (no raw transcripts), A11 (forget path required), A13 (provenance mandatory). |
| What must exist before rollout? | Eval suite, telemetry, action limits, human escalation, rollback path, and kill switch. |
| Is this "graph engineering" or "loop engineering"? | Start with [references/graph-and-loop-engineering.md](references/graph-and-loop-engineering.md); identify the graph's purpose before selecting a runtime or datastore. |

## Autonomy Shapes — How to Host an Agent 24/7

Three deployment shapes for running agents continuously. Pick by the **trigger model**, not by the framework.

| Shape | Trigger | When to use | Primary guide |
|---|---|---|---|
| **A — Triggered / hosted run** | Webhook, queue, schedule, `/fire` | Per-event agent work, scheduled jobs, fan-out from external sources | [`../ai-coding-agents-state/references/webhook-and-queue-triggers.md`](../ai-coding-agents-state/references/webhook-and-queue-triggers.md) + [`../ai-coding-agents-state/references/durable-trigger-integration.md`](../ai-coding-agents-state/references/durable-trigger-integration.md) |
| **B — Always-on bot / voice server** | Sessions, WebSocket, SIP call | Support / sales / voice bots with conversational state | [`../ai-bot-builder/references/production-deployment.md`](../ai-bot-builder/references/production-deployment.md) + [`../ai-bot-builder/references/stateful-rollout-and-blue-green.md`](../ai-bot-builder/references/stateful-rollout-and-blue-green.md) + [`../ai-voice-bots/references/production-deployment.md`](../ai-voice-bots/references/production-deployment.md) |
| **C — Autonomous loop** | PRD + loop driver until acceptance met | Long-horizon work: refactors, migrations, research, Ralph-Loop class | [references/autonomous-loop-patterns.md](references/autonomous-loop-patterns.md) |

Hosted or self-hosted loop: self-host when you need a custom sandbox or egress policy, tools on a private network, data residency, or deterministic replay; otherwise prefer a vendor-hosted agent runtime. Before committing, check the vendor docs for session persistence, idle billing, and sandbox limits.

Cross-shape requirements:

- **Budget and kill-switch enforcement**: [`../agents-hooks/references/budget-and-loop-hooks.md`](../agents-hooks/references/budget-and-loop-hooks.md)
- **24/7 operating model (SLOs, on-call, runbooks)**: [references/24-7-operating-model.md](references/24-7-operating-model.md)
- **Provider failover and secret rotation**: [`../ai-bot-builder/references/secret-rotation-and-model-fallback.md`](../ai-bot-builder/references/secret-rotation-and-model-fallback.md)
- **Where to host (Vercel / Fly.io / Railway / Cloudflare / Render)**: [`../software-paas-hosting/SKILL.md`](../software-paas-hosting/SKILL.md) and [`../software-paas-hosting/references/agent-hosting-matrix.md`](../software-paas-hosting/references/agent-hosting-matrix.md)

## Architecture Selection

| Need | Default Agent Shape | Notes |
| --- | --- | --- |
| Deterministic business process | Workflow agent | Best default for auditable production behavior. |
| Bounded external actions | Tool-using agent | Keep tools narrow, typed, and permission-scoped. |
| Knowledge-grounded answers | RAG agent | Require citations, ACL-aware retrieval, and refusal on missing evidence. |
| Long multi-step work with branching | Planner/executor | Use strict step budgets, checkpoints, and replanning limits. |
| Specialized roles with explicit ownership | Multi-agent orchestrator | Handoffs are APIs; add verifier/evaluator roles early. Score the design against the MAST failure taxonomy (Cemri et al., 2025, arXiv:2503.13657) — do not re-derive it: [`../agents-subagents/references/mast-failure-taxonomy.md`](../agents-subagents/references/mast-failure-taxonomy.md). |
| Desktop or browser control | OS agent | Require sandboxing, UI verification, and action gating. |
| Code changes and CI feedback | SWE agent | Require repo isolation, tests, review gates, and rollback. |
| Autonomous improvement of code, prompts, or artifacts | Research / experiment agent | Fixed eval metric, bounded modification surface, keep/revert loop |

### Autonomous Improvement Loops

A research/experiment agent iterates autonomously: suggest a change → apply it → evaluate → keep or revert → repeat. The pattern works on anything with a measurable evaluation function.

| Component | Purpose | Example |
|-----------|---------|---------|
| **Modification surface** | What the agent can change | One file (`train.py`), one prompt, one config |
| **Eval function** | How to score the result | `val_bpb`, yes/no checklist (3-6 questions), latency measurement |
| **Keep/revert rule** | When to keep a change | Score improves; revert if it regresses |
| **Termination** | When to stop | N rounds, target score reached, or manual stop |
| **Ledger** | Experiment history | Git commits, results.tsv, changelog with reasoning |

Design constraints:
- Keep the modification surface small (one file, one prompt). Broader surfaces compound silent regressions.
- Use binary or scalar metrics, not subjective ratings. "Does the headline include a specific number?" beats "rate the headline quality 1-10."
- 3-6 eval criteria is the sweet spot. More causes gaming; fewer misses failure modes.
- Preserve the changelog — future models pick up where the last agent left off.

See: [autoresearch](https://github.com/karpathy/autoresearch) (ML training), Lehmann's skill-optimization adaptation (prompt/skill improvement).

## Protocol Choice

| If the system needs... | Use |
| --- | --- |
| tool calls, database access, file access, prompts, resources | MCP |
| task handoffs, agent cards, multi-agent routing | A2A |
| both tools and collaborating agents | MCP + A2A |

Protocol defaults:

- Treat MCP as the tool/data integration layer, not as the agent architecture itself.
- Treat A2A handoffs as versioned APIs with schema validation and `trace_id` propagation.
- MCP has two standard transports, `stdio` and Streamable HTTP; SSE-only servers are legacy. A2A discovery is the Agent Card at `/.well-known/agent-card.json`; a handoff without a task id and state enum is not A2A, whatever it is called. Verified wire-level facts: [`references/protocol-decision-tree.md` § Protocol Facts](references/protocol-decision-tree.md#protocol-facts-checked-against-the-specs-2026-09-27).
- For remote MCP, scope authorization and identity explicitly; do not rely on network trust alone.
- A `stdio` server config is a command the client runs: never build it from untrusted input, and sandbox the host that launches servers. Local-transport security controls: [`../agents-mcp/references/mcp-security.md` § Local `stdio`](../agents-mcp/references/mcp-security.md#local-stdio).

## Agent-as-Code Pattern

Define agent personas as structured, versioned artifacts with explicit expertise, constraints, and expected outputs. This pattern treats agent definitions as reviewable code rather than ad-hoc prompt strings.

A well-defined agent spec includes:

| Field | Purpose |
|-------|---------|
| **Role** | What the agent is responsible for (e.g., "Architect", "QA reviewer") |
| **Expertise** | Domain knowledge and capabilities |
| **Constraints** | What it must not do, boundaries of authority |
| **Expected outputs** | Artifacts it produces (specs, reviews, plans, code) |
| **Interaction rules** | How it communicates with other agents or the human |

Benefits: agents can be reviewed in PRs, diffed between versions, and composed into teams with explicit role boundaries.

For current delivery methods and when to borrow from GSD, BMAD, Spec Kit, OpenSpec, MADD, or AI-SDLC, see [references/agent-delivery-methods.md](references/agent-delivery-methods.md).

### Scale-Adaptive Agent Complexity

Match agent sophistication to task complexity. Do not use a full multi-agent orchestration for a bug fix, and do not use a single prompt for a platform migration.

| Task Complexity | Agent Approach |
|----------------|----------------|
| Config change, typo | Direct prompt, no agent infrastructure |
| Bug fix, small feature | Single agent with bounded tools |
| Multi-module feature | Lead + 2-3 specialized workers |
| Cross-service migration | Full orchestration with persona definitions, debate, and verification |

The decision to scale up should be driven by observed ambiguity, not assumed complexity.

## Production Defaults

- Keep state explicit, serializable, and replayable.
- **Externalize all state to files** — plan, progress, decisions, and dependency outputs persist in structured files so any agent session can resume without context inheritance.
- Keep tool surfaces narrow; publish tasks, not raw backend complexity.
- Bound retries, budgets, context size, and recursion depth.
- Treat retrieved/tool content as untrusted input.
- Never put untrusted content, private data, and an exfiltration-capable tool in one model context. Split into a privileged planner that never sees raw untrusted text and a quarantined reader whose output is treated as data, not instructions (Debenedetti et al., 2025, CaMeL); injection classifiers are a second layer, not the boundary.
- Instrument LLM calls, retrieval, memory ops, and tool calls with consistent tracing.
- Gate database writes, financial actions, legal/compliance actions, and destructive operations behind human approval.
- Prefer refusal or degraded mode over hidden unsafe fallbacks.

For fresh-context workers, durable state, and session-vs-project boundaries, see [references/context-rotation-and-state.md](references/context-rotation-and-state.md).

## Templates And Entry Points

- Standard agent spec → [assets/core/agent-template-standard.md](assets/core/agent-template-standard.md)
- Quick prototype spec → [assets/core/agent-template-quick.md](assets/core/agent-template-quick.md)
- Specialized agent spec → [assets/core/agent-template-specialized.md](assets/core/agent-template-specialized.md)
- AI-native SDLC runbook → [assets/agent-template-ainative-sdlc.md](assets/agent-template-ainative-sdlc.md)
- Safety gate → [assets/checklists/agent-safety-checklist.md](assets/checklists/agent-safety-checklist.md)
- Tool schema template → [assets/tools/tool-definition.md](assets/tools/tool-definition.md)
- Tool validation checklist → [assets/tools/tool-validation-checklist.md](assets/tools/tool-validation-checklist.md)
- Multi-agent starter patterns → [assets/multi-agent/manager-worker-template.md](assets/multi-agent/manager-worker-template.md), [assets/multi-agent/evaluator-router-template.md](assets/multi-agent/evaluator-router-template.md)
- RAG starter templates → [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md) `assets/`; agent-side retrieval rules → [references/rag-patterns.md](references/rag-patterns.md); knowledge-base layout → [assets/knowledge-base/kb-architecture.md](assets/knowledge-base/kb-architecture.md)
- Usage-report `--pricing` file → [assets/pricing-template.json](assets/pricing-template.json) (ships no rates)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/agent_eval_runner.py` | Read JSONL task/expected/actual triples and report pass rates (offline). Fails closed: malformed or incomplete records count as failures. For adversarial suites and multi-turn harnesses, delegate to [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md). |
| `scripts/claude-usage.py` | Parse Claude Code usage logs, including subagent transcripts under each session, into token reports, counting each API response once (lines deduplicated on message ID plus request ID). Cost only with `--pricing <file>` (rates you copy from the provider's pricing page; schema in `assets/pricing-template.json`); without it cost is `unpriced`. With it, an unknown model or a 1-hour cache write without its own 1-hour rate is `unpriced` (exit 3), never priced at a default rate. `daily` from `stats-cache.json` has no tokens to price and exits 3 under `--pricing`; `models --pricing` reads the logs instead, where the cache-write TTL split exists. |
| `scripts/codex-usage.py` | Parse Codex usage logs into token reports, skipping re-sent token events. Cost only with `--pricing <file>`, same fail-closed rules and exit 3. Every report prices per event, as `traces` does. Codex logs carry no service tier or context class, so the script assumes the standard tier and base context, prints that it did, and marks the cost `estimated`. |

## Navigation

- Full deep-dive map → [references/index.md](references/index.md)
- Should we build this? → [references/build-vs-not-decision.md](references/build-vs-not-decision.md)
- MCP vs A2A → [references/protocol-decision-tree.md](references/protocol-decision-tree.md)
- Current operating defaults → [references/modern-best-practices.md](references/modern-best-practices.md)
- Delivery methods and planning systems → [references/agent-delivery-methods.md](references/agent-delivery-methods.md)
- Evaluation and telemetry → [references/evaluation-and-observability.md](references/evaluation-and-observability.md)
- CLI usage tracking → [references/coding-agent-usage-tracking.md](references/coding-agent-usage-tracking.md)
- Context rotation and durable state → [references/context-rotation-and-state.md](references/context-rotation-and-state.md)
- Deployment safety → [references/deployment-ci-cd-and-safety.md](references/deployment-ci-cd-and-safety.md)
- Autonomous loop / Ralph-Loop class → [references/autonomous-loop-patterns.md](references/autonomous-loop-patterns.md)
- Graph engineering, loop engineering, and graph-type disambiguation → [references/graph-and-loop-engineering.md](references/graph-and-loop-engineering.md)
- 24/7 operating model (SLOs, on-call, runbooks) → [references/24-7-operating-model.md](references/24-7-operating-model.md)
- Tool schemas and contracts → [references/tool-design-specs.md](references/tool-design-specs.md), [references/api-contracts-for-agents.md](references/api-contracts-for-agents.md)
- Decision and economics → [agent economics and ROI](references/agent-economics.md), [maturity and fleet governance](references/agent-maturity-governance.md), [framework landscape](references/framework-landscape.md)
- Architecture → [AI engine layers](references/ai-engine-layers.md), [OODA loop architecture](references/ooda-loop-agent-architecture.md), [inbox engine (event-driven intake)](references/inbox-engine-patterns.md), [OS agent capabilities](references/os-agent-capabilities.md), [code/SWE agents](references/code-swe-agents.md), [voice and multimodal agents](references/voice-multimodal-agents.md)
- Coordination → [A2A handoff patterns](references/a2a-handoff-patterns.md), [multi-agent patterns](references/multi-agent-patterns.md), [game theory for multi-agent systems](references/game-theory-multi-agent-systems.md), [principal-agent theory](references/principal-agent-theory.md)
- Context and memory → [context engineering](references/context-engineering.md), [context graph patterns](references/context-graph-patterns.md), [memory systems quick reference](references/memory-systems.md)
- SDK patterns → [Claude Agent SDK](references/claude-agent-sdk-patterns.md), [Pydantic AI](references/pydantic-ai-patterns.md)
- Operations and safety → [agent operations](references/agent-operations-best-practices.md), [guardrails implementation](references/guardrails-implementation.md), [escalation patterns](references/escalation-patterns.md)
- Curated external sources → [`data/sources.json`](data/sources.json); when browsing is unavailable, answer framework-ranking, lifecycle, transport/auth, A2A-maturity, and pricing questions from it, say what is assumed, and label the claim unverified

## Related Skills

- Choosing agent vs single call vs RAG vs fine-tune, and broad LLM system design → [`../ai-architecture-advisor/SKILL.md`](../ai-architecture-advisor/SKILL.md)
- LangGraph bot implementation → [`../ai-bot-builder/SKILL.md`](../ai-bot-builder/SKILL.md)
- RAG implementation → [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md)
- Vector-brain implementation → [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md)
- MCP implementation → [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md)
- Subagent orchestration → [`../agents-subagents/SKILL.md`](../agents-subagents/SKILL.md)
- Swarm and parallel dispatch → [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md)
- Hook guardrails and lifecycle → [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md)
- Skill packaging → [`../agents-skills/SKILL.md`](../agents-skills/SKILL.md)
- Project memory → [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md)
- Eval harnesses → [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md)
- Observability → [`../qa-observability/SKILL.md`](../qa-observability/SKILL.md)
- Security and AppSec → [`../software-security-appsec/SKILL.md`](../software-security-appsec/SKILL.md)

## Usage Notes

- Start here for architecture and production posture, not for deep implementation walkthroughs.
- Prefer stable capability guidance over dated framework rankings.
- Load detailed references only after the user’s direction is clear.
- Keep recommendations operational: contracts, failure modes, gates, telemetry, and rollback.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
