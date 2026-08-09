# AI Agent Reliability — Reference


Extension of the foundations-reliability-theory primitives for stochastic LLM/AI agent systems. Load this reference when the system under analysis is an LLM agent, multi-step tool chain, or autonomous agent pipeline — not a hardware component or a traditional cloud service with stationary failure rates.

## Table of Contents

- [Why Classic MTBF Does Not Transfer Cleanly](#why-classic-mtbf-does-not-transfer-cleanly)
- [Core Vocabulary](#core-vocabulary)
- [Markov Chain Step-Reliability](#markov-chain-step-reliability)
- [Agent FMEA — Failure Modes Specific to LLM Agents](#agent-fmea--failure-modes-specific-to-llm-agents)
- [Decision Additions for AI/Agent Systems](#decision-additions-for-aiagent-systems)
- [Sources](#sources)

---

## Why Classic MTBF Does Not Transfer Cleanly

Classic MTBF (primitive 01) assumes a **stationary failure process**: the probability of failure per unit time is constant in the CFR phase. AI agents violate this assumption in two ways:

1. **Run-to-run stochasticity**: the same prompt with the same inputs can succeed or fail on different runs due to sampling temperature, model nondeterminism, and context sensitivity. There is no "time-between-failures" — each run is an independent Bernoulli trial with a task-specific success probability.

2. **Duration-dependent degradation**: agent success probability is not constant across task lengths. Longer tasks accumulate more opportunities for tool-call failures, context window saturation, and error propagation. Pass@1 on a 2-step task does not predict pass@1 on a 20-step task.

These two violations mean that "availability" and "MTBF" require adaptation before they apply to AI agents.

---

## Core Vocabulary

### pass@1 vs pass^k

| Metric | Definition | Limitation |
|--------|-----------|------------|
| **pass@1** | Single-run success rate | Does not capture consistency; a model can achieve 90% pass@1 while having highly variable behaviour — some runs succeed, others fail on the same task |
| **pass^k** | All k runs succeed (conjunction) | Consistency metric; threshold: k ≥ 10 runs. A system with pass@1 = 0.90 has pass^10 = 0.90^10 ≈ 0.35 — far lower than pass@1 suggests |

**Practical threshold**: treat pass^10 < 0.80 as a reliability red flag regardless of pass@1. (Gupta 2026 found perturbations dropped pass@1 from 96.9% to 88.1% — pass^k would diverge further.)

### Reliability Decay Curve (RDC)

The RDC plots pass@1 as a function of task duration (number of steps, tokens, or tool calls). For most current LLM agents, pass@1 decays as duration grows — the relationship is approximately exponential in the number of steps when steps are independent.

**Variance Amplification Factor (VAF)**: measures how duration amplifies variance across runs. A system with high VAF becomes unpredictable at longer horizons even if pass@1 looks acceptable on short tasks.

Source: Khanal et al. (2026), arXiv:2603.29231 — 396 tasks, 23,392 episodes, 10 models.

### Graceful Degradation Score (GDS) and Meltdown Onset Point (MOP)

- **GDS**: measures continuity of performance decline — a system that degrades smoothly is operationally preferable to one that catastrophically collapses.
- **MOP**: the task-duration point at which entropy-based behavioral collapse begins. Useful for setting maximum-task-length guardrails in production agents.

Both are author-coined metrics from arXiv:2603.29231 with single-paper pedigree. Treat as useful diagnostic framing, not established standards.

---

## Markov Chain Step-Reliability

For a sequential agent with N tool calls or steps, each with independent per-step reliability rᵢ, system reliability composes as:

```
R_system = r₁ × r₂ × ... × rN = ∏ rᵢ
```

This is the series reliability formula from primitive 10, applied per-step rather than per-component.

**TraceToChain methodology** (Tran-Truong & Le 2026, arXiv:2604.24579): fits agent execution traces to absorbing Markov chains using:
- Laplace-smoothed maximum-likelihood estimation for transition probabilities
- AIC + Kolmogorov-Smirnov goodness-of-fit validation
- Dirichlet-posterior credible intervals with bootstrap validation

Key finding: pass@k, pass^k, and RDC are all projections of a single success-time distribution — the Markov chain model unifies them. Validated across seven agent frameworks with max L∞ error 0.053.

**Practical application**: if an agent has ≥3 sequential tool calls with measurable per-step failure rates, fit a Markov step-reliability model using primitive 10 arithmetic before claiming an overall reliability figure. Do not assume all steps have equal reliability.

---

## Agent FMEA — Failure Modes Specific to LLM Agents

Classic FMEA (primitive 06) applies with these agent-specific failure modes added:

| Failure Mode | Typical Severity | Occurrence Signal | Detection |
|---|---|---|---|
| Context window saturation | High — agent loses earlier instructions or facts | Long tasks; many tool calls | Monitor prompt length; set hard-cap guardrail |
| Tool hallucination | High — agent calls a non-existent tool or wrong API | Sparse tool-use training; ambiguous schemas | Validate tool calls against schema before execution |
| Schema drift | Medium — tool API changes; agent uses stale schema | Dependency updates without re-grounding | Pin schema versions; integration test on deploy |
| Rate-limit failure cascade | High — sequential calls hit rate limit; agent stalls or retries incorrectly | High-throughput pipelines | Instrument rate-limit errors; add exponential backoff with jitter |
| Error propagation amplification | High — early step failure propagates silently through chain | No intermediate validation between steps | Add per-step output validation gates; fail loudly on schema violations |
| Prompt injection via tool output | Critical — adversarial content in tool response hijacks agent | Tools that fetch external content | Sanitize tool outputs; use structured output schemas |

RPN scoring follows primitive 06: Severity × Occurrence × Detection (1–10 each). All Severity ≥ 9 items must be reviewed independently of RPN score.

---

## Decision Additions for AI/Agent Systems

Add these to the Decision Checklist (SKILL.md) when the system is an LLM agent:

- [ ] **Agent with sequential tool calls (≥3 steps)**: measure per-step reliability; compose via Markov step-reliability (primitive 10 extension). Do not use aggregate pass@1 as a reliability promise.
- [ ] **Agent reliability target must be set**: express as pass^k (k ≥ 10) not as a single-run percentage.
- [ ] **Task duration varies widely**: measure RDC across short/medium/long task buckets; do not extrapolate short-task reliability to long tasks.
- [ ] **Pre-launch agent FMEA required**: use the agent-specific failure mode table above alongside standard FMEA (primitive 06).

---

## Sources

1. Rabanser, S., Kapoor, S., Kirgis, P., Liu, K., Utpala, S., & Narayanan, A. (2026). "Towards a Science of AI Agent Reliability." arXiv:2602.16666. https://arxiv.org/abs/2602.16666
2. Khanal, A., Tao, Y., & Zhou, J. (2026). "Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents." arXiv:2603.29231. https://arxiv.org/abs/2603.29231
3. Tran-Truong, P. T., & Le, X.-B. (2026). "Measuring the Unmeasurable: Markov Chain Reliability for LLM Agents." arXiv:2604.24579. https://arxiv.org/abs/2604.24579
4. Gupta, A. (2026). "ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions." arXiv:2601.06112. https://arxiv.org/abs/2601.06112 _(already in sources.json)_
5. Yan, H. et al. (2025). "An Empirical Study of Production Incidents in Generative AI Cloud Services." ISSRE 2025. arXiv:2504.08865. _(already in sources.json — GenAI incidents take 1.83× longer to mitigate vs. non-GenAI)_
