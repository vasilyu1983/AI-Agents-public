---
name: software-ui-ux-design
description: "Designs and audits UI/UX systems with usability and accessibility requirements. Use when shaping flows, design systems, interaction patterns, or WCAG-aware product behavior."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-08-10
---

# Software UI/UX Design

Use this skill to design or audit interfaces, flows, component systems, and AI-assisted frontend briefs. It owns design direction, interaction behavior, state coverage, and implementation-ready handoff, not user research or code remediation.

## Quick Reference

| Mode | Use When | Required Output |
|------|----------|-----------------|
| audit existing UI | product has usability, accessibility, consistency, or conversion issues | findings plus acceptance criteria |
| design new UI | flow or screen must be shaped from scratch | flow, states, components, handoff spec |
| design-system decision | team must choose primitives or token structure | recommendation with tradeoffs |
| AI frontend brief | Codex or Claude will generate UI | visual thesis, interaction thesis, verification plan |
| AI UX review | product includes chat, agents, or automation | transparency, control, failure handling guidance |
| style/palette/font selection | new surface needs a concrete design direction | generated design system from the offline database (`scripts/search.py --design-system`) |

## When to Use This Skill

Use this skill when the main task is:

- designing screens, flows, or component behavior
- auditing an interface for design-level issues
- choosing design-system patterns or component libraries
- preparing a strong brief for AI-generated frontend work
- reviewing AI/automation UX

Route elsewhere when the main task is:

| Need | Use Instead |
|------|-------------|
| user research and study design | [../software-ux-research/SKILL.md](../software-ux-research/SKILL.md) |
| code-level accessibility fixes | [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md) |
| accessibility test automation | [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md) |
| frontend implementation | [../software-frontend/SKILL.md](../software-frontend/SKILL.md) |
| product strategy or roadmap | [../product-management/SKILL.md](../product-management/SKILL.md) |

## Defaults

- clarify platform, primary user journey, and constraints first
- one primary task flow per output
- cover loading, empty, error, offline, and degraded states — these decide trust, not happy paths
- semantic and accessibility constraints must be present in the handoff
- for AI-generated UI, define visual and interaction thesis before code generation
- verify current platform-guideline claims before final advice
- aim for *consumer-grade craft*, not just "passes audit". A screen that meets WCAG and feels lifeless is not done.

## Craft Bar

Consumer-grade product work is judged on the rows below, not just task completion. Every substantive design output should be reviewed against these.

| Dimension | Pass | Fail |
|-----------|------|------|
| Time to first value | <60s for primary user | multi-step setup wizard |
| Empty state | models populated state with one verb CTA | "No items yet" + grey illustration |
| Loading state | skeleton matching populated layout | centered spinner |
| Error recovery | names cause + offers specific next step in user voice | "Something went wrong" |
| Microcopy | one voice; numbers humanised; verbs in CTAs | system-speak, status codes, noun CTAs |
| Motion | functional (origin → destination, hierarchy) | decorative bounces on every state change |
| Touch feedback | every tappable element has press + commit states | silent commits |
| Optical alignment | icons, numbers, capitals optically balanced | pixel-grid measured equal but reads off |
| First-run delight | one non-functional moment that earns a smile | none |
| Recovery without restart | back, undo, edit-without-redo paths exist | "Are you sure?" gating every action |

If three or more rows fail, the screen is debt regardless of what metrics say. See `consumer-craft-patterns.md` for the full playbook.

For agent surfaces — anything that acts on the user's behalf over multiple steps — add these four rows. They fail independently of the ones above, and a surface can pass every row of the table above while failing all four of these.

| Dimension | Pass | Fail |
|-----------|------|------|
| Steerability | user can add, revise, or retract a requirement mid-run; composer stays live | only "Stop", or input disabled while working |
| Action reversibility | tiered auto / notify+undo / block by what the action does in the world | one confirm dialog for everything, or none |
| Cost visibility | estimate before, accrual during, receipt after — in the user's units | token counts only, or nothing until the invoice |
| Memory legibility | user can see, attribute, edit, and delete what the agent remembers | opaque personalization, or global wipe as the only control |

See [references/ai-automation-ux.md](references/ai-automation-ux.md) for each.

## Workflow

1. Confirm the mode: audit, new UI, design-system decision, or AI frontend brief.
2. Gather states, constraints, and quality bars.
3. For new surfaces, generate a concrete design direction from the offline database: `python3 scripts/search.py "<product> <industry> <tone>" --design-system` (see [references/design-database-search.md](references/design-database-search.md)); persist it with `--persist` for cross-session reuse.
4. Define the primary flow and supporting states.
5. Produce acceptance criteria and implementation-ready handoff details; check priorities 1-3 in [references/ui-quality-priority-rules.md](references/ui-quality-priority-rules.md).
6. For AI-generated UI, add visual anchor, content plan, and browser-based verification path.

## ASCII Flow

```text
UI/UX design task
  -> Confirm mode: audit, new UI, system decision, or AI frontend brief
  -> Gather platform, primary journey, states, constraints, and quality bar
  -> Define hierarchy, interaction model, and supporting states
  -> Add accessibility, performance, and implementation handoff criteria
  -> Specify verification path and evidence needed
  -> Deliver acceptance criteria and unresolved tradeoffs
```

## Accessibility Baseline

WCAG 2.2 is the current W3C standard (October 2023; became ISO standard October 2025) and the legally mandated baseline under the European Accessibility Act (in force June 2025), ADA/Section 508, and EN 301 549. WCAG 3.0 remains a Working Draft — the 3 March 2026 update published the majority of requirements plus a proposed conformance model for public review, and renamed "outcomes" to "requirements". Candidate Recommendation is anticipated Q4 2027 and full Recommendation 2028 or later — do not use it as a compliance target yet. Note its broader stated scope (static, dynamic, interactive, and *streaming* content; apps, tools, publishing) when designing token-by-token streaming agent surfaces: WCAG 2.2 remains the compliance baseline, but streaming UI is squarely in WCAG 3's forward scope.

| Requirement | Minimum target | Notes |
|-------------|---------------|-------|
| Web (EU B2C) | WCAG 2.2 AA | EAA enforcement active; CNIL precedent fines on cookie/consent dark patterns |
| Web (US public) | WCAG 2.2 AA | ADA / Section 508; court-tested |
| iOS / Android | Platform guidelines + WCAG 2.2 AA equivalent | Use native accessibility APIs; avoid custom reimplementations of standard controls |
| Rich media / APNG / video | WCAG 2.2 AA 1.4.2, 1.4.5, 1.2.x | Captions, audio description, no strobing |

## Verification Checklist

Before finalizing any UI/UX design output:

- [ ] Platform confirmed (web, iOS, Android) and platform-specific constraints applied
- [ ] All five state types covered: loading, empty, error, offline/degraded, and happy path
- [ ] Primary action is singular per view; secondary actions visually subordinate
- [ ] Craft Bar row pass/fail reviewed; fewer than 3 fails before shipping
- [ ] Accessibility: focus order, error recovery, target size (≥44×44pt), color contrast (AA minimum)
- [ ] Consent and accept/reject buttons carry equal visual weight (DSA Article 25)
- [ ] Motion fallback present for any scroll-driven or CSS animation (prefers-reduced-motion)
- [ ] Microcopy uses user voice: names cause, offers specific recovery step
- [ ] AI-generated UI verified in browser with real content, not lorem ipsum
- [ ] Legal obligations checked for EU-facing surfaces: EAA accessibility, DSA dark-pattern rules

## Output Contract

Every substantial output should include:

- user/task context
- primary flow
- state coverage
- accessibility and performance checks relevant to the platform
- component or token guidance where needed
- acceptance criteria suitable for implementation or review

## Core Design Rules

- one primary action per view
- immediate feedback for interactions
- explicit recovery paths for failure states
- consistency in language and interaction patterns
- design for the actual platform, not a generic rectangle

## Platform Defaults

| Platform | Key Constraints |
|----------|-----------------|
| web | semantic structure, focus behavior, reflow, target size |
| iOS | system navigation, Dynamic Type, safe areas |
| Android | Material 3 patterns, edge-to-edge, predictive back, large-screen behavior |

## AI Frontend Briefing Rules

When using AI to generate UI:

- define the visual thesis
- define the page type and content structure
- specify composition rules and design-system constraints
- require real content instead of lorem ipsum
- require post-generation browser verification

## Known Traps

- Designing the happy path only and discovering later that loading, empty, error, permission, and degraded states contradict the main flow.
- Confusing accessibility conformance with usable interaction design, especially for focus order, error recovery, and dense component systems.
- Treating design-system consistency as a substitute for hierarchy, task clarity, or actual decision support in the interface.
- Writing AI frontend briefs around adjectives like `modern` or `clean` without defining composition, content density, or interaction constraints.
- Letting responsive behavior remain implicit, which pushes layout collapse, tap-target, and overflow problems into implementation.
- Recommending patterns from another platform without checking whether web, iOS, or Android conventions support them cleanly.
- Treating EU compliance as a legal afterthought. The European Accessibility Act (in force since 28 June 2025) and DSA Article 25 (dark-pattern prohibition) create design-level obligations with active enforcement (in September 2025 the CNIL fined Google €325M and SHEIN €150M for cookie-consent dark patterns). For any EU-facing B2C surface, accessibility and consent design are legal requirements, not preferences.
- Specifying motion or scroll-driven animation without `prefers-reduced-motion` fallback. CSS scroll-driven animations are invisible to users with reduced-motion preferences if the spec doesn't explicitly handle the case.
- Designing agent surfaces where the only mid-run control is "Stop". Users change their mind in three distinct ways — adding a requirement, revising the goal, retracting part of it — and collapsing all three into a cancel button forces the most destructive option. Interruption is a normal interaction, not an error path.
- Gating agent actions by model confidence instead of by real-world reversibility. High confidence on an irreversible action is still irreversible; confidence belongs in the display, never in the gating decision.
- Shipping a "notify and undo" affordance whose undo does not actually work. That is an unrecoverable action wearing a recoverable-looking UI — worse than an honest confirmation dialog. If the undo can't be built, promote the action to a blocking gate.

## Common Anti-Patterns

- Over-carding and over-sectioning every surface until the primary task disappears into chrome.
- Designing multiple primary actions per screen and then relying on color or emphasis tweaks to recover clarity.
- Using hidden gestures, hover-only affordances, or animation to carry critical meaning.
- Treating AI-generated UI as almost done before browser verification, semantic checks, and real-content pass.
- Optimizing purely for visual novelty when the product needs trust, comprehension, and low cognitive load.
- Asymmetric Accept vs Reject buttons in consent flows (different size, color, or visual weight). Under DSA Article 25 and CNIL enforcement practice, both options must carry equal visual weight; pre-ticked consent boxes and forced-consent walls are explicitly prohibited.
- Showing AI-generated content in high-stakes surfaces (medical, legal, financial, safety-critical) without a mandatory human confirmation gate before action.
- Generic empty states ("No items yet" + grey illustration). Empty states are the first impression of every feature — model the populated state, offer a verb-driven CTA, speak to motivation.
- Centered spinners when the layout is known. Skeleton screens that match the populated layout feel faster even when actual load is identical.
- Onboarding tour carousels with lottie illustrations. Skipped by everyone; replace with first-action UI and contextual coaching.
- Permission walls on first launch. Defer; explain in-context at the moment the permission is needed.
- Form labels inside fields that disappear on focus. Use labels above inputs; floating labels fail older users and screen readers.
- Robot voice in error and confirmation copy ("Operation completed successfully", "An unexpected error occurred"). Use user-voice: name what happened, offer recovery.
- Decorative motion on every state change. Spring-bouncing into existence is not joy; it's noise. Reserve pronounced motion for navigation transitions and primary commit moments.

## Navigation

**References** — read at most 2-3 per task; pick the cluster that matches the ask.

*Workflow & systems*

- [references/design-database-search.md](references/design-database-search.md) — offline searchable design database: 80+ styles, 160 palettes, font pairings, UX guidelines, 16 stacks (BM25 search via `scripts/search.py`)
- [references/ui-quality-priority-rules.md](references/ui-quality-priority-rules.md) — priority-ordered quality rules (1=accessibility … 10=charts) plus professional-polish rules and app pre-delivery checklist
- [references/implementation-research-workflow.md](references/implementation-research-workflow.md) — research-to-implementation workflow
- [references/ui-generation-workflows.md](references/ui-generation-workflows.md) — end-to-end UI creation from discovery to handoff
- [references/prototype-to-production.md](references/prototype-to-production.md) — closing the gap between prototype and shipped UI
- [references/design-systems.md](references/design-systems.md) — token structure, primitives, design-system decisions
- [references/design-token-governance.md](references/design-token-governance.md) — two-tier token source of truth, parity guard, optional four-layer ownership taxonomy
- [references/component-library-comparison.md](references/component-library-comparison.md) — choosing component libraries
- [references/operational-playbook.md](references/operational-playbook.md) — day-to-day UI/UX decision frameworks

*Heuristics, accessibility & inclusion*

- [references/nielsen-heuristics.md](references/nielsen-heuristics.md) — usability heuristics
- [references/wcag-accessibility.md](references/wcag-accessibility.md) — WCAG conformance guidance
- [references/neurodiversity-design.md](references/neurodiversity-design.md) — patterns for ADHD, autism, dyslexia, dyscalculia
- [references/demographic-inclusive-design.md](references/demographic-inclusive-design.md) — patterns by age group and life stage
- [references/cultural-design-patterns.md](references/cultural-design-patterns.md) — international, RTL, and regional-market patterns

*Visual craft*

- [references/frontend-aesthetics.md](references/frontend-aesthetics.md) — distinctive design beyond template-driven looks
- [references/typography-systems.md](references/typography-systems.md) — systematic, accessible, responsive type
- [references/dark-mode-theming.md](references/dark-mode-theming.md) — dark mode and multi-theme systems
- [references/consumer-craft-patterns.md](references/consumer-craft-patterns.md) — consumer-grade craft playbook

*Patterns & surfaces*

- [references/modern-ux-patterns.md](references/modern-ux-patterns.md) — contemporary UX patterns and expectations
- [references/mobile-ux-patterns.md](references/mobile-ux-patterns.md) — iOS/Android mobile patterns
- [references/form-design-patterns.md](references/form-design-patterns.md) — layout, validation, multi-step, error handling
- [references/data-visualization-ux.md](references/data-visualization-ux.md) — accessible, interactive charts and dashboards
- [references/surface-type-recipes.md](references/surface-type-recipes.md) — data tables, command palette, settings, search, notifications, pricing, paywalls, comparison tables, comments, forms, onboarding, modals
- [references/simplification-patterns.md](references/simplification-patterns.md) — reducing interface complexity

*Conversion & AI*

- [references/cro-framework.md](references/cro-framework.md) — conversion optimization via research and testing
- [references/ai-assisted-frontend-briefing.md](references/ai-assisted-frontend-briefing.md) — briefing AI to generate UI
- [references/ai-automation-ux.md](references/ai-automation-ux.md) — UX for chat, agents, and automation; reversibility-tiered approval gates, interruption/steering, cost visibility, agent memory surfaces, the 4-stage human-agent frame, ACI tool design, and the agent-to-UI event contract
- [references/ai-design-tools.md](references/ai-design-tools.md) — AI-assisted design tools: use, quality control, ethics

*Performance*

- [references/performance-ux-vitals.md](references/performance-ux-vitals.md) — Core Web Vitals and perceived performance

- [data/sources.json](data/sources.json)

**Scripts** — offline design-database search engine (stdlib-only Python, vendored from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), MIT)

> **Upstream trust note (verified 2026-08-10):** that repo shows 115,186 stars against only 493 watchers and 30 contributors on a repo created 2025-11-30 — a star-inflation signature. This says nothing about the vendored content, which was taken on merit and is unaffected. It does mean: never cite its star count as social proof, and re-diff before pulling any upstream update.

- `scripts/search.py` — CLI: `--design-system`, `--domain <domain>`, `--stack <stack>`, `--persist`
- `scripts/core.py` — BM25 engine and CSV domain config
- `scripts/design_system.py` — design-system generation and Master + page-overrides persistence
- `data/*.csv` and `data/stacks/*.csv` — style, color, typography, product, landing, chart, UX-guideline, icon, and per-stack databases
- `data/slides/*.csv` — slide/deck design database (layouts, typography, charts, copy formulas, backgrounds, color logic, layout logic, narrative strategies); not yet wired into `scripts/core.py` domain config, so `scripts/search.py` cannot query it directly — read these CSVs directly until the engine is extended
- `data/cip/*.csv` — corporate identity pack reference data (industries, deliverables, mockup contexts); same caveat — not yet wired into the search engine

**Templates**

- [assets/design-brief.md](assets/design-brief.md)
- [assets/ux-review-checklist.md](assets/ux-review-checklist.md)
- [assets/ui-generation/full-ui-spec.md](assets/ui-generation/full-ui-spec.md)
- [assets/audits/cro-audit-template.md](assets/audits/cro-audit-template.md)
- [assets/audits/simplification-audit-template.md](assets/audits/simplification-audit-template.md)
- [assets/accessibility/template-wcag-testing.md](assets/accessibility/template-wcag-testing.md)
- [assets/design-systems/template-design-system.md](assets/design-systems/template-design-system.md)

## Related Skills

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- [../software-ux-research/SKILL.md](../software-ux-research/SKILL.md)
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md)
- [../software-mobile/SKILL.md](../software-mobile/SKILL.md)
- [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md)
- [../software-localisation/SKILL.md](../software-localisation/SKILL.md)
- [../foundations-consumer-neuroscience/SKILL.md](../foundations-consumer-neuroscience/SKILL.md) — attention/salience, predictive processing, embodied cognition, and reward-anticipation primitives underlying interface design decisions

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current platform guidelines, accessibility baselines, and component-library claims before final advice.
- Prefer official platform docs and standards over trend roundups.
- If live verification is unavailable, mark external guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

