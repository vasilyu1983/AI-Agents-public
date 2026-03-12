# Usability Testing Guide

Complete methodology for planning, executing, and synthesizing usability tests to validate UX decisions.

---

## Test Type Selection

### Test Type Comparison

| Type | Participants | Moderation | Best For | Cost | Speed |
|------|--------------|------------|----------|------|-------|
| **Moderated Remote** | 5-8 | Live facilitator | Complex tasks, follow-up questions | Medium | 1-2 weeks |
| **Unmoderated Remote** | 15-50 | None (recorded) | Quick validation, large samples | Low | Days |
| **In-Person Lab** | 5-8 | Live facilitator | High-fidelity, observation | High | 2-4 weeks |
| **Guerrilla** | 5-10 | Informal | Quick feedback, early concepts | Very Low | Hours |
| **A/B Testing** | 1000s | None (automated) | Quantitative validation | Medium | Weeks |

### Test Type Decision Tree

```text
What's your primary goal?
    |
    +-- Understand WHY users struggle?
    |   +-- Need follow-up questions? --> Moderated
    |   +-- Limited budget? --> Unmoderated + post-survey
    |
    +-- Validate a specific design?
    |   +-- Early concept? --> Guerrilla / First-click
    |   +-- Final design? --> Moderated or Unmoderated
    |
    +-- Compare two options?
    |   +-- Need statistical significance? --> A/B Test
    |   +-- Qualitative preference? --> Moderated comparison
    |
    +-- Benchmark metrics?
        +-- Establish baseline --> Unmoderated (large sample)
        +-- Compare to previous --> Same methodology as baseline
```

### Formative vs Summative Testing

| Aspect | Formative | Summative |
|--------|-----------|-----------|
| **Purpose** | Find problems to fix | Measure against benchmarks |
| **Timing** | During design/development | After launch/release |
| **Sample size** | 5-8 users | 20-50 users |
| **Output** | Issues list, recommendations | Metrics, pass/fail criteria |
| **Analysis** | Qualitative themes | Quantitative statistics |

---

## Test Planning

### Objectives Definition

**Good Objectives** (Specific, Measurable):
- "Determine if users can complete checkout in under 3 minutes"
- "Identify why users abandon the signup flow"
- "Evaluate whether new navigation helps users find settings faster"

**Bad Objectives** (Vague):
- "See if users like the design"
- "Test the product"
- "Get user feedback"

### Participant Recruitment

**Sample Size Guidelines**:

| Test Type | Recommended Sample | Why |
|-----------|-------------------|-----|
| Qualitative (find issues) | 5-8 per segment | 85% of issues found with 5 users |
| Quantitative (measure) | 20-50 per variant | Statistical significance |
| A/B testing | 1000+ per variant | Detect small differences |

**Recruitment Criteria Template**:

```text
TARGET PARTICIPANT PROFILE

Demographics:
• Age range: [e.g., 25-45]
• Location: [if relevant]
• Device usage: [desktop/mobile/both]

Experience:
• Product familiarity: [never used / used <3 times / regular user]
• Domain expertise: [novice / intermediate / expert]
• Tech comfort: [low / medium / high]

Behavioral:
• Currently uses: [competitor products]
• Recently performed: [relevant activity]
• Decision-maker: [yes/no for B2B]

Exclusions:
• Works in UX/design/marketing (bias)
• Used product in last [X] months (if testing new users)
• [Company employees]
```

### Screener Questions

```text
SCREENER QUESTIONNAIRE

Q1: How often do you [relevant activity]?
[ ] Never (DISQUALIFY)
[ ] Monthly
[ ] Weekly (IDEAL)
[ ] Daily (IDEAL)

Q2: Which of the following have you used in the past 3 months?
[ ] [Competitor A] (QUALIFY)
[ ] [Competitor B] (QUALIFY)
[ ] [Your product] (DEPENDS on objective)
[ ] None of the above (DISQUALIFY)

Q3: What is your primary role?
[Open text - screen for target roles]

Q4: What devices do you primarily use for [activity]?
[ ] Desktop/laptop
[ ] Smartphone
[ ] Tablet
(Screen based on test requirements)
```

---

## Task Design

### Task Scenario Writing

**Good Task Scenarios**:
- Context: Why the user is doing this
- Goal: What they're trying to achieve
- No instructions: Don't tell them how

**Template**:
```text
SCENARIO: [Descriptive name]

CONTEXT:
"Imagine you're [situation that creates need]..."

GOAL:
"You want to [specific outcome]..."

SUCCESS CRITERIA:
• [Observable completion indicator]
• Time limit: [X minutes]
```

**Example**:
```text
SCENARIO: Find account settings

CONTEXT:
"Imagine you just got married and need to update your name on the account."

GOAL:
"Change your last name in your profile settings."

SUCCESS CRITERIA:
• User navigates to profile/settings
• User locates name field
• User makes change (or understands how to)
• Time limit: 3 minutes
```

### Task Complexity Balancing

| Task Type | Complexity | Purpose | Number per Session |
|-----------|------------|---------|-------------------|
| Warm-up | Easy | Build confidence, practice think-aloud | 1 |
| Core | Medium-Hard | Main research questions | 3-5 |
| Stretch | Hard | Stress test, edge cases | 1-2 |
| Recovery | Easy | End on positive note | 1 |

### Red Routes Prioritization

**Red Routes**: Most critical, frequently-used paths

```text
PRIORITY 1 (Must test):
• Core transaction (purchase, signup, submit)
• Primary task (what most users do most often)
• Revenue-critical paths

PRIORITY 2 (Should test):
• Secondary tasks (settings, profile)
• Error recovery paths
• Help/support access

PRIORITY 3 (Could test):
• Edge cases
• Advanced features
• Admin/power user flows
```

---

## Think-Aloud Protocol

### Types of Think-Aloud

| Type | When User Speaks | Best For | Pros | Cons |
|------|------------------|----------|------|------|
| **Concurrent** | While doing task | Natural reactions | Real-time thoughts | May slow performance |
| **Retrospective** | After task, with recording | Performance metrics | Accurate timing | Memory decay |
| **Cued Retrospective** | After task, prompted by video | Specific moments | Targeted insights | Longer sessions |

### Facilitator Introduction Script

```text
INTRODUCTION (Moderated)

"Thank you for joining today. I'm [name], and I'll be guiding you
through this session.

First, some context:
• We're testing the [product/feature], not you
• There are no wrong answers
• Your honest feedback helps us improve
• We'll be recording for our team to review

Think-aloud instructions:
• Please think out loud as you work through the tasks
• Tell me what you're looking at, thinking, and wondering
• If you'd go silent, I might ask 'What are you thinking?'

Any questions before we begin?"
```

### Probing Questions

**Use these when participant goes silent or seems stuck**:

| Situation | Probe |
|-----------|-------|
| Silent | "What are you thinking right now?" |
| Confused | "What did you expect to happen?" |
| Hesitating | "What's making you pause?" |
| Clicked wrong thing | "What were you looking for?" |
| Completed task | "How did that go?" |
| Expressing frustration | "Tell me more about that." |

### Avoiding Bias

**DON'T**:
- Ask leading questions ("Don't you think this is easier?")
- Help or give hints ("Click the blue button")
- Express opinions ("That's a good choice")
- Fill silence (give them time)
- Defend the design ("That's because...")

**DO**:
- Stay neutral ("Interesting, tell me more")
- Ask open questions ("What would you do next?")
- Observe without judgment
- Note non-verbal cues
- Follow up on interesting moments

---

## Data Collection

### Task-Level Metrics

| Metric | Definition | How to Measure |
|--------|------------|----------------|
| **Task Success Rate** | % who completed task | Binary (yes/no) or partial (0/50/100) |
| **Time on Task** | Duration to complete | Start to success or abandonment |
| **Error Rate** | Mistakes made | Count of wrong clicks/paths |
| **Assists Needed** | Help requested | Count of facilitator interventions |
| **Lostness** | Unnecessary navigation | (Pages visited - Optimal) / Pages visited |

### Task Success Scoring

```text
SUCCESS SCORING OPTIONS

Binary (simple):
• 1 = Task completed successfully
• 0 = Task failed or abandoned

Partial (nuanced):
• 100% = Completed without issues
• 50% = Completed with significant difficulty or hints
• 0% = Failed or abandoned

Granular (detailed):
• 4 = Perfect completion, no issues
• 3 = Completed with minor difficulty
• 2 = Completed with major difficulty or hints
• 1 = Partial completion
• 0 = Failed or abandoned
```

### Satisfaction Ratings

**Single Ease Question (SEQ)** - After each task:
```text
"Overall, how easy or difficult was this task?"
1 = Very Difficult ... 7 = Very Easy

Benchmark: 5.5+ is good
```

**After-Scenario Questionnaire (ASQ)** - After each task:
```text
1. "I am satisfied with the ease of completing this task"
2. "I am satisfied with the time it took to complete this task"
3. "I am satisfied with the support information"

Scale: 1 (Strongly Disagree) to 7 (Strongly Agree)
```

### Note-Taking Template

```text
SESSION NOTES

Participant: P[X]
Date/Time: [Date]
Observer: [Name]

TASK: [Task name]
Start time: [HH:MM:SS]
End time: [HH:MM:SS]
Success: [0/50/100]
SEQ: [1-7]

OBSERVATIONS:
• [Timestamp] [Observation]
• [Timestamp] [Quote - verbatim in quotes]
• [Timestamp] [Non-verbal - describe]

ISSUES IDENTIFIED:
• [Severity] [Description]

KEY QUOTES:
• "[Exact quote]"
```

---

## Analysis and Synthesis

### Affinity Mapping Process

**Step 1**: Capture all observations on sticky notes
- One observation per note
- Include participant ID
- Include task context

**Step 2**: Cluster similar observations
- Group by theme (not task)
- Name each cluster
- Identify patterns

**Step 3**: Prioritize clusters
- Frequency (how many users)
- Severity (impact on task)
- Scope (how many tasks affected)

### Issue Severity Assignment

```text
SEVERITY MATRIX

| Impact on Task | Frequency | Severity |
|----------------|-----------|----------|
| Blocks completion | 3+ users | CRITICAL |
| Blocks completion | 1-2 users | HIGH |
| Significant delay | 3+ users | HIGH |
| Significant delay | 1-2 users | MEDIUM |
| Minor friction | 3+ users | MEDIUM |
| Minor friction | 1-2 users | LOW |
```

### Pattern Identification

Look for:
- **Behavioral patterns**: Similar actions across users
- **Mental model mismatches**: Where expectations differ from reality
- **Vocabulary gaps**: Where labels don't match user language
- **Recovery strategies**: How users get unstuck
- **Success factors**: What helps users succeed

### Statistical Significance (Quantitative)

For task success rates:
```text
Sample Size Needed for 95% Confidence:

Current Success Rate | Target | Sample per Variant
60% | 80% | 36
70% | 85% | 46
80% | 90% | 64
85% | 95% | 50
```

---

## Reporting Formats

### Highlight Reel

**Purpose**: Communicate key findings quickly to stakeholders

**Structure**:
```text
USABILITY HIGHLIGHT REEL

Video Length: 5-10 minutes

1. Introduction (30 sec)
   • Test objectives
   • Participant profile

2. Key Finding 1 (1-2 min)
   • Video clip showing issue
   • Voice-over explaining impact
   • Severity rating

3. Key Finding 2 (1-2 min)
   [Same structure]

4. Key Finding 3 (1-2 min)
   [Same structure]

5. Summary and Recommendations (1 min)
   • Priorities
   • Next steps
```

### Executive Summary

```text
USABILITY TEST: Executive Summary

TEST DETAILS
• Product: [Name]
• Features tested: [List]
• Methodology: [Moderated remote / Unmoderated / etc.]
• Participants: [N] ([profile description])
• Date: [Range]

KEY METRICS
• Overall task success: [X]%
• Average SUS score: [X]/100
• Top-line finding: [One sentence]

CRITICAL ISSUES (Fix immediately)
1. [Issue] - [Impact] - [X/N users]
2. [Issue] - [Impact] - [X/N users]

HIGH-PRIORITY ISSUES (Fix soon)
1. [Issue] - [X/N users]
2. [Issue] - [X/N users]

RECOMMENDATIONS
1. [Specific action]
2. [Specific action]
3. [Specific action]

NEXT STEPS
• [Action] by [Date]
• [Action] by [Date]
```

### Detailed Findings Report

For each finding:
```text
FINDING #[X]: [Descriptive title]

SEVERITY: [Critical / High / Medium / Low]
FREQUENCY: [X of N participants]
TASKS AFFECTED: [List]

DESCRIPTION:
[What happened and why it matters]

EVIDENCE:
• Video clips: [Timestamps or links]
• Quotes: "[Verbatim quotes from users]"
• Metrics: [Task success, time, errors]

SCREENSHOTS:
[Annotated screenshots showing the issue]

ROOT CAUSE:
[Why this is happening - design, content, technical]

RECOMMENDATION:
[Specific design solution]

EFFORT ESTIMATE: [S / M / L / XL]
```

---

## Remote Testing Tools

### Tool Comparison

| Tool | Type | Best For | Price Range |
|------|------|----------|-------------|
| **UserTesting** | Unmoderated | Large-scale studies, video feedback | $$$ |
| **Maze** | Unmoderated | Rapid prototype testing | $$ |
| **Lookback** | Moderated | Live sessions, recording | $$ |
| **Hotjar** | Behavior analytics | Heatmaps, session recordings | $ |
| **Optimal Workshop** | IA testing | Card sorts, tree tests | $$ |
| **Lyssna (UsabilityHub)** | Quick tests | First-click, preference | $ |
| **Zoom** | Moderated | Live sessions (DIY) | $ |

### Tool Selection Criteria

```text
TOOL SELECTION MATRIX

| Criteria | Weight | Tool A | Tool B | Tool C |
|----------|--------|--------|--------|--------|
| Participant panel | High | 5 | 3 | 4 |
| Task builder | High | 4 | 5 | 3 |
| Recording quality | Medium | 5 | 4 | 4 |
| Analysis features | Medium | 3 | 5 | 4 |
| Price | High | 2 | 4 | 5 |
| Integration | Low | 3 | 4 | 3 |
| WEIGHTED SCORE | | 3.6 | 4.1 | 4.0 |
```

### DIY Remote Testing Setup

```text
MINIMAL REMOTE TESTING KIT

Video Conferencing:
• Zoom (screen share + recording)
• Backup: Google Meet

Screen Recording (unmoderated):
• Loom (free for short)
• OBS (free, complex)

Note-Taking:
• Notion / Google Docs
• Timer for task timing

Participant Recruitment:
• Social media outreach
• User base email
• Respondent.io (paid panel)

Analysis:
• Spreadsheet for metrics
• Miro for affinity mapping
```

---

## Usability Testing Checklist

### Planning Phase

- [ ] Define clear objectives
- [ ] Select appropriate test type
- [ ] Determine sample size
- [ ] Create screening criteria
- [ ] Write screener questionnaire
- [ ] Recruit participants
- [ ] Design tasks and scenarios
- [ ] Create facilitator guide
- [ ] Set up recording tools
- [ ] Conduct pilot test

### Execution Phase

- [ ] Send participant reminders
- [ ] Test tech setup before session
- [ ] Obtain consent and recording permission
- [ ] Deliver intro and think-aloud instructions
- [ ] Run tasks in planned order
- [ ] Take notes during session
- [ ] Administer post-task questions
- [ ] Administer post-test questionnaire (SUS)
- [ ] Thank and compensate participant

### Analysis Phase

- [ ] Review all session recordings
- [ ] Extract key observations
- [ ] Code observations by theme
- [ ] Conduct affinity mapping
- [ ] Calculate metrics (success rate, time, SEQ)
- [ ] Assign severity to issues
- [ ] Identify patterns across participants
- [ ] Prioritize findings
- [ ] Develop recommendations

### Reporting Phase

- [ ] Create highlight reel
- [ ] Write executive summary
- [ ] Document detailed findings
- [ ] Present to stakeholders
- [ ] Track issues to resolution
- [ ] Plan follow-up testing
