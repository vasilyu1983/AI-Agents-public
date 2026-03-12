# Researching Non-Technical User Segments

Research methods, recruitment strategies, and measurement frameworks for studying users with low digital literacy or low tech confidence. Complements standard UX research methods with adaptations for this population.

**When to use**: Products targeting broad consumer demographics, digital inclusion projects, government/public services, healthcare portals, or any product where a significant user segment has limited digital experience.

---

## 1. Digital Literacy Assessment Framework

### Tiers and Behavioral Indicators

| Tier | Behavioral Indicators | Assessment Method |
|------|----------------------|-------------------|
| **Excluded** | No personal device; relies on family/staff | Pre-screening: "Do you own a smartphone or computer?" |
| **Dependent** | Uses 1-2 apps with help; avoids new apps | Ask: "Which apps do you use every day?" (expect 1-3) |
| **Hesitant** | Uses familiar apps; panics at unfamiliar screens | Observe: Give a simple novel task; note hesitation time |
| **Capable** | Comfortable with common apps; avoids settings | Ask about last time they changed a setting or installed an app |
| **Confident** | Explores features; troubleshoots independently | Self-report + observed behavior match |

### Quick Assessment Protocol (5 minutes)

1. "Which devices do you use?" (phone, tablet, laptop, desktop, none)
2. "How many apps do you use at least once a week?" (0-2, 3-5, 6-10, 10+)
3. "When something goes wrong on your phone/computer, what do you do?" (ask someone / restart / search for answer / troubleshoot)
4. "Have you ever changed a setting on your phone?" (never / yes, with help / yes, independently)
5. "How would you rate your comfort with technology?" (1-5 scale)

**Scoring**: Map responses to tiers. Use tier to select appropriate research method adaptations.

---

## 2. Recruitment

### Channels (Offline-First)

Non-technical users are often underrepresented in online research panels. Recruit through:

| Channel | Reach | Quality | Cost |
|---------|-------|---------|------|
| Community centers / libraries | Digitally excluded-hesitant | High (real context) | Low (volunteer/incentive) |
| GP surgeries / pharmacies | Older adults, health-focused | High | Medium (partnership) |
| Religious organizations | Broad age range, community trust | Medium | Low |
| Adult education classes | Actively learning digital skills | High | Low |
| Customer support calls | Already users; struggling | High (real friction data) | Low (internal) |
| Family referral ("bring a relative") | Authentic non-tech users | High | Medium (dual incentive) |
| Social housing associations | Digitally excluded populations | High | Low-Medium |

**Online panels** (UserTesting, Prolific): Use screener questions to filter, but expect lower representation of truly non-technical users.

### Screening Questions (Plain Language)

Avoid jargon in screeners. Bad: "Rate your digital proficiency." Good:

- "When did you last download a new app?" (This week / This month / More than 6 months ago / Never)
- "If a website asked you to 'upload a file,' would you know how?" (Yes, easily / I'd need help / I don't know what that means)
- "Do you use a password manager?" (Yes / No / What's a password manager?)

### Recruitment Anti-Patterns

- **Don't recruit via email-only**: Excludes the most relevant participants
- **Don't use online-only screeners**: Self-selection bias toward more technical users
- **Don't require participants to install software**: Use phone calls, in-person, or browser-based tools only
- **Don't assume smartphone ownership**: Confirm device access in screening

---

## 3. Research Method Adaptations

### Usability Testing Adaptations

| Standard Practice | Adaptation for Non-Tech Users | Why |
|------------------|------------------------------|-----|
| Think-aloud protocol | Demonstrate first with unrelated example | "Think aloud" is unfamiliar to many |
| Timed tasks | Remove visible timers; measure silently | Timers cause anxiety and unnatural behavior |
| Task instructions on screen | Read tasks aloud; provide paper backup | Screen-reading while testing adds cognitive load |
| "Navigate to Settings" | "Find where you can change your password" | Use goal language, not UI language |
| Remote unmoderated | Remote moderated or in-person | Non-tech users need reassurance and help with setup |
| Recording consent form (digital) | Paper consent form read aloud | Digital forms may be intimidating |
| Post-test questionnaire (online) | Verbal debrief with structured questions | More comfortable and yields richer data |

**Session length**: 30-40 minutes maximum (shorter than typical 60-minute sessions). Non-technical users fatigue faster in unfamiliar testing environments.

### Interview Adaptations

| Standard Practice | Adaptation | Why |
|------------------|------------|-----|
| "Tell me about your workflow" | "Walk me through what you did last time you..." | Abstract questions get vague answers |
| Follow-up: "Why?" | "What happened next?" / "How did that feel?" | "Why" feels interrogative |
| Screen sharing | Sit beside them watching their screen | Screen sharing is a technical barrier |
| Scheduled via Calendly | Phone call to schedule; SMS reminder | Scheduling tools may be unfamiliar |
| Jargon in questions | Plain language; define terms if needed | Jargon causes shut-down or guessing |

### Survey Adaptations

| Standard Practice | Adaptation | Why |
|------------------|------------|-----|
| Online survey link | Paper option; phone interview option | Not all respondents are online |
| 7-point Likert scale | 3-point or 5-point with emoji faces | Granular scales are harder to differentiate |
| Matrix questions | One question per page | Matrix grids confuse non-technical users |
| Open-ended text boxes | Voice recording option; interviewer writes | Typing barriers exclude important responses |
| Technical language | Grade 6 reading level | Ensures comprehension across literacy levels |
| 15-minute survey | 5-7 minutes maximum | Shorter attention spans for unfamiliar format |

### Contextual Inquiry Adaptations

- **Conduct in their environment**: Home, community center, workplace — not a lab
- **Use their device**: Don't provide test devices; observe real conditions (cracked screens, slow connections, shared devices)
- **Note environmental factors**: Distractions, lighting, seating, other people helping
- **Ask about workarounds**: "What do you do when [X] doesn't work?" reveals real coping strategies

---

## 4. Simplification-Specific Research Questions

### Discovery Phase

- What tasks do users currently complete digitally vs. with help vs. on paper?
- What triggers abandonment? (specific screens, error types, terminology)
- What mental models do users have for common concepts? (e.g., "the cloud," "logging in," "saving")
- What existing apps do users feel confident with, and why?
- Who do users ask for help, and what do they ask about most?

### Validation Phase

- Can users complete the primary task without assistance on first attempt?
- Where do users pause or show confusion? (measure hesitation >3 seconds)
- Do users understand the terminology? (ask them to explain in their own words)
- Can users recover from errors without help?
- Do suggested actions reduce time-to-first-meaningful-action?

### Evaluative Phase

- Is the simplified flow faster than the previous version for non-tech users?
- Do non-tech users rate the experience as "easy" (top-2 box on 5-point scale)?
- Does the simplified version still work for confident users? (no feature regression)
- Are error recovery paths successful without assistance?
- Does onboarding reduce support tickets / help requests?

---

## 5. Metrics

### Primary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Unassisted task completion** | >=80% | Can users complete the primary task without researcher help? |
| **Time to first value** | <2 minutes | Time from first screen to first meaningful action/result |
| **Error recovery rate** | >=70% | Users who hit an error and successfully complete the task |
| **Comprehension score** | >=80% | Users who can explain what the screen is for in their own words |

### Secondary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Hesitation rate** | <20% of screens | Screens where users pause >3 seconds before acting |
| **Help-seeking rate** | <10% of tasks | Tasks where users ask for help or look away from screen |
| **Satisfaction (ease)** | Top-2 box >=75% | "How easy was this?" on 5-point scale |
| **Return rate** | Baseline +20% | Users who come back within 7 days (for non-one-time tasks) |

### Anti-Metrics (Track but Don't Optimize)

- **Time on task** (alone): Slower may be fine if completion is high — don't optimize for speed at the cost of comprehension
- **Feature adoption count**: Non-tech users may only need 2-3 features — breadth is not the goal
- **Session length**: Longer sessions may indicate engagement, not confusion — cross-reference with completion

---

## 6. Simplification Audit Research Protocol

Use this protocol to evaluate whether an existing interface works for non-technical users.

### Step 1: Heuristic Pre-Audit (1 day)

Run the [simplification audit template](../../software-ui-ux-design/assets/audits/simplification-audit-template.md) internally. Identify the 5 highest-risk areas.

### Step 2: Recruit (3-5 days)

Recruit 5-8 participants across tiers: 2-3 digitally hesitant, 2-3 digitally dependent, 1-2 digitally capable (control group). Use offline-first channels.

### Step 3: Task-Based Usability Test (1-2 days)

- 5-7 core tasks covering primary user journey
- Moderated, in-person or remote-moderated (never unmoderated for this population)
- Record: completion (Y/N), hesitation points, error encounters, help requests, verbal reactions

### Step 4: Comprehension Check (During Session)

After each task, ask:
- "What just happened?" (tests comprehension)
- "What would you do if [error scenario]?" (tests error recovery mental model)
- "Was anything confusing?" (open-ended)

### Step 5: Analyze and Map

- Map findings to the audit template sections (Navigation, Language, Interaction, Onboarding, Cognitive Load)
- Score severity: Critical (blocks task), Major (causes confusion + delay), Minor (noticeable but recoverable)
- Cross-reference with heuristic pre-audit — validate or refute initial assessment

### Step 6: Report and Recommend

Use the findings format below. Frame recommendations as "inclusion improvements," not "dumbing down."

---

## 7. Common Findings Patterns

### Recurring Issues

| Finding | Frequency | Typical Severity | Solution Pattern |
|---------|-----------|-----------------|-----------------|
| Icon-only buttons not understood | Very common | Major | Add text labels |
| Technical jargon in errors | Very common | Critical | Plain language error messages |
| Settings buried in nested menus | Common | Major | Surface top settings; add search |
| No recovery path from errors | Common | Critical | Add "go back" + specific guidance |
| Form validation too aggressive | Common | Major | Validate on submit, not on blur |
| Empty states with no guidance | Common | Major | Add illustration + explanation + CTA |
| Multi-step flows lose progress | Occasional | Critical | Auto-save; show progress; allow back |
| Password requirements confusing | Very common | Major | Show requirements upfront; show/hide toggle |

### Severity Framework

| Severity | Definition | Action |
|----------|-----------|--------|
| **Critical** | Blocks task completion for >=50% of non-tech users | Must fix before launch/next sprint |
| **Major** | Causes significant confusion or delay; some users abandon | Fix within 2 sprints |
| **Minor** | Noticeable friction but users recover | Backlog; fix with related work |
| **Enhancement** | Would improve experience but current is functional | Nice-to-have |

---

## 8. Reporting

### Findings Format

```text
FINDING: [Short descriptive title]
SEVERITY: Critical / Major / Minor
AFFECTED TIER: Excluded / Dependent / Hesitant / Capable
SCREEN/FLOW: [Where it occurs]
EVIDENCE: [Quote or observation from N participants]
CONFIDENCE: High (3+ participants) / Medium (2) / Low (1)
RECOMMENDATION: [Specific design change]
RELATED PATTERN: [Link to simplification-patterns.md section]
```

### Stakeholder Communication

**Frame as inclusion, not simplification**:
- Instead of: "We need to dumb down the interface"
- Say: "We're expanding our addressable market by designing for the full digital literacy spectrum"

**Use business impact language**:
- "X% of our target demographic falls below digital confidence — this represents Y potential users"
- "Support ticket analysis shows Z% of tickets come from interface confusion, not product bugs"
- "Competitor [name] serves this segment already — our current UX is a competitive gap"

**Show the spectrum**: Present findings by tier to show that simplification benefits all users, not just the "lowest" tier. Capable users also benefit from clearer language and better error messages.

---

## 9. Related Resources

- [demographic-research-methods.md](demographic-research-methods.md) — Inclusive research for seniors, children, cultures, disabilities
- [usability-testing-guide.md](usability-testing-guide.md) — Standard usability testing methods
- [ux-metrics-framework.md](ux-metrics-framework.md) — Measurement and metrics guidance
- [survey-design-guide.md](survey-design-guide.md) — Survey design and sampling
- [../../software-ui-ux-design/references/simplification-patterns.md](../../software-ui-ux-design/references/simplification-patterns.md) — Design patterns for simplified interfaces
- [../../software-ui-ux-design/assets/audits/simplification-audit-template.md](../../software-ui-ux-design/assets/audits/simplification-audit-template.md) — Scored audit template
