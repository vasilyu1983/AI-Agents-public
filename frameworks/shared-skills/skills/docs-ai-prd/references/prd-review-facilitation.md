# PRD Review Facilitation

*Purpose: Operational guide for running effective PRD reviews -- choosing the right format, structuring feedback, managing iteration cycles, and avoiding common review dysfunction.*

## Contents

- Review types and format selection
- Agenda template and feedback labels
- Iteration workflow and tools
- Measuring effectiveness
- Anti-patterns

---

## Review Types

### Decision Guide

| Type | Duration | Best For | Participants |
|------|----------|----------|--------------|
| Async comment | 0 (async) | Minor updates, focused sections, final polish | 2-4 targeted reviewers |
| Live walkthrough | 30-45 min | New PRD first read, complex domain, many open questions | Full review group (5-8) |
| Structured critique | 60 min | Contentious scope, cross-team dependencies, architectural decisions | Decision-makers + domain experts |
| Silent read + discuss | 15 min read + 30 min discuss | Amazon-style; eliminates presenter bias | Any size group |

### Choosing a Format

```text
Is this the first review of a new PRD?
  -> Yes: Live walkthrough or silent-read + discuss
  -> No: Has feedback from the last round been resolved?
    -> No: Async comment (reviewers verify fixes)
    -> Yes: Are there unresolved conflicts or scope debates?
      -> Yes: Structured critique
      -> No: Async sign-off with deadline
```

---

## Review Agenda Template

**Use for live walkthroughs and structured critiques.**

1. Context and scope (5 min) -- What changed since last version
2. Open questions walkthrough (10 min) -- Items tagged `[OPEN]`
3. Section-by-section feedback (15-30 min) -- Facilitator time-boxes each section
4. Blockers and decisions (5-10 min) -- Items that need resolution before next step
5. Action items and next steps (5 min) -- Who does what by when

**Ground rules:** Label feedback (BLOCKER/QUESTION/SUGGESTION/NITPICK). One speaker at a time. No solutioning during review. Silence does not equal approval.

---

## Feedback Categorization

### Labels

| Label | Meaning | Response Required | Blocks Approval |
|-------|---------|:-----------------:|:---------------:|
| **BLOCKER** | Incorrect, unsafe, or missing critical requirement | Yes -- must resolve | Yes |
| **QUESTION** | Unclear intent or missing context; needs clarification | Yes -- must answer | Maybe |
| **SUGGESTION** | Improvement idea; take-it-or-leave-it | Acknowledge | No |
| **NITPICK** | Style, formatting, minor wording | Optional | No |

### Usage Examples

- `[BLOCKER] PRD specifies OAuth2 but target system only supports SAML. Requires different auth integration.`
- `[QUESTION] "Real-time updates" -- WebSocket push or polling <5s? Infrastructure differs.`
- `[SUGGESTION] Add rate-limit section. Not MVP but avoids redesign at scale.`
- `[NITPICK] Typo: "recieve" -> "receive"`

**Rules:**
- Every comment must have a label. Unlabeled feedback is triaged last.
- BLOCKERs must include a reason and (ideally) a proposed resolution.
- PM must respond to every BLOCKER and QUESTION before the next review round.

---

## Iteration Workflow

**Flow:** Draft v0.1 -> Review Round 1 -> Revise -> Review Round 2 -> Approve

### Iteration Rules

- **Maximum 3 review rounds.** If not converging, escalate to decision-maker.
- **Each revision must include a changelog** at the top: what changed, what was deferred, what was rejected and why.
- **Scope freeze after Round 2.** New requirements discovered in Round 3 go to a follow-up PRD.
- **Version the document.** Use v0.1, v0.2, v1.0 (approved). Never overwrite without version bump.

### Changelog Format

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| v0.3 | 2025-04-10 | Resolved auth BLOCKER: switched to SAML | @pm |
| v0.2 | 2025-04-07 | Clarified "real-time" definition | @pm |
| v0.1 | 2025-04-03 | Initial draft for review | @pm |

---

## Tools and Platforms

| Platform | Strengths | Review Pattern |
|----------|-----------|----------------|
| Google Docs | Inline comments, suggestion mode, real-time collab | Async comment, live walkthrough |
| Notion | Structured pages, inline comments, status properties | Async comment, sign-off checklists |
| GitHub PR (markdown) | Version control, diff view, required reviewers | Async comment, approval gates |
| Linear / Jira | Links to implementation tickets, status tracking | Post-approval handoff, traceability |
| Confluence | Enterprise wiki, page approval workflows | Async comment, formal sign-off |

### Platform Selection

```text
Is the PRD in version control (engineers are primary audience)?
  -> Yes: GitHub PR with markdown file
  -> No: Is real-time co-editing needed?
    -> Yes: Google Docs or Notion
    -> No: Notion or Confluence (structured, async-first)
```

---

## Measuring Review Effectiveness

| Metric | Target | Signal |
|--------|--------|--------|
| Rounds to approval | <= 3 | Higher = weak first drafts or unclear scope |
| BLOCKER resolution time | < 48h | Slow = missing decision-maker or escalation path |
| Review turnaround | < 48h per round | Slow = review fatigue or wrong reviewers |
| Post-approval change rate | < 10% | High = inadequate review or scope creep |
| Reviewer participation | 100% of Consulted | Low = ghost reviewers or irrelevant assignments |

### Quarterly Health Check

- [ ] Average rounds-to-approval stable or decreasing
- [ ] No PRDs stuck in review > 2 weeks
- [ ] All Consulted reviewers participating

---

## Anti-Patterns

AVOID: **Review fatigue** -- Sending PRDs for review every other day; reviewers stop reading carefully.
FIX: Batch reviews. Send for review when a full draft is ready, not after every paragraph change.

AVOID: **Rubber-stamping** -- Approving without reading due to short window or long doc.
FIX: Set realistic deadlines (48h minimum). Highlight sections that need the most scrutiny.

AVOID: **Review-as-design** -- Brainstorming solutions instead of evaluating the spec.
FIX: Separate design from review. Log new ideas and schedule a follow-up session.

AVOID: **Endless iteration** -- Four or more rounds with diminishing returns.
FIX: Cap at 3 rounds. After Round 3, decision-maker approves with noted risks or kills the PRD.

AVOID: **Ghost reviewers** -- People on the list who never comment.
FIX: Require explicit "no objections" or "approved" from every Consulted reviewer.

AVOID: **BLOCKER inflation** -- Labeling everything as BLOCKER to get attention.
FIX: Define BLOCKER criteria upfront: "Would this cause a production incident or require re-architecture?"

---

## Related Resources

- [Stakeholder Alignment](stakeholder-alignment.md) -- RACI, conflict resolution, escalation paths
- [Acceptance Criteria Patterns](acceptance-criteria-patterns.md) -- Writing testable ACs for PRD requirements
- [Requirements Checklists](requirements-checklists.md) -- PRD completeness validation
- [Traditional PRD Writing Guide](traditional-prd-writing.md) -- PRD structure and best practices
