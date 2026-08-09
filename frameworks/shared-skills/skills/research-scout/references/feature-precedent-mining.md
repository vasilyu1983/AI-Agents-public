# Feature-Precedent Mining (Killer-Feature Mode)

## Table of Contents

- [When to use this mode](#when-to-use-this-mode)
- [What this mode does NOT do](#what-this-mode-does-not-do)
- [Source mix for this mode](#source-mix-for-this-mode)
- [Extraction protocol (killer-feature delta)](#extraction-protocol-killer-feature-delta)
- [The new method shape: `monetizable-feature-pattern`](#the-new-method-shape-monetizable-feature-pattern)
- [Anti-patterns specific to this mode](#anti-patterns-specific-to-this-mode)
- [Honest precision](#honest-precision)

Specialized mode for contributing the **`industry_blog_attribution`** and **`hci_retention_paper`** signals to a downstream feature-convergence protocol.

**The premise.** Research blogs (Anthropic, OpenAI, DeepMind, Google, Meta, MSR, Apple ML, Netflix Tech, Stripe Engineering, Figma Engineering, Linear blog) and HCI/CSCW papers periodically publish post-mortems that explicitly attribute retention, conversion, or revenue to a specific feature. These are the highest-signal source for "this feature is the killer feature" claims because:

1. **They're written by the people who shipped it** (not bystanders).
2. **They typically cite metrics** (retention curves, conversion lift, ARPU delta).
3. **Self-attribution incentive is publishing prestige, not sales** — closer to ground truth than marketing copy.

Examples that paid back the bundle:
- *Figma Engineering* blog 2019 — explicitly attributed Figma's freemium → paid conversion to multiplayer cursors. Signal: `multiplayer_realtime_collaboration` = killer feature in design tool category.
- *Linear blog* on speed-as-a-feature (multiple posts 2021-2023) — attributed enterprise upsell to keyboard-shortcut and sub-50ms responsiveness work. Signal: `perceived_performance` = killer feature in PM tool category.
- *Netflix Tech blog* on "recommendation tuning earns us $1B/year" (2016) — explicit dollar attribution. Signal: `personalized_homepage_carousels` = killer feature in streaming category.
- *Stripe blog* on `radar` machine-learning fraud — explicit ARPU lift. Signal in payments category.

HCI/CSCW papers are a parallel source. They publish year-after-year retention studies that often identify the **single interaction pattern** that predicts long-term use. These are slower but more rigorous than industry blogs.

---

## When to use this mode

- A downstream product-review workflow asks for industry-blog and HCI-paper signals
- You're researching a commercial product and want the highest-credibility attribution signal
- You have a candidate `feature_id` and want to find a published metric-backed claim that the feature drives retention/conversion/revenue

## What this mode does NOT do

- Does **not** decide the killer feature. Contributes 1-2 of the 6 signal types in the Convergence Rule.
- Does **not** mine community pain (use dedicated community-pain and product-review workflows).
- Does **not** mine OSS clone choices (that's `research-git` Mode D).

---

## Source mix for this mode

Reuse the existing scout sources, but **bias the source weight** toward:

| Source family | Weight in this mode | Why |
|---------------|----------------------|------|
| Industry research blogs (Anthropic, OpenAI, DeepMind, Google Research, Meta, MSR, Apple ML) | high — but mostly for AI feature attribution | Researchers explicitly attribute features to retention/revenue |
| Engineering blogs (Netflix Tech, Stripe Engineering, Figma Engineering, Linear, Notion, Airbnb, Uber, Shopify, GitHub, GitLab, Vercel, Dropbox, Slack) | **highest** | This is where "X feature drove Y retention" posts live; not a default source — add explicitly for this mode |
| HCI / CSCW conferences (CHI, CSCW, UIST, IUI) | high | Rigorous long-term retention studies; attribute use patterns to feature design choices |
| Curator newsletters (growth.design, Lenny's Newsletter, Reforge, Andrew Chen's blog) | high | Practitioner synthesis that often surfaces the same attribution claims |
| arXiv | low | Rare to find feature-attribution work; only relevant in AI/ML product category |
| HF Papers | low | Same as arXiv |
| Semantic Scholar | medium | Useful for citation-graph follow-up on a found HCI paper |

To run a scan in this mode, run the standard generators with the engineering-blog list explicitly added:

```bash
python3 scripts/generate_blog_queries.py \
  --domains netflixtechblog.com stripe.com/blog figma.com/blog linear.app/blog \
            notion.so/blog airbnb.io eng.uber.com shopify.engineering github.blog \
            blog.gitlab.com vercel.com/blog dropbox.tech slack.engineering \
  --topic "{{commercial_product}} {{candidate_feature}} retention conversion revenue"

python3 scripts/generate_conference_queries.py \
  --conference chi --year 2024 --topic "{{candidate_feature}} retention long-term use"
python3 scripts/generate_conference_queries.py \
  --conference cscw --year 2024 --topic "{{candidate_feature}}"
```

---

## Extraction protocol (killer-feature delta)

For each found post / paper:

```text
KF-PREC-1. CLASSIFY ATTRIBUTION
           - explicit:  post names a specific feature AND cites a metric
                        (retention delta, conversion delta, ARPU delta, NRR, etc.)
           - strong:    post names a specific feature AND describes a qualitative
                        attribution ("this is why customers stay") with internal
                        author authority (PM, eng lead, founder)
           - implicit:  feature is mentioned in passing as important; no metric,
                        no qualitative claim
           - reject:    feature is mentioned only as a future plan, or attribution
                        is to a competitor's feature

KF-PREC-2. EXTRACT THE FEATURE NOUN
           - Must be specific enough to test (e.g., "multiplayer cursor presence
             in the canvas", not "collaboration")
           - Reject if the noun is the product itself ("Linear's speed" is too
             vague; "sub-50ms response time on keyboard shortcuts" is testable)

KF-PREC-3. EXTRACT THE WTP QUOTE
           - Verbatim, ≤200 chars
           - Should include the metric if explicit, or the qualitative attribution
             if strong

KF-PREC-4. APPEND to shared ledger
           - For industry/engineering-blog finds, append to
             the downstream workflow's pay-trigger ledger with:
               signal_type   = industry_blog_attribution
               wtp_strength  = explicit | strong | implicit per KF-PREC-1
               source_type   = industry_blog
               llm_method    = feature_precedent_extraction
           - For CHI/CSCW/UIST paper finds, append with:
               signal_type   = hci_retention_paper
               source_type   = academic_paper
           - Pin paper_id (DOI or arXiv ID) in the ledger row's notes field

KF-PREC-5. HAND OFF to convergence
           - Invoke the downstream feature-convergence step
```

---

## The new method shape: `monetizable-feature-pattern`

This mode adds an **11th method shape** to the [idea-extraction-framework](idea-extraction-framework.md) catalog, alongside `prompting-pattern`, `architecture-tweak`, etc.

**Definition.** A `monetizable-feature-pattern` finding describes a *product feature* whose presence is empirically tied to retention, conversion, or revenue — at a specific product, in a specific period, with a stated metric.

**Extraction template** (use in `aggregate_research_ideas.py` output and idea-card.md):

- **Feature noun** (testable, specific)
- **Source product** (which commercial product attributed it)
- **Metric quoted** (the number; "qualitative" if no number)
- **Attribution authority** (PM blog post / eng blog post / academic paper / founder talk)
- **Category** (PM tool / payments / design / streaming / etc.)
- **Replicability hypothesis** (would this feature plausibly drive the same metric for a similar product?)
- **Anti-pattern guard** (is this just brand halo? would a competitor copying it actually retain users?)

`monetizable-feature-pattern` findings are **not subject** to the standard `kill` rules in the scoring engine (trap 11, trap 12). The reproducibility model is different: we're not trying to reproduce a research result; we're trying to test whether a single product's feature attribution generalizes. Instead, this shape uses these gates:

- `kill` if Attribution authority = "marketing/PR copy" (not engineering/PM/research)
- `validate` if metric is qualitative only AND no second source corroborates
- `promote` if metric is quantitative AND author has internal authority

---

## Anti-patterns specific to this mode

| Anti-pattern | Why it fools you | Counter |
|--------------|------------------|---------|
| "Our X feature is what users love" in a marketing blog | PR-tinged self-praise | Require either a metric OR a non-marketing author (engineer/PM/founder) — and ideally both |
| Author was paid by the product they're attributing to | Conflict of interest masked as analysis | Spot-check author bio; reject "sponsored" or "in partnership with" |
| Single post making a bold claim with no follow-up | One-off marketing push | Convergence Rule requires ≥3 signal types anyway; this row alone never promotes |
| HCI paper studies use of a feature without attributing causal lift | Pure descriptive work | Read the paper's discussion section: did they actually test causality? If no, downgrade to `implicit` |
| Engineering blog attributes lift to a feature that was actually a price change | Confounded; eng team didn't run the price experiment | Cross-check pricing-page history via Wayback (review-mining script `diff_wayback_pricing.py`) — if pricing changed in the same period, mark the row's confidence as `low` |
| Engineering blog post is >5 years old | Market moved; the feature may no longer be the killer feature even at that product | Mark `observed_at` and let convergence aggregator's stale-row gate (>180 days) downweight |

---

## Honest precision

`industry_blog_attribution` and `hci_retention_paper` are the **highest-credibility single signals** in the bundle when they exist. But they exist much less often than community pain or OSS clones. Mode coverage by product category:

| Category | Likely to find a strong attribution signal? |
|----------|---------------------------------------------|
| Big-tech consumer apps (Netflix, Spotify, Airbnb, Uber) | Yes — engineering blogs publish regularly |
| Big-tech B2B SaaS (Figma, Linear, Notion, Stripe, GitHub, Vercel) | Yes — eng/PM blogs strong |
| Mid-stage startup (Series B/C with a blog) | Sometimes — read the careers page; teams with PMs are more likely to publish attribution posts |
| Early-stage startup (no engineering blog) | No — fall back to OSS clone signal + community pain |
| Vertical enterprise (procurement-driven, e.g., Workday, ServiceNow) | Almost never — attribution is internal; bundle convergence here relies on OSS + community |

When this mode returns 0 strong signals, that's information for the convergence aggregator: it caps the gate at `validate` until at least one strong attribution is found OR three of the other five signals converge.

Cross-reference the downstream workflow's precision-ceiling table before promotion.
