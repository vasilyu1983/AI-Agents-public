# Research Scan: {{topic}} → {{target}}

**Scan date:** {{YYYY-MM-DD}}
**Time windows:** {{30d / 90d / 365d}}
**Sources scanned:** {{arxiv, hf_papers, semantic_scholar, papers_with_code, conferences, industry_blogs, curator_newsletters}}
**Total findings:** {{N}} → after dedupe: {{M}} → after extraction: {{K}}
**Promoted:** {{P}}  **Validate:** {{V}}  **Background:** {{B}}  **Killed:** {{X}}

---

## Executive Shortlist (Top 5 Stealable Ideas)

| # | Idea (mechanism name) | Shape | Evidence | Lift | Cross-source | Score |
|---|----------------------|-------|----------|------|--------------|-------|
| 1 | {{name}} | {{shape}} | {{grade}} | {{low/med/high}} | {{N families}} | {{score}} |
| 2 | … | | | | | |
| 3 | … | | | | | |
| 4 | … | | | | | |
| 5 | … | | | | | |

> Idea cards in `idea-cards/` directory below.

---

## Idea Cards

> One [idea-card.md](idea-card.md) per promoted idea. List them here with summary lines.

### 1. {{Mechanism name}}

{{One-sentence summary. Link to full card.}}

### 2. {{Mechanism name}}

…

---

## Validate Pile

Ideas that didn't promote but are worth a controlled smoke test before discarding:

| Idea | Why not `promote` | What would change the call |
|------|-------------------|---------------------------|
| {{idea}} | {{reason from gate}} | {{independent reproduction / cross-source corroboration / lower compute}} |

## Killed Pile (with reasons)

> Recording kills is informative. Future scans can re-score if signal changes.

| Idea | Trap(s) tripped | One-line reason |
|------|----------------|----------------|
| {{idea}} | {{tags}} | {{reason}} |

## Background (negative results & surveys — not steal candidates)

> `background` rows are not killed: a falsified method you considered is
> information (it saves the next scan from re-litigating it). Surveys/taxonomies
> are context, not stealable units.

| Item | Shape | Why it matters as context |
|------|-------|---------------------------|
| {{negative result}} | negative-result | {{which method/assumption it falsifies}} |
| {{survey}} | survey-or-taxonomy | {{what landscape it maps}} |

---

## Trends

**Emerging methods** (in 30d, sparse in 365d):
- {{idea}} — {{why it's emerging}}

**Cresting methods** (cross-source momentum building):
- {{idea}} — {{which sources picked it up in what order}}

**Mature methods** (stable across all windows, multiple implementations):
- {{idea}} — {{maturity evidence}}

**Declining methods** (mentions falling):
- {{idea}} — {{likely successor}}

---

## Cross-Source Corroboration Map

> Corroboration is keyed on `cluster_id`: ≥2 distinct source families sharing
> one `cluster_id` is what makes an idea promotable.

| Idea (cluster_id) | arXiv | HF Papers | Semantic Scholar | GitHub (research-git) | Conference | Industry blog | Curator |
|------|-------|-----------|------------------|-----------------------|------------|---------------|---------|
| {{idea}} | ✓ | ✓ | {{N citing}} | {{repo}} | {{venue/year}} | {{lab}} | {{curator}} |

---

## Methodology & Limitations

**Sources scanned and time windows:**
- arXiv: categories {{list}}, window {{30d/90d/365d}}
- HF Papers: daily for last {{N}} days
- Semantic Scholar: topic + citation walk
- GitHub (research-git): reimplementation/star signal {{list}} — replaces dead Papers with Code
- Conferences: {{venues + years}}
- Industry blogs: {{labs}}
- Curator newsletters: {{names}}

**Known biases:**
- arXiv: no peer review, English-language and Western-institution skew, self-promotion risk
- HF Papers: LLM/VLM/agents-skewed, daily upvote noise
- Semantic Scholar: citation lag for last 6 months, possible citation gaming; free-email-domain API keys no longer issued (2026)
- GitHub repo signal: star count correlates with hype as much as quality
- Conferences: 6-12 month lag behind preprints
- Industry blogs: corporate selection bias, capability-marketing framing
- Curator newsletters: curator selection bias, recency / hype bias, LLM-skewed

**What this scan did *not* cover:**
- {{e.g., non-English sources, paywalled archives, video / podcast content}}
- {{e.g., specific specialty venues skipped}}

**Trap filter applied:** [known-traps.md](../references/known-traps.md) — 12 traps. Hard kills: trap 11 (`proprietary-component`), trap 12 (`benchmark-gaming`).

---

## Suggested Follow-ups

- [ ] {{Specific smoke-test recipe to run from `recipes.md`}}
- [ ] {{Specific eval to add to existing skill knowledge base}}
- [ ] {{Skill or `02_sources-*.json` file to update}}
- [ ] {{Re-scan in {{N}} days to recheck cresting methods}}

---

_This output uses arXiv data — Thank you to arXiv for use of its open access interoperability._
