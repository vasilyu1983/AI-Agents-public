# Mechanism: Per-Claim Credibility Scoring

**Source**: *An Adversary-Resistant Multi-Agent LLM System via Credibility Scoring* ([arxiv 2505.24239](https://arxiv.org/html/2505.24239), 2025–2026 work).

## Domain Applications

- **Misinformation detection pipelines**: each claim in a news article or social post scored by evidence quality × corroboration count independently of source reputation; high-risk claims flagged before publication.
- **Adversarial content moderation**: prompt injection or manipulated claims from trusted users pass reputation gating but fail per-claim credibility check; scoring is claim-level not sender-level.
- **Security intelligence synthesis**: threat intelligence from multiple feeds; each indicator-of-compromise scored on evidence chain; prevents a single compromised feed from propagating false claims.
- **Agent team adversarial contexts**: per-claim scoring applied to all member outputs independent of member reputation; catches single-claim failures (out-of-domain hallucination, injected step) that Shapley scores miss.

## Problem

Reputation gating (mechanism 5) tracks trust **across runs** — but within a single run, a normally-reliable member can produce a low-quality claim because:
- The question is out-of-domain for them
- Their context window was poisoned by adversarial input
- They were prompt-injected by retrieved evidence
- The specific sub-claim is a hallucination even though most of their output is solid

Cross-run reputation cannot catch single-claim, single-run failure. You need a **per-claim** signal.

## Distinction From Reputation Gating

| Aspect | Reputation Gating (5) | Credibility Scoring (14) |
|---|---|---|
| Scope | Across runs | Within one run |
| Granularity | Per member | Per claim |
| Updates | Slow, after run completes | Fast, during synthesis |
| Catches | Member is consistently weak | Member is locally compromised, out-of-domain, or hallucinating one specific claim |
| Action on low score | Demote to probationary tier | Downweight this claim only |

The two mechanisms compose: credibility scores from a run feed back into reputation updates between runs.

## Solution

Score each member's individual claims on:
1. **Evidence quality** — does the cited evidence actually support the claim?
2. **Corroboration** — do other members reach a compatible claim independently with non-overlapping evidence?

Combine them. Downweight low-credibility claims at synthesis without ejecting the member.

## Protocol

```
Phase 1 — Per-claim evidence binding
  Each member submits findings as DISCRETE CLAIMS, each tagged with:
    - Cited evidence (source, span, retrieval timestamp if from RAG)
    - Reasoning chain linking evidence to claim
    - Per-claim confidence (NOT per-member confidence)

Phase 2 — Credibility computation
  For each claim C from member M:
    evidence_quality(C) = does cited evidence actually support C?
                          0.0 = missing or contradictory
                          0.5 = weakly supportive or analogical
                          1.0 = directly supports C
    corroboration(C)    = do other members reach a compatible claim
                          via independent evidence (not citing the same source)?
                          0.0 = contradicted by another member
                          0.5 = unique (no one else addressed it)
                          1.0 = corroborated by independent evidence
    credibility(C)      = evidence_quality(C) × (0.5 + 0.5 × corroboration(C))

Phase 3 — Synthesis weighting
  credibility < 0.3   → discard or flag as unverified
  0.3 ≤ c < 0.7       → include with explicit uncertainty in artifact
  credibility ≥ 0.7   → include in primary synthesis
```

## When To Use

- Any team that draws on retrieved evidence (RAG, web search, code search) — credibility binding requires citations
- High-stakes decisions where one bad claim flips the outcome (security, legal, payments, regulatory)
- Mixed-domain teams where one member may be answering outside their specialization
- When prompt injection or context poisoning is realistic (user-provided content in the brief)

## When NOT To Use

- Pure-reasoning teams where members produce no citable evidence — credibility collapses to confidence; use mechanism 11 instead
- Teams of 2 — corroboration signal is too weak; use mechanism 5 (reputation) or 13 (reasoning-tree audit) instead
- Brainstorming or creative teams where unique claims are the *point* — penalizing low corroboration kills the value

## Operating Rule

Claims must be **separable**. When a member produces a single load-bearing argument that depends on a chain of intermediate claims, score the chain at its weakest link, not at the conclusion. A 95%-credible conclusion built on a 20%-credible premise is a 20%-credible argument.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Conflating member credibility with claim credibility | Score the claim, not the speaker — a strong member can have a weak claim |
| Using corroboration as the sole signal | LLMs share biases and corroborate hallucinations; require evidence_quality > 0 first |
| Treating low credibility as "remove member" | Per-claim downweighting, not ejection — the member may produce strong claims later in the same run |
| Silently discarding low-credibility claims | Flag them in the artifact so the parent thread can audit the decision |
| Letting members self-score their own evidence_quality | Cross-score: another member or the synthesis owner scores the evidence binding |

## Incentive-Compatible Claim Decomposition (Peer-Prediction Layer)

Per-claim credibility scoring measures evidence quality and corroboration, but does not provide formal incentive guarantees — a strategic source can still craft claims that score well on evidence_quality while steering the synthesis.

For synthesis tasks with multiple sources where strategic manipulation is a concern, add a peer-prediction layer on top of credibility scoring: decompose the synthesis into atomic claims, elicit each source's stance on each claim, and apply multi-task peer-prediction scoring that rewards informative agreement. This provides a formal Bayesian Nash Equilibrium guarantee that honest reporting is a best response.

**Sequencing**: run per-claim credibility scoring (Phase 1–3 above) first to filter low-evidence claims; then apply peer-prediction on the remaining claims to discourage strategic stance manipulation before re-synthesis.

**Boundary condition**: peer-prediction degrades when sources share the same training data (correlated stances nullify the signal). Check source diversity before adding this layer.

Source: TTS-PeerPrediction — arXiv 2509.25184, ICLR 2026.

## Related

- [`05-reputation-gating.md`](05-reputation-gating.md) — cross-run trust tier; credibility scores feed into reputation updates between runs
- [`13-reasoning-tree-audit.md`](13-reasoning-tree-audit.md) — credibility scoring is the natural input to FPD branch selection
- [`07-mechanism-design-synthesis.md`](07-mechanism-design-synthesis.md) — credibility-weighted synthesis as the truthful-revelation default; see also Claim-Level Truthfulness recipe there
- [`11-prediction-market.md`](11-prediction-market.md) — confidence and credibility are independent signals; combine with care
