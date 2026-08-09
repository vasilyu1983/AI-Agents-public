# Knowledge Operations

## Table of Contents

- [Contents](#contents)
- [Governance Model](#governance-model)
- [Content Lifecycle](#content-lifecycle)
- [Freshness And Quality Signals](#freshness-and-quality-signals)
- [Release And Incident Integration](#release-and-incident-integration)
- [Localization And Accessibility](#localization-and-accessibility)
- [AI Support Alignment](#ai-support-alignment)
- [Operating Cadence](#operating-cadence)

Governance and operating cadence for maintaining a high-quality, AI-ready help center over time.

## Contents

- Governance model
- Content lifecycle
- Freshness and quality signals
- Release and incident integration
- Localization and accessibility
- AI support alignment
- Operating cadence

## Governance Model

Define clear ownership so content stays correct, current, and safe.

Recommended roles:
- Help center owner (program owner, prioritization, standards)
- Support operations (tooling, workflows, reporting)
- Product SMEs (technical correctness)
- Legal/security reviewer (when required)
- Writers/editors (clarity, consistency, UX)

Assign ownership at two levels:
- Category owner: responsible for taxonomy area health
- Top-article owner: responsible for the highest-impact articles in that area

## Content Lifecycle

Use a consistent lifecycle to avoid drift:

1. Intake
   - Sources: tickets, search logs, escalations, release notes, incidents.
2. Draft
   - Use standard templates and AI-friendly writing rules.
3. Review
   - SME approval for correctness; legal/security review when needed.
4. Publish
   - Ensure correct IA placement, tags, and internal links.
5. Measure
   - Track helpfulness, search success, and escalation after reading.
6. Improve
   - Rewrite titles, add visuals, and fix missing prerequisites.
7. Retire
   - Redirect obsolete URLs; archive deprecated content with rationale.

## Freshness And Quality Signals

Use both time-based and behavior-based signals.

Freshness signals:
- Product releases affecting a feature referenced in the article
- Broken links, outdated screenshots, or changed UI labels
- Article not updated in 6-12 months (threshold depends on release cadence)

Behavior signals:
- High search-to-exit rate (users give up after searching)
- High escalation rate after article view (content does not resolve the issue)
- High negative feedback rate (thumbs down, low rating)
- High repeat view rate for the same issue (users need multiple passes)

Prioritization heuristic:
- Fix the smallest number of articles that deflect the largest number of tickets.

## Release And Incident Integration

Make content updates a standard part of delivery:

- For every release that changes UI/workflows, update impacted how-to and troubleshooting articles.
- For every incident, publish:
  - "Status and workaround" article (during incident)
  - Post-incident explanation and prevention guidance (after incident)
- Keep a "What's New" category that is also used as a freshness trigger for AI retrieval.

## Localization And Accessibility

Localization:
- Maintain a glossary for product terms and translated UI labels.
- Prefer text instructions over images with embedded text.
- Track translation coverage for the top traffic articles first.

Accessibility:
- Add alt text for images and captions for videos.
- Use headings and lists for structure; avoid conveying meaning by color only.
- Keep steps scannable and avoid long paragraphs.

## Content Debt Diagnosis

A checklist tells you an article is missing or stale. It does not tell you the help center has structural debt — and treating debt as a backlog of individual article fixes wastes effort. Diagnose debt before prescribing more writing:

- **Multiple competing IAs.** Three redesigns left three overlapping category trees (old URLs still resolve, new nav points elsewhere, search indexes both). Symptom: users and AI retrieval both surface two different "correct" answers for the same question. Fix is a taxonomy consolidation project, not a content sprint.
- **Technically-correct, practically-wrong articles.** High ticket volume persists on a topic that already has a current, accurate article. The article is not stale — it just does not match how users describe the problem (their words, their mental model, their error message) or it hides the answer below unrelated context. Rewriting the title and the first two sentences often fixes more than adding new articles does.
- **Tribal knowledge that never made it to docs.** Support agents resolve a recurring issue correctly and consistently, but the resolution only exists in Slack threads, agent macros, or one person's head. High resolution quality with no matching public article is a leading indicator of undocumented debt, not a healthy KB.
- **Orphaned "current" content.** Articles pass every freshness check (recently reviewed, correct facts) but reference a workflow, plan, or UI that shipped a redesign since the last edit. Time-based freshness signals miss this; only usage signals (rising escalation-after-view, rising reopen rate) catch it.
- **Metadata rot.** Plan tier, audience, and version metadata drift out of sync with product reality as pricing and packaging change. This silently degrades AI retrieval (wrong article surfaced for a plan that no longer has that limit) well before anyone notices from the human-facing side.

Distinguish a content gap (no answer exists) from content debt (an answer exists but the system around it is broken) before prioritizing the backlog — they require different fixes and different owners.

## AI Support Alignment

Keep the help center retrieval-friendly:
- Use unique, intent-rich titles.
- Keep error messages verbatim and in dedicated blocks.
- Add metadata where the platform supports it (product area, audience, plan tier, version, last_updated).
- Prefer explicit prerequisites and explicit success criteria.

Define AI answer safety rules:
- Require citations/links for factual answers and procedures.
- Ask clarifying questions when plan tier, role, or product version affects the steps.
- Escalate for billing disputes, account security, legal/compliance, and low confidence.
- For transactional requests, require explicit confirmation before irreversible actions.

Maintain an evaluation set for AI and search:
- Top 50 searches and their expected destination article(s)
- Top 50 tickets and the minimum viable "self-service answer"
- A set of failure-mode queries (ambiguous, missing context, policy-sensitive)

## Operating Cadence

Weekly:
- Review top zero-result searches and add/retitle content.
- Review "high traffic + low helpfulness" articles and rewrite one batch.
- Audit AI escalations to identify content gaps and safety failures.

Monthly:
- Refresh screenshots and UI labels for the highest traffic categories.
- Review top deflection opportunities from ticket tags.
- Validate analytics event coverage and dashboard health.

Quarterly:
- Taxonomy audit (category sprawl, duplicates, broken navigation).
- Content pruning and redirect cleanup.
- Governance review (owners, SLAs, escalation playbooks).
