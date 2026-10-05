# Specialist Source Routing for Area Research

This reference maps specialist sources to the existing research and startup
skills. It is an optional source-selection aid for a concrete buyer/problem or
technical uncertainty; it does not turn `research-scout` into a general market
scanner and it does not add source types to the findings aggregator.

The operator pages below were checked on **2026-09-13**. Access, rate limits,
coverage and licence terms can change. Recheck the operator page when a source
is used for a current claim or a product input.

## Contents

- [Two source roles](#two-source-roles)
- [Source-to-angle matrix](#source-to-angle-matrix)
- [Practical routing recipes](#practical-routing-recipes)
- [What goes into the research-scout findings contract](#what-goes-into-the-research-scout-findings-contract)
- [Operator pages checked](#operator-pages-checked)

## Two source roles

Classify the reason for opening a source before collecting anything:

| Role | What it can support | What it cannot establish by itself |
|------|---------------------|------------------------------------|
| **Evidence source** | A documented problem, technical capability, institutional priority, alternative, workflow or constraint | Customer willingness to pay, a reachable buyer, repeat usage or commercial success for a new offer |
| **Product input** | Candidate corpus, API, data feed, text, code or workflow material an app might use | The right to reuse the material, reliable access, a sustainable distribution channel or demand for the resulting product |

Record the source URL, stable record or post identifier, event date, observed
date, role, scope, direct observation, interpretation, limitation and next
test. When handing evidence to the startup bundle, preserve the existing
`source_ids`, `evidence_scope`, direction and unknown fields. A source can be
useful evidence and still be adverse to the idea.

## Source-to-angle matrix

Use the owning skill shown here. `research-scout` remains the owner only for a
research method or framework question; `startup-market-intel` owns area
discovery and `startup-idea-validation` owns the offer decision.

| Source | Useful angle | Owner or handoff | Evidence and product-input boundary |
|--------|--------------|------------------|--------------------------------------|
| **arXiv** | Technical timing, methods, feasibility and failure modes | `research-arxiv-scout` for arXiv-only triage; this skill for cross-source method mining | A preprint supports a feasibility or timing hypothesis. It is not buyer or revenue evidence. The API attribution and rate rules remain in [arxiv-strategy.md](arxiv-strategy.md). |
| **GitHub** | Feasibility, implementation patterns, maintenance, issues and alternatives | `research-git` for repositories and history; `research-painpoint-scanner` for public issues/discussions | Pin a repository commit and inspect licence, activity, dependencies and representative failures. Stars, reported stacks and issue volume are signals, not demand or quality proof. |
| **Stack Exchange** | Repeated domain questions, workarounds, unanswered or poorly answered jobs | `research-painpoint-scanner` for pain; `qa-debugging` for a known solved answer | Select the relevant `site` instead of treating Stack Overflow as the whole network. Questions and answers reveal jobs and friction, not willingness to pay. Do not copy user content into a product without checking the site licence and API/ToS. |
| **Hacker News** | Builder pain, launch reactions, alternative discovery and technical timing | `research-painpoint-scanner` | Treat comments and ranking as a technically selective conversation sample. HN attention is not market size, customer validation or independent corroboration when the same launch is syndicated. |
| **YouTube** | Workflow observation, tutorials, product demonstrations, integration friction and terminology | `research-painpoint-scanner` for practitioner workflow observation; hand area synthesis to `startup-market-intel`, and technical-method questions to `research-scout` or the relevant specialist | Record channel, video URL, publication date, segment or timestamp and whether the material is a tutorial, demo, review, sponsored claim or user workflow. A demonstration shows a claimed workflow; it does not prove frequency, performance or demand. Treat captions/transcripts as source material and verify key claims at the linked primary source. |
| **PubMed Central (PMC)** | Biomedical and health research methods, clinical workflow context and technical feasibility | Conditional health/life-science pass via `life-science-research:research-router-skill` or `ai-deep-research`; area selection remains `startup-market-intel` | PMC contains journal articles, author manuscripts and preprints. Separate peer-reviewed status and article type. Free reading is not blanket reuse permission: use the article licence and official retrieval services for text mining or bulk access. Research relevance is not clinical adoption, procurement or patient demand. |
| **NIH ExPORTER / RePORTER** | Funded research themes, institutions, programmes and timing in health or life sciences | Conditional health/research-market pass via `startup-market-intel` with `ai-deep-research` for synthesis | Funding records describe awarded research activity, not a market purchase or customer commitment. Preserve project and award identifiers, fiscal/award dates and the distinction between research site, grantee and funding institute. |
| **Free Law Project** | US legal-data availability, court-record workflows and legal-tech alternatives | Conditional US legal-tech pass via `startup-market-intel`; use `ai-deep-research` for jurisdiction-bounded synthesis | Confirm jurisdiction, dataset coverage, update cadence, access terms and whether a record is primary law or an interpretation. Public legal data does not remove professional, privacy, licensing or legal-advice constraints. |
| **US Patent and Trademark Office (USPTO)** | Prior-art landscape, crowded claims, technical directions and possible competitors | Conditional invention-heavy pass via `startup-market-intel`; legal interpretation requires a qualified professional | A patent or application is a discovery and prior-art record. It is not proof of market demand, enforceability, freedom to operate or a permission to use an invention. Record publication/application identifiers and jurisdictions. |
| **Ubuntu IRC logs** | Historical Linux/Ubuntu troubleshooting, recurring operational friction and terminology | Conditional Linux/Ubuntu pain pass via `research-painpoint-scanner` | Logs are a time-bound and technically selective sample. Check date, channel, context and whether the workaround still applies. Do not treat a repeated troubleshooting exchange as a representative customer population. |
| **PhilPapers** | Philosophy, ethics, reasoning and education research relevant to a specialist product | Conditional specialist research pass via `ai-deep-research` or the relevant domain router | Use the canonical paper record and inspect the underlying paper. A bibliography or abstract is a discovery signal; it does not establish a product requirement, user segment or commercial opportunity. |
| **Project Gutenberg** | Public-domain or openly reusable text as a possible content input for reading, education or language products | Conditional content-product pass via `startup-market-intel`; use `ai-deep-research` for rights synthesis | Check the title-specific notice, jurisdiction and intended distribution. A text being readable online does not automatically grant the same rights for a derivative or commercial product. Content availability does not establish an audience or repeat value. |
| **Wikipedia** | Terminology, entity discovery and links to primary sources | Background-only pass; follow cited primary sources using `ai-deep-research` or the domain owner | Do not use an article as the final support for a material technical, legal, medical, market or historical claim. Record the underlying source and date, and use Wikipedia only to improve query coverage or orientation. |

## Practical routing recipes

### Technical uncertainty

1. Frame the exact task, input, output, baseline and acceptable correction or
   support labour.
2. Use arXiv/PMC/PhilPapers only when the research method is relevant to that
   task; use GitHub to inspect an implementation and its history.
3. Use YouTube only to observe a workflow or implementation claim, with a
   timestamp and source classification.
4. Return method IDs, dates, tested task, baseline, reproducibility, licence or
   access constraints, transfer limits and a bounded feasibility test.

### Problem and workflow discovery

1. Send HN, Stack Exchange, GitHub Issues, Ubuntu IRC and practitioner
   workflow observations from YouTube to `research-painpoint-scanner`. Use the
   relevant site/channel/video segment and a dated window.
2. Cluster independent observations, preserve adverse and unanswered examples,
   and separate a solved answer from an unmet problem.
3. Add PMC, Free Law Project or NIH ExPORTER only when the candidate's domain
   makes that source relevant. Do not add specialist sources to increase a
   source count.
4. Hand the resulting problem and workflow records to `startup-market-intel`
   for area comparison, then to `startup-idea-validation` for the next test.

### Product-input discovery

1. State what the product would ingest or redistribute: code, records, papers,
   video, text or a workflow interface.
2. Verify machine access, licence, attribution, jurisdiction, retention and
   redistribution limits at the source operator and record level.
3. Test a small representative input against the intended product path. Do not
   infer demand from the existence, size or openness of the corpus.
4. Carry rights and access as explicit delivery constraints into the comparison
   worksheet; an unverified right to use is an unknown, not a pass.

## What goes into the research-scout findings contract

The findings TSV and `aggregate_research_ideas.py` accept a deliberately small
method-source enum. Do not invent `source_type` values for PMC, YouTube, HN,
USPTO or the other specialist sources. Use this reference to route the work to
the owning skill. If a specialist source is cited as context for a research
method, keep it as a direct URL and explain its role in the report; it does not
create corroboration unless the existing aggregator contract supports that
source family.

No source count, ranking, funded project, patent, repository, video, article,
question or public-domain text can pass a commercial gate. The startup matrix
must still establish the candidate buyer/problem, alternatives, access,
delivery, economics and a bounded next test.

## Operator pages checked

These are discovery and compliance anchors, not a guarantee that every record
is reusable:

- [arXiv API documentation](https://info.arxiv.org/help/api/index.html)
- [GitHub REST API documentation](https://docs.github.com/en/rest)
- [Stack Exchange API documentation](https://api.stackexchange.com/docs)
- [Hacker News FAQ](https://news.ycombinator.com/newsfaq.html)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [About PMC](https://pmc.ncbi.nlm.nih.gov/about/intro/) and [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/)
- [NIH ExPORTER data dictionary](https://report.nih.gov/exporter-data-dictionary)
- [Free Law Project](https://free.law/)
- [USPTO Patent Public Search](https://www.uspto.gov/patents/search/patent-public-search)
- [Ubuntu IRC logs](https://irclogs.ubuntu.com/)
- [PhilPapers](https://philpapers.org/)
- [Project Gutenberg about page](https://www.gutenberg.org/about/) and [policies](https://www.gutenberg.org/policy/)
- [Wikipedia](https://www.wikipedia.org/) and [reliable-source guidance](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources)
