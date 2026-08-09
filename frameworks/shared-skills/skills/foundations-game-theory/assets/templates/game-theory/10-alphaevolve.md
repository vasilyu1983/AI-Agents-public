# Mechanism: Evolutionary Coordination Search

**Sources**:
- AlphaEvolve (DeepMind, [2506.13131](https://arxiv.org/abs/2506.13131)) is the general evolutionary coding-agent baseline.
- Discovering Multiagent Learning Algorithms with Large Language Models ([2602.16928](https://arxiv.org/abs/2602.16928)) applies AlphaEvolve to game-theoretic MARL and discovers **VAD-CFR** and **SHOR-PSRO** variants. Treat the April 2026 commentary around this result as secondary; use the arXiv paper for primary claims.
- ShinkaEvolve (Sakana AI, [2509.19349](https://arxiv.org/html/2509.19349v1), ICLR 2026). Sample-efficient alternative — order-of-magnitude fewer LLM calls than AlphaEvolve via parent-sampling, code-novelty rejection, and bandit-based ensemble selection.
- CodeEvolve (open-source, [2510.14150](https://arxiv.org/html/2510.14150v1)). Island-based GA with inspiration-based crossover; surpasses AlphaEvolve on several mathematical benchmarks.

**Source posture**: Evolutionary search applied to team coordination is the durable concept; specific frameworks evolve quickly. Do not present this template as proof that a team will outperform expert baselines.

## Domain Applications

- **Algorithm selection for recurring pipelines**: evolve routing/scoring rules against a measurable quality metric over many runs; use ShinkaEvolve when LLM call budget is constrained.
- **Prompt optimization for high-frequency systems**: treat prompt as a program to mutate; fitness = task performance on held-out eval set; LLM proposes mutations, evaluator scores.
- **Pricing rule evolution**: evolve the pricing algorithm against a revenue + retention composite fitness signal across historical data; ShinkaEvolve for sample efficiency.
- **Agent team coordination rule tuning**: evolve which mechanisms to apply (belief briefs, debate triggers, synthesis protocol) against team quality metrics; use only when team has 50+ measurable runs.

## Problem

Hand-designed coordination rules (task routing, debate rules, synthesis protocols) may not fit a repeated workflow. The design space is too large for manual exploration once the team runs frequently.

## Concept

Use an LLM to iteratively refine the coordination rules themselves:

```
Seed: current team manifest coordination rules
Loop:
  1. Run team on benchmark task set
  2. Measure: output quality, token cost, member utilization, debate efficiency
  3. LLM proposes mutations to coordination rules (belief briefs, debate triggers, synthesis protocol)
  4. Run mutated rules on same benchmark
  5. Keep if better on Pareto frontier (quality + cost)
  6. Repeat for N generations

Output: evolved coordination rules tailored to the specific team composition
```

## Practical Application

This is expensive (many runs per generation) and only worth it for high-frequency teams. Candidates:

- `startup-growth-board` — runs frequently, clear quality metrics
- `software-code-review-board` — high volume, measurable output (issues found vs. false positives)
- `dev-feature-delivery` — daily use, clear success criteria (task completion, review pass rate)

For infrequent teams, hand-tuned rules remain more cost-effective.

## Framework Selection (April 2026)

| Framework | When to pick |
|---|---|
| **AlphaEvolve** | High-budget runs; frontier-quality results matter more than per-call cost; access to Gemini Pro/Flash ensemble |
| **ShinkaEvolve** | Sample efficiency matters; budget for hundreds of evaluations not millions; ICLR 2026 sample-efficiency techniques (parent sampling + novelty rejection + bandit ensemble) |
| **CodeEvolve** | Open-source requirement; mathematical/algorithmic benchmarks; want the island-based diversity for exploration breadth |

For agent-team coordination evolution specifically (not algorithm discovery), ShinkaEvolve's sample efficiency is usually the right starting point — coordination-rule benchmarks rarely justify AlphaEvolve's evaluation budget.

## When NOT To Use

- Teams that run a few times a month — hand-tuning is cheaper
- Teams without an objective quality metric — evolution needs a fitness signal
- Pre-launch teams without a benchmark task set — evolve only after baseline data exists

## Related

- [`09-pareto-nash.md`](09-pareto-nash.md) — Pareto-frontier criterion for selecting evolved variants
- [`04-shapley-contribution.md`](04-shapley-contribution.md) — quality signal for the fitness function
