# Mode D — Killer-Feature Mining (OSS clones + comparison matrices)

## Table of Contents

- [When to use this mode](#when-to-use-this-mode)
- [What this mode does NOT do](#what-this-mode-does-not-do)
- [Target signal taxonomy](#target-signal-taxonomy)
- [Discovery query patterns](#discovery-query-patterns)
- [Extraction workflow](#extraction-workflow)
- [LLM extraction prompts](#llm-extraction-prompts)
- [Anti-patterns specific to Mode D](#anti-patterns-specific-to-mode-d)
- [Where Mode D's output goes](#where-mode-ds-output-goes)
- [Honest precision](#honest-precision)

Specialized mode for contributing the **`oss_clone_focus`** signal to the bundle's Killer-Feature Convergence Protocol owned by `startup-review-mining`.

**The premise.** When developers spend nights/weekends building an OSS clone of a commercial product, they pick which features to replicate. They almost never reimplement the full surface — they reimplement the **one or two features they consider load-bearing for the use case**. That choice is a strong (and very cheap to extract) signal about which features the market sees as the monetizable core.

Examples that paid back the bundle:
- `supabase/supabase` README: "Firebase, but open source" — replicates Auth + Realtime Postgres + Storage. Skips: hosting, ML, analytics, crash reporting. Signal: **Firebase's monetizable core is auth + realtime DB**, not the long tail.
- `plausible/analytics`: replicates a single Goals + page-view + UTM dashboard. Skips: funnels, cohorts, session recording. Signal: **GA's killer feature for the SMB segment is the dashboard, not the analytics depth.**
- `n8n-io/n8n`: replicates the visual workflow builder + 400 integrations. Signal: **Zapier's monetizable core is the integration count + visual builder, not the AI features.**

The signal is so strong because it's **revealed preference under cost** — the OSS author has to ship the feature, not just talk about it.

---

## When to use this mode

- A bundle handoff from `startup-review-mining` Killer-Feature Mode KF4 asks for the OSS clone signal
- You're researching a commercial product and want to see what the OSS world considers its essential feature(s)
- You have a candidate `feature_id` and want to check if any OSS clone explicitly markets it as the load-bearing feature

## What this mode does NOT do

- Mode D does **not** decide whether a feature is the killer feature. It contributes **one** of the six signal types. The Convergence Rule in `../../startup-review-mining/references/killer-feature-convergence.md` (≥3 signals + ≥1 explicit/strong WTP) does the deciding.
- Mode D does **not** extract code patterns from the OSS clone — that's Mode C. Mode D only mines the **focus signal**: which features were chosen for replication, which were skipped, and (when present) which features the README explicitly attributes monetizability to.

---

## Target signal taxonomy

| Sub-signal | Where it appears | Strength |
|------------|------------------|----------|
| README banner: "Open source alternative to {{commercial}}" + named feature list | `README.md` top section | strong |
| Comparison matrix table in README (us vs {{commercial}}) | README "Comparison" / "Why X over Y" section | strong (the rows the author *included*; the rows they *omitted* are also signal) |
| `/why-{{commercial-product}}` page or docs section | `docs/`, `website/`, `apps/landing/` | strong |
| Engineering blog post titled "How we cloned the X feature of {{commercial}}" | repo's blog, dev.to crossposts linked from README | medium |
| Issue label `feature:parity` or `parity-with-{{commercial}}` with multiple open issues | GitHub Issues | medium |
| GitHub Discussion: "what should we build next?" with feature votes ranked by emoji reactions | Discussions tab | medium (proxy for community demand) |
| "Limitations vs {{commercial}}" section in README | README bottom / docs | strong inverse (features the OSS *explicitly* didn't build are often non-monetizable — useful for ruling out) |

The OSS comparison matrix in particular often **omits** rows that the commercial product markets heavily, because the OSS author found those rows weren't load-bearing for actual users. That omission is signal.

---

## Discovery query patterns

For a target commercial product `{{commercial}}`:

```bash
# Direct clone repos
gh search repos "$commercial alternative" --sort stars --limit 25 --archived=false --json fullName,description,stargazersCount
gh search repos "open source $commercial" --sort stars --limit 25 --archived=false
gh search repos "self-hosted $commercial" --sort stars --limit 25 --archived=false

# Topic-based
gh search repos --topic "$commercial-alternative" --limit 20
gh search repos --topic "alternative-to-$commercial" --limit 20

# README comparison matrices (code search — beware 9 req/min limit, see code-search-syntax.md)
gh search code "vs $commercial" path:README.md --limit 30
gh search code "alternative to $commercial" path:README.md --limit 30
```

For a category-wide scan (when you don't have a target product yet but a target category like "analytics"):

```bash
gh search repos "$category alternative open source" --sort stars --limit 25
gh search repos "$category self-hosted" --sort stars --limit 25
```

Rank candidates by stars, then triage with [discovery-protocol.md](discovery-protocol.md) signals. The bundle expects 3-5 OSS clones reviewed per target product.

---

## Extraction workflow

For each shortlisted OSS clone:

```text
KF-OSS-1. FETCH
          - scripts/fetch_repo_assets.sh <owner>/<repo> docs/research/<scan>/raw/ --kind killer-feature
          - Pulls: README.md, docs/, website/ landing pages, package.json/Cargo.toml/etc
            (for "feature flag" enumeration), CHANGELOG.md (for what shipped first =
            what was perceived as load-bearing at launch)

KF-OSS-2. EXTRACT focus signals (LLM)
          - Feed README + landing page to LLM prompt §1 below
          - Output JSONL: {feature_name, evidence_type, evidence_quote, target_commercial, confidence}

KF-OSS-3. EXTRACT omissions (LLM, inverse signal)
          - Feed README "Limitations" section (if present) + comparison matrix to LLM prompt §2 below
          - Output JSONL of features explicitly NOT replicated — these become DOWNGRADING evidence
            for those feature_ids in the convergence ledger

KF-OSS-4. APPEND to shared ledger
          - For each "included" feature, append a row to
            ../../startup-review-mining/assets/pay-trigger-ledger.tsv with:
              signal_type   = oss_clone_focus
              wtp_quote     = the README/landing-page quote
              wtp_strength  = strong (if "we built X because users pay for it" type wording)
                              implicit (if the feature is just present without monetization framing)
              source_type   = github_repo
              llm_method    = oss_clone_readme_extraction
              homepage_marketed = (leave blank — not the right field for OSS)

KF-OSS-5. HAND OFF to convergence
          - Call ../../startup-review-mining/scripts/converge_killer_features.py
          - The aggregator will look for 3-of-6 signal-type convergence including oss_clone_focus
```

---

## LLM extraction prompts

These are Mode D-specific. The general WTP/convergence prompts live in `../../startup-review-mining/references/llm-extraction-prompts.md`.

### §1 — OSS clone focus extraction

```
SYSTEM: You are extracting the "killer-feature focus" signal from an open-source
clone of a commercial product. Your job is to identify which features the OSS
author chose to replicate, and surface evidence about why.

INPUT_README: <full README.md + first landing-page markdown if present>
TARGET_COMMERCIAL: <e.g., "Firebase">

OUTPUT: JSONL, one object per claimed-replicated feature. Fields:
  feature_name           — short noun phrase (e.g., "realtime postgres subscriptions")
  evidence_type          — "headline_banner" | "comparison_matrix_row" | "explicit_why" | "feature_table_inclusion"
  evidence_quote         — verbatim quote from README, ≤200 chars
  target_commercial      — the commercial product being cloned
  monetization_framing   — "explicit" if the README says "this is what people pay X for" or similar;
                           "strong" if the README markets the feature as the differentiator vs the commercial;
                           "implicit" if the feature is just present in the matrix with no framing
  confidence             — 0.0–1.0; downweight if the README is LLM-generated, fork-only, or <30d old

RULES:
- temperature 0
- Skip generic infrastructure (auth, hosting, deployment) unless the README
  explicitly frames it as the differentiator
- If multiple OSS clones replicate the same feature, that's stronger signal —
  but record one row per clone, not aggregated
```

### §2 — OSS clone omission extraction (inverse signal)

```
SYSTEM: You are extracting the "killer-feature OMISSION" signal — features
the OSS author explicitly chose NOT to replicate from the commercial product.

INPUT_README_LIMITATIONS: <"Limitations vs X" section, "Not supported" section,
  or comparison matrix rows where the OSS column is empty>
TARGET_COMMERCIAL: <e.g., "Firebase">

OUTPUT: JSONL, one object per omitted feature. Fields:
  feature_name        — short noun phrase
  omission_evidence   — verbatim quote or matrix-row description
  stated_reason       — quote of any stated reason; "(none)" if author just lists it as missing
  classification      — "non_monetizable" if the author says "few users actually need this"
                        "out_of_scope" if the author says "this is a separate product"
                        "deferred" if the author says "we'll get to it"
                        "(unstated)" otherwise

USE: convergence aggregator treats "non_monetizable" omissions as evidence
against promoting that feature_id even if other signals point to it. This is
the bundle's main mechanism for not getting fooled by features that look
talked-about but aren't actually paid for.
```

---

## Anti-patterns specific to Mode D

| Anti-pattern | Why it fools you | Counter |
|--------------|------------------|---------|
| The OSS clone is itself a SaaS competitor (sells hosted version) | Its feature choices reflect what *it* wants to monetize, not what the original commercial product is paid for | Prefer truly community-maintained OSS clones; downgrade signal weight when the same repo's owner ships a paid hosted tier |
| Fresh repo, fork-only, no commits | LLM-generated shell | Phase 0 triage: skip repos <90 days old with no contributor history |
| Comparison matrix copied from a third-party "alternativeto.net"-style site | Author didn't make the choice, just transcribed it | Spot-check the matrix wording against alternativeto.net for the target — if it matches, downgrade |
| README says "we replicate {{feature}}" but the code doesn't actually ship it | Aspirational README | Spot-check: does the feature appear in the changelog before any of the marketed examples? |
| Multiple OSS clones from the same maintainer (e.g., all by one author farming the niche) | Looks like multi-signal convergence but is one author's bet | Convergence Rule counts repos by distinct owners only |

---

## Where Mode D's output goes

- **Shared ledger row** with `signal_type=oss_clone_focus` → contributes to the 3-of-6 Convergence Rule
- **Omission rows** (Prompt §2 output) → optional but valuable; reduce the score of feature_ids that other signals overweight
- **Research pack** at `docs/research/YYYY-MM-DD-killer-feature-<product>-scan.md` documenting the OSS clones reviewed, the focus signals extracted, and which feature_ids appeared most/least often

The convergence aggregator is owned by `startup-review-mining`; this skill only contributes one of the six signal types.

---

## Honest precision

OSS clone focus is the **most reliable single signal** in the bundle for B2B developer tools, infrastructure products, and dev-facing SaaS — the OSS author community is dense and self-selects for the same use cases as paying buyers.

It is the **least reliable signal** for:
- Consumer mobile apps (no OSS clones exist for most; the few that do are niche)
- Vertical enterprise software (CRM, ERP, finance) — OSS authors don't replicate procurement-driven features
- Brand-driven consumer SaaS (Calm, Headspace, Duolingo) — the killer "feature" is brand/content, not codeable

Cross-reference the precision ceiling table in [`../../startup-review-mining/references/killer-feature-convergence.md`](../../startup-review-mining/references/killer-feature-convergence.md).
