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
- Before a large pull, look up each API's current key requirement, daily budget, and rate limit on its operator page (OpenAlex: https://help.openalex.org/api/authentication/; Semantic Scholar: https://www.semanticscholar.org/product/api) and pace the scan to what you find.
- OpenAlex: full citation edges, author disambiguation, institution data.
- Semantic Scholar: influential-papers ranking, embedding similarity search.
- Use for: systematic citation traversal, "what built on this paper?", prior-work mapping.

**Rung 2 — Freemium with account:** ResearchRabbit (`researchrabbit.ai`)
- Requires an account; check the current free-plan limits at the vendor page before relying on it.
- Best for: ongoing monitoring — subscribe to a method family and receive email alerts when new citing papers appear.
- Not suitable for bulk automated queries.

**Rung 3 — Freemium (justify before use):** Connected Papers
- The free plan caps searches; check current limits at the vendor page.
- Justify escalation when: a new subfield needs visual orientation and the graph layout genuinely saves exploration time vs. traversing raw citation lists.
- Do not use for automated pipelines; reserve for manual exploratory sessions.

**Do not use:** Papers with Code citation data (the site is retired and its data frozen).

---

### Paper Discovery

**Rung 1 — Free:** HF Papers (`huggingface.co/papers`) + arXiv export API
- HF Papers: best daily signal for LLM/VLM/agent work; community-curated with engagement signal.
- arXiv API: broadest coverage; pace requests to the operator's terms of use (https://info.arxiv.org/help/api/tou.html); use categories to narrow (cs.AI, cs.CL, cs.LG, cs.SE).
- Together these cover most AI/ML preprint discovery needs at zero cost.

**Rung 2 — Free:** Emergent Mind (`emergentmind.com`)
- Social traction signal (X/Reddit/GitHub cross-reference on arXiv papers).
- Use when you need method-popularity signal before citation accumulation — replaces the PwC "trending" function.

**Rung 3 — Free:** alphaXiv (`alphaxiv.org`)
- Community discussion layer; useful for surfacing flagged issues, critiques, and corroboration on specific papers.

**Rung 4 — Freemium (justify before use):** Elicit, Consensus. Free-tier caps and prices change often; read them at each vendor's own pricing page on the day you decide.
- Elicit: AI-assisted systematic review / claim extraction over large paper sets.
- Consensus: semantic search with evidence-quality tags; good for yes/no empirical questions.
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
- Abstracts and metadata are free. PDFs require ACM DL access (institutional or per-paper purchase).
- For method-scouting: abstract + arXiv preprint (if authors posted one) is usually sufficient. Check arXiv for author-posted versions before paying.

**Never pay for:** Papers that have arXiv preprints. Check `arxiv.org/search/?searchtype=all&query=<title>` before accessing paywalled PDFs.

---

### API Rate Management (Cross-Family)

Limits and key rules change, so this table says where to look, not what the numbers are. Read the current values before a large scan and pace to the strictest source.

| Source | Where to read current limits | Pacing rule |
|--------|------------------------------|-------------|
| arXiv export API | https://info.arxiv.org/help/api/tou.html | Single connection, fixed gap from the terms; no parallelism |
| Semantic Scholar | https://www.semanticscholar.org/product/api | Exponential backoff on 429 with a capped wait |
| OpenAlex | https://help.openalex.org/api/authentication/ | Backoff on 429; add a free key if the keyless budget is too small |
| HF Papers | the Hugging Face Hub docs | Polite gap between requests |
| GitHub (via research-git) | `gh api rate_limit` | Per `research-git` |

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
