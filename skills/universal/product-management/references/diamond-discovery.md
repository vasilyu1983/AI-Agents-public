# Diamond Discovery — Finding the Hidden Gem and Pricing It

The interpretation-tier half of Diamond Discovery. The detection tier
(`marketing-product-analytics/references/micro-signal-methods.md` + detectors 11–14) surfaces
*candidates*. This reference turns a candidate into a **diamond**: a non-obvious product detail that is
real, valuable, addressable, and differentiating — and then into one priced, testable bet.

The differentiator is not generating candidates. It is **not fooling yourself**. Every candidate passes a
disconfirmation gate before it is believed; the ones that fail are logged as *fool's gold*, not diamonds.

## Table of Contents

- [When to use](#when-to-use)
- [The four lenses](#the-four-lenses)
- [The disconfirmation gate](#the-disconfirmation-gate)
- [Diamond scoring](#diamond-scoring)
- [The Diamond Brief](#the-diamond-brief)
- [Worked example](#worked-example)
- [Cross-links](#cross-links)

## When to use

Trigger phrases: *"what am I missing?"*, *"find the hidden gem"*, *"what could 10x this?"*,
*"where's the diamond?"*, *"see what a human can't see in this product."*

Works in two modes:
- **Data-rich** — you have a radar from `run_blind_spot_detectors.py` (detectors 11–14 fired/emitted).
  Start from the radar's top `diamond_score` rows.
- **Low-data** — you have screenshots, support tickets, sales-call notes, five interviews, or just
  intuition. Run the four lenses below with the zero-data question batteries; no analytics required.

The pipeline is the same either way: **detect → interpret → disprove → price → convert to one bet.**

## The four lenses

Each lens targets one diamond substrate and carries a question battery usable with no data. When data
exists, pair the lens with its detector.

### Anomaly lens (statistical micro-signals)
*Pair with detectors 11 (anti-average-segment), 12 (activation-precursor-sequence).*
- Which segment behaves *opposite* to the average?
- Which step do power users skip that everyone else does (or vice versa)?
- What in the data is "flat" — and therefore probably hiding two things cancelling out?

### Jobs lens (unmet / adjacent jobs)
*Pair with detector 08 (unmet-adjacent-job).*
- What do users export, screenshot, copy out, or paste into another tool?
- What workaround do power users describe with pride? (Workarounds are unbuilt features.)
- Which segment loves the product for a reason you never designed for?

### Friction lens (micro-friction & delight)
*Pair with detector 13 (micro-friction-rage).*
- Where do users hesitate, repeat a step, or apologize ("I always mess this up")?
- What tiny moment makes a user smile or say "oh nice"? (Delight gaps are diamonds too.)
- What is one tap too many on the most-used path?

### Value-capture lens (value-wedge / monetization)
*Pair with detectors 04 (pricing-value-mismatch), 14 (underpriced-power-user).*
- Who gets outsized value for the price they pay?
- What would your happiest users pay more for — and are you giving it away?
- What outcome (not feature) would a client write a bigger check for?

## The disconfirmation gate

**Front-and-center, non-optional.** Generating plausible candidates is easy and worthless. Before any
candidate becomes a diamond, answer three questions:

1. **What would make this fake?** Name the specific way this could be a coincidence, an artifact, or a
   marker of users who would have behaved that way regardless.
2. **What is the cheapest test that would kill it?** A survey, five user calls, a one-week holdout, a
   single query on a held-out time window — the smallest thing that could disprove it.
3. **What evidence would exist if it were real but I don't see?** If a value-wedge is real, you'd expect
   upgrade-page visits, support asks, or competitor-comparison mentions. Their absence is a warning.

A candidate that survives all three → a **scored diamond**. One that fails → logged as **fool's gold**
with the reason, so the team does not rediscover and re-chase it next quarter.

> **Fool's-gold example.** "Users who use the CSV export retain 30% better — export is our killer
> feature, let's build more export formats." Disconfirmation: *what would make this fake?* Heavy-export
> users may simply be the most engaged users, who retain better for unrelated reasons (reverse causation —
> see detector 07). Cheapest test: check whether export *precedes* the retention lift or merely
> co-occurs. It co-occurs. **Logged as fool's gold**; do not build export formats.

## Diamond scoring

Rank surviving diamonds with the same formula the analytics radar uses (kept numerically identical so a
radar `diamond_score` and a hand-scored diamond mean the same thing):

```
diamond_score = magnitude × addressability × evidence_strength × value_signal × differentiation
```

The first three are the existing leverage formula (`pmf-insight-engine.md`). The two new dimensions:

| Dimension | Question | Bands (high=3 / medium=2 / low=1) |
|-----------|----------|-----------------------------------|
| **value_signal** | Willingness-to-pay / outcome value if acted on | high = users will pay / a client outcome; low = nice but no money |
| **differentiation** | Moat vs parity | high = hard to copy / compounding; low = a rival ships it in a week |

Two failure shapes the new dimensions catch:
- A **real-but-worthless curiosity** scores near zero on `value_signal` — true, reproducible, and not
  worth a sprint. The score sinks it even if magnitude is high.
- A **real-but-copyable** detail scores low on `differentiation` — flag it **"ship fast, no moat"**:
  worth doing quickly, not worth a strategic bet (e.g. a micro-friction fix from detector 13).

Pick the single highest-scoring diamond. One diamond → one bet.

## The Diamond Brief

The output. A compact summary that feeds the existing `assets/pmf-bet-memo-template.md` field-for-field —
do not invent new bet machinery.

```
DIAMOND BRIEF
- Diamond:            <one sentence: the non-obvious detail>
- Substrate / lens:   <statistical | adjacent-job | micro-friction | value-wedge> via <lens>
- Found by:           <detector NN  |  zero-data lens question>
- Score:              magnitude=<H/M/L> addressability=<H/M/L> evidence=<H/M/L>
                      value_signal=<H/M/L> differentiation=<H/M/L>  → diamond_score=<n>
- Disconfirmation:    what would make it fake / cheapest test / expected-but-missing evidence
- Verdict:            DIAMOND (survived)  |  FOOL'S GOLD (reason)
- Cheapest next test: <the single experiment that would confirm or kill it>
```

**Convert to bet** — map the Brief into the bet memo by field name:

| Diamond Brief field | Bet memo section |
|---------------------|------------------|
| Found by (detector / lens) | §0 Linked detector(s) |
| Diamond + Substrate/lens | §1 The blind spot (quote the detector row; name what blended dashboards missed) |
| Cheapest next test → the change | §2 The hypothesis / §3 The bet |
| value_signal | §4 Success metric (a value-wedge diamond's metric is revenue/expansion, not just engagement) |
| Disconfirmation "cheapest test that kills it" | §5 Kill criterion |
| Found-by + paired detectors | §8 Cross-detector check |

## Worked example

Starting from a radar where detector **14-underpriced-power-user** emitted against the sample product.

**Candidate (value-capture lens).** A cohort of ~60 paying users on the cheapest paid tier ("Starter,"
$8/mo) run 4.1× the median paid user's intensity. Value-capture lens question — *"who gets outsized value
for the price they pay?"* — points straight at them.

**Disconfirmation gate.**
1. *What would make this fake?* They might churn the moment the price rises — high intensity could mean
   "extracting everything before they leave," not durable value (reverse-causation, cross-check detector
   07). 2. *Cheapest test that kills it?* A holdout upgrade-offer to 20 of them, plus a one-question
   price-sensitivity survey. 3. *Expected-but-missing evidence?* If they truly value the product, expect
   upgrade-page visits or "can I get more X" support tickets — and those **are** present (12 tickets last
   month). Survives. → **DIAMOND.**

**A second candidate, logged as fool's gold.** "Starter users who hit the rate limit retain better — the
rate limit drives engagement, let's lower it for everyone." Disconfirmation: lowering the limit for
low-intensity users would just annoy them; the retention lift is specific to *already-heavy* users.
Expected-but-missing evidence: no broad demand for the limit as a feature. **FOOL'S GOLD** — do not ship.

**Diamond score.** magnitude=H(3), addressability=H(3), evidence=M(2), value_signal=H(3),
differentiation=M(2) → leverage 18 × value 3 × moat 2, ranked top of the radar's value-wedge rows.

**Diamond Brief → bet.**
```
- Diamond:            ~60 Starter-tier users run 4.1x median intensity — paid value we don't capture.
- Substrate / lens:   value-wedge via value-capture lens
- Found by:           14-underpriced-power-user
- Score:              mag=H addr=H ev=M value_signal=H differentiation=M → high
- Disconfirmation:    fake if they churn on price; test = 20-user holdout upgrade-offer + price survey;
                      missing-evidence check passed (12 "want more" tickets present)
- Verdict:            DIAMOND
- Cheapest next test: holdout upgrade-offer to 20 users at a usage-aligned tier
```
This maps to a bet memo: §1 quotes the detector row; §2 hypothesizes a usage-aligned tier lifts ARPU for
the cohort; §4's success metric is expansion revenue (value_signal=high makes revenue the right metric,
not engagement); §5's kill criterion is the holdout offer's take-rate floor by the decision date.

## Cross-links

- Detection tier and the statistical methods behind detectors 11–14:
  `marketing-product-analytics/references/micro-signal-methods.md`.
- The engine, leverage formula, and radar that produce `diamond_score`:
  `marketing-product-analytics/assets/pmf-insight-engine.md`.
- The bet target: `assets/pmf-bet-memo-template.md` (one diamond → one bet → one kill criterion).
