# AI in UX Research

When and how to use AI in research workflows — what it accelerates, what it breaks, and what regulatory exposure it creates.

**Last updated**: July 2026.

---

## Table of Contents

- [Decision Tree: When AI Helps](#decision-tree-when-ai-helps)
- [Synthetic Users](#synthetic-users)
- [AI-Assisted Analysis](#ai-assisted-analysis)
- [AI Moderators](#ai-moderators)
- [Researching AI Features in a Product](#researching-ai-features-in-a-product)
- [Regulatory Exposure (EU AI Act + GDPR)](#regulatory-exposure-eu-ai-act--gdpr)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

---

## Decision Tree: When AI Helps

| Task | Default | Why |
|------|---------|-----|
| Generate hypotheses before fieldwork | AI on | Cheap; no participants exposed; humans validate |
| Pilot recruiting screener questions | AI on | Saves cycles; reviewer catches leading items |
| Cluster and tag transcripts after coding | AI assist | Speeds synthesis; require human sample audit |
| Draft summary insight from coded data | AI assist | Speeds writing; researcher signs off on claims |
| Replace participants with simulated personas | AI off | Hallucinated demand signals; NN/g position |
| Conduct unstructured generative interviews | AI off | Cannot adapt probing to emotional pivots |
| Conduct structured task-success usability runs | AI optional | Acceptable for scale; not for first-time tasks |

The rule: AI accelerates the *researcher's* work. It does not replace the *participant's* signal.

---

## Synthetic Users

A 2024–2026 vendor category (Synthetic Users, Useberry SyntheticUsers, others) sells AI-generated participants as substitutes for human research.

NN/g's published position: AI-generated users are not a substitute for real users. The output reflects the LLM's training data and the prompter's framing, not actual demand. Multiple replicated tests show synthetic users systematically over-confirm whatever hypothesis is presented and miss the friction patterns that real participants surface.

**Acceptable uses**:
- pre-fieldwork hypothesis generation ("what objections might a CFO raise?")
- screener and discussion-guide pilot ("does this question read as leading?")
- pilot survey response generation to test instrument structure (not signal)

**Unacceptable uses**:
- generating "findings" without recruiting humans
- counting synthetic responses toward sample size
- presenting synthetic output as evidence in a decision brief

If the budget genuinely doesn't allow human recruitment, the correct answer is "we have no evidence yet," not "we have synthetic evidence."

---

## AI-Assisted Analysis

The widely adopted tools for AI-assisted synthesis (verify current):

| Tool | Capability | When to choose |
|------|------------|----------------|
| **Dovetail** (Magic Summarize, Magic Cluster, Ask AI) | repository-wide AI synthesis and Q&A over coded data | already on Dovetail; need cross-study queries |
| **Marvin** | AI note-taking, theme detection during interviews | live note generation while moderating |
| **Looppanel** | AI tagging, theme clustering, claims-of-evidence summaries | high-volume usability or interview throughput |
| **UserTesting Insights AI** | summarisation across UserTesting panel sessions | already on UserTesting platform |
| **Notably** | AI-assisted thematic analysis with audit trail | small teams without Dovetail |

**Workflow guardrails**:

1. **Researcher codes the first sample manually**, then lets AI extend codes across the rest. Never start from AI codes.
2. **Audit at least 10–15% of AI-tagged segments** by hand. Reject the run if disagreement exceeds ~15%.
3. **Keep evidence links to source recordings/quotes** — AI synthesis without traceable evidence is just generated prose.
4. **Refuse "generate the report" prompts**. AI can draft sections; the researcher writes the claims.

---

## AI Moderators

AI moderators (Outset, Strella, Great Question AI moderation, Maze AI moderation) conduct text or voice interviews at scale.

**Strengths**: structured task interviews, large-N onboarding research, post-launch comprehension checks where the script is well-defined.

**Failure modes**:
- cannot adapt probing to unexpected emotional content
- amplify methodological errors in the prompt (a leading prompt produces leading follow-ups, at scale)
- miss context cues (sarcasm, hesitation, body language)
- produce transcripts that *look* like research but encode the moderator's prior beliefs

**Decision rule**: AI moderators are appropriate when the protocol is so structured that a junior moderator could follow it. They are inappropriate for generative or first-time discovery work.

---

## Researching AI Features in a Product

When the *product under test* is AI-driven (chat, agents, generative UI, copilots), study design must address dimensions that traditional usability tests do not cover.

| Dimension | What to measure | Method |
|-----------|-----------------|--------|
| Trust calibration | does perceived reliability match actual reliability? | think-aloud + post-task confidence rating |
| Explainability | can users predict what the agent will do next? | predict-then-act tasks |
| Failure recovery | can users tell when the AI is wrong, and recover? | seed deliberate failures; observe detection time |
| Tool-use disclosure | do users know what data was accessed or modified? | post-task probe on actions taken |
| Approval gating | are gates placed where users actually want oversight? | preference test with destructive vs non-destructive actions |
| Hallucination cost | what is the cost of acting on wrong output? | scenario-based ranking by stakes |
| Steerability | can users redirect a multi-step run? | mid-task interruption + recovery study |

For agentic products, study sessions across more than one turn — single-turn chat usability misses most of the failure surface.

References: [NN/g — Generative AI UX Research Agenda](https://www.nngroup.com/articles/genai-ux-research-agenda/), [CHI 2026 HCI + AI preprints](https://dbuschek.medium.com/chi26-preprint-collection-bdbfe9492a7b).

---

## Regulatory Exposure (EU AI Act + GDPR)

Two stacks apply to AI use in research with EU/UK participants.

### EU AI Act

The EU AI Act entered into force August 2024 with a tiered timeline: prohibited-practice rules have applied since **2 February 2025**; general-purpose AI (GPAI) provider obligations since **2 August 2025**; and high-risk system (Annex III) obligations were originally set for **2 August 2026** but postponed to **2 December 2027** (embedded high-risk systems under Annex I to 2 August 2028) under the Digital Omnibus on AI. As of this writing the Omnibus has cleared both co-legislators — European Parliament final vote 16 June 2026, Council final sign-off 29 June 2026 — and enters into force shortly after Official Journal publication. Treat the postponed dates as reliable but verify the exact in-force date and any last-minute textual changes before citing it in a compliance-critical context.

For research operations the relevant questions are:

- **Are we using a high-risk AI system?** Research transcription and synthesis tools used to make decisions about *people in regulated contexts* (employment, education, public services) can fall into Annex III high-risk categories. Most product research does not, but enterprise research about workforce or hiring tools can.
- **Are we deploying a general-purpose AI?** If a tool processes participant recordings via a foundation model (Dovetail Ask, Marvin, AI moderators), the *deployer* (your team) carries transparency and disclosure obligations regardless of risk classification.
- **Have we performed a Fundamental Rights Impact Assessment (FRIA)?** Required for high-risk AI deployers in public-interest sectors before first use.

Practical compliance actions:
1. Inventory every AI tool that processes participant data.
2. Update participant consent forms to disclose AI processing, retention, and any cross-border processing.
3. Update Data Processing Agreements (DPAs) with each AI vendor — confirm sub-processors and EU representatives.
4. Document the legal basis for AI processing (usually legitimate interest with opt-out, sometimes explicit consent).

### GDPR

GDPR continues to apply. Specific to AI in research:

- Recordings and transcripts are personal data. Sending them to a non-EU AI provider triggers Chapter V transfer rules (SCCs, adequacy decisions).
- "Right to explanation" obligations apply if AI synthesis directly affects a decision about an identifiable participant (rare in research, common in research-ops automation).
- Retention: AI-processed transcripts inherit the source recording's retention policy unless the AI output is genuinely de-identified.

Sources: [IAPP — GDPR + EU AI Act interplay](https://iapp.org/resources/article/mapping-interplays-gdpr-eu-ai-act), [European Commission — AI Act timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai).

---

## Anti-Patterns

- Counting synthetic-user output as evidence in a decision brief (NN/g position; over-confirms hypotheses).
- Letting an AI moderator run discovery interviews where the protocol is open-ended.
- Starting analysis from AI-generated codes instead of human-coded seed sample.
- Generating "the report" with AI and signing off without auditing claims back to source quotes.
- Sending EU/UK participant recordings to a US AI vendor without an updated DPA and consent disclosure.
- Treating "AI processed it" as anonymisation.
- Stack-ranking AI moderator transcripts as if they were equivalent to human-moderated transcripts (they are not — different signal quality).
- Skipping a FRIA when deploying a high-risk research AI tool in a regulated sector.

---

## Sources

- [NN/g — Synthetic Users video](https://www.nngroup.com/videos/ai-generated-users/)
- [NN/g — GenAI UX Research Agenda](https://www.nngroup.com/articles/genai-ux-research-agenda/)
- [Looppanel — AI for UX Research Methods](https://www.looppanel.com/blog/ai-for-ux-research-methods)
- [Dovetail — AI features](https://dovetail.com/product/ai/)
- [Great Question — AI moderation guide](https://greatquestion.co/ux-research/ai-moderation)
- [Maze — AI moderation collection](https://maze.co/collections/ai/ai-moderation/)
- [Carl J Pearson — AI moderated interviews methodological error](https://carljpearson.com/ai-moderated-interviews-methodological-error-amplified/)
- [IAPP — GDPR + EU AI Act interplay](https://iapp.org/resources/article/mapping-interplays-gdpr-eu-ai-act)
- [European Commission — AI Act regulatory framework](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [CHI 2026 HCI + AI preprints](https://dbuschek.medium.com/chi26-preprint-collection-bdbfe9492a7b)
