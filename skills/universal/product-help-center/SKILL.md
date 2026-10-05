---
name: product-help-center
description: "Designs AI-first help centers and self-service support. Use when shaping taxonomy, article templates, or content and answer contract for support AI, not the bot build."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Help Center Design

Design public help centers, in-app self-service, and AI-consumable documentation systems.

Use this skill when the user needs one of these outcomes:
- pick or compare a help center, docs, or support-AI platform
- design or audit taxonomy, navigation, article standards, and governance
- define the approved sources, answer contract, and escalation-policy content that support AI grounds on
- measure self-service outcomes, including whether deflection is incremental
- make docs easier for humans, search, and AI agents to consume

Route elsewhere:
- bot runtime, flows, state, intent automation, and tool permissions → [ai-bot-builder](../ai-bot-builder/SKILL.md)
- voice and IVR → [ai-voice-bots](../ai-voice-bots/SKILL.md)
- getting pages cited by AI answer engines → `marketing-aeo-geo`
- accessibility fixes in product code → [software-accessibility](../software-accessibility/SKILL.md)
- i18n in product code → [software-localisation](../software-localisation/SKILL.md); country-level marketing localization → `marketing-geo-localization`

## Workflow

1. Classify the surface
   - Support help center, developer docs portal, internal knowledge base, in-app guidance, or hybrid.
2. Define audience and risk
   - End users, admins, developers, agents, regulated customers, multilingual audiences.
3. Choose the operating model
   - Human-authored docs only, retrieval-first support AI, or agentic support with approved tools.
4. Design information architecture
   - Category structure, navigation, search strategy, metadata, URL rules, and versioning.
   - Tree-test the category tree on the top tasks before launch or migration; fix failing paths before writing redirects.
5. Standardize content
   - Article types, writing rules, visual rules, and reusable templates.
6. Instrument quality
   - Search analytics, self-service outcomes, citation quality, handoff quality, and freshness signals.
7. Run knowledge operations
   - Owners, review cadences, release-driven updates, and stale-content remediation.

Expected outputs:
- help center or docs platform recommendation with rationale
- taxonomy map, metadata schema, and article backlog
- support AI design with sources, escalation policy, and guardrails
- operating model for ownership, QA, and measurement

## Quick Reference

### Surface Selection

| Need | Primary Surface | Good Fits |
|------|-----------------|-----------|
| Customer troubleshooting, billing, account help | Support help center | Zendesk, Intercom, Freshdesk |
| API guides, SDK docs, AI-consumable docs | Developer docs portal | ReadMe, Mintlify, GitBook |
| In-app onboarding and contextual help | In-app guidance layer | Intercom, Pendo, Appcues, custom |
| Internal-only runbooks and agent knowledge | Internal knowledge base | Guru, Confluence, Notion |
| High-volume support automation | Retrieval-first support AI | Zendesk AI, Intercom Fin, custom |

### Content Type Decision Matrix

| User Need | Content Type | Format | AI Role |
|-----------|--------------|--------|---------|
| "How do I..." | How-to | Step-by-step | Link, summarize, adapt steps |
| "Why is this failing?" | Troubleshooting | Symptoms -> causes -> fixes | Diagnose and route |
| "What does this mean?" | Conceptual | Plain-language explanation | Summarize context |
| "Where do I find..." | Navigation | Short answer + links | Point to exact surface |
| "What are the limits or rules?" | Reference | Tables, lists, exact wording | Retrieve verbatim facts |
| "Can you do this for me?" | Task policy | Action rules + approvals | Decide whether AI may act |

### Platform Selection Rules

- Recommend support suites when ticketing, SLAs, handoff, and compliance are first-class requirements.
- Recommend docs portals when the main problem is structured product or API documentation.
- Treat Notion as acceptable for lightweight internal knowledge and early-stage public docs, not as a durable default for serious public help centers.
- Verify pricing, packaging, plan limits, and current AI features before making final vendor recommendations.
- Before recommending a support-AI agent, read the vendor's own plan and product pages for its AI-agent tiers, supported channels, and pricing model (per seat, per resolution, or bundled). These change faster than this skill.

See [platform-guides.md](references/platform-guides.md) for current platform-fit rules and [sources.json](data/sources.json) for preferred sources.

## Answer Contract Before Retrieval Design

Define the answer contract for each high-risk intent before choosing chunks, embeddings, or a support model:

- canonical source and source owner;
- applicable product version, plan, role, locale, and effective date;
- the exact exception or precedence rule when two sources disagree;
- whether the answer may be summarized, must be quoted exactly, or must escalate;
- the observable completion state and evidence captured after any tool action.

If two approved sources conflict, freshness alone does not choose the winner. Apply the recorded authority, scope, effective period, and precedence rule. When those fields identify a governing source, answer or act from it, disclose the conflict, queue the stale lower-authority source for correction, and preserve the action evidence. Pause only the affected transaction when precedence does not resolve the conflict, the governing source is outside scope or period, or residual uncertainty is material to an irreversible action. A retrieval system that returns a plausible passage without this contract is not ready for support automation.

### AI-Consumable Docs Principles

- Publish stable canonical URLs and clear page titles.
- Keep one main task or concept per page.
- Use headings, tables, lists, and exact error strings.
- Expose machine-friendly surfaces (markdown export, API references, MCP servers, agent-facing indexes) when a named consumer uses them.
- Publish `llms.txt` or `llms-full.txt` only for a named consumer that documents or demonstrates use of it. Treat the files as an experimental index, not proof of crawling, ranking, citation, or model training, and not a replacement for good IA, search, or structured docs.

See [ai-consumable-docs.md](references/ai-consumable-docs.md) for the AI-docs layer.

### Answer-Engine Hygiene

Help-center pages are often what AI answer engines cite, so keep the facts they would cite clean:

- **Canonical URLs**: one canonical URL per fact; do not duplicate the same answer across the help center and the marketing site.
- **Freshness**: keep review dates and version labels accurate on pages that state limits, prices, or policies.
- **Entity hygiene**: use exact product names, feature names, and error strings consistently across pages.

Do not promise that answer formatting, FAQ or HowTo markup, or `llms.txt` improves AI citation. Route citation-share work to `marketing-aeo-geo`.

## Help Center Architecture

### Category Structure Rules

Size categories from top tasks and ticket intents, then confirm their labels and depth with a tree test. Organize by user goal, separate end-user help from developer docs when the audiences differ, and keep billing, security, troubleshooting, and release notes findable.

### Recommended Top-Level Categories

```
DEFAULT STRUCTURE
1. Getting Started
2. Core Workflows
3. Integrations
4. Account, Billing, and Security
5. Troubleshooting
6. Developers or API
7. Release Notes / What's New
8. Contact / Escalation
```

### Navigation Patterns

- Place search where users can find it on the relevant page layouts; test discovery on mobile and desktop.
- Breadcrumbs and related articles are standard.
- Every troubleshooting article includes an escalation path.
- Every how-to article includes prerequisites, result state, and next steps.
- Versioned products need explicit version selectors or version labels.

## Article Standards

- Keep the core set small: how-to, troubleshooting, conceptual, FAQ, reference, release note.
- Include exact UI labels, feature names, and error strings.
- Remove marketing language from support content.
- Use screenshots only when they materially reduce ambiguity; keep them current.
- Make every article independently understandable to users and retrieval systems.

Use [article-templates.md](references/article-templates.md) for templates and [taxonomy-patterns.md](references/taxonomy-patterns.md) for IA patterns.

## Support AI Design

### Resolution Modes

| Mode | Content the Mode Needs | Source Requirements |
|------|------------------------|---------------------|
| Informational | An approved article that answers the intent | Citations, freshness, fallback |
| Navigational | The canonical page or workflow link | Precise links, plan and role labels |
| Diagnostic | Troubleshooting content: symptoms, causes, fixes | Exact error strings, safe troubleshooting steps |
| Transactional | Task-policy content: preconditions, approvals, completion state | Owner-approved policy with an effective date |
| Escalation | Escalation-policy content: triggers and handoff fields | Trigger rules, summary, captured context |

What the AI may do in each mode, its tool allowlist, and its confirmation rule belong to the [Intent Automation Gate in ai-bot-builder](../ai-bot-builder/SKILL.md#intent-automation-gate).

### Guardrails

- Approved sources list.
- Per-intent tool permissions, set in the bot-builder gate linked above.
- Escalation triggers for low evidence, high risk, or repeated failure.
- Citation requirement for factual claims.
- Simulation and QA before live traffic increases.

See [ai-integration.md](references/ai-integration.md) for implementation patterns.

## Metrics & Quality

### Core Measures

| Metric | What It Answers |
|--------|-----------------|
| Search success | Did users find something relevant? |
| Self-service completion | Did the issue resolve without assisted support? |
| Citation quality | Were answers grounded in the right sources? |
| Escalation quality | Did AI hand off at the right time with enough context? |
| Freshness coverage | Are high-impact pages current? |
| Content gap rate | Which intents have no good answer yet? |

### AI-Specific Measures

- unresolved-intent rate
- citation rate
- tool-call success rate
- reopen-after-AI rate
- stale-source hit rate
- handoff acceptance rate

Measure deflection against a holdout or staggered rollout, and count a self-service session as resolved only when no assisted contact on the same intent follows within a set window. Do not use fixed ROI or benchmark numbers unless the user asks for them and you verify current data. Use the measurement framework in [metrics-optimization.md](references/metrics-optimization.md).

### Judgment Beyond the Checklist

A checklist audit catches missing articles and broken links. It does not catch these failure modes, which matter more and require judgment:

- **Deflection-vs-resolution gap**: a falling contact rate can mean users are self-serving successfully, or it can mean the contact path got harder to find, an AI assistant is stalling instead of escalating, or frustrated users are churning silently instead of reopening. Never trust a deflection or containment number without a paired resolution-quality signal. See [Where Deflection Targets Backfire](references/metrics-optimization.md#where-deflection-targets-backfire).
- **Content debt vs. content gaps**: high ticket volume on a topic with an existing, accurate, recently-reviewed article is usually not a missing-content problem — it is a mismatch between the article and how users describe the issue, or a sign of competing information architectures from past redesigns. Diagnose debt before assigning more writing. See [Content Debt Diagnosis](references/knowledge-ops.md#content-debt-diagnosis).
- **Shallow AI grounding**: a citation on an AI answer does not mean the answer is correct — chunking can separate a rule from its exception, retrieval can return the right fact for the wrong plan or version, and synthesis across two accurate sources can produce an inaccurate combined claim. Citation rate alone will not catch any of this; it requires human review of cited claims against source text. See [Grounding Quality Judgment](references/ai-integration.md#grounding-quality-judgment).

## Knowledge Operations

Operate the help center like a product:
- assign an owner per category and per high-impact article set
- tie content updates to releases, incidents, and high-volume search gaps
- review zero-result searches, escalation-after-view, and low-rated articles on a set cadence
- maintain one canonical source per fact domain where possible

See [knowledge-ops.md](references/knowledge-ops.md), [content-migration-guide.md](references/content-migration-guide.md), [multilingual-support.md](references/multilingual-support.md), and [accessibility-standards.md](references/accessibility-standards.md).

## Navigation

| Resource | Content |
|----------|---------|
| [article-templates.md](references/article-templates.md) | Templates for common help-center article types |
| [taxonomy-patterns.md](references/taxonomy-patterns.md) | Information architecture and metadata patterns |
| [ai-integration.md](references/ai-integration.md) | Retrieval-first support AI, tool policy, and escalation |
| [ai-consumable-docs.md](references/ai-consumable-docs.md) | `llms.txt`, MCP, markdown export, and agent-facing docs |
| [platform-guides.md](references/platform-guides.md) | Platform-fit guidance for support suites and docs portals; the in-app guidance content contract |
| [metrics-optimization.md](references/metrics-optimization.md) | Measurement framework and instrumentation patterns |
| [knowledge-ops.md](references/knowledge-ops.md) | Governance and review cadences |
| [content-migration-guide.md](references/content-migration-guide.md) | Migration, redirects, and validation |
| [multilingual-support.md](references/multilingual-support.md) | Translation workflows and locale operations |
| [accessibility-standards.md](references/accessibility-standards.md) | WCAG 2.2 AA guidance for help content |
| [sources.json](data/sources.json) | Curated external sources with authority and volatility metadata |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
