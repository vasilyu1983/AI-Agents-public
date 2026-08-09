---
name: Radial Consensus Score (RCS)
mechanism_id: 19
layer: selection
status: stable
last_verified: 2026-05-01
sources:
  - https://arxiv.org/abs/2604.12196
---

# Radial Consensus Score — Embedding-Centroid Best-of-N

Geometric selector that picks the candidate closest to the *consensus direction* of the proposal cloud, not the candidate with the most votes.

Process:

1. Embed every candidate answer into a shared semantic space.
2. Compute the centroid of the embedding cloud.
3. Score each candidate by cosine similarity to the centroid (the radial distance from "average opinion").
4. Pick the candidate with the highest similarity — the one that best represents the cluster's consensus *meaning*, even if it isn't the most-voted exact string.

The trick: textual majority voting fails when 5 agents give 5 lexically different but semantically equivalent answers. RCS treats the embedding cluster as the signal.

## When to Use

- Open-ended generation where multiple wordings express the same idea (summaries, rewrites, design proposals, naming).
- Best-of-N selection over 5+ candidates from heterogeneous agents.
- Synthesis after an MoA layer (proposers fan out, RCS picks the consensus aggregator output).
- Code review verdicts where 3 reviewers say "this is fine" in 3 different sentences.

## When NOT to Use

- Categorical answers (yes/no, A/B/C/D). Use BMV or majority vote — embeddings add noise to discrete choices.
- N < 5 candidates. The centroid is unstable below 5 points.
- High-stakes verifiable tasks (compile, test). Use the oracle.
- Tasks where the right answer is intentionally an outlier (security review, edge cases, contrarian critique). RCS will suppress the correct minority.

## How It Plugs In

```yaml
selection:
  method: radial_consensus_score
  inputs:
    candidates: <list of N text outputs>
    embedding_model: text-embedding-3-large  # or any sentence transformer
  steps:
    - embed: each candidate → vector
    - centroid: mean(vectors)
    - score: cosine_similarity(candidate_vector, centroid) for each
    - rank: descending
  output:
    winner: highest similarity
    outliers: candidates below 1 SD from mean similarity (kept for review)
```

Outliers are *not discarded* — surface them to the operator, since they may carry the minority-correct insight that RCS by design suppresses.

## Composition

- **Replaces** majority voting in MoA aggregator layer when proposals are open-ended.
- **Pairs with G02 (Adversarial Debate)** — RCS picks the centroid argument; outliers feed back into a second debate round.
- **Pairs with G18 (BMV)** — use RCS to cluster, BMV-ISP to evaluate the outliers.
- **Stacks under G13 (Reasoning-Tree Audit)** — audit verdicts get RCS-clustered into a single "consensus diagnosis."

## Anti-Patterns

- **Centroid collapse.** If all agents share a system prompt, the centroid is the prompt's bias, not consensus. Force prompt diversity.
- **Outlier blindness.** Discarding outliers without operator review is the failure mode. Always log them.
- **Embedding model drift.** Lock the embedding model for a session. Switching models invalidates the cluster geometry.
- **Length bias.** Longer answers can drag the centroid. Normalize embeddings before averaging, or truncate to a uniform length budget.

## Calibration

Sanity check on a held-out task set: does RCS pick the human-preferred answer ≥ 60% of the time? If not, the embedding model is wrong for the domain (e.g., code embeddings for natural-language tasks).

## Sources

- arxiv 2604.12196 — *Radial Consensus Scoring for LLM Best-of-N Selection* (2026).
- Together AI MoA blog — establishes aggregator pattern that RCS slots into.
