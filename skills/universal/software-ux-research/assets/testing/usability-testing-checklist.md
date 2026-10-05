# Usability Testing Checklist

Complete checklist for planning, executing, and analyzing usability tests.

---

## Pre-Test Planning

### Study Definition

- [ ] Research questions documented
- [ ] Success metrics defined (task success rate, time-on-task, error rate)
- [ ] Scope limited to a small set of core tasks
- [ ] Hypothesis stated (what we expect to find)

### Task Design Checklist

| Task # | Task Description | Success Criteria | Time Limit |
|--------|------------------|------------------|------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Task Quality Checks

- [ ] Tasks are realistic user goals (not feature tours)
- [ ] Tasks avoid leading language ("Click the blue button")
- [ ] Tasks have clear start and end points
- [ ] Tasks are ordered from easy to hard (warm-up first)
- [ ] Tasks don't reveal answers in wording
- [ ] Tasks can be completed in session time

### Participant Recruitment

| Criterion | Target | Actual |
|-----------|--------|--------|
| **Total participants** | | |
| **Novice users** | | |
| **Experienced users** | | |
| **Segment A** | | |
| **Segment B** | | |

### Recruitment Checklist

- [ ] Screener questions drafted
- [ ] Screener tested with team member
- [ ] Incentive determined and budget approved
- [ ] Recruitment channel selected
- [ ] Calendar slots available
- [ ] Backup participants scheduled (+20%)
- [ ] Confirmation emails scheduled

---

## Test Setup

### Environment Checklist

**For Remote Testing:**

- [ ] Video conferencing tool tested (Zoom, Lookback, UserTesting)
- [ ] Screen sharing works
- [ ] Recording permissions configured
- [ ] Backup recording method ready
- [ ] Quiet environment confirmed
- [ ] Internet connection stable
- [ ] Calendar invites sent with join link

**For In-Person Testing:**

- [ ] Room booked
- [ ] Recording equipment tested
- [ ] Prototype/product accessible
- [ ] Observer seating arranged
- [ ] Consent forms printed
- [ ] Incentives ready
- [ ] Water/snacks available

### Materials Checklist

- [ ] Discussion guide printed/accessible
- [ ] Consent form ready
- [ ] Note-taking template open
- [ ] Task scenarios prepared (no leading language)
- [ ] Prototype/product tested and working
- [ ] SUS questionnaire ready (if using)
- [ ] Post-task questions ready
- [ ] Observer instructions sent

### Prototype/Product Readiness

- [ ] All task paths functional
- [ ] Realistic data populated
- [ ] Error states tested
- [ ] Mobile/responsive checked (if applicable)
- [ ] Login credentials prepared
- [ ] Reset procedure documented

---

## Session Execution

### Introduction Script Checklist (5 min)

- [ ] Thank participant for time
- [ ] Explain session purpose (testing product, not them)
- [ ] Review consent and recording
- [ ] Explain think-aloud protocol
- [ ] Confirm participant can stop anytime
- [ ] Ask if they have questions
- [ ] Start recording

### Think-Aloud Prompts

| Situation | Prompt |
|-----------|--------|
| Participant goes silent | "What are you thinking?" |
| Participant stuck | "What would you do normally?" |
| Participant asks for help | "What do you think you should do?" |
| Participant frustrated | "It's okay, this is exactly what we need to learn" |
| Participant succeeds quickly | "Walk me through what you just did" |

### During-Task Observation Checklist

For each task, note:

- [ ] Task success (Complete / Partial / Fail)
- [ ] Time to complete
- [ ] Errors made (count and type)
- [ ] Hesitations/confusion points
- [ ] Verbalized thoughts
- [ ] Workarounds attempted
- [ ] Help sought
- [ ] Emotional reactions

### Post-Task Questions

After each task:
1. "How easy or difficult was that?" (1-5 scale)
2. "What made it [easy/difficult]?"
3. "Was there anything you expected to find but didn't?"

### Session Close Checklist (5 min)

- [ ] Overall impressions asked
- [ ] SUS questionnaire administered (if using)
- [ ] Open questions invited
- [ ] Next steps explained
- [ ] Incentive provided/sent
- [ ] Thank participant
- [ ] Stop recording

---

## Post-Session Processing

### Immediate (Within 24 Hours)

- [ ] Notes reviewed and cleaned
- [ ] Key observations highlighted
- [ ] Video timestamps noted for key moments
- [ ] Task success recorded
- [ ] SUS score calculated (if applicable)
- [ ] Urgent issues flagged

### Data Recording Template

| Participant | Task 1 | Task 2 | Task 3 | Task 4 | Task 5 | SUS | Key Quote |
|-------------|--------|--------|--------|--------|--------|-----|-----------|
| P1 | [check]/[x]/~ | | | | | | |
| P2 | | | | | | | |
| P3 | | | | | | | |
| P4 | | | | | | | |
| P5 | | | | | | | |

**Legend**: [check] = Complete, [x] = Fail, ~ = Partial

---

## Analysis Framework

### Quantitative Metrics

| Metric | Formula | Baseline/Goal | Result |
|--------|---------|---------------|--------|
| **Task success rate** | Successful / Total × 100 | | |
| **Time on task** | Average completion time | | |
| **Error rate** | Errors / Attempts | | |
| **SUS score** | Standard calculation | | |
| **Task difficulty (avg)** | Sum of ratings / N | | |

### Issue Identification

For each issue found:

| Field | Value |
|-------|-------|
| **Issue ID** | |
| **Description** | |
| **Task affected** | |
| **Participants affected** | P1, P3, P5 (n=3) |
| **Severity** | Critical / Major / Minor |
| **Frequency** | How many encountered |
| **User impact** | What happened |
| **Quote** | "Participant verbatim" |
| **Video timestamp** | 00:00:00 |
| **Recommendation** | |

### Severity Rating Guide

| Severity | Criteria | Action |
|----------|----------|--------|
| **Critical** | Prevents completion or causes data loss/safety risk | Fix before launch |
| **Major** | Completion possible but high friction or repeated errors | Fix soon |
| **Minor** | Low impact confusion; workaround exists | Backlog |
| **Enhancement** | Improvement opportunity, not a problem | Consider for future |

### Pattern Recognition Checklist

- [ ] Grouped issues by task
- [ ] Grouped issues by page/screen
- [ ] Grouped issues by issue type (navigation, labeling, feedback, etc.)
- [ ] Identified issues affecting multiple participants
- [ ] Noted positive feedback and successes
- [ ] Compared novice vs. expert performance

---

## Synthesis & Reporting

### Findings Report Structure

```markdown
# Usability Test Report: [Product/Feature]

## Executive Summary
- **Date**:
- **Participants**: n=X
- **Tasks tested**: X
- **Overall task success rate**: X%
- **SUS score**: X
- **Critical issues found**: X
- **Top recommendation**: [One sentence]

## Methodology
- [Method description]
- [Participant criteria]
- [Tasks tested]

## Key Findings

### Critical Issues (Fix Before Launch)
1. [Issue + Evidence + Recommendation]

### Major Issues (Next Sprint)
1. [Issue + Evidence + Recommendation]

### Minor Issues (Backlog)
1. [Issue + Evidence + Recommendation]

## What Worked Well
1. [Positive finding]

## Recommendations Summary
| Priority | Issue | Recommendation | Effort |
|----------|-------|----------------|--------|
| P0 | | | |
| P1 | | | |
| P2 | | | |

## Next Steps
- [Action items]

## Appendix
- Task success by participant
- SUS responses
- Session recordings (links)
```

### Stakeholder Presentation Checklist

- [ ] Executive summary on first slide
- [ ] Video clips prepared (3-5 key moments)
- [ ] Issues prioritized by severity
- [ ] Recommendations are specific and actionable
- [ ] Design solutions proposed (link to software-ui-ux-design patterns)
- [ ] Next steps clear
- [ ] Q&A time allocated

---

## Repository Upload

### Tagging Checklist

- [ ] Product area tagged
- [ ] Method: "Usability Testing"
- [ ] Date recorded
- [ ] Participant count
- [ ] Tasks tested listed
- [ ] Key findings summarized
- [ ] Recommendations linked to backlog items
- [ ] Video clips stored (with consent)

### Artifact Storage

| Artifact | Location | Access |
|----------|----------|--------|
| Raw recordings | [Link] | Research team |
| Transcripts (redacted) | [Link] | Research + Product |
| Analysis spreadsheet | [Link] | Research team |
| Final report | [Link] | All stakeholders |
| Video highlights | [Link] | All employees |

---

## Quality Standards

### Study Quality Checklist

- [ ] Research questions clearly stated
- [ ] Tasks realistic and unbiased
- [ ] Participant criteria documented
- [ ] Sample size justified for risk/segments
- [ ] Findings tied to evidence (quotes, timestamps)
- [ ] Recommendations actionable
- [ ] Severity ratings applied consistently
- [ ] Report uploaded within 2 weeks

### Common Pitfalls to Avoid

| Pitfall | Prevention |
|---------|------------|
| Leading questions | Use neutral language, pilot test script |
| Too many tasks | Limit to a small set of core tasks |
| Wrong participants | Rigorous screening, pilot screener |
| Observer bias | Use consistent rating criteria |
| Ignoring successes | Document what worked well |
| Vague recommendations | Tie to specific UI patterns |

---

## Optional: AI/Automation Features

> Complete this section ONLY if the product includes automation/AI-powered features.

### Scenario Coverage Checklist

- [ ] Test “good” outputs and clearly wrong outputs.
- [ ] Include “ambiguous” cases where the right answer is uncertain.
- [ ] Validate user control: edit/override/cancel.
- [ ] Validate recovery: fallback path completes the task.
- [ ] Validate feedback loops: user can report issues and see outcomes.

### Additional Metrics (If Applicable)

| Metric | What it indicates |
|--------|-------------------|
| Override rate | Users frequently correct the system |
| Verification rate | Users don’t trust outputs without checking |
| Recovery success | Users can still finish tasks after failure |

---

## References (Primary Sources)

- ISO 9241-11:2018 (usability definitions): https://www.iso.org/standard/63500.html
- ISO 9241-210:2019 (human-centred design): https://www.iso.org/standard/77520.html
