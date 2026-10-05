# Click Models & Bias Correction

Turning raw click logs into relevance judgments you can actually train on. Covers the three biases that make naive click-through rate (CTR) unusable as a training label — position bias, confidence bias, presentation bias — and the method that fixes each.

Source for the click-model material: Grainger, Turnbull & Irwin, *AI-Powered Search* (Manning, 2025), ch. 8, 11–12.

---
## Table of Contents

- [Why Raw CTR Is Not a Label](#why-raw-ctr-is-not-a-label)
- [The Three Biases](#the-three-biases)
- [Pattern CM-1: SDBN — Correcting Position Bias with Examines](#pattern-cm-1-sdbn--correcting-position-bias-with-examines)
  - [What an "examine" is](#what-an-examine-is)
  - [The SDBN algorithm](#the-sdbn-algorithm)
  - [Choosing a click model](#choosing-a-click-model)
- [Pattern CM-2: Beta Prior — Correcting Confidence Bias](#pattern-cm-2-beta-prior--correcting-confidence-bias)
  - [The lucky-click problem](#the-lucky-click-problem)
  - [Why not just filter low-confidence rows](#why-not-just-filter-low-confidence-rows)
  - [The beta prior](#the-beta-prior)
  - [Tuning prior_weight](#tuning-prior_weight)
- [Pattern CM-3: Exploration — Correcting Presentation Bias](#pattern-cm-3-exploration--correcting-presentation-bias)
  - [Ad-hoc diversification vs. systematic exploration](#ad-hoc-diversification-vs-systematic-exploration)
  - [Gaussian-process-driven exploration](#gaussian-process-driven-exploration)
- [Pattern CM-4: Signal Spam Defence](#pattern-cm-4-signal-spam-defence)
- [Adversarial Signal Checklist](#adversarial-signal-checklist)
- [Putting It Together](#putting-it-together)
- [Cross-References](#cross-references)

---

## Why Raw CTR Is Not a Label

The obvious way to turn clicks into judgments is clicks ÷ impressions per query-document pair. It does not work. CTR is dominated by where you already put the result, not by whether the result was good. Train a ranker on raw CTR and you teach it to reproduce the ranking it was already showing — an echo chamber, not a relevance signal.

Every pattern below exists to strip one systematic distortion out of that number before it becomes a training label.

---

## The Three Biases

| Bias | What it is | Fix |
|---|---|---|
| **Position bias** | Users prefer higher-ranked results even when lower ones are more relevant | Pattern CM-1 (SDBN examines) |
| **Confidence bias** | Grades built on statistically insignificant, spurious events — one click on one view grades 1.0 | Pattern CM-2 (beta prior) |
| **Presentation bias** | The model cannot learn about documents it never shows | Pattern CM-3 (exploration) |

*AI-Powered Search* attributes position bias to three mechanisms, citing Joachims et al., "Evaluating the Accuracy of Implicit Feedback from Clicks and Query Reformulations in Web Search":

- **Trust bias** — users trust the engine knows what it's doing, so they interact with higher results more.
- **Scanning behaviours** — users examine results in patterns (typically top-to-bottom) and often don't explore everything in front of them.
- **Visibility** — higher-ranked results are more likely to be rendered on screen; users must scroll to see the rest.

---

## Pattern CM-1: SDBN — Correcting Position Bias with Examines

**Use when:** you are deriving relevance judgments from click logs and have per-session result ordering. This is the default first correction — apply it before anything else.

### What an "examine" is

An **impression** is a UI element rendered in the viewport. An **examine** is different: the probability that a result was *consciously considered* by the user. Users routinely fail to notice things rendered right in front of them.

The distinction matters because a result that was rendered but never considered should not be penalised for its lack of clicks. Modelling examines is how a click model represents position bias at all — another way of saying "position bias" is "whether users examine a result depends on its position."

Click models differ in how they estimate examines:

- **Position-based model (PBM)** — estimates an examine probability per position, across all searches.
- **Cascade / dynamic Bayesian network (DBN) family** — assume a result was likely examined if it appeared at or above the last click on the page.

### The SDBN algorithm

A **simplified dynamic Bayesian network (SDBN)** is a slightly less accurate version of the fuller DBN click model. These models assume that, within a search session, the probability a user examined a document depends heavily on whether it sat at or above the lowest clicked document.

Three steps:

1. Mark the last (lowest-ranked) click of each session.
2. Treat every document at or above that rank as examined.
3. Grade = total clicks ÷ total examines, aggregated across sessions.

```python
# Step 1-2: mark examines per session
def calculate_examine_probability(sessions):
    last_click_per_session = sessions.groupby(
        ["clicked", "sess_id"])["rank"].max()[True]
    sessions["last_click_rank"] = last_click_per_session
    sessions["examined"] = sessions["rank"] <= sessions["last_click_rank"]
    return sessions

# Aggregate clicks and examines per document, examined rows only
def calculate_clicked_examined(sessions):
    sessions = calculate_examine_probability(sessions)
    return (sessions[sessions["examined"]]
            .groupby("doc_id")[["clicked", "examined"]].sum())

# Step 3: the SDBN grade
def calculate_grade(sessions):
    sessions = calculate_clicked_examined(sessions)
    sessions["grade"] = sessions["clicked"] / sessions["examined"]
    return sessions
```

The result is a kind of *dynamic* CTR: it tracks, within each session, when a result was likely considered, and uses only those opportunities as the denominator. Results examined often and clicked are rewarded; results examined often and not clicked are demoted. Results never examined are not punished for it.

This is the method that fulfils the "position bias corrected" checklist item in [`user-feedback-learning.md`](user-feedback-learning.md) — that file previously listed the requirement without naming a method.

### Choosing a click model

SDBN is the right default: it needs only per-session rank + click, no per-position probability fitting, and it is cheap to recompute on every batch. Move to full DBN or PBM only when you have the traffic volume to fit the extra parameters reliably and evidence that SDBN's last-click assumption is wrong for your surface (e.g. an infinite-scroll UI where "last click" does not bound the scanned region).

---

## Pattern CM-2: Beta Prior — Correcting Confidence Bias

**Use when:** always, alongside CM-1. SDBN alone produces grades of 1.0 from a single click.

### The lucky-click problem

The book's analogy: a little-league player's first at-bat is a hit, so their batting average is technically 1.000. Nobody concludes they are a prodigy.

Same thing in click data. In the book's worked example for the query `blue ray`, the top-graded document was a pack of Blu-ray cases with **1 click out of 1 examine — grade 1.000**. It outranked a Blu-ray *player* graded 0.411765 on 34 examines. The sparse row wins purely because it is sparse.

This is **confidence bias**: a judgment list carrying many grades derived from statistically insignificant, spurious events. It bites hardest on torso and long-tail queries, and on common misspellings like `blue ray` that mix modest-traffic documents with near-zero-traffic ones.

### Why not just filter low-confidence rows

Tempting, and the book advises against it:

- Filtering below a minimum-examines threshold throws away training data.
- Documents-per-query are examined on a power law — a few very frequently, the vast majority very infrequently. A threshold therefore removes a large share of examples and can cause the model to miss important patterns.
- You are still left with the harder question a threshold does not answer: how to weight *medium*-confidence examples against high-confidence ones.

Keep every row; weight it by confidence instead.

### The beta prior

A beta distribution turns a point probability into two values, `a` and `b`, where `mean = a / (a + b)`:

- **`a` (successes)** — examines with clicks.
- **`b` (failures)** — examines without clicks.

Declare a prior grade (the default belief about an unknown document, plausibly the typical grade seen across your judgments) and a prior weight (how much confidence to place in that prior; `prior_weight = a + b`). Then update from observed data:

```python
def calculate_prior(sessions, prior_grade, prior_weight):
    sessions = calculate_grade(sessions)          # SDBN grade from CM-1
    sessions["prior_a"] = prior_grade * prior_weight
    sessions["prior_b"] = (1 - prior_grade) * prior_weight
    return sessions

def calculate_sdbn(sessions, prior_grade=0.3, prior_weight=100):
    sessions = calculate_prior(sessions, prior_grade, prior_weight)
    sessions["posterior_a"] = sessions["prior_a"] + sessions["clicked"]
    sessions["posterior_b"] = (sessions["prior_b"]
                               + sessions["examined"] - sessions["clicked"])
    sessions["beta_grade"] = (sessions["posterior_a"]
                              / (sessions["posterior_a"] + sessions["posterior_b"]))
    return sessions.sort_values("beta_grade", ascending=False)
```

With `prior_grade = 0.3` and `prior_weight = 100`, every document starts at `prior_a = 30, prior_b = 70` (0.3 = 30 / (30 + 70)). Reworking the `blue ray` example from the book:

| doc | clicks | examines | raw grade | posterior_a | posterior_b | beta_grade |
|---|---|---|---|---|---|---|
| Blu-ray player | 14 | 34 | 0.411 | 44.0 | 90.0 | 0.328358 |
| Blues Brothers (Blu-ray) | 8 | 20 | 0.400 | 38.0 | 82.0 | 0.316667 |
| Blu-ray cases (10-pack) | 1 | 1 | 1.000 | 31.0 | 70.0 | 0.306931 |

The one-click document falls from first to third. Its grade of 1.000 becomes 0.306931 — barely moved off the 0.3 prior, which is exactly right for a single observation.

### Tuning prior_weight

The magnitude of the prior is the tuning knob, and it matters more than the prior grade:

- **Weak prior** — the book's illustration uses `a=0.25, b=1.75` (still mean 0.125). One click moves the posterior mean to `1.25 / (1.25 + 1.75)`, roughly **0.416**. The book calls that "a major effect for just one click."
- **Strong prior** — very high `a` and `b` make the prior barely budge regardless of data.

Tune the magnitude so updates have the effect you want. A practical starting point: set `prior_weight` near the median examine count across your judgment list, so a typical-traffic document is weighted roughly equally between prior and evidence, while tail documents stay pinned near the prior.

---

## Pattern CM-3: Exploration — Correcting Presentation Bias

**Use when:** your click model has been running long enough that its training data covers only what the current ranker already surfaces.

**Presentation bias** is the bias that no amount of cleverness with the existing logs can fix: a model cannot learn about documents it never shows. Documents with no traffic generate no clicks, no examines, and therefore no evidence — so they never get shown, so they never generate traffic. Correcting it requires changing what you show, which makes this an **active learning** problem rather than a log-processing one.

The tradeoff is explore vs. exploit. Exploring grows the coverage of the click model to new and different documents; exploiting optimises against what you already know. Always exploring means never using hard-earned knowledge; always exploiting means never gaining any.

### Ad-hoc diversification vs. systematic exploration

The naive approach is to eyeball a query's logged features, notice the gaps, and inject something different. In the book's `transformers dvd` example the gaps were visible by inspection: every training item had a name match, and no promoted items (`has_promotion=0`) appeared at all.

The book is explicit that this does not scale — it analysed a single query by hand and calls the approach "not systematic." Two failure modes:

- It does not generalise across a query catalogue.
- It gives you no principled answer to "how much risk are we willing to take?" You do not want to blanket results with random products just to broaden training data.

Ad-hoc randomisation is therefore a stopgap, not the pattern.

### Gaussian-process-driven exploration

A **Gaussian process** is a statistical model that makes predictions *and* provides a probability distribution capturing the certainty of each prediction. That second output is what makes it the right tool here: it lets you rank exploration candidates by both expected relevance and expected knowledge gain.

The mapping to ranking: just as nearby dates have similar river levels (the book's surveying analogy), documents with similar feature values should have similar relevance. A GP trained to predict relevance grade as a function of exploration features will therefore report low standard deviation in feature regions well covered by your judgments, and high standard deviation in the unexplored regions.

The selection rule combines the two outputs — prefer candidates whose predicted relevance is acceptable *and* whose standard deviation is high, since those maximally increase knowledge. The book exposes the balance as a tunable weight on the standard deviation: the higher the weight, the more it favours the unknown, higher-standard-deviation cases over safe high-predicted-value ones.

```python
from sklearn.gaussian_process import GaussianProcessRegressor

gpr = GaussianProcessRegressor()
gpr.fit(explore_features, grades)

mean, std = gpr.predict(candidate_features, return_std=True)
# theta weights knowledge gain against predicted relevance;
# higher theta favours unexplored, high-variance candidates
score = mean + theta * std
```

Run exploration on a bounded slice of traffic and feed the resulting clicks back through CM-1 and CM-2 like any other session data. Guardrails from [`user-feedback-learning.md`](user-feedback-learning.md) Pattern 3 apply unchanged — exploration is a live-traffic intervention and can degrade CTR.

---

## Pattern CM-4: Signal Spam Defence

**Use when:** click signals influence ranking and the surface is open to the public. Any crowdsourced ranking input is an attack surface.

The attack is trivial. In the book's demonstration, a single malicious user (`u8675309`) issues a repeated query (`star wars`) and clicks a chosen document — a Star Wars-themed trash can — **5,000 times**. The signals-boosting aggregation faithfully records a boost of 5000 and promotes the target to the top of the results for every subsequent visitor.

The defence is one line of aggregation logic: **collapse duplicate clicks by the same user to one vote** per query/document pair. Group by user before counting, so whether a user clicks once or a million times, they contribute a single signal.

```sql
SELECT query, doc, COUNT(doc) AS boost FROM (
  SELECT c.user unique_user, LOWER(q.target) AS query, c.target AS doc,
         MAX(c.signal_time) AS boost
  FROM signals c LEFT JOIN signals q ON c.query_id = q.query_id
  WHERE c.type = 'click' AND q.type = 'query'
  GROUP BY unique_user, LOWER(q.target), doc)   -- one vote per user
GROUP BY query, doc
ORDER BY boost DESC
```

The book reports the effect directly: the **5,000 spammy signals are deduplicated to 1 signal** in the anti-spam boosting model, and the normal results return. The aggregated count lands close to the pre-attack baseline.

Note that this defence lives at the *aggregation* layer, not the collection layer — you still log every raw signal, you just refuse to let one identity vote more than once when building the model. That preserves the raw data for forensics.

---

## Adversarial Signal Checklist

Companion to the Privacy Checklist in [`user-feedback-learning.md`](user-feedback-learning.md) Pattern 1. Privacy protects users *from* your logs; this protects your model *from* your users.

- [ ] Per-user dedup in signal aggregation — one vote per user per query/doc pair
- [ ] Raw signals retained un-deduplicated for forensics; dedup applied at aggregation only
- [ ] Rate limits on signal ingestion per identity and per IP
- [ ] Bot and automation traffic classified and excluded from judgment generation
- [ ] Session validity checks (a "click" without a preceding query is not a signal)
- [ ] Alert on abnormal signal concentration — one user or one document dominating a query's boost
- [ ] High-value or monetised queries reviewed for manipulation before judgments ship
- [ ] Newly-promoted documents spot-checked against the identities that promoted them

---

## Putting It Together

Order matters. Each stage consumes the output of the previous one:

1. **Collect** rank/click/session signals needed for bias correction; retain query text and stable per-user IDs only if the product's data-governance decision permits them, with bounded access and retention. ([`user-feedback-learning.md`](user-feedback-learning.md) Pattern 1)
2. **Dedup** per user at aggregation time (CM-4) before any grading.
3. **Grade** with SDBN examines, not raw CTR (CM-1).
4. **Damp** with a beta prior so sparse rows cannot dominate (CM-2).
5. **Feed** the resulting judgment list into the LTR pipeline ([`learning-to-rank-pipeline.md`](learning-to-rank-pipeline.md) Step 1).
6. **Explore** a bounded traffic slice so the next cycle's judgments cover documents the current model never shows (CM-3).
7. Repeat. The loop is what makes LTR retraining automatic rather than a one-off.

Steps 3 and 4 are not optional refinements — skipping them produces a judgment list that trains the ranker to reproduce itself.

---

## Cross-References

- [`user-feedback-learning.md`](user-feedback-learning.md) — signal capture, interleaving, reranker retraining, monitoring. This file supplies the label-generation method its Pattern 2 checklist calls for.
- [`learning-to-rank-pipeline.md`](learning-to-rank-pipeline.md) — the six-step pipeline these judgments feed (Step 1).
- [`ranking-pipeline-guide.md`](../../ai-rag/references/ranking-pipeline-guide.md) — where a trained model sits in the serving path.
- [`search-evaluation-guide.md`](search-evaluation-guide.md) — offline metrics for judging whether a new judgment list is actually better.
