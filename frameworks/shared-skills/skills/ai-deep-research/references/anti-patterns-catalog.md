# Deep Research Anti-Patterns Catalog

**Purpose.** Numbered catalog of the durable anti-patterns for deep-research workflows, each with detection signals and a blocking pattern from `patterns-catalog.md`. Run this sweep against any research design or existing workflow before shipping.

## Table of Contents

- [Anti-Pattern Index](#anti-pattern-index)
- [A1 — Pre-synthesizing the answer](#a1--pre-synthesizing-the-answer)
- [A2 — Single-pass search](#a2--single-pass-search)
- [A3 — Mixing evidence tiers](#a3--mixing-evidence-tiers)
- [A4 — Model-output-as-source](#a4--model-output-as-source)
- [A5 — Unbounded research loop](#a5--unbounded-research-loop)
- [A6 — Citation laundering](#a6--citation-laundering)
- [A7 — Verifier-with-same-context-as-researcher](#a7--verifier-with-same-context-as-researcher)
- [A8 — Vague consensus language](#a8--vague-consensus-language)
- [A9 — Date-free volatile claims](#a9--date-free-volatile-claims)
- [A10 — Retrofitting citations](#a10--retrofitting-citations)
- [A11 — Overweighting recency](#a11--overweighting-recency)
- [A12 — Storing evidence with synthesis](#a12--storing-evidence-with-synthesis)

## Anti-Pattern Index

| ID | Name | Detection signal | Blocked by |
|----|------|-----------------|------------|
| A1 | Pre-synthesizing the answer | Synthesis text exists before the ledger | P10, P1 |
| A2 | Single-pass search | One query batch, no iterative refinement | P2, P10 |
| A3 | Mixing evidence tiers | `evidence_tier` field absent or always "source" | P6 |
| A4 | Model-output-as-source | LLM summary URL or "AI-generated" in ledger as primary | P6 |
| A5 | Unbounded research loop | No stop criterion in the research plan | P8 |
| A6 | Citation laundering | Chain: blog → blog → primary; no direct primary citation | P9, P6 |
| A7 | Verifier-with-same-context | Verifier agent shares session with researcher | P4 |
| A8 | Vague consensus language | "Multiple sources say" without ledger IDs | P7 |
| A9 | Date-free volatile claims | AI capability or market claims with no date stamp | P5 |
| A10 | Retrofitting citations | Citations added after synthesis is complete | P1, P7 |
| A11 | Overweighting recency | Most recent blog post outweights older primary doc | P5, P6 |
| A12 | Storing evidence with synthesis | Raw evidence and final memo in the same retrieval bucket | P6, P1 |

---

## A1 — Pre-synthesizing the answer

**Description**: the researcher (human or agent) forms a conclusion before a source ledger exists. All subsequent evidence gathering is influenced by the prior conclusion.

**Detection signals**:
- Synthesis paragraph appears in agent scratchpad before ledger entry count > 0.
- Research plan contains a "hypothesis to confirm" rather than open questions.
- Ledger entries are added after the synthesis is drafted.

**Resolution**: freeze the research question as open; emit no synthesis until the ledger passes its minimum source count and verifier check. Use P10 (synthesis-after-saturation).

---

## A2 — Single-pass search

**Description**: the research loop runs one query batch and produces a synthesis without iterative query refinement, contradiction checks, or diversification of source types.

**Detection signals**:
- Total distinct queries = 1–3 for a multi-faceted question.
- No evidence of query refinement based on initial results.
- No minority or dissenting sources present in the ledger.

**Resolution**: require iterative refinement; add a P2 (plan-then-execute) loop with a minimum of N distinct query branches and a contradiction-check step.

---

## A3 — Mixing evidence tiers

**Description**: primary source documents (official specs, filings, release notes, primary research) are stored and cited in the same bucket as secondary commentary (blogs, summaries, opinion pieces) with no tier distinction.

**Detection signals**:
- Ledger has no `evidence_tier` field.
- Blog posts and official documentation share the same citation weight in the synthesis.
- A secondary source is cited to support a technical capability claim where a primary source exists.

**Resolution**: apply P6 (evidence-tier separation); enforce `evidence_tier: primary | secondary | model-working-notes` on every ledger entry.

---

## A4 — Model-output-as-source

**Description**: an LLM-generated summary, paraphrase, or AI assistant output is included in the ledger as a primary or secondary source.

**Detection signals**:
- Source URL points to an AI chat interface or AI-writing tool.
- Source has no author, date, or institutional affiliation.
- "According to ChatGPT / Claude / Gemini" appears in a source note.

**Resolution**: stamp all model outputs `tier: model-working-notes`; the verifier (P4) rejects model-working-notes as primary evidence.

---

## A5 — Unbounded research loop

**Description**: the research loop has no explicit termination condition; it continues until cost or time forces a stop, with no quality signal that additional iterations improve the output.

**Detection signals**:
- Research plan has no `stop_criterion` field.
- Agent continues querying after the ledger has stopped growing.
- Budget is the only termination signal.

**Resolution**: define the stop criterion in the plan before starting (P8): saturation condition, hard cap on queries, or minimum distinct-primary-source count.

---

## A6 — Citation laundering

**Description**: a source is cited that in turn cites the actual primary, without the researcher ever accessing or verifying the primary document. Provenance chains break silently.

**Detection signals**:
- Citation chain is blog → blog → primary (two or more hops).
- The primary document URL is not present in the ledger.
- Source notes contain "as cited in" or "according to [secondary source]".

**Resolution**: require direct citation of primary sources (P6); apply P9 hostile-source detection; reject chains longer than one hop without primary verification.

---

## A7 — Verifier-with-same-context-as-researcher

**Description**: the verifier agent that checks claims read the same sources, search results, or conversation context as the researcher, adding no independence.

**Detection signals**:
- Verifier and researcher share the same agent session.
- Verifier has access to the researcher's browser history or tool-call log.
- Verifier approval rate is consistently ≥ 95% (suspiciously high agreement).

**Resolution**: apply P4 (verifier subagent isolation); verifier receives only the ledger JSONL and claim list, never the search session.

---

## A8 — Vague consensus language

**Description**: synthesis uses phrases like "multiple sources agree," "experts say," or "it is widely understood" without citing the specific ledger entries that support the claim.

**Detection signals**:
- Synthesis sentences contain "multiple sources" or "many experts" with no bracket citation.
- Ledger entries exist but are not referenced in the synthesis.
- Citation density is low relative to claim density.

**Resolution**: apply P7 (citation back-pointer); every factual claim in synthesis carries a `[LEDGER-ID]`.

---

## A9 — Date-free volatile claims

**Description**: claims about fast-moving domains (AI capabilities, pricing, market share, regulatory status) carry no date anchor and no freshness class, so they decay silently.

**Detection signals**:
- Synthesis contains AI capability or pricing claims with no date.
- Ledger entries for volatile topics have no `date_published` or `date_accessed`.
- Research plan has no `freshness_class` per topic.

**Resolution**: apply P5 (freshness-window sourcing); define freshness class per topic; stamp all volatile claims with date.

---

## A10 — Retrofitting citations

**Description**: the synthesis memo is written in full and citations are added afterward by finding sources that "support" each claim. This consistently inflates confidence in unsupported claims.

**Detection signals**:
- Ledger was last modified after the synthesis document.
- Citation discovery is a post-writing step in the workflow.
- Several synthesis claims have no corresponding ledger entry.

**Resolution**: build the ledger first (P1); write synthesis only from ledger entries already present; any claim with no ledger entry is marked `[UNVERIFIED]`.

---

## A11 — Overweighting recency

**Description**: the most recently published source (often a blog post summarizing older primary work) receives more weight than an older authoritative primary source.

**Detection signals**:
- Synthesis cites a 2025 blog post instead of the 2023 primary paper it summarizes.
- Ledger sort order is by `date_accessed` descending with no tier weighting.
- Evidence-tier separation (P6) is absent.

**Resolution**: weight by `evidence_tier` first, then `date_published`; apply P6 to prevent secondary sources from outranking primary sources.

---

## A12 — Storing evidence with synthesis

**Description**: raw evidence captures and final synthesis are stored in the same retrieval bucket. Follow-on RAG queries or future research passes cite derived text as if it were original evidence.

**Detection signals**:
- Research output folder contains a single file mixing ledger entries and synthesis prose.
- Vector store or note vault ingests the full research output without tier separation.
- Future search passes retrieve model-generated summaries as top hits.

**Resolution**: maintain separate artifacts — `source-ledger.jsonl`, `working-notes.md`, `synthesis-final.md` — and ingest only the ledger into retrieval systems (P1, P6).
