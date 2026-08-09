# Known Traps in Research Idea Mining

12-trap catalog. Apply at workflow Step 5b. Multi-tag allowed.

## Table of Contents

- [How to Use](#how-to-use)
- [The 12 Traps](#the-12-traps)
- [Scoring Effect](#scoring-effect)

## How to Use

For each surviving idea after extraction:

1. Read the trap definitions; tag every trap that applies.
2. Apply each trap's counter-recipe (try to disconfirm the trap).
3. If the counter-recipe disconfirms, drop the tag.
4. Apply the scoring effect for any remaining tags.
5. Hard kills: Trap 11 (`proprietary-component`) and Trap 12 (`benchmark-gaming`) eliminate the idea unless an alternative is documented.

## The 12 Traps

### 1. `irreproducibility`

**Smell:** Strong claims, no code, vague hyperparameters, single benchmark.
**Why it fools you:** Prestigious authors or venues create halo effect. The method *might* work, but you can't verify — and adopting it without verification means inheriting unknown risk.
**Counter-recipe:** Search GitHub (via `research-git`) and Semantic Scholar (`intent=methodology` citations) for third-party reimplementations; check OpenReview/alphaXiv for flagged reproduction failures. If none exist 6+ months after publication, the result is suspect. (Papers with Code is dead — see [papers-with-code-strategy.md](papers-with-code-strategy.md).)
**Red flag:** "Our setup details are in the supplementary" + supplementary lacks them.

### 2. `cherry-picked-baselines`

**Smell:** Compares only to weak or outdated baselines. Doesn't compare to the obvious recent SOTA.
**Why it fools you:** Headline numbers look amazing.
**Counter-recipe:** List the recent SOTA methods on the same benchmark from the benchmark's own leaderboard, HF Papers, or Semantic Scholar (sort citing papers by recency). If any obvious recent SOTA is missing from the comparison, downgrade.
**Red flag:** Baselines are 2+ years older than the paper.

### 3. `benchmark-overfit`

**Smell:** Numbers on the target benchmark are far better than on related held-out benchmarks.
**Why it fools you:** Single-benchmark wins look like broad gains.
**Counter-recipe:** Look for cross-benchmark generalization data. If the method gains 20% on Benchmark A and 1% on similar Benchmark B, it's specific to A.
**Red flag:** No cross-benchmark evaluation or only "we tested on the standard benchmark".

### 4. `compute-asymmetry`

**Smell:** Method requires compute scale that you can't replicate (huge models, long training, expensive inference).
**Why it fools you:** Method works *for them*. May not be your method.
**Counter-recipe:** Note compute requirements explicitly in the idea card. If 10× yours, mark as `validate` not `promote`.
**Red flag:** "We used 1024 H100s for two weeks" without a smaller-scale variant.

### 5. `data-leakage-suspicion`

**Smell:** Method tests on benchmarks whose data may have leaked into pretraining (esp. for LLMs).
**Why it fools you:** Test-set memorization looks like generalization.
**Counter-recipe:** Check benchmark publication date vs. base model training cutoff. Look for contamination analysis in the paper.
**Red flag:** Paper uses pre-2023 LLM benchmarks without contamination discussion.

### 6. `preprint-only-no-corroboration`

**Smell:** arXiv preprint, no peer review, no derivative work, 6+ months old.
**Why it fools you:** Preprints feel current and authoritative.
**Counter-recipe:** Check Semantic Scholar for citing-paper count and quality. Check GitHub (via `research-git`) for an official or third-party implementation.
**Red flag:** Preprint with strong claims, zero citations, zero forks.

### 7. `corporate-selection-bias`

**Smell:** Industry research blog post about a method "we use in production".
**Why it fools you:** The corp publishes only what works for them; the failures aren't in the post.
**Counter-recipe:** Find an independent reproduction or a failure mode discussion. If only the publishing org reports success, downgrade.
**Red flag:** Single-source method with marketing-style framing.

### 8. `hype-bubble`

**Smell:** Method gets covered by 5+ curator newsletters in 2 weeks but lacks third-party benchmark replication.
**Why it fools you:** Cresting signal mimics maturity.
**Counter-recipe:** Wait 60 days. Recheck for replications. If none, the bubble was the only signal.
**Red flag:** Curator coverage > implementation activity ratio.

### 9. `narrow-applicability`

**Smell:** Method is task-specific (e.g., a prompting trick for math word problems) but framed as general.
**Why it fools you:** Generality framing inflates perceived value.
**Counter-recipe:** Identify the *exact* task and ask if your target uses that task. If not, downgrade.
**Red flag:** Title says "for X" but paper only evaluates on X — and X isn't your target.

### 10. `negative-trade-off-hidden`

**Smell:** Method improves metric A while ignoring metrics B and C.
**Why it fools you:** Headline gain is real; cost is hidden.
**Counter-recipe:** Look for latency, cost, or robustness numbers. If absent, assume the trade-off is unfavorable.
**Red flag:** "Our method achieves +5 on accuracy" with no cost or latency table.

### 11. `proprietary-component`

**Smell:** Method depends on a proprietary model, dataset, or API (e.g., GPT-4 as judge, internal corpus).
**Why it fools you:** The method itself sounds general.
**Counter-recipe:** Identify the proprietary dependency and find an open replacement candidate. If none works, hard kill.
**Red flag:** A closed model (GPT-4, Claude, Gemini, etc.) is the judge, labeler, or data source, with no open fallback offered.

### 12. `benchmark-gaming`

**Smell:** Method's gains pattern-match Goodhart's Law — optimizing the metric, not the underlying capability.
**Why it fools you:** Numbers go up.
**Counter-recipe:** Read failure cases. If failures are off-distribution from the benchmark, the method gamed the benchmark.
**Red flag:** Benchmark-specific tricks (token-level edits to match benchmark format) are the headline contribution.

## Scoring Effect

> **How these are applied:** `aggregate_research_ideas.py` owns the gate. The
> "`gate_status` ≥ `validate`" and **Hard kill** rows are enforced as rule caps by
> the aggregator (the numeric score never overrides them). The numeric adjustments
> (`evidence_grade -1`, `applicability -1/-2`, `lift +1 tier`) are applied to the
> **ranking score only** — they change ordering within a gate bucket, never the
> gate decision itself. Trap tags must be present in the findings TSV `trap_tags`
> column for the aggregator to act on them.

| Trap | Effect on idea card |
|------|---------------------|
| 1. irreproducibility | `evidence_grade` capped at C; `gate_status` ≥ `validate` |
| 2. cherry-picked-baselines | `evidence_grade` -1 grade |
| 3. benchmark-overfit | `applicability` -1 |
| 4. compute-asymmetry | `lift` raised by 1 tier; mark hardware constraint |
| 5. data-leakage-suspicion | `evidence_grade` -1; `gate_status` ≥ `validate` |
| 6. preprint-only-no-corroboration | `gate_status` ≥ `validate` |
| 7. corporate-selection-bias | `evidence_grade` -1; require independent corroboration |
| 8. hype-bubble | `gate_status` = `validate`; recheck after 60d |
| 9. narrow-applicability | `applicability` -2 if target task differs |
| 10. negative-trade-off-hidden | `applicability` -1; flag missing cost data |
| 11. proprietary-component | **Hard kill** unless alternative documented |
| 12. benchmark-gaming | **Hard kill** unless out-of-distribution evidence |

The aggregator script applies penalties via `trap_penalty` (starts at 1.0; +0.5 per non-hard tag).

## Cross-Trap Patterns

Common combinations to watch for:

- **6 + 8** (preprint-only + hype-bubble) = textbook AI-Twitter cycle. Wait it out.
- **1 + 7** (irreproducible + corporate-selection-bias) = "internal results" papers that no one outside can verify.
- **3 + 9** (benchmark-overfit + narrow-applicability) = method works for exactly one task on exactly one dataset.
- **4 + 11** (compute-asymmetry + proprietary-component) = "you can't run it and you can't see it" — almost always kill.

### LLM-as-judge evidence (a signal, not a 13th trap)

When a method's headline result rests on **LLM-as-judge** scoring (an LLM rates outputs instead of humans or an objective metric), the evidence is weaker than the paper's framing implies. Known LLM-judge biases: **position bias** (favours the first/last candidate), **verbosity bias** (favours longer answers), **style/sycophancy bias** (favours its own family's phrasing), and **self-preference** (a judge from model family X over-rates model family X).

This is deliberately *not* a new numbered trap — the scoring engine (`aggregate_research_ideas.py`) hard-codes traps 1–12 and a new number would silently never fire. Instead, map it onto the existing engine:

- Tag **trap 2 (`cherry-picked-baselines`)** and apply its `evidence_grade -1` whenever the win is LLM-judge-decided and the paper shows no human-calibration, no position/verbosity controls (swap order, length-normalise), and no agreement statistic (e.g. Cohen's κ vs. humans).
- Additionally tag **trap 7 (`corporate-selection-bias`)** when the judge model is from the **same family** as the proposed method — self-preference makes the result non-independent; require independent (different-family or human) corroboration before `promote`.
- In the idea card, record the judge model, whether order/length were controlled, and any human-agreement number. "GPT-4 judged it better" with no controls is a `validate`, never a `promote`.

If two or more traps fire, the idea moves to `validate` minimum; three or more fire, default to `kill` unless the idea is unusually novel and cheap to test.
