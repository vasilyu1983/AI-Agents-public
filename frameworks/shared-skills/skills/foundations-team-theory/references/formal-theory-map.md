# Team Theory — Formal Theory Map


Use this file when a task needs source-level justification, production boundaries, or a clean bridge from classical team decision theory to modern subagent orchestration.

## Table of Contents

- [Canonical Stack](#canonical-stack)
- [Primitive-To-Source Map](#primitive-to-source-map)
- [Production Boundary](#production-boundary)
- [Application Layer Status](#application-layer-status)
- [Do Not Overclaim](#do-not-overclaim)

---

## Canonical Stack

| Layer | Primary sources | Use |
|---|---|---|
| Classical team decision theory | Marschak (1955), Radner (1962), Marschak & Radner (1972) | Define shared-payoff agents with partitioned observations and optimal decision rules |
| Non-classical information structures | Witsenhausen (1968), Ho (1980) | Handle action-as-signal regimes where one agent's output changes another's observation |
| Information cost and organization | Sims (2003), Sah & Stiglitz (1986), Radner (1993) | Price observation, communication, hierarchy, and decentralization |
| Sequential decentralized control | Bernstein et al. (2002), Oliehoek & Amato (2016) | Frame stateful multi-agent tasks as Dec-POMDPs |
| Cooperative MARL approximations | QMIX, MAPPO, CTDE literature | Implement approximate policies when exact Dec-POMDP solution is intractable |
| LLM multi-agent failures | Cemri et al. (2025) MAST; May 2026 orchestration-trace and coordination-layer work | Translate formal information structure into practical agent-team design risks |

## Primitive-To-Source Map

| Primitive | Source authority | Production use |
|---|---|---|
| Team Decision Problem | Marschak; Marschak & Radner | Confirm the system is a team before optimizing it as one |
| Information Structure | Radner; Ho | Map who observes what before assigning agents |
| Person-by-Person Optimality | Radner; Marschak & Radner | Detect local-optimum traps in independently tuned agents |
| Value of Communication | Marschak & Radner; information economics | Add channels only when expected payoff lift exceeds cost |
| Radner's LQG Theorem | Radner | Use linear policies only under classical LQG conditions |
| Witsenhausen Counterexample | Witsenhausen | Treat agent-output-as-signal systems as nonlinear and high-risk |
| Information Cost | Sims; Radner | Budget context, tool calls, latency, and review effort |
| Organizational Forms | Sah & Stiglitz; Radner | Choose centralized, decentralized, or hierarchical topology by coupling and cost |
| Dec-POMDP / MARL Extension | Bernstein et al.; Oliehoek & Amato | Model sequential partially observable agent teams |
| Common-Task Condition | Marschak; game-theory boundary | Exit to game theory when payoffs diverge |

## Production Boundary

Use team theory to design information topology and decision rights. Do not treat it as a guarantee that subagents will behave optimally. Production systems still need:

- explicit success metric shared across agents
- per-agent observation matrix and tool-permission map
- communication-channel cost estimates before adding peer chatter
- final aggregation and verification plan
- trace logging for spawn, delegate, communicate, aggregate, and stop decisions
- local evals that compare centralized, decentralized, and hierarchical variants

## Application Layer Status

The stable layer is classical and low-drift. The application layer is high-drift: MAST v3 reports broad system-design, inter-agent misalignment, and task-verification failure classes across 1,600+ traces. May 2026 orchestration-trace work decomposes multi-agent operation into spawn, delegate, communicate, aggregate, and stop decisions; this matches team theory's separation of information structure, channels, and decision rules. Coordination-layer work similarly treats coordination as a configurable architectural layer rather than incidental prompt text.

## Do Not Overclaim

- Do not call divergent incentives a team problem; exit to game theory.
- Do not assume more communication is better; value must exceed cost.
- Do not apply Radner linear-policy results when actions signal to later agents.
- Do not confuse per-agent prompt tuning with team optimality.
- Do not claim Dec-POMDP framing gives an exact production solution; finite-horizon Dec-POMDPs are intractable in worst case.
