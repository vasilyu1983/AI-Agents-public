# AI Design Tools

When AI tools help product-UI design work, how to connect design files to coding agents, and how to review what they generate. Image, video and brand-asset generation, model routing and usage rights live in marketing-visual-design/references/ai-design-tools.md; disclosure and provenance duties live in ai-governance-disclosure.md.

## Table of Contents

- [Route by Job, Not by Brand](#route-by-job-not-by-brand)
- [Design Files to Code: Figma MCP and Code Connect](#design-files-to-code-figma-mcp-and-code-connect)
- [When Not to Use AI Tools](#when-not-to-use-ai-tools)
- [Reviewing Generated UI](#reviewing-generated-ui)
- [Prompting for UI Copy](#prompting-for-ui-copy)
- [Related Resources](#related-resources)

---

## Route by Job, Not by Brand

Tool names, features, ownership and pricing in this category change within months. Pick the job first, then check the current docs of two or three candidates for that job on the day you decide.

| Job | Tool category | Example tools (verify current capability) | Output to expect |
|-----|---------------|-------------------------------------------|------------------|
| Information architecture | Sitemap and wireframe generators | Relume | Sitemap and low-fi wireframes to refine by hand |
| Design exploration | In-canvas AI and design generators | Figma AI, Google Stitch, Magic Patterns | Several layout directions for a stakeholder review |
| Prompt-to-app | App generators that build and host running apps | Figma Make, v0, Lovable, Bolt | A working prototype, sometimes publishable and wired to a backend; treat it as a prototype until reviewed |
| Marketing sites | AI site builders | Framer AI | Live pages owned by marketing, not the product codebase |
| Component code in the repo | Repo-aware coding agents | Claude Code, Cursor, Copilot | Code that must match the repo's design system |
| UI copy | General LLMs | Claude and similar | Variations to test against the voice guide |
| Images, icons, video | Generative media | See the marketing-visual-design routing table | Assets; use an icon library for UI icons |

The distinction worth holding: exploration tools answer "which direction?" for a review; prompt-to-app tools answer "does this flow work?" with running code. Neither output is production code for an existing product until it passes the review below and is rebuilt on the repo's components and tokens.

## Design Files to Code: Figma MCP and Code Connect

Figma provides an MCP server that gives coding agents structured design context (frames, variables, components, layout) instead of screenshots. It is available as a remote server (endpoint `https://mcp.figma.com/mcp`) and through the desktop app. **Code Connect** maps Figma components to the real code components, so the agent emits `<Button variant="primary">` from the design system rather than a fresh approximation.

Operating rules:

- Set up Code Connect for the core components before asking an agent to build screens from Figma; without it, expect near-duplicate components.
- Keep design tokens as Figma variables that mirror the code tokens (see [design-token-governance.md](design-token-governance.md)); the agent can then reference token names instead of raw values.
- Select a single frame or component per request; very large selections produce truncated or low-quality context.
- Which seats can write to the canvas versus read only, rate limits, per-call response-size limits, and support for images and custom fonts are plan- and release-dependent. Check the [Figma MCP server docs](https://developers.figma.com/docs/figma-mcp-server/) before promising a workflow.
- Review agent output against the design with the same checklist as any generated UI; MCP context reduces guesswork but does not verify states, accessibility or responsiveness.

Other design-tool MCP servers exist for asset generation; treat each as a third-party integration (check commercial-use rights, data handling and pricing on the provider's own pages before a client deliverable).

## When Not to Use AI Tools

- Final brand identity decisions and the design system's core tokens.
- Accessibility sign-off: automated checks and generated code both miss keyboard, focus and screen-reader behaviour.
- Legal, compliance, pricing and consent copy.
- Research synthesis where the context of individual sessions matters.
- Cultural-sensitivity review for localised markets.
- Final UI acceptance without human design and engineering review.

Use AI tools as accelerators, not decision-makers.

## Reviewing Generated UI

Run this before any generated screen or component enters review:

- **System fit**: uses existing components and tokens; no new near-duplicate component; no raw hex, px or font values; icons from the project's icon family.
- **States**: loading, empty, error, success, disabled and long-content states exist, not just the happy path.
- **Responsive**: works at the narrowest supported width and at 200% zoom; no fixed-width containers or horizontal scroll.
- **Accessibility**: semantic elements, visible labels, focus styles, keyboard paths, contrast checked with `../scripts/contrast_check.py`, reduced-motion variants; see [wcag-accessibility.md](wcag-accessibility.md).
- **Generic-AI tells**: default font choices, purple-blue gradients, three identical feature columns and other tells listed in [frontend-aesthetics.md](frontend-aesthetics.md#anti-patterns-checklist).
- **Code**: imports resolve at the installed versions; no second pattern for something the repo already does (modals, fetching, forms); types and lint pass.
- **Content**: no placeholder or invented data, claims or testimonials; inclusive language and imagery; licensing of any generated asset recorded.

## Prompting for UI Copy

Give the model the surface, the user's state, the voice, the constraints and the job of the text, and ask for several options:

```text
Write 5 options for the error shown when a saved card is declined at checkout.
User state: mid-purchase, cart still intact.
Voice: calm, plain, no blame. Title under 40 characters, body under 100.
Must say what happened and the next step (try another card or contact the bank).
```

Pick against the voice guide and test the shortlist with users or in an experiment; never ship generated legal, pricing or compliance text without review.

## Related Resources

- [ai-assisted-frontend-briefing.md](ai-assisted-frontend-briefing.md) — the brief to write before any generation
- [ui-generation-workflows.md](ui-generation-workflows.md) — the full design process
- [component-library-comparison.md](component-library-comparison.md) — choosing the component base the agent should build on
- [design-systems.md](design-systems.md) — system architecture
