---
name: marketing-visual-design
description: Visual marketing asset creation for ads, social media, email, presentations, and brand collateral. Platform-specific dimensions, creative best practices, AI design tools, and conversion-focused visual hierarchy.
---

# MARKETING VISUAL DESIGN — CREATIVE OS (OPERATIONAL)

Built as a **no-fluff execution skill** for marketing visual asset creation.

**Scope**: Ad creatives, social media graphics, email visuals, presentation design, brand collateral. NOT product UI (use `software-ui-ux-design` for apps/dashboards).

**Structure**: Platform specs and dimensions first. Creative best practices second. AI tools in clearly labeled sections.

---

## Modern Best Practices (January 2026)

- **Meta Ads Manager**: https://www.facebook.com/business/ads-guide
- **Google Ads Creative Guidelines**: https://support.google.com/google-ads/answer/1722096
- **LinkedIn Campaign Manager**: https://business.linkedin.com/marketing-solutions/ads/ad-specifications
- **TikTok Ads Manager**: https://ads.tiktok.com/help/article/ad-specs
- **TikTok Safe Zones 2026**: https://zeely.ai/blog/tiktok-safe-zones/
- **Canva Design School**: https://www.canva.com/designschool/
- **Figma for Marketing**: https://www.figma.com/templates/marketing/
- **Adobe Creative Trends 2026**: https://blog.adobe.com/en/publish/2025/12/09/four-creative-trends-define-marketing-2026

---

## 2026 Creative Trends

### Key Trends Shaping Marketing Visuals

| Trend | Description | Application | Source |
|-------|-------------|-------------|--------|
| **Sensory/Tactile Design** | Real textures, depth, analog feel—audiences want content they can "touch" | Hero images, product shots, backgrounds | [Adobe Blog](https://blog.adobe.com/en/publish/2025/12/09/four-creative-trends-define-marketing-2026) |
| **"Unhinged" Playful Creativity** | Absurdist humor, chronically online culture, niche obsessions | Gen Z/Alpha campaigns, TikTok, memes | [Superside](https://www.superside.com/blog/advertising-creative-trends) |
| **UGC-Style Content** | Lo-fi, authentic, phone-shot visuals outperform polished studio work | Social ads, TikTok, testimonials | [Billo](https://billo.app/blog/meta-ads-best-practices/) |
| **Adaptive Visual Systems** | Fluid logos and variable color themes that shift across contexts | Multi-platform brands, responsive design | [The Branding Journal](https://www.thebrandingjournal.com/2026/01/top-branding-design-trends-2026/) |
| **Bold Typography & Color** | Vibrant gradients, neon accents, contrasting color blocks | Scroll-stopping social posts | [Versa Creative](https://versacreative.com/blog/top-15-social-media-design-trends-for-2025/) |

### UGC-Style Performance Data

- **6 in 10 marketers** report UGC-style content leads to higher conversion rates than branded content
- **Lo-fi phone-shot videos** consistently outperform glossy studio ads on TikTok
- **Authentic visuals** (real textures, real people) set brands apart from stock photo competitors

### Meta Algorithm Update (2026)

The algorithm now uses **creative as the primary targeting signal**. Key implications:

| Issue | Impact | Solution |
|-------|--------|----------|
| **Repetitive visuals** | Higher CPMs, ad fatigue | Vary formats, angles, lengths |
| **Same image with text variants** | System sees as "same image" | Change the base creative, not just text |
| **Lack of diversity** | Algorithm punishes account | Maintain diverse creative library |

**Best practice**: Test 3-5 different creative angles per campaign, not just text variations

---

## When to Use This Skill

Invoke when users ask for:

- **Ad creatives**: Meta (Facebook/Instagram), Google Display, YouTube thumbnails, LinkedIn, TikTok
- **Social media graphics**: Feed posts, Stories, Reels covers, carousels, LinkedIn banners
- **Email marketing visuals**: Header images, promotional banners, newsletter graphics
- **Presentation design**: Investor decks, sales decks, webinar slides, pitch decks
- **Brand collateral**: One-pagers, leave-behinds, case study PDFs, brochures
- **Landing page heroes**: Visual design (not CRO strategy—use `marketing-cro` for that)
- **Event/campaign graphics**: Launch banners, seasonal promotions, event invites
- **AI-generated marketing visuals**: Midjourney, DALL-E, Adobe Firefly, Canva AI

**Do NOT use for**:
- Product UI design → use `software-ui-ux-design`
- A/B testing strategy → use `marketing-cro`
- Brand positioning/messaging → use `marketing-content-strategy`
- Social media strategy → use `marketing-social-media`

---

## Decision Tree: What Visual Asset?

```text
MARKETING VISUAL REQUEST
    │
    ├─> "Ad creative" ──────────────> AD CREATIVES
    │                                  → references/ad-creative-specs.md
    │
    ├─> "Social media graphic" ─────> SOCIAL GRAPHICS
    │                                  → references/social-media-dimensions.md
    │
    ├─> "Email banner/header" ──────> EMAIL VISUALS
    │                                  → references/email-visual-specs.md
    │
    ├─> "Presentation/deck" ────────> PRESENTATION DESIGN
    │                                  → references/presentation-design.md
    │
    ├─> "One-pager/collateral" ─────> BRAND COLLATERAL
    │                                  → references/brand-collateral.md
    │
    ├─> "Landing page hero" ────────> HERO DESIGN
    │                                  → See AI Tools: references/ai-design-tools.md
    │                                  → For CRO strategy: ../marketing-cro/SKILL.md
    │
    └─> "AI-generated visual" ──────> AI TOOLS
                                       → references/ai-design-tools.md
```

---

## Core: Platform Dimensions Quick Reference

### Social Media (Static)

| Platform | Post | Story/Reel | Profile | Cover/Banner |
|----------|------|------------|---------|--------------|
| **Instagram** | 1080×1080 (1:1), 1080×1350 (4:5) | 1080×1920 (9:16) | 320×320 | N/A |
| **Facebook** | 1200×630, 1080×1080 | 1080×1920 | 170×170 | 820×312 |
| **LinkedIn** | 1200×1200, 1200×628 | N/A | 400×400 | 1584×396 |
| **TikTok** | 1080×1080 | 1080×1920 | 200×200 | N/A |
| **X (Twitter)** | 1600×900, 1080×1080 | N/A | 400×400 | 1500×500 |
| **YouTube** | N/A | 1080×1920 (Shorts) | 800×800 | 2560×1440 |
| **Pinterest** | 1000×1500 (2:3) | 1080×1920 | 165×165 | N/A |

### Ad Platforms

| Platform | Recommended Sizes | Safe Zone | Max File Size |
|----------|-------------------|-----------|---------------|
| **Meta (FB/IG)** | 1080×1080, 1080×1350 (4:5 best), 1080×1920 | 14% from edges (text overlay) | 30MB image, 4GB video |

**2026 Performance Note**: 4:5 vertical (1080×1350) performs **15% better CTR** in feeds than square. 1:1 now works across 80% of placements.
| **Google Display** | 300×250, 336×280, 728×90, 160×600, 300×600 | N/A | 150KB |
| **Google Responsive** | 1200×628 (landscape), 1200×1200 (square), 628×1200 (portrait) | N/A | 5MB |
| **YouTube Thumbnail** | 1280×720 (16:9) | Right-bottom (timestamp) | 2MB |
| **LinkedIn Ads** | 1200×628 (single), 1080×1080 (carousel) | N/A | 5MB |
| **TikTok Ads** | 1080×1920 (9:16) | Top 130px, bottom 440px (Shop: 25-30%) | 500MB video |

### Video Specifications

| Platform | Aspect Ratio | Duration | Resolution |
|----------|--------------|----------|------------|
| **Instagram Reels** | 9:16 | 15-90s | 1080×1920 |
| **TikTok** | 9:16 | 15s-10min | 1080×1920 |
| **YouTube Shorts** | 9:16 | ≤60s | 1080×1920 |
| **Meta Stories** | 9:16 | ≤15s (ads), 60s (organic) | 1080×1920 |
| **LinkedIn Video** | 1:1, 16:9, 9:16 | 3s-10min | 1080p max |

---

## Core: Visual Hierarchy for Marketing

### Attention Flow (F-Pattern & Z-Pattern)

```text
F-PATTERN (content-heavy pages):
┌────────────────────────┐
│ ███████████████████    │  ← Top horizontal scan
│ ██████████             │  ← Second horizontal (shorter)
│ █                      │
│ █                      │  ← Vertical scan down left
│ █                      │
└────────────────────────┘

Z-PATTERN (landing pages, ads):
┌────────────────────────┐
│ 1 ─────────────────► 2 │  ← Logo to CTA
│     ╲                  │
│       ╲                │  ← Diagonal scan
│         ╲              │
│ 3 ─────────────────► 4 │  ← Supporting content to CTA
└────────────────────────┘
```

### Ad Creative Hierarchy

| Element | Priority | Placement | Purpose |
|---------|----------|-----------|---------|
| **Hook/Headline** | 1 | Top 1/3 | Stop the scroll |
| **Hero Visual** | 2 | Center | Communicate value |
| **Value Prop** | 3 | Middle | Why care? |
| **CTA** | 4 | Bottom 1/3 | What to do |
| **Logo** | 5 | Corner (consistent) | Brand attribution |

### Text Overlay Rules

| Platform | Max Text Coverage | Safe Zone |
|----------|-------------------|-----------|
| **Meta Ads** | <20% recommended (not enforced but affects delivery) | 14% from edges |
| **Google Display** | <25% | Varies by placement |
| **LinkedIn** | No strict limit | Keep headlines <2 lines |
| **TikTok** | Minimal—native feel | Top 130px, bottom 440px (Shop ads: 25-30% bottom No Fly Zone) |

---

## Core: Color Psychology for Marketing

### Conversion-Focused Color Use

| Color | Association | Best For | Avoid For |
|-------|-------------|----------|-----------|
| **Blue** | Trust, security, calm | Finance, B2B, tech | Food, urgency |
| **Green** | Growth, health, money | Finance, eco, health | Luxury |
| **Red** | Urgency, excitement, passion | Sales, food, entertainment | Healthcare |
| **Orange** | Energy, confidence, warmth | CTAs, retail, youth | Luxury, corporate |
| **Yellow** | Optimism, attention, caution | Highlights, warnings | Primary (hard to read) |
| **Purple** | Luxury, creativity, wisdom | Beauty, premium, education | Budget brands |
| **Black** | Sophistication, luxury, power | Luxury, fashion, tech | Children's products |
| **White** | Clean, minimal, modern | Tech, healthcare, minimalist | Can feel empty |

### CTA Button Colors (Conversion Research)

| Color | Effect | Best Use Case |
|-------|--------|---------------|
| **Orange** | High visibility, action-oriented | Primary CTAs, "Buy Now" |
| **Green** | Positive association, "go" signal | "Get Started", "Download" |
| **Blue** | Trustworthy, professional | "Learn More", B2B |
| **Red** | Urgency, limited time | "Limited Offer", "Sale" |
| **Contrast** | Whatever contrasts most with page | Universal rule |

---

## Core: Typography for Marketing

### Font Pairing Principles

| Combination | Example | Best For |
|-------------|---------|----------|
| **Serif + Sans-Serif** | Playfair Display + Inter | Luxury, editorial |
| **Sans + Sans** | Montserrat + Open Sans | Modern, tech, SaaS |
| **Display + Body** | Bebas Neue + Roboto | Bold headlines, clean body |
| **Mono + Sans** | JetBrains Mono + Inter | Developer, tech products |

### Readability Rules

| Element | Size (Desktop) | Size (Mobile) | Line Height |
|---------|----------------|---------------|-------------|
| **Headline** | 32-48px | 24-32px | 1.1-1.2 |
| **Subheadline** | 20-28px | 18-24px | 1.2-1.3 |
| **Body** | 16-18px | 14-16px | 1.5-1.6 |
| **CTA Button** | 16-20px | 14-18px | 1.0 |
| **Caption** | 12-14px | 11-13px | 1.4 |

### Ad Copy Character Limits

| Platform | Headline | Description | CTA |
|----------|----------|-------------|-----|
| **Meta** | 40 chars (recommended) | 125 chars (primary text) | 25 chars |
| **Google Search** | 30 chars × 3 | 90 chars × 2 | N/A |
| **Google Display** | 30 chars (short), 90 chars (long) | 90 chars | 15 chars |
| **LinkedIn** | 70 chars (introductory) | 150 chars | N/A |
| **TikTok** | 100 chars | 100 chars (ad name) | N/A |

---

## Core: Ad Creative Formats

### Static Ad Checklist

- [ ] Clear focal point (one hero element)
- [ ] Readable text at thumbnail size
- [ ] Brand colors/logo present
- [ ] CTA visible and action-oriented
- [ ] Text within safe zones
- [ ] High contrast between text and background
- [ ] Mobile-first design (most impressions are mobile)

### Carousel Ad Structure

```text
SLIDE 1: Hook (problem or bold statement)
SLIDE 2-4: Solution/Benefits (one per slide)
SLIDE 5: Social proof or testimonial
SLIDE 6: CTA with offer

Design consistency:
- Same template/layout across slides
- Consistent brand colors
- Arrow or visual cue to swipe
- Each slide stands alone AND connects
```

### Video Ad Structure (Hook-Retain-Convert)

| Section | Duration | Purpose | Visual |
|---------|----------|---------|--------|
| **Hook** | 0-3s | Stop scroll, state problem | Bold text, movement, face |
| **Agitate** | 3-10s | Amplify pain point | Problem visualization |
| **Solution** | 10-20s | Introduce product/service | Product demo, benefits |
| **Proof** | 20-30s | Build credibility | Testimonials, stats |
| **CTA** | 30-45s | Tell them what to do | Clear action, urgency |

### Video Captions (2026 Best Practice)

- **Large black-on-white subtitles** boost retention for silent playback (80%+ of social video is watched muted)
- **"Pop-in" product PNGs** during hook moments increase brand recall by ~10%
- Over **93% of top-performing TikTok videos** use audio
- **Sound is key** for 88% of TikTok users—but captions are mandatory for accessibility

---

## Core: Social Media Content Types

### Content Format Matrix

| Format | Best For | Engagement Level | Production Effort |
|--------|----------|------------------|-------------------|
| **Static Image** | Quotes, announcements, products | Medium | Low |
| **Carousel** | Education, storytelling, comparisons | High | Medium |
| **Reels/Shorts** | Reach, trends, tutorials | Very High | Medium-High |
| **Stories** | Behind-scenes, polls, urgency | Medium | Low |
| **Live** | Q&A, launches, authenticity | High | Low |
| **Infographic** | Data, processes, comparisons | High | High |

### Carousel Best Practices

- **Slide 1**: Hook (question, bold statement, problem)
- **Slide 2-8**: Content (one idea per slide)
- **Final Slide**: CTA (save, share, follow, link in bio)
- **Visual**: Consistent template, swipe indicator
- **Text**: Max 3-4 lines per slide

### Reel/Short-Form Video Hooks

| Hook Type | Example | When to Use |
|-----------|---------|-------------|
| **Question** | "Why do 90% of ads fail?" | Educational content |
| **Bold Statement** | "This changed everything" | Transformation stories |
| **Pattern Interrupt** | [unexpected visual/sound] | Entertainment, virality |
| **POV** | "POV: You just discovered..." | Relatable content |
| **Tutorial Start** | "Here's how to..." | How-to content |
| **Controversy** | "Unpopular opinion:..." | Engagement bait |

---

## Core: Email Visual Design

### Email Layout Structure

```text
┌─────────────────────────────────┐
│         HEADER/LOGO             │  ← Brand recognition (max 600px wide)
├─────────────────────────────────┤
│                                 │
│         HERO IMAGE              │  ← 600×300px typical
│                                 │
├─────────────────────────────────┤
│         HEADLINE                │  ← 22-28px, bold
│         Subheadline             │  ← 16-18px
├─────────────────────────────────┤
│         BODY COPY               │  ← 14-16px, left-aligned
│                                 │
│        [ CTA BUTTON ]           │  ← 44px+ height, contrast color
│                                 │
├─────────────────────────────────┤
│     SECONDARY CONTENT           │  ← Optional: products, links
├─────────────────────────────────┤
│         FOOTER                  │  ← Unsubscribe, address, socials
└─────────────────────────────────┘
```

### Email Design Specs

| Element | Specification | Notes |
|---------|---------------|-------|
| **Width** | 600px (max 640px) | Mobile-responsive |
| **Hero Image** | 600×300px typical | Include alt text |
| **CTA Button** | 44px+ height, 200px+ width | Finger-tap friendly |
| **Font Size** | 14-16px body, 22-28px headlines | Mobile readability |
| **Image Weight** | <1MB total, <200KB each | Load speed |
| **Alt Text** | Required for all images | Accessibility + image blocking |

### Dark Mode Considerations

- Use transparent PNGs for logos (or provide dark mode version)
- Avoid pure black (#000000)—use dark gray (#1a1a1a)
- Test with Gmail, Apple Mail, Outlook dark modes
- Add white/light borders around dark images

---

## Core: Presentation Design

### Slide Structure (Investor/Sales Deck)

| Slide # | Purpose | Visual Approach |
|---------|---------|-----------------|
| 1 | Title + Hook | Bold statement, minimal |
| 2 | Problem | Pain visualization, stats |
| 3 | Solution | Product/service hero |
| 4 | How It Works | 3-step process, icons |
| 5 | Traction/Proof | Metrics, logos, testimonials |
| 6 | Market Size | TAM/SAM/SOM, charts |
| 7 | Business Model | Revenue streams, pricing |
| 8 | Team | Photos, credentials |
| 9 | Ask/CTA | Clear next step |

### Slide Design Rules

| Rule | Do | Don't |
|------|----|----|
| **Text** | Max 6 lines, 6 words per line | Walls of text |
| **Images** | High-quality, relevant | Stock clichés (handshakes) |
| **Charts** | Highlight one insight | Complex multi-axis charts |
| **Bullets** | Max 5 per slide | Sub-bullets of sub-bullets |
| **Fonts** | 2 max (heading + body) | Multiple decorative fonts |
| **Colors** | 3-4 brand colors | Rainbow slides |
| **Animation** | Subtle, purposeful | Spinning/flying elements |

### Presentation Dimensions

| Platform | Aspect Ratio | Resolution |
|----------|--------------|------------|
| **Standard (4:3)** | 4:3 | 1024×768 |
| **Widescreen (16:9)** | 16:9 | 1920×1080 |
| **Google Slides** | 16:9 default | 1920×1080 |
| **Figma Export** | Custom | 1920×1080 recommended |

---

## AI Design Tools (2026)

### Tool Comparison

| Tool | Best For | Limitations | Pricing |
|------|----------|-------------|---------|
| **Midjourney** | Hero images, illustrations, backgrounds | No text rendering | $10-60/mo |
| **DALL-E 3** | Quick concepts, ChatGPT integration | Lower quality than MJ | Pay-per-use |
| **Adobe Firefly** | Photoshop integration, commercial safety | Less creative range | Creative Cloud |
| **Canva AI** | Social graphics, quick edits | Template-bound | Free-$15/mo |
| **Ideogram** | Text-in-image rendering | Newer, less refined | Free tier |
| **Leonardo.ai** | Consistent character/style | Learning curve | Free-$24/mo |

### Midjourney Prompting for Marketing

```text
STRUCTURE:
[subject], [style], [composition], [lighting], [mood], [technical params]

EXAMPLES:

Hero image for SaaS landing page:
"modern tech workspace, minimalist illustration style, isometric view,
soft ambient lighting, professional and trustworthy mood, --ar 16:9 --v 6"

Social media product shot:
"premium skincare bottle on marble surface, product photography,
centered composition, soft studio lighting, luxury aesthetic, --ar 1:1 --v 6"

Abstract background for ads:
"flowing gradient mesh, blue and purple tones, abstract digital art,
smooth curves, modern tech feel, --ar 9:16 --v 6 --style raw"
```

### AI Workflow for Marketing Assets

```text
1. BRIEF → Define asset type, dimensions, brand guidelines
2. GENERATE → Create base images with AI (Midjourney/DALL-E)
3. REFINE → Edit in Figma/Canva (add text, adjust, composite)
4. BRAND → Apply brand colors, fonts, logo
5. OPTIMIZE → Export for platform (correct dimensions, file size)
6. VARIANT → Create size variations for different placements
```

---

## Quick Reference: Export Checklist

### Before Exporting Any Asset

- [ ] Correct dimensions for target platform
- [ ] Text within safe zones
- [ ] Brand colors accurate (check hex codes)
- [ ] Logo present and positioned consistently
- [ ] CTA clear and readable
- [ ] Mobile preview checked (most views are mobile)
- [ ] File size within platform limits
- [ ] Alt text/accessibility considered
- [ ] A/B variant created (if testing)

### File Format Guide

| Use Case | Format | Why |
|----------|--------|-----|
| **Photos/complex images** | JPEG | Smaller file size |
| **Graphics with transparency** | PNG | Preserves transparency |
| **Logos/icons** | SVG | Scalable, tiny file |
| **Animated graphics** | GIF/WebP | Animation support |
| **Print collateral** | PDF | Vector, CMYK support |
| **Video** | MP4 (H.264) | Universal compatibility |

---

## Navigation

### References (Detailed Guides)

- [references/ad-creative-specs.md](references/ad-creative-specs.md) — Full ad specs for Meta, Google, LinkedIn, TikTok
- [references/social-media-dimensions.md](references/social-media-dimensions.md) — Complete platform dimension guide
- [references/presentation-design.md](references/presentation-design.md) — Investor deck and sales deck design
- [references/email-visual-specs.md](references/email-visual-specs.md) — Email design specifications
- [references/ai-design-tools.md](references/ai-design-tools.md) — AI tool prompting and workflows
- [references/brand-collateral.md](references/brand-collateral.md) — One-pagers, case studies, brochures

### Assets (Templates)

- [assets/ad-creative-brief.md](assets/ad-creative-brief.md) — Creative brief template
- [assets/social-carousel-template.md](assets/social-carousel-template.md) — Carousel structure template
- [assets/pitch-deck-outline.md](assets/pitch-deck-outline.md) — Investor deck slide outline

### Related Skills

- [marketing-cro](../marketing-cro/SKILL.md) — Landing page optimization, A/B testing
- [marketing-content-strategy](../marketing-content-strategy/SKILL.md) — Positioning, messaging, brand
- [marketing-social-media](../marketing-social-media/SKILL.md) — Social media strategy
- [marketing-paid-advertising](../marketing-paid-advertising/SKILL.md) — Ad campaign strategy
- [software-ui-ux-design](../software-ui-ux-design/SKILL.md) — Product interface design (NOT marketing)

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Instead |
|--------------|--------------|---------|
| **Text-heavy ads** | Low engagement, hard to read | One message per visual |
| **Stock photo clichés** | Ignored by audience | Custom or AI-generated |
| **Inconsistent branding** | Weak recognition | Template system |
| **Ignoring safe zones** | Text cut off | Check platform specs |
| **Desktop-first design** | Most views are mobile | Design mobile-first |
| **Complex charts in ads** | Too much cognitive load | One insight, simple visual |
| **Generic CTAs** | Low click-through | Specific, benefit-driven |

---

## Usage Notes (Claude)

- Always ask for target platform before designing (dimensions vary significantly)
- Provide dimensions and safe zones for every recommendation
- Recommend AI tools when appropriate for hero images or backgrounds
- Link to `marketing-cro` for conversion optimization strategy
- Link to `software-ui-ux-design` if the request is product UI, not marketing
- Stay operational: provide specs, checklists, templates—not theory
