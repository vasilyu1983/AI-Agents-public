# Free-First Sourcing Recipe

Decision ladder for source selection in `research-scout`. Start at the top of each ladder rung; only descend when the free option is genuinely insufficient for the task.

---

## Contents

- [The Core Rule](#the-core-rule)
- [Decision Ladder by Source Family](#decision-ladder-by-source-family)
- [When to Pay](#when-to-pay)
- [Evidence Ledger Fields](#evidence-ledger-fields)

---

## The Core Rule

**Free / official-API first.** Escalate to freemium or paid only when the free tier creates a concrete bottleneck (rate, data gap, or time cost) that justifies the expense. Document the justification.

---

## Decision Ladder by Source Family

### Citation Graphs

**Rung 1 — Free:** OpenAlex API (`api.openalex.org`) + Semantic Scholar API (`api.semanticscholar.org`)
- Both require a free API key (register once; takes minutes) — OpenAlex has required one for every request since 2026-02-13 (unkeyed requests get $0.10/day then 409s).
- OpenAlex: full citation edges, author disambiguation, institution data. ~$1/day free credit covers hundreds of queries.
- Semantic Scholar: influential-papers ranking, embedding similarity search. ~1 RPS with key.
- Use for: systematic citation traversal, "what built on this paper?", prior-work mapping.

**Rung 2 — Free with account:** ResearchRabbit (`researchrabbit.ai`) *(Litmaps-acquired 2025-05-08; relaunched freemium ~Oct/Nov 2025; free plan still $0 — 50-input cap, 1 project, no sharing)*
- Requires free account.
- Best for: ongoing monitoring — subscribe to a method family and receive email alerts when new citing papers appear.
- Not suitable for bulk automated queries.

**Rung 3 — Freemium (justify before use):** Connected Papers
- Free plan: 50 inputs/searches.
- Justify escalation when: a new subfield needs visual orientation and the graph layout genuinely saves exploration time vs. traversing raw citation lists.
- Do not use for automated pipelines; reserve for manual exploratory sessions.

**Do not use:** Papers with Code citation data (dead Jul 2025).

---

### Paper Discovery

**Rung 1 — Free:** HF Papers (`huggingface.co/papers`) + arXiv export API
- HF Papers: best daily signal for LLM/VLM/agent work; community-curated with engagement signal.
- arXiv API: broadest coverage; enforce 1 req/3s; use categories to narrow (cs.AI, cs.CL, cs.LG, cs.SE).
- Together these cover >90% of AI/ML preprint discovery needs at zero cost.

**Rung 2 — Free:** Emergent Mind (`emergentmind.com`)
- Social traction signal (X/Reddit/GitHub cross-reference on arXiv papers).
- Use when you need method-popularity signal before citation accumulation — replaces the PwC "trending" function.

**Rung 3 — Free:** alphaXiv (`alphaxiv.org`)
- Community discussion layer; useful for surfacing flagged issues, critiques, and corroboration on specific papers.

**Rung 4 — Freemium (justify before use):** Elicit, Consensus *(re-verified 2026-07-11; exact free-tier caps vary by source and move fast — confirm at the vendor pricing page before relying on them)*
- Elicit: AI-assisted systematic review / claim extraction over large paper sets. Free Basic now ≈ unlimited search/summaries/full-text chat (only Research Agent and Research Reports are usage-capped on Free — this replaced the old "5,000 one-time credits" model); paid Pro $49/mo, Scale $169/mo.
- Consensus: semantic search with evidence-quality tags; good for yes/no empirical questions. Free ≈ unlimited basic searches with ~10 capped monthly AI analyses; paid Pro ~$10/mo, Deep ~$45/mo.
- **Justify escalation when:** you need structured evidence extraction across 50+ papers and manual extraction would take longer than the setup plus subscription cost (verify current pricing first).
- **Do not escalate for:** standard method-scouting tasks where HF Papers + arXiv + 2 newsletters covers the space adequately.

---

### Literature Synthesis / Curator Signal

**Rung 1 — Free:** Lilian Weng Lil'Log, Eugene Yan, Simon Willison, The Batch, Import AI, Chip Huyen, Karpathy blog
- All free, no account required. High signal-to-noise. Start here for synthesized understanding.

**Rung 2 — Freemium:** Sebastian Raschka (Ahead of AI), Latent Space
- Free tiers cover most content. Paid tiers unlock archives and priority posts.
- Justify upgrade only if you need systematic access to full archives for a literature review.

---

### Conference Proceedings

**Rung 1 — Free:** NeurIPS, ICML/PMLR, ICLR/OpenReview, ACL Anthology, USENIX
- Fully open access. No account, no paywall on full PDFs.
- USENIX specifically fills the systems/SWE gap (OSDI, NSDI, ATC, Security).

**Rung 2 — Free abstracts, paywalled PDFs:** KDD, ICSE, FSE (via ACM Digital Library)
- Abstracts and metadata are free. PDFs require ACM DL access (institutional or $15/paper).
- For method-scouting: abstract + arXiv preprint (if authors posted one) is usually sufficient. Check arXiv for author-posted versions before paying.

**Never pay for:** Papers that have arXiv preprints. Check `arxiv.org/search/?searchtype=all&query=<title>` before accessing paywalled PDFs.

---

### API Rate Management (Cross-Family)

| Source | Free rate | Key required | Backoff strategy |
|--------|-----------|--------------|-----------------|
| arXiv export API | 1 req / 3s, 1 connection | No | Fixed 3s gap; no parallelism |
| Semantic Scholar | ~1 RPS authed | Recommended | Exponential backoff on 429 (2^n s, max 60s) |
| OpenAlex | ~10 req/s max with key (credit-metered, not just rate-limited) | Yes (mandatory since 2026-02-13) | Exponential backoff on 429; also budget the $-credit, not just the rate — list/search/semantic calls consume the $1/day free credit even under the rate cap |
| HF Papers | No documented limit | No | Polite 1s gap |
| GitHub (via research-git) | 5000 req/hr authed | Yes (free) | Per `research-git` defaults |

---

## Escalation Justification Template

When escalating beyond Rung 1, record the justification before spending:

```
Source: [name]
Escalation rung: [2 / 3 / paid]
Bottleneck: [rate limit / data gap / time cost]
Papers/queries needed: [N]
Free alternative tried: [yes/no — result]
Cost estimate: [$X/mo or one-time]
Time saved vs. free alternative: [estimate]
Decision: [proceed / use free alternative]
```

Minimum bar for paid escalation: the time saved must exceed the cost at a rate of at least $50/hr equivalent. For most research-scout tasks under 200 papers, the free tier is sufficient.
