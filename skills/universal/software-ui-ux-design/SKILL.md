---
name: software-ui-ux-design
description: "Designs and audits UI/UX systems with usability and accessibility requirements. Use when shaping flows, design systems, interaction patterns, or WCAG-aware product behavior."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-08-13
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

For agent surfaces — anything that acts on the user's behalf over multiple steps — also score the four agent rows (steerability, action reversibility, cost visibility, memory legibility); a surface can pass every row above and fail all four. See [references/ai-automation-ux.md#agent-surface-craft-bar](references/ai-automation-ux.md#agent-surface-craft-bar).

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

Design new work to WCAG 2.2 AA (conformance also covers 2.1 and 2.0), but the legally binding version differs by jurisdiction and surface (EU public sector, EAA, ADA Title II, Section 508, native apps). Check the jurisdiction table in [references/wcag-accessibility.md#jurisdictional-baselines](references/wcag-accessibility.md#jurisdictional-baselines) before stating what a product must meet; WCAG 3.0 drafts are not a shipping target.

## Verification Checklist

Before finalizing any UI/UX design output:

- [ ] Platform confirmed (web, iOS, Android) and platform-specific constraints applied
- [ ] All five state types covered: loading, empty, error, offline/degraded, and happy path
- [ ] Primary action is singular per view; secondary actions visually subordinate
- [ ] Craft Bar row pass/fail reviewed; fewer than 3 fails before shipping
- [ ] Accessibility is *computed, not asserted*: every contrast ratio in the spec comes from running `scripts/contrast_check.py <fg> <bg>` — never from estimation (a model-estimated ratio labeled "computed" is a fabrication) — and is measured against the surface the text actually renders on (row, card, modal), not only the page canvas; focus order listed element by element; target size ≥24×24 CSS px (WCAG 2.2 AA, SC 2.5.8) with the platform size (44pt iOS / 48dp Android) for primary controls
- [ ] Dynamic content announces itself: any live-updating region (new rows, status changes, streaming) has a specified `aria-live` politeness level and batching rule — a visual pulse alone is invisible to screen readers
- [ ] Single-key shortcuts specify a remap/disable mechanism (WCAG 2.1.4) and focus-scoping rule
- [ ] Press + commit states specified for *every* tappable element, not demonstrated once on the primary CTA and left implicit elsewhere
- [ ] Undo/recovery semantics defined end-to-end: what happens to server state, audit trail, and concurrent users when an action is undone; every focus surface has a named normal-path exit (not just error-path)
- [ ] Consent and accept/reject buttons carry equal visual weight (GDPR/ePrivacy consent rules and regulator cookie guidance)
- [ ] Motion fallback present for any scroll-driven or CSS animation (prefers-reduced-motion)
- [ ] Microcopy uses user voice: names cause, offers specific recovery step
- [ ] AI-generated UI verified in browser with real content, not lorem ipsum
- [ ] Legal obligations checked for EU-facing surfaces: EAA accessibility, GDPR/ePrivacy consent design, and DSA Article 25 for platform dark patterns not already covered by GDPR or consumer law

## Output Contract

Every substantial output should include:

- user/task context
- primary flow
- state coverage
- accessibility and performance checks relevant to the platform
- component or token guidance where needed
- acceptance criteria suitable for implementation or review

## Platform Defaults

| Platform | Key Constraints |
|----------|-----------------|
| web | semantic structure, focus behavior, reflow, target size |
| iOS | system navigation, Dynamic Type, safe areas |
| Android | Material 3 patterns, edge-to-edge, predictive back, large-screen behavior |

## AI Frontend Briefing Rules

When using AI to generate UI, define the visual thesis, page type, content structure, composition rules, and design-system constraints first; require real content instead of lorem ipsum and post-generation browser verification. Full brief template: [references/ai-assisted-frontend-briefing.md](references/ai-assisted-frontend-briefing.md).

## Known Traps

- Designing the happy path only and discovering later that loading, empty, error, permission, and degraded states contradict the main flow.
- Confusing accessibility conformance with usable interaction design, especially for focus order, error recovery, and dense component systems.
- Treating design-system consistency as a substitute for hierarchy, task clarity, or actual decision support in the interface.
- Writing AI frontend briefs around adjectives like `modern` or `clean` without defining composition, content density, or interaction constraints.
- Letting responsive behavior remain implicit, which pushes layout collapse, tap-target, and overflow problems into implementation.
- Recommending patterns from another platform without checking whether web, iOS, or Android conventions support them cleanly.
- Treating EU compliance as a legal afterthought. The European Accessibility Act (applies from 28 June 2025), GDPR/ePrivacy consent rules, and DSA Article 25 (dark patterns on online platforms, excluding practices already covered by GDPR or the Unfair Commercial Practices Directive) create design-level obligations with active enforcement (the CNIL's 2025 fines against Google and SHEIN were for cookies set without valid consent or after refusal, under French data-protection law, not the DSA). For the legal basis in a given case, use qualified EU regulatory counsel. For any EU-facing B2C surface, accessibility and consent design are legal requirements, not preferences.
- Specifying motion or scroll-driven animation without `prefers-reduced-motion` fallback. CSS scroll-driven animations are invisible to users with reduced-motion preferences if the spec doesn't explicitly handle the case.
- Writing accessibility as checklist assertions ("AA minimum", "focus order logical") instead of computed, implementable constraints. Expert review rejects specs whose contrast was never calculated at the element's real size and whose live regions have no announcement behavior — checklist-level a11y reads as bolted-on and fails sign-off.
- Spec depth inversely proportional to surface frequency: the daily-return screen (home, dashboard) written in one paragraph while one-time flows get pages. Detail budget should follow visit frequency.

## Common Anti-Patterns

Over-carding, multiple primary actions, meaning carried only by hover/gesture/animation, unverified AI-generated UI, asymmetric consent buttons, generic empty states, centered spinners, permission walls, robot-voice copy, and decorative motion. Full list with the fix for each: [references/operational-playbook.md#common-anti-patterns-to-avoid](references/operational-playbook.md#common-anti-patterns-to-avoid).

## Navigation

**References** — read at most 2-3 per task; pick the cluster that matches the ask.

*Workflow & systems*

- [references/design-database-search.md](references/design-database-search.md) — offline searchable design database: 80+ styles, 190+ palettes, font pairings, UX guidelines (BM25 search via `scripts/search.py`)
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
- [references/motion-design.md](references/motion-design.md) — functional motion: library landscape (Motion née Framer Motion, GSAP), spring/tween defaults, reduced-motion implementation, motion spec checklist
- [references/consumer-craft-patterns.md](references/consumer-craft-patterns.md) — consumer-grade craft playbook

*Patterns & surfaces*

- [references/modern-ux-patterns.md](references/modern-ux-patterns.md) — contemporary UX patterns and expectations
- [references/mobile-ux-patterns.md](references/mobile-ux-patterns.md) — iOS/Android mobile patterns
- [references/form-design-patterns.md](references/form-design-patterns.md) — layout, validation, multi-step, error handling
- [references/data-visualization-ux.md](references/data-visualization-ux.md) — accessible, interactive charts and dashboards
- [references/surface-type-recipes.md](references/surface-type-recipes.md) — data tables, command palette, settings, search, notifications, pricing, paywalls, comparison tables, comments, forms, onboarding, modals
- [references/simplification-patterns.md](references/simplification-patterns.md) — reducing interface complexity

*Conversion & AI*

- [references/cro-framework.md](references/cro-framework.md) — design-to-CRO hand-off (routes to marketing-cro) and vertical UI benchmarking
- [references/ai-assisted-frontend-briefing.md](references/ai-assisted-frontend-briefing.md) — briefing AI to generate UI
- [references/ai-automation-ux.md](references/ai-automation-ux.md) — UX for chat, agents, and automation; reversibility-tiered approval gates, interruption/steering, cost visibility, agent memory surfaces, the 4-stage human-agent frame, ACI tool design, and the agent-to-UI event contract
- [references/ai-design-tools.md](references/ai-design-tools.md) — AI-assisted design tools: use, quality control, ethics
- [references/performance-ux-vitals.md](references/performance-ux-vitals.md) — perceived performance, loading states, focus on content change (metrics route to software-frontend)

- [data/sources.json](data/sources.json)

**Scripts** — offline design-database search engine (stdlib-only Python, vendored, MIT): `scripts/search.py` (CLI), `scripts/core.py`, `scripts/design_system.py`, and `scripts/contrast_check.py` (the only accepted source for contrast numbers in a spec), over CSV databases in `data/`. Flags, data files, `DESIGN.md` export, and the upstream trust note: [references/design-database-search.md#scripts-and-data-files](references/design-database-search.md#scripts-and-data-files).

**Templates**

- [assets/design-brief.md](assets/design-brief.md)
- [assets/ux-review-checklist.md](assets/ux-review-checklist.md)
- [assets/ui-generation/full-ui-spec.md](assets/ui-generation/full-ui-spec.md)
- [assets/audits/simplification-audit-template.md](assets/audits/simplification-audit-template.md)
- [assets/design-systems/template-design-system.md](assets/design-systems/template-design-system.md)
- [assets/interaction-patterns/template-micro-interactions.md](assets/interaction-patterns/template-micro-interactions.md) — micro-interaction implementation detail, for motion specs in [references/motion-design.md](references/motion-design.md)

## Related Skills

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- [../software-ux-research/SKILL.md](../software-ux-research/SKILL.md)
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md)
- [../software-mobile/SKILL.md](../software-mobile/SKILL.md)
- [../software-accessibility/SKILL.md](../software-accessibility/SKILL.md)
- [../software-localisation/SKILL.md](../software-localisation/SKILL.md)
- [../foundations-consumer-neuroscience/SKILL.md](../foundations-consumer-neuroscience/SKILL.md) — validity of eye-tracking/biometric UX studies and neural-data law scope; attention and salience templates

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
