# Team Theory Primitives — Overview


Canonical primitive definitions for team-theoretic decision problems. Each entry: definition, inputs, outputs, failure modes, multi-agent application.

For applied patterns and anti-patterns specific to subagent design, see [`patterns-scenarios-traps.md`](patterns-scenarios-traps.md).

## Table of Contents

1. [Team Decision Problem](#1-team-decision-problem)
2. [Information Structure](#2-information-structure)
3. [Person-by-Person Optimality](#3-person-by-person-optimality)
4. [Value of Communication](#4-value-of-communication)
5. [Radner's LQG Theorem](#5-radners-lqg-theorem)
6. [Witsenhausen Counterexample](#6-witsenhausen-counterexample)
7. [Information Cost](#7-information-cost)
8. [Organizational Forms](#8-organizational-forms) (see [8a](#8a-applying-marschakradner-to-real-org-and-agent-design), [8b](#8b-team-size-and-coordination-cost-curve))
9. [Dec-POMDP / MARL Extension](#9-dec-pomdp--marl-extension)
10. [Common-Task Condition](#10-common-task-condition)

---

## 1. Team Decision Problem

**Definition (Marschak 1955).** A team is a tuple `(N, X, A, η, U)`:
- `N` agents indexed `i = 1..n`
- World state `x ∈ X` drawn from prior `p(x)`
- Each agent receives signal `y_i = η_i(x)` (a partition of `X`)
- Each agent picks action `a_i ∈ A_i` based on `y_i` via decision rule `δ_i: y_i → a_i`
- Single shared payoff `U(x, a_1, ..., a_n)`

**The team problem**: choose decision rules `(δ_1, ..., δ_n)` to maximize `E[U]`.

**Inputs**: agent set, observation partitions, action sets, joint payoff function, prior.

**Outputs**: decision rules per agent.

**Why it matters for subagents**: this is the formal model for "shared-goal multi-agent system." Game theory assumes per-agent payoffs `U_i`; team theory collapses them to one `U`. Most LLM agent teams are team-theoretic, not game-theoretic — they share an outcome metric.

**Failure modes**:
- Modeling the team as a single super-agent (loses the partition structure that makes decentralization valuable)
- Modeling the team as strategic players (overstates conflict, adds incentive-compatibility overhead that isn't needed)

---

## 2. Information Structure

**Definition.** The collection of observation partitions `{η_1, ..., η_n}` describing what each agent sees. Five canonical types:

| Type | Description | Subagent example |
|---|---|---|
| Centralized | One agent observes everything; others observe nothing | Orchestrator reads all files, dispatches summaries |
| Decentralized (static) | Each agent observes a disjoint slice; no agent sees what others see | Parallel reviewers each on a different file |
| Partial | Agents have overlapping but not identical views | Two researchers querying the same source with different prompts |
| Nested | Agent `i+1` observes everything agent `i` observed plus more | Hierarchical chain: planner → architect → implementer |
| Non-classical | An agent's action affects another agent's observation | Subagent A writes a note that subagent B reads (signaling) |

**Why it matters**: most multi-agent design errors trace to an unexamined information structure. Naming the type (especially "non-classical") changes which solution methods are valid.

**Human team analog — Transactive Memory Systems (TMS):** In human teams, the information structure corresponds to a *transactive memory system* (Wegner 1987): each member specializes in different knowledge domains and the group maintains a shared directory of "who knows what." TMS is explicitly *differentiated* (not shared), making it the direct human-team analog to the formal `η` partition. Three measurable dimensions of a functioning TMS: specialization (each member owns distinct knowledge), credibility (members trust each other's domain knowledge), and coordination (members can retrieve from each other without redundant encoding). Brandon & Hollingshead (2004, Organization Science 15(6)) establish that task structure is a primary developmental influence on TMS. For subagent design, this maps to: (a) assign each agent a disjoint observation lane, (b) build a "who-knows-what" directory at the orchestrator level, (c) route queries to the agent whose lane covers the domain. Narayanan et al. (2025, Human Factors) extends TMS to human-AI teams, confirming the construct applies when AI takes a specialist role.

**Failure modes**:
- Assumed information structure differs from actual (e.g., hidden global state agents implicitly read)
- Non-classical structure treated as classical → linear policies look optimal but aren't (see #6)

---

## 3. Person-by-Person Optimality

**Definition.** A decision rule profile `(δ_1*, ..., δ_n*)` is *person-by-person optimal* (PBPO) if no single agent can improve `E[U]` by changing only their rule, holding all others fixed.

**Key result**: team-optimum implies PBPO. **The reverse does not hold** — PBPO is only a necessary condition. Multiple PBPO equilibria can exist, and joint deviations can dominate any of them.

**Why it matters**: "each subagent doing its best given the others" is *not* a guarantee of optimality. Subagent teams routinely sit at PBPO points that are dominated by joint policy changes.

**Diagnostic**: hold all agent rules fixed except two; vary that pair jointly. If you find a higher `E[U]`, you were at a PBPO that wasn't the team optimum.

**Failure modes**:
- Local prompt-tuning that achieves PBPO but ignores joint redesign
- "Each agent is doing its best" used as evidence of system optimality

---

## 4. Value of Communication

**Definition.** For two information structures `η` (without channel) and `η'` (with channel `c`), value of communication is `V(c) = max E[U | η'] − max E[U | η]`. Adopt the channel iff `V(c) > cost(c)`.

**Inputs**: payoff structure, prior, observation partitions before/after, channel cost (latency, tokens, ops complexity).

**Outputs**: keep/drop decision; channel sizing.

**Why it matters**: subagent designs accrete communication channels by default. Each channel that doesn't pay for itself in expected payoff is dead weight that also adds inter-agent misalignment and coordination failure surface.

**Worked example**: a planner agent and an executor agent. Channel A: planner shares full plan with executor each step (high token cost). Channel B: planner shares only next-step instruction (low cost). Compute expected payoff under both. If executor doesn't actually condition on plan-beyond-next-step, V(A) − V(B) ≈ 0 and channel A loses on cost.

**Failure modes**:
- Adding observability/comms "in case it's useful" with no payoff calculation
- Conflating value of information (decision-theoretic, single agent) with value of communication (team-theoretic, between agents)

---

## 5. Radner's LQG Theorem

**Theorem (Radner 1962).** For a team with linear dynamics, quadratic payoff, and Gaussian information, the team-optimal decision rules are *linear* in each agent's observation, and the optimum is computable in closed form.

**Inputs**: linear state dynamics, quadratic-form payoff `U = -(x − Ka)' Q (x − Ka)`, Gaussian noise on observations.

**Outputs**: closed-form linear decision rules `δ_i(y_i) = L_i y_i + c_i`.

**Why it matters**: LQG teams are the *only* canonical class with closed-form team optima. They're the upper-bound benchmark and the right starting point for any team where payoff is approximately quadratic-in-error.

**Limits**: depends on classical information structure (no signaling between agents). When that fails, see #6.

**Failure modes**:
- Re-deriving optimization for problems that fit Radner conditions
- Applying LQG structure to obviously-non-LQG problems (categorical actions, discrete observations) and getting away with it because the linearity is "close enough" — until it isn't

---

## 6. Witsenhausen Counterexample

**Result (Witsenhausen 1968).** A simple two-stage LQG team with non-classical information structure (agent 1's action observed by agent 2) has a *nonlinear* optimal policy that strictly dominates any linear policy.

**Why it matters**: this is the exact regime where one subagent's output becomes another's input. Any "the planner writes; the executor reads" pattern is non-classical. Linear/affine extrapolation of Radner's theorem fails here. Decades later, the exact optimum is still unknown — this is a hard problem.

**Practical takeaway**: when one agent signals to another (via shared scratchpad, message, or written artifact), expect:
- Optimal policies to be nonlinear
- Local search (gradient methods) to get stuck in poor minima
- "Just give them a comms channel" to underperform careful policy design

**Failure modes**:
- Assuming linear policies are optimal in any team where signaling exists
- Treating the problem as if more communication monotonically improves payoff — Witsenhausen's setting shows this is false

---

## 7. Information Cost

**Definition.** Each observation `y_i` has a cost `κ_i(y_i)` — latency, tokens, money, attention. Effective payoff is `E[U] − Σ κ_i`.

**Why it matters**: in classical team theory, information was free; in real systems it isn't. Modern restatements (rational-inattention, Sims 2003) make this explicit. For subagents, every tool call, file read, or context entry has a token cost; observations must justify themselves.

**Diagnostic**: marginal payoff per marginal token spent on observation should be monotonically decreasing across the agent's observation budget. If it isn't, either trim cheap-but-low-payoff observations or invest in more expensive-but-high-payoff ones.

**Failure modes**:
- Treating subagent context as free
- Loading every file "in case the agent needs it" — observation cost paid up front, payoff often zero
- Confusing "more context = better answers" with the actual relationship (which has diminishing returns and eventually inverts)

---

## 8. Organizational Forms

**Definition.** Higher-level structure that bundles information structure + communication topology + decision rights:

- **Centralized**: one agent observes-and-decides; others execute. Cheap when info is cheap and coupling is high.
- **Decentralized (polyarchy)**: agents observe and decide locally; aggregation only at the end. Cheap when info is expensive and coupling is low.
- **Hierarchical**: tree structure; each level summarizes for the next. Compromise; loses some bottom-up signal.
- **Market / mechanism**: agents bid for tasks via a price signal. Crosses into game theory when payoffs diverge.

**Choice rule** (Sah and Stiglitz 1986; Radner 1993):
- High information cost + low coupling → decentralized
- Low information cost + high coupling → centralized
- Mixed → hierarchical, with the partition matching the coupling structure

**Why it matters**: the orchestrator-led pattern is the default in LLM agent design, but it isn't always optimal. When tasks are independent (low coupling), decentralized swarms with end-stage aggregation match centralized payoff at lower cost.

**Failure modes**:
- Defaulting to orchestrator-led without checking the coupling and cost regime
- Hierarchical chains that strip too much signal at each summarization step

### 8a. Applying Marschak–Radner to Real Org and Agent Design

The formal apparatus (#1–#8) reduces, in practice, to one recurring judgment call: **for this decision, does the cost of moving information to a central point exceed the cost of moving the decision right to where the information already sits?** Two failure directions are equally common and equally expensive:

- **Over-centralizing**: routing a decision upward past the person/agent who already holds the decisive signal. The center pays the observation cost (#7) of absorbing detail it will use once, and the decision is delayed by the round-trip.
- **Over-decentralizing**: letting each local holder of information decide alone when their actions are coupled (#6) or when consistency across decisions has its own payoff term (e.g., pricing, brand, compliance) that no single local decision-maker internalizes.

**A practical four-question test** (grounded in #2, #6, #7, #8; not a formal theorem — a decision heuristic):

1. **Who has the decisive information, and can it be cheaply summarized?** If the local signal compresses well (a number, a flag, a short judgment) without losing what the center needs, centralizing is cheap — do it. If the signal is high-dimensional, tacit, or time-decaying (it's stale by the time it's reported up), decentralize the decision to where the signal lives.
2. **Is the decision reversible?** Low-reversibility decisions (pricing architecture, a compliance stance, an irreversible spend) have payoff terms that reward consistency and deliberation — this pushes toward centralizing even at real observation cost. High-reversibility decisions (a subagent's tool choice, a regional promotion, a draft's phrasing) are cheap to get locally wrong and correct later — decentralize.
3. **Are the actions coupled (#6)?** If one decision-maker's action changes what another should do (signaling, shared inventory, shared reputation), classical independent-decentralization breaks down; either centralize the coupled subset or design an explicit nonlinear coordination policy (not "add a status channel and hope").
4. **What does a wrong local decision cost the rest of the system relative to what a wrong central decision costs?** If local errors stay local (independent files, independent regional markets), decentralize. If a local error propagates system-wide (a shared schema, a shared brand promise, a shared customer relationship), centralize the parts that touch the shared surface and decentralize the rest.

**Applied to human orgs**: this is the same logic Sah & Stiglitz (1986) and Radner (1993) formalize as hierarchy-vs-polyarchy — and it is why real organizations centralize finance/legal/brand (low reversibility, high cross-decision coupling, cheap-to-summarize signals) while decentralizing field sales pricing exceptions, local hiring, and day-to-day engineering implementation (high-dimensional local signal, high reversibility, low cross-decision coupling). The common mistake is applying one answer org-wide ("we are a centralized company" / "we are a decentralized company") instead of applying the test decision-by-decision.

**Applied to agent orchestration**: identical structure — centralize the parts of the task with shared state or brand/consistency payoff (final answer synthesis, safety checks, shared schema decisions); decentralize the parts with disjoint, cheaply-verified local signal (independent file reviews, independent source lookups). See the Composition Recipes below for worked examples.

### 8b. Team-Size and Coordination-Cost Curve

Team theory prices *observation and communication*, not headcount directly — but headcount determines the number of pairwise (or higher-order) channels that can carry a cost, which is why team size interacts with #7 and #8 so strongly in practice.

**The mechanism**: if every pair of agents/members has a potential coordination channel, the number of pairwise links grows as `n(n−1)/2` — quadratic in team size. This is the same structural point Fred Brooks made about human engineering teams in *The Mythical Man-Month* (1975): adding people to a late project adds communication paths faster than it adds working hands, so the project gets later, not sooner. Team theory gives this the formal frame: each additional pairwise channel must clear the value-of-communication test (#4) on its own, and in a densely-linked team most of those channels are not worth their cost — which is exactly the empirical finding for LLM multi-agent topologies (see the "moderately sparse beats dense" anti-pattern below, Shen et al. 2025).

**Practical reading of the curve, not a precise formula** — team-optimal size depends on task coupling, not a universal number:
- **Low coupling, cheap aggregation** (independent subtasks, disjoint files/regions): near-linear scaling is achievable because the *effective* communication graph stays sparse regardless of `n` — most pairs never need to talk. This is why split-and-merge patterns and large sales/support orgs can scale headcount with only sub-quadratic coordination cost.
- **High coupling** (shared state, shared interface, tight sequential dependency): coordination cost grows toward the full quadratic curve, and beyond some team size the marginal member's *contribution* is smaller than the coordination cost they add — the point Brooks's Law describes as "later." The fix is not "add fewer people" in the abstract; it is to cut the coupling (modularize the shared state, add a single decision owner for the shared interface) so the *effective* graph sparsifies even as headcount grows.
- **Rule of thumb for both human and agent teams**: before adding the Nth member/agent, ask which existing members it must coordinate with (not "could," "must" — #4). If the answer is "most of them," you are on the steep part of the curve and should restructure (hierarchy, ownership split, sparser topology) rather than add capacity. If the answer is "one or two," near-linear scaling is still available.

**Failure modes**:
- Treating team size as a free scaling knob because "more hands / more agents" feels additive — it is additive only when coupling is low
- Solving a coordination-cost problem by adding a coordinator role without first cutting coupling — this centralizes the cost rather than removing it
- Applying a fixed "ideal team size" number (e.g., "7±2," "two-pizza team") across tasks with different coupling structures — the right size is a function of coupling and information cost, not a constant

---

## 9. Dec-POMDP / MARL Extension

**Definition.** A *Decentralized Partially Observable MDP* extends the team decision problem to sequential decisions with state dynamics:
- State `s_t` evolves under joint actions `(a_1,t, ..., a_n,t)`
- Each agent receives observation `o_i,t = O_i(s_t)`
- Agents pick actions to maximize `E[Σ_t γ^t r(s_t, a_t)]`

**Complexity result** (Bernstein et al. 2002): finite-horizon Dec-POMDP is **NEXP-complete** — intractable in worst case. Approximation methods (centralized training with decentralized execution, MAPPO, QMIX, MADDPG) drive modern multi-agent RL.

**Why it matters**: if the subagent problem has state across steps (not just one-shot dispatch + aggregate), Dec-POMDP is the right computational frame. Most production agent teams approximate this badly — by treating each step as fresh, they discard learnable state.

**Failure modes**:
- Memorylessness assumed without justification
- Centralized-training-decentralized-execution mixed up at runtime (training-time information leakage into "decentralized" rules)

---

## 10. Common-Task Condition

**Definition.** A multi-agent system is a *team* iff all agents share a single payoff `U`. If agents have distinct payoffs `U_i`, it is a game.

**Why it matters**: this is the boundary condition that decides which foundation to use. Team theory is much simpler than game theory because incentive compatibility is free — agents *want* to maximize the joint payoff.

**Practical heuristic**: ask "does each agent succeed only if the team succeeds?" If yes, team. If an agent can succeed while the team fails (or vice versa), it's a game.

**Subagent regime**: most LLM subagent teams are *nominally* team problems — all agents share the user's goal — but **incentive divergence creeps in** when:
- Subagents are trained on different objectives (RLHF reward differs from team payoff)
- One subagent is incentivized for verbosity / completeness while another is for brevity
- Subagents from different vendors with different alignment objectives are mixed

When divergence is real, exit to [foundations-game-theory](../../foundations-game-theory/SKILL.md) and add mechanism design.

**Failure modes**:
- Calling a system a "team" when payoffs actually diverge
- Calling a system a "game" when payoffs are aligned, and then over-engineering with mechanism design
