# Multi-Agent Coding Patterns

Three multi-agent architectures for coding teams, drawn from Claude Code source code. Each pattern solves a different coordination problem. Choose based on task shape, not complexity.

---

## Table of Contents

- [A. Coordinator-Led Coding Team](#a-coordinator-led-coding-team)
- [B. Fork Subagent Pattern](#b-fork-subagent-pattern)
- [C. Agent Teams (Peer Swarm)](#c-agent-teams-peer-swarm)
- [Common Multi-Agent Principles](#common-multi-agent-principles)
- [Anti-Patterns](#anti-patterns)
- [Choosing the Right Pattern](#choosing-the-right-pattern)

For Claude Code implementation details behind the swarm and worktree behaviors summarized here, read [`claude-code-swarm-and-worktree-patterns.md`](claude-code-swarm-and-worktree-patterns.md).

---

## A. Coordinator-Led Coding Team

### How It Works

The coordinator is a single leader agent that launches background workers via the Agent tool. Workers execute independently with no visibility into the coordinator's conversation. Results arrive as `<task-notification>` XML:

```xml
<task-notification>
  <task-id>abc-123</task-id>
  <status>completed</status>        <!-- completed | failed | killed -->
  <summary>Found race condition in connection pool</summary>
  <result>
    File: src/db/pool.ts, line 47
    The acquire() method does not hold the lock across the await boundary.
    When two coroutines call acquire() simultaneously, both receive the same connection.
  </result>
  <usage>
    <tokens>12400</tokens>
    <tool_count>8</tool_count>
  </usage>
</task-notification>
```

The coordinator reads notifications, synthesizes findings, and directs the next phase.

### The Synthesis Principle

The coordinator must read and understand worker findings before directing next steps. Never write "based on your findings, fix it" -- that delegates understanding. The coordinator must include file paths, line numbers, and exact changes in every implementation spec.

Bad:
```
"Based on the researcher's findings, fix the bug."
```

Good:
```
"In src/db/pool.ts line 47, the acquire() method drops the lock across the await.
Wrap lines 47-52 in a try/finally that holds this._mutex through the await.
Do NOT change the release() method. Do NOT add new dependencies."
```

### Coding Workflow Phases

**Phase 1 -- Research (parallel)**

Launch multiple explore workers simultaneously. Each worker is read-only and investigates a different part of the codebase.

```
Agent({ prompt: "Search src/db/ for all connection pool usage. List every file, function, and line number where acquire() or release() is called.", tools: ["Read", "Glob", "Grep", "Bash"] })

Agent({ prompt: "Search test/ for all connection pool tests. List what scenarios are covered and what is missing.", tools: ["Read", "Glob", "Grep", "Bash"] })
```

Launch all independent tasks in a single message with multiple Agent() calls. This is the coordinator's superpower.

**Phase 2 -- Synthesis**

The coordinator reads all notifications, understands the problem, identifies root cause. This step happens in the coordinator's own context, not delegated to a worker.

The coordinator produces:
- Root cause statement (one sentence)
- Affected files with line numbers
- Proposed fix with exact changes
- Files to NOT touch
- Expected behavior after fix

**Phase 3 -- Implementation**

Two options:
1. **Continue existing worker** via `SendMessage({ to: "task-abc-123", message: "..." })` -- use when the worker already has the relevant context loaded.
2. **Spawn fresh worker** -- use when the implementation brief is self-contained or the research worker's context is polluted with exploration noise.

The implementation spec must be self-contained:

```
Agent({
  prompt: `
    Fix the connection pool race condition.
    
    File: src/db/pool.ts
    
    Current code (lines 47-52):
    async acquire(): Promise<Connection> {
      await this._mutex.acquire();
      const conn = this._pool.pop();
      this._mutex.release();
      return conn;
    }
    
    Required change:
    Wrap the body in try/finally so the mutex is held through the pop():
    async acquire(): Promise<Connection> {
      await this._mutex.acquire();
      try {
        const conn = this._pool.pop();
        return conn;
      } finally {
        this._mutex.release();
      }
    }
    
    Do NOT modify release().
    Do NOT add new imports.
    Do NOT change the Connection type.
    
    After editing, run: npm test -- --grep "pool"
  `,
  tools: ["Read", "Edit", "Bash"]
})
```

**Phase 4 -- Verification**

Spawn a fresh worker with an adversarial posture. This worker does NOT know what the implementation worker changed. It checks independently.

```
Agent({
  prompt: `
    Verify the connection pool implementation in src/db/pool.ts.
    
    Check:
    1. Read acquire() and release() methods
    2. Verify the mutex is held across the entire critical section in acquire()
    3. Run: npm test -- --grep "pool"
    4. Run: npm test -- --grep "concurrent"
    5. Check for other callers of _mutex that might have the same pattern
    
    Report PASS or FAIL with evidence.
    Do not explain away failures. Report what you observe.
  `,
  tools: ["Read", "Grep", "Glob", "Bash"]
})
```

### Worker Prompts

Workers cannot see the coordinator's conversation. Every worker prompt must be self-contained:

| Include | Why |
|---------|-----|
| File paths | Worker cannot guess locations |
| Line numbers | Worker wastes turns searching without them |
| Expected behavior | Worker needs success criteria |
| Constraints (do NOT) | Prevents scope creep |
| Verification command | Worker confirms its own work |

### Parallelism

The coordinator's primary advantage is launching parallel workers. Independent tasks go in a single message:

```
# All three launch simultaneously
Agent({ prompt: "Search src/auth/ for ...", tools: [...] })
Agent({ prompt: "Search src/api/ for ...", tools: [...] })
Agent({ prompt: "Search src/db/ for ...", tools: [...] })
```

Never launch workers one at a time when they are independent.

### When to Use

- 3+ bounded coding tasks that can be parallelized
- Research-then-implement loops with clear phase boundaries
- Parallel review or testing of different modules
- Tasks where the coordinator must synthesize before acting

### When NOT to Use

- Simple single-file changes (overhead not justified)
- Tasks requiring constant back-and-forth (fork is cheaper)
- Exploratory work where the next step depends entirely on the previous

### Template Reference

`assets/templates/coordinator-coding-team.md`

### Example: Multi-File Bug Fix

1. Launch 2 parallel research workers: one searches src/, one searches test/
2. Coordinator reads both notifications, identifies root cause in src/db/pool.ts
3. Coordinator writes exact implementation spec with file, lines, and constraints
4. Implementation worker applies the fix and runs tests
5. Verification worker (fresh, adversarial) checks the fix independently
6. Coordinator reports result to user

---

## B. Fork Subagent Pattern

### How It Works

Omit `subagent_type` when calling Agent. The child inherits the parent's full conversation history and system prompt. It runs silently in the background and reports a structured result when done.

```
Agent({
  prompt: "Search the auth module for all uses of the deprecated session API. List each file and line."
})
```

No `subagent_type` field means "fork from my current context."

### Prompt Cache Sharing

All fork children use identical placeholder text for inherited tool results. Only the final directive differs. This enables prompt cache sharing across parallel forks -- making forks significantly cheaper than fresh agents when launching multiple in parallel.

```
# These three forks share prompt cache because they inherit identical history
Agent({ prompt: "Search src/auth/ for deprecated session API usage" })
Agent({ prompt: "Search src/api/ for deprecated session API usage" })
Agent({ prompt: "Search src/db/ for deprecated session API usage" })
```

### The "Don't Peek" Rule

The parent receives a notification with an `output_file` path. Do NOT Read or tail the output file unless the user explicitly asks. Trust the notification summary. Reading mid-flight pulls tool noise into the parent's context and wastes tokens.

### The "Don't Race" Rule

After launching a fork, the parent knows nothing about what the fork found. Never fabricate or predict fork results. If the user asks before the notification arrives:

```
"The background search is still running. I'll share findings when it completes."
```

### Structured Report Format

Forks report with a consistent structure:

```
Scope: Searched src/auth/ for deprecated session API usage.
Result: Found 7 call sites across 3 files.
Key files:
  - src/auth/login.ts (lines 23, 45, 89)
  - src/auth/refresh.ts (lines 12, 67)
  - src/auth/logout.ts (lines 34, 56)
Files changed: None (read-only task)
Issues: login.ts line 89 uses session.extend() which was removed in v3.
```

### Recursive Guard (revised for depth-5 nesting, 2026)

Forks are no longer capped at one level. Since Claude Code v2.1.172, subagents — including forks — can spawn their own subagents up to 5 levels below the main conversation; a subagent at depth 5 does not receive the Agent tool and cannot spawn further. Since v2.1.187, a fork's depth is fixed at spawn time and forked subagents count toward the same 5-level cap as named subagents (resuming a subagent later does not change its recorded depth).

Depth being *allowed* is not the same as depth being *advisable*. Every additional level adds a synthesis hop — a depth-3 worker's findings have already been summarized by a depth-2 worker before the depth-1 coordinator (or user) ever sees them, and each hop is a chance to drop a caveat or a file:line reference. Default to depth 1-2 (a fork or a coordinator's direct workers). Reach for deeper nesting only when a sub-task is itself decomposable into independent, boundable pieces — not as a substitute for writing a clear, self-contained brief.

### When to Use

| Scenario | Why Fork Works |
|----------|----------------|
| Background research while chatting with user | Non-blocking, silent |
| Parallel search across modules | Cache sharing makes it cheap |
| Quick exploration that benefits from parent context | Full history inherited |
| Tasks where the parent should keep talking | Fork is non-blocking |

### When NOT to Use

| Scenario | Why Fork Fails |
|----------|----------------|
| Phase boundaries (explore then implement) | Spawn fresh -- context rotation needed |
| Long-running sessions with polluted context | Fork inherits the pollution |
| Tasks needing a focused brief | Fresh agent with clean prompt is better |
| Deep implementation work needing several verification hops | Depth compounds cost and dilutes synthesis fidelity even though nesting to depth 5 is technically allowed |

### Coding Example

Search 5 modules in parallel for usage of a deprecated API:

```
Agent({ prompt: "Search src/auth/ for calls to legacyHash(). List file, line, and surrounding context." })
Agent({ prompt: "Search src/api/ for calls to legacyHash(). List file, line, and surrounding context." })
Agent({ prompt: "Search src/db/ for calls to legacyHash(). List file, line, and surrounding context." })
Agent({ prompt: "Search src/billing/ for calls to legacyHash(). List file, line, and surrounding context." })
Agent({ prompt: "Search src/admin/ for calls to legacyHash(). List file, line, and surrounding context." })
```

The parent continues thinking about the migration strategy while forks run in parallel.

---

## C. Agent Teams (Peer Swarm)

### How It Works

Multiple agents run simultaneously with their own identities. They communicate via file-based mailboxes. They share a task list. Each can have its own git worktree for isolation.

Mailbox location: `~/.claude/teams/{team_name}/inboxes/{agent_name}.json`

### Spawning a Teammate

```
Agent({
  name: "researcher",
  team_name: "bug-hunt",
  prompt: "You are the researcher on the bug-hunt team. Search for evidence of the memory leak in src/cache/. Report findings to the team lead via mailbox."
})

Agent({
  name: "test-runner",
  team_name: "bug-hunt",
  prompt: "You are the test runner on the bug-hunt team. Run the cache test suite with memory profiling enabled. Report results to the team lead via mailbox."
})
```

The `name` field makes the agent addressable via SendMessage.

### Peer Messaging

Direct message:
```
SendMessage({ to: "researcher", message: "What did you find in the cache module?" })
```

Broadcast to all teammates:
```
SendMessage({ to: "*", message: "Found root cause: unbounded LRU cache in src/cache/store.ts line 34" })
```

### Mailbox Protocol

File-based JSON with lockfile concurrency control:

```json
{
  "messages": [
    {
      "from": "researcher",
      "text": "Found unbounded growth in LRU cache. See src/cache/store.ts line 34.",
      "summary": "Unbounded LRU cache growth found",
      "timestamp": "2025-01-15T10:23:45Z",
      "color": "blue",
      "read": false
    }
  ]
}
```

Lockfile protocol prevents concurrent write corruption. Each agent acquires `{inbox}.lock` before writing.

### Permission Bridge

When a teammate needs tool permission (e.g., to run a destructive bash command), the request travels via mailbox to the team lead's UI. The lead approves or denies. The response flows back through the mailbox. Teammates have independent permission modes.

### Worktree Isolation

Each teammate can work in its own git worktree:

```
Agent({
  name: "implementer-auth",
  team_name: "migration",
  isolation: "worktree",
  prompt: "Migrate src/auth/ from v2 to v3 API. Work in your own worktree."
})
```

This enables 100+ concurrent agents editing different files without merge conflicts. Each worktree is a full working copy of the repo at the same commit.

### Owned Files Pattern

Critical for teams. Assign each teammate exclusive files. No two teammates should edit the same file.

```
Agent({
  name: "auth-migrator",
  team_name: "v3-migration",
  prompt: `
    You own these files exclusively:
    - src/auth/login.ts
    - src/auth/refresh.ts
    - src/auth/logout.ts
    
    No other teammate will edit these files.
    Do NOT edit files outside this list.
    
    Migrate all deprecated session API calls to the v3 API.
  `
})
```

The lead validates file assignments before dispatch to ensure no overlaps.

### Shared Task List

All team members access the same task list directory: `~/.claude/teams/{team_name}/tasks/`

```json
{
  "id": "task-001",
  "description": "Migrate src/auth/login.ts to v3 API",
  "owner": "auth-migrator",
  "owned_files": ["src/auth/login.ts"],
  "depends_on": [],
  "verify": "npm test -- --grep auth/login",
  "status": "in-progress"
}
```

Task states: `pending` | `in-progress` | `done` | `failed` | `blocked`

### Idle Notification

Teammates notify the lead when done via the Stop hook. The lead can then reassign the teammate to new work or merge results.

### When to Use

- Self-coordinating specialists working on different parts of a codebase
- Complex investigations where agents need to discuss findings
- Large-scale migrations with many independent file sets
- Tasks requiring more than one level of delegation

### When NOT to Use

- Small tasks (overhead of team setup exceeds benefit)
- Tasks where all files are interdependent (owned files pattern breaks down)
- Quick searches (forks are cheaper and simpler)

### Coding Example: Bug Investigation

1. Lead spawns: code-searcher + test-runner + log-analyzer
2. code-searcher greps for memory allocation patterns in src/cache/
3. test-runner runs cache tests with `--detect-open-handles`
4. log-analyzer searches production logs for OOM patterns
5. Each reports findings via mailbox to lead
6. Lead synthesizes: "The LRU cache in store.ts has no max-size. Under load, it grows unbounded."
7. Lead spawns implementer with exact fix spec and owned files
8. Lead spawns verifier (fresh, adversarial) to check the fix

---

## Common Multi-Agent Principles

These apply across all three patterns.

### 1. Freeze Interfaces Before Dispatch

Define contracts, owned files, and expected outputs before launching any worker. Changing the contract mid-flight causes rework and confusion.

```
# Before dispatch, define:
- Input: what the worker receives
- Output: what the worker must produce (structure, not just content)
- Constraints: what the worker must NOT do
- Owned files: exclusive file list per worker
- Verification: how to check the worker's output
```

### 2. Give Every Worker Exclusive Owned Files

Two workers editing the same file produces merge conflicts. Even with worktree isolation, merging concurrent edits to the same file is error-prone.

### 3. Require Structured Reports

Workers must produce reports in a defined schema. The coordinator validates structure before processing content.

```
# Required report fields:
Scope:          (one sentence)
Result:         (findings or changes made)
Key files:      (absolute paths)
Files changed:  (paths + commit hash if applicable)
Verification:   (command run + output)
Issues:         (blockers or concerns, if any)
```

### 4. Spawn Fresh Workers at Phase Boundaries

Exploration and implementation are different phases. The explorer's context is full of search results and dead ends. The implementer needs a clean context with just the spec.

| Phase transition | Action |
|-----------------|--------|
| Explore -> Implement | Spawn fresh with implementation spec |
| Implement -> Verify | Spawn fresh with adversarial verification prompt |
| Verify -> Fix | Continue implementer (context overlap) or spawn fresh |

### 5. Persist State in Durable Files

Task graphs, decisions, and dependency outputs belong in files (JSON, YAML, Markdown), not in agent memory. Agents come and go; files persist.

```
.claude/
  tasks/
    task-001.json
    task-002.json
  decisions/
    2025-01-15-root-cause.md
  outputs/
    research-findings.md
    verification-report.md
```

### 6. Escalation Pattern

```
Worker encounters failure
  -> Worker self-corrects (one attempt)
    -> Still failing? Worker escalates to coordinator/lead
      -> Coordinator diagnoses, reassigns, or adjusts spec
        -> Still failing? Escalate to human
```

Never let a worker retry the same approach more than once. Escalation is faster than repetition.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Using one worker to check on another | Workers can't see each other's context | Trust notifications; coordinator synthesizes |
| Passing raw transcripts between workers | Too noisy, wastes tokens | Distill findings into structured reports |
| Self-verifying implementation | Confirmation bias | Separate verifier with fresh context |
| Launching before freezing interfaces | Rework and conflicts | Define contracts, owned files, outputs first |
| "Based on your findings, fix it" | Delegates understanding | Coordinator synthesizes and writes exact spec |
| Retrying same failure approach | Wasted turns, context pollution | Escalate after one retry |
| Launching workers one at a time | Slow; wastes coordinator's parallelism advantage | Batch all independent launches in one message |
| Giving workers overlapping file ownership | Merge conflicts | Exclusive owned_files per worker |

---

## Choosing the Right Pattern

| Situation | Pattern | Reason |
|-----------|---------|--------|
| 2-3 independent research tasks | Coordinator | Simple, leader retains control |
| Quick parallel search across modules | Fork | Cheap (cache sharing), context inherited |
| Complex bug requiring specialist coordination | Agent Teams | Peer messaging, self-coordination |
| Research -> implement -> verify pipeline | Coordinator | Clear phase boundaries |
| 10+ files across different modules | Agent Teams + worktrees | File isolation, scalable |
| Background work while chatting with user | Fork | Non-blocking, silent |
| Single-file fix with verification | Coordinator | Overkill to use teams |
| Exploratory work with uncertain next steps | Fork | Parent context helps; cheap to try |
| Long-running migration across entire codebase | Agent Teams | Worktrees, shared task list, idle reassignment |

### Decision Flowchart

```
Is the task a single bounded unit?
  YES -> Do it yourself, no multi-agent needed
  NO -> Continue

Are the subtasks independent with no coordination needed?
  YES -> Are they small searches?
    YES -> Fork (cache sharing, cheap)
    NO -> Coordinator (structured phases)
  NO -> Do subtasks need to discuss findings?
    YES -> Agent Teams (mailbox communication)
    NO -> Coordinator (leader synthesizes)

Are there 10+ files to edit?
  YES -> Agent Teams with worktree isolation
  NO -> Coordinator is sufficient
```
