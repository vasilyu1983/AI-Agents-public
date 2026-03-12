# Agile Ceremony Patterns

> Operational reference for running effective agile ceremonies — sprint planning, standups, retrospectives, sprint reviews, backlog refinement, and PI planning. Covers facilitation techniques, timeboxing, async alternatives, and anti-patterns.

**Freshness anchor:** January 2026 — aligned with Scrum Guide 2020, SAFe 6.0, and current remote-first tooling (Linear, Jira, Miro, Notion).

---

## Ceremony Quick Reference

| Ceremony | Frequency | Timebox | Attendees | Output |
|---|---|---|---|---|
| Sprint Planning | Start of sprint | 2h (2-week sprint) | Team + PO | Sprint goal, committed backlog |
| Daily Standup | Daily | 15 min | Team | Blockers surfaced, sync |
| Sprint Review / Demo | End of sprint | 1h | Team + stakeholders | Feedback, acceptance |
| Retrospective | End of sprint | 1.5h | Team only | Action items (max 3) |
| Backlog Refinement | Mid-sprint (1-2x) | 1h | Team + PO | Estimated, ready stories |
| PI Planning | Quarterly (SAFe) | 2 days | Multiple teams | PI objectives, dependencies |

---

## Sprint Planning

### Decision Tree: Planning Approach

```
Does the team have stable velocity (>3 sprints of data)?
├── YES → Capacity-based planning
│   ├── Calculate capacity: team members × available days × focus factor
│   ├── Pull stories up to capacity from refined backlog
│   └── Commit to sprint goal, not individual stories
└── NO (new team, changing composition)
    └── Goal-based planning
        ├── Define sprint goal first
        ├── Pull minimum stories to achieve goal
        ├── Leave buffer (30-40% of estimated capacity)
        └── Track velocity to calibrate future sprints
```

### Sprint Planning Agenda

| Phase | Duration | Activity |
|---|---|---|
| 1. Context (What) | 20 min | PO presents sprint goal, top priorities, any dependencies |
| 2. Capacity check | 10 min | Team calculates available capacity (PTO, meetings, support rotation) |
| 3. Story selection (What) | 30 min | Team pulls stories from refined backlog, asks clarifying questions |
| 4. Task breakdown (How) | 45 min | Team breaks stories into tasks, identifies unknowns |
| 5. Commitment | 15 min | Team confirms sprint goal and committed scope |

### Capacity Calculation

```
Team capacity = Σ (team member available days × focus factor)

Focus factor:
- New team: 0.5-0.6
- Established team: 0.7-0.8
- Experienced team: 0.8-0.85
- Never assume 1.0

Deductions:
- PTO / holidays
- On-call / support rotation
- Company meetings / all-hands
- Onboarding new members (both mentor and mentee)
```

### Sprint Planning Checklist

- [ ] Sprint goal is a single sentence describing the outcome
- [ ] Stories are refined (acceptance criteria exist, estimated)
- [ ] Dependencies on other teams identified and communicated
- [ ] Tech debt allocation included (target 15-20% of capacity)
- [ ] Team members confirmed availability for the sprint
- [ ] No story exceeds 50% of sprint capacity (split if larger)
- [ ] Sprint goal is visible in the team's workspace

---

## Daily Standup

### Format Options

| Format | How it works | Best for |
|---|---|---|
| Three Questions | Each person: yesterday/today/blockers | Small teams (3-5), co-located |
| Walk the Board | Review tickets right-to-left on the board | Larger teams, focus on flow |
| Focus + Blockers | Each person: focus today + any blockers | Fast, outcome-oriented |
| Async Written | Written update in Slack/Linear by 10am | Distributed teams, timezone gaps |

### Walk-the-Board Protocol

```
1. Open the sprint board
2. Start from the rightmost column (closest to done)
3. For each ticket in progress:
   - Who is working on it?
   - Is it on track to move today?
   - Any blockers?
4. Skip items not started (they are the plan, not the status)
5. Flag anything at risk of not completing this sprint
```

### Async Standup Template

```markdown
## Daily Update — [Name] — [Date]

**Focus today:**
- [Primary task/ticket]
- [Secondary task if applicable]

**Blockers:**
- [Blocker description] → need [specific help from specific person]

**FYI:**
- [Optional: anything the team should know]
```

### Standup Facilitation Rules

- [ ] Start on time, every time (don't wait for latecomers)
- [ ] Standing / camera-on to maintain energy
- [ ] Timebox individual updates to 2 minutes
- [ ] Parking lot for discussions that need >30 seconds
- [ ] Rotate facilitator weekly (builds ownership)
- [ ] End with: "Who needs help today?"

---

## Retrospective

### Format Selection Guide

| Format | Best for | Duration | Energy level |
|---|---|---|---|
| Start / Stop / Continue | Quick, general health check | 45 min | Low effort |
| 4Ls (Liked, Learned, Lacked, Longed for) | Balanced reflection | 60 min | Medium |
| Mad / Sad / Glad | Emotional temperature check | 45 min | Medium |
| Sailboat (wind/anchor/rocks/island) | Visual, metaphor-driven | 60 min | High |
| Timeline | After incidents or long sprints | 90 min | High |
| Lean Coffee | Team chooses topics, democratic | 60 min | Medium |

### Retrospective Facilitation Agenda

| Phase | Duration | Activity |
|---|---|---|
| 1. Set the stage | 5 min | Check-in question, set safety |
| 2. Gather data | 15 min | Silent writing on stickies/cards |
| 3. Group and vote | 10 min | Affinity grouping, dot voting (3 votes each) |
| 4. Discuss top items | 20 min | Deep dive on top 2-3 voted topics |
| 5. Define actions | 10 min | Max 3 action items with owners and due dates |
| 6. Close | 5 min | Rate the retro (1-5), thank the team |

### Action Item Rules

- Maximum 3 action items per retro (more won't get done)
- Each action item has a single owner (not "the team")
- Each action item has a due date (default: next retro)
- Review previous retro actions at the start of each retro
- Track completion rate — if <50%, reduce to 1-2 actions

### Psychological Safety Checklist

- [ ] Vegas rule stated ("what's said here stays here")
- [ ] Facilitator is NOT the manager (rotate, or use external facilitator)
- [ ] Anonymous input option available (sticky notes, digital cards)
- [ ] No blame language ("the process failed" not "you failed")
- [ ] Manager speaks last (if present at all)
- [ ] Follow through on action items (broken trust kills future retros)

---

## Sprint Review / Demo

### Sprint Review Agenda

| Phase | Duration | Activity |
|---|---|---|
| 1. Sprint goal recap | 5 min | PO states the sprint goal and whether it was met |
| 2. Demo completed work | 30 min | Team demos working software (not slides) |
| 3. Stakeholder feedback | 15 min | Structured feedback, questions, concerns |
| 4. Backlog impact | 10 min | PO discusses how feedback affects upcoming priorities |

### Demo Preparation Checklist

- [ ] Demo environment prepared and tested before the meeting
- [ ] Demo script covers the user flow, not technical implementation
- [ ] Each demo item tied to a user story or sprint goal
- [ ] Backup plan if live demo fails (screenshots, recording)
- [ ] Non-completed items mentioned (transparency, not hidden)
- [ ] Stakeholder questions captured for backlog consideration

---

## Backlog Refinement

### Refinement Session Structure

| Phase | Duration | Activity |
|---|---|---|
| 1. Review upcoming priorities | 10 min | PO presents next sprint candidates |
| 2. Story walkthrough | 30 min | Team asks questions, clarifies acceptance criteria |
| 3. Estimation | 15 min | Team estimates using chosen method |
| 4. Ready check | 5 min | Each story passes Definition of Ready |

### Definition of Ready Checklist

- [ ] User story follows format: "As a [who], I want [what], so that [why]"
- [ ] Acceptance criteria are specific and testable
- [ ] Technical approach discussed (no unknown unknowns)
- [ ] Dependencies identified and unblocked (or plan exists)
- [ ] Story sized to complete within one sprint
- [ ] UX designs attached (if applicable)
- [ ] Edge cases documented

### Estimation Methods

| Method | How | Best for |
|---|---|---|
| Story Points (Fibonacci) | Relative sizing: 1, 2, 3, 5, 8, 13 | Teams wanting relative complexity |
| T-Shirt Sizing | XS, S, M, L, XL | Quick estimation, high-level planning |
| #NoEstimates | Count stories, assume similar size | Teams with consistently small stories |
| Time-based (hours) | Direct time estimate | Teams with predictable work types |

### Estimation Anti-Patterns

- Spending >5 minutes debating 5 vs 8 points — pick the higher one and move on
- Estimating without acceptance criteria — refuse to estimate, send back to PO
- One person dominating estimates — use simultaneous reveal (planning poker)
- Averaging estimates — discuss the gap, understand different assumptions
- Re-estimating completed stories — velocity self-corrects over time

---

## PI Planning (SAFe)

### PI Planning Agenda (2 Days)

| Day | Time | Activity |
|---|---|---|
| Day 1 AM | 2h | Business context, product vision, architecture vision |
| Day 1 PM | 3h | Team breakouts: draft PI plans, identify dependencies |
| Day 1 Close | 1h | Draft plan review, management review |
| Day 2 AM | 2h | Team breakouts: adjust plans, resolve dependencies |
| Day 2 PM | 2h | Final plan review, confidence vote, planning retrospective |

### PI Planning Outputs

- [ ] PI objectives for each team (SMART format)
- [ ] Program board showing cross-team dependencies
- [ ] Risks identified with ROAM classification (Resolved, Owned, Accepted, Mitigated)
- [ ] Confidence vote: average ≥3 out of 5 (re-plan if below)
- [ ] Uncommitted objectives clearly marked (stretch goals)

---

## Anti-Patterns

| Anti-Pattern | Ceremony | Problem | Fix |
|---|---|---|---|
| Status report standup | Daily | Manager asks for updates, not team sync | Use walk-the-board, rotate facilitator |
| Sprint planning = story assignment | Planning | No team ownership of commitment | Team pulls work, self-assigns during sprint |
| Skipping retros when "things are fine" | Retro | Missed improvement opportunities, stagnation | Always run retros, vary the format |
| Demo with slides, no working software | Review | Stakeholders can't give meaningful feedback | Demo real features in test environment |
| Refinement = estimation only | Refinement | Stories enter sprint with unclear requirements | Focus on understanding and acceptance criteria first |
| Sprint goal is a list of tickets | Planning | No cohesion, can't make scope tradeoffs | Sprint goal is one sentence, an outcome |
| Same retro format every time | Retro | Team disengages, goes through the motions | Rotate formats quarterly |
| No action item follow-through | Retro | Team stops raising issues, learned helplessness | Review actions at start of every retro |
| 60-minute standup | Daily | Problem-solving in standup instead of parking lot | Strict 15-min timebox, take topics offline |
| Inviting everyone to every ceremony | All | Decision paralysis, wasted time | Core team only; stakeholders to review/demo |

---

## Cross-References

- `dev-workflow-planning/references/technical-debt-management.md` — allocating debt work in sprint planning
- `dev-workflow-planning/references/remote-async-workflows.md` — async alternatives to ceremonies
- `startup-hiring-and-management/references/remote-team-management.md` — managing distributed agile teams
- `qa-testing-strategy/SKILL.md` — integrating testing into sprint workflow
- `software-architecture-design/SKILL.md` — architecture decisions in refinement
