# Context Management for Coding Agents

Token budgets, file selection strategies, and context patterns for agents that work with code. Code-heavy tasks consume context differently from general tasks because source files are large, interdependent, and require cross-file understanding.

---

## Table of Contents

- [1. Token Budget Model](#1-token-budget-model)
- [2. File Selection Strategies](#2-file-selection-strategies)
- [3. Progressive Disclosure](#3-progressive-disclosure)
- [4. Handling Large Files](#4-handling-large-files)
- [5. Cross-File Context](#5-cross-file-context)
- [6. The Explore-Then-Act Pattern](#6-the-explore-then-act-pattern)
- [7. Multi-Agent Context Management](#7-multi-agent-context-management)
- [8. When to Split into Subagents](#8-when-to-split-into-subagents)

---

## 1. Token Budget Model

Every agent has a fixed context window. Split it into three buckets:

| Bucket | Allocation | Contents |
|--------|-----------|----------|
| Instructions | 15-20% | System prompt, skill content, agent rules, output format |
| Code | 50-60% | File contents the agent reads during its work |
| Output | 20-30% | The agent's reasoning, tool calls, and generated code/findings |

### Practical Allocation by Context Size

**200k context window (standard models):**

| Bucket | Tokens | Rough Capacity |
|--------|--------|---------------|
| Instructions | 30k-40k | System prompt + one reference file |
| Code | 100k-120k | ~25-30 files of ~100 lines each |
| Output | 40k-60k | Detailed findings or ~500 lines of generated code |

**1M context window (extended context):**

| Bucket | Tokens | Rough Capacity |
|--------|--------|---------------|
| Instructions | 150k-200k | System prompt + multiple reference files + examples |
| Code | 500k-600k | ~125-150 files of ~100 lines each |
| Output | 200k-300k | Comprehensive reports or large code generation |

### Estimation Formula

To estimate whether your task fits in the context window:

```
tokens_needed = instruction_tokens
              + (file_count x avg_lines_per_file x 4)
              + estimated_output_tokens
```

The multiplier of ~4 tokens per line of code is an average. Dense code (minified JS, one-liners) may reach 6-8 tokens/line. Well-spaced Python or Go is closer to 3 tokens/line.

### Budget Monitoring

If the agent starts truncating output, forgetting earlier files, or producing lower-quality analysis on later files, it is running out of context. Solutions:
- Reduce the number of files read
- Use targeted reads (offset/limit) instead of full-file reads
- Split the task into subagents with smaller scope

---

## 2. File Selection Strategies

How the agent decides which files to read.

### Targeted Reads

Use when file paths are known (user provided them, grep returned them, or import tracing identified them).

```
User says: "Review changes in src/auth/validate.ts"
Agent action: Read("src/auth/validate.ts")
```

This is the most token-efficient strategy. No discovery overhead.

### Discovery

Use when the agent must find relevant files.

**Grep-first discovery:**
1. Grep for a pattern (function name, import path, error message)
2. Read the matching files
3. Optionally: grep within those files for deeper context

```
Task: "Find all callers of validateToken"
Agent:
  1. Grep for "validateToken" across the repo
  2. Read each file that contains a call
  3. Understand the call context
```

**Glob-first discovery:**
1. Glob for files matching a pattern (*.test.ts, src/api/*.ts)
2. Read a sample to understand the pattern
3. Read remaining files as needed

```
Task: "Review all API route handlers"
Agent:
  1. Glob for src/api/**/*.ts
  2. Read 2-3 route files to understand the pattern
  3. Read remaining routes, focusing on non-standard ones
```

### Import Tracing

Use when you need to understand the dependency graph around a file.

1. Read the target file
2. Parse its imports
3. Read the imported modules (1 level deep is usually sufficient)
4. If needed: read the importers of the target file (who depends on it)

```
Target: src/auth/validate.ts
Imports: src/auth/types.ts, src/utils/crypto.ts, src/config/env.ts
Importers: src/api/login.ts, src/api/refresh.ts, src/middleware/auth.ts
Context: 1 target + 3 imports + 3 importers = 7 files
```

Going more than 2 levels deep on import tracing usually exceeds the token budget without adding proportional value. Stop at 1-2 levels and note unexplored branches.

---

## 3. Progressive Disclosure

Start broad, narrow down. This pattern is modeled on Claude Code's Explore agent.

**Level 1: Repository structure**
```
ls src/
ls src/api/
ls src/auth/
```
Output: directory names and file counts. Very low token cost. Gives the agent a mental map.

**Level 2: Key configuration files**
```
Read package.json (dependencies, scripts)
Read tsconfig.json (paths, strict mode)
Read .eslintrc (rules)
```
Output: project conventions, available tools, build targets. Moderate token cost.

**Level 3: Entry points and interfaces**
```
Read src/index.ts
Read src/types/index.ts
Read src/api/routes.ts
```
Output: the shape of the application. How modules connect. What the public API looks like.

**Level 4: Specific source files**
```
Read src/auth/validate.ts
Read src/auth/validate.test.ts
```
Output: the actual code under analysis.

Not every task needs all four levels. A code reviewer that receives a diff can skip levels 1-3 entirely. A security scanner benefits from all four levels.

---

## 4. Handling Large Files

Files over 500 lines strain the token budget. Strategies:

### Use Read with Offset/Limit

Read specific sections instead of the entire file:

```
Read("src/api/routes.ts", offset=0, limit=50)    # imports and setup
Read("src/api/routes.ts", offset=140, limit=30)   # the specific function
```

### Search, Then Read

Use Grep to find the exact location, then read a narrow window:

```
Grep("validateToken", "src/auth/validate.ts")     # returns line number
Read("src/auth/validate.ts", offset=38, limit=25) # read the function
```

### Split Reads Across Tool Calls

For analysis tasks, read different sections in separate tool calls rather than loading the entire file:

```
Call 1: Read lines 1-50 (imports and types)
Call 2: Read lines 200-250 (the function under review)
Call 3: Read lines 400-430 (related helper)
```

### When to Read the Full File

Read the full file when:
- The file is under 200 lines
- The task requires understanding the entire file's structure (refactoring, documentation)
- You need to understand how multiple functions in the same file interact

---

## 5. Cross-File Context

Coding agents need more than the target file. They need to understand the types, interfaces, and dependencies around it.

### Type Definition Files

Read type/interface files that the target file imports:

```
Target imports: import { User, Token } from '../types'
Agent reads: src/types/index.ts (or the specific export file)
```

Without type context, the agent will guess at parameter shapes and return types, leading to hallucinated findings or incorrect code generation.

### Interface Files

For services with contracts (API routes, database models, message handlers):

```
Target: src/api/users.ts
Agent reads: src/api/types.ts (request/response shapes)
Agent reads: src/db/models/user.ts (database schema)
```

### Follow Import Chains (1-2 Levels)

**Level 0**: The target file itself.
**Level 1**: Files the target directly imports.
**Level 2**: Files that level-1 files import (only if needed for understanding).

Beyond level 2, the agent is reading code that is too distant from the task. Stop and note the boundary.

### Give Context About the Surrounding Module

For agents that need to understand how a file fits into a larger system:

```
Read the directory listing of the target's parent directory
Read the module's index file (re-exports show the public API)
Read the module's README if it exists
```

---

## 6. The Explore-Then-Act Pattern

Two-phase approach from Claude Code's built-in architecture. The most reliable pattern for complex coding tasks.

### Phase 1: Read-Only Exploration

A dedicated exploration phase (or a separate Explore agent) that:
- Uses only read-only tools: Read, Grep, Glob, Bash (read-only commands)
- Makes parallel tool calls for speed
- Cannot write, edit, or modify files
- Produces a structured summary of findings

```
Explore agent output:
- Files relevant to the task: [list with brief descriptions]
- Key types/interfaces: [summary]
- Existing test coverage: [summary]
- Potential issues found: [list]
- Recommended changes: [list with file:line references]
```

### Phase 2: Focused Editing

A fresh agent (or fresh phase) that receives the exploration summary and makes targeted edits:
- Knows exactly which files to modify (from exploration)
- Knows the types and interfaces involved (from exploration)
- Has specific change instructions (from exploration)
- Runs verification after changes

### Why Separate Phases

1. **Context efficiency**: The exploration phase reads many files but discards intermediate reasoning. The edit phase receives only the synthesized findings, leaving more context for actual code generation.
2. **Error isolation**: If exploration was wrong, it did not modify any files. If editing fails, the exploration findings are still valid for a retry.
3. **Different tool sets**: Exploration agents are read-only (safer). Edit agents need write tools (constrained by exploration findings).

### When to Use a Single Phase

Skip the two-phase pattern when:
- The task is simple enough that exploration and editing can happen in one pass
- The target files are already known (no discovery needed)
- The edit is mechanical (e.g., rename a variable in known locations)

---

## 7. Multi-Agent Context Management

When multiple agents work on the same codebase.

### Fork vs Spawn: Context Sharing Decision

| Pattern | Context Behavior | When to Use |
|---------|-----------------|-------------|
| Fork | Inherits parent's prompt cache (shared context) | Parallel exploration that builds on parent's understanding |
| Spawn | Fresh context (clean slate) | Phase boundary (exploration done, start implementation) |

**Fork** when the child agent benefits from everything the parent has already read. Example: the parent has read the project structure and key types; forked children search different modules in parallel.

**Spawn fresh** when context rotation is needed. Example: exploration is done, the synthesized findings are ready, and a fresh agent should implement without the noise of exploration reasoning.

### Context Rotation at Phase Boundaries

The transition from exploration to implementation is a natural rotation point:

```
Phase 1 (Explore agent): reads 30 files, produces summary
Phase 2 (Edit agent):    receives summary (~2 pages), reads only the 5 target files
```

The edit agent starts with a clean context containing only the summary and the files it needs. This prevents the "lost in earlier context" problem where an agent forgets its findings after reading too many files.

### State Shape for Coding Task Graphs

When a coordinator manages multiple workers, persist state in a structured format:

```json
{
  "tasks": [
    {
      "id": "refactor-auth",
      "owner": "worker-1",
      "owned_files": ["src/auth/validate.ts", "src/auth/helpers.ts"],
      "depends_on": ["explore-auth"],
      "verify_command": "npx jest src/auth/",
      "status": "in_progress"
    },
    {
      "id": "refactor-api",
      "owner": "worker-2",
      "owned_files": ["src/api/users.ts", "src/api/posts.ts"],
      "depends_on": ["explore-api"],
      "verify_command": "npx jest src/api/",
      "status": "pending"
    }
  ]
}
```

### Durable State in Files

Conversation memory is ephemeral. For multi-agent workflows, persist important state in files:

- **Task graph**: JSON file tracking task status, ownership, dependencies
- **Exploration findings**: Markdown file with structured analysis results
- **Decision log**: Why certain approaches were chosen or rejected
- **Change manifest**: List of all files modified, by which agent, with commit hashes

This allows a new agent (spawned fresh) to pick up where a failed agent left off by reading the state files.

---

## 8. When to Split into Subagents

### Signals That Splitting Is Needed

**File count threshold**: More than 5-10 files across different, unrelated modules. A single agent trying to hold context for `src/auth/`, `src/billing/`, and `src/notifications/` simultaneously will lose coherence.

**Context degradation**: The agent starts:
- Referring to details from earlier files incorrectly
- Forgetting constraints stated in the system prompt
- Producing lower-quality output on later files vs earlier files
- Missing obvious issues that it would catch with a fresh context

**Independent sub-tasks**: If parts of the task do not share files or state, they are candidates for parallel subagents. Example: reviewing the auth module and the billing module are independent tasks.

### How to Split

1. Identify independent sub-tasks with clear boundaries
2. Assign each sub-task exclusive owned_files (no overlap)
3. Define the output contract for each subagent
4. Spawn subagents (fork if they share exploration context, spawn fresh if not)
5. Collect and synthesize results at the coordinator level

### Example Split

**Original task**: "Review all API endpoints for input validation issues"

**Split**:
- Subagent 1: Review `src/api/auth/` endpoints (3 files)
- Subagent 2: Review `src/api/users/` endpoints (4 files)
- Subagent 3: Review `src/api/billing/` endpoints (3 files)
- Coordinator: Merge findings, deduplicate, sort by severity

Each subagent has a focused context (3-4 files + their imports) instead of one agent holding 10+ files.

### When NOT to Split

- Files are tightly coupled and understanding one requires the others
- The task is sequential (output of step 1 is input to step 2)
- Coordination overhead exceeds the task itself (small tasks)
- The total file count is under 5 and files are in the same module
