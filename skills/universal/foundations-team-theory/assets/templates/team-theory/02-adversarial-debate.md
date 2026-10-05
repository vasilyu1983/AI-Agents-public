# Mechanism: Structured Adversarial Debate

**Source**: A-HMAD (+4-6% absolute accuracy over *standard debate*, >30% fewer factual errors *in biography facts*; the gain includes a learned coordination policy and vote-weighting optimizer, not heterogeneity alone), RedDebate, AgentAuditor (2025-2026).

## Domain Applications

- **Content moderation / risk review**: two heterogeneous evaluators (policy expert + adversarial red-teamer) debate borderline cases; reasoning-tree synthesis produces an audit-ready decision with dissent captured.
- **Security threat assessment**: attacker-mindset agent vs. defender-mindset agent; disagreements on severity force evidence-grounded resolution rather than averaging.
- **Regulatory compliance go/no-go**: legal perspective vs. business-risk perspective; debate-on-trigger fires only when positions diverge above a threshold.
- **Agent teams**: standard use case — members with different specializations debate before synthesis to prevent confabulation consensus.

## Problem

Debate is not the default: Choi, Zhu & Li (*Debate or Vote*, arXiv:2508.17536, NeurIPS 2025 Spotlight) find "Majority Voting alone accounts for most of the performance gains typically attributed to MAD" and that "debate alone does not improve expected correctness" — it behaves as a martingale over beliefs. Run a matched-token-budget majority-vote / self-consistency baseline first. Debate only when it beats that baseline on held-out data, when targeted interventions are used (Choi also shows these help), or when an audit trail is itself the product. The failure this template still addresses — unweighted voting over a *correlated* pool (same model family, shared training biases, "confabulation consensus") — is real; the fix is heterogeneity plus a baseline check, not "never vote."

## What Works

| Pattern | When to Use | Evidence |
|---------|-------------|---------|
| **Heterogeneous debate** | Use members with different specializations or model sizes | 4-6pp accuracy gain over standard debate, with a learned consensus optimizer weighting each agent's vote (A-HMAD) — this is weighted voting, not an alternative to voting |
| **Reasoning tree audit** | Audit a correlated majority with structured divergence analysis instead of trusting the count | AgentAuditor: resolves conflicts by comparing reasoning branches |
| **Debate-on-trigger** (already in your system) | Only debate when triggers fire, not by default | Avoids wasted cost on agreement cases |
| **Red-team memory** | Store safety-critical debate insights for future inference | RedDebate: reduces unsafe outputs without per-session human intervention |

## What Fails

| Pattern | Why It Fails | Fix |
|---------|-------------|-----|
| **Unweighted vote over a correlated pool** | Same-family agents share biases — they agree on hallucinations; this is what debate must beat, not voting itself | Run a matched-budget vote/self-consistency baseline; use reasoning-tree audit or heterogeneous debate only if it wins |
| **Unlimited rounds** | Agents converge to consensus regardless of correctness after many rounds | "Cap at 2 rounds" is an engineering default, not a sourced result — set your own cap from observed convergence and reconcile it with any team-selection round policy in use |
| **Homogeneous debaters** | Same model = same biases = correlated errors | Use members with different skill specializations |

## Self-MoA Conditional — When Heterogeneity Isn't Required

Default rule: heterogeneous debaters beat homogeneous ones (A-HMAD +4-6pp over standard debate, with a learned vote-weighting optimizer). But there is a documented exception.

| Error Type | Best Choice | Source |
|---|---|---|
| **Model-level error** (training-data bias, shared blind spots) | Heterogeneous debate (different model families) | A-HMAD 2025 |
| **Task-level error** (sampling variance, reasoning-step slips on a verifiable task) | Self-MoA — **same model, multiple samples**, aggregator picks best | Self-MoA arxiv 2502.00674 (2025) |

Self-MoA finding: when the task has a verifiable oracle (compile, test pass, math evaluation), running the strongest single model 5-7 times and aggregating beats heterogeneous debate. Heterogeneity *adds* model-level error in this regime because the weaker family pulls the aggregator down.

**Rule of thumb**:
- Verifiable oracle present → Self-MoA on the strongest model.
- No oracle, soft-judgment task → heterogeneous debate.
- Hybrid (some claims verifiable, others not) → heterogeneous debate, but route the verifiable claims through a Self-MoA pre-pass.

This is a synthesis-layer choice, not a debate-shape choice. Both feed into G07 (mechanism-design synthesis) or G18 (BMV) the same way.

## Enhanced Debate Protocol

For teams with `debate.enabled: true`:

```
Round 1: Independent analysis (parallel, no inter-member communication)
  → Each member produces: position + reasoning chain + confidence + key evidence

Divergence check: Synthesis owner identifies critical disagreements
  → Agreement on >80% of points? Skip debate, go to synthesis
  → Disagreement on high-stakes points? Trigger Round 2

Round 2: Targeted rebuttal (only on divergence points)
  → Each disagreeing member responds to the specific opposing argument
  → Must address the evidence, not just restate position

Synthesis: Reasoning tree audit (not voting)
  → Synthesis owner traces each argument to its evidence
  → Where evidence conflicts: note the conflict and its implications
  → Where reasoning diverges from evidence: flag as potential hallucination
  → Final output includes: decision + dissenting view + confidence + evidence gaps
```

## Related

- [`08-courtroom-proclaim.md`](08-courtroom-proclaim.md) — courtroom progressive debate is a more rigorous variant
- [`07-mechanism-design-synthesis.md`](../../../../foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md) — synthesis protocol that avoids majority-voting pathologies
