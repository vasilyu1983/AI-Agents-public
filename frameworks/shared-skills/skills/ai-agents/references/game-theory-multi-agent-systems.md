# Game Theory for Multi-Agent Systems

> **Gate before invoking:** Check [`foundations-game-theory` § When to Apply](../../foundations-game-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Nash equilibrium, mechanism design, and common knowledge applied to AI agent coordination, tool access negotiation, and multi-agent workflow design. Based on non-cooperative game theory and mechanism design.

## Contents

- [Agents as Strategic Players](#agents-as-strategic-players)
- [Nash Equilibrium in Agent Coordination](#nash-equilibrium-in-agent-coordination)
- [Mechanism Design for Agent Incentives](#mechanism-design-for-agent-incentives)
- [Common Knowledge and Communication](#common-knowledge-and-communication)
- [Resource Contention Games](#resource-contention-games)
- [Cooperative vs. Competitive Agent Architectures](#cooperative-vs-competitive-agent-architectures)
- [Design Patterns](#design-patterns)
- [Decision Checklist](#decision-checklist)

---

## Agents as Strategic Players

When multiple AI agents operate in a shared environment (shared tools, APIs, file systems, or tasks), their interactions form a game:

| Game Element | Agent System Equivalent |
|-------------|----------------------|
| Players | Individual agents (worker, reviewer, orchestrator) |
| Strategies | Tool calls, task selection, output formats, resource requests |
| Payoffs | Task completion quality, latency, cost, user satisfaction |
| Information | Context available to each agent, visibility into other agents' state |

### When Game Theory Applies to Agent Systems

| Situation | Applies? | Why |
|-----------|:--------:|-----|
| Single agent, single task | No | No strategic interaction |
| Multiple agents, independent tasks | Minimal | No interdependence — each agent optimizes alone |
| Multiple agents, shared resources | Yes | Resource contention creates strategic interaction |
| Multiple agents, dependent tasks | Yes | Output quality of one affects payoff of another |
| Adversarial agents (red team/blue team) | Yes | Directly competitive strategic interaction |
| Agent + human interaction | Yes | Human and agent preferences may conflict |

---

## Nash Equilibrium in Agent Coordination

### Finding Stable Agent Configurations

A multi-agent system is in **Nash equilibrium** when no single agent can improve its outcome by unilaterally changing behavior.

**Desirable equilibria**:
- All agents complete their assigned tasks efficiently
- No agent overloads shared resources
- Quality meets thresholds across all outputs

**Undesirable equilibria**:
- Agents race for the same resources (contention spiral)
- Agents produce redundant work (duplication equilibrium)
- Agents wait for each other indefinitely (deadlock)

### Equilibrium Design Principles

| Principle | Implementation | Avoids |
|-----------|---------------|--------|
| **Clear task ownership** | Assign non-overlapping task domains | Duplication and contention |
| **Resource quotas** | Rate limits, token budgets per agent | Resource starvation |
| **Priority ordering** | Explicit agent priority for shared resources | Deadlock |
| **Output contracts** | Defined interface between agents | Cascading quality failures |

---

## Mechanism Design for Agent Incentives

### Designing the Rules

Mechanism design for agents means designing the orchestration rules so that each agent, acting in its own "interest" (optimizing its objective), produces the outcome you want.

| Design Goal | Mechanism | How It Works |
|-------------|-----------|-------------|
| **Truthful status reporting** | Reward accuracy, penalize over-optimism | Agents report task completion honestly instead of prematurely |
| **Efficient resource use** | Budget constraints with rollover | Agents conserve resources because budget is finite |
| **Quality over speed** | Score on output quality, not completion time | Agents don't race to finish at the expense of quality |
| **Collaboration over competition** | Joint scoring on shared outcomes | Agents help each other because joint outcome affects each agent's score |

### Incentive Compatibility for Agents

An agent orchestration system is **incentive compatible** when each agent's locally optimal behavior produces the globally optimal outcome.

**Test**: If each agent greedily optimizes its own objective, does the system converge to a good state?

| System | Incentive Compatible? | Fix |
|--------|:--------------------:|-----|
| Workers compete for limited context window | No — agents bloat context to monopolize | Budget per agent, shared context pool with priority |
| Reviewer agent gets same score regardless of feedback quality | No — reviewer has no incentive to be thorough | Score reviewer on downstream impact of reviewed work |
| Parallel agents with no dependency tracking | No — agents may duplicate or conflict | Dependency graph with task locks |

---

## Common Knowledge and Communication

### Common Knowledge in Agent Systems

**Common knowledge** means every agent knows X, every agent knows that every agent knows X, and so on infinitely. In game theory, common knowledge enables coordination without explicit communication.

### Agent Communication Protocols

| Protocol | Game Theory Analogy | When to Use |
|----------|--------------------:|-------------|
| **Broadcast** (all agents see all messages) | Common knowledge — everyone knows and knows everyone knows | Small agent teams, critical coordination |
| **Point-to-point** (1:1 messages) | Private information — only sender and receiver know | Large teams, need-to-know basis |
| **Shared state** (database/file) | Public information — available to all who check | Asynchronous coordination, audit trail |
| **Event-driven** (pub/sub) | Observable actions — agents infer from events | Loosely coupled, scalable systems |

### Information Revelation Strategy

| What to Share | With Whom | Game Theory Basis |
|--------------|-----------|-------------------|
| Task completion status | Orchestrator + dependent agents | Enables coordination without polling |
| Error/failure state | Orchestrator only | Prevents cascading panic — orchestrator decides response |
| Resource usage | Orchestrator (for budgeting) | Enables fair allocation |
| Intermediate outputs | Dependent agents only | Reduces context bloat; targeted information sharing |

---

## Resource Contention Games

### Common Contention Scenarios

| Resource | Contention Type | Resolution |
|----------|----------------|------------|
| **API rate limits** | Multiple agents hitting same API | Token bucket shared across agents, priority queue |
| **File system** | Concurrent writes to same files | File locking, single-writer principle |
| **Context window** | Multiple agents consuming shared context | Per-agent context budget, summarization gates |
| **Human attention** | Multiple agents requesting human review | Priority queue, batched review sessions |
| **Compute budget** | Cost allocation across agents | Per-agent cost caps, shared pool with fairness rules |

### Fair Division Mechanisms

| Mechanism | How It Works | When to Use |
|-----------|-------------|-------------|
| **Equal split** | Each agent gets 1/N of resources | Tasks are roughly equal in resource needs |
| **Proportional** | Allocation proportional to task importance | Tasks vary in priority |
| **Priority queue** | Highest-priority agent goes first | Strict ordering exists (critical path vs. optional) |
| **Auction** | Agents "bid" importance; highest bid wins | Dynamic priority that changes per round |

---

## Cooperative vs. Competitive Agent Architectures

### Cooperative (Aligned Objectives)

All agents share the same goal — optimize the system-level outcome.

| Pattern | Structure | Strength |
|---------|-----------|----------|
| Orchestrator-worker | Central coordinator assigns tasks | Clear control, efficient allocation |
| Pipeline | Output of agent A feeds into agent B | Sequential efficiency, clear interfaces |
| Ensemble | Multiple agents produce outputs, best is selected | Quality through diversity |

### Competitive (Adversarial Objectives)

Agents have opposed or independent objectives — used intentionally for quality.

| Pattern | Structure | Strength |
|---------|-----------|----------|
| Red team / blue team | Attacker agent vs. defender agent | Security and robustness testing |
| Evaluator-optimizer | One agent optimizes, another critiques | Prevents quality drift |
| Debate | Two agents argue opposing positions | Better reasoning through adversarial pressure |

### Choosing the Architecture

| Criterion | Cooperative | Competitive |
|-----------|:-----------:|:-----------:|
| Task requires consistency | Preferred | Risky — agents may contradict |
| Quality depends on scrutiny | Secondary | Preferred — adversarial pressure catches errors |
| Speed is critical | Preferred — less overhead | Slower — requires resolution mechanism |
| Creativity needed | Useful (ensemble) | Useful (debate) |
| Trust in individual agent output | Assumed | Verified through opposition |

### LLM Agent Behavioral Realities (2026 Research)

LLM-based agents deviate from classical game-theoretic rationality in important ways:

| Finding | Source | Design Implication |
|---------|--------|-------------------|
| **Pro-social bias** | IJCAI-25 survey: "Game Theory Meets LLMs" | LLM agents cooperate more than Nash equilibrium predicts — useful for cooperative architectures but may underperform in adversarial roles |
| **Tacit collusion** | GPT-4 agents in repeated Bertrand pricing games learned to maintain supracompetitive prices via reward-punishment | In competitive agent designs, LLM agents may spontaneously collude instead of competing — monitor for convergence to non-competitive equilibria |
| **Rationality degrades with complexity** | arXiv 2411.05990: game-theoretic workflow scaffolding restores rationality | For complex multi-agent games, add explicit game-theoretic reasoning steps to agent prompts — don't assume rational play emerges naturally |
| **Personality affects strategy** | Big Five trait definitions in prompts alter negotiation behavior | Agent persona design is a strategic variable — aggressive vs. cooperative agents behave differently in the same game |

**Key takeaway**: Don't assume LLM agents will play Nash-optimal strategies. They bring human-like biases — cooperation bias in competitive settings, collusion risk in pricing, and irrationality under complexity. Design accordingly: add guardrails for competitive agents, exploit cooperation bias for collaborative ones.

---

## Design Patterns

### Pattern: Vickrey Task Allocation

Agents "bid" on tasks by reporting estimated difficulty/time. Assign to lowest bidder. Agent doesn't "pay" their bid — they pay the second-lowest bid (in terms of expected effort). Incentive: report true estimates.

### Pattern: Tit-for-Tat Collaboration

In multi-round agent interactions: Agent A cooperates (provides quality output) in round 1. If Agent B reciprocates with quality, continue cooperating. If Agent B provides low quality, reduce effort in response. Prevents free-riding in collaborative pipelines.

### Pattern: Common Knowledge Checkpoint

Before critical coordination points, broadcast state to all agents and confirm receipt. This creates common knowledge — every agent knows the state AND knows every other agent knows. Enables coordinated action without explicit synchronization.

### Pattern: Game-Theoretic Workflow Scaffolding (2026)

For complex multi-agent interactions, add explicit game-theoretic reasoning as an intermediate step:
1. Agent receives task context
2. Agent explicitly models: "What are other agents' likely strategies?"
3. Agent computes best response given those strategies
4. Agent executes action

This scaffolding restores rational behavior that degrades when LLM agents face complex games without structured reasoning.

### Pattern: Federated Multi-Agent Coordination

For independent AI systems with competing priorities (inspired by Johns Hopkins MpFL framework): use game-theoretic mechanisms to negotiate resource allocation across autonomous agents that don't share a central orchestrator. Each agent reports its utility function; a fair division mechanism allocates shared resources.

---

### Pattern: Courtroom Debate with Progressive Evidence (PROClaim, March 2026)

Structure adversarial verification as a trial: plaintiff argues FOR, defense argues AGAINST, a critic independently evaluates, and a judicial panel renders verdict. Progressive RAG dynamically retrieves new evidence during rounds instead of relying on a static pool (+7.5pp accuracy). A role-switching consistency test swaps plaintiff and defense after the primary debate to detect position-anchored reasoning (-4.2pp errors without it). Key finding: LLMs exhibit structural negativity bias — REFUTE positions converge faster. See [agents-subagents game theory reference](../../agents-subagents/references/game-theory-agent-teams.md#8-courtroom-style-progressive-debate-proclaim-pattern) for full protocol.

### Pattern: Pareto-Nash Multi-Objective Synthesis (2025-2026)

When teams optimize for multiple competing objectives (growth vs. monetization vs. retention), map the Pareto frontier: identify all options where no objective can improve without worsening another, remove dominated options (worse on ALL objectives), and present Pareto-optimal choices with explicit tradeoffs. Merges Nash stability with Pareto optimality. See [agents-subagents game theory reference](../../agents-subagents/references/game-theory-agent-teams.md#9-pareto-nash-equilibrium-for-multi-objective-teams).

### Pattern: Evolutionary Coordination Rule Design (AlphaEvolve, DeepMind April 2026)

Use an LLM to iteratively refine coordination rules (belief briefs, debate triggers, synthesis protocols) themselves. Seed with current rules, run team on benchmark, measure quality + cost, propose mutations, keep improvements. Only cost-effective for high-frequency teams where many benchmark runs justify the search cost. See [agents-subagents game theory reference](../../agents-subagents/references/game-theory-agent-teams.md#10-evolutionary-algorithm-design-alphaevolve-pattern).

---

## Decision Checklist

- [ ] Identified which agents interact strategically (shared resources, dependent tasks)
- [ ] Designed for Nash equilibrium — would any agent benefit from deviating?
- [ ] Tested incentive compatibility — does local optimization produce good global outcomes?
- [ ] Chose communication protocol matching information needs (broadcast vs. point-to-point)
- [ ] Resolved resource contention with fair division mechanisms
- [ ] Selected cooperative vs. competitive architecture based on quality requirements
- [ ] Defined output contracts between agents (interface quality guarantees)
- [ ] Built monitoring for undesirable equilibria (deadlock, duplication, starvation)
- [ ] For multi-objective decisions: mapped Pareto frontier instead of single-objective optimization
- [ ] For claim verification: considered courtroom pattern with progressive evidence retrieval
- [ ] For high-frequency teams: considered evolutionary rule optimization
