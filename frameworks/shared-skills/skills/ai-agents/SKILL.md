---
name: ai-agents
description: AI agent architecture, protocol choice, evaluation, observability, and build-vs-not decisions. Use when scoping or reviewing agent systems before deeper implementation.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Agents Development — Architecture Hub

Use this skill to decide whether a workflow should be an agent, which agent shape fits, which protocol boundary to use, and what production controls must exist before rollout.

Default posture: explicit control flow, bounded tools, typed contracts, auditable state, human approval for high-risk actions, and telemetry from day one.

Keep this file lean. Load detail from [`references/index.md`](references/index.md), `assets/`, and sibling skills only when needed.

## When to Use This Skill

Use this skill when the user asks for:

- agent architecture or operating-model decisions
- build-vs-not-agent assessment
- MCP vs A2A protocol choice
- production readiness review for an existing agent system
- evaluation, observability, rollout, or safety planning
- framework selection after requirements are already clear
- a starting template for a new agent spec

## Use Other Skills for Depth

- Prompt contracts and structured outputs → [`../ai-prompt-engineering/SKILL.md`](../ai-prompt-engineering/SKILL.md)
- Retrieval, chunking, reranking, search quality → [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md)
- Vector-brain implementation, schemas, ingest scripts, manifests, and retrieval tool contracts → [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md)
- Bot building (support, sales, conversation design, LangGraph) → `ai-bot-builder`
- Voice bots (STT/TTS pipeline, telephony, latency) → [`../ai-voice-bots/SKILL.md`](../ai-voice-bots/SKILL.md)
- MCP server setup, transports, server builds → [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md)
- Subagents, delegation contracts, least-privilege tools → `agents-subagents`
- CLI-based tools (non-interactive, idempotent, agent-friendly patterns) → [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md)
- Evaluation harnesses, attack suites, regression gates → [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md)
- Deployment guardrails and model operations → [`../ai-mlops/SKILL.md`](../ai-mlops/SKILL.md)
- Application security and high-risk controls → [`../software-security-appsec/SKILL.md`](../software-security-appsec/SKILL.md)
- Model and inference cost tuning → [`../ai-llm/SKILL.md`](../ai-llm/SKILL.md), [`../ai-llm-inference/SKILL.md`](../ai-llm-inference/SKILL.md)

## Default Workflow

1. Run the build-vs-not decision gate.
2. Define the task environment: performance measure, environment, percepts/sensors, actions/tools, observability, determinism, time horizon, and single-agent vs multi-agent interaction.
3. Choose control flow; default to workflow/FSM/DAG for production.
4. Choose protocol boundaries: MCP for tools/data, A2A for agent handoffs.
5. Define contracts: tool schemas, handoff payloads, state model, success criteria.
6. Add evaluation and telemetry before shipping.
7. Add human approval, rollback, and kill-switches for irreversible actions.
8. Start from templates, then route to specialized skills for implementation depth.

## ASCII Flow

```text
Agent-system request
  -> Build-vs-not gate
     +-- simpler workflow/form/tool fits -> do not build an agent
     +-- autonomy justified              -> continue
  -> Define task environment and performance measure
  -> Choose control flow: workflow, FSM, DAG, or agent loop
  -> Set boundaries: MCP for tools/data, A2A for handoffs
  -> Define state, schemas, success criteria, and approvals
  -> Add evals, telemetry, rollback, and kill switches
  -> Route implementation depth to specialized skills
```

## Known Traps

- treating "agent" as the default interaction pattern when a workflow, form, or plain tool call would be simpler
- using MCP as the overall agent architecture instead of the tool and resource integration layer
- adding long-term memory without provenance (A13), retention policy, correction flow (A11 — forget path), and user-value proof. Use [`ai-context-layer/patterns-catalog.md`](../ai-context-layer/references/patterns-catalog.md) to pick a named pattern and [`ai-context-layer/anti-patterns-catalog.md`](../ai-context-layer/references/anti-patterns-catalog.md) for the sweep
- letting planner loops recurse without explicit step, budget, and escalation limits
- shipping autonomous actions before evaluator coverage, rollback controls, and human approval paths exist
- defaulting to a multi-agent topology for reasoning-heavy work when a single strong model at an equal token budget matches or beats it — under a fixed reasoning-token budget, message-passing between agents loses mutual information vs. full-context conditioning (Data Processing Inequality). Confirm the task is genuinely parallelizable or tool/role-diverse before fanning out. (arXiv:2604.02460, Apr 2026 preprint — not peer-reviewed; scope: text-only multi-hop reasoning; verify before relying.)

## Common Anti-Patterns

- chat-first agent design with no state model, contract, or action boundary
- multi-agent topologies introduced before single-agent failure modes are understood
- tool surfaces defined by convenience rather than least privilege
- evaluation added after launch as observability theater instead of a release gate
- provider or framework selection driven by hype, benchmark screenshots, or marketing taxonomy alone

## Quick Reference

| Question | Default |
| --- | --- |
| Should this be an agent? | Start with [`references/build-vs-not-decision.md`](references/build-vs-not-decision.md); default answer is "no" until volume, ambiguity, and value justify autonomy. |
| What is the task environment? | State the performance measure, environment, percepts/sensors, actions/tools, observability, determinism, horizon, and other agents before choosing a framework. |
| Which control flow fits? | Prefer workflow/FSM/DAG; use planner/executor only when branching cannot be modeled explicitly. |
| MCP or A2A? | MCP for external tools/data, A2A for agent-to-agent coordination, both when a multi-agent system also needs tools. |
| When to use multi-agent? | Only when roles, handoff contracts, and verifier responsibilities are explicit. |
| When to add long-term memory? | Only with provenance, retention rules, user consent, and clear value. Pick a named pattern from [`ai-context-layer/patterns-catalog.md`](../ai-context-layer/references/patterns-catalog.md) (P2 for app-orchestrated, P3 for self-editing, P4 for temporal, P6 for conversational). Run the anti-pattern sweep — A1 (no raw transcripts), A11 (forget path required), A13 (provenance mandatory). |
| What must exist before rollout? | Eval suite, telemetry, action limits, human escalation, rollback path, and kill switch. |

## Autonomy Shapes — How to Host an Agent 24/7

Three deployment shapes for running agents continuously. Pick by the **trigger model**, not by the framework.

| Shape | Trigger | When to use | Primary guide |
|---|---|---|---|
| **A — Triggered / hosted run** | Webhook, queue, schedule, `/fire` | Per-event agent work, scheduled jobs, fan-out from external sources | [`../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md`](../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md) + [`../ai-coding-agents-tasks/references/durable-trigger-integration.md`](../ai-coding-agents-tasks/references/durable-trigger-integration.md) |
| **B — Always-on bot / voice server** | Sessions, WebSocket, SIP call | Support / sales / voice bots with conversational state | [`../ai-bot-builder/references/production-deployment.md`](../ai-bot-builder/references/production-deployment.md) + [`../ai-bot-builder/references/stateful-rollout-and-blue-green.md`](../ai-bot-builder/references/stateful-rollout-and-blue-green.md) + [`../ai-voice-bots/references/production-deployment.md`](../ai-voice-bots/references/production-deployment.md) |
| **C — Autonomous loop** | PRD + loop driver until acceptance met | Long-horizon work: refactors, migrations, research, Ralph-Loop class | [`references/autonomous-loop-patterns.md`](references/autonomous-loop-patterns.md) |

Cross-shape requirements:

- **Budget and kill-switch enforcement**: [`../agents-hooks/references/budget-and-loop-hooks.md`](../agents-hooks/references/budget-and-loop-hooks.md)
- **24/7 operating model (SLOs, on-call, runbooks)**: [`references/24-7-operating-model.md`](references/24-7-operating-model.md)
- **Provider failover and secret rotation**: [`../ai-bot-builder/references/secret-rotation-and-model-fallback.md`](../ai-bot-builder/references/secret-rotation-and-model-fallback.md)
- **Where to host (Vercel / Fly.io / Railway / Cloudflare / Render)**: [`../software-paas-hosting/SKILL.md`](../software-paas-hosting/SKILL.md) and [`../software-paas-hosting/references/agent-hosting-matrix.md`](../software-paas-hosting/references/agent-hosting-matrix.md)

## Architecture Selection

| Need | Default Agent Shape | Notes |
| --- | --- | --- |
| Deterministic business process | Workflow agent | Best default for auditable production behavior. |
| Bounded external actions | Tool-using agent | Keep tools narrow, typed, and permission-scoped. |
| Knowledge-grounded answers | RAG agent | Require citations, ACL-aware retrieval, and refusal on missing evidence. |
| Long multi-step work with branching | Planner/executor | Use strict step budgets, checkpoints, and replanning limits. |
| Specialized roles with explicit ownership | Multi-agent orchestrator | Handoffs are APIs; add verifier/evaluator roles early. Score the design against the MAST failure taxonomy — do not re-derive it: [`../agents-subagents/references/mast-failure-taxonomy.md`](../agents-subagents/references/mast-failure-taxonomy.md) (14 modes; original Cemri et al. distribution ≈ Specification/System Design 41.8% / Inter-Agent Misalignment 36.9% / Task Verification 21.3% — figures vary across secondary write-ups, verify against the primary paper before quoting; NeurIPS 2025 Datasets & Benchmarks track — arXiv:2503.13657). |
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
- Prefer `stdio` or Streamable HTTP for MCP transports; treat older SSE-only guidance as compatibility material, not the default.
- For remote MCP, scope authorization and identity explicitly; do not rely on network trust alone.
- Known footgun: the official MCP SDK `stdio` interface has a by-design config→OS-command execution path (CVE-2026-30623; ~7k public servers exposed; Anthropic confirmed by-design and declined a protocol-level fix — input sanitization is the integrator's responsibility). Never pass untrusted server config into an `stdio` MCP launch; sandbox the MCP host process. Verified multi-source, April 2026.

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

For current delivery methods and when to borrow from GSD, BMAD, Spec Kit, OpenSpec, MADD, or AI-SDLC, see [`references/agent-delivery-methods.md`](references/agent-delivery-methods.md).

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
- Instrument LLM calls, retrieval, memory ops, and tool calls with consistent tracing.
- Gate database writes, financial actions, legal/compliance actions, and destructive operations behind human approval.
- Prefer refusal or degraded mode over hidden unsafe fallbacks.

For fresh-context workers, durable state, and session-vs-project boundaries, see [`references/context-rotation-and-state.md`](references/context-rotation-and-state.md).

## Templates And Entry Points

- Standard agent spec → [`assets/core/agent-template-standard.md`](assets/core/agent-template-standard.md)
- Quick prototype spec → [`assets/core/agent-template-quick.md`](assets/core/agent-template-quick.md)
- Specialized agent spec → [`assets/core/agent-template-specialized.md`](assets/core/agent-template-specialized.md)
- AI-native SDLC runbook → [`assets/agent-template-ainative-sdlc.md`](assets/agent-template-ainative-sdlc.md)
- Safety gate → [`assets/checklists/agent-safety-checklist.md`](assets/checklists/agent-safety-checklist.md)
- Tool schema template → [`assets/tools/tool-definition.md`](assets/tools/tool-definition.md)
- Tool validation checklist → [`assets/tools/tool-validation-checklist.md`](assets/tools/tool-validation-checklist.md)
- Multi-agent starter patterns → [`assets/multi-agent/manager-worker-template.md`](assets/multi-agent/manager-worker-template.md), [`assets/multi-agent/evaluator-router-template.md`](assets/multi-agent/evaluator-router-template.md)
- RAG starter patterns → [`assets/rag/rag-basic.md`](assets/rag/rag-basic.md), [`assets/rag/rag-advanced.md`](assets/rag/rag-advanced.md), [`assets/rag/hybrid-retrieval.md`](assets/rag/hybrid-retrieval.md)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/agent_eval_runner.py` | Read JSONL task/expected/actual triples and report pass rates (offline). For adversarial suites and multi-turn harnesses, delegate to [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md). |
| `scripts/claude-usage.py` | Parse Claude Code usage logs |
| `scripts/codex-usage.py` | Parse Codex usage logs |

## Navigation

- Full deep-dive map → [`references/index.md`](references/index.md)
- Should we build this? → [`references/build-vs-not-decision.md`](references/build-vs-not-decision.md)
- MCP vs A2A → [`references/protocol-decision-tree.md`](references/protocol-decision-tree.md)
- Current operating defaults → [`references/modern-best-practices.md`](references/modern-best-practices.md)
- Delivery methods and planning systems → [`references/agent-delivery-methods.md`](references/agent-delivery-methods.md)
- Evaluation and telemetry → [`references/evaluation-and-observability.md`](references/evaluation-and-observability.md)
- CLI usage tracking → [`references/coding-agent-usage-tracking.md`](references/coding-agent-usage-tracking.md)
- Context rotation and durable state → [`references/context-rotation-and-state.md`](references/context-rotation-and-state.md)
- Deployment safety → [`references/deployment-ci-cd-and-safety.md`](references/deployment-ci-cd-and-safety.md)
- Autonomous loop / Ralph-Loop class → [`references/autonomous-loop-patterns.md`](references/autonomous-loop-patterns.md)
- 24/7 operating model (SLOs, on-call, runbooks) → [`references/24-7-operating-model.md`](references/24-7-operating-model.md)
- Tool schemas and contracts → [`references/tool-design-specs.md`](references/tool-design-specs.md), [`references/api-contracts-for-agents.md`](references/api-contracts-for-agents.md)
- Curated external sources → [`data/sources.json`](data/sources.json)

## Related Skills

- Choosing agent vs single call vs RAG vs fine-tune → [`../ai-architecture-advisor/SKILL.md`](../ai-architecture-advisor/SKILL.md)
- Broad LLM system design → [`../ai-llm/SKILL.md`](../ai-llm/SKILL.md)
- LangGraph bot implementation → `ai-bot-builder`
- RAG implementation → [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md)
- Vector-brain implementation → [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md)
- MCP implementation → [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md)
- Subagent orchestration → `agents-subagents`
- Swarm and parallel dispatch → [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md)
- Hook guardrails and lifecycle → [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md)
- Skill packaging → [`../agents-skills/SKILL.md`](../agents-skills/SKILL.md)
- Project memory → [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md)
- Eval harnesses → [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md)
- Observability → [`../qa-observability/SKILL.md`](../qa-observability/SKILL.md)
- Security and AppSec → [`../software-security-appsec/SKILL.md`](../software-security-appsec/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current protocol specs, framework capabilities, release status, and vendor behavior before final answers.
- Prefer official docs, primary specifications, and first-party repos for fast-moving agent infrastructure claims.
- If a volatile claim cannot be checked, label it as unverified instead of presenting it as settled guidance.

## Trend Awareness Protocol

When users ask for:

- "best framework for X"
- "is X still relevant"
- "latest AI agent stack"
- pricing, version, or support-matrix questions
- MCP transport/auth guidance
- A2A ecosystem or vendor SDK recommendations

verify with web search and primary sources before answering.

Volatile areas to re-check every time:

- framework language support and lifecycle status
- MCP transport and authorization guidance
- OpenAI/Anthropic/Google pricing
- A2A ecosystem maturity and official docs
- vendor-specific tool, tracing, and handoff capabilities

If browsing is unavailable, use [`data/sources.json`](data/sources.json), say what is assumed, and avoid strong ranking claims.

## Usage Notes

- Start here for architecture and production posture, not for deep implementation walkthroughs.
- Prefer stable capability guidance over dated framework rankings.
- Load detailed references only after the user’s direction is clear.
- Keep recommendations operational: contracts, failure modes, gates, telemetry, and rollback.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
