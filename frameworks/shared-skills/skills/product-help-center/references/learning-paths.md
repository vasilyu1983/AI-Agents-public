# Learning Paths

Onboarding sequences, tutorial design, and course structure for product education.

## Contents

- Onboarding Design Principles (2025)
- Onboarding Sequences
- Tutorial Design
- In-App Help Patterns
- Course Structure
- Tools & Platforms
- Metrics & Optimization
- Accessibility

## Onboarding Design Principles (2025)

### Modern Onboarding Philosophy

```
SHIFT FROM -> TO

Linear tours -> User-driven journeys
Feature dumps -> Value-first moments
One-size-fits-all -> Personalized paths
Separate help center -> Embedded contextual help
Completion focus -> Activation focus
```

### Activation-Focused Onboarding

```
ACTIVATION FRAMEWORK

1. Define "Aha Moment"
   - What makes users stick?
   - First value experience
   - Time to value (TTV)

2. Map critical path
   Setup -> First Use -> First Value -> Habit

3. Remove friction
   - Reduce steps to Aha moment
   - Defer non-essential setup
   - Progressive disclosure

4. Measure activation rate
   - % reaching Aha moment in Day 1
   - % reaching in Week 1
   - Drop-off points
```

### Onboarding by User Type

| User Type | Goal | Approach |
|-----------|------|----------|
| Self-serve | Quick win | Minimal guidance, clear CTAs |
| Assisted | Full setup | Guided tour + checklist |
| Enterprise | Team rollout | Admin setup + training |
| Technical | Deep understanding | Docs + sandbox |

## Onboarding Sequences

### Checklist Pattern

```
ONBOARDING CHECKLIST DESIGN

Structure:
- Account setup (required)
  -> Profile basics
  -> Connect integrations

- First [core action] (required)
  -> Guided walkthrough
  -> Celebrate completion

- Invite team (recommended)
  -> Team benefits explained
  -> Easy invite flow

- Advanced setup (optional)
  -> Power features
  -> When ready prompt

UI Best Practices:
- Progress indicator (3/5 complete)
- Estimated time per step
- Skip option (but track)
- Persistent but dismissible
- Re-accessible from menu
```

### Email Sequence

```
ONBOARDING EMAIL FLOW

Day 0 (Immediate):
Subject: Welcome to [Product] - Start here
Content: Quick start link, support contact

Day 1:
Subject: Complete your setup in 5 minutes
Content: Checklist progress, unfinished steps

Day 3:
Subject: [Feature] tip: [specific value]
Content: One feature highlight, use case

Day 7:
Subject: You're doing great - here's what's next
Content: Progress summary, advanced features

Day 14:
Subject: [Segment-specific content]
Content: Based on usage patterns

TRIGGERS (alternative to time-based):
- After first action -> Next step email
- After inactivity (3d) -> Re-engagement
- After milestone -> Celebration + next level
```

### In-App Onboarding Flow

```
IN-APP SEQUENCE

1. Welcome modal
   - Personalization question
   - "What's your goal?"
   - Route to appropriate path

2. Guided setup (critical path only)
   - Tooltip chain for setup
   - Celebrate completions
   - Max 5 steps to first value

3. Contextual prompts
   - Feature discovery on hover
   - Empty state education
   - "Did you know?" nudges

4. Progress tracking
   - Onboarding checklist widget
   - Achievement unlocks
   - Setup score/percentage
```

## Tutorial Design

### Video Tutorial Best Practices (2025)

```
VIDEO SPECIFICATIONS

Length:
- Quick tip: 30-60 seconds
- How-to: 2-4 minutes (optimal)
- Deep dive: 5-10 minutes max

Format:
- Screen recording + voiceover
- Face optional (improves trust)
- Captions always (accessibility + silent viewing)

Structure:
0:00 - Hook (problem/outcome)
0:15 - Prerequisites (if any)
0:30 - Step-by-step walkthrough
X:XX - Result demonstration
X:XX - Next steps / CTA

PRODUCTION TIPS

- Consistent intro/outro (3-5 sec)
- Zoom on important UI elements
- Highlight clicks/actions
- Pause on complex steps
- Clean desktop/browser
- HD quality (1080p minimum)
```

### Interactive Guide Patterns

```
GUIDE TYPES

1. Product Tour
   - Full feature walkthrough
   - Use for: New users, new features
   - Length: 5-10 steps
   - Trigger: First login, feature release

2. Spotlight
   - Single element highlight
   - Use for: New feature, hidden feature
   - Length: 1-3 steps
   - Trigger: First visit to area

3. Tooltip Chain
   - Sequential tooltips
   - Use for: Complex workflows
   - Length: 3-7 steps
   - Trigger: User starts action

4. Hotspot
   - Persistent help indicator
   - Use for: Complex forms
   - Length: On-demand
   - Trigger: Always visible

5. Checklist
   - Progress tracker
   - Use for: Onboarding, setup
   - Length: 5-10 items
   - Trigger: Account creation
```

### Micro-Learning Format

```
MICRO-LEARNING DESIGN

Principle: "Moment of need" support

Format:
- 1-3 minute content chunks
- Single concept per unit
- Immediately applicable
- Available in-context

Types:
- GIF demos (5-15 sec)
- Step cards (3-5 steps)
- Quick videos (60-90 sec)
- Interactive clickthroughs

Delivery:
- Contextual help panel
- Search results
- AI assistant suggestions
- Email tips
```

## In-App Help Patterns

### Tooltip Best Practices

```
TOOLTIP DESIGN

Content:
- Max 2 short sentences
- Action-oriented language
- Link to "Learn more" if needed

Positioning:
- Adjacent to element
- Never cover important UI
- Consistent placement (top/right preferred)

Behavior:
- Hover-triggered (desktop)
- Click-triggered (mobile)
- Dismissible with X
- Don't re-show if dismissed

EXAMPLE

"Import your contacts from CSV, Excel, or
directly from Google Contacts. [Learn more]"
```

### Empty State Education

```
EMPTY STATE PATTERN

Components:
1. Illustration (friendly, relevant)
2. Headline (benefit-focused)
3. Description (what to do)
4. Primary CTA (start action)
5. Secondary link (learn more)

EXAMPLE

[Illustration: Person organizing tasks]

"Get organized with your first project"

Projects help you group related tasks,
track progress, and collaborate with your team.

[+ Create Project] (primary)
"Watch a quick tour" (secondary)
```

### Contextual Help Panel

```
HELP PANEL DESIGN

Trigger:
- ? icon in UI
- Keyboard shortcut (?)
- Menu item (Help)

Content:
- Relevant to current page
- Search box
- Quick links (top 3-5)
- AI assistant option
- Contact support fallback

Behavior:
- Slide-in from right
- Doesn't navigate away
- Persists across pages
- Easy dismiss (X or outside click)
```

### Error State Education

```
ERROR MESSAGE PATTERN

Structure:
1. What happened (clear, non-technical)
2. Why it happened (if known)
3. How to fix it (actionable steps)
4. Help link (if complex)

EXAMPLES

Bad: "Error 403: Forbidden"

Good:
"You don't have access to this page

This page is only available to Admin users.
If you need access, contact your team admin.

[Request Access] [Go to Dashboard]"

---

Bad: "Validation failed"

Good:
"Please fix these issues to continue:

- Email: Enter a valid email address
- Password: Must be at least 8 characters
- Company: This field is required"
```

## Course Structure

### Learning Path Design

```
LEARNING PATH FRAMEWORK

Structure:
Path -> Modules -> Lessons -> Topics

Path: "Become a Power User"
|-- Module 1: Getting Started (Beginner)
|   |-- Lesson 1.1: Account Setup
|   |-- Lesson 1.2: Dashboard Overview
|   \\-- Lesson 1.3: First [Action]
|-- Module 2: Core Features (Intermediate)
|   |-- Lesson 2.1: [Feature A]
|   |-- Lesson 2.2: [Feature B]
|   \\-- Lesson 2.3: [Feature C]
\\-- Module 3: Advanced (Expert)
    |-- Lesson 3.1: Automation
    |-- Lesson 3.2: Integrations
    \\-- Lesson 3.3: Best Practices

EACH LESSON INCLUDES:
- Video (2-4 min)
- Written guide
- Practice exercise
- Quiz (optional)
- Completion badge
```

### Course Content Templates

```markdown
# Lesson: [Lesson Title]

**Duration**: [X minutes]
**Level**: [Beginner/Intermediate/Advanced]
**Prerequisites**: [List or "None"]

## Learning Objectives

By the end of this lesson, you will:
- [ ] [Objective 1]
- [ ] [Objective 2]
- [ ] [Objective 3]

## Video Tutorial

[Embedded video]

## Step-by-Step Guide

### Step 1: [Action]

[Instructions]

![Screenshot](path/to/screenshot.png)

### Step 2: [Action]

[Instructions]

> **Tip**: [Helpful hint]

## Practice Exercise

Try this on your own:

1. [Task 1]
2. [Task 2]
3. [Task 3]

**Expected result**: [What they should see]

## Quiz (Optional)

1. [Question]
   - [ ] Option A
   - [ ] Option B
   - [x] Option C (correct)

## Summary

Key takeaways:
- [Point 1]
- [Point 2]
- [Point 3]

## Next Steps

- [Next lesson link]
- [Related resource]
- [Practice project]
```

### Certification Programs

```
CERTIFICATION STRUCTURE

Levels:
1. Foundation (Basics)
2. Professional (Core competency)
3. Expert (Advanced + real-world)

Requirements per level:
- Complete all modules
- Pass assessment (70%+ score)
- Practical project (optional)

Assessment types:
- Multiple choice quiz
- Hands-on tasks
- Scenario-based questions
- Peer review (expert level)

Benefits:
- Badge/certificate
- LinkedIn credential
- Community recognition
- Partner/agency requirement
```

## Tools & Platforms

### Onboarding Tools Comparison

| Tool | Best For | Pricing | Key Feature |
|------|----------|---------|-------------|
| **Appcues** | No-code flows | $$$ | Visual builder |
| **UserPilot** | PLG companies | $$ | Segment targeting |
| **Pendo** | Enterprise | $$$$ | Analytics depth |
| **Whatfix** | Complex enterprise | $$$$ | DAP features |
| **Chameleon** | Startups | $ | Simple setup |
| **Intercom Tours** | Intercom users | Included | Messenger integration |

### Video Hosting

| Platform | Best For | Features |
|----------|----------|----------|
| **Loom** | Quick captures | Easy recording, sharing |
| **Wistia** | Marketing | CTAs, heatmaps, SEO |
| **Vidyard** | Sales/support | Personalization |
| **YouTube** | Public content | Free, SEO |
| **Vimeo** | Professional | Quality, privacy |

### Course Platforms

| Platform | Best For | Type |
|----------|----------|------|
| **Thinkific** | Course business | Hosted |
| **Teachable** | Creators | Hosted |
| **LearnDash** | WordPress | Plugin |
| **Skilljar** | Customer education | Enterprise |
| **WorkRamp** | Employee training | Enterprise |

## Metrics & Optimization

### Onboarding Metrics

| Metric | Definition | Benchmark |
|--------|------------|-----------|
| **Activation rate** | % reaching Aha moment | 30-50% |
| **Onboarding completion** | % finishing checklist | 60-80% |
| **Time to value** | Time to first value | <1 day ideal |
| **Tour completion** | % finishing tours | 40-60% |
| **Drop-off point** | Where users abandon | Identify & fix |
| **Feature adoption** | % using key features | Track per feature |

### Tutorial Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Video completion** | % watching to end | >60% |
| **Avg. watch time** | Seconds viewed | >70% of length |
| **Rewatch rate** | % rewatching | <20% (too complex?) |
| **Help -> action** | Tutorial -> feature use | Track correlation |
| **Support ticket reduction** | Tickets pre/post | 20-40% reduction |

### Optimization Strategies

```
CONTINUOUS IMPROVEMENT

Weekly:
- Review drop-off points
- Check completion rates
- Identify stuck users

Monthly:
- Update outdated content
- A/B test tour variants
- Analyze feature adoption

Quarterly:
- Full onboarding audit
- User interviews
- Benchmark against peers
- Rebuild underperforming flows
```

## Accessibility

### Accessible Onboarding

```
ACCESSIBILITY REQUIREMENTS

Visual:
- Sufficient color contrast (4.5:1)
- Don't rely on color alone
- Alt text for images/GIFs
- Captions for all videos

Interaction:
- Keyboard navigable tours
- Focus management
- Skip options
- Respect reduced motion

Content:
- Clear, simple language
- Reading level: Grade 8
- Avoid jargon
- Multiple formats (video + text)

TESTING

- Screen reader testing (NVDA, VoiceOver)
- Keyboard-only navigation
- Color blindness simulation
- Automated a11y tools (axe, Lighthouse)
```
