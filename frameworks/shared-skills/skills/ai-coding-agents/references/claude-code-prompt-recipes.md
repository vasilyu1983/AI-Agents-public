# Claude Code Prompt Recipes

## Table of Contents

- [Session Setup](#session-setup)
- [Patterns](#patterns)
- [Planning & Architecture](#planning--architecture)
- [Reference & Context](#reference--context)
- [Execution Discipline](#execution-discipline)
- [Review & Verification](#review--verification)
- [Debug & Recovery](#debug--recovery)
- [Checkpoint Hygiene](#checkpoint-hygiene)
- [Dependency & Release](#dependency--release)
- [Session Economics](#session-economics)
- [Setup Sequence for a New Project](#setup-sequence-for-a-new-project)
- [See Also](#see-also)

A catalog of named prompt patterns for Claude Code sessions. These are **prompt shapes**, not agent definitions — use them inside any session to steer a specific outcome. For building agents themselves, see [`creation-workflow.md`](creation-workflow.md).

Each recipe lists the shape, when to use it, and the failure it prevents.

## Session Setup

### R1. Init Project Context
```
/init
```
Scans the codebase and generates `CLAUDE.md` (project structure, tech stack, patterns, key architecture). Run once per new repo. Claude re-reads it every future session.

### R2. Persistent Rule
```
/memory
> Always use TypeScript strict mode.
> Always add JSDoc to exported functions.
> Always run `pnpm test` after modifying files under src/core.
```
Persists across all future sessions without re-stating. Use for rules that apply to **every** prompt.

### R3. Pattern Enforcer (inside `CLAUDE.md`)
```markdown
## Patterns
- API routes follow src/api/example-route.ts
- DB queries use the repository pattern in src/repositories/example-repo.ts
- React components follow src/components/ExampleComponent.tsx
```
Anchors new files to reference implementations. Matches house style automatically.

## Planning & Architecture

### R4. Plan Mode First
`Shift + Tab` into plan mode **before** any implementation. Claude analyses, proposes architecture, writes no code. Approve, then switch to implementation.

Prevents wasted code on the wrong approach. The highest-leverage habit for non-trivial work.

### R5. Architecture Audit
```
Analyse my project requirements: {list}.
Propose 2 architectural approaches. For each: component diagram,
pros, cons, estimated complexity, failure modes.
Recommend one with reasoning.
```
Use at project start and before any major refactor.

### R6. Refactoring Planner
```
Read {file}. It has grown to {N} lines and handles too many responsibilities.
Propose a refactoring plan: new file structure, what moves where, verify
no external imports break. Do NOT start refactoring — show the plan only.
```
The "plan only" clause is load-bearing. Without it Claude will dive in.

### R7. Migration Builder
```
I need to change {schema change}. Generate the migration, update the
repository layer, update every API route that references the old schema,
update TypeScript types. Show me every file that needs to change before
making any modifications.
```
Catches ripple effects at planning time, not discovery time.

## Reference & Context

### R8. Reference File Technique
```
Look at how {feature} is implemented in {path/to/reference.ts}.
Implement {new feature} following the exact same patterns.
```
Point to a file instead of describing style. Produces far more consistent code than verbal rules.

### R9. Codebase Question (before touching unfamiliar area)
```
Read {directory}/ and explain how data flows from {X} to {Y}.
What patterns are used? What should I know before modifying anything here?
```
Understanding before building. Prevents architectural mistakes.

## Execution Discipline

### R10. Incremental Build
Never say "build the entire feature." Split into: schema → API → validation → frontend → tests between each step. Five small steps beat one big prompt.

### R11. Test-First Workflow
```
Write tests for a function that {behaviour}.
Cover: {edge case list}.
Then implement the function to pass all tests.
```
Tests define behaviour before code exists. Implementation is automatically correct because it must pass the predefined tests.

### R12. Parallel Sessions
Open two terminals. One runs Claude on the backend, one on the frontend. Each session has clean, focused context for its domain. Connect the pieces at the end.

For larger fan-out, prefer routines or swarm teams — see [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md).

## Review & Verification

### R13. Diff Review
```
Show me a diff of every file you modified. Explain each change in one sentence.
```
Catches unintended modifications. Run after any batch of changes.

### R14. API Design Review
```
Review my API design: {paste route definitions}.
Check for: inconsistent naming, missing error responses, unpaginated
endpoints, missing auth on protected routes, REST convention violations.
Suggest specific improvements.
```

### R15. Security Scan
```
Scan this codebase for: SQL injection, XSS, exposed secrets in code or
config, missing input validation, IDOR, missing rate limiting.
For each finding: severity, exact location, why it's dangerous, the fix.
```

### R16. Performance Profiler
```
Analyse this codebase for: N+1 queries, missing indexes based on query
patterns, unnecessary React re-renders, large imports that should be lazy
loaded, endpoints that should be cached. Prioritise by estimated impact.
```

### R17. Documentation Pass
```
Read every file you created or modified for this feature. Generate docs:
what each function does, how they connect, expected I/O, non-obvious
design decisions.
```
Run **immediately** after building. Memory is fresh and accurate; docs written days later hallucinate.

## Debug & Recovery

### R18. Full Error Paste
```
I got this error: {paste complete error including stack trace}.
Diagnose the root cause step by step before suggesting a fix.
```
The "step by step before fix" constraint prevents jumping to a wrong answer. Always paste the **full** trace, never a summary.

### R19. Reproduction Prompt
```
Bug report: {paste}. Create a minimal reproduction: exact steps, expected
behaviour, actual behaviour. Then write a failing test that captures this
bug. Then fix the code to make the test pass.
```

### R20. Blame Investigator
```
This function started failing yesterday. Read the git log for this file
over the past week. Identify which commit likely introduced the issue
and explain what changed. Then suggest the fix.
```

### R21. Dependency Conflict Resolver
```
Dependency conflict: {paste}. Identify which packages require conflicting
versions. Suggest the resolution with the fewest changes, explain tradeoffs.
```

### R22. Recovery Mode
```
Stop. Read the original working version of this file from git:
{git show output}. The goal is: {restate simply}. Start fresh with a
different approach — the previous approach is not working.
```
Use when you've been going back and forth for too long. Starting over beats patching accumulated mistakes.

### R23. Screenshot Debug
Paste a screenshot with `Ctrl+V`. "The button is misaligned with the input field. The spacing between cards is inconsistent. Fix both." Visual feedback beats prose for UI bugs.

## Checkpoint Hygiene

### R24. Undo Checkpoint
```bash
git add . && git commit -m "checkpoint before {change}"
```
Before every major change. Revert in seconds instead of debugging for thirty minutes what used to work.

### R25. Terminal Escape Hatch
Prefix any message with `!` to run as a shell command instead of sending to Claude. Use for quick `git status`, test runs, directory checks without leaving the session.

## Dependency & Release

### R26. Dependency Check (pre-install)
```
I want to add {package} for {use case}. Check: actively maintained?
Known security issues? Bundle size impact? Lighter alternatives
covering my specific use case?
```

### R27. Release Notes
```
Read the git log since {last tag}. Generate release notes organised by:
new features, bug fixes, performance improvements, breaking changes.
Each entry in user-friendly language. Format as a markdown changelog.
```

### R28. Git Hook Writer
```
Create a pre-commit hook that: runs the linter on staged files, runs type
checking, blocks commits with console.log in production code. Install at
.husky/pre-commit.
```

### R29. Environment Setup Script
```
Create setup.sh a new developer runs once: install deps, create .env from
.env.example, set up local DB, run migrations, seed test data, verify by
running tests.
```

### R30. Database Seed Builder
```
Create a seed file for the dev database. Include: 5 users (1 admin,
2 editors, 2 viewers), 20 sample projects with realistic data,
relationships, edge cases (archived project, deleted user, empty project).
Realistic data, not 'test123'.
```

## Session Economics

### R31. Model Switching
- **Opus** → planning, architecture, deep refactor design
- **Sonnet** → implementation, execution
- **Haiku** → grammar, formatting, short translations, quick one-shots

Plan with the thinker. Build with the builder.

### R32. Cost Check
```
/cost
```
Every 30-60 minutes during long sessions. Set a mental budget per session; check against it.

### R33. Compact Mid-Session
```
/compact
```
After 30-45 minutes, when context gets bloated. Compresses history to key decisions and current state. For session-management depth (when to compact vs. clear vs. rewind), see [`../../ai-coding-agents-sessions/SKILL.md`](../../ai-coding-agents-sessions/SKILL.md).

### R34. Clean Slate Between Tasks
```
/clear
```
New task = new session. Carrying context from a DB refactor into a frontend redesign produces confused code.

### R35. Edit Over Follow-up
When Claude misunderstood, **edit the original message and regenerate** instead of sending "no, I meant X." Follow-ups stack onto history — editing replaces the bad turn and avoids quadratic token growth.

## Setup Sequence for a New Project

1. `/init` — generate `CLAUDE.md`
2. Add coding standards + patterns to `CLAUDE.md` (see R3)
3. `/memory` — persistent rules (see R2)
4. Plan mode — architecture before code (R4)
5. Build incrementally with tests between steps (R10, R11)

Five minutes of setup changes every subsequent hour.

## See Also

- [`../../ai-coding-agents-sessions/SKILL.md`](../../ai-coding-agents-sessions/SKILL.md) — session lifecycle, rewind, compact vs. clear decisions
- [`../../ai-prompt-engineering/SKILL.md`](../../ai-prompt-engineering/SKILL.md) — general prompt design patterns beyond Claude Code
- [`../../agents-memory/SKILL.md`](../../agents-memory/SKILL.md) — `CLAUDE.md` authoring rules
- [`creation-workflow.md`](creation-workflow.md) — building agents (different level of abstraction)
