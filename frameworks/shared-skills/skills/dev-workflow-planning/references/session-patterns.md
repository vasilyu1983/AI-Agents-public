# Session Patterns

Patterns for managing multi-session projects with a coding assistant.

---

## The Session Lifecycle

```text
SESSION START
1. Load context (project memory, previous session notes)
2. Review current plan status
3. Identify today's goal

ACTIVE WORK
- Execute plan steps
- Track progress visibly
- Checkpoint at milestones

SESSION END
1. Summarize completed work
2. Document decisions made
3. Capture context for next session
4. Update project memory if needed
```

---

## Pattern 1: Context Handoff

**Problem**: The assistant loses context between sessions. How do you maintain continuity?

**Solution**: Use structured session summaries stored in a project memory file (e.g., `CLAUDE.md`, `AGENTS.md`) or a dedicated `session-notes.md`.

```markdown
## Session Summary: [Date]

### Completed
- [x] Implemented user authentication API
- [x] Added JWT token generation
- [x] Created login/logout endpoints

### In Progress
- [ ] Frontend login form (50% done, form exists, validation pending)

### Decisions Made
1. Using JWT over sessions for stateless auth
2. Token expiry set to 24 hours
3. Refresh tokens stored in httpOnly cookies

### Blockers
- Need design review for password reset flow

### Next Session: Start Here
1. Complete login form validation
2. Add error handling for auth failures
3. Implement "remember me" checkbox

### Files Modified
- src/auth/jwt.ts (new)
- src/api/routes/auth.ts (new)
- src/middleware/authenticate.ts (new)
```

---

## Pattern 2: Checkpoint Recovery

**Problem**: Session interrupted mid-task. How do you resume safely?

**Solution**: Frequent micro-checkpoints during complex work.

```text
/checkpoint [after each significant action]

CHECKPOINT FORMAT:
================
Time: [timestamp]
Last Action: [what was just completed]
Current State: [what exists now]
Next Action: [what comes next]
Rollback Point: [how to undo if needed]
================

Example:
================
Time: 14:32
Last Action: Created database migration for users table
Current State: Migration file exists, not yet applied
Next Action: Run migration, then create User model
Rollback Point: Delete migration file, no DB changes yet
================
```

---

## Pattern 3: Multi-Day Project Tracking

**Problem**: Large projects span many sessions. How do you track overall progress?

**Solution**: Maintain a project status file updated each session.

```markdown
# Project: [Name]

## Overall Progress
Progress: 40% complete

## Milestones
- [x] M1: Project setup and scaffolding (Day 1)
- [x] M2: Database schema and models (Day 2)
- [CURRENT] M3: API endpoints (Day 3-4)
- [ ] M4: Frontend integration (Day 5-6)
- [ ] M5: Testing and polish (Day 7)

## Session Log
| Date | Focus | Outcome |
|------|-------|---------|
| Dec 1 | Setup | Project scaffolded, deps installed |
| Dec 2 | Models | 5 models created, migrations run |
| Dec 3 | API | 3/8 endpoints done |

## Current Sprint
Focus: Complete API endpoints

Tasks:
- [x] GET /users
- [x] POST /users
- [x] GET /users/:id
- [ ] PUT /users/:id
- [ ] DELETE /users/:id
- [ ] GET /posts
- [ ] POST /posts
- [ ] GET /posts/:id

## Blockers Log
| Date | Blocker | Resolution |
|------|---------|------------|
| Dec 2 | DB connection issues | Fixed .env config |
```

---

## Pattern 4: Decision Log

**Problem**: Forgetting why decisions were made leads to revisiting them.

**Solution**: Maintain an append-only decision log.

```markdown
# Decision Log

## DEC-001: Authentication Method
**Date**: 2024-12-01
**Decision**: Use JWT tokens over server-side sessions
**Context**: Building stateless API for mobile app
**Alternatives Considered**:
- Sessions: Simpler but requires sticky sessions
- OAuth only: Too complex for MVP
**Rationale**: JWT allows horizontal scaling, mobile-friendly
**Consequences**: Need token refresh logic, secure storage on client

## DEC-002: Database Choice
**Date**: 2024-12-01
**Decision**: PostgreSQL over MongoDB
**Context**: Relational data with complex queries needed
**Rationale**: Strong consistency, better for financial data
**Consequences**: Need to design schema upfront

## DEC-003: [Next Decision]
...
```

---

## Pattern 5: Context Window Management

**Problem**: Long sessions fill context window, degrading performance.

**Solution**: If your platform supports clearing/compacting context, use it intentionally with preserved context.

```text
CONTEXT MANAGEMENT WORKFLOW:

1. Before clearing, extract critical context:
   /summarize -> Save to session-notes.md

2. Clear context:
   /clear

3. Reload essential context:
   "Read project memory and session-notes.md, then continue with [task]"

WHEN TO CLEAR:
- Switching to unrelated task
- After completing major milestone
- When responses slow down
- After ~50+ back-and-forth messages

WHAT TO PRESERVE:
- Current plan and progress
- Recent decisions
- Active file paths
- Uncommitted changes
```

---

## Pattern 6: Parallel Workstreams

**Problem**: Multiple features in progress simultaneously.

**Solution**: Track workstreams separately with clear boundaries.

```markdown
# Active Workstreams

## Workstream A: Authentication
Status: [YELLOW] In Progress (70%)
Branch: feature/auth
Last Updated: Dec 3
Next Action: Implement password reset

## Workstream B: Dashboard UI
Status: [GREEN] Ready for Review
Branch: feature/dashboard
Last Updated: Dec 2
Next Action: Awaiting design approval

## Workstream C: API Rate Limiting
Status: [RED] Blocked
Branch: feature/rate-limit
Blocker: Need Redis setup in staging
Next Action: Wait for DevOps

---

## Today's Focus: Workstream A
[Detailed tasks for current session]
```

---

## Anti-Patterns to Avoid

### 1. Context Hoarding
**Bad**: Never clearing context, hoping the assistant remembers everything
**Good**: Regular summarize -> clear -> reload cycles

### 2. No Checkpoints
**Bad**: Working for hours without saving progress
**Good**: Checkpoint after each completed step

### 3. Vague Handoffs
**Bad**: "Continue where we left off"
**Good**: "Read session-notes.md, we're on Step 3 of the auth implementation"

### 4. Decision Amnesia
**Bad**: Rediscussing the same choices each session
**Good**: Reference decision log: "Per DEC-001, we're using JWT"

---

## Quick Reference Commands

```text
/session-start [project]  -> Load context, show status
/checkpoint               -> Save current progress
/summarize                -> Generate session summary
/clear                    -> Reset context (after summarize!)
/status                   -> Show project progress
```

---

---

## Lessons from Production (Feb 2026)

Evidence from real coding sessions showing what works and what fails at scale.

### Context Exhaustion Is the Dominant Constraint

A single session covering 5 workstreams (i18n, auth, products, retention, docs) ran to 121MB / 33 context continuations. Each continuation lost detail from prior context, causing repeated investigation of known failures, redundant file reads, and solutions contradicting earlier decisions.

**Rule: One feature per session.** If scope creep appears during execution, checkpoint and start a fresh session for the new scope.

| Session Style | Messages | Context Continuations | Errors | Outcome |
|--------------|----------|----------------------|--------|---------|
| Focused (chart gating) | 5 | 0 | 0 | Clean, zero rework |
| Medium (crush UI + BirthTimeInput) | 8 | 0 | 1 rewrite | Good after UX audit |
| Sprawling (3D + retention + quota + crush + i18n + docs) | 38 | 3+ | Multiple | Several errors, context loss |
| Massive (full redesign implementation) | 100+ | 33 | Many | Completed but costly |

### Pre-Written Plans Eliminate Rework

Sessions with pre-written, numbered step plans had near-zero rework:
- Docs actualization (11 steps, 10 files): zero rework, linear execution
- i18n refactor (5 phases, 7 tasks): systematic, minimal rework

Sessions without plans had 1-3 rewrites (e.g., BirthTimeInput: v1 → v2 after UX skill audit).

**Rule:** For any task touching 3+ files, write a plan first with:
1. Numbered steps with specific file paths
2. Verification criteria per step
3. Dependencies between steps

### Checkpoint Protocol for Long Sessions

If a session must span multiple features:
1. After completing each feature, summarize: what changed, what was verified, what's pending
2. Commit completed work before starting next feature
3. If context starts feeling thin (repeating file reads, losing track of changes), start a new session
4. Transfer context via a written summary in the plan file, not by relying on conversation history

### Proactive Plan-Doc Reading

Before implementing any feature step:
1. Check if a plan/spec doc exists for the current feature.
2. Read the relevant section of the plan before writing code.
3. Do not rely on user to paste plan context — proactively find and load it.

This prevents building features that contradict the agreed plan or miss requirements documented elsewhere.

---

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Planning Templates](planning-templates.md)
