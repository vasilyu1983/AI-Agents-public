---
description: Architecture decision: isolated sub-agents vs. collaborating agent teams. Decompose by coordination shape, not role labels. Community-sourced framing.
last_verified: 2026-09-16
status: community-reported
---

# Sub-Agents vs Agent Teams

Architecture decision: when to use isolated sub-agents vs collaborating agent teams. The right axis is *coordination shape* — what context the task actually needs — not *task complexity*.

Source: @Suryanshti777, 2026-04-24 — <https://x.com/Suryanshti777/status/2047694444787577236>

Cross-links: [`team-selection-guide.md`](team-selection-guide.md), [`agent-patterns.md`](agent-patterns.md).

## Table of Contents

- [Industry Vocabulary (Conductor / Swarm / Holonic)](#industry-vocabulary-conductor--swarm--holonic)
- [Sub-Agents: Parallelism with Isolation](#sub-agents-parallelism-with-isolation)
- [Agent Teams: Coordination through Communication](#agent-teams-coordination-through-communication)
- [Core Difference Table](#core-difference-table)
- [Where Most Designs Go Wrong](#where-most-designs-go-wrong)
- [The 5 Patterns That Actually Matter](#the-5-patterns-that-actually-matter)
- [When NOT To Use Multi-Agent](#when-not-to-use-multi-agent)
- [SDK Example](#sdk-example)

## Industry Vocabulary (Conductor / Swarm / Holonic)

The 2026 industry vocabulary for multi-agent topology has crystallized around three names. This skill's internal terminology maps directly:

| Industry term | What it is | Maps to in this skill |
|---|---|---|
| **Conductor** | Centralized hierarchical control. One lead routes work, synthesizes results. | Subagent (parent + workers) + harness pattern "orchestrator-worker" in [`harness-patterns.md`](harness-patterns.md) |
| **Swarm** | Decentralized parallel execution. Workers coordinate peer-to-peer or via shared task layer. | Claude Code Agent Teams (peer-to-peer mailbox + shared task list) when v2.1.32+ flag is on |
| **Hybrid** | Hierarchical swarm — conductor at top, swarm inside one or more nodes. | Most production setups; e.g. orchestrator-worker with one worker that itself runs an agent team |
| **Holonic / nested-summary** | Recursive structure. Lower-level "holons" share **summaries** upward and peer-coordinate sideways within a parent. | The `dev-context-*` pipeline (portfolio → repo → packet → feature delivery) is a natural holon: each layer summarizes for the layer above. See [`context-first-protocol.md`](context-first-protocol.md). |
| **MoA-layered (Mixture-of-Agents)** | Layered fan-out → aggregator. N proposers answer the same question in parallel; one or more aggregator layers merge their outputs. Distinct from Conductor because aggregators don't decompose — they synthesize. | Mixture-of-Agents harness pattern in [`harness-patterns.md`](harness-patterns.md). Stack BMV (G18) or RCS (G19) as aggregator selection rules. Use Self-MoA variant (single strong model, N samples) on verifiable tasks. |

**Why holonic deserves naming:** when a long-running team produces summary artifacts that feed *other* teams (e.g. a portfolio map feeding a code-review team feeding a release-readiness team), the topology isn't flat hierarchy and isn't pure swarm. It's nested holons that share context laterally inside their level and summaries vertically across levels. This is the right mental model for cross-team handoffs.

**Practical rules:**

- For 2–5 specialists on one decision, prefer Conductor (subagents + parent synthesis). Lower coordination cost.
- For 6+ workers on independently parallelizable sub-tasks, prefer Swarm (agent teams or explicit fan-out). Higher coordination cost is amortized by parallelism.
- For cross-domain work that naturally summarizes upward (portfolio → repo → feature), explicitly model as Holonic and design the summary contract per level.
- For high-stakes single-answer questions where the task can't be decomposed (architecture proposals, security verdicts), prefer MoA-layered (proposers + aggregator). Documented gains are in the mid single digits of points on AlpacaEval 2.0 (MoA: 65.1% vs 57.5%, [arXiv:2406.04692](https://arxiv.org/abs/2406.04692); Self-MoA: +6.6% over MoA, [arXiv:2502.00674](https://arxiv.org/abs/2502.00674)); the paper abstracts, not the community post, are the source for these figures. The 5-10× token multiple is a planning estimate [unverified as of 2026-09-16: not reported in the cited papers].
- Avoid pure flat-hierarchy designs above ~7 workers — message routing through the lead becomes the bottleneck.

Sources: [arXiv 2508.12683 (Hierarchical MAS taxonomy)](https://arxiv.org/abs/2508.12683); [Conductor vs Swarm (2026 industry guide)](https://agixtech.com/insights/conductor-vs-swarm-multi-agent-ai-orchestration/); [arXiv 2406.04692 (Mixture-of-Agents)](https://arxiv.org/abs/2406.04692); [arXiv 2502.00674 (Self-MoA)](https://arxiv.org/abs/2502.00674).

## Sub-Agents: Parallelism with Isolation

Each sub-agent has:

- A system prompt defining its role.
- A limited set of tools.
- A completely isolated context.
- A single, well-scoped task.
- Returns only the final output, not reasoning or intermediate steps.

Hard constraints:

- Parent-led result return is the portable/default topology. Some collaboration surfaces also expose follow-up or agent-to-agent messaging; do not design around that unless the target runtime documents it.
- Subagents can spawn children on supported Claude and Codex collaboration surfaces. Bound nesting through tools, prompts, and repository policy rather than an undocumented Codex `max_depth` assumption. On Claude, omit `Agent` or add `disallowedTools: [Agent]` when a role must remain a leaf.
- Keep the parent as the source of truth for requirements and synthesis even when a runtime permits direct messaging.

Sub-agents are about **compression**, not just speed: they turn messy exploration into clean signal.

## Agent Teams: Coordination through Communication

Built for collaboration, not delegation:

- **Lead agent** assigns tasks and synthesizes results.
- **Teammate agents** execute.
- **Shared task layer** tracks progress and dependencies.

Teammates maintain context, communicate, and adapt in real time — a frontend agent can signal a backend change and the rest update instantly.

### Reusing a subagent definition as a teammate drops its skill wiring

When a subagent definition runs as a teammate, its `skills:` and `mcpServers` frontmatter is **silently ignored** — teammates load skills from project and user settings like a normal session, and no warning is emitted. `tools`, `model`, and the body instructions still apply. Source: [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams), verified 2026-08-15.

This is a design constraint on the whole member catalog, not an edge case: **all 156 canonical members in `agents/claude/` declare `skills:`**, none declare `mcpServers`. Affected by family — legal (62), startup (14), software (14), marketing (12), dev (12), ai (9), project (9), data (6), qa/ops/docs (5 each), product (3).

The compensation is already in place and must stay: every canonical member carries an inline **Teammate mode** brief in its body telling the role to treat the launch prompt as authoritative for skill guidance rather than assuming frontmatter was inherited. When authoring a new member, write the role brief so it survives without `skills:` — a member whose competence depends on frontmatter injection will silently degrade to a generic session the moment it is used as a teammate. See [`runtime-surfaces.md`](runtime-surfaces.md) §"Teammate reuse rules" and [`team-lifecycle.md`](team-lifecycle.md).

## Core Difference Table

| Axis | Sub-Agents | Agent Teams |
|---|---|---|
| Lifetime | Stateless / one-shot | Persistent |
| Communication | Through parent only | Peer-to-peer |
| Context | Isolated per agent | Shared task layer |
| Control | Parent-controlled | Lead + collaborative |
| Best for | Independent tasks | Tasks that depend on each other |

## Where Most Designs Go Wrong

Splitting by **role** (planner / developer / tester) creates context loss at every handoff:

- The implementer doesn't know what the planner knew.
- The tester doesn't know what the implementer decided.
- Quality drops at every boundary.

Right approach: **decompose by context, not by role.** Ask "what information does this task need?" If two tasks share deep context, keep them in the same agent. Split only when context can be cleanly separated.

## The 5 Patterns That Actually Matter

1. **Prompt chaining** — sequential steps.
2. **Routing** — send tasks to the right agent.
3. **Parallelization** — run independent work together.
4. **Orchestrator–worker** — one agent delegates.
5. **Evaluator–optimizer** — generate and refine.

Match the pattern to the dependency shape, not to how complex the task feels.

## When NOT To Use Multi-Agent

Use multi-agent when:

- Context isolation is required.
- Tasks are independently parallelizable.
- Real specialization (different tools, models, prompts) earns its keep.

Avoid multi-agent when:

- Agents would depend heavily on each other (coordination overhead > savings).
- The task is simple — a single agent is enough.

Final principle: **design around context boundaries, not roles. Start simple and add complexity only when needed.**

## SDK Example

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async def main():
    async for message in query(
        prompt="Review the authentication module for issues",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob", "Agent"],
            agents={
                "security-reviewer": AgentDefinition(
                    description="Find vulnerabilities and security risks",
                    prompt="You are a security expert.",
                    tools=["Read", "Grep", "Glob"],
                    model="sonnet",
                ),
                "performance-optimizer": AgentDefinition(
                    description="Identify performance bottlenecks",
                    prompt="You are a performance engineer.",
                    tools=["Read", "Grep", "Glob"],
                    model="sonnet",
                ),
            },
        ),
    ):
        print(message)
```

The `description` field is the routing signal — write it for the matcher (concrete capabilities + when to use), not for humans.
