# UX Audit Framework

Expert-review methods from the research side: when an expert review is enough and when it is not, the cognitive walkthrough protocol, and a severity model tied to evidence. The heuristic checklists, design-quality dimensions and UI polish loops belong to the design skill: [nielsen-heuristics.md](../../software-ui-ux-design/references/nielsen-heuristics.md) (heuristics and severity rubric) and [ui-quality-priority-rules.md](../../software-ui-ux-design/references/ui-quality-priority-rules.md) (priority-ordered audit dimensions). Conformance audits belong to [software-accessibility](../../software-accessibility/SKILL.md). Report template: [assets/audits/ux-audit-report-template.md](../assets/audits/ux-audit-report-template.md).

---
## Table of Contents

- [Expert Review or User Research?](#expert-review-or-user-research)
- [Cognitive Walkthrough Protocol](#cognitive-walkthrough-protocol)
- [Severity Rating System](#severity-rating-system)
- [Synthesis: Clustering and Root Cause](#synthesis-clustering-and-root-cause)

---

## Expert Review or User Research?

| Method | Focus | Best for | Blind spot |
|--------|-------|----------|------------|
| Heuristic evaluation | Expert review against principles | Fast baseline, limited budget | Domain comprehension, real mental models |
| Cognitive walkthrough | Step-by-step learnability of one task | Critical first-use flows | Expert and repeat-use efficiency |
| Accessibility audit | WCAG conformance | Legal exposure, inclusion | Usability for assistive-technology users (needs AT users in sessions) |
| Competitive audit | Comparison with competitors | Positioning, gap finding | Whether the gap matters to your users ([competitive-ux-analysis.md](competitive-ux-analysis.md)) |

Rules:
- Use expert review to find and fix obvious problems *before* spending participant time, not as a substitute for testing when task comprehension, domain literacy or trust is the core risk.
- Use three to five independent evaluators and merge findings; a single evaluator misses many problems and over-weights their own taste.
- Label expert-review findings as predictions. Promote them to findings only when a usability session, analytics or support data confirms them.

## Cognitive Walkthrough Protocol

Walk through a task as a specific first-time user would, and ask four questions at every action:

1. **Will users try to achieve the right effect?** Is the goal of this step clear to them?
2. **Will users notice the correct action is available?** Is it visible and clearly labelled?
3. **Will users associate the action with the effect they want?** Do the label and affordance match their expectations?
4. **Will users interpret the feedback correctly?** Is success or failure clear, and is the next step obvious?

Process: define the user profile and realistic task scenarios, break each task into discrete actions, answer the four questions per action, then group issues and assign severity.

```text
Task: [Create new project]    User: [First-time user, technical background]

| Step | Action               | Q1 Goal | Q2 Visible | Q3 Association | Q4 Feedback           | Severity |
|------|----------------------|---------|------------|----------------|-----------------------|----------|
| 1    | Click "New"          | Yes     | Yes        | Yes            | Partial: modal unclear | 2        |
| 2    | Select template      | No: unclear it is required | Yes | Partial | Yes           | 4        |
```

## Severity Rating System

| Level | Name | Definition | Evidence bar |
|-------|------|------------|--------------|
| 0 | Not a problem | Preference only | n/a |
| 1 | Cosmetic | Visual or convention deviation, no task impact | Observation |
| 2 | Minor | Slows users or degrades trust; workaround exists | Guideline breach with plausible user cost |
| 3 | Major | Errors, abandonment or repeated friction on a core path | Observed failure, or breach on a high-priority dimension |
| 4 | Critical | Task failure, data loss, security exposure, or excludes an assistive-technology user | Reproduced blocker or WCAG failure on a core task |

Cap any finding without observed-user, data or standards evidence at level 2. Expert opinion alone never yields a Critical.

Frequency x impact, when observation data exists (bands are a team convention; set and record your own):

```text
Frequency: affects few = 1, some = 2, most = 3 users on the path
Impact:    annoyance = 1, delayed with workaround = 2, blocked = 3
Score 2-3 = Cosmetic/Minor, 4 = Major, 5-6 = Critical
```

## Synthesis: Clustering and Root Cause

- Report findings grouped by theme or dimension, not screen by screen; page-by-page lists hide systemic failures (for example, every form validating on keystroke).
- For each Major or Critical cluster, ask "why" until you reach a cause the team can act on (missing error mapping, a component default, a content process), and recommend the fix at that level.
- State current vs expected state with the evidence for "expected" (a usability benchmark, a competitor measurement, or a standard), not a guess.
