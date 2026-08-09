# Agentic Benchmarks

Use this reference when choosing or critiquing an agent benchmark, or when interpreting benchmark results published for a model or agent system.

Two resources frame the current state of the field: τ²-bench as a tool-use / agentic task benchmark, and the Agentic Benchmark Checklist (ABC) as a methodology for not fooling yourself when building or reading benchmarks.

---

## Contents

- [τ-bench and τ²-bench (Sierra)](#τ-bench-and-τ²-bench-sierra)
- [Agentic Benchmark Checklist (ABC)](#agentic-benchmark-checklist-abc)
- [How to Use These Together](#how-to-use-these-together)
- [Anti-Patterns When Reading Benchmark Results](#anti-patterns-when-reading-benchmark-results)

---

## τ-bench and τ²-bench (Sierra)

### What They Are

**τ-bench** (tau-bench) is an agent benchmark that emulates dynamic conversations between a simulated user and a language agent equipped with domain-specific API tools and policy guidelines. It evaluates whether agents can follow real-world policies, use tools correctly, and resolve user requests across multi-turn dialogue.

Source: [arxiv.org/abs/2406.12045](https://arxiv.org/abs/2406.12045) — "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" (Sierra Research, June 2024, arXiv 2406.12045). Code: [github.com/sierra-research/tau-bench](https://github.com/sierra-research/tau-bench).

**τ²-bench** (tau2-bench) extends τ-bench with a dual-control paradigm: both the agent and the user can invoke tools to modify a shared world state. This models real technical support scenarios (e.g. telecom troubleshooting) where the agent must coordinate with an active user rather than operate unilaterally.

Source: [arxiv.org/abs/2506.07982](https://arxiv.org/abs/2506.07982) — "τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment" (Victor Barres, Honghua Dong, Soham Ray, Xujie Si, Karthik Narasimhan; June 9, 2025, arXiv 2506.07982). Code: [github.com/sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench).

### Key Design Decisions Worth Understanding

**pass^k metric.** τ-bench proposes pass^k: the probability that an agent succeeds on k independent trials of the same task. Pass^1 measures first-attempt success; pass^8 measures consistency across 8 trials. This matters because a model that passes 60% of tasks on one run but only 20% on eight runs is unreliable for production. (Verified: even frontier function-calling agents achieved pass^8 below 25% in retail domains at the time of publication — verify against current leaderboard for up-to-date figures.)

**Dual-control (τ²-bench).** Adding a user who can also use tools reveals a distinct failure mode: agents that perform well autonomously degrade by approximately 20 percentage points when they must coordinate with an active user. This gap is invisible in single-control benchmarks. (Source: arXiv 2506.07982 abstract — "a substantial performance decrease (around 20% pass)" — verify against paper for exact figures.)

**Compositional task generation.** τ²-bench generates tasks programmatically from atomic subtask components, making task diversity verifiable and preventing memorization shortcuts.

**Domains covered:** airline, retail (τ-bench); telecom added in τ²-bench with 2,285 compositionally generated tasks across 15 subtask groups.

### Where τ²-bench Sits in an Agent Test Strategy

| Use it for | Skip it when |
|---|---|
| Benchmarking a conversational or tool-using customer-service agent | Your agent is single-turn or does not use tools |
| Comparing model versions on policy-adherence and tool-use reliability | You need a general capability benchmark — τ²-bench is domain-specific |
| Detecting the autonomous-vs-collaborative capability gap | You need a code or math reasoning benchmark |
| Validating pass^k consistency before production rollout | You need a quick smoke test — this is an offline benchmark, not a CI gate |

**Note:** τ²-bench covers airline, retail, and telecom domains. Treat scores on these domains as proxies for tool-use and policy-following capability, not as direct performance guarantees in other verticals. Domain-specific policy adherence should still be validated on your own task distribution.

---

## Agentic Benchmark Checklist (ABC)

### What It Is

The Agentic Benchmark Checklist (ABC) is a peer-reviewed methodology for constructing and auditing agentic benchmarks. It was published in response to systematic flaws found in widely-used benchmarks that cause performance to be over- or underestimated by up to 100% in relative terms.

Source: [arxiv.org/abs/2507.02825](https://arxiv.org/abs/2507.02825) — "Establishing Best Practices for Building Rigorous Agentic Benchmarks" (Yuxuan Zhu, Tengjun Jin, Percy Liang, Daniel Kang, Ion Stoica et al.; submitted July 3, 2025, arXiv 2507.02825). Live checklist: [uiuc-kang-lab.github.io/agentic-benchmarks/](https://uiuc-kang-lab.github.io/agentic-benchmarks/).

### The Problem It Addresses

Specific documented failures the ABC was written to prevent (from the paper):

- **SWE-bench Verified** uses insufficient test cases, causing performance overestimation.
- **TAU-bench** counts empty responses as successful, causing performance underestimation.
- **CVE-Bench** had an "ungated outbound server" shortcut that inflated success rates by 10 percentage points; applying ABC reduced overall overestimation by 33 percentage points.

If a benchmark you are relying on has not been audited against ABC-style criteria, treat its absolute numbers with skepticism.

### The Three Categories

| Category | What it checks | Example concerns |
|---|---|---|
| **Task Validity** | A task is solvable if and only if the agent has the target capability — not because of evaluation shortcuts | Tool versioning, environment isolation, ground-truth freezing, no trivial shortcuts (e.g. ungated outbound servers) |
| **Outcome Validity** | The evaluation method correctly detects whether the task was solved | Sufficient test coverage, semantic matching quality, adversarial judge robustness, empty-response handling |
| **Benchmark Reporting** | Transparent and reproducible reporting | Open code and data, confidence intervals, baseline statistics, judge reproducibility |

### How to Use ABC When Evaluating a Published Benchmark

Before relying on a benchmark result, check:

1. **Task validity:** Are tasks solvable only through the capability being tested? Is the environment isolated and stable between runs? Are shortcuts (trivial exploits, unhardened endpoints) ruled out?
2. **Outcome validity:** Does the reward function correctly identify both success and failure? Are empty or trivial responses scored correctly? Are LLM-as-judge graders validated for reproducibility?
3. **Reporting:** Is there a confidence interval? Is the eval code open? Is a sensible baseline reported?

If a benchmark fails on task or outcome validity, its numbers are unreliable — even if the paper reports high inter-rater agreement or large sample sizes.

### Anti-Pattern: Trusting Leaderboard Numbers Without Auditing

Many published agent benchmarks have not been through ABC-style auditing. Common failure patterns:

- Pass rate inflated because trivial shortcuts were not blocked.
- Pass rate deflated because the reward function penalizes valid alternative solutions.
- Variance hidden because only pass^1 is reported, not pass^k.
- Generalization assumed without domain-transfer validation.

When comparing models using benchmark results, look for: error bars, pass^k (not just pass^1), open eval code, and evidence that shortcuts were audited.

---

## How to Use These Together

τ²-bench and ABC serve different functions:

- **τ²-bench** tells you *how well* an agent performs on tool-use, policy adherence, and user coordination tasks.
- **ABC** tells you *whether to trust* the evaluation method producing that score.

When running τ²-bench (or any benchmark) internally:

1. Apply ABC task-validity checks to your local setup before treating results as meaningful: is the environment isolated? are shortcuts possible? does the reward function handle edge cases correctly?
2. Report pass^k alongside pass^1 — a model that passes 60% on first try but collapses to 20% on 8 trials is not production-ready.
3. Use τ²-bench scores as a signal for capability trends, not as absolute deployment thresholds. Validate on your own task distribution.

---

## Anti-Patterns When Reading Benchmark Results

| Anti-pattern | Why it misleads | Better approach |
|---|---|---|
| Citing only pass^1 | Hides consistency failures across runs | Require pass^k for k ≥ 3 |
| Comparing across domains without adjustment | τ²-bench retail vs. telecom domains have different difficulty profiles | Compare same domain across model versions |
| Assuming benchmark improvements generalize | Models can overfit to benchmark domains | Validate on your own held-out task set |
| Ignoring reward-function validity | Inflated/deflated numbers cause wrong decisions | Apply ABC outcome-validity checks before comparing |
| Treating benchmark rank as production rank | Latency, cost, and integration factors matter | Pair benchmark rank with operational evals |

---

## Related Resources

- **[eval-platform-selection.md](eval-platform-selection.md)** - Choosing a toolchain (DeepEval, Inspect AI, Braintrust, Ragas, Promptfoo, Langfuse)
- **[prompt-injection-testing.md](prompt-injection-testing.md)** - Adversarial red-team tooling (garak, PyRIT, Promptfoo)
- **[scoring-rubric.md](scoring-rubric.md)** - Internal task rubric for your own agent evaluations
- **[SKILL.md](../SKILL.md)** - QA Agent Testing skill overview
