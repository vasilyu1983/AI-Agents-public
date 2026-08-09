# Conference Proceedings Strategy

## Table of Contents

- [Why Conferences Matter](#why-conferences-matter)
- [Venue Map](#venue-map)
- [Discovery Path](#discovery-path)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)

## Why Conferences Matter

Conference proceedings are **peer-reviewed** — they're the strongest evidence baseline available. They lag arXiv by 6-12 months, but acceptance is a credibility signal that arXiv lacks. For methods worth investing real time in, conference-corroborated > arXiv-only.

Treat conferences as a **filter pass**: if a method that surfaced on arXiv 6+ months ago hasn't shown up at a top venue, that's information.

## Venue Map

| Field | Top venues | Proceedings URL pattern |
|-------|-----------|------------------------|
| ML (general) | NeurIPS, ICML, ICLR | https://proceedings.neurips.cc/, https://proceedings.mlr.press/, https://openreview.net/group?id=ICLR.cc |
| NLP / LLMs | ACL, EMNLP, NAACL, EACL, COLING | https://aclanthology.org/ |
| AI (general) | AAAI, IJCAI | https://aaai.org/, https://www.ijcai.org/ |
| Computer Vision | CVPR, ICCV, ECCV | https://openaccess.thecvf.com/ |
| Information Retrieval | SIGIR, WSDM, CIKM | https://dl.acm.org/ |
| Data Mining | KDD | https://dl.acm.org/conference/kdd |
| Software Engineering | ICSE, FSE, ASE, OOPSLA, PLDI | https://dl.acm.org/ |
| Systems | OSDI, SOSP, NSDI | https://www.usenix.org/conferences |
| Security | USENIX Security, S&P (Oakland), CCS | https://www.usenix.org/, https://www.ieee-security.org/ |
| Databases | VLDB, SIGMOD, ICDE | https://dl.acm.org/, https://vldb.org/ |
| HCI | CHI, UIST | https://dl.acm.org/conference/chi |

## Discovery Path

1. **Identify the relevant venue** for your topic from the map above.
2. **Walk the most recent year's accepted-paper list** — usually a single page with all papers.
3. **Filter by title keyword** for the topic.
4. **For top hits**, follow to the paper PDF and code link.
5. **Cross-check on arXiv / Semantic Scholar** for the same paper — conference and arXiv versions can differ; the conference version is canonical.

For OpenReview venues (ICLR, AISTATS, some workshops), reviewer comments and author responses are public — read them to find acknowledged limitations the abstract glosses over.

## Per-Venue Discovery Cues

- **NeurIPS / ICML**: best for general ML methods. Look for the year's accepted-paper page; PMLR organizes ICML by volume number.
- **ICLR (OpenReview)**: read the reviews. The "Soundness" and "Presentation" scores plus reviewer-author exchanges expose method weaknesses.
- **ACL Anthology**: queryable URL structure (`https://aclanthology.org/{{year}}.{{venue}}-{{paper-id}}/`); fast to filter.
- **CVF Open Access**: free PDFs for CVPR, ICCV, ECCV; no paywall.
- **USENIX**: free PDFs and full proceedings; high-quality systems work.
- **ACM Digital Library**: many SE / DB / KDD venues. Some PDFs paywalled, but abstracts are free.

## Credibility Signals

- **Acceptance at a top-tier venue** is the floor — at this point evidence_grade defaults to B+ minimum.
- **Best Paper / Outstanding Paper Award** — extra signal but also a hype magnet (apply trap 8).
- **Reviewer comments visible** (OpenReview) — read them.
- **Multiple author institutions** — corporate-academic collaborations are less single-source-biased.
- **Ablations table present** — published reviewers usually demand them; absence at top venue is unusual.

## Venue Quality Triage

Weight acceptance tiers in this order: **Oral > Spotlight > Poster > Workshop**. Workshop papers have weaker review and should be treated as effectively preprints — they can surface interesting directions, but evidence grade caps at C by default. For non-ML venues, use CORE ranking (A* > A > B > C) or journal tier (Q1/Q2 in Scimago) as a secondary credibility signal when conference tier is ambiguous.

## Mining OpenReview Review Text

For ICLR, NeurIPS (2023+), AISTATS, and any other OpenReview-hosted venue, reviewer comments are a free evidence signal:

- **Strong-accept consensus** (average score ≥ 8, low variance) upgrades evidence grade by one step relative to what the abstract alone would justify.
- **Borderline accept** (score 5-6 with high variance) is a yellow flag — read the author rebuttal and check whether the main concern was addressed or merely deflected.
- **Reviewer critiques as trap-tag detection:** reviewers routinely flag benchmark gaming (Trap 12), irreproducibility (Trap 1), narrow applicability (Trap 9), and compute-scale confounds (Trap 3) in plain language before these patterns are named in the literature. Scan all `"Weaknesses"` fields for these patterns before assigning an evidence grade.

Query pattern (OpenReview API v2):

```text
GET https://api.openreview.net/notes?forum={{paper_id}}&details=replies
```

Filter replies where `invitation` contains `Review` to isolate reviewer notes.

## Biases

- **Lag.** Conference papers are 6-12 months behind the bleeding edge. For fast-moving fields (LLM agents in 2024-2026), bleeding-edge methods aren't yet at venues.
- **Venue politics.** Some venues over-favor incremental work that fits existing benchmarks; others over-favor novelty without applicability. Read the call-for-papers framing.
- **Workshop ≠ main track.** Workshop papers have weaker review; treat closer to arXiv preprints than to main-track papers.
- **Reproducibility checklists** are now required at most ML venues, but compliance varies.
- **Submission rate** at top venues is enormous (~10k+ submissions at NeurIPS); reviewer noise is non-trivial. A single reject doesn't condemn a method; a single accept doesn't prove one.
