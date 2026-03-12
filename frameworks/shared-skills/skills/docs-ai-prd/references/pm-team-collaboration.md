# PM Team Collaboration Guide

*Purpose: Operational guide for Product Managers working with cross-functional teams (engineering, design, leadership) following traditional product development processes.*

**Note**: This guide focuses on human team collaboration. For AI-assisted coding workflows, see [agentic-coding-best-practices.md](agentic-coding-best-practices.md).

---

## When to Use This Guide

Use this guide when:

- Writing specs for human engineering teams (not AI agents)
- Collaborating across PM, design, engineering, and leadership
- Following structured product development processes (sprint planning, reviews, retrospectives)
- Need stakeholder alignment and formal documentation
- Conducting discovery research and user testing with human teams

---

## Discovery Interview Template

### Purpose

Conduct structured, unbiased interviews to uncover real user problems, goals, behaviors, and constraints before solutioning.

**Based on:** Inspired (Cagan), Software Requirements Essentials (Wiegers), User Story Mapping (Patton)

### When to Use

- Validating user problems or unmet needs
- Performing continuous discovery (ongoing user conversations)
- Exploring opportunities before committing to solutions
- Testing assumptions behind a PRD or feature
- Preparing for prototyping or usability testing
- Avoiding leading questions or opinion-driven requirements

---

### Session Setup

**Before the interview:**

1. Define learning goals (what you want to understand)
   - Example: "Understand how users currently create performance reports"
   - Example: "Identify where users struggle with data exports"
   - Example: "Validate whether problem X is worth solving"

2. Select target persona(s)
   - Primary users (most affected by problem)
   - Secondary users (indirectly affected)
   - Non-users (why don't they use current solution?)

3. Prepare context (if needed)
   - Brief product/workflow overview (don't bias with features)
   - Ensure questions are open-ended, not leading

4. Logistics
   - Decide whether to record (ask for consent)
   - Plan for 30-45 minutes
   - Bring notetaker or use transcription tool

---

### Interview Script

#### 1. Opening (5 minutes)

Use this verbatim or adapt lightly:

> "Thanks for speaking with us today. We're exploring how people do [TASK/WORKFLOW].
> There are no right or wrong answers — we're interested in your experience.
> We're not testing you; we're testing our understanding.
> With your permission, we may take notes/record for internal use only."

**Avoid:**
- Talking about your solution
- Mentioning specific features
- Setting expectations or influencing user responses

---

#### 2. Warm-Up Questions (5 minutes)

**Purpose:** Build rapport and understand context.

**Ask:**
- "Tell me a bit about your role."
- "How often do you work with [WORKFLOW/TASK]?"
- "What tools or processes do you use today?"

**Guidelines:**
- Keep this section brief
- Use open-ended questions
- Avoid yes/no questions

---

#### 3. Core Problem Exploration (15 minutes)

**Purpose:** Understand whether the problem exists and how painful it is.

**Questions:**
- "Walk me through how you currently do [TASK]."
  - Listen for steps, pain points, workarounds
- "What's the hardest part about that?"
  - Dig into specific friction points
- "When was the last time this caused an issue?"
  - Get concrete, recent examples
- "How often does this happen?"
  - Quantify frequency (daily, weekly, monthly)
- "What have you tried to solve it?"
  - Understand existing workarounds and their limitations

**Follow-Ups:**
- "Can you give an example?"
- "What happened then?"
- "How did you feel about that?"
- "Why do you think that happened?"

**Listen For:**
- Emotional language ("frustrating", "tedious", "scary")
- Workarounds (signs of unmet needs)
- Frequency and impact quantification

---

#### 4. Task & Workflow Exploration (10 minutes)

**Purpose:** Build a task map of actual behavior (not ideal or aspirational).

**Questions:**
- "What are the steps you take to accomplish [GOAL]?"
  - Map out sequence: Step 1 → Step 2 → Step 3
- "Where do you spend the most time?"
  - Identify bottlenecks
- "What tasks are manual or repetitive?"
  - Automation opportunities
- "Who else is involved in this workflow?"
  - Collaboration dependencies

**Artifacts to Create:**
- Simple sequence diagram or bullet list of steps
- Note dependencies, decision points, handoffs

**Example Output:**
```
Task: Create quarterly performance report

Steps:
1. Log into Analytics Dashboard (5 min)
2. Export data from 5 different screens (10 min)
3. Copy-paste into Excel spreadsheet (3 min)
4. Format charts and tables (7 min)
5. Add commentary and context (5 min)
6. Email to stakeholders (1 min)

Total: ~30 minutes
Bottleneck: Step 2 (multiple exports)
Pain Point: Step 4 (manual formatting inconsistent)
```

---

#### 5. Pain Points & Constraints (5 minutes)

**Purpose:** Identify root causes and real problems.

**Questions:**
- "What do you find frustrating or slow about this process?"
- "Where do errors occur?"
- "What would happen if you did nothing (or skipped this step)?"
- "Are there any regulations, policies, or constraints you must follow?"
  - Security, compliance, industry standards

**Guidelines:**
- Surface latent needs (problems users may not articulate directly)
- Avoid asking "What solution do you want?" (leads to feature requests, not problems)

---

#### 6. Validation & Evidence Gathering (5 minutes)

**Purpose:** Prioritize user problems by severity.

**Questions:**
- "How important is solving this for you?" (Scale: Low, Medium, High, Critical)
- "What would a good outcome look like?"
  - Not "What features do you want?" but "What would be different?"
- "If you had a magic wand, what would change?" (Non-binding fantasy question)

**Collect Evidence:**
- Quantify frequency: "How often?" (daily, weekly, monthly)
- Quantify impact: "How much time?" "How much money?" "How many errors?"
- Capture real examples: "Tell me about the last time..."
- Capture metrics: "How long does this take?" "How many people are affected?"

---

#### 7. Closing (5 minutes)

**Questions:**
- "Anything we didn't cover that you think is important?"
- "Would you be open to future testing (prototypes, usability studies)?"
- "Can we contact you for clarifications later?"

**Close With:**
> "Thank you — this has been extremely helpful. We'll share what we learn and how it shapes our work."

---

### Interview Debrief Template

**Use immediately after the interview (within 1 hour):**

```markdown
## Interview Debrief

**Date:** YYYY-MM-DD
**Participant:** [Name, Role, Company]
**Interviewer:** [Your Name]
**Duration:** [X minutes]

### Snapshot Summary
**Persona:** [Primary persona this user represents]
**Problem(s) Observed:** [1-2 sentence summary]
**Severity:** Low | Medium | High | Critical
**Frequency:** Daily | Weekly | Monthly | Rare
**Opportunities Identified:** [Potential solutions or next steps]

### Key Quotes
- "[Exact quote 1]"
- "[Exact quote 2]"
- "[Exact quote 3]"

### Evidence
**Quantitative:**
- Time spent: [X minutes/hours per task]
- Frequency: [X times per week/month]
- Error rate: [X% of tasks fail or require rework]

**Qualitative:**
- Example 1: [Specific incident user described]
- Example 2: [Another concrete example]

### Patterns Noted
- [Pattern 1: e.g., "All 3 users mentioned manual data entry"]
- [Pattern 2: e.g., "Users work around the system by using spreadsheets"]

### Open Questions
- [Question 1: Requires follow-up or research]
- [Question 2: Needs validation with more users]

### Next Steps
- [ ] Follow up on [specific question]
- [ ] Validate [assumption] with [X more users]
- [ ] Schedule usability test if pattern confirmed
```

---

## Quality Checklist

**During Interview:**
- [ ] User spoke >70% of the time (you mostly listened)
- [ ] No leading questions were asked ("Wouldn't it be easier if...?" AVOID)
- [ ] Problems validated with concrete examples (not hypothetical)
- [ ] Frequency and severity captured for each pain point
- [ ] No solutions pitched prematurely (focus on problem, not solution)

**After Interview:**
- [ ] Notes captured immediately (within 1 hour of interview)
- [ ] Debrief completed with key quotes and evidence
- [ ] Patterns identified across multiple interviews
- [ ] Open questions documented for follow-up

---

## Common Mistakes

### AVOID: Asking Users What Features They Want

**Bad:**
- "What features would you like to see?"
- "Would you use a PDF export button?"
- "How would you design this feature?"

**Why Bad:** Users are not designers. They'll describe incremental improvements to current tools, not breakthrough solutions.

**Good:**
- "Walk me through how you currently create reports."
- "What's frustrating about the current process?"
- "When was the last time this caused a problem?"

---

### AVOID: Talking Too Much

**Bad:** Interviewer talks 50% or more of the time.

**Why Bad:** You learn nothing. User feels interrogated, not heard.

**Good:** Interviewer talks ~20-30% of the time (asking questions, clarifying). User talks 70-80%.

---

### AVOID: Solutioning Early

**Bad:**
> "We're thinking of building a PDF export feature. Would you use it?"

**Why Bad:** Biases user response. They'll say "yes" to be polite.

**Good:**
> "How do you currently share reports with stakeholders?"
> [Listen for pain points, then explore solutions later]

---

### AVOID: Leading Questions

**Bad:**
- "Don't you think it's frustrating to manually copy data?"
- "Wouldn't it be better if we automated this?"

**Why Bad:** Puts words in user's mouth. Confirms your bias, doesn't validate real problem.

**Good:**
- "How do you feel about the current data copying process?"
- "What would be different if this step were automated?"

---

### AVOID: Accepting Hypothetical Answers

**Bad:**
> User: "I might use that feature if it were available."

**Why Bad:** Hypothetical. User hasn't demonstrated real need.

**Good:**
> "When was the last time you needed to do this?"
> "Walk me through what you did."
> [Get concrete, lived experience]

---

## Integration with PRD Writing

**Discovery Interview → PRD Flow:**

1. **Conduct 10-15 interviews** across target personas
2. **Synthesize findings** into patterns (use debrief template)
3. **Draft PRD Problem Statement** based on validated problems
4. **Reference evidence** in PRD (quotes, quantitative data)
5. **Validate PRD with users** (show draft, confirm understanding)
6. **Iterate** based on feedback

**Example Evidence in PRD:**

```markdown
## Problem Statement

### Evidence from User Research

**Qualitative:**
- "I spend more time reformatting spreadsheets than analyzing the data. I just want to click 'export' and share it." (PM Paula, Nov 2024)
- "Every time I manually copy data, there's a 50/50 chance I'll make a mistake." (PM Mike, Nov 2024)

**Quantitative:**
- 12/15 interviewed PMs cited report export as top pain point
- Average time per report: 18 minutes (n=15, time-tracking study)
- 15% of manually created reports contain data errors (QA audit, Oct 2024)
- 47 support tickets requesting export feature in Q3 2024
```

---

## Related Resources

**Internal Resources:**
- [Traditional PRD Writing Guide](traditional-prd-writing.md) - Comprehensive PRD structure and best practices
- [Requirements Checklists](requirements-checklists.md) - Validation checklists for requirements
- [Agentic Coding Best Practices](agentic-coding-best-practices.md) - AI-assisted development workflows (for comparison)

**Templates:**
- [PRD Template](../assets/prd/prd-template.md) - Copy-paste ready PRD structure
- [Story Mapping Template](../assets/stories/story-mapping-template.md) - User story mapping

**External Resources:**
- See `data/sources.json` for curated resources on user research, discovery interviews, and product management frameworks

---

> **Remember:** Great products start with great discovery. Invest time understanding the problem before jumping to solutions.
