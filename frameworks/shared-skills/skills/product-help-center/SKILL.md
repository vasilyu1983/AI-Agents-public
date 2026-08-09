---
name: product-help-center
description: Designs AI-first help centers and self-service support systems. Use when shaping taxonomy, article templates, support AI, or docs platform choices.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Help Center Design

Design public help centers, in-app self-service, and AI-consumable documentation systems.

Use this skill when the user needs one of these outcomes:
- pick or compare a help center, docs, or support-AI platform
- design or audit taxonomy, navigation, article standards, and governance
- plan retrieval-first support AI with citations, tool permissions, and escalation
- make docs easier for humans, search, and AI agents to consume

## Workflow

1. Classify the surface
   - Support help center, developer docs portal, internal knowledge base, in-app guidance, or hybrid.
2. Define audience and risk
   - End users, admins, developers, agents, regulated customers, multilingual audiences.
3. Choose the operating model
   - Human-authored docs only, retrieval-first support AI, or agentic support with approved tools.
4. Design information architecture
   - Category structure, navigation, search strategy, metadata, URL rules, and versioning.
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

## ASCII Flow

```text
Help center or support-docs request
  -> Classify surface: help center, developer docs, KB, in-app, or hybrid
  -> Define audience, risk, locale, and support context
  -> Choose operating model
     +-- human-authored docs
     +-- retrieval-first support AI
     +-- agentic support with approved tools
  -> Design IA, taxonomy, metadata, URLs, search, and versioning
  -> Standardize article types and templates
  -> Add measurement: search, self-service, citations, handoff, freshness
  -> Assign owners, review cadence, migration plan, and stale-content loop
```

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
- Zendesk consolidated AI agent tiers in mid-2026: the Essential/Advanced distinction is being removed, with advanced AI features (agentic reasoning, multi-step procedures, external API integrations) included across Suite and Support plans. Legacy Essential functionality reaches end-of-life December 2026. Verify current plan structure before advising on AI agent capabilities.
- Intercom Fin (2026) supports multi-channel deployment (web, iOS, Android, Email, WhatsApp, SMS, Facebook, Instagram), persona customization, and plan/locale-aware content targeting. Pricing is resolution-based; verify current rates.

See [platform-guides.md](references/platform-guides.md) for current platform-fit rules and [sources.json](data/sources.json) for preferred sources.

## 2026 Default Guidance

### Durable Shifts

| Area | Legacy Pattern | 2026 Default |
|------|----------------|--------------|
| Help delivery | Separate help portal | Contextual support across web, app, and AI |
| Search | Keyword-only | Hybrid retrieval: semantic + lexical + metadata |
| AI behavior | Bot answers only | Retrieval-first assistant with explicit escalation policy |
| Content | Text-heavy article library | Structured, visual, version-aware, agent-consumable content |
| Maintenance | Manual cleanup | Release-driven and signal-driven knowledge ops |
| Personalization | Same experience for all | Role, plan, locale, and environment-aware support |

### AI-First Principles

1. Retrieval before generation.
2. Citations before confidence claims.
3. Clarify or escalate before guessing.
4. Tool access by explicit permission, not by default.
5. Knowledge freshness matters as much as model quality.
6. Support AI needs QA, monitoring, and rollback paths.

### AI-Consumable Docs Principles

- Publish stable canonical URLs and clear page titles.
- Keep one main task or concept per page.
- Use headings, tables, lists, and exact error strings.
- Expose machine-friendly surfaces when relevant: markdown export, API references, MCP servers, `llms.txt`, `llms-full.txt`, and agent-facing indexes.
- Treat `llms.txt` as additive and emerging, not a replacement for good IA, search, or structured docs.

See [ai-consumable-docs.md](references/ai-consumable-docs.md) for the AI-docs layer.

### Answer Engine Optimization (AEO)

Help center content is a primary source for AI answer engines (ChatGPT, Perplexity, Gemini, Claude). Two complementary layers improve citation and retrieval:

- **Page-level markup**: use `FAQPage`, `HowTo`, and `Article` schema.org types on help articles. FAQs and step-by-step lists are the formats AI models favour most; explicit schema reinforces what the content is.
- **Site-level signaling**: publish `llms.txt` and `llms-full.txt` at a well-known URL to indicate canonical structure and priority pages to AI crawlers. As of mid-2026, adoption is growing but support is uneven — treat it as a fast-growing signal rather than a guaranteed channel.
- **Content shape**: short declarative answers at the top of each article (before procedural detail) improve extraction by AI answer engines. Use exact product names, error strings, and version numbers — AI engines retrieve verbatim matches better than paraphrases.
- **Canonical hygiene**: one canonical URL per fact; avoid duplicate content across help center and marketing site, which splits AI citation confidence.

These optimizations compound with good IA and structured markup; neither replaces the other.

## Help Center Architecture

### Category Structure Rules

```
HIERARCHY RULES
- Prefer 2 levels; use 3 only when the product genuinely needs it
- Top-level categories: usually 5-8
- Organize by user goal, not internal org chart
- Separate end-user help from developer docs when the audiences differ
- Keep billing, security, troubleshooting, and release notes easy to find
```

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

- Search is always above the fold.
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

### Retrieval-First Support Flow

```
USER QUESTION
  -> classify intent and risk
  -> retrieve from approved sources
  -> answer with citations
  -> clarify if evidence is weak or ambiguous
  -> hand off or execute only if policy allows
  -> log outcome and quality signals
```

### Resolution Modes

| Mode | What AI May Do | Requirements |
|------|----------------|-------------|
| Informational | Answer from approved content | Citations, freshness, fallback |
| Navigational | Send user to the right page or workflow | Precise links, plan/role awareness |
| Diagnostic | Narrow likely cause | Observability context, safe troubleshooting |
| Transactional | Execute approved task | Explicit tool permissions, audit trail, rollback |
| Escalation | Hand to human | Trigger rules, summary, captured context |

### Guardrails

- Approved sources list.
- Tool permission matrix by task.
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

Do not use fixed ROI or benchmark numbers unless the user asks for them and you verify current data. Use the measurement framework in [metrics-optimization.md](references/metrics-optimization.md).

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
| [platform-guides.md](references/platform-guides.md) | Platform-fit guidance for support suites and docs portals |
| [metrics-optimization.md](references/metrics-optimization.md) | Measurement framework and instrumentation patterns |
| [knowledge-ops.md](references/knowledge-ops.md) | Governance and review cadences |
| [content-migration-guide.md](references/content-migration-guide.md) | Migration, redirects, and validation |
| [multilingual-support.md](references/multilingual-support.md) | Translation workflows and locale operations |
| [accessibility-standards.md](references/accessibility-standards.md) | WCAG 2.2 AA guidance for help content |
| [learning-paths.md](references/learning-paths.md) | Onboarding sequences, tutorial design, in-app guidance, and product education course structure |
| [sources.json](data/sources.json) | Curated external sources with authority and volatility metadata |

## Trend Awareness Protocol

When the user asks for recommendations involving vendors, AI features, pricing, or platform relevance:
- run a fresh web search
- prefer official docs and product pages first
- use independent comparisons only as support, not as the decision anchor
- report source links and note dates for volatile claims

Priority source order:
1. Official docs and product pages
2. Official protocol/spec pages
3. High-quality independent comparisons
4. Vendor blogs and SEO content as secondary evidence only

## Fact-Checking

- Verify current pricing, plan limits, AI capabilities, and product naming before final answers.
- Prefer primary sources for platform behavior and protocol details.
- If web access is unavailable, say so and mark volatile guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

