# Handoffs and Scope Boundaries

## Contents

- [When NOT to Use This Skill](#when-not-to-use-this-skill)
- [Layered Opportunity Handoff](#layered-opportunity-handoff)
- [Startup Scouting Handoff](#startup-scouting-handoff)
- [Scout to Validate Chain](#scout-to-validate-chain)
- [Related Skills](#related-skills)
- [Case Study: How Reflection Stole Reasoning](#case-study-how-reflection-stole-reasoning)

## When NOT to Use This Skill

| Situation | Use instead |
|-----------|------------|
| Find an app area using YC, incubators, accelerator cohorts or VC investment theses | `startup-market-intel` via `router-startup`; use its [opportunity radar](../../startup-market-intel/references/opportunity-radar.md) |
| Discover paid-product areas, revenue precedents or reported stacks through TrustMRR | `startup-market-intel`; use its [paid-product precedent layer](../../startup-market-intel/references/paid-product-revenue-precedents.md) |
| Compare startup candidates, choose a bounded experiment or assess commercial commitment | `startup-idea-validation`; use its shared method and comparison worksheet |
| arXiv-only deep triage with attribution | `research-arxiv-scout` |
| Community pain points, not research methods | `research-painpoint-scanner` |
| Mining public GitHub repos for skills, practices, or code patterns | `research-git` |
| Validated Q&A answers or known-error solutions (the Stack Overflow corpus / Stack Overflow for Agents exchange) | `qa-debugging` — that is solved-answer lookup, not research-method mining |
| Production deep-research synthesis (verified citations plus reasoning trace) | `ai-deep-research` |
| Single-paper summary for a known arXiv ID | `research-arxiv-scout` step 3 |
| End-user career positioning, company interview reviews, recruiter pitches, or CV tailoring | `career-jobhunt`; this skill may still mine research methods to improve that skill |

## Layered Opportunity Handoff

Use the [opportunity evidence layers](../../startup-market-intel/references/opportunity-evidence-layers.md) when this scan supports area discovery. Support L7 feasible delivery and, when a dated technical change matters, L4 timing. Preserve original study/event IDs across papers, repos and commentary; report representative task, baseline, correction labour and limits. Technical scores rank methods only. Area selection belongs to `startup-market-intel`; a concrete offer or experiment decision belongs to `startup-idea-validation`.

Carry source and underlying event IDs, dates, scope, supportive/mixed/adverse/unknown direction, evidence basis, counterevidence and the decisive unknown into the [comparison worksheet](../../startup-idea-validation/references/opportunity-comparison.md). The same event appearing in several layers remains one event. No scout score, source count or convergence label passes a commercial gate; retain missing and adverse evidence in the handoff.

## Startup Scouting Handoff

For TrustMRR discovery by product area, revenue or reported technology, use the [paid-product precedent layer](../../startup-market-intel/references/paid-product-revenue-precedents.md). It turns comparable businesses into app, stack and channel hypotheses plus revenue scenarios. Carry comparable records with `evidence_scope: comparable_product`; their revenue does not establish demand for a new offer. Concrete candidate comparisons belong to `startup-idea-validation`.

If the user invokes this scout to ask **where to build an app**, route the primary task to `startup-market-intel`. Its [radar procedure](../../startup-market-intel/references/opportunity-radar.md#incubator-and-investor-search) owns incubator requests, cohorts, investor theses, buyer problems, alternatives and area selection. Do not turn the academic source list into a market-validation workflow.

Use this skill as a supporting research pass only when a candidate has a specific technical uncertainty: for example, whether a new extraction method can handle the buyer's messy documents. Return source IDs and dates, measured task and baseline, reproducibility, applicability limits and what to test. Papers and prototypes can support feasibility hypotheses; they do not establish buyer access or payment.

The sequence is **area discovery, candidate comparison, bounded test, evidence update**. Apply [startup-idea-validation's method](../../startup-idea-validation/references/opportunity-decision-method.md) when choosing the experiment or making a commitment, with its [comparison worksheet](../../startup-idea-validation/references/opportunity-comparison.md). Unknown demand does not prevent a bounded feasibility test. Use the commercial gates before treating an approach as BUILD-ELIGIBLE; do not require completed commercial gates merely to scan incubators.

## Scout to Validate Chain

One node in the startup signal chain. Preserve the partition — hand off, do not absorb a sibling's sources.

| Stage | Skill | Owns |
|-------|-------|------|
| Scan - community pain | `research-painpoint-scanner` | Reddit / HN / GitHub Issues / forums / complaint DBs |
| Scan - reviews | `research-review-mining` | App stores / G2 / Trustpilot / community reviews |
| Scan - research methods | `research-scout` (this skill) | Papers / research blogs / curator newsletters |
| Validate | `startup-idea-validation` | Go / pivot / kill on scanned evidence |

**Hand off when:** you need product/market pain rather than research methods, go to `research-painpoint-scanner` (community) or `research-review-mining` (reviews); when a mined method needs a build / no-build decision, go to `startup-idea-validation`. This skill does not absorb product-signal sources.

## Related Skills

| Skill | Relationship |
|-------|-------------|
| [`../../research-arxiv-scout/SKILL.md`](../../research-arxiv-scout/SKILL.md) | Specialist downstream — arXiv-only triage with full attribution |
| `ai-deep-research` | Use when ideas need verified-citation synthesis, not just a shortlist |
| `dev-context-engineering` | Use when applying ideas to context layer or agent design |
| `ai-prompt-engineering` | Use when applying ideas to prompts or LLM workflows |
| `ai-coding-agents-observability-evals` | Use when the stolen idea is an eval method or agent metric |
| `huggingface-skills:` plugin (external) | Use for HF-Hub-specific paper publishing/citation flows |
| `agents-skills` | Use when packaging stolen ideas as a new skill |
| `agents-skills-feedback-loop` | Runtime dependency — the Learnings Loop calls its `append_learning.py` / `consolidate.py` scripts |
| `research-git` | Reproducibility-signal replacement for dead Papers with Code (GitHub repo/reimplementation inspection) |
| `career-jobhunt` | Owns AI-company jobhunt workflows; use this skill to mine research methods that improve matching, tailoring, ATS gates, or interview prep |

## Case Study: How Reflection Stole Reasoning

The Reflexion / self-refine / reflection family (2023-2024) is a textbook case of an idea that was steal-worthy and easy to detect with this scout:

| Scout Dimension | Reflexion Evidence |
|-----------------|--------------------|
| **Source mix** | arXiv preprint, then HF Papers daily, then curator coverage (Lilian Weng), then GitHub reimplementations (today via `research-git`; Papers with Code at the time, now dead), then conference acceptance |
| **Evidence grade** | B rising to A as benchmarks accumulated |
| **Reproducibility** | `code+benchmarks` from week one |
| **Lift** | Low — 1-3 days to add a critique-and-retry pass |
| **Method shape** | `prompting-pattern` plus `inference-time-method` |
| **Trap tags** | None initially; later `benchmark-gaming` flagged on some derivatives |
| **Cross-source corroboration** | 4 or more source families within 90d |

**Pattern to look for:** when an idea (a) ships with code in week one, (b) gets covered by two or more curator newsletters in 30 days, and (c) generates a wave of derivative papers in 90 days, it is a high-confidence steal — even before formal peer review.
