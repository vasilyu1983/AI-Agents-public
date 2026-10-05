# PM Collaboration and PRD Handoff Guide

*Purpose: Operational guide for Product Managers turning discovery interviews into PRD-ready evidence, for human cross-functional teams (engineering, design, leadership) following traditional product development processes.*

**Note**: This guide picks up after an interview is conducted — for interview structure and question patterns, see [interviewing-patterns.md](interviewing-patterns.md) and [discovery-best-practices.md](discovery-best-practices.md). For AI-assisted coding workflows, see docs-ai-prd's agentic-coding-best-practices.md.

---
## Table of Contents

- [When to Use This Guide](#when-to-use-this-guide)
- [Interview Debrief Template](#interview-debrief-template)
- [Interview Debrief](#interview-debrief)
- [Snapshot Summary](#snapshot-summary)
- [Key Quotes](#key-quotes)
- [Evidence](#evidence)
- [Patterns Noted](#patterns-noted)
- [Open Questions](#open-questions)
- [Next Steps](#next-steps)
- [Quality Checklist](#quality-checklist)
- [Common Mistakes](#common-mistakes)
- [AVOID: Asking Users What Features They Want](#avoid-asking-users-what-features-they-want)
- [AVOID: Talking Too Much](#avoid-talking-too-much)
- [AVOID: Solutioning Early](#avoid-solutioning-early)
- [AVOID: Leading Questions](#avoid-leading-questions)
- [AVOID: Accepting Hypothetical Answers](#avoid-accepting-hypothetical-answers)
- [Integration with PRD Writing](#integration-with-prd-writing)
- [Problem Statement](#problem-statement)
- [Evidence from User Research](#evidence-from-user-research)
- [Related Resources](#related-resources)


## When to Use This Guide

Use this guide when:

- Writing specs for human engineering teams (not AI agents)
- Collaborating across PM, design, engineering, and leadership
- Following structured product development processes (sprint planning, reviews, retrospectives)
- Need stakeholder alignment and formal documentation
- Conducting discovery research and user testing with human teams

---

For interview structure, question patterns, and session setup, use [interviewing-patterns.md](interviewing-patterns.md) and [discovery-best-practices.md](discovery-best-practices.md) — this guide picks up from a completed interview through PRD handoff.

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

**Quantitative (illustrative example, not a sourced finding):**
- 12/15 interviewed PMs cited report export as top pain point
- Average time per report: 18 minutes (n=15, time-tracking study)
- 15% of manually created reports contain data errors (QA audit, Oct 2024)
- 47 support tickets requesting export feature in Q3 2024
```

---

## Related Resources

**Internal Resources:**
- [Traditional PRD Writing Guide](traditional-prd-writing.md) - Comprehensive PRD structure and best practices
- [Interviewing Patterns](interviewing-patterns.md) - Interview structure and question patterns
- [Discovery Best Practices](discovery-best-practices.md) - Discovery cadence and synthesis
- docs-ai-prd's requirements-checklists.md - Validation checklists for requirements
- docs-ai-prd's agentic-coding-best-practices.md - AI-assisted development workflows (for comparison)

**Templates:**
- docs-ai-prd's assets/prd/prd-template.md - Copy-paste ready PRD structure
- docs-ai-prd's assets/stories/story-mapping-template.md - User story mapping

**External Resources:**
- See `data/sources.json` for curated resources on user research, discovery interviews, and product management frameworks

---

> **Remember:** Great products start with great discovery. Invest time understanding the problem before jumping to solutions.
