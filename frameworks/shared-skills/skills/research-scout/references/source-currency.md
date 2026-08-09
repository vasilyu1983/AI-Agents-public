# Source Currency 2026 — Jul-2026 Verified Sweep

Reference for `research-scout`. Tracks verified status of all sources; last re-verified against primary sources on 2026-07-11 (supersedes the 2026-05-18 sweep — corrected the OpenAlex mandate date and ResearchRabbit acquisition date, and refreshed Elicit pricing, all of which had drifted).
Use alongside `data/sources.json` (canonical) — this file adds structured rationale and the anti-pattern catalog. Commercial-tool prices and free-tier caps move fast (weeks, not months) — treat any $-figure here as "as of 2026-07-11, verify at the vendor's own pricing page" rather than a durable fact.

---

## Contents

- [Verified Status Table](#verified-status-table)
- [May-2026 Structural Shifts](#may-2026-structural-shifts)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
- [Maintenance Rules](#maintenance-rules)

---

## Verified Status Table

| Source | access_tier | status_2026 | Note |
|--------|-------------|-------------|------|
| arXiv API Documentation | free | alive | |
| arXiv API Terms of Use | free | alive | |
| arXiv Category Taxonomy | free | alive | |
| arXiv export API endpoint | free | **changed** | Hard 1 req/3s; stricter 429 from Feb 2026 |
| alphaXiv | free | alive | |
| Hugging Face Papers | free | alive | |
| HF Papers Trending | free | alive | Also receives PwC 301-redirect traffic |
| Daily Papers RSS | free | alive | |
| Semantic Scholar API | freemium | **changed** | API key officially recommended; ~1 RPS authed; exponential backoff required |
| Semantic Scholar Search | free | alive | |
| OpenAlex | freemium | **changed** | API key mandatory since 2026-02-13 (corrected from an earlier 02-24 note); keyed=$1/day free credit, unkeyed=$0.10/day then 409s |
| Connected Papers | freemium | **changed** | Free plan capped at 50 inputs/searches since 2025 |
| Papers with Code (archive) | free | **dead** | Meta shutdown Jul 2025; PwC.com → HF Trending; GitHub dataset frozen |
| NeurIPS Proceedings | free | alive | |
| ICML Proceedings (PMLR) | free | alive | |
| ICLR / OpenReview | free | **changed** | OpenReview API v2 mandatory; v1 deprecated |
| ACL Anthology | free | alive | |
| KDD Proceedings | free | alive | |
| ICSE Proceedings | free | alive | |
| FSE Proceedings | free | alive | |
| USENIX Open Access Proceedings | free | alive | New in 2026 sweep; systems/SWE gap filled |
| Anthropic Research | free | **changed** | Expanded: alignment.anthropic.com (Mar 2026) + red.anthropic.com |
| Anthropic Alignment Science Blog | free | alive | New Mar 2026 |
| OpenAI Research | free | alive | |
| Google DeepMind Blog | free | alive | Canonical URL: deepmind.google/blog/ |
| Google Research Blog | free | alive | |
| Meta AI Research | free | alive | |
| Microsoft Research Blog | free | alive | |
| Apple Machine Learning Research | free | alive | |
| Hugging Face Blog | free | alive | |
| Distill.pub (archive) | free | **dead** | Indefinite hiatus since 2021; no resumption through May 2026 |
| AI Alignment Forum | free | alive | New in 2026 sweep |
| Lilian Weng's Lil'Log | free | alive | |
| Sebastian Raschka - Ahead of AI | freemium | alive | |
| Eugene Yan - eugeneyan.com | free | alive | Author now at Anthropic |
| Latent Space | freemium | alive | |
| Simon Willison - simonwillison.net | free | alive | |
| The Batch (DeepLearning.AI) | free | alive | Canonical URL: deeplearning.ai/the-batch |
| Import AI (Jack Clark) | free | alive | |
| Chip Huyen - huyenchip.com | free | alive | |
| Andrej Karpathy blog | free | **changed** | URL moved to karpathy.bearblog.dev/blog/ (also karpathy.substack.com) |
| aimodels.fyi | free | alive | New in 2026 sweep |
| Emergent Mind | free | alive | New in 2026 sweep; partial PwC replacement |
| ACM Reproducibility Badging | free | alive | |
| ML Reproducibility Checklist | free | alive | |
| Goodhart's Law reference | free | alive | |
| Elicit | freemium | **changed** | Re-verified Jul-2026; pricing overhauled — free tier now unlimited search/summaries/chat (only Research Agent/Reports capped); paid Pro $49/mo, Scale $169/mo. Supersedes stale "5,000 one-time credits, $12/mo" figures |
| Consensus | freemium | alive | Verified Jul-2026; free ≈unlimited basic search + ~10 capped monthly AI analyses; Pro ~$10/mo, Deep ~$45/mo |
| ResearchRabbit | freemium | changed | Re-verified Jul-2026; acquired by Litmaps 2025-05-08 (date corrected — earlier note said 2026), relaunched freemium ~Oct/Nov 2025; free plan still $0 |

---

## Structural Shifts by Sweep Date

### Jul-2026 sweep corrections

Re-verifying against primary sources on 2026-07-11 (one month after the last sweep) caught three drifted facts that had propagated from the May/Jun-2026 sweeps — a reminder that even a recently-validated skill accumulates small errors and needs re-checking, not just re-dating:

1. **OpenAlex mandate date was wrong by 11 days.** Earlier notes said the API-key mandate started 2026-02-24; the OpenAlex team's own Google Groups announcement fixes the deadline at **2026-02-13**. Corrected throughout this file and `data/sources.json`.
2. **Elicit pricing had actually changed**, not just aged. Elicit moved from a "5,000 one-time credits" free tier to an unlimited-search/summaries/chat free tier (only Research Agent/Reports are capped), and repriced Pro from ~$12/mo to $49/mo. The old figures were still in `data/sources.json` as if current.
3. **ResearchRabbit's Litmaps acquisition date was wrong by a year.** It closed 2025-05-08, not "2026" as an earlier note implied — the freemium relaunch (Oct/Nov 2025) is a separate, later event from the acquisition itself.

See [AP-6](#ap-6-citing-commercial-tool-pricing-as-a-durable-fact) for the general pattern this reveals about commercial-tool facts.

### Papers with Code → Dead (Jul 2025)

Meta shut down Papers with Code in July 2025. `paperswithcode.com` now 301-redirects to HF Trending Papers. The GitHub dataset (`paperswithcode/paperswithcode-data`) is frozen.

**Replacement path:** For live reproducibility signal, use HF Papers Trending + Emergent Mind (social traction on arXiv papers) + direct GitHub search via `research-git`. For benchmark comparisons, use the frozen archive for historical context only.

### OpenAlex and Connected Papers → Now Freemium

Two previously-free citation graph tools shifted models in 2025-2026:

- **OpenAlex**: API key mandatory since 2026-02-13 (primary-source-verified 2026-07-11; the "02-24" date circulating in some earlier notes is wrong — the OpenAlex team's own announcement fixes 02-13 as the deadline). The polite-pool `email=` parameter was retired the same day. A keyed request gets $1/day free credit (covers typical research volume — hundreds of queries/day); an unkeyed request gets $0.10/day, then 409s. Register at openalex.org/settings/api.
- **Connected Papers**: Free plan now caps at 50 inputs/searches. For bulk citation traversal, the OpenAlex API or Semantic Scholar's graph endpoint are free alternatives.

### arXiv Rate Clamp (Feb 2026)

The arXiv export API enforces a hard **1 request / 3 seconds** limit with a single persistent connection per client. The `generate_arxiv_queries.py` script already enforces the 3s gap. Do not parallelize arXiv requests; do not use multiple connections in the same session.

### Anthropic Blog Split (Mar 2026)

Anthropic's research output now spans three properties:
1. `anthropic.com/research` — main research blog (general)
2. `alignment.anthropic.com` — Alignment Science Blog (interpretability, oversight) — launched Mar 2026
3. `red.anthropic.com` — Frontier Red Team blog (safety evaluations)

Include all three when scanning for Anthropic-sourced methods. The alignment blog is the primary venue for interpretability work previously published only on the main site.

### Semantic Scholar API Key Now Standard (2026)

Key officially recommended; register at `semanticscholar.org/product/api`. Authenticated rate: ~1 RPS. Implement exponential backoff — the API returns 429 without warning under burst patterns. The `generate_semantic_scholar_queries.py` script enforces the default 3s gap; do not override this.

### OpenReview API v2 Mandatory

All 2026 ICLR/OpenReview venues use API v2. v1 endpoints are deprecated and may return stale or incomplete data. Update any scripts using v1 endpoints. Official docs: `docs.openreview.net`.

---

## Anti-Pattern Catalog

Each entry: smell → why it fools you → counter-recipe.

---

### AP-1: Counting Papers with Code as a Live Reproducibility Signal

**Smell:** A workflow checks `paperswithcode.com` for "code available" badges or benchmark leaderboard entries, treating the result as current.

**Why it fools you:** PwC shut down in July 2025. The site now redirects to HF Trending. The GitHub dataset is frozen at the 2025 snapshot. Any "code available" signal from PwC reflects the state at shutdown — implementations may have been deleted, forked, or superseded since.

**Counter-recipe:**
1. Replace PwC leaderboard checks with direct GitHub search for the paper title or arXiv ID.
2. Use `research-git` to inspect top-starred implementations for activity date, open issues, and dependency freshness.
3. Use Emergent Mind (`emergentmind.com`) for community-signal cross-reference (X/Reddit/GitHub traction on a paper).
4. For benchmark comparisons, treat PwC data as historical baseline only; verify current SOTA at the conference proceedings or the paper's own GitHub.

---

### AP-2: Treating Distill.pub as Current

**Smell:** A scan includes `distill.pub` as an active source, or a workflow checks it for recent visual explainers.

**Why it fools you:** Distill has been on indefinite hiatus since 2021. The newest article is from 2021. It has not published new content in nearly five years and has confirmed no resumption through May 2026. Including it as a "live" source inflates source count without adding signal.

**Counter-recipe:**
1. Use Distill as a historical archive only — for foundational method visualizations (attention mechanisms, t-SNE, etc.) that remain canonical references.
2. For current visual explainers, use HF Blog (`huggingface.co/blog`) and Eugene Yan's `eugeneyan.com`.
3. Mark Distill entries in findings with `window: pre-2021` and evidence grade capped at B (no recent validation).

---

### AP-3: Citing the Stale Karpathy URL

**Smell:** A workflow or sources file points to `karpathy.github.io` as Karpathy's active blog.

**Why it fools you:** Karpathy migrated from GitHub Pages to Bear Blog. The old URL (`karpathy.github.io`) may still serve cached content or redirect inconsistently, but new posts are only published at `karpathy.bearblog.dev/blog/` and `karpathy.substack.com`. A scan against the old URL will miss all posts after migration.

**Counter-recipe:**
1. Update all references to `https://karpathy.bearblog.dev/blog/` (primary) or `https://karpathy.substack.com` (Substack mirror).
2. In `data/sources.json`, the canonical entry now points to `karpathy.bearblog.dev/blog/`.
3. When scraping/searching for Karpathy content, search both the blog and Substack.

---

### AP-4: Treating OpenAlex or Semantic Scholar as Unlimited and Free

**Smell:** A script issues burst API calls to OpenAlex or Semantic Scholar without rate controls, or treats both as fully free with no key.

**Why it fools you:**
- **OpenAlex** requires an API key since 2026-02-24 and charges usage-based beyond the $1/day free credit. Keyless requests return 401 or degraded results.
- **Semantic Scholar** now officially recommends a key; authenticated rate is ~1 RPS. Unauthenticated burst requests reliably produce 429s.
Both will silently degrade (returning partial results or empty pages) before hard-failing, which means a script can appear to succeed while returning only a fraction of the intended results.

**Counter-recipe:**
1. Register for both API keys (free tier sufficient for most research use).
2. Enforce at minimum 1 second between requests for Semantic Scholar; 3 seconds for arXiv.
3. Implement exponential backoff: on 429, wait 2^n seconds (n = retry count, max 60s).
4. Log response counts per query; alert if a query returns 0 results unexpectedly (distinguish "no papers" from "rate-limited empty response").

---

### AP-5: Over-Paying for Connected Papers When Free Citation Graphs Suffice

**Smell:** A workflow uses Connected Papers as the default citation graph tool, burning through the 50-input free plan limit or paying for the pro tier.

**Why it fools you:** Connected Papers is useful for visual exploration, but its underlying data (citation edges) is available for free through OpenAlex's citation endpoint and Semantic Scholar's paper references API. The paid tier is only justified when the visual graph interface is genuinely the bottleneck, which is rarely true for automated scanning.

**Counter-recipe:**
1. Use OpenAlex `https://api.openalex.org/works/{id}/references` and `cites` endpoints for bulk citation traversal — free with API key.
2. Use Semantic Scholar `GET /graph/v1/paper/{paper_id}/references` for cited-by lookups — free with key.
3. Reserve Connected Papers for manual exploratory sessions where the visual graph layout adds genuine value (e.g., onboarding to an unfamiliar subfield).
4. For automated pipelines, use ResearchRabbit (free, account required) for alert-based citation tracking.

---

### AP-6: Citing Commercial-Tool Pricing as a Durable Fact


**Smell:** A scan report, idea card, or `data/sources.json` entry states a specific dollar figure for Elicit, Consensus, Connected Papers, or ResearchRabbit as if it were stable, without a verification date attached.

**Why it fools you:** Freemium research tools reprice on a cadence closer to a SaaS product than to a research API — Elicit overhauled its entire pricing model (moved from a "5,000 one-time credits" free tier to an "unlimited search/summaries/chat, capped agent runs" free tier, and repriced paid tiers from ~$12/mo to $49/mo) between the May-2026 and Jul-2026 sweeps of this very file. A two-month-old price quote can already be wrong, and third-party pricing-aggregator sites (costbench, aiproductivity.ai, etc.) frequently disagree with each other and with the vendor's own page.

**Counter-recipe:**
1. Never state a commercial-tool price without a date: "$49/mo (verified 2026-07-11 at elicit.com/pricing)", not "$49/mo".
2. Prefer the vendor's own `/pricing` page over aggregator sites; if the vendor page 403s an automated fetch, corroborate across ≥2 independent aggregator sources before citing a number.
3. When packaging an idea card or scan report that references tool cost, add "verify current pricing before acting" rather than presenting the cached figure as current.
4. Re-run this AP-6 check at every scheduled currency sweep (see Maintenance Rules) — commercial-tool pricing is the single fastest-moving fact category in this skill, faster than API deprecations.

---

## Maintenance Rules

1. **Re-verify this file against primary sources at least every 4-6 weeks**, not on a fixed calendar — the Jul-2026 sweep found drift after only ~4 weeks (see [Jul-2026 sweep corrections](#jul-2026-sweep-corrections)). Prioritize `commercial_accelerators` (fastest-moving) and any source with `status_2026: changed` (already known to be in flux).
2. **Verify from the vendor/operator's own primary source first** — official blog posts, changelogs, or the vendor's own pricing/docs page. Only fall back to secondary aggregators (news sites, third-party pricing trackers) when the primary source 403s or is otherwise unreachable, and say so in the note.
3. **Every dated claim gets a re-verification date, not just an origin date.** Prefer "mandatory since 2026-02-13 (re-verified 2026-07-11)" over a bare origin date — the reader needs to know how stale the claim might be, not just when the underlying change happened.
4. **When a sweep finds a factual error in a prior sweep (not just staleness), say so explicitly** with both the wrong and corrected value — silently overwriting an error erases the signal that this file's own verification process needs tightening.
5. **Update `data/sources.json` and this file together.** They must never disagree on a `status_2026` or a dated fact — `sources.json` is canonical for the compact record, this file is canonical for the rationale.
