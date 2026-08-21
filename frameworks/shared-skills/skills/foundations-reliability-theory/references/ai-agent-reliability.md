# AI Agent Reliability — Reference


Extension of the foundations-reliability-theory primitives for stochastic LLM/AI agent systems. Load this reference when the system under analysis is an LLM agent, multi-step tool chain, or autonomous agent pipeline — not a hardware component or a traditional cloud service with stationary failure rates.

## Table of Contents

- [Why Classic MTBF Does Not Transfer Cleanly](#why-classic-mtbf-does-not-transfer-cleanly)
- [Core Vocabulary](#core-vocabulary)
- [Markov Chain Step-Reliability](#markov-chain-step-reliability)
- [Multi-Agent Topologies Break the Series Assumption](#multi-agent-topologies-break-the-series-assumption)
- [Silent Failure and the Detection Score](#silent-failure-and-the-detection-score)
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

## Multi-Agent Topologies Break the Series Assumption

`R_system = ∏ rᵢ` treats a step's failure as *contained*: step i either produces a correct output or fails, and the failure does not change what the other steps are. Multi-agent systems violate this. An agent that hands off a subtly wrong artefact does not fail — it succeeds at producing something the next agent will treat as ground truth.

MAST (Cemri et al., arXiv:2503.13657 — 1,600+ traces across 7 frameworks, 14 failure modes, κ = 0.88 on the taxonomy) attributes failures to three categories:

| Category | Share | Examples |
|---|---|---|
| Specification / system design | ~41.8% | task misinterpretation, ambiguous role definitions, poor decomposition, duplicate roles, missing termination conditions |
| Inter-agent misalignment | ~36.9% | communication breakdown, context loss at handoff, conflicting outputs, format mismatch |
| Task verification | remainder | absent or inadequate verification of the final artefact |

Note what this implies: the largest failure category is *specification*, which is fixed before the system runs and has no per-step reliability at all. Improving each agent's rᵢ does not touch ~42% of the failure mass.

**Practical consequences:**

- Use `∏ rᵢ` as a **best case**, not an estimate. Real systems fall below it.
- Enumerate handoff points as FMEA line items in their own right, not as properties of the adjacent agents.
- Prefer a centralised validating coordinator over peer-to-peer handoff when reliability matters more than latency — a single validation point bounds propagation; peer-to-peer does not.
- Missing termination conditions are a reliability failure mode, not a cost problem. Bound step count explicitly (see MOP, above).

## Silent Failure and the Detection Score

The Detection score in FMEA (primitive 06) asks how likely the failure is to be caught before it reaches the user. For LLM agents this is the score most often set wrong, because the classic intuition — failures announce themselves as errors — does not hold. An LLM given a failed tool call frequently renders it into fluent, plausible narrative and returns it as a successful answer.

Wu (arXiv:2606.14589) documents this longitudinally in a production personal-assistant runtime: 22 incidents over eight weeks, with roughly 70% of silent failures caught by human observation rather than by automated testing or audit — in a system carrying 4,286 unit tests and 827 governance checks. Individual failures persisted from 13 hours to 60 days, with duration driven by architectural seams between components. The tests were not absent; they were testing the wrong layer.

**Scoring rule:** rate Detection against *silent* failure, not against crash failure. A system with comprehensive unit tests and no end-to-end ground-truth assertion has poor Detection on this failure class regardless of test count.

**Detection controls that work on this class:**

- Per-step output validation against a schema, executed independently of the agent.
- End-to-end assertions on external ground truth, never on the agent's own report of success.
- Alerting on anomalous *success* patterns — a step that never fails is usually a step whose failures are being absorbed.
- Explicit failure propagation: a failed tool call must be a typed error the orchestrator handles, not free text handed back into a prompt.

Also relevant to duration modelling: HORIZON (Wang et al., arXiv:2604.11978; 3,100+ trajectories across four domains, human-judge agreement κ = 0.84) finds agents perform strongly on short and mid-horizon tasks and break down on long-horizon ones — consistent with the RDC framing above, and evidence that a short-task reliability figure should never be extrapolated.

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
| Failure narrated as success ("fail-plausible") | Critical — wrong answer delivered with full confidence; no error signal reaches anyone | Any step whose error path returns text into a prompt rather than a typed error | Assert on external ground truth, never on the agent's self-report; make tool failures typed errors the orchestrator must handle |
| Context loss or format mismatch at agent handoff | High — downstream agent treats a degraded artefact as ground truth | Multi-agent topologies; peer-to-peer handoff without a validating coordinator | Validate the handoff artefact against a schema at the boundary; prefer a centralised validating coordinator |
| Missing termination condition | High — agent loops until budget or timeout; no result, cost incurred | Open-ended goals; no explicit step cap | Bound step count and wall-clock explicitly; alert on runs reaching the cap (MOP framing above) |

RPN scoring follows primitive 06: Severity × Occurrence × Detection (1–10 each). All Severity ≥ 9 items must be reviewed independently of RPN score.

---

## Decision Additions for AI/Agent Systems

Add these to the Decision Checklist (SKILL.md) when the system is an LLM agent:

- [ ] **Agent with sequential tool calls (≥3 steps)**: measure per-step reliability; compose via Markov step-reliability (primitive 10 extension). Do not use aggregate pass@1 as a reliability promise.
- [ ] **Agent reliability target must be set**: express as pass^k (k ≥ 10) not as a single-run percentage.
- [ ] **Task duration varies widely**: measure RDC across short/medium/long task buckets; do not extrapolate short-task reliability to long tasks.
- [ ] **Pre-launch agent FMEA required**: use the agent-specific failure mode table above alongside standard FMEA (primitive 06).
- [ ] **More than one agent in the system**: treat ∏ rᵢ as a best case; enumerate handoff points as their own FMEA items; check for a missing termination condition.
- [ ] **Scoring Detection in an agent FMEA**: score against silent failure, not crash failure. Test count is not evidence of detection.
- [ ] **Deciding where to spend reliability budget**: scaffolding, routing, and specialist-model selection have empirically outperformed adding a verification loop (Dastidar 2026); a verifier is a low-coverage control (catch rate ≈0.20).

---

## Sources

1. Rabanser, S., Kapoor, S., Kirgis, P., Liu, K., Utpala, S., & Narayanan, A. (2026). "Towards a Science of AI Agent Reliability." arXiv:2602.16666. https://arxiv.org/abs/2602.16666
2. Khanal, A., Tao, Y., & Zhou, J. (2026). "Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents." arXiv:2603.29231. https://arxiv.org/abs/2603.29231
3. Tran-Truong, P. T., & Le, X.-B. (2026). "Measuring the Unmeasurable: Markov Chain Reliability for LLM Agents." arXiv:2604.24579. https://arxiv.org/abs/2604.24579
4. Gupta, A. (2026). "ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions." arXiv:2601.06112. https://arxiv.org/abs/2601.06112 _(already in sources.json)_
5. Yan, H. et al. (2025). "An Empirical Study of Production Incidents in Generative AI Cloud Services." ISSRE 2025. arXiv:2504.08865. _(already in sources.json — GenAI incidents take 1.83× longer to mitigate vs. non-GenAI)_
6. Cemri, M., Pan, M. Z., Yang, S., Agrawal, L. A., Chopra, B., Tiwari, R., Keutzer, K., Parameswaran, A., Klein, D., Ramchandran, K., Zaharia, M., Gonzalez, J. E., & Stoica, I. (2025). "Why Do Multi-Agent LLM Systems Fail?" arXiv:2503.13657. https://arxiv.org/abs/2503.13657 — MAST taxonomy.
7. Wu, W. (2026). "When Errors Become Narratives: A Longitudinal Taxonomy of Silent Failures in a Production LLM Agent Runtime." arXiv:2606.14589. https://arxiv.org/abs/2606.14589
8. Wang, X. J., Bai, H., Sun, Y., Wang, H., Zhang, S., Hu, W., Schroder, M., Mutlu, B., Song, D., & Nowak, R. D. (2026). "The Long-Horizon Task Mirage? Diagnosing Where and Why Agentic Systems Break." arXiv:2604.11978. https://arxiv.org/abs/2604.11978 — HORIZON benchmark.
9. Dastidar, A. (2026). "Where Does Agent Reliability Come From? A Cross-Benchmark Decomposition of Verification Loops, Specialist Models, and Scaffolding in a Production Enterprise Agent." arXiv:2607.17044. https://arxiv.org/abs/2607.17044
