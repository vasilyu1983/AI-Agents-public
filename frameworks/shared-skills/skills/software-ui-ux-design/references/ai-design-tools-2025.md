# AI Design Tools (2025-2026)

Guide to AI-assisted design tools: when to use them, quality control, and ethical considerations.

**Last Updated**: January 2026
**References**: [Figma AI](https://www.figma.com/ai/), [Vercel v0](https://v0.dev/), [Google Stitch](https://stitch.withgoogle.com/), [Relume](https://www.relume.io/), [Anthropic Guidelines](https://www.anthropic.com/responsible-disclosure)

---

## Tool Landscape

### Design Generation Tools

| Tool | Category | Output | Best For |
|------|----------|--------|----------|
| **Figma AI** | Design tool | Figma components | Layout suggestions, auto-layout |
| **v0 (Vercel)** | Code generation | React/Tailwind/shadcn | Component code from prompts |
| **Google Stitch** | Design generation | Full UI designs | Rapid prototyping (formerly Galileo AI, acquired by Google 2025) |
| **Relume** | Sitemap/Wireframes | Sitemaps + wireframes | Information architecture, Figma/Webflow integration |
| **Framer AI** | Web builder | Live websites | Marketing pages |
| **Midjourney** | Image generation | Images | Design assets, hero images |
| **DALL-E 3** | Image generation | Images | Icons, illustrations |
| **Adobe Firefly** | Image generation | Images + effects | Photo editing, generative fill |
| **Claude** | Text generation | Copy, specs | UI copy, documentation |
| **Cursor/Copilot** | Code assistance | Code | CSS, component logic |

### When to Use AI Tools

| Scenario | Tool | Value |
|----------|------|-------|
| Rapid wireframing | Figma AI, Google Stitch | Speed |
| Sitemap generation | Relume | Complete IA from prompts |
| Component scaffolding | v0 | Boilerplate reduction |
| Design asset creation | Midjourney, Firefly | Unique visuals |
| Copy iteration | Claude | Variations fast |
| Accessibility check | Lighthouse, axe | Automated audit |
| Code implementation | v0, Copilot | Dev speed |

### When NOT to Use AI Tools

```
AVOID AI for:
- Final brand identity decisions (needs human creativity)
- Accessibility compliance (requires expert review)
- Legal/compliance copy (needs legal review)
- User research synthesis (context matters)
- Edge case handling (AI misses nuance)
- Cultural sensitivity review (requires cultural expertise)
```

---

## Tool Deep Dives

### Figma AI

**Capabilities (2025)**
- Auto-layout suggestions
- Component recommendations
- Color palette generation
- Text rewriting/variation
- Image background removal
- Design search ("find all buttons")

**Usage Patterns**
```
GOOD PROMPTS:
- "Create a pricing table with 3 tiers"
- "Suggest color palette for healthcare app"
- "Auto-layout this frame"

POOR PROMPTS:
- "Make it look good" (too vague)
- "Design entire app" (too broad)
- "Copy competitor's style" (ethical issue)
```

**Quality Control**
```
AFTER Figma AI generation:
- [ ] Check color contrast (use Stark plugin)
- [ ] Verify component consistency
- [ ] Test responsive behavior
- [ ] Review accessibility (focus states)
- [ ] Ensure brand alignment
```

### v0 (Vercel)

**Capabilities**
- React/Next.js component generation
- Tailwind CSS styling
- shadcn/ui component usage
- TypeScript types
- Responsive design

**Prompt Engineering for v0**
```
STRUCTURE:
[Component type] with [key features]
Style: [design system/aesthetic]
Include: [specific requirements]
Accessibility: [specific needs]

EXAMPLE:
"Create a product card with image, title, price, and add-to-cart button.
Style: Clean, modern with subtle shadows.
Include: Sale badge, rating stars, hover state.
Accessibility: Proper focus states, aria-labels."
```

**Output Review Checklist**
```
CODE QUALITY:
- [ ] TypeScript types complete
- [ ] Props make sense
- [ ] No hardcoded values
- [ ] Responsive breakpoints work

ACCESSIBILITY:
- [ ] Semantic HTML (button, not div)
- [ ] ARIA labels present
- [ ] Focus states visible
- [ ] Keyboard navigable

DESIGN:
- [ ] Matches design system
- [ ] States (hover, focus, disabled) complete
- [ ] Loading/error states included
```

### Midjourney / DALL-E for Design Assets

**Use Cases**
| Asset Type | Good Fit | Approach |
|------------|----------|----------|
| Hero images | Yes | Generate, then edit |
| Illustrations | Yes | Style consistency prompts |
| Icons | Limited | Better to use icon libraries |
| Photos of real people | Caution | Ethical concerns |
| Product photos | No | Use real products |

**Prompt Structure**
```
[Subject], [style], [mood], [technical specs]

EXAMPLE:
"Abstract geometric pattern, minimal, calm blue tones,
seamless tileable, 4K resolution, flat design"

"Isometric office workspace, tech startup aesthetic,
warm lighting, no people, clean lines"
```

**Quality Control for Generated Images**
```
CHECK:
- [ ] No artifacts or distortions
- [ ] Consistent style across assets
- [ ] Appropriate for brand
- [ ] No copyright concerns
- [ ] Culturally appropriate
- [ ] Accessibility (alt text planned)
- [ ] Resolution sufficient
```

### Claude for UI Copy

**Use Cases**
- Button text variations
- Error messages
- Empty states
- Onboarding copy
- Microcopy (tooltips, labels)
- A/B test variations

**Prompt Patterns**
```
BUTTON VARIATIONS:
"Generate 5 variations for a call-to-action button
that invites users to start a free trial.
Tone: Friendly, not pushy.
Length: 2-4 words."

ERROR MESSAGES:
"Write an error message for when a user's
payment card is declined.
Requirements:
- Don't blame the user
- Suggest next steps
- Keep under 50 characters for title
- Keep description under 100 characters"

EMPTY STATES:
"Create empty state copy for an empty inbox.
Include:
- Heading (encouraging)
- Description (helpful)
- CTA text (actionable)"
```

---

## AI Design Workflow Integration

### Phase Integration

| Design Phase | AI Integration | Human Role |
|--------------|----------------|------------|
| Discovery | Research synthesis help | Strategy decisions |
| Information Architecture | Sitemap suggestions | Structure validation |
| Wireframes | Layout generation | UX decisions |
| Visual Design | Component generation | Brand refinement |
| Prototyping | Interactive code | Testing |
| Handoff | Spec generation | Review and approval |

### Hybrid Workflow Example

```
1. DISCOVERY
   Human: Define goals, conduct research
   AI: Summarize research findings

2. INFORMATION ARCHITECTURE
   AI: Generate sitemap and wireframes (Relume)
   Human: Review and refine structure

3. IDEATION
   AI: Generate 5 layout variations (Figma AI, Google Stitch)
   Human: Select and refine best concepts

4. COMPONENTS
   AI: Generate component code (v0)
   Human: Review accessibility, adjust styling

5. COPY
   AI: Generate copy variations (Claude)
   Human: Select, edit for voice/tone

6. ASSETS
   AI: Generate placeholder images (Midjourney)
   Human: Replace with final assets or approve

7. HANDOFF
   AI: Generate component specs
   Human: Review, add context, approve
```

---

## Quality Control Framework

### AI Output Review Checklist

```
DESIGN:
- [ ] Aligns with design system
- [ ] Consistent with brand
- [ ] Appropriate for context
- [ ] No copied copyrighted elements

ACCESSIBILITY:
- [ ] WCAG AA compliant
- [ ] Screen reader compatible
- [ ] Keyboard navigable
- [ ] Motion preferences respected

CODE:
- [ ] Clean, maintainable
- [ ] Type-safe (if TypeScript)
- [ ] No security vulnerabilities
- [ ] Performance acceptable

CONTENT:
- [ ] Factually accurate
- [ ] Culturally appropriate
- [ ] Inclusive language
- [ ] Legal compliance
```

### Bias Detection

```
CHECK for:
- Gender bias in imagery/language
- Age bias (only young people shown)
- Cultural bias (Western-centric)
- Ability bias (no disability representation)
- Socioeconomic bias

MITIGATION:
- Use diverse reference images
- Review generated content for representation
- Test with diverse user groups
- Include diversity requirements in prompts
```

---

## Ethical Guidelines

### What's Allowed

```
ACCEPTABLE:
- Using AI for ideation and exploration
- Generating variations for testing
- Creating placeholder content
- Automating repetitive tasks
- Summarizing research
- Generating code scaffolding
```

### What Requires Caution

```
PROCEED WITH CARE:
- Generated images of people (disclose)
- Copy for legal/compliance (human review required)
- Brand-critical decisions (human approval)
- Accessibility compliance (expert verification)
- User-facing final content (review carefully)
```

### What to Avoid

```
DO NOT:
- Pass AI work as fully human-created (when disclosure expected)
- Use AI to copy competitor designs
- Generate content that violates copyright
- Create deceptive or manipulative content
- Skip human review for safety-critical UIs
- Use AI for final accessibility compliance
```

### Disclosure Practices

| Context | Disclosure |
|---------|------------|
| Internal ideation | Not required |
| Client presentations | Mention if asked |
| Public portfolio | Best to disclose |
| Marketing materials | Depends on context |
| User-facing content | Check legal requirements |

---

## Tool-Specific Tips

### Maximizing v0 Output

```
PROMPT TIPS:
1. Be specific about component type
2. Reference design systems (shadcn, Tailwind)
3. Specify states needed
4. Include accessibility requirements
5. Ask for TypeScript

ITERATION:
- "Add loading state"
- "Make it responsive"
- "Add dark mode support"
- "Fix accessibility: add aria-labels"
```

### Maximizing Figma AI

```
EFFECTIVE USE:
1. Start with clear structure
2. Use for auto-layout suggestions
3. Generate color variations
4. Component recommendations
5. Design search for consistency

LIMITATIONS:
- Not great at complex interactions
- May miss brand nuances
- Accessibility needs verification
```

### Maximizing Claude for Copy

```
CONTEXT MATTERS:
- Describe the product
- Explain the user's emotional state
- Share brand voice guidelines
- Provide examples of good copy
- Specify constraints (length, tone)

ITERATION:
- "Make it more casual"
- "Add urgency without being pushy"
- "Create a variation that's more direct"
- "Now make it accessible-friendly"
```

---

## Performance Metrics

### Track AI Tool ROI

| Metric | Measure |
|--------|---------|
| Time saved | Hours per project |
| Quality impact | Revision rounds |
| Accessibility | Auto-detected issues |
| Consistency | Design system compliance |
| Cost | Tool subscriptions vs time saved |

### Quality Benchmarks

```
AI-GENERATED vs MANUAL:
- Same accessibility standards
- Same brand compliance
- Same code quality
- Faster iteration
- More variations explored
```

---

## Tool Selection Decision Tree

```
Need sitemap/IA first?
├── Yes → Relume (generates complete sitemap + wireframes)
└── No ↓

Need rapid wireframes/designs?
├── Yes → Figma AI or Google Stitch
└── No ↓

Need component code?
├── Yes → v0 (React/Tailwind/shadcn) or Cursor (any framework)
└── No ↓

Need design assets?
├── Yes ↓
│   └── Photos/illustrations → Midjourney/Firefly
│   └── Icons → Use icon library instead
└── No ↓

Need UI copy?
├── Yes → Claude
└── No ↓

Need code assistance?
└── Yes → Cursor/Copilot
```

---

## Related Resources

- [UI Generation Workflows](ui-generation-workflows.md) - Full design process
- [Design Systems](design-systems.md) - System architecture
- [Component Library Comparison](component-library-comparison.md) - shadcn, MUI, etc.
