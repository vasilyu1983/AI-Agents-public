# Remote Async-First Workflows

> Operational reference for running async-first development workflows — documentation-driven development, RFC/ADR decision processes, async standups, distributed team coordination, meeting minimization, and async retrospectives.

**Freshness anchor:** January 2026 — aligned with current tooling: Linear, Notion, Loom, Slack workflows, GitHub Discussions, and async-first practices from GitLab, Doist, and Basecamp.

---

## Async vs Sync Decision Tree

```
Does this need to happen in real-time?
├── YES (requires sync)
│   ├── Incident response / live debugging
│   ├── Sensitive feedback (performance reviews, conflict resolution)
│   ├── Complex negotiation with high ambiguity
│   ├── Team bonding / social connection
│   └── Brainstorming requiring rapid iteration (timebox to 30 min)
└── NO (default to async)
    ├── Status updates → Written standup
    ├── Code review → PR comments
    ├── Design decisions → RFC document
    ├── Knowledge sharing → Loom video or written doc
    ├── Sprint planning → Pre-populated board + async review
    ├── Retrospective → Async collection + optional short sync discussion
    └── Announcements → Written post with Q&A thread
```

### Meeting Necessity Checklist

Before scheduling a meeting, verify:

- [ ] Could this be a document? (default: yes)
- [ ] Could this be a Loom video? (for demos, walkthroughs)
- [ ] Could this be a Slack thread? (for quick decisions)
- [ ] Does this require back-and-forth discussion that would take >10 async messages?
- [ ] Are all required participants in overlapping timezone hours?
- [ ] Is the outcome clearly defined (not "discuss X")?

If all answers favor async, do not schedule a meeting.

---

## Documentation-Driven Development

### Core Principle

> Write the document before writing the code. If you can't explain it in writing, you don't understand it well enough to build it.

### Document-First Workflow

```
1. Write the RFC/design doc
   └── Describe: problem, proposed solution, alternatives, risks

2. Share for async review
   └── Set review deadline (48-72 hours)
   └── Tag specific reviewers, not "everyone"

3. Collect feedback
   └── Reviewers comment directly on the document
   └── Author responds to all comments

4. Decide
   └── Author summarizes decision and rationale
   └── Escalate unresolved disagreements to a short sync call

5. Build
   └── Reference the RFC in all related PRs
   └── Update the doc if implementation deviates

6. Archive
   └── Mark as "Implemented" with link to final PR/deployment
```

### RFC (Request for Comments) Template

```markdown
# RFC: [Title]

**Author:** [name]
**Status:** Draft | In Review | Accepted | Rejected | Implemented
**Created:** 2026-01-15
**Review deadline:** 2026-01-18
**Reviewers:** @person1, @person2, @person3

## Problem Statement
- [1-3 bullet points describing the problem]
- [Quantify impact if possible]

## Proposed Solution
- [Description of the approach]
- [Key design decisions and their rationale]

## Alternatives Considered
| Alternative | Pros | Cons | Why not chosen |
|---|---|---|---|
| [Option A] | [pros] | [cons] | [reason] |
| [Option B] | [pros] | [cons] | [reason] |

## Technical Design
- [Architecture diagram or description]
- [API contracts or data models]
- [Migration plan if applicable]

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [risk] | [H/M/L] | [H/M/L] | [plan] |

## Rollout Plan
- [ ] Phase 1: [what, when]
- [ ] Phase 2: [what, when]
- [ ] Rollback plan: [how]

## Open Questions
- [ ] [Question 1] — @person to answer
- [ ] [Question 2] — needs investigation

## Decision Log
- [Date]: [Decision made and rationale]
```

### ADR (Architecture Decision Record) Template

```markdown
# ADR-NNN: [Short title of decision]

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXX
**Date:** 2026-01-15
**Deciders:** [names]

## Context
- [What forces are at play]
- [Why a decision is needed now]

## Decision
- [What we decided]

## Consequences
- [Positive outcomes]
- [Negative outcomes and tradeoffs]
- [Follow-up actions needed]
```

### ADR Management Rules

- [ ] ADRs are numbered sequentially (ADR-001, ADR-002, ...)
- [ ] ADRs are stored in `docs/adr/` or `docs/decisions/`
- [ ] ADRs are never deleted — superseded ADRs link to the replacement
- [ ] ADRs are referenced in related PRs and code comments
- [ ] Quarterly review of recent ADRs to verify decisions still hold

---

## Async Standup Patterns

### Written Standup (Slack/Linear)

**Schedule:** Post by team's latest timezone 10:00 AM local time.

```markdown
## Standup — [Name] — 2026-01-15

**Completed yesterday:**
- [PROJ-123] Finished API endpoint for user search
- Code review on [PROJ-145]

**Focus today:**
- [PROJ-130] Implement pagination for search results
- Pair with @sarah on auth integration (scheduled 2pm UTC)

**Blockers:**
- Waiting on design review for [PROJ-135] — @designer ETA?

**FYI:**
- Out tomorrow afternoon (dentist appointment)
```

### Loom Video Standup

**Use when:**

- Demonstrating visual work (UI, design, dashboards)
- Explaining complex technical context
- Team prefers face-to-face but timezones prevent it

**Format:**

- Maximum 3 minutes per person
- Screen share optional (show code, UI, or board)
- Post in dedicated Slack channel with timestamp summary
- Viewers watch at 1.5x speed, comment in thread

### Standup Bot Configuration

| Tool | Setup | Features |
|---|---|---|
| Geekbot (Slack) | `/geekbot` setup | Scheduled prompts, thread collection, analytics |
| Linear Standup | Built-in | Pulls from ticket activity, auto-generates |
| Slack Workflow | Workflow Builder | Custom questions, scheduled triggers |
| Notion Standup DB | Template database | Structured entries, rollup views |

### Async Standup Rules

- [ ] Post window defined (e.g., within first 2 hours of your workday)
- [ ] Blockers get immediate attention (don't wait for someone to read)
- [ ] Tag specific people when you need something from them
- [ ] Link to tickets/PRs rather than describing them
- [ ] Read and react to teammates' standups within 4 hours
- [ ] Weekly summary auto-generated from daily posts

---

## Timezone-Distributed Coordination

### Overlap Windows Strategy

```
Team across US Pacific, US Eastern, UK, India:

PST:    06:00 ████████████████████ 22:00
EST:    09:00 ████████████████████ 01:00
GMT:    14:00 ████████████████████ 06:00
IST:    19:30 ████████████████████ 11:30

Overlap (all four): NONE
Overlap (PST+EST+GMT): 14:00-17:00 GMT (06:00-09:00 PST)
Overlap (EST+GMT+IST): 14:00-17:30 GMT (19:30-23:00 IST)
```

### Coordination Patterns by Timezone Gap

| Gap | Pattern | Example |
|---|---|---|
| 0-3 hours | Near-sync, overlap meetings ok | US East + US West |
| 4-6 hours | Async-default, 1-2 overlap hours for sync | US East + UK |
| 7-10 hours | Async-first, intentional handoff docs | US West + India |
| 11+ hours | Follow-the-sun, relay-style handoff | US West + Australia |

### Handoff Document Template

```markdown
## End-of-Day Handoff — [Name] — 2026-01-15

**What I worked on:**
- [PROJ-123] — Status: In Review, PR #456
- [PROJ-130] — Status: Blocked (see below)

**Needs attention from next timezone:**
- PR #456 needs review — context: [brief explanation]
- [PROJ-130] blocked on API response from third-party — if response arrives, proceed with [specific instructions]

**Decisions made today:**
- Chose approach B for caching (see RFC-015 comment thread)

**Don't touch:**
- [PROJ-140] — waiting for design, do not start implementation
```

### Distributed Team Checklist

- [ ] Core hours defined for each timezone pairing (not one global core hour)
- [ ] No meetings outside anyone's 8am-6pm local time
- [ ] Meeting recordings posted with timestamps for key decisions
- [ ] Shared calendar shows each person's working hours
- [ ] Decision-making defaults to async with 48h response window
- [ ] Urgent escalation path defined (and rarely used)

---

## Tool Configuration

### Communication Layer Map

| Purpose | Tool | Async/Sync | Response Expectation |
|---|---|---|---|
| Quick questions | Slack (channel) | Async | Within 4 hours |
| Urgent/incident | Slack (DM or @channel) | Near-sync | Within 30 min |
| Decisions | RFC/ADR (Notion, GitHub) | Async | Within 48-72 hours |
| Status updates | Standup bot (Geekbot, Slack) | Async | Daily |
| Deep discussion | Document comments (Notion, Google Docs) | Async | Within 48 hours |
| Code review | PR comments (GitHub, GitLab) | Async | Within 24 hours |
| Demo / walkthrough | Loom video | Async | Watch within 24 hours |
| Brainstorming | Sync call or FigJam/Miro | Sync | Scheduled |
| Social / bonding | Optional video call | Sync | Voluntary |

### Slack Configuration for Async

- [ ] Channel naming convention: `#team-[name]`, `#proj-[name]`, `#standup-[name]`
- [ ] Notification schedule set per timezone (no pings outside work hours)
- [ ] Threads used for all replies (not top-level messages)
- [ ] Important decisions summarized in a pinned message or doc (not buried in Slack)
- [ ] "Do not disturb" hours configured for each timezone
- [ ] Weekly digest of key decisions posted to `#team-[name]-decisions`

### Linear/Jira Async Workflow

- [ ] Ticket status changes trigger Slack notifications to project channel
- [ ] Comments on tickets preferred over Slack for project discussion (searchable, permanent)
- [ ] Sprint board visible to all (no access gatekeeping)
- [ ] Automated weekly velocity/burndown report posted to channel

---

## Async Retrospectives

### Async Retro Process

```
Day 1-3: Collection Phase
├── Retro board open (Miro, EasyRetro, Notion)
├── Team members add cards at their own pace
├── Categories: What went well | What didn't | Ideas for improvement
└── Encouraged: 3+ cards per person minimum

Day 4: Voting Phase (async)
├── Each person gets 3-5 votes
├── Vote on cards across all categories
└── Deadline: end of day

Day 5: Discussion + Actions
├── Option A: Short sync call (30 min) to discuss top 3 voted items
├── Option B: Facilitator writes summary, proposes actions in document
│   └── Team has 24h to comment/adjust
└── Output: Max 3 action items with owners and due dates
```

### When to Use Sync vs Async Retro

| Factor | Async Retro | Sync Retro |
|---|---|---|
| Timezone spread | >6 hours | <4 hours |
| Team size | >8 people | 3-7 people |
| Psychological safety | High (established team) | Building (new team) |
| Sprint outcome | Normal | After incident or major failure |
| Team energy | Meeting fatigue is high | Team wants face time |

---

## Meeting Minimization Strategies

### Meeting Audit Process

```
1. List all recurring meetings for the team
2. For each meeting, answer:
   ├── What decision or outcome does this produce?
   ├── Could this outcome be achieved async?
   ├── Who actually needs to attend (vs who is invited)?
   └── What is the cost? (attendees × duration × hourly rate)
3. Categorize:
   ├── KEEP: Clear outcome, requires sync, right attendees
   ├── SHORTEN: Outcome ok, but meeting is too long
   ├── CONVERT: Can be done async (document, Loom, Slack)
   └── KILL: No clear outcome, habit meeting
4. Implement changes, review in 4 weeks
```

### Meeting Replacement Patterns

| Meeting Type | Async Replacement |
|---|---|
| Status update | Written standup or dashboard |
| Knowledge share | Loom video or written guide |
| Design review | RFC document with comment period |
| Sprint planning | Pre-populated board + async confirmation |
| Demo | Recorded Loom + feedback form |
| All-hands | Written update + AMA thread |
| 1:1 (some) | Async check-in document + sync when needed |

### Meeting Rules for Async-First Teams

- [ ] Default meeting length: 25 minutes (not 30), 50 minutes (not 60)
- [ ] Every meeting has an agenda shared 24h in advance
- [ ] No agenda, no meeting (attendees can decline)
- [ ] Meetings produce a written summary within 1 hour (not 1 day)
- [ ] Recordings available for all meetings (async participants)
- [ ] "No meeting" days: Tuesday and Thursday (or team's choice)
- [ ] Meeting-free weeks once per quarter (deep work focus)

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| "Quick call" for every question | Interrupts deep work, timezone-excluding | Post in Slack with 4-hour response expectation |
| No written record of sync meetings | Decisions lost, absent members uninformed | Written summary required within 1 hour of every meeting |
| Slack as source of truth | Important context buried in scrollback | Decisions go in docs/tickets; Slack is ephemeral |
| Async but no response SLA | Messages ignored for days, async breaks down | Define and enforce response windows per channel type |
| Forcing sync across 12+ hour timezone gap | Unsustainable for someone (always early/late) | Rotate meeting times or go fully async |
| Document everything, read nothing | Information overload, nobody reads | Summarize, use structured templates, limit length |
| No social connection | Team feels isolated, trust erodes | Optional social calls, virtual coffee, team channels |
| Async standup becomes a chore | Low-effort copy-paste updates | Rotate format, add "FYI" and "appreciation" sections |
| Over-indexing on tools | Tool switching overhead, context fragmentation | Consolidate: one project tool, one docs tool, one chat tool |
| No escalation path for urgent items | Async response times block critical work | Define "urgent" criteria and direct-message protocol |

---

## Cross-References

- `dev-workflow-planning/references/agile-ceremony-patterns.md` — ceremony formats including async variants
- `dev-workflow-planning/references/technical-debt-management.md` — tracking debt decisions via ADRs
- `startup-hiring-and-management/references/remote-team-management.md` — broader remote team management
- `startup-hiring-and-management/references/culture-and-values-design.md` — async culture design
- `startup-hiring-and-management/references/founder-delegation-patterns.md` — delegation in async environments
