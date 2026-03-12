# Implementation Research Workflow

**Before building any UI component, research how leaders in your space already solved it.**

This guide provides operational workflows for studying existing implementations to avoid reinventing the wheel.

**Last Updated**: January 2026
**Tools**: [Mobbin](https://mobbin.com/), [Page Flows](https://pageflows.com/), [Screenlane](https://screenlane.com/), [Refero](https://refero.design/)

---

## The Research-First Rule

**Before designing or implementing ANY of these UI elements, search existing implementations:**

| UI Element | Search Terms | Leader Apps to Study |
|------------|--------------|----------------------|
| Onboarding | "onboarding", "welcome", "first run" | Duolingo, Notion, Slack |
| Checkout | "checkout", "payment", "cart" | Stripe, Shopify, Amazon |
| Pricing table | "pricing", "plans", "subscription" | Linear, Figma, Notion |
| Settings | "settings", "preferences", "account" | iOS Settings, Slack, Discord |
| Search | "search", "filter", "results" | Airbnb, Amazon, Algolia |
| Dashboard | "dashboard", "analytics", "overview" | Stripe, Linear, Vercel |
| Forms | "signup", "registration", "input" | Typeform, Cal.com, Clerk |
| Empty states | "empty state", "zero state", "first use" | Notion, Linear, Figma |
| Notifications | "notifications", "alerts", "inbox" | Slack, Discord, GitHub |
| Profile | "profile", "user settings", "account" | X, LinkedIn, Spotify |
| Navigation | "sidebar", "nav", "menu" | Notion, Linear, Figma |
| Data tables | "table", "list", "grid" | Airtable, Notion, Linear |
| Modals | "modal", "dialog", "popup" | Stripe, Vercel, Linear |
| Cards | "card", "tile", "preview" | Pinterest, Dribbble, Mobbin |

---

## Step-by-Step Research Workflow

### Step 1: Define What You're Building

```
Before searching, answer:
- What specific component/flow am I building?
- What's the user goal? (e.g., "complete purchase", "find information")
- What's my vertical? (Fintech, SaaS, E-commerce, etc.)
```

### Step 2: Search Pattern Libraries

**Mobbin** (300k+ screenshots, best for mobile):
1. Go to [mobbin.com](https://mobbin.com/)
2. Search by component: "checkout", "onboarding", "pricing"
3. Filter by platform: iOS, Android, Web
4. Filter by app category: Finance, Productivity, E-commerce
5. Save screenshots to collection

**Page Flows** (video recordings of flows):
1. Go to [pageflows.com](https://pageflows.com/)
2. Browse by flow type: Onboarding, Checkout, Upgrade, etc.
3. Watch full video of how users progress through flows
4. Note transition animations, loading states, error handling

**Screenlane** (curated web screenshots):
1. Go to [screenlane.com](https://screenlane.com/)
2. Search by screen type: Dashboard, Pricing, Login
3. Good for SaaS and web applications

**Refero** (web design by industry):
1. Go to [refero.design](https://refero.design/)
2. Filter by industry vertical
3. Captures full-page screenshots with interactions

### Step 3: Study Leader Implementations

For each pattern, study **3-5 leader apps** in your space:

```markdown
## Implementation Study Template

### App: [Name]
**Category**: [Fintech/SaaS/E-commerce/etc.]
**Screen**: [Onboarding/Checkout/Settings/etc.]

#### What I See
- Layout: [Describe structure]
- Components used: [List UI elements]
- Interactions: [Describe animations, transitions]
- Visual hierarchy: [What draws attention first?]

#### How They Solved It
- User flow: [Steps user takes]
- Error handling: [How errors are shown]
- Loading states: [How loading is handled]
- Edge cases: [Empty states, long content, etc.]

#### Why It Works
- [Insight 1]
- [Insight 2]
- [Insight 3]

#### What I'll Adopt
- [ ] [Specific pattern to reuse]
- [ ] [Specific pattern to reuse]
- [ ] [Specific pattern to reuse]
```

### Step 4: Document Patterns

Create a comparison matrix for your specific component:

```markdown
| Pattern | Stripe | Wise | Revolut | My App |
|---------|--------|------|---------|--------|
| Steps to complete | 3 | 4 | 5 | ? |
| Guest checkout | Yes | No | No | ? |
| Express pay options | 4 | 2 | 3 | ? |
| Progress indicator | Stepper | Progress bar | None | ? |
| Error inline/toast | Inline | Inline | Toast | ? |
| Save for later | Yes | Yes | No | ? |
```

### Step 5: Implement with Learnings

Translate research into implementation decisions:

```tsx
// Before: I guessed at the implementation
function Checkout() {
  return <form>...</form>;
}

// After: Research-informed implementation
function Checkout() {
  // PASS From Stripe: 3-step flow, not single long form
  // PASS From Wise: Show fee breakdown inline, not at end
  // PASS From Revolut: Real-time validation, not submit-then-error
  return (
    <CheckoutFlow steps={3}>
      <ShippingStep />
      <PaymentStep showFees={true} />
      <ReviewStep />
    </CheckoutFlow>
  );
}
```

---

## Screen-by-Screen Research Guide

### Onboarding Flow Research

**Search terms**: "onboarding", "welcome", "get started", "first run", "tutorial"

**Study these leaders**:
| App | Why Study It |
|-----|--------------|
| Duolingo | Gamified onboarding, immediate value |
| Notion | Template-first, reduce empty state friction |
| Slack | Workspace setup + team invite flow |
| Figma | Interactive tutorial, learn-by-doing |
| Linear | Role-based personalization |

**Questions to answer**:
- How many steps to first value?
- Account creation: before or after showing value?
- How do they reduce abandonment?
- What personalization questions do they ask?
- How do they handle empty states post-onboarding?

### Checkout Flow Research

**Search terms**: "checkout", "payment", "cart", "order summary", "shipping"

**Study these leaders**:
| App | Why Study It |
|-----|--------------|
| Stripe Checkout | Industry standard, accessibility |
| Shopify | Optimized for conversion, Shop Pay |
| Amazon | 1-click, minimal friction |
| Apple | Clean, trust signals, Apple Pay |
| Airbnb | Date selection, pricing breakdown |

**Questions to answer**:
- How many pages/steps in checkout?
- Guest checkout: yes/no, how prominent?
- When do they show final price?
- How do they handle errors?
- What trust signals are present?

### Dashboard Research

**Search terms**: "dashboard", "home", "overview", "analytics", "stats"

**Study these leaders**:
| App | Why Study It |
|-----|--------------|
| Stripe Dashboard | Data density, filters, date ranges |
| Vercel | Build status, deployment flow |
| Linear | Focused views, keyboard shortcuts |
| Notion | Customizable, recent items |
| Mixpanel | Data visualization, drill-down |

**Questions to answer**:
- What data is shown first?
- How deep is the hierarchy?
- Sidebar vs top nav?
- How do they handle empty/loading states?
- What actions are available inline?

### Settings & Account Research

**Search terms**: "settings", "account", "preferences", "profile", "security"

**Study these leaders**:
| App | Why Study It |
|-----|--------------|
| iOS Settings | Grouping, deep hierarchy |
| Slack | Organized by category |
| GitHub | Security-first layout |
| Linear | Search within settings |
| Discord | Visual customization |

**Questions to answer**:
- How are settings grouped?
- Sidebar nav vs scrolling page?
- Search within settings?
- How are dangerous actions (delete) protected?
- How is security/privacy section organized?

### Pricing Page Research

**Search terms**: "pricing", "plans", "subscription", "upgrade", "billing"

**Study these leaders**:
| App | Why Study It |
|-----|--------------|
| Linear | Toggle annual/monthly, feature comparison |
| Notion | Per-seat pricing, clear CTAs |
| Figma | Usage-based elements explained |
| Vercel | Generous free tier highlighted |
| Stripe | API usage pricing clarity |

**Questions to answer**:
- How many tiers shown?
- Which tier is highlighted as "recommended"?
- How do they show annual savings?
- Feature comparison: table vs list?
- Free tier: how prominent?

---

## Quick Reference: Component Patterns

### Common UI Patterns by Component

**Buttons**:
- Primary: Single, high-contrast, clear verb
- Secondary: Lower contrast, supports primary
- Destructive: Red, requires confirmation

**Forms**:
- Labels: Above inputs (not floating labels for a11y)
- Validation: Real-time, inline errors
- Progress: Stepper for multi-step

**Navigation**:
- Primary: Left sidebar (desktop), bottom tab (mobile)
- Secondary: Top nav or nested sidebar
- Breadcrumbs: Deep hierarchies only

**Feedback**:
- Success: Green toast, auto-dismiss
- Error: Red inline near input, or toast for system errors
- Loading: Skeleton or spinner, progress for long ops

**Modals**:
- Size: Compact for confirms, full-screen for creation
- Close: X button + outside click + Escape key
- Focus: Trap focus, return focus on close

---

## Tools Quick Reference

| Tool | Best For | URL | Cost |
|------|----------|-----|------|
| **Mobbin** | Mobile patterns, 300k+ screens | mobbin.com | Free tier / $20+/mo |
| **Page Flows** | Full user flow videos | pageflows.com | Free tier / $19+/mo |
| **Screenlane** | Web SaaS patterns | screenlane.com | Free |
| **Refero** | Web design by industry | refero.design | Free tier / Paid |
| **ReallyGoodUX** | Annotated UX examples | reallygoodux.io | Free |
| **Land-book** | Landing page designs | land-book.com | Free |
| **One Page Love** | One-page sites | onepagelove.com | Free |
| **Awwwards** | Award-winning design | awwwards.com | Free |
| **Dribbble** | Visual design inspiration | dribbble.com | Free |

---

## Integration with Design Process

```
┌─────────────────────────────────────────────────────────┐
│ BEFORE DESIGNING ANY COMPONENT:                         │
│                                                         │
│ 1. Search Mobbin/Page Flows for component type          │
│ 2. Study 3-5 leader implementations                     │
│ 3. Document patterns in comparison matrix               │
│ 4. Decide which patterns to adopt                       │
│ 5. THEN start designing/implementing                    │
│                                                         │
│ This avoids reinventing solved problems                 │
└─────────────────────────────────────────────────────────┘
```

**Time Investment**:
- Quick research: 15-30 minutes
- Deep research: 1-2 hours
- ROI: Save hours of iteration by starting with proven patterns

---

## Related Resources

- [Domain-Specific UI Benchmarks](cro-framework.md#domain-specific-ui-benchmarks) — Industry leader tables
- [Modern UX Patterns 2025](modern-ux-patterns-2025.md) — Current interaction patterns
- [Design Systems](design-systems.md) — Foundations, tokens, governance
- [Component Library Comparison](component-library-comparison.md) — Component library selection
