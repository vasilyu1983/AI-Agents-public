# Deck Narrative and Visual Patterns

Judgment for deciding what a deck says and how each slide looks, before any python-pptx or pptxgenjs work. The API side lives in [pptx-layouts.md](pptx-layouts.md), [pptx-charts.md](pptx-charts.md) and [pptx-template-branding.md](pptx-template-branding.md); the per-slide planning table lives in [../assets/slide-narrative-template.md](../assets/slide-narrative-template.md). Structures and heuristics are adapted in part from the slide and corporate-identity data in [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT, © 2024 Next Level Builder).

---

## Deck Structure by Purpose

Pick the structure from the decision the audience must make, then cut every slide that does not serve it.

| Purpose | Typical length | Spine |
|---------|----------------|-------|
| Seed investor pitch | 10-12 | Title → Problem → Solution → Traction → Market → Product → Business model → Team → Financials → Ask |
| Kawasaki 10/20/30 pitch | 10 | Title → Problem → Value proposition → Underlying magic → Business model → Go-to-market → Competition → Team → Projections → Status and ask (10 slides, 20 minutes, 30 pt minimum text) |
| Growth-round pitch | 12-15 | Seed spine plus mission, product demo, go-to-market and use of funds |
| Product demo | 5-8 | Hook/problem → Solution overview → Demo or screenshots → Key features → Benefits → Pricing → CTA |
| Sales pitch | 7-10 | Their problem → Cost of inaction → Solution → Proof → Differentiators → Pricing/ROI → Objections → Next steps |
| Quarterly business review | 10-15 | Executive summary → Goals vs results → Key metrics → Wins → Challenges → Learnings → Next-quarter goals → Resource needs |
| All-hands | 8-12 | Wins → Metrics → Team spotlights → Product updates → Customer stories → Challenges → Roadmap → Q&A |
| Conference talk | 15-25 | Hook story → Credibility → Big idea → 3 points with evidence → Synthesis → Call to action |
| Workshop | 20-40 | Objectives → Agenda → (Concept → Exercise) × n → Synthesis → Resources |
| Case study | 8-12 | Customer → Challenge → Why they chose us → Implementation → Results → Quote → Lessons → Applicability |
| Competitive analysis | 6-10 | Landscape → Competitor overview → Feature matrix → Pricing → Strengths/weaknesses → Our position → Recommendations |
| Board meeting | 15-20 | Agenda → Executive summary → Financials → Key metrics → Functional updates → Risks → Strategic initiatives → Decisions needed |
| Webinar | 20-30 | Housekeeping → Presenter → Agenda → Problem → Teaching content → Case study → Product → Offer → Q&A |

Pitch-deck ordering details are in [../assets/pitch-deck.md](../assets/pitch-deck.md); QBR status colours are in [../assets/quarterly-review.md](../assets/quarterly-review.md).

## Persuasion Arcs

- **Sparkline (Nancy Duarte, *Resonate*)**: alternate "what is" with "what could be", building tension and release, and end on the new state the audience will reach. Use it for vision, change and fundraising talks.
- **Problem → Agitate → Solution**: the most direct arc for sales and problem slides; keep the agitation factual, not fear-mongering.
- **Before → After → Bridge**: transformation and case-study decks.
- **Feature → Advantage → Benefit**: per-feature slides; end on what the audience gains, not on the feature name.
- **Stat → Source → Implication**: every proof slide. A number without a named source and a "so what" is decoration.

Do not use false scarcity or invented urgency on a slide; if a deadline or limit is real, state it with its source.

## Slide Goal → Layout Pattern

| Slide goal | Layout pattern | Visual weight |
|------------|----------------|---------------|
| Hook / vision | Split hero or full-bleed image, text on one side | Visual-dominant |
| Problem | Card grid of 3-4 pains | Balanced |
| Single shock statistic | Full-bleed number, one line of context | Text-dominant |
| Solution / demo | Split: product visual one side, 3 benefits the other | 50/50 or visual-led |
| Proof / traction | Metric grid, or one chart with an annotated insight | Numbers-dominant |
| Testimonial | Large quote, name, role, photo | Text-dominant |
| Comparison | Side-by-side columns or a comparison table | Balanced |
| Pricing | Tier cards with one highlighted | Balanced |
| Team | Photo grid with role and one credential each | Balanced |
| Timeline / roadmap | Horizontal flow with 5-8 milestones | Balanced |
| CTA / ask | Centred single ask, one supporting line | Text-dominant |

Break the pattern (full-bleed, colour inversion) at most on the two or three slides that carry the emotional peaks; if every slide is a "moment", none is.

## Type Scale on a Slide

For a 1920 × 1080 HTML or image slide, a working ratio is: hero statement ~120 px over ~32 px support; metric callout ~96 px over ~18 px label; section title ~80 px; body-focused slide ~24 px body with 1.5-1.6 line height; quotes ~32-36 px, looser leading. Large display text wants tight leading (1.0-1.1); body text wants 1.4-1.6. For native PowerPoint text, the point hierarchy in [pptx-template-branding.md](pptx-template-branding.md) applies. Check projected readability from the back of the room, not on a laptop.

## Charts on Slides

- One chart per slide, with the insight written as the slide title ("Churn halved after onboarding change"), not the chart name.
- Pie or donut only for 2-5 parts of a whole that sum to 100%; beyond about six slices use a sorted bar.
- Line for trends over time; vertical bar for 3-12 categories; horizontal bar for long labels; funnel for sequential drop-off; waterfall for a bridge between two totals; KPI card for one number with its trend and comparison period.
- Annotate the point that matters (callout, highlight colour) and grey out the rest.
- Every chart needs a text equivalent for accessibility: see [pptx-accessibility-compliance.md](pptx-accessibility-compliance.md).
- Verify every rendered figure against the source data (see the release gate in [../SKILL.md](../SKILL.md)).

## Backgrounds and Text Contrast

Use a photo background only where the slide goal is emotional (hook, vision, team, CTA). Put text over a gradient, darkening or blur overlay so it keeps readable contrast across the whole image, and place text where the image is quietest. Data slides get plain backgrounds. Check stock-image licences before reuse, and disclose AI-generated imagery where the audience would assume it is real.
