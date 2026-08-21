# AI Planning And Search Primitives Overview

## Contents

- [1. Problem Formulation](#1-problem-formulation)
- [2. Uninformed Search](#2-uninformed-search)
- [3. Heuristic Search](#3-heuristic-search)
- [4. Local Search](#4-local-search)
- [5. Constraint Satisfaction](#5-constraint-satisfaction)
- [6. Adversarial Search](#6-adversarial-search)
- [7. Classical Planning](#7-classical-planning)
- [8. Hierarchical Planning](#8-hierarchical-planning)
- [9. Contingent And Belief-State Planning](#9-contingent-and-belief-state-planning)
- [10. Planner-Agent Integration](#10-planner-agent-integration)

## 1. Problem Formulation

Define the search problem before choosing an algorithm:

- initial state
- legal actions
- transition model
- goal test
- path cost

For agentic systems, also define percepts, sensors, tools/actions, observability, determinism, time horizon, and whether other actors are cooperative, adversarial, or irrelevant.

## 2. Uninformed Search

Use BFS, DFS, depth-limited search, iterative deepening, or uniform-cost search when no reliable heuristic exists. Track completeness, optimality, memory, and branching factor explicitly.

## 3. Heuristic Search

Use greedy best-first search, A*, weighted A*, beam search, or IDA* when a heuristic can guide exploration. A* optimality depends on admissible/consistent heuristics and nonnegative step costs.

**2025 note — LLM-generated heuristics**: an LLM asked to generate several domain-dependent heuristic functions as Python code, evaluated within a greedy best-first search and selected by training-task performance, solved more unseen test tasks than state-of-the-art domain-independent heuristics for classical planning — using an unoptimized Python planner against highly optimized C++ baselines (Corrêa, Pereira & Seipp, arXiv:2503.18809, 2025). This is a search-and-select process over LLM output, not a guarantee: verify admissibility empirically before claiming A* optimality, and treat LLM-generated heuristics as inadmissible by default (use weighted A* or beam search instead).

## 4. Local Search

Use hill climbing, simulated annealing, local beam search, or genetic/evolutionary search when the path does not matter and the state space is too large for full frontier search.

## 5. Constraint Satisfaction

Model variables, domains, and constraints separately from objectives. Use backtracking, forward checking, arc consistency, MRV/LCV ordering, and CP-SAT/constraint solvers when constraints should be executable.

## 6. Adversarial Search

Use minimax, alpha-beta pruning, expectimax, or Monte Carlo Tree Search for finite game trees or simulations where another actor's moves shape outcomes.

Route mechanism design, negotiation, auctions, and equilibrium analysis to `foundations-game-theory`.

**MCTS/UCT mechanics, stated precisely**: MCTS builds a tree incrementally through four steps per iteration — selection (walk down the tree via a tree policy), expansion (add one or more child nodes), simulation/rollout (estimate value from the new node, by random or learned rollout policy), and backpropagation (update visit counts and value estimates up the path). The standard tree policy is UCT (Kocsis & Szepesvári, 2006), which at each node picks the child maximizing `Q(s,a) + c * sqrt(ln(N(s)) / N(s,a))` — exploiting the highest mean value while an exploration bonus favors under-visited children; `c` trades exploration against exploitation and has no universally correct value, so treat it as a tuned hyperparameter, not a constant to copy from a paper. MCTS converges to the optimal action given unbounded simulations and a rollout policy correlated with true value; with a bad rollout/evaluation policy or too few simulations it can be confidently wrong, which is why production deployments should log visit-count distributions, not just the argmax action, to catch cases where the tree never had enough budget to separate top candidates.

**Test-time search over LLM reasoning/action traces**: MCTS is also applied without an adversary, as an inference-time scaling method — rolling out multiple candidate reasoning or tool-call trajectories, scoring them (self-evaluation, a verifier model, or execution feedback), and backing up value estimates to pick the next step (Language Agent Tree Search / Tree-of-Thoughts-style patterns). This is a real cost tradeoff, not a free accuracy gain: each rollout multiplies token and latency cost, and the scoring signal is a heuristic, not a ground-truth reward, so treat it like #3's inadmissible-heuristic warning — verify the scorer's reliability before trusting the tree's argmax. Reserve it for tasks where a single-pass answer is unreliable and a verifier/execution signal is cheap relative to being wrong (code with a test harness, math with a checker); do not reach for it as a default agent loop.

Three refinements from the 2025–2026 work on this, in the order they usually matter:

- **The verifier is the load-bearing part, not the tree.** Reported gains from MCTS over LLM reasoning are consistently conditional on being paired with a verifier or process reward model; without a reliable scorer, extra rollouts buy confidence rather than correctness. Budget verifier quality before budgeting search width.
- **Budget is a first-class parameter.** Naive MCTS spends its rollouts unevenly and scales poorly against a fixed token budget. Bandit-style allocation schemes — sequential halving and Gumbel-based selection over candidate actions — are designed to distribute a fixed budget across candidates rather than let the tree policy decide how much total compute to consume. If you have a hard per-request token or latency ceiling, choose a method that takes that ceiling as input.
- **Trees are cheaper than independent trajectories.** Agent rollouts are long and multi-turn, so branching from shared prefixes yields more distinct trajectories per unit of compute than sampling independent ones, and the tree structure additionally yields step-level signal from an outcome-only reward (the Tree-GRPO result, Ji et al., arXiv:2509.21240, ICLR 2026). This is a training-time argument but the prefix-sharing economics apply equally at inference time.

## 7. Classical Planning

Use symbolic action models when preconditions and effects determine whether a plan is valid. STRIPS/PDDL-style domains separate operator definitions from problem instances.

**LLM as formalizer, not planner**: the more reliable division of labour is to use the LLM to *write or repair the formal model* — translating natural-language domain descriptions into PDDL operators and problem instances — and then hand the result to an off-the-shelf sound planner, rather than asking the LLM to emit the plan itself. This is the organizing thesis of the LLMs-as-planning-formalizers literature (Tantakoun, Zhu & Muise, arXiv:2503.18971, survey, 2025). It relocates the LLM's error mode from "invalid plan that reads well" to "wrong domain model," which is the better failure to have: a wrong domain model is inspectable, testable against known instances, and fixed once, whereas an invalid plan must be caught on every request. Validate generated PDDL for both syntax and semantics — syntactic well-formedness does not imply the domain means what the description said.

**Benchmark reality check**: direct prompting of state-of-the-art models with PDDL domain and problem files remains competent on simple instances and unreliable on complex ones, with the specific weaknesses being resource management, consistent state tracking, and strict constraint compliance; the recommendation from that work is hybrid LLM-plus-classical-planner architectures rather than replacement (Goebel & Zips, arXiv:2507.23589, 2025). Treat "can the model just plan this" as a question to be answered empirically per domain, not by model generation.

**Validity is not safety.** These are independent axes and they have been measured to diverge sharply. On DESPITE, a 12,279-task embodied-planning benchmark covering physical and normative dangers, the best-planning model failed to produce a valid plan on only 0.4 % of tasks yet produced dangerous plans on 28.3 % of them; across open-source models from 3B to 671B, planning ability scaled from 0.4 % to 99.3 % while safety awareness stayed roughly flat at 38–57 % (Zhang, Qu, Li, Wu, Hutter, Li & Shi, arXiv:2604.18463, 2026). The design consequence: scaling the planner, or improving its success rate, does not buy safety. A permission/safety gate over the action set is a separate component with its own tests, and it belongs outside the planner's own success metric.

## 8. Hierarchical Planning

Use HTN-style methods when task decomposition is reusable and domain-specific. HTN planning is useful for operational workflows where "how to do task X" is stable and can be encoded.

## 9. Contingent And Belief-State Planning

Use contingent plans or belief-state policies when observations are incomplete or actions have nondeterministic effects. If probabilities, utilities, or value of information dominate the choice, route to `foundations-decision-theory`.

## 10. Planner-Agent Integration

Use an LLM for language-heavy goal interpretation, abstraction, or explanation. Use a planner or verifier for legal actions, preconditions/effects, constraint satisfaction, and plan validity. Keep replanning triggers explicit: failed precondition, new observation, external state drift, budget exhaustion, or changed goal.

**Generate-critique-repair loop (LLM-Modulo shape)**: the durable architecture from this literature is an LLM generator wrapped in a bank of *sound* external verifiers — syntax, precondition/effect replay, domain-specific constraint checks — where a failing check re-prompts the generator with the specific violation rather than a generic "try again" (Kambhampati et al., ICML 2024 position paper; extended in arXiv:2411.14484, 2024). Two properties make or break it: the verifiers must be sound (a verifier that passes bad plans converts the loop into laundering), and the feedback must name the violated condition, since undirected retries mostly resample the same error. Bound the loop with a maximum round count and a defined give-up path; unbounded critique loops are a latency and cost failure mode, and a plan that has not converged after several targeted critiques usually indicates a domain-model error, not a sampling error.

**Where the plan lives**: in long-horizon production agents the plan is increasingly externalized — written to a file or a structured task list the executor reads and updates — rather than held in the model's context window. This makes the plan inspectable, diffable, and survivable across context compaction, and it lets progress be checked against an artifact instead of re-derived from conversation history. The planning theory is unchanged; what changes is that state and goal tracking stop degrading as the session grows. Pair it with the same explicit replanning triggers above.

**Cost-shaping the orchestrator**: when a verifier-guided repair loop is already producing certified-correct trajectories, those trajectories are supervision. Distilling the orchestration policy — which repair action to apply in which state — into a small fine-tuned model has been reported to match frontier-model orchestration quality on PDDL repair at roughly two orders of magnitude lower cost per task and 40–50 % fewer LLM calls (Mangannavar, Coalson, Dugar & Tadepalli, arXiv:2606.21740, 2026). Treat this as a maturity-stage optimization, not a starting architecture: it presupposes you already have a sound verifier and enough accepted trajectories to train on.

**Build-vs-skip threshold**: a full symbolic planner (PDDL domain, Fast Downward or similar) earns its cost when action sequences are long (roughly 5+ steps), branching is combinatorial, or preconditions interact in ways a human reviewer would miss. Below that, cheaper structure often suffices: typed function-call schemas with precondition checks in code, or a single verifier pass that replays proposed actions against current state before execution. Do not stand up a PDDL pipeline to gate 2-3 independent, idempotent tool calls; do rely on one when a wrong action order is costly (irreversible side effects, spend, data loss) or when the domain has recurring structure worth encoding once.

**2026 note — MCP-exposed PDDL simulators**: agentic LLM planning via step-wise PDDL simulation through an MCP interface (PyPDDLEngine) lets the LLM act as an interactive search policy — select one action, observe resulting state, reset and retry. On Blocksworld, this raised success from 63.7 % (direct LLM planning) to 66.7 % (agentic, step-wise), at 5.7x token cost — but classical Fast Downward still solved 85.3 % of the same instances (Göbel, Lorang, Zips & Glück, arXiv:2603.06064, 2026). Read this as evidence that a symbolic planner remains the stronger default whenever one is available; only fall back to agentic LLM-as-search-policy when no PDDL solver can be invoked directly, and even then keep expectations calibrated to the gap versus Fast Downward, not versus direct LLM planning. The authors attribute the agentic gain to the value of grounded step-wise feedback, not to the LLM's own search competence — token cost buys marginal accuracy, not planner-grade reliability.
