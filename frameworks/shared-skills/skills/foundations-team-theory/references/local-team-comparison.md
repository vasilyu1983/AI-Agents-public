# Local Team and Information-Structure Comparison

## Design record

Specify shared payoff, task population, agent capabilities, per-agent observation sets, tool/authority boundaries, dependencies, aggregator, communication channels and total token/latency/money budget. Distinguish human survey evidence from agent telemetry.

Classify the information sets before invoking a theorem. Action-dependent observations alone do not establish a non-classical structure; check whether a later decision-maker has the information available to the earlier decision-maker whose action affects it (partial nestedness). Static convex Gaussian/quadratic results do not automatically apply to categorical LLM actions.

## Comparison protocol

1. Freeze task population, outcome and practical decision threshold.
2. Include the strongest single-agent candidate with the same tools and total budget.
3. Compare feasible centralized, decentralized and dependency-preserving sparse/dense candidates; select candidates from actual coupling, not a universal sparsity threshold.
4. Hold useful work and total resources comparable; count tool observations, peer communication, aggregation, verification and retries.
5. Test aggregation competence-weighting, correlated failures and planted bad contributions; competence signals must be measured independently of the final answer.
6. Ablate optional channels and compare quality, critical failures, latency and cost with uncertainty. Predeclare escalation, termination and failed-agent handling.
7. Report conditional winner or insufficient evidence; do not claim a global team optimum from a few pairwise policy variations.

Latent exchange is a specialized candidate only when embeddings are accessible and representations compatible. A hosted heterogeneous-agent team need not have that capability. Structured text/artifacts with verification are viable alternatives.

With optional costless information and an unrestricted policy set that preserves old policies, optimal payoff cannot decrease: information may be ignored. Costs, bounded contexts, compulsory messages and heuristic behavior can reduce realized performance. Witsenhausen concerns nonlinear-policy advantages in a specific non-classical problem, not a general rejection of information monotonicity.

## Minimal deliverable

Return observation/authority matrix, classified assumptions, feasible topology candidates, best-single-agent baseline, matched-budget result, aggregation/communication ablations, correlated failures, escalation/stop policy and uncertainty. Do not infer that human oversight is unnecessary solely because it does not improve predictive accuracy.

## Regression checks

- Planner-to-executor text alone does not prove non-classical structure.
- Optional free information can be ignored when old policies remain feasible.
- No universal embedding, moderate-sparsity, four-agent or video-first requirement.
- O(1) work per agent does not imply O(1) total system cost.
- Westrum self-report does not become LLM telemetry.

## Primary sources

- [Ho & Chu (1972)](https://doi.org/10.1109/TAC.1972.1099850), “Team Decision Theory and Information Structures in Optimal Control Problems—Part I”: partially nested information structures.
- Radner (1962), “Team Decision Problems”: convex/team-policy assumptions matter.
- Witsenhausen (1968), “A Counterexample in Stochastic Optimum Control”: linear policies need not be optimal in the specified non-classical problem.
- [LatentMAS (preprint)](https://arxiv.org/abs/2511.20639): specialized latent architecture; validate compatibility and reported conditions locally.

## Why limited deviations cannot certify a team optimum

Exact counterexample: three agents choose binary actions with shared payoff 1 only at `111`, otherwise 0. At `000`, neither a unilateral nor a pairwise change improves payoff, yet the three-agent change to `111` does. Failure to find a one- or two-policy improvement therefore cannot certify global optimality. Finding a pairwise improvement disproves global optimality, but does not establish that unilateral optimality held before the change. Report searched deviations and the best evaluated policy, unless a complete finite search or applicable theorem supplies a real certificate.
