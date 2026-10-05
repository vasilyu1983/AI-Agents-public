---
name: research-arxiv-scout
description: "Discovers and triages recent arXiv papers for AI/ML, agents, and software/QA. Use when scouting categories, arXiv IDs, or source lists."
compatibility: Portable core. arXiv API attribution required in any output that uses arXiv data.
version: "1.2"
last_validated: 2026-07-11
---

# research-arxiv-scout

Use arXiv as a discovery layer for recent research, then produce repo-friendly outputs (ranked recommendations and `02_sources-*.json`-style entries) without fabricating metrics.

## Required attribution (arXiv API terms of use)

Include the following line in any output that uses arXiv data:

Thank you to arXiv for use of its open access interoperability.

Source: [arXiv API Access](https://info.arxiv.org/help/api/index.html). The separate [API Terms of Use](https://info.arxiv.org/help/api/tou.html) covers request limits and permitted use.

## Quick Reference

| Task | Inputs | Deliverable | Use these files |
| --- | --- | --- | --- |
| Scout for a known skill | Skill name | Ranked list + actions | `config.yaml`, `assets/recommendation-output-template.md` |
| Scout for a topic | Topic + categories | Ranked list + actions | `references/category-taxonomy.md` |
| Summarize one paper | arXiv ID | Single-paper summary | `references/arxiv-api-guide.md` |
| Propose sources updates | Target path | `02_sources-*.json` entries | `assets/sources-json-template.md` |
| Mine HCI/CSCW retention papers (killer-feature bundle handoff) | Commercial product / candidate feature_id | Rows on shared bundle ledger | `references/product-retention-categories.md`, `config.yaml` key `killer-feature-retention` |

## Layered opportunity handoff

Use the opportunity evidence layers when this scan supports area discovery. Contribute L7 feasible delivery and L4 timing where a dated capability change is relevant. Return the original study ID, tested task, baseline, reproducibility, cost and transfer limits. HCI findings may inform L9 repeat-value hypotheses only for a matched job/population; do not transfer another product’s retention or willingness to pay to the new offer. Pure paper triage stays here without requiring commercial gates.

Carry source and underlying event IDs, dates, scope, supportive/mixed/adverse/unknown direction, evidence basis, counterevidence and the decisive unknown into the comparison worksheet. The same event appearing in several layers remains one event. No scout score, source count or convergence label passes a commercial gate; retain missing and adverse evidence in the handoff.

## Workflow

### 1) Map target to categories and keywords

- If the target matches a key in `config.yaml`, use its categories, keywords, and time window.
- Otherwise, pick 1-4 arXiv categories and 3-8 keywords using `references/category-taxonomy.md`.

### 2) Query arXiv (metadata only)

- Use `references/arxiv-api-guide.md` to build queries for `export.arxiv.org/api/query`.
- Put the time window in the query as a `submittedDate:[YYYYMMDDTTTT TO YYYYMMDDTTTT]` range (GMT) so each window returns its own results; prefer `sortBy=submittedDate` and `sortOrder=descending` when scouting recent work.
- Read `opensearch:totalResults` from the first page and report coverage as fetched/total for every query. If the total is larger than you will fetch, narrow the query (categories, terms, shorter window) before paginating. Never describe a first page as "the top of the window": a date-sorted first page is the newest papers, not the best ones.
- For field scans, keep papers whose `arxiv:primary_category` is in your categories and label the rest cross-lists; do not assume `cat:` excludes cross-listed papers.

Generate queries from `config.yaml` rather than hand-building them:

```bash
# List available config keys (skill → categories, window)
python3 scripts/generate_arxiv_scout_queries.py --list-skills

# Resolve categories, keywords, and time window from config.yaml
python3 scripts/generate_arxiv_scout_queries.py --skill ai-agents

# Ad-hoc topic when no config key fits
python3 scripts/generate_arxiv_scout_queries.py --topic "agent memory" \
    --categories cs.AI cs.CL --windows 30d 90d
```

Each emitted query carries its window as a server-side `submittedDate` range and a
`pagination` plan (page size, page cap, stop rule, coverage report, what to do when
the total exceeds the cap, and the primary-category filter). The output also includes
`estimated_min_runtime_seconds` (first pages only) and `estimated_max_runtime_seconds`
(every page) at the arXiv terms-of-use request gap. Execute serially; do not
parallelise to beat it, which is the fastest route to a 429.

Minimal query skeleton (if building by hand):

```text
search_query=cat:cs.AI AND (agents OR "tool use")
sortBy=submittedDate&sortOrder=descending&start=0&max_results=50
```

### 2b) Pre-triage: social-signal cross-reference

Before scoring API results, cross-reference candidate arXiv IDs against:

- **HF Papers** (`huggingface.co/papers`) — daily community highlights and upvotes.
- **alphaXiv** (`alphaxiv.org`) — social layer on arXiv with comments and trending signals.

Flag any paper that appears on either platform as an **attention signal for triage**, never a quality or evidence upgrade. Cross-posts, coordinated launch traffic, and one source syndicating another are not independent corroboration. Also check each candidate's abstract for a GitHub or project-page link; a verified code link can improve Practicality, while Evidence changes only after the evaluation itself is inspected.

### 3) Triage and score

For each candidate paper, extract:

- Title, authors, arXiv ID, submitted date, categories
- Abstract-based relevance to the target
- Implementation signals (only if verified): code repository, dataset, benchmark, reproducibility notes

Do not include citation counts, GitHub stars, conference acceptance, or affiliations unless you can verify them.

**Signal-vs-noise judgment calls (apply before scoring):**

- **Versioned re-announcements.** A paper with `v2`/`v3` in its history and an `updated` date inside your window but a `published` (first-submission) date months or years older is a *revision*, not new work — see `references/arxiv-api-guide.md#version-deduplication`. Sorting by `lastUpdatedDate` will surface these; always cross-check `published` before treating a hit as fresh.
- **Citation-count traps on fresh papers.** A low citation count can reflect indexing and citation lag. Do not grade a recent paper down solely for its count; state its submission date and evaluate its methods instead.
- **Preprint vs. peer-reviewed.** arXiv listing alone does not establish peer review. Verify any venue claim against the venue's record before reporting it; otherwise leave review status unknown.
- **Hype-paper tells.** Down-weight (do not auto-reject, but flag) candidates that combine: (a) marketing-register title/abstract language ("revolutionary", "unprecedented", state-of-the-art claims with no named baseline), (b) benchmarks limited to the authors' own curated dataset with no third-party eval, and (c) heavy same-day cross-posting to HF Papers / alphaXiv / X with upvote counts but no substantive technical discussion in the comments. Community attention (step 2b) is a *volume* signal, not a *quality* signal — read the abstract and, where available, the actual discussion thread before letting upvotes raise a score.
- **Author/lab self-citation and PR-driven timing.** A paper timed to a product launch or funding announcement from the same lab is not disqualifying, but note the coincidence in "Limits/risks" rather than silently treating it as independent validation.

Suggested scoring: Relevance and Practicality on 0-10, Evidence as a grade.

| Dimension | 0-3 | 4-7 | 8-10 |
| --- | --- | --- | --- |
| Relevance | Weak match | Partial match | Direct match |
| Practicality | High lift | Moderate lift | Low lift |

**Evidence** uses `research-scout`'s A-F grade from its [evidence-grade rubric](../research-scout/references/idea-extraction-framework.md#evidence-grades) (benchmarks, baselines, error bars, released code, review status), so a paper graded here keeps the same grade if it moves into a `research-scout` scan. Report the grade next to the two scores; do not fold it into a single number.

### 4) Produce deliverables

- Recommendation report: use `assets/recommendation-output-template.md`
- `02_sources-*.json` entries: use `assets/sources-json-template.md`

### 5) Final checks (before handoff)

- [ ] Attribution line included (above)
- [ ] Time window stated (and matches what you searched)
- [ ] Categories and keywords listed (or referenced via `config.yaml`)
- [ ] All URLs point to abstract pages (`https://arxiv.org/abs/...`)
- [ ] arXiv IDs are exact (no typos, correct year/format)
- [ ] No duplicates in the final shortlist
- [ ] Paper titles/authors match the abstract page
- [ ] Any code links included were verified
- [ ] Any datasets/benchmarks referenced were verified
- [ ] Any conference/venue claims were verified (or omitted)
- [ ] Any impact metrics (citations/stars) were verified (or omitted)
- [ ] No unverified metrics or claims
- [ ] Suggested actions are concrete and repo-specific
- [ ] Target `02_sources-*.json` schema preserved (no reshaping)

- For volatile claims such as dataset size or benchmark results, record when the primary source was read; omit claims you could not verify.

## Killer-Feature Mode (HCI Retention Papers)

Specialized mode that contributes the **`hci_retention_paper`** signal to the bundle's Killer-Feature Convergence Protocol owned by `research-review-mining`.

Search arXiv's `cs.HC`, `cs.CY`, `cs.SI`, and `cs.IR` categories for relevant work. arXiv coverage of HCI venues is incomplete; use `research-scout`'s conference queries when venue coverage matters.

**When to use:** bundle handoff from `research-review-mining` Killer-Feature Mode KF3 asks for the HCI signal; OR you have a candidate `feature_id` and want a rigorous attribution study.

**Workflow delta:**

```text
KF-ARX-1. Map target to the config.yaml key `killer-feature-retention`
          (categories: cs.HC, cs.CY, cs.SI, cs.IR;
           keywords: long-term retention, feature adoption, freemium conversion, ...)
KF-ARX-2. Query arXiv per templates in references/product-retention-categories.md
KF-ARX-3. Triage with the standard Relevance/Practicality scores and evidence grade PLUS the
          "Attribution rigor" dimension defined in that reference
KF-ARX-4. Only papers with rigor>=7 graduate to a row on
          ../research-review-mining/assets/pay-trigger-ledger.tsv
          (signal_type=hci_retention_paper; wtp_strength=strong if causal,
           implicit if correlational only)
KF-ARX-5. Run ../research-review-mining/scripts/converge_killer_features.py
```

Zero qualifying rows is a valid result and does not downgrade other signals in the Convergence Rule.

**References:**
- [references/product-retention-categories.md](references/product-retention-categories.md) — categories, keyword groups, query templates, attribution-rigor scoring, anti-patterns
- ../research-review-mining/references/killer-feature-convergence.md — bundle Convergence Rule
- [config.yaml](config.yaml) — `killer-feature-retention` key

## Navigation

Resources:

- [data/sources.json](data/sources.json) — Official arXiv sources, complementary discovery tools, and the `dead_or_changed` inventory (arXiv request limits, OpenAlex keyless access with an optional key, Semantic Scholar key policy, OpenReview v2, Connected Papers / ResearchRabbit tier changes). Confirm any entry at the operator page before relying on it
- [scripts/generate_arxiv_scout_queries.py](scripts/generate_arxiv_scout_queries.py) — Query generator; resolves categories/keywords/window from `config.yaml` (`--skill`) or an ad-hoc `--topic`. Stdlib only
- [references/arxiv-api-guide.md](references/arxiv-api-guide.md) — API query patterns for `export.arxiv.org/api/query`
- [references/category-taxonomy.md](references/category-taxonomy.md) — Category selection and examples
- [references/product-retention-categories.md](references/product-retention-categories.md) — Killer-feature mode (HCI retention papers) categories + scoring
- [config.yaml](config.yaml) — Project mappings (skill → categories/keywords/time windows)
- [assets/recommendation-output-template.md](assets/recommendation-output-template.md) — Recommendation report template
- [assets/sources-json-template.md](assets/sources-json-template.md) — `02_sources-*.json` entry template

Related skills:

- [`../research-scout/SKILL.md`](../research-scout/SKILL.md) — multi-source research idea mining (arXiv + HF Papers + Semantic Scholar + conferences + industry blogs + curator newsletters). Use it when you want corroboration from independent origins; use this skill when arXiv depth and category taxonomy are the priority.
- [`../research-git/SKILL.md`](../research-git/SKILL.md) — scans public GitHub repos for skills, practices, and code patterns; use it to check a paper's code link or find independent reimplementations.
- [`../ai-deep-research/SKILL.md`](../ai-deep-research/SKILL.md) — deep verification of a contested claim (the Promotion Check hand-off).

## Promotion Check

Before any finding is promoted, run these five checks:

1. Resolve the primary artifact (the paper, the repo at a pinned commit, or the operator's own page), not a summary of it.
2. Copy the claim verbatim from that artifact, with its number, benchmark, or quote. Never restate it from memory.
3. Confirm an independent origin: a separate study, reproduction, or team, not a re-post or second channel for the same release.
4. Record the date you checked the artifact.
5. If any check fails, label the finding "unverified" and do not promote it.

For a contested or high-stakes claim, hand off to `ai-deep-research` for its verifier pass.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
