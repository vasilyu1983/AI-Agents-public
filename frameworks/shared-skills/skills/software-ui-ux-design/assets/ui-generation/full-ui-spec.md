# UI Specification Template

Complete specification for a page/screen design handoff.

---

## Page Information

| Field | Value |
|-------|-------|
| **Page Name** | [e.g., Product Detail Page] |
| **URL/Route** | [e.g., /products/{id}] |
| **Platform** | [Web/iOS/Android] |
| **Version** | [e.g., 1.0] |
| **Last Updated** | [Date] |
| **Designer** | [Name] |

---

## Page Purpose

**Primary Goal**: [What is the main purpose of this page?]

**Surface Type**: [Landing page / Marketing surface / App shell / Dashboard / Detail page]

**Visual Thesis**: [What should the page feel like at first glance?]

**Content Plan**: [Hero / support / detail / proof / CTA, or equivalent utility sequence]

**Interaction Thesis**: [Which 2-3 motions or hierarchy moves create presence?]

**Success Metrics**:
- [Metric 1: e.g., Add to cart rate > 10%]
- [Metric 2: e.g., Time on page < 2 minutes]

**User Entry Points**:
- [ ] [Entry point 1: e.g., Search results]
- [ ] [Entry point 2: e.g., Category page]
- [ ] [Entry point 3: e.g., Direct link]

---

## Visual Direction And Constraints

### Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Design system | [Tokens/library/brand guide] | [Required constraints] |
| Visual references | [Screenshots/mood board/live product] | [What to match or avoid] |
| Real content source | [Marketing copy/product data] | [Do not use placeholder text] |

### Composition Rules

| Rule | Decision |
|------|----------|
| First viewport reads as one composition | [Yes/How] |
| Primary visual anchor | [Hero image/product visual/data focal point] |
| Copy mode | [Marketing / Utility / Mixed with rules] |
| Card usage | [Avoid / Allowed when card is the interaction] |
| Hero budget | [What must fit above the fold] |
| Fixed/floating UI constraints | [Header, FAB, badges, overlays] |

---

## Layout Structure

### Breakpoints

| Breakpoint | Min Width | Columns | Behavior |
|------------|-----------|---------|----------|
| Mobile | 0 | 4 | [Stack/scroll behavior] |
| Tablet | 768px | 8 | [Layout changes] |
| Desktop | 1024px | 12 | [Full layout] |
| Wide | 1440px | 12 | [Max width/centering] |

### Content Sections

```
┌─────────────────────────────────────────┐
│ HEADER (Component: GlobalHeader)        │
├─────────────────────────────────────────┤
│ HERO SECTION                            │
│ [Component: ProductGallery]             │
│ [Component: ProductInfo]                │
├─────────────────────────────────────────┤
│ DETAILS SECTION                         │
│ [Component: TabsContainer]              │
│   - Description                         │
│   - Specifications                      │
│   - Reviews                             │
├─────────────────────────────────────────┤
│ RELATED PRODUCTS                        │
│ [Component: ProductCarousel]            │
├─────────────────────────────────────────┤
│ FOOTER (Component: GlobalFooter)        │
└─────────────────────────────────────────┘
```

### Section Jobs

| Section | One job only | Primary proof or action |
|---------|--------------|-------------------------|
| Hero | [Identity/promise/primary task] | [CTA or proof] |
| Section 2 | [Single purpose] | [Support] |
| Section 3 | [Single purpose] | [Support] |

---

## Component Specifications

### Component: [Name]

**Purpose**: [What this component does]

**Variants**:
| Variant | Use Case |
|---------|----------|
| default | [Standard use] |
| compact | [Mobile/constrained] |
| expanded | [Detail view] |

**Props/Data**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| [prop1] | string | Yes | - | [Description] |
| [prop2] | number | No | 0 | [Description] |
| [prop3] | boolean | No | false | [Description] |

**States**:
| State | Visual Change | Trigger |
|-------|---------------|---------|
| Default | [Base appearance] | - |
| Hover | [Highlight/shadow] | Mouse hover |
| Focus | [Focus ring] | Keyboard focus |
| Active | [Pressed effect] | Click/tap |
| Loading | [Skeleton/spinner] | Data fetching |
| Disabled | [50% opacity] | isDisabled prop |
| Error | [Red border/text] | Validation failure |

**Responsive Behavior**:
| Breakpoint | Behavior |
|------------|----------|
| Mobile | [e.g., Stack vertically, hide secondary actions] |
| Tablet | [e.g., 2-column grid] |
| Desktop | [e.g., Full horizontal layout] |

**Accessibility**:
- Role: [e.g., button, link, region]
- ARIA: [Required aria attributes]
- Keyboard: [Tab order, shortcuts]
- Focus: [Focus management behavior]

**Code Example**:
```jsx
<ComponentName
  prop1="value"
  prop2={123}
  prop3={false}
  onAction={handleAction}
/>
```

---

## Interaction Specifications

### Interaction: [Name]

**Trigger**: [What initiates this interaction]

**Behavior**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Animation**:
| Property | Value | Duration | Easing |
|----------|-------|----------|--------|
| opacity | 0 → 1 | 200ms | ease-out |
| transform | translateY(10px) → 0 | 200ms | ease-out |

**Error Handling**:
| Error Case | Behavior |
|------------|----------|
| [Error 1] | [Response] |
| [Error 2] | [Response] |

---

## Content Requirements

### Static Content

| Element | Content | Character Limit | Notes |
|---------|---------|-----------------|-------|
| Page Title | [Title] | 60 chars | SEO title |
| H1 | [Heading] | 70 chars | - |
| CTA Button | [Label] | 25 chars | - |

### Copy Rules

| Surface | Rule | Example |
|---------|------|---------|
| Marketing | Promise-driven and concise | [Short supporting sentence] |
| App/Dashboard | Utility-first and operator-friendly | [Actionable heading or label] |
| Global | Do not explain the design in the UI copy | [Avoid meta commentary] |

### Dynamic Content

| Data Point | Source | Fallback |
|------------|--------|----------|
| [Field 1] | [API endpoint/field] | [Default value] |
| [Field 2] | [API endpoint/field] | [Default value] |

### Images

| Image | Dimensions | Format | Alt Text Pattern |
|-------|------------|--------|------------------|
| Hero | 1200×600 | WebP + fallback | [Description pattern] |
| Thumbnail | 300×300 | WebP + fallback | [Description pattern] |

### Visual Anchor Checklist

- [ ] The primary image or visual explains context, product, or atmosphere
- [ ] Decorative gradients are not standing in for a missing visual idea
- [ ] Overlays, stickers, or floating badges do not compete with the primary CTA
- [ ] If the image were removed, the section would materially weaken

---

## State Handling

### Empty State

**When**: [Condition for empty state]

**Display**:
- Illustration: [Yes/No, description]
- Heading: [Copy]
- Description: [Copy]
- CTA: [Label] → [Action]

### Loading State

**When**: [Initial load, data refresh, etc.]

**Display**:
- Type: [Skeleton/Spinner/Progress]
- Duration threshold: [When to show]
- Transition: [How it appears/disappears]

### Error State

**When**: [API failure, validation error, etc.]

| Error Type | Title | Message | Action |
|------------|-------|---------|--------|
| Network | [Title] | [Message] | [Retry/Contact] |
| Validation | [Title] | [Message] | [Fix guidance] |
| Permission | [Title] | [Message] | [Login/Request] |

### Degraded State

**When**: [Partial data, feature unavailable, stale data, limited capability]

| Degradation | User message | Recovery |
|-------------|--------------|----------|
| [Case 1] | [Warning copy] | [Retry/Fallback] |
| [Case 2] | [Warning copy] | [Fallback path] |

---

## Accessibility Checklist

### WCAG 2.2 AA Compliance

**Perceivable**:
- [ ] Color contrast ≥ 4.5:1 (text), ≥ 3:1 (large text)
- [ ] Text resizable to 200%
- [ ] Non-text content has alt text
- [ ] No information conveyed by color alone

**Operable**:
- [ ] All interactive elements keyboard accessible
- [ ] Focus visible and logical order
- [ ] No keyboard traps
- [ ] Skip links available
- [ ] Touch targets ≥ 24×24px (44×44px recommended)

**Understandable**:
- [ ] Labels describe purpose
- [ ] Error messages specific and helpful
- [ ] Consistent navigation
- [ ] Language specified

**Robust**:
- [ ] Valid HTML
- [ ] ARIA used correctly
- [ ] Compatible with assistive technology

### Screen Reader Notes

| Element | Announcement | Notes |
|---------|--------------|-------|
| [Element 1] | [What is announced] | [Special handling] |
| [Element 2] | [What is announced] | [Special handling] |

---

## Design Tokens Used

### Colors
| Token | Value | Usage |
|-------|-------|-------|
| --color-primary | #2196F3 | CTAs, links |
| --color-text-primary | #1A1A1A | Body text |
| --color-background | #FFFFFF | Page background |

### Typography
| Token | Value | Usage |
|-------|-------|-------|
| --font-size-h1 | 2.25rem | Page heading |
| --font-size-body | 1rem | Body text |
| --font-weight-bold | 700 | Headings, emphasis |

### Spacing
| Token | Value | Usage |
|-------|-------|-------|
| --space-4 | 1rem | Standard padding |
| --space-8 | 2rem | Section spacing |

---

## Assets Required

### Icons
| Icon | Source | Size | Notes |
|------|--------|------|-------|
| [Icon name] | [Lucide/custom] | 24px | [Usage] |

### Images
| Asset | Location | Formats |
|-------|----------|---------|
| [Asset name] | /assets/images/ | WebP, PNG fallback |

---

## Developer Notes

### Dependencies
- [Component library: e.g., shadcn/ui]
- [Animation library: e.g., Framer Motion]
- [Form library: e.g., React Hook Form]

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| [/api/...] | GET | [Data fetch] |
| [/api/...] | POST | [Action] |

### Performance Requirements
| Metric | Target |
|--------|--------|
| LCP | < 2.5s |
| INP | < 200ms |
| CLS | < 0.1 |

### Verification Plan

| Check | Method | Viewports / States |
|-------|--------|--------------------|
| Composition check | [Browser review / screenshot diff / live QA] | [Mobile, desktop] |
| Content realism | [Real data / approved copy review] | [Hero, key states] |
| Accessibility review | [Keyboard / screen reader / contrast] | [Primary flow] |
| Motion review | [Reduced motion + default] | [Hero, transitions] |

### Known Issues/Constraints
- [Issue 1]
- [Issue 2]

---

## Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Designer | [Name] | [Date] | [x] Approved |
| Developer | [Name] | [Date] | [ ] Pending |
| Product | [Name] | [Date] | [ ] Pending |
