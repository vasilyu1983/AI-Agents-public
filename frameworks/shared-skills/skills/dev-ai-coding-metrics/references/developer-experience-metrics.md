# Developer Experience Metrics for AI Tools

Measurement frameworks for developer satisfaction, cognitive load, tool friction, onboarding, and trust when using AI coding tools.

---

## Satisfaction Surveys

### Survey Cadence

| Phase | Cadence | Purpose |
|-------|---------|---------|
| Pilot (first 3 months) | Monthly | Track rapid sentiment changes during rollout |
| Post-pilot (steady state) | Quarterly | Ongoing monitoring without survey fatigue |
| After major tool changes | Ad-hoc (within 2 weeks) | Capture immediate reaction to updates |

**Response rate targets**: 70%+ for actionable data. Below 50% means results are unreliable due to self-selection bias.

Response rate improvement tactics:
- Keep surveys under 5 minutes
- Share results and actions taken from previous surveys
- Have engineering leadership visibly endorse participation
- Send during low-pressure periods (not during sprints or releases)
- Close the loop: "You said X, we did Y"

### Core Survey Questions (15 items)

Rate 1-5 (Strongly Disagree to Strongly Agree):

**Productivity Block**
1. AI tools help me complete coding tasks faster
2. AI tools reduce time I spend on repetitive work
3. I produce higher-quality code when using AI tools
4. AI tools help me learn new patterns and approaches

**Workflow Integration Block**
5. AI tools fit naturally into my existing workflow
6. I can easily switch between AI-assisted and manual coding
7. The AI tools are reliable enough for daily use
8. AI tool suggestions are relevant to my current task

**Trust and Confidence Block**
9. I trust AI-generated code enough to ship it after review
10. I can identify when AI output is incorrect or suboptimal
11. AI tools do not introduce more bugs than they prevent

**Satisfaction Block**
12. Overall, AI tools make my job more enjoyable
13. I would recommend our AI tools setup to a peer at another company
14. I feel supported in learning to use AI tools effectively
15. I prefer working at a company that provides AI coding tools

**Open-ended questions** (include 2-3):
- What is the biggest frustration with our current AI tools?
- Describe a recent situation where AI tools saved you significant time.
- What would you change about how we use AI tools?

### Tool Net Promoter Score (tNPS)

Adapt standard NPS for AI tools:

```
Question: "How likely are you to recommend [AI tool] to a
developer friend?" (0-10 scale)

Scoring:
  Promoters (9-10)  - Would actively recommend
  Passives  (7-8)   - Satisfied but not enthusiastic
  Detractors (0-6)  - Would not recommend or would warn against

tNPS = % Promoters - % Detractors
```

| tNPS Range | Interpretation |
|------------|---------------|
| 50+ | Exceptional; tool is a competitive hiring advantage |
| 30-49 | Strong; developers see clear value |
| 10-29 | Moderate; value is real but friction exists |
| 0-9 | Weak; benefits and frustrations roughly balanced |
| Below 0 | Negative; tool is hurting developer experience |

### Benchmarking Sources

- **DX Company** (getdx.com): Developer experience benchmarks across 100+ companies
- **Stack Overflow Developer Survey**: Annual data on tool satisfaction and adoption
- **JetBrains Developer Ecosystem Survey**: IDE and tool usage patterns
- **SPACE Framework** (Microsoft Research): Satisfaction, Performance, Activity, Communication, Efficiency

---

## Cognitive Load Measurement

### NASA-TLX Adaptation for AI-Assisted Coding

The NASA Task Load Index measures perceived workload across 6 dimensions. Adapted for AI coding context:

| Dimension | Original Definition | AI Coding Adaptation | Scale |
|-----------|-------------------|---------------------|-------|
| **Mental Demand** | How mentally demanding was the task? | How much mental effort was needed to formulate prompts, evaluate AI output, and integrate suggestions? | Low (1) to High (7) |
| **Temporal Demand** | How rushed did you feel? | Did AI speed create pressure to work faster than comfortable? Did waiting for AI responses disrupt your flow? | Low (1) to High (7) |
| **Performance** | How successful were you? | How satisfied are you with the quality of the AI-assisted output? | Perfect (1) to Failure (7) |
| **Effort** | How hard did you work? | How much energy did you spend steering AI (prompting, correcting, refining) vs doing the work directly? | Low (1) to High (7) |
| **Frustration** | How frustrated were you? | How much frustration from hallucinations, irrelevant suggestions, tool crashes, or context loss? | Low (1) to High (7) |
| **Trust Burden** | (New dimension) | How much effort did you spend verifying AI output for correctness, security, and style? | Low (1) to High (7) |

### Measurement Approach

**Post-task survey** (best for controlled studies):
- Administer after completing a defined coding task
- Compare AI-assisted vs manual for same task type
- Minimum sample: 20 tasks per condition per developer

**Experience sampling** (best for ongoing monitoring):
- Random prompts 2-3x per day during coding
- Brief (30-second) assessment of current cognitive state
- Captures in-the-moment load rather than recalled load

### Interpreting Results

```
HEALTHY PATTERN:
  Mental Demand:    3-4/7 (moderate, engaged but not overwhelmed)
  Temporal Demand:  2-3/7 (AI speeds up without creating pressure)
  Performance:      2-3/7 (developer is satisfied with output)
  Effort:           3-4/7 (some steering needed, but net positive)
  Frustration:      1-2/7 (minor friction, manageable)
  Trust Burden:     2-3/7 (verification needed but not exhausting)

WARNING PATTERN:
  Mental Demand:    5+/7 (prompting is harder than just coding)
  Temporal Demand:  5+/7 (AI creates speed expectations)
  Effort:           5+/7 (more energy steering than doing)
  Frustration:      4+/7 (significant friction)
  Trust Burden:     5+/7 (verification negates time savings)
```

---

## Tool Friction Indicators

Operational signals that reveal problems without requiring surveys.

### Context Switch Frequency

Track transitions between AI-assisted and manual coding within a session.

| Metric | How to Measure | Healthy Range |
|--------|---------------|---------------|
| Switches per hour | IDE telemetry or observation | 2-5 |
| Average AI-assisted stretch | Duration before switching to manual | 15+ minutes |
| Switch trigger | Log what caused the switch | Track categories |

Common switch triggers (track distribution):
- AI output not relevant to current task
- Need to think through architecture (AI not helpful)
- AI tool latency or downtime
- Task too complex for AI assistance
- Context window limitations

### Give-Up Rate

Percentage of tasks where a developer starts with AI but finishes manually.

```
Give-up rate = Tasks abandoned mid-AI / Total AI-started tasks
```

| Rate | Interpretation |
|------|---------------|
| < 10% | Excellent; AI is reliably useful |
| 10-25% | Normal; AI handles most tasks but not all |
| 25-40% | Concerning; significant task categories where AI fails |
| > 40% | Critical; tool is not fit for purpose or needs training |

Track give-up rate by task type to identify where AI tools underperform.

### Prompt Retry Rate

Average number of prompts before getting useful output.

| Attempts | Interpretation |
|----------|---------------|
| 1 | Ideal; developer has strong prompting skills |
| 2-3 | Normal; some refinement expected |
| 4-5 | Friction zone; prompting is becoming effortful |
| 6+ | Failure; developer should switch to manual |

### Suggestion Rejection Patterns

Categorize why developers reject AI suggestions:

- **Wrong approach**: AI solved the wrong problem
- **Wrong style**: Correct solution but doesn't match codebase patterns
- **Wrong scope**: Too much or too little code generated
- **Quality issue**: Bugs, security problems, or anti-patterns
- **Stale context**: AI used outdated information
- **Preference**: Developer simply prefers their approach

High rejection rates in specific categories reveal targeted improvement opportunities.

### Workflow Interruption Frequency

Count involuntary interruptions caused by AI tools:

- Tool crashes or freezes
- Unacceptable latency (> 5 seconds for inline suggestions, > 30 seconds for generation)
- Incorrect auto-complete that requires undo
- Distraction from unwanted suggestions

---

## Onboarding Metrics

### Time to First AI-Assisted PR

```
Metric: Calendar days from account activation to first merged PR
        that used AI tools in its creation.

Target: Within first 5 working days.
```

Track by:
- Role (junior, mid, senior)
- Prior AI tool experience
- Team (some teams enable faster onboarding)

### Time to Self-Sufficiency

When a developer no longer needs help from an AI champion to use tools effectively.

Indicators of self-sufficiency:
- No longer asking "how do I prompt for X?"
- Using tools for multiple task types (not just code completion)
- Helping others with AI tool questions
- Give-up rate below 25%

| Experience Level | Expected Time to Self-Sufficiency |
|-----------------|----------------------------------|
| Senior + prior AI experience | 1-2 weeks |
| Senior + no AI experience | 2-4 weeks |
| Mid-level | 3-6 weeks |
| Junior | 4-8 weeks |

### Onboarding Completion Rate

```
Completion rate = Developers who finished AI training / Total enrolled
```

Target: 90%+. Below 80% indicates training is too long, poorly timed, or not seen as valuable.

### First-Week vs First-Month Usage Patterns

| Metric | Week 1 (healthy) | Month 1 (healthy) |
|--------|------------------|-------------------|
| Daily active usage | 50%+ of workdays | 70%+ of workdays |
| Tasks attempted with AI | 3-5 per day | 8-15 per day |
| Task variety | 1-2 types | 4-6 types |
| Give-up rate | 30-50% (learning) | 15-25% (stabilizing) |

A developer whose Week 1 and Month 1 patterns are identical has stalled. Intervene with coaching.

### Mentor Dependency Duration

Track how long new developers rely on AI champions:

- **Questions asked per week** (should decline over time)
- **Question complexity** (should shift from "how to" to "best approach for")
- **Channel** (direct message vs public channel indicates confidence)

---

## Trust and Confidence Metrics

### Trust Calibration

The goal is calibrated trust: developers review AI output proportionally to its actual error rate.

```
TRUST CALIBRATION MATRIX:

                    AI Output Correct    AI Output Incorrect
                   ┌────────────────────┬────────────────────┐
Developer Accepts  │ True Acceptance    │ Over-Trust         │
                   │ (desired)          │ (dangerous)        │
                   ├────────────────────┼────────────────────┤
Developer Rejects  │ Under-Trust        │ True Rejection     │
                   │ (wasteful)         │ (desired)          │
                   └────────────────────┴────────────────────┘

Calibration Score = (True Acceptance + True Rejection) / Total Decisions
Target: > 0.80
```

### Over-Trust Indicators

Signals that developers accept AI output without adequate review:

- **Low review time**: PR review time decreases after AI adoption (should increase or stay flat)
- **Blind acceptance rate**: Accepting suggestions without cursor movement into the generated code
- **Copy-paste without edit**: AI output used verbatim at high rates (> 70%)
- **Bug attribution**: Increase in bugs traced to AI-generated code that passed review
- **Test coverage for AI code**: Lower test coverage on AI-generated sections

### Under-Trust Indicators

Signals that developers waste time rewriting adequate AI output:

- **High rejection rate with low defect rate**: Rejecting suggestions that were actually correct
- **Rewrite rate**: Developer rewrites AI output that is functionally equivalent to what was generated
- **Non-adoption despite training**: Developer avoids AI tools after completing training
- **Manual override pattern**: Consistently turning off AI suggestions in specific file types

### Confidence Progression

Track quarterly or monthly:

```
Survey item: "How confident are you in your ability to effectively
             use AI coding tools?" (1-5 scale)

Expected progression:
  Month 1:  2.5-3.0 (uncertain, still learning)
  Month 3:  3.5-4.0 (developing patterns)
  Month 6:  4.0-4.5 (confident in known scenarios)
  Month 12: 4.0-4.5 (stable, aware of limitations)
```

A confidence score that exceeds 4.5 may indicate over-confidence rather than mastery.

### Trust Recovery After AI Failures

When AI tools produce a significant failure (major bug, security issue, outage):

| Metric | Measurement |
|--------|-------------|
| Usage dip | % decrease in AI usage in the week following the failure |
| Recovery time | Days until usage returns to pre-failure levels |
| Behavioral shift | Change in review depth post-failure (should increase temporarily) |
| Narrative impact | Does the failure become "folklore" that discourages adoption? |

Track these after every notable AI failure. Typical recovery is 1-3 weeks; if longer, intervene with communication and process improvement.

---

## DX Anti-Patterns

Practices that reliably erode developer experience with AI tools.

### Mandatory Usage Policies Without Support

**What it looks like**: "All developers must use AI tools for code generation" with no training, champions, or adjustment period.

**Why it fails**: Forced adoption without support creates resentment. Developers who struggle feel judged rather than helped.

**Instead**: Set expectations for experimentation, provide training and champions, let adoption grow organically with nudges.

### Individual Productivity Tracking and Surveillance

**What it looks like**: Dashboards showing each developer's AI acceptance rate, lines generated, or time saved.

**Why it fails**: Developers game metrics. Those with lower usage feel surveilled. Trust erodes.

**Instead**: Track metrics at team level only. Individual data is for the individual developer's self-improvement, never for performance reviews.

### Comparing Developers by AI Usage

**What it looks like**: "Developer A accepts 45% of AI suggestions while Developer B only accepts 20%."

**Why it fails**: Acceptance rate depends on task type, code complexity, and coding style. Comparing developers is meaningless and harmful.

**Instead**: Compare teams over time. Compare the same developer's before/after. Never rank developers by AI metrics.

### Ignoring Negative Feedback

**What it looks like**: Dismissing complaints as "resistance to change" or "they just need more training."

**Why it fails**: Negative feedback often identifies real tool limitations. Developers who feel unheard disengage entirely.

**Instead**: Create a structured feedback channel. Categorize feedback (tool issue, training gap, workflow mismatch, personal preference). Act on the first three categories; respect the fourth.

### Removing Traditional Tools Before AI Tools Are Ready

**What it looks like**: Eliminating code snippet libraries, templates, or scaffolding tools because "AI does that now."

**Why it fails**: AI tools have failure modes. Removing fallback options creates single points of failure.

**Instead**: Keep traditional tools available. Let them naturally atrophy as AI tools prove reliable. Remove only after 6+ months of demonstrated redundancy.

### Additional Anti-Patterns

- **One-size-fits-all configuration**: Forcing identical AI tool settings across teams with different needs
- **No opt-out mechanism**: Not allowing developers to disable AI suggestions when doing focused work
- **Measuring only positive outcomes**: Collecting success stories while ignoring or suppressing negative experiences
- **AI tool sprawl**: Deploying 4-5 overlapping AI tools without consolidation guidance
- **Executive demos as proof**: Using curated demos instead of real-world measurement to justify expansion
