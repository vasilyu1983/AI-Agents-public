# Deep Research Patterns Catalog

**Purpose.** Named, numbered catalog of the durable April 2026 patterns for deep-research workflows. Every research design this skill produces should cite one or more pattern IDs from this catalog. Pair with `anti-patterns-catalog.md` for the sweep and `agentic-research-loop-architecture.md` for composed recipes.

## Table of Contents

- [Pattern Index](#pattern-index)
- [P1 — Source-ledger-as-contract](#p1--source-ledger-as-contract)
- [P2 — Plan-then-execute loop](#p2--plan-then-execute-loop)
- [P3 — Multi-agent research swarm](#p3--multi-agent-research-swarm)
- [P4 — Verifier subagent](#p4--verifier-subagent)
- [P5 — Freshness-window sourcing](#p5--freshness-window-sourcing)
- [P6 — Evidence-tier separation](#p6--evidence-tier-separation)
- [P7 — Citation back-pointer](#p7--citation-back-pointer)
- [P8 — Stop-criterion-as-eval](#p8--stop-criterion-as-eval)
- [P9 — Hostile-source detection](#p9--hostile-source-detection)
- [P10 — Synthesis-after-saturation](#p10--synthesis-after-saturation)
- [Composition Rules of Thumb](#composition-rules-of-thumb)

## Pattern Index

| ID | Name | Primary role |
|----|------|--------------|
| P1 | Source-ledger-as-contract | Provenance foundation for all research tasks |
| P2 | Plan-then-execute loop | Structured query planning before search execution |
| P3 | Multi-agent research swarm | Parallel query execution across many source types |
| P4 | Verifier subagent | Independent claim verification with isolated context |
| P5 | Freshness-window sourcing | Explicit temporal boundaries for volatile claims |
| P6 | Evidence-tier separation | Primary vs secondary vs model-notes isolation |
| P7 | Citation back-pointer | Sentence-level provenance in synthesis |
| P8 | Stop-criterion-as-eval | Termination condition defined before the loop starts |
| P9 | Hostile-source detection | Adversarial content and laundering detection |
| P10 | Synthesis-after-saturation | Synthesis deferred until the research loop saturates |

---

## P1 — Source-ledger-as-contract

- **Problem shape**: research tasks produce synthesis without a traceable record of what was consulted, when, and why.
- **Non-negotiables**: the ledger is written before any synthesis begins; every source entry has: `url`, `title`, `author`, `date_published`, `date_accessed`, `evidence_tier`, `supporting_quote`, `confidence`.
- **When to use**: every research task of any size.
- **Template**: `assets/templates/source-ledger.template.md`
- **Blocks**: A1, A10, A12

---

## P2 — Plan-then-execute loop

- **Problem shape**: searchers jump into queries without a structured plan, leading to coverage gaps, redundant queries, and unbounded cost.
- **Non-negotiables**: emit a `ResearchPlan` before the first tool call; plan includes query list, source targets, freshness class per topic, and stop criterion.
- **When to use**: any multi-query or multi-source research task.
- **Template**: `assets/templates/research-plan.template.md`
- **Blocks**: A2, A5

---

## P3 — Multi-agent research swarm

- **Problem shape**: large corpora or many parallel source types exceed what a single searcher can cover serially.
- **Non-negotiables**: each searcher agent writes to a shared ledger, not to a shared context; results are merged at the ledger level, not at the conversation level; conflicts are flagged, not resolved silently.
- **When to use**: vendor landscape surveys, academic literature sweeps, multi-jurisdiction regulatory research.
- **Architecture reference**: `references/agentic-research-loop-architecture.md`
- **Blocks**: A2, A8

---

## P4 — Verifier subagent

- **Problem shape**: the researcher who found sources also checks them — confirmation bias is structural.
- **Non-negotiables**: verifier receives only the ledger JSONL and the list of claims to check; it has no access to the search session, browser history, or planner context; it scores each claim as `supported / unsupported / inconclusive`.
- **When to use**: any claim that will reach a user, product, or published deliverable.
- **Script**: `scripts/citation_verifier.py`
- **Blocks**: A7

---

## P5 — Freshness-window sourcing

- **Problem shape**: research on fast-moving topics (AI capabilities, market data, regulatory changes) cites outdated sources without flagging the risk.
- **Non-negotiables**: define a `freshness_class` per topic in the plan — `stable` (> 2 years OK), `volatile` (< 90 days required), `unknown`; sources outside the window for volatile topics are flagged, not silently included.
- **When to use**: AI product research, pricing comparisons, regulatory guidance, vendor capability claims.
- **Blocks**: A9, A11

---

## P6 — Evidence-tier separation

- **Problem shape**: primary sources (official docs, filings, specs, release notes) and secondary commentary (blog posts, summaries, interpretations) are stored and cited interchangeably.
- **Non-negotiables**: evidence tiers are `primary`, `secondary`, and `model-working-notes`; synthesis sentences must cite the tier; model-working-notes are never cited as evidence.
- **When to use**: any research task that mixes official sources with commentary.
- **Blocks**: A3, A4, A6, A12

---

## P7 — Citation back-pointer

- **Problem shape**: synthesis paragraphs make factual claims with no traceable link to specific ledger entries.
- **Non-negotiables**: every sentence in the synthesis that asserts a fact carries a `[LEDGER-ID]` or inline citation that resolves to a specific ledger row.
- **When to use**: all synthesis artifacts that will be shared, published, or used in product decisions.
- **Blocks**: A8, A10

---

## P8 — Stop-criterion-as-eval

- **Problem shape**: research loops run indefinitely — more queries, more sources — with no signal that additional work improves quality.
- **Non-negotiables**: define the stop criterion in the plan before starting; acceptable forms: saturation condition (N consecutive iterations with no novel facts), hard cap (M total queries), or coverage threshold (K distinct primary sources per sub-question).
- **When to use**: all agentic research loops.
- **Blocks**: A5

---

## P9 — Hostile-source detection

- **Problem shape**: public-web research surfaces adversarial SEO content, AI-generated content farms, and citation-laundering chains that appear authoritative.
- **Non-negotiables**: before adding a URL to the ledger, check: domain age and reputation, authorship attribution, whether the source cites a traceable primary, AI-content signals (no byline, generic structure, keyword stuffing); flag and quarantine suspicious sources rather than silently including them.
- **When to use**: vendor comparisons, competitive intelligence, public-web-heavy research tasks.
- **Blocks**: A6, A11

---

## P10 — Synthesis-after-saturation

- **Problem shape**: synthesis begins after one or two passes and then drives subsequent searching — the research is framed by early conclusions.
- **Non-negotiables**: no synthesis artifact is emitted until the research loop has reached its stop criterion (P8); interim working notes are stamped `draft / not for citation`; the synthesis phase reads the finalized ledger, not the search session.
- **When to use**: all multi-pass research tasks.
- **Blocks**: A1, A2

---

## Composition Rules of Thumb

- Every research task should use P1 (ledger) + P7 (back-pointers) at minimum.
- Any task with more than three queries should add P2 (plan) and P8 (stop criterion).
- Any task that produces a user-facing or published claim should add P4 (verifier).
- Fast-moving domains always add P5 (freshness window).
- Public-web research always adds P9 (hostile-source detection).
