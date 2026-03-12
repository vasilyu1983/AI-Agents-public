# Operational Playbook — UI/UX Design Decision Frameworks

Decision frameworks, design themes, and operational patterns for day-to-day UI/UX design work.

**Last Updated**: January 2026

---

## Core Design Themes

- Design for humans first, technology second.
- Consistency creates predictability and builds user confidence.
- Accessibility is not optional — design inclusively from the start.
- Test with real users early and often.
- Mobile-first approach ensures usability across all devices.
- Every design decision should solve a user problem.
- **Avoid generic, template-driven aesthetics — create distinctive, context-specific designs.**

---

## Pattern: Distinctive Frontend Aesthetics

Use this pattern to avoid generic, template-driven designs and create memorable, context-appropriate interfaces.

**Problem**: Trend cycles converge toward the same default patterns (safe fonts, safe gradients, familiar layouts), creating forgettable “template sameness”.

**Solution**: Intentionally choose distinctive typography, committed color themes, orchestrated motion, and atmospheric backgrounds.

**Four Pillars**:

1. **Typography with Character**
   - Avoid: Inter, Roboto, Arial, Space Grotesk (overused)
   - Choose: Distinctive display fonts + readable body fonts
   - Examples: Outfit + Source Serif Pro, Syne + IBM Plex Sans

2. **Committed Color & Themes**
   - Avoid: Purple gradients, evenly-distributed palettes
   - Choose: Dominant color (60-70%) + sharp accents (5-10%)
   - Strategies: Dark-first with neon, warm earth tones, bold monochrome, brutalist

3. **Motion with Intention**
   - Avoid: Scattered micro-interactions everywhere
   - Choose: One well-orchestrated page load with staggered reveals (animation-delay)
   - Focus: High-impact moments (page transitions, success states)

4. **Backgrounds with Depth**
   - Avoid: Flat solid colors
   - Choose: Layered gradients, geometric patterns, contextual effects
   - Examples: Mesh gradients, grid patterns, glassmorphism (when appropriate)

**Checklist**:
- Font choice is intentional, not default
- Color palette has dominant theme (not evenly distributed)
- Motion is orchestrated, not scattered
- Background creates atmosphere, not just fills space
- Design feels context-specific, not generic

See [references/frontend-aesthetics-2025.md](frontend-aesthetics-2025.md) for comprehensive implementation guide.

---

## Cognitive Design Foundations

Apply perceptual and cognitive principles to reduce effort and error risk.

- Gestalt grouping: proximity, alignment, similarity, continuity to cluster related elements; avoid equidistant “flat grids” that hide hierarchy.
- Preattentive cues: color, weight, size, and iconography to signal status/priority; reserve strong color for primary action/safety states.
- Hick’s Law: reduce visible choices per step; progressive disclosure beats crowded screens.
- Fitts’ Law: make primary targets larger and closer to expected cursor/touch paths; keep touch targets ≥44x44px.
- Working memory limits: chunk content, avoid forcing recall; use recognition (chips, recent items, suggested defaults).
- Change blindness: keep persistent anchors (headers, tabs), animate layout changes, confirm destructive actions.

Checklist:
- At-a-glance hierarchy is clear (size/weight/color/spacing).
- One dominant action per screen; secondary actions visually demoted.
- Dense data? Add visual grouping and scanning aids (striping, column alignment, sparklines).
- Reduce steps by default; reveal detail on demand.

---

## Pattern: User-Centered Design (UCD)

Use this pattern to keep users at the center of every design decision.

Process:
1. Research — Understand user needs, behaviors, and pain points.
2. Define — Identify problems and requirements.
3. Ideate — Generate multiple solutions.
4. Prototype — Create low to high-fidelity mockups.
5. Test — Validate with real users.
6. Iterate — Refine based on feedback.

Checklist:
- User research conducted before design.
- Personas or user profiles defined.
- Usability testing planned for each iteration.
- Feedback loops incorporated into timeline.

---

## Pattern: Nielsen's 10 Usability Heuristics

Use these heuristics for rapid UX evaluation and design decisions.

Quick Reference:
1. Visibility of system status — Keep users informed.
2. Match between system and real world — Use familiar language.
3. User control and freedom — Provide undo/redo.
4. Consistency and standards — Follow platform conventions.
5. Error prevention — Design to prevent errors before they occur.
6. Recognition over recall — Minimize memory load.
7. Flexibility and efficiency — Support novice and expert users.
8. Aesthetic and minimalist design — Remove unnecessary elements.
9. Help users recognize, diagnose, and recover from errors.
10. Help and documentation — Provide when needed.

See [references/nielsen-heuristics.md](nielsen-heuristics.md) for detailed examples and implementation.

---

## Pattern: WCAG Accessibility (POUR Principles)

Use these principles to ensure accessible design for all users.

Four Core Principles:
1. Perceivable — Content must be presentable in different ways.
   - Text alternatives for images
   - Captions for audio/video
   - Color contrast ratio 4.5:1 minimum (7:1 for AAA)
   - Responsive text sizing

2. Operable — Interface components must be operable.
   - Keyboard navigation support
   - Touch targets minimum 44x44 pixels
   - No keyboard traps
   - Avoid flashing content (seizure risk)

3. Understandable — Information and operation must be clear.
   - Readable text (language, reading level)
   - Predictable navigation
- Clear error messages with recovery guidance
- Consistent labels and instructions

4. Robust — Content works with current and future tools.
  - Valid HTML/semantic markup
   - ARIA labels where needed
   - Screen reader compatibility
   - Cross-browser testing

Checklist:
- Color contrast validated (use tools like WebAIM Contrast Checker)
- All interactive elements keyboard accessible
- Form fields have visible labels
- Alt text for all meaningful images
- ARIA roles applied correctly

See [references/wcag-accessibility.md](wcag-accessibility.md) for WCAG 2.2 success criteria.

---

## Pattern: Signifiers, Mappings, Constraints

Use to make interactivity obvious, map controls to outcomes, and prevent slips/mistakes.

Principles:
- Signifiers: Make interactive elements visually distinct (focus/hover/active states, iconography, affordance hints).
- Natural mapping: Place controls near the thing they affect; align motion/values with real-world direction (up = more, right = next).
- Constraints and forcing functions: Disable destructive actions until preconditions are met; require confirmations for irreversible steps.
- Slips vs. mistakes: Offer undo for slips (accidental taps/edits); add warnings and previews for mistakes (wrong target/goal).

Checklist:
- Every interactive element has visible default + focus/active states.
- Primary action placement matches expected flow (e.g., forward on the right, cancel on the left).
- Destructive actions require confirmation or staged disclosure.
- Undo available for common errors (draft restore, revert, back).

---

## Pattern: Mobile-First Design

Use when designing for multiple screen sizes and device types.

Principles:
- Start with smallest screen (320px)
- Progressive enhancement as screen grows
- Touch targets 44x44 pixels minimum
- Vertical scrolling preferred over horizontal
- Simplify navigation (hamburger menus, bottom nav)
- Optimize images and assets for mobile bandwidth

Responsive Breakpoints:
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px - 1439px
- Large Desktop: 1440px+

Checklist:
- Critical content visible without scrolling on mobile
- Touch gestures tested on actual devices
- Forms optimized (correct input types, minimal fields)
- Performance budget defined for mobile

---

## Pattern: Design Systems

Use to maintain consistency across products and teams.

Components:
- Foundations:
  - Color palette (primary, secondary, semantic)
  - Typography scale (headings, body, captions)
  - Spacing system (4px or 8px grid)
  - Elevation/shadows
  - Border radius and borders

- Components:
  - Buttons (primary, secondary, tertiary, disabled states)
  - Form inputs (text, select, checkbox, radio, toggle)
  - Navigation (header, sidebar, tabs, breadcrumbs)
  - Feedback (alerts, toasts, modals, tooltips)
  - Cards, lists, tables
  - Icons and illustrations

- Patterns:
  - Page layouts
  - Form patterns
  - Data visualization
  - Loading states
  - Empty states
  - Error states

Benefits:
- 34% faster design completion (Figma research)
- Consistent user experience
- Easier onboarding for new team members
- Faster development with reusable components

See [references/design-systems.md](design-systems.md) for implementation guide.

---

## Pattern: Information Architecture

Use when organizing content and navigation structure.

Principles:
- Card sorting — Organize content based on user mental models.
- Hierarchy — Most important content most visible.
- Progressive disclosure — Show essential info first, details on demand.
- Chunking — Group related items (7±2 rule).
- Clear labeling — Avoid jargon, use user language.

Navigation Types:
- Global navigation — Primary site/app navigation
- Local navigation — Section-specific navigation
- Contextual navigation — Related content links
- Breadcrumbs — Show location in hierarchy

Checklist:
- Site map or flow diagram created
- Navigation tested with users
- Maximum 3 clicks to reach any page (when possible)
- Search functionality for content-heavy sites

---

## Pattern: Form Design Best Practices

Use when designing data entry and input interfaces.

Guidelines:
- Single column layouts reduce errors
- Group related fields
- Inline validation (real-time feedback)
- Clear error messages near the field
- Required fields marked clearly
- Appropriate input types (email, tel, number, date)
- Auto-complete and auto-format when possible
- Progress indicators for multi-step forms

Error Prevention:
- Validate on blur, not on every keystroke
- Provide format examples (e.g., "MM/DD/YYYY")
- Disable submit button until form is valid
- Preserve data if user navigates away

Field Reduction:
- Most forms can reduce fields by 20-60%
- Only ask for essential information
- Use smart defaults
- Consider progressive profiling

Checklist:
- All fields have visible labels
- Tab order follows visual flow
- Error states tested and clear
- Success confirmation shown

---

## Pattern: Visual Hierarchy

Use to guide users' attention to the most important content.

Techniques:
- Size — Larger elements attract attention first
- Color — High contrast and bright colors stand out
- Spacing — White space creates emphasis
- Typography — Weight, style, and case for hierarchy
- Position — Top-left gets noticed first (F-pattern reading)

F-Pattern Reading:
- Users scan horizontally at the top
- Second horizontal scan lower
- Vertical scan down left side
- Design most important content along this pattern

Z-Pattern (Simpler Pages):
- Eyes start top-left
- Move horizontally to top-right
- Diagonal to bottom-left
- Horizontal to bottom-right
- Place CTAs at terminal points

Checklist:
- One clear primary action per screen
- Visual weight matches importance
- Sufficient white space around key elements
- Color used intentionally, not decoratively

---

## Pattern: Interaction Design

Use when designing user interactions and micro-interactions.

Principles:
- Feedback — Every action gets a response
- Consistency — Similar actions behave similarly
- Constraints — Prevent invalid actions
- Affordances — Visual cues indicate interactivity

Micro-interactions (Four Parts):
1. Trigger — What initiates the interaction
2. Rules — What happens during interaction
3. Feedback — How users know it happened
4. Loops/Modes — Meta-rules for ongoing behavior

Examples:
- Button states: default, hover, active, disabled
- Loading spinners for async operations
- Success animations after form submission
- Skeleton screens while content loads
- Toast notifications for background actions

Timing Guidelines:
- Instant: <100ms (feels immediate)
- Quick: 100-300ms (perceptible but fast)
- Smooth: 300-500ms (animations, transitions)
- Patient: 500-1000ms (complex state changes)
- Beyond 1s: Show progress indicator

---

## Optional: AI/Automation — Personalization and Automation UX

> Use only when the product includes automation/AI-powered features. Skip for traditional software UX.

Principles (Modern Best Practices):
- Transparency — Explain when automation is used
- Control — Allow users to override automation decisions
- Fallbacks — Graceful degradation if automation fails
- Privacy — Clear data usage policies

Automation UX Patterns:
- Smart suggestions (not forced)
- Adaptive interfaces based on behavior
- Personalized content recommendations
- Predictive search and autocomplete
- Context-aware defaults

Guidelines:
- Don't hide that automation is powering features
- Provide "why" explanations for recommendations
- Easy opt-out or manual override
- Test for bias in automated outputs

---

## Component Library Selection (2024-2025)

**Quick Decision Guide:**

**For Tailwind CSS Users:**
- **1st Choice**: shadcn/ui (copy-paste, full ownership, 66k+ stars)
- **Alternative**: Headless UI (official Tailwind companion)

**For Enterprise Applications:**
- **1st Choice**: MUI (Material Design, 95k+ stars, 4.1M downloads/week)
- **Alternative**: Ant Design (admin dashboards, 94k+ stars)

**For Accessibility Priority:**
- **1st Choice**: Chakra UI (best-in-class accessibility, intuitive API)
- **Alternative**: Radix UI or React Aria (unstyled primitives)

**For Rapid Prototyping:**
- **1st Choice**: Mantine (120+ components, 100+ hooks)
- **Alternative**: MUI (comprehensive out-of-the-box)

See [references/component-library-comparison.md](component-library-comparison.md) for detailed comparison with bundle sizes, performance metrics, and migration guides.

---

## Modern UX Patterns (2024 Standards)

**Essential Patterns:**
- **Skeleton Screens** — Preferred over spinners for loading states
- **Optimistic UI** — Instant feedback before server confirmation (likes, favorites, cart)
- **Progressive Disclosure** — Show essential info first, details on demand
- **Inline Validation** — Real-time form feedback (validate on blur, not keystroke)
- **Micro-interactions** — Standard across mobile and desktop (200-400ms timing)
- **Toast Notifications** — Non-blocking feedback (auto-dismiss 3-5 seconds)
- **Command Palettes** — Keyboard-driven quick actions (Cmd+K)
- **Empty States with Actions** — Clear next steps (never blank pages)

See [references/modern-ux-patterns-2025.md](modern-ux-patterns-2025.md) for implementation details and code examples.

---

## Quick Decision Framework

When making UI/UX decisions, ask:

1. Does this solve a real user problem? (User-centered)
2. Is this consistent with platform conventions? (Standards)
3. Can all users access this feature? (Accessibility)
4. Is the interaction clear without explanation? (Intuitive)
5. Does this add value or just complexity? (Minimalism)
6. How will we measure success? (Metrics)

If "no" to any question, reconsider the design.

---

## Lean Testing Cadence

- Habitual testing: 5-user hallway/usability tests for each significant flow monthly or per feature increment.
- Protocol: 5-second test (what is this page?), first-click test (where do you act?), then task success/time, errors, and comments.
- Metrics to log: Task success rate, time on task, error rate (slips vs mistakes), SUS/CSAT, drop-off points.
- Rapid checks: Run microcopy and navigation labels through plain-language/read-aloud review; validate focus order and touch targets after UI changes.

---

## Common Anti-Patterns to Avoid

- Auto-playing videos or audio
- Carousel/slideshow for critical content (most users only see first slide)
- Hamburger menus hiding essential navigation
- Disabled buttons without explanation
- Tooltips for critical information
- Modal overload (disruptive)
- Infinite scroll without pagination option
- Generic error messages ("Something went wrong")
- Forced registration before showing value
- Dark patterns (manipulative design)

---

## Metrics and Testing

Usability Metrics:
- Task success rate
- Time on task
- Error rate
- Satisfaction (System Usability Scale)
- Net Promoter Score (NPS)

Testing Methods:
- A/B testing for data-driven decisions
- Usability testing (5 users find 85% of issues)
- Heuristic evaluation
- Accessibility audits
- Analytics and heatmaps

---

## External Resources

See [data/sources.json](../data/sources.json) for curated references on:

- Nielsen Norman Group usability research
- WCAG accessibility guidelines and tools
- Design system examples (Material, Fluent, Carbon, Polaris)
- UX research methodologies
- Design and prototyping tools (Figma, Sketch, Adobe XD)
- Component libraries and frameworks
