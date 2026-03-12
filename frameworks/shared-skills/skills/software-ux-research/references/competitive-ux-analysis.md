# Competitive UX Analysis

Systematic methodology for benchmarking UX against competitors and top companies, with case studies from industry leaders.

---

## Competitor Selection Framework

### Competitor Types

| Type | Definition | Why Analyze |
|------|------------|-------------|
| **Direct** | Same product, same market | Feature parity, differentiation |
| **Indirect** | Different product, same need | Alternative solutions, JTBD |
| **Aspirational** | Best-in-class, any industry | UX patterns, inspiration |
| **Emerging** | New entrants, startups | Disruption signals, innovation |

### Selection Matrix

```text
COMPETITOR SELECTION GUIDE

Must Include (2-3):
├── Top direct competitor
├── Fastest-growing competitor
└── Current user's alternative

Should Include (1-2):
├── Aspirational best-in-class
└── Adjacent market leader

Consider (1):
└── Disruptive newcomer

Total: 4-6 competitors maximum
```

### Competitor Research Sources

| Source | What You'll Learn |
|--------|-------------------|
| Their product (trial/demo) | Actual UX experience |
| App Store / Play Store | User complaints, praised features |
| G2, Capterra reviews | Feature gaps, satisfaction drivers |
| Customer interviews | Why they chose/left competitor |
| Job postings | Their priorities and investment areas |
| Crunchbase, LinkedIn | Size, growth, team composition |

---

## UX Pattern Analysis

### Navigation Patterns Comparison

| Pattern | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Primary nav style | Sidebar | Top bar | Sidebar | Context-dependent |
| Mobile nav | Hamburger | Bottom tabs | Hamburger | Bottom tabs for frequent use |
| Search placement | Top right | Top center | Top left | Prominent, consistent |
| Breadcrumbs | None | Full path | Abbreviated | Full path for deep hierarchy |
| Back behavior | Browser | In-app stack | Both | In-app + browser support |

### Onboarding Flow Analysis

| Element | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Steps to signup | 5 | 3 | 4 | 3-4 maximum |
| Social login | No | Yes | Yes | Offer multiple options |
| Email verification | Before use | After value | Before use | After first value |
| First-run tutorial | 8 screens | 3 tips | Progressive | Progressive in context |
| Time to value | 10 min | 2 min | 5 min | < 5 minutes |
| Skip option | No | Yes | Partial | Allow skip |

### Error Handling Comparison

| Element | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Error visibility | Red text below | Inline + icon | Toast notification | Inline + prominent |
| Error message clarity | Technical code | Plain language | Plain + solution | Plain + specific solution |
| Prevention | Minimal | Confirmations | Smart defaults | Both confirmation + prevention |
| Recovery assistance | "Try again" | Specific steps | Auto-retry | Context-specific guidance |

### Mobile Experience Benchmarking

| Element | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Touch targets | 32px | 44px | 48px | 44-48px minimum |
| Gesture support | Tap only | Swipe actions | Full gesture | Common gestures supported |
| Offline capability | None | Partial read | Full sync | Graceful degradation |
| Performance (LCP) | 3.2s | 1.8s | 2.4s | < 2.5s |
| PWA/native | Responsive web | PWA | Native app | Match user expectations |

---

## Feature Comparison Matrix

### Feature Parity Analysis

```text
FEATURE COMPARISON MATRIX

| Feature Category | Feature | Ours | Comp A | Comp B | Comp C | Priority |
|------------------|---------|------|--------|--------|--------|----------|
| Core | Basic function | Yes | Yes | Yes | Yes | Table stakes |
| Core | Advanced function | No | Yes | Yes | No | Gap to close |
| Differentiation | Unique feature | Yes | No | No | No | Maintain lead |
| Nice-to-have | Extra feature | No | Yes | No | Yes | Evaluate need |

LEGEND:
Yes = Available and good quality
Partial = Available but limited
No = Not available
Best = Best-in-class implementation
```

### UX Quality Scoring

Score each feature's UX implementation (1-5):

```text
| Feature | Ours | Comp A | Comp B | Notes |
|---------|------|--------|--------|-------|
| Search | 3 | 5 | 4 | A has autocomplete + filters |
| Dashboard | 4 | 3 | 4 | Ours is cleaner |
| Settings | 2 | 4 | 3 | Ours is scattered |
| Mobile | 2 | 4 | 5 | B is native app |
| Onboarding | 3 | 5 | 4 | A has best first-run |

SCORING CRITERIA:
1 = Major usability issues, frustrating
2 = Usable but clunky, workarounds needed
3 = Acceptable, meets basic expectations
4 = Good, pleasant to use
5 = Excellent, delightful, sets standard
```

---

## Industry Benchmarks

### E-commerce UX Standards (Baymard Institute)

| Metric | Poor | Average | Good | Best-in-Class |
|--------|------|---------|------|---------------|
| Cart abandonment | >80% | 70% | 65% | <60% |
| Checkout steps | >5 | 4-5 | 3-4 | 1-2 (guest) |
| Form fields | >15 | 10-15 | 7-10 | <7 |
| Mobile conversion | <1% | 1-2% | 2-3% | >3% |
| Product page bounce | >60% | 40-60% | 30-40% | <30% |

### SaaS UX Standards

| Metric | Poor | Average | Good | Best-in-Class |
|--------|------|---------|------|---------------|
| Signup completion | <30% | 30-50% | 50-70% | >70% |
| Activation (Day 1) | <10% | 10-25% | 25-40% | >40% |
| Time to first value | >30 min | 15-30 min | 5-15 min | <5 min |
| Trial conversion | <5% | 5-15% | 15-25% | >25% |
| NPS | <0 | 0-30 | 30-50 | >50 |

### Mobile App Standards

| Metric | Poor | Average | Good | Best-in-Class |
|--------|------|---------|------|---------------|
| App Store rating | <3.5 | 3.5-4.0 | 4.0-4.5 | >4.5 |
| Day 1 retention | <20% | 20-30% | 30-40% | >40% |
| Day 30 retention | <5% | 5-10% | 10-20% | >20% |
| Crash-free rate | <95% | 95-98% | 98-99% | >99.5% |
| Cold start time | >5s | 3-5s | 2-3s | <2s |

---

## Case Studies: Top Companies

### Optional: Assistant/Automation UX Benchmark

**UX Strengths**:
- **Simplicity**: Single input field, no complex UI
- **Conversational paradigm**: Natural interaction model
- **Progressive disclosure**: Advanced features hidden until needed
- **Error handling**: Graceful degradation, regenerate option
- **Feedback loop**: Thumbs up/down for continuous improvement

**Key Patterns to Adopt**:
```text
- Start with simplest possible interface
- Let conversation reveal complexity
- Inline feedback collection
- Clear system status (typing indicator)
- Easy recovery (regenerate, edit)
```

**UX Weaknesses**:
- Long response times (but well-communicated)
- Context management can be confusing
- Limited conversation organization

### Apple

**UX Strengths**:
- **Consistency**: Predictable patterns across all products
- **Attention to detail**: Micro-interactions, animations
- **Accessibility**: Industry-leading a11y features
- **Simplicity**: "It just works" philosophy
- **Premium feel**: Quality perception through design

**Key Patterns to Adopt**:
```text
- Design system consistency (every pixel matters)
- Thoughtful defaults (minimize configuration)
- Animation with purpose (not decoration)
- Accessibility as feature, not afterthought
- Clear hierarchy and focus
```

**Key Documents**: Human Interface Guidelines

### Stripe

**UX Strengths**:
- **Developer experience**: Best-in-class docs and API
- **Dashboard clarity**: Complex data made simple
- **Error prevention**: Smart validation, suggestions
- **Onboarding**: Guided setup with progress tracking
- **Consistency**: Unified design language

**Key Patterns to Adopt**:
```text
- Inline documentation and examples
- Smart defaults with easy override
- Progress indicators for multi-step flows
- Clear error messages with solutions
- Sandbox/test mode for learning
```

**Case Study**: Stripe's checkout conversion optimization
- Reduced fields from 8 to 4
- Added autocomplete
- Result: +10% conversion

### Notion

**UX Strengths**:
- **Flexibility**: Block-based, customizable
- **Information architecture**: Everything is a page
- **Keyboard-first**: Power user efficiency
- **Templates**: Quick start for common use cases
- **Collaboration**: Real-time, transparent

**Key Patterns to Adopt**:
```text
- Progressive complexity (simple to power user)
- Keyboard shortcuts for efficiency
- Templates for quick starts
- Slash commands for discoverability
- Block-based modularity
```

**UX Challenges**:
- Steep learning curve
- Performance with large workspaces
- Mobile limitations

### Linear

**UX Strengths**:
- **Speed**: Instant UI, optimistic updates
- **Keyboard navigation**: Full app control via keyboard
- **Minimalism**: Essential features only
- **Workflow focus**: Built around how teams work
- **Aesthetics**: Beautiful, distinctive design

**Key Patterns to Adopt**:
```text
- Performance as feature (perceived + actual)
- Keyboard shortcuts prominently featured
- Opinionated defaults (reduces decisions)
- Focus mode (reduce distractions)
- Command palette for everything
```

**Case Study**: Linear's keyboard-first approach
- Every action has shortcut
- Command palette (Cmd+K)
- Result: 40% of actions via keyboard

### Figma

**UX Strengths**:
- **Real-time collaboration**: See others' cursors
- **Browser-based**: No installation friction
- **Community**: Templates, plugins, resources
- **Multiplayer**: Built for teams from start
- **Performance**: Complex files, smooth experience

**Key Patterns to Adopt**:
```text
- Multiplayer indicators (cursors, presence)
- Web-first with native performance
- Community content integration
- Comment and feedback workflow
- Version history accessibility
```

### X (Twitter)

**UX Strengths**:
- **Feed algorithm**: Relevant content surfacing
- **Engagement mechanics**: Repost, quote, thread
- **Real-time**: Breaking news, live events
- **Brevity constraint**: Forces concise content
- **Notifications**: Engagement loop

**Key Patterns to Adopt**:
```text
- Infinite scroll with clear refresh
- Pull-to-refresh pattern
- Engagement actions always visible
- Notification badges and urgency
- Thread/conversation threading
```

**UX Challenges**:
- Content overload
- Algorithmic unpredictability
- Harassment management

### Spotify

**UX Strengths**:
- **Personalization**: Discover Weekly, algorithmic playlists
- **Search**: Fast, forgiving, predictive
- **Cross-device**: Seamless handoff
- **Browse**: Effective content discovery
- **Social**: Sharing, collaborative playlists

**Key Patterns to Adopt**:
```text
- Personalization that learns
- Cross-device continuity
- Quick actions (save, share, queue)
- Rich previews (hover to play)
- Curated collections with context
```

---

## Benchmarking Metrics

### Task Completion Comparison

```text
TASK: [Create new project]

| Step | Ours (time) | Comp A (time) | Comp B (time) |
|------|-------------|---------------|---------------|
| Find action | 5s | 2s | 3s |
| Fill form | 45s | 30s | 20s |
| Submit | 3s | 2s | 2s |
| Confirmation | 2s | 5s | 1s |
| TOTAL | 55s | 39s | 26s |

Gap Analysis:
• Fill form: Our 45s vs B's 20s (-25s)
• Root cause: Too many required fields
• Recommendation: Reduce to essential fields, smart defaults
```

### Error Rate Comparison

```text
TASK: [Complete checkout]

| Error Type | Ours | Comp A | Comp B | Industry Avg |
|------------|------|--------|--------|--------------|
| Form validation | 35% | 20% | 15% | 25% |
| Payment failure | 8% | 5% | 4% | 6% |
| Session timeout | 5% | 2% | 1% | 3% |
| User error (recoverable) | 20% | 10% | 8% | 15% |

Priority: Reduce form validation errors (biggest gap)
```

### User Satisfaction Benchmarks

```text
| Metric | Ours | Comp A | Comp B | Target |
|--------|------|--------|--------|--------|
| SUS Score | 62 | 78 | 72 | 75+ |
| NPS | +12 | +45 | +32 | +40 |
| Task satisfaction | 3.2 | 4.1 | 3.8 | 4.0 |
| Effort score | 3.8 | 2.4 | 2.9 | <3.0 |

Biggest Gap: NPS (+12 vs +45 for Comp A)
Investigation: Deep dive into promoter/detractor reasons
```

---

## Competitive Report Structure

### Executive Summary

```text
COMPETITIVE UX ANALYSIS: Executive Summary

Analysis Date: [Date]
Products Analyzed: [List]
Methodology: [Heuristic evaluation, task analysis, benchmark comparison]

KEY FINDINGS:
1. [Top competitive gap]
2. [Secondary gap]
3. [Our strength to maintain]

COMPETITIVE POSITION:
• Overall UX rank: [X of Y analyzed]
• Strongest area: [Feature/capability]
• Biggest gap: [Feature/capability]

PRIORITY RECOMMENDATIONS:
1. [High-impact, achievable improvement]
2. [Strategic investment area]
3. [Quick win opportunity]
```

### Feature-by-Feature Analysis

For each major feature area:

```text
FEATURE AREA: [Search]

OUR IMPLEMENTATION:
• Basic text search
• Filters available but hidden
• No autocomplete
• Results: relevance-based

COMPETITOR A:
• Autocomplete + suggestions
• Prominent filters
• Search history
• Results: personalized

COMPETITOR B:
• Semantic search
• Natural language queries
• Faceted navigation
• Results: contextual

GAP ANALYSIS:
• Must close: Autocomplete (table stakes)
• Should close: Prominent filters
• Opportunity: semantic/NLP capabilities

RECOMMENDATION:
Phase 1: Add autocomplete (2 weeks)
Phase 2: Surface filters (1 week)
Phase 3: Evaluate semantic search (discovery)
```

### UX Pattern Learnings

```text
PATTERNS TO ADOPT FROM COMPETITORS

From Competitor A:
• Inline onboarding tooltips (vs. our modal tutorials)
• Progress indicators in multi-step flows
• Contextual help without leaving page

From Competitor B:
• Keyboard shortcuts for power users
• Dark mode implementation
• Offline capability

From Aspirational (Linear):
• Command palette for quick actions
• Speed as feature priority
• Minimal, focused interface

PATTERNS TO AVOID:
• Competitor C's overly complex settings
• Competitor A's notification overload
```

### Recommendations Prioritization

```text
COMPETITIVE UX IMPROVEMENT ROADMAP

IMMEDIATE (0-30 days):
| Improvement | Gap Closed | Effort | Impact |
|-------------|------------|--------|--------|
| Add autocomplete search | vs. all competitors | M | High |
| Improve error messages | vs. A, B | S | Medium |

SHORT-TERM (30-90 days):
| Improvement | Gap Closed | Effort | Impact |
|-------------|------------|--------|--------|
| Redesign onboarding | vs. A | L | High |
| Add keyboard shortcuts | vs. B, Linear | M | Medium |

STRATEGIC (90+ days):
| Improvement | Gap Closed | Effort | Impact |
|-------------|------------|--------|--------|
| Mobile app (native) | vs. B | XL | High |
| Automation features | vs. emerging | XL | Uncertain |
```

---

## Competitive Analysis Checklist

### Before Analysis

- [ ] Define analysis objectives
- [ ] Select 4-6 competitors (mixed types)
- [ ] Get access to competitor products
- [ ] Prepare evaluation framework
- [ ] Align stakeholders on scope

### During Analysis

- [ ] Complete each competitor signup/onboarding
- [ ] Execute core task scenarios
- [ ] Document with screenshots/recordings
- [ ] Score using consistent criteria
- [ ] Note standout patterns (good and bad)

### After Analysis

- [ ] Synthesize findings by theme
- [ ] Create comparison matrices
- [ ] Calculate gap severity
- [ ] Prioritize recommendations
- [ ] Present to stakeholders
- [ ] Define action items with owners

---

## Domain-Specific UX Flow Patterns

**Purpose**: When designing UX flows, reference these step-by-step patterns from industry leaders instead of reinventing the wheel. Use WebSearch to verify current implementations.

### Fintech: Money Transfer Flow

**Leaders**: Wise, Revolut, Monzo, N26

#### Wise Money Transfer (Best-in-Class)

```text
FLOW: Send Money Internationally

Step 1: Amount Entry
├── Input: "You send" amount + currency selector
├── Output: "Recipient gets" with live rate
├── Show: Fee breakdown (transfer fee + conversion)
├── Show: Delivery time estimate
└── CTA: "Continue"

Step 2: Recipient Details
├── Input: Recipient name, email/phone
├── Select: How to deliver (bank, mobile money, etc.)
├── Input: Bank details (with validation)
├── Feature: Save recipient for future
└── CTA: "Continue"

Step 3: Review & Confirm
├── Show: Complete summary (amount, fee, rate, recipient)
├── Show: Rate lock countdown (e.g., "Rate guaranteed for 24h")
├── Show: Estimated arrival date
├── Checkbox: Terms acceptance
└── CTA: "Confirm and send"

Step 4: Payment
├── Select: Payment method (bank transfer, card, etc.)
├── Show: Instructions for bank transfer OR
├── Input: Card details
└── Processing indicator

Step 5: Confirmation
├── Show: Transfer ID and status
├── Show: Tracking timeline
├── Action: Share receipt
├── Action: Set up another transfer
└── Email: Confirmation sent

KEY PATTERNS:
- Upfront fee transparency (before recipient input)
- Live exchange rate with market comparison
- Rate lock feature (reduces anxiety)
- Delivery time per payment method
- Bank account validation before send
- Progress indicator throughout
```

#### Revolut Money Transfer

```text
FLOW: Send Money

Step 1: Recipient Selection
├── Show: Recent recipients (quick resend)
├── Show: Revolut contacts (instant/free)
├── Action: Add new recipient
└── Search: Find by name/phone

Step 2: Amount & Currency
├── Input: Amount to send
├── Toggle: Send in sender's or recipient's currency
├── Show: Exchange rate + comparison to market
├── Show: Fee (often £0 for Revolut-to-Revolut)
└── CTA: "Review"

Step 3: Review
├── Show: Summary with recipient photo
├── Show: Arrival time (Instant for Revolut users)
├── Optional: Add note/reference
└── CTA: "Send [amount]"

Step 4: Authentication
├── Biometric (Face ID/fingerprint)
└── Fallback: PIN

Step 5: Confirmation
├── Animation: Success checkmark
├── Show: Transaction in activity feed
└── Action: Send another

KEY PATTERNS:
- P2P prioritized (free/instant to other users)
- Recipient photos from contacts
- Biometric authentication (fast)
- Minimal steps for repeat transfers
- Real-time activity feed update
```

### Fintech: KYC/Onboarding Flow

**Leaders**: Wise, Revolut, Monzo

```text
FLOW: Account Onboarding (Wise Pattern)

Step 1: Basic Info
├── Input: Email
├── Input: Password (with strength meter)
├── Select: Country of residence
└── CTA: "Get started"

Step 2: Personal Details
├── Input: Full legal name
├── Input: Date of birth
├── Input: Phone number (with verification)
└── CTA: "Continue"

Step 3: Address Verification
├── Input: Address (with autocomplete)
├── Alternative: Manual entry
└── CTA: "Continue"

Step 4: Identity Verification
├── Select: Document type (passport, ID, license)
├── Camera: Take photo of document front
├── Camera: Take photo of document back (if needed)
├── Camera: Take selfie (liveness check)
├── Show: Processing status
└── Fallback: Manual review queue

Step 5: Verification Pending
├── Show: What's being verified
├── Show: Expected time (usually minutes)
├── Action: Continue limited setup
└── Notification: When verified

Step 6: Setup Complete
├── Show: Welcome + what you can do now
├── Action: Add money / Link bank
├── Action: Get card (physical/virtual)
└── Action: Explore features

KEY PATTERNS:
- Progressive verification (use limited features while pending)
- Real-time document scanning feedback
- Liveness detection for selfie
- Clear status on what's pending
- Estimated verification time
- Skip-and-return for optional steps
```

### E-commerce: Checkout Flow

**Leaders**: Shopify, Amazon, Stripe Checkout

#### Shopify Checkout (Best-in-Class)

```text
FLOW: Checkout

Step 1: Information
├── Input: Email (for guest) OR login prompt
├── Show: Express checkout (Shop Pay, PayPal, Apple Pay)
├── Input: Shipping address (with autocomplete)
├── Checkbox: Save info for next time
└── CTA: "Continue to shipping"

Step 2: Shipping
├── Show: Available shipping methods with prices
├── Show: Estimated delivery dates
├── Select: Preferred method
├── Show: Running total
└── CTA: "Continue to payment"

Step 3: Payment
├── Input: Card details (with card type detection)
├── Alternative: Saved payment methods
├── Alternative: Buy now pay later options
├── Input: Billing address (or same as shipping)
├── Show: Order summary
└── CTA: "Pay now"

Step 4: Confirmation
├── Show: Order number
├── Show: Confirmation email sent
├── Show: Estimated delivery
├── Action: Track order
├── Action: Create account (for guests)
└── Upsell: Related products

KEY PATTERNS:
- Express checkout above the fold
- Address autocomplete (Google Places)
- Real-time shipping calculation
- Card type auto-detection
- Guest checkout prominent
- Order summary always visible
- Trust badges near payment
```

### SaaS: Onboarding Flow

**Leaders**: Notion, Linear, Figma, Slack

#### Notion Onboarding

```text
FLOW: New User Onboarding

Step 1: Signup
├── Options: Google, Apple, Email
├── If email: Verification link sent
└── Transition: Animated loading

Step 2: Personalization
├── Question: "What will you use Notion for?"
│   ├── Personal notes
│   ├── Team wiki
│   ├── Project management
│   └── Other
├── Question: "What's your role?"
└── CTA: "Continue"

Step 3: Workspace Setup
├── Input: Workspace name
├── Optional: Invite teammates (skip available)
├── Select: Template based on earlier answers
└── CTA: "Create workspace"

Step 4: Guided Tour (Contextual)
├── Tooltip: "This is your sidebar"
├── Tooltip: "Click + to create a page"
├── Action: User creates first page
├── Tooltip: "Type / for commands"
├── Celebration: "You created your first page!"
└── CTA: "Explore templates" or dismiss

Step 5: Ongoing Education
├── Subtle hints on unused features
├── Weekly tips email (optional)
└── Help center integration

KEY PATTERNS:
- Social login (reduce friction)
- Purpose-driven personalization
- Template pre-selection based on use case
- Skip option for team invite
- Interactive tour (not video)
- Celebration moments
- Progressive feature discovery
```

#### Linear Onboarding

```text
FLOW: Team Onboarding

Step 1: Signup
├── Options: Google, SAML SSO
├── Detect: Company domain
└── Join existing workspace OR create new

Step 2: Workspace Creation
├── Input: Company name
├── Auto-suggest: URL slug
├── Select: Team size
└── CTA: "Create workspace"

Step 3: First Project
├── Input: First project name
├── Guided: Create first issue
├── Teach: Keyboard shortcut (Cmd+K)
└── Celebration: First issue created

Step 4: Team Invite
├── Input: Email addresses
├── Auto-detect: Domain colleagues
├── Slack integration: Auto-invite
└── Skip: "I'll do this later"

Step 5: Integration Setup
├── Suggest: GitHub, Slack, Figma
├── One-click: OAuth connection
└── Skip: Available

KEY PATTERNS:
- Domain detection (existing workspace join)
- Keyboard-first education early
- Minimal required steps
- Integration suggestions based on tech stack
- Skip always available
- Opinionated defaults (less choice)
```

### Developer Tools: API Documentation

**Leaders**: Stripe, Twilio, GitHub

#### Stripe Documentation Pattern

```text
FLOW: Developer First Experience

Landing:
├── Show: Code example immediately visible
├── Select: Language toggle (Node, Python, Ruby, etc.)
├── Copy: One-click code copy
└── CTA: "Get your API keys"

API Reference:
├── Left: Navigation by resource
├── Center: Endpoint documentation
│   ├── HTTP method + path
│   ├── Description
│   ├── Parameters table (required/optional)
│   ├── Code examples (request + response)
│   └── Related endpoints
├── Right: Live code example
│   ├── Toggle: Test mode / Live mode
│   ├── Auto-fill: User's API key
│   └── Run: Execute in browser
└── Footer: Related guides

Dashboard Integration:
├── Show: Recent API calls
├── Show: Error logs with debugging
├── Webhook: Test endpoint
└── Sandbox: Full test environment

KEY PATTERNS:
- Code-first (show don't tell)
- Language toggle persistent
- Copy button on all code blocks
- Live API key auto-insertion
- Try-it-now functionality
- Test mode clearly indicated
- Error messages developer-friendly
```

### Healthcare: Appointment Booking

**Leaders**: One Medical, Zocdoc, Oscar

```text
FLOW: Book Appointment

Step 1: Find Provider
├── Input: Symptom/reason for visit
├── Filter: Location, availability, insurance
├── Show: Provider cards with:
│   ├── Photo, name, specialty
│   ├── Rating + reviews
│   ├── Next available time
│   └── Distance
└── CTA: "Select provider"

Step 2: Choose Time
├── Calendar: Available dates highlighted
├── Time slots: Visual time picker
├── Show: Visit type (in-person, video)
├── Show: Duration estimate
└── CTA: "Select time"

Step 3: Patient Info
├── Input: Reason for visit (pre-filled if entered)
├── Input: Symptoms checklist
├── Input: Insurance info (or skip for self-pay)
├── Input: Pharmacy preference
└── CTA: "Continue"

Step 4: Confirm
├── Show: Appointment summary
├── Show: Cancellation policy
├── Checkbox: SMS reminders opt-in
├── Input: Add to calendar
└── CTA: "Confirm appointment"

Step 5: Pre-Visit
├── Form: Pre-visit questionnaire
├── Upload: Insurance card photo
├── Info: What to expect
└── Reminder: 24h before notification

KEY PATTERNS:
- Symptom-first search
- Next available prominently shown
- Video visit option normalized
- Insurance verification upfront
- Pre-visit forms reduce wait time
- Calendar integration
- SMS reminders default on
```

---

## Flow Pattern Usage Guide

### How to Use These Patterns

1. **Identify your domain** from the table above
2. **Find the closest flow** to what you're building
3. **WebSearch** to verify current implementation:
   - `"[company] [flow] 2026 UX"`
   - `site:mobbin.com [company]`
   - `site:pageflows.com [company]`
4. **Adapt, don't copy**: Use patterns as starting point
5. **Identify differentiation**: Where can you improve?

### Pattern Adaptation Checklist

- [ ] Reviewed 2-3 leader implementations
- [ ] Identified common patterns across leaders
- [ ] Mapped patterns to your user needs
- [ ] Identified required regulatory differences
- [ ] Found 1-2 differentiation opportunities
- [ ] Validated with user testing

### WebSearch Queries for Flow Research

```text
DISCOVERY:
"[company] [flow type] UX walkthrough"
"[company] app screenshots [feature]"
site:mobbin.com [company] [flow]
site:pageflows.com [company]

ANALYSIS:
"[company] UX case study"
"[company] design system"
"[industry] UX best practices 2026"

TEARDOWNS:
"[company] UX teardown"
"[company] vs [competitor] UX comparison"
```
