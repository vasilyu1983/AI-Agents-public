# AI-Assisted Frontend Briefing

Use this reference when the user is asking an AI to generate or reshape a frontend and the output quality depends on the brief, not just the code.

## Table of Contents

- [Scope](#scope)
- [Shared Quickstart](#shared-quickstart)
- [Runtime-Scoped Notes](#runtime-scoped-notes)
- [Required Brief Before Coding](#required-brief-before-coding)
- [Composition Rules](#composition-rules)
- [Structure the Page as a Narrative](#structure-the-page-as-a-narrative)
- [Landing Pages vs Apps](#landing-pages-vs-apps)
- [Copy and Imagery Rules](#copy-and-imagery-rules)
- [Component Sourcing and Generated Assets](#component-sourcing-and-generated-assets)
- [Motion and Verification](#motion-and-verification)
- [Typical Failure Modes](#typical-failure-modes)
- [Litmus Checks](#litmus-checks)

## Scope

- Shared baseline: establish the visual thesis, content plan, interaction thesis, and page type before implementation.
- Runtime-scoped Codex notes: the reasoning-level guidance and model-specific workflow details below are derived from OpenAI's published frontend guidance for its current-generation coding model (as of early 2026) and should not be treated as a universal frontend rule for every model or assumed current without re-checking OpenAI's latest developer guidance.
- If an existing product, brand, or design system already exists, preserve it. These rules are defaults for greenfield work or deliberate redesigns.

## Shared Quickstart

- Define the design system upfront: typography, color palette, layout rules, tokens, and component constraints.
- Provide visual references. If none exist, have the agent generate a mood board or a few visual directions first.
- Use real copy, real product context, and a clear page goal. Placeholder text usually produces placeholder design.
- Pick one golden screen before generating additional pages or variants.
- Decide the surface type up front: landing page, marketing surface, app shell, dashboard, or detail page.
- Plan a verification loop before implementation: browser inspection, viewport checks, and comparison against references where tooling exists.

## Runtime-Scoped Notes

- For Codex specifically, start with low or medium reasoning unless the UI problem is genuinely complex (verify this default against current OpenAI guidance, since reasoning-effort defaults shift across model releases).
- If a runtime has strong browser tooling available, use it to visually inspect the page instead of trusting the first generated draft.
- Keep any claims about model strengths or weaknesses scoped to the runtime where they were observed.

## Required Brief Before Coding

Write these items first:

- **Visual thesis**: one sentence on the mood, energy, and overall visual direction
- **Content plan**: hero, support, detail, proof, final CTA
- **Interaction thesis**: the 2-3 motions that should create hierarchy or atmosphere
- **Page type**: landing page, marketing surface, app shell, dashboard, or detail page
- **Surface constraints**: existing design-system rules, viewport budget, sticky-header budget, and fixed/floating UI constraints
- **Reference inputs**: screenshots, mood board, brand system, or live product references
- **Verification plan**: which viewports, which states, and which browser or rendering checks will be used after generation

## Composition Rules

- The first viewport should read as one composition, not a pile of components.
- On branded pages, the brand or product name should be a hero-level signal, not just nav text or an eyebrow.
- Pick or build one golden screen before generating additional pages. New screens should feel like they belong to that reference immediately.
- Use a strong visual anchor in the hero.
- On landing pages, default to a dominant full-bleed hero image or background plane unless the established design system clearly requires otherwise.
- Keep the first viewport lean: brand, one headline, one short supporting sentence, one CTA group, and one dominant image is usually enough.
- Treat the hero as a viewport budget, not an infinite canvas. Fixed headers, floating controls, and overlays must not obscure the main identity, CTA, or hero media.
- Do not place detached labels, floating badges, promo stickers, info chips, or callout boxes on top of hero media by default.
- Avoid cards by default; never use cards in the hero unless a card is the interaction itself.
- Keep one purpose per section.
- Keep typography and color tightly constrained. As a default, use no more than two typefaces and one accent color.
- Use real content and real product context. Placeholder copy produces generic output.
- Define semantic tokens up front: background, surface, primary text, muted text, accent, and typography roles.
- Prefer intent-revealing token names like `color-primary` and `button-padding` over raw values or vague labels.
- If a design system exists, express it as tokens as data, components as templates, and guidelines as constraints.
- Use motion to create presence and hierarchy, not noise. Ship 2-3 intentional motions, not many decorative ones.
- Prefer expressive, purposeful typography and a clear visual direction over default SaaS styling.

## Structure the Page as a Narrative

Before implementation, define:

- **Visual thesis**: what the page should feel like at first glance
- **Content plan**: what each section needs to communicate
- **Interaction thesis**: where motion adds hierarchy or presence

For marketing and landing pages, this sequence is the default:

1. Hero: establish identity and promise
2. Supporting imagery: show context or atmosphere
3. Product detail: explain the offer
4. Social proof: build credibility
5. Final CTA: convert

Each section should have one job. If a section is trying to do two things, cut one.

## Landing Pages vs Apps

### Landing Pages and Promotional Surfaces

- Default to a strong visual thesis, a dominant hero, and a page that reads as a narrative rather than a document.
- Use imagery that shows the product, place, atmosphere, or context. Decorative gradients alone are not the main visual idea.
- Avoid clutter in the first screen: stats strips, icon rows, metadata blocks, event schedules, and secondary promos usually dilute the core message.
- Let imagery do real narrative work. Avoid collage-like hero treatments, UI screenshots buried inside busy scenes, or decorative artifacts that compete with the CTA.

### Apps and Dashboards

- Default to restraint: calm surface hierarchy, strong spacing, few colors, and dense but readable information.
- Cards are allowed when the card is the interaction. If removing borders, shadows, or backgrounds does not hurt understanding, it probably should not be a card.
- Avoid dashboard mosaics, thick borders around every region, decorative gradients, and multiple competing accent colors.
- Prefer utility copy over promotional copy. Headings, labels, and empty states should help an operator act quickly instead of sounding like a landing page.

## Copy and Imagery Rules

- Marketing surfaces can use promise-driven copy, but app surfaces should default to utility copy: clear labels, fast scanning, and direct next steps.
- Do not let generated copy explain the design itself. UI text should help the user use the product, not narrate visual intent.
- Use one strong visual idea per section. If an image is present, it should either establish atmosphere, explain the product, or support trust.
- If an image can be removed without changing the reading of the section, the image is probably decorative and should be reconsidered.
- When existing brand photography or product visuals exist, prefer them over synthetic style exploration.

## Component Sourcing and Generated Assets

Optional accelerators for the brief — each requires the brief to exist first; none replaces it.

- **Component registries with MCP access** (e.g., 21st.dev's 21st MCP — see [component-library-comparison.md](component-library-comparison.md)): useful for pulling or generating shadcn-convention components in the project's own style during prototyping. Always follow a pull with a license check and a token-normalization pass against the brief's semantic tokens — registry components arrive with their own values baked in.
- **Generated visual anchors**: when no brand photography exists, any connected image-generation MCP (see [ai-design-tools.md](ai-design-tools.md)) can produce the hero image or mood-board directions the Shared Quickstart calls for. Specify aspect ratio to match the target viewport, generate 2-4 variants, and pick one *before* code generation so the composition is designed around a real asset, not a placeholder box.
- **Generated motion references**: video-generation tools with named camera presets can communicate an interaction thesis ("slow dolly-in on the hero") more precisely than adjectives — use as a reference artifact in the brief, not as shipped media, and confirm commercial-use rights before any generated asset ships.
- **DESIGN.md as the brief carrier**: when the design system is generated from this skill's offline database, export it as a `DESIGN.md` file in the project root (`scripts/search.py --design-system --format designmd`) so any coding agent — Claude Code, Cursor, Windsurf — picks up the same tokens and constraints without re-briefing.

## Motion and Verification

- Pick 2-3 intentional motions and commit to them:
  - one entrance sequence in the hero
  - one scroll-linked, sticky, or spatial transition
  - one hover, reveal, or layout transition
- If a motion is only decorative, remove it.
- Respect reduced-motion preferences and preserve orientation cues when toning motion down.
- Use browser tools such as Playwright when available to inspect rendered pages, compare against references, test multiple viewports, and refine the output visually.
- Verify both the first viewport and one downstream screen before calling the visual system coherent.

## Typical Failure Modes

- generic card grids
- weak hierarchy
- weak or invisible branding
- decorative gradients standing in for a real visual idea
- too many colors or type styles
- cluttered first viewports
- promotional hero language leaking into app surfaces
- fixed headers or floating elements colliding with the hero composition
- images that decorate instead of communicate
- sections doing multiple jobs
- motion that adds noise rather than hierarchy

## Litmus Checks

- Is the brand or product unmistakable in the first screen?
- If the first viewport lost the nav, would it still feel unmistakably on-brand?
- Would a newly generated screen obviously match the golden screen?
- Can the page be understood by scanning headlines only?
- For apps and dashboards, can an operator understand the page by scanning headings, labels, and numbers?
- Does each section have one job?
- Are cards actually necessary?
- If you remove the hero image and the page still works, was the image strong enough?
- Would the page still feel strong without decorative shadows?
