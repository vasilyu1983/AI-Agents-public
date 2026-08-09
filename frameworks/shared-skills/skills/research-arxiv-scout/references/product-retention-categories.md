# Product-Retention Research Categories (Killer-Feature Mode)

## Table of Contents

- [Categories](#categories)
- [Keyword groups](#keyword-groups)
- [Suggested query templates](#suggested-query-templates)
- [Triage delta for killer-feature mode](#triage-delta-for-killer-feature-mode)
- [Honest precision](#honest-precision)

Specialized arXiv category + keyword map for contributing the **`hci_retention_paper`** signal to the bundle's [Killer-Feature Convergence Protocol](../../startup-review-mining/references/killer-feature-convergence.md) owned by `startup-review-mining`.

**Premise.** HCI and CSCW research periodically publishes long-term studies that empirically tie *specific interaction patterns or features* to user retention, engagement, or willingness-to-pay. These are the slowest-but-most-rigorous signal in the bundle. arXiv's `cs.HC` category indexes most of this work; `cs.CY` and `cs.SI` catch adjacent retention/adoption research.

**Note on arXiv coverage:** Many CHI/CSCW/UIST papers are *also* posted to arXiv (`cs.HC`), but a non-trivial fraction is only published through the ACM Digital Library. arXiv coverage is roughly 50-70% of CHI/CSCW for the last 5 years. Use this skill for the arXiv-indexed fraction; use `research-scout` (with `generate_conference_queries.py --conference chi`) for the ACM-only fraction.

---

## Categories

| arXiv code | Name | Why it matters for killer-feature work |
|------------|------|----------------------------------------|
| `cs.HC` | Human-Computer Interaction | Primary — interaction patterns, feature studies, retention research, freemium conversion, paywall design |
| `cs.CY` | Computers and Society | Adoption studies, longitudinal user studies, willingness-to-pay surveys |
| `cs.SI` | Social and Information Networks | Network-effect features (multiplayer, social), engagement loops, virality vs retention separation |
| `cs.IR` | Information Retrieval | Recommendation-feature attribution (Netflix-style "carousel ranking drove $X retention" papers) |

---

## Keyword groups

Use these keyword clusters with the arXiv API. Combine 1 category + 2-4 keywords per query.

### Retention attribution

- "long-term retention" — papers that measure retention beyond a session
- "feature adoption study" — empirical studies of which features drive use
- "freemium conversion" — paywall and pricing-page interaction studies
- "willingness to pay" — survey or behavioral measurement
- "engagement vs retention" — papers separating shallow engagement from deep retention (important — many "engagement" claims don't predict pay)
- "habit formation" — Fogg / BJ-Fogg-derived studies of repeat-use patterns
- "churn study" — empirical churn attribution

### Feature-pattern studies

- "interaction pattern" — generic pattern catalog work
- "feature attribution"
- "multiplayer" / "real-time collaboration" — strong signal in design/PM tool categories
- "personalization" — recommendation-feature attribution
- "notifications" — long-tail retention driver (often over-attributed; cross-check)
- "onboarding" — first-session retention work
- "aha moment" — Sean Ellis / Reforge-derived activation-feature research (a few academic papers exist)
- "magic moment"

### Paywall / pricing interaction

- "paywall design"
- "pricing experiment"
- "trial conversion"
- "subscription churn"

### Anti-patterns (search and REJECT)

These appear in the same queries but are *not* killer-feature signals:

- "dark pattern" — usually a critique paper, not an attribution study
- "addiction" — moral-panic framing, rarely useful attribution
- "engagement maximization" — usually critical/policy, not feature-attribution

---

## Suggested query templates

```text
# CHI/CSCW retention papers attributing a specific feature
search_query=cat:cs.HC AND ("long-term retention" OR "feature adoption" OR "habit formation") AND ({{candidate_feature}} OR {{commercial_product}})
sortBy=submittedDate&sortOrder=descending&max_results=50

# Freemium / paywall studies
search_query=(cat:cs.HC OR cat:cs.CY) AND ("freemium" OR "paywall" OR "willingness to pay") AND ({{category}})
sortBy=submittedDate&sortOrder=descending&max_results=30

# Recommendation-feature attribution (Netflix-style)
search_query=cat:cs.IR AND ("recommendation" AND ("retention" OR "engagement attribution" OR "user lifetime")) AND ({{commercial_product}} OR {{category}})
sortBy=submittedDate&sortOrder=descending&max_results=30

# Network-effect feature studies (multiplayer, social)
search_query=cat:cs.SI AND ("network effect" OR "multiplayer" OR "co-presence") AND ("retention" OR "adoption")
sortBy=submittedDate&sortOrder=descending&max_results=30
```

---

## Triage delta for killer-feature mode

The standard 0-10 scoring in SKILL.md still applies, but add this scoring dimension specific to this mode:

| Dimension | 0-3 | 4-7 | 8-10 |
|-----------|-----|-----|-------|
| **Attribution rigor** | Paper just describes feature use; no causal claim | Paper measures correlation between feature use and retention | Paper runs A/B or natural experiment with causal identification AND names the specific feature |

**Promote-to-ledger rule.** A paper graduates into a row on the shared bundle ledger only if:
- Attribution rigor ≥ 7 (the paper makes a causal-ish claim about a specific feature)
- The feature is described specifically enough to map to a candidate `feature_id` in the bundle
- The paper's product/category overlaps the bundle's target

When a paper passes, append a row to `../../startup-review-mining/assets/pay-trigger-ledger.tsv` with:

```
signal_type        = hci_retention_paper
wtp_strength       = strong (if causal) | implicit (if correlational only)
source_type        = academic_paper
source_url         = https://arxiv.org/abs/<id>
llm_method         = hci_paper_extraction
notes              = arxiv_id=<id>; rigor_score=<n>/10
```

Then run `../../startup-review-mining/scripts/converge_killer_features.py`.

---

## Honest precision

Coverage is sparse but **high credibility per hit**. Expect:

- 0-2 strong rows per scan in a typical category
- Higher hit rate in well-studied categories (note-taking apps, fitness apps, social apps, recommender systems)
- Near-zero hit rate in vertical enterprise software and niche developer tools

When this mode returns 0 strong rows, that's information for the convergence aggregator: the absence of academic attribution is normal for most products, so it should not downgrade other signals. The Convergence Rule already requires only 3 of 6 signal types — this mode often contributes 0, and the protocol assumes that's fine.

See the precision-ceiling table in [`../../startup-review-mining/references/killer-feature-convergence.md`](../../startup-review-mining/references/killer-feature-convergence.md).
