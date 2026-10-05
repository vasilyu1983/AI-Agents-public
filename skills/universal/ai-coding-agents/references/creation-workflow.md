# Coding Agent Creation Workflow

End-to-end guide for going from a coding task to a working agent definition. Follow these steps in order. Each step produces a concrete artifact or decision that feeds into the next.

---

## Table of Contents

- [Step 1: Task Classification](#step-1-task-classification)
- [Step 2: Single vs Multi-Agent Decision](#step-2-single-vs-multi-agent-decision)
- [Step 3: Archetype Selection](#step-3-archetype-selection)
- [Step 4: Platform Selection](#step-4-platform-selection)
- [Step 5: Template Instantiation](#step-5-template-instantiation)
- [Step 6: Tool Scoping](#step-6-tool-scoping)
- [Step 7: Context Design](#step-7-context-design)
- [Step 8: Instruction Writing](#step-8-instruction-writing)
- [Step 9: Self-Verification Design](#step-9-self-verification-design)
- [Step 10: Smoke Testing](#step-10-smoke-testing)
- [Extension-Robustness Gate](#extension-robustness-gate)
- [Step 11: Iteration Loop](#step-11-iteration-loop)

---

## Step 1: Task Classification

Before choosing any archetype or platform, answer these questions about the task itself.

**What code does the agent touch?**

| Scope | Examples | Implication |
|-------|----------|-------------|
| Single file | Fix one function, add docstring | Simple agent, low maxTurns |
| Module (5-15 files) | Refactor a service, add test suite | Medium agent, needs context discovery |
| Cross-module (15+ files) | API migration, framework upgrade | Multi-agent team or batch processing |
| Whole repo | Security scan, documentation generation | Read-only sweep or parallelized workers |

**Input/output shape:**

- Input: What does the agent receive? A diff, a file path, a natural language description, a list of files?
- Output: What must the agent produce? A structured report, edited files, new files, a commit?

**Deterministic or open-ended?**

- Deterministic: the correct output is predictable given the input (rename variable, apply formatter, migrate API call). These agents are easier to verify and can use tighter maxTurns.
- Open-ended: the output depends on judgment (code review findings, architecture suggestions, test strategy). These need more turns and explicit output format constraints.

**Classification output:** Write one sentence like this: "This agent reads [input], touches [scope], and produces [output]. The task is [deterministic/open-ended]."

Example: "This agent reads a git diff, touches no files (read-only), and produces a severity-ordered list of findings. The task is open-ended."

---

## Step 2: Single vs Multi-Agent Decision

Use this decision tree:

```
Is there exactly one bounded task?
├── YES → Single agent
│   (code review, test gen for one module, targeted refactor)
└── NO → Does the work decompose into 2+ independent sub-tasks?
    ├── YES → Can sub-tasks share files?
    │   ├── NO → Multi-agent team (each agent gets owned_files)
    │   └── YES → Sequential single agents or coordinator with phases
    └── NO → Is the work a pipeline (output of A feeds B)?
        ├── YES → Coordinator-led team with phase boundaries
        └── NO → Single agent with higher maxTurns
```

**Choose multi-agent when:**
- Three or more independent tasks that can run in parallel
- The investigation phase is complex enough to warrant a separate explorer
- Different sub-tasks require different tool sets (read-only research vs file editing)
- The task touches 15+ files across unrelated modules
- You need independent verification (verifier agent separate from implementer)

**Stay single-agent when:**
- The task is bounded to one module
- All sub-tasks share the same files and context
- The overhead of coordination exceeds the work itself
- You are prototyping and want fast iteration

**Decision output:** "Single agent" or "Multi-agent team with [pattern name]." If multi-agent, see [`multi-agent-coding-patterns.md`](multi-agent-coding-patterns.md).

---

## Step 3: Archetype Selection

Match the task classification from Step 1 to an archetype from [`agent-archetypes.md`](agent-archetypes.md).

| Task Type | Archetype | Key Trait |
|-----------|-----------|-----------|
| Analyze code, find issues | Code Reviewer | Read-only, findings-first |
| Create tests for existing code | Test Generator | Write tests, run them, verify they pass |
| Restructure code, preserve behavior | Refactoring Agent | Edit with before/after test validation |
| Apply pattern across many files | Migration Agent | Batch processing with checkpoints |
| Generate/update docs from code | Documentation Agent | Source-anchored, no hallucinated APIs |
| Find security vulnerabilities | Security Scanner | Read-only, evidence-based severity ordering |

If no archetype fits exactly, start from the closest one and adjust. The archetypes are starting points, not constraints.

**Selection output:** The archetype name and any modifications needed.

---

## Step 4: Platform Selection

| Scenario | Platform | Format |
|----------|----------|--------|
| Repo-local agent, team-shared, auto-delegated | Claude Code | `.md` file in `.claude/agents/` |
| Codex thread workers, sandbox-scoped | Codex | `.toml` custom agent |
| CI pipeline, API integration, custom orchestration | Agent SDK | Python or TypeScript |
| Quick prototype, single developer | Claude Code | `.md` file |

Decision tree:

```
Does the agent run inside a repo for a team?
├── YES → Claude Code .md
└── NO → Is it a Codex workflow?
    ├── YES → Codex .toml
    └── NO → Agent SDK (Python or TypeScript)
```

See [`platform-patterns.md`](platform-patterns.md) for side-by-side comparison and porting guide.

**Selection output:** Platform name and file format.

---

## Step 5: Template Instantiation

Start from the matching template in `assets/templates/`. Do not write from scratch.

**Steps:**

1. Copy the template file to your target location:
   - Claude Code: `.claude/agents/<agent-name>.md`
   - Codex: project config directory
   - Agent SDK: your application's agent directory

2. Update frontmatter fields:
   ```yaml
   ---
   name: <kebab-case-name>
   description: "<One sentence: what it does and when to use it>"
   tools: <tool list from Step 6>
   maxTurns: <based on archetype>
   model: <sonnet for most, opus for complex reasoning>
   permissionMode: <default | bypassPermissions | acceptEdits>
   ---
   ```

3. Keep the description concrete and trigger-oriented. Claude uses the description to decide when to delegate to this agent. Bad: "Helps with code." Good: "Review TypeScript files for type safety issues and missing null checks. Use after changes to shared type definitions."

4. Adapt the system prompt body for your specific task (see Step 8).

**Instantiation output:** A working agent file with correct frontmatter and placeholder system prompt.

---

## Step 6: Tool Scoping

Start with the minimum tool set. Add tools only when the agent demonstrably fails without them.

**Read-only agents** (Code Reviewer, Security Scanner):

| Tool | Purpose |
|------|---------|
| Read | Read file contents by path |
| Grep | Search file contents by pattern |
| Glob | Find files by name pattern |
| Bash | Run read-only commands (git diff, git log, ls) |

Explicitly disallow write tools in the system prompt: "You must NOT use Edit, Write, or any command that modifies files."

**Edit agents** (Test Generator, Refactoring Agent, Migration Agent):

| Tool | Purpose |
|------|---------|
| Read | Read file contents |
| Grep | Search for patterns |
| Glob | Find files |
| Edit | Make targeted changes to existing files |
| Write | Create new files |
| Bash | Run tests, linters, formatters, build commands |

**Documentation agents** (lighter write set):

| Tool | Purpose |
|------|---------|
| Read | Read source code |
| Write | Create/update doc files |
| Grep | Find functions, classes, exports |
| Glob | Discover file structure |

**Principles:**

- Every tool in the list must have a reason. If you cannot articulate why the agent needs Bash, remove it.
- Bash is the most powerful and most dangerous tool. Restrict it when possible by listing allowed commands in the system prompt.
- For read-only agents, listing Bash but constraining it to read commands (git diff, cat, ls, find) is safer than removing it entirely, because some analysis tasks genuinely need shell commands.
- MCP tools follow the same principle: add only when Bash cannot accomplish the same task. See [`tool-integration.md`](tool-integration.md) for when MCP is warranted.

**Scoping output:** The tools list for frontmatter and any tool constraints for the system prompt.

---

## Step 7: Context Design

Determine what files the agent needs to read and how it discovers them.

**Key decisions:**

1. **Known files vs discovered files**: Does the user provide file paths, or must the agent find them?
2. **Token budget**: How many files can fit in context? Estimate: files x avg_lines x 4 tokens/line.
3. **Exploration strategy**: Targeted reads, grep discovery, or progressive disclosure (ls → key files → source)?

For most coding agents, use the explore-then-act pattern: read-only exploration first, then focused editing in a second phase or fresh context.

See [`context-management.md`](context-management.md) for detailed strategies including token budget allocation, large file handling, and multi-agent context management.

**Context output:** A brief context strategy: "Agent receives file paths from user, reads each file, then reads imported dependencies up to 1 level deep. Budget: ~30 files."

---

## Step 8: Instruction Writing

The system prompt body is the most important part of the agent definition. For coding agents, follow this structure.

### 8.1 Lead with Identity and Purpose

First line establishes what the agent is and what it does:

```markdown
You are a code review agent that analyzes TypeScript diffs for correctness,
regression risk, and missing test coverage.
```

Not: "You are a helpful assistant." Not: "You are an AI." State the specific role.

### 8.2 Define Constraints Before Workflow

Constraints come before the workflow because the agent must internalize limits before executing steps.

```markdown
## Constraints
- You must NOT modify any files. You are read-only.
- You must NOT suggest changes outside the diff scope.
- If you cannot determine severity, mark the finding as "needs-review".
- Stop after 8 tool calls if you have not found actionable findings.
```

### 8.3 Use the Explore-Then-Act Pattern

For agents that both read and write, structure the workflow in two explicit phases:

```markdown
## Workflow
### Phase 1: Exploration (read-only)
1. Read the target files listed in the task
2. Grep for related imports and type definitions
3. Run existing tests to establish baseline: `npm test -- --related <files>`
4. Summarize findings before proceeding

### Phase 2: Implementation
5. Make changes to the target files only
6. Run tests again to verify no regressions
7. Run the linter on changed files
```

### 8.4 Specify the Output Contract

Tell the agent exactly what format to produce. Coding agents that return unstructured prose are hard to consume programmatically or by coordinator agents.

```markdown
## Output Format
Return findings as a structured list:

### Finding: <title>
- **Severity**: critical | high | medium | low
- **File**: <path>:<line>
- **Issue**: <one sentence>
- **Evidence**: <code snippet or reasoning>
- **Suggestion**: <concrete fix or "needs human review">
```

### 8.5 Include Self-Verification Steps

Build verification into the workflow, not as an afterthought:

```markdown
### Phase 3: Verification
8. Run the full test suite for affected modules
9. Grep for TODO or FIXME you may have introduced
10. Confirm no files outside owned_files were modified
11. If any test fails, revert your last change and report the failure
```

### 8.6 Worked Example

Putting it all together for a test generator agent:

```markdown
You are a test generator agent that creates Jest test files for TypeScript modules.

## Constraints
- Only create files matching `*.test.ts` or `*.spec.ts`
- Never modify source files (only test files)
- Every generated test must import from the real source module — no mocking the module under test
- If a function has no clear testable behavior, skip it and note why

## Workflow
### Phase 1: Understand the Code
1. Read the target source file
2. Read its imports to understand types and dependencies
3. Identify public exports and their signatures

### Phase 2: Generate Tests
4. Create a test file next to the source file
5. Write tests for each public export: happy path, edge case, error case
6. Mock only external dependencies (network, filesystem, database)

### Phase 3: Verify
7. Run: npx jest <test-file> --no-coverage
8. If tests fail, read the error output and fix the test (not the source)
9. Re-run until all tests pass
10. Report: number of tests created, functions covered, any skipped functions

## Output Format
### Test Summary
- **File created**: <path>
- **Tests**: <count> passing
- **Coverage**: <list of functions tested>
- **Skipped**: <list of functions skipped with reasons>
```

---

## Step 9: Self-Verification Design

Every coding agent must verify its own work before reporting completion. The verification approach depends on the archetype.

### Run Tests After Edits

Any agent that modifies source code or creates test files must run the relevant test suite:

```bash
# Run related tests only (faster, stays in token budget)
npx jest --findRelatedTests <changed-files>
# or
pytest <changed-files> -x --tb=short
```

### Grep for Anti-Patterns in Output

After generating code, search for known problems:

```bash
# Check for debug statements left behind
grep -rn "console.log\|debugger\|TODO.*HACK" <changed-files>
# Check for incomplete implementations
grep -rn "throw new Error.*not implemented" <changed-files>
```

### Compare Before/After Behavior

For refactoring agents:

1. Run tests before changes (capture baseline)
2. Make changes
3. Run tests after changes (compare to baseline)
4. If any test that passed before now fails, revert

### Assign a Separate Verifier (Multi-Agent Teams)

For multi-agent teams, never let an agent verify its own work. Spawn a fresh agent with:
- Read-only tools
- The list of changed files
- The original task description
- An adversarial posture: "Find problems with these changes"

### Verification Design Output

State the verification approach: "Run pytest on changed files, grep for TODO/FIXME, report any test failures."

---

## Step 10: Smoke Testing

Before deploying the agent, run these five tests in order. Each tests a different failure mode.

### Test 1: Simple Happy Path

Give the agent a clean, small, well-structured input that should produce a correct result with no ambiguity. If this fails, the agent definition has a fundamental problem.

Example for a Code Reviewer: a diff with one obvious bug.

### Test 2: Edge Case — Empty or Minimal Input

Give the agent an empty file, an empty diff, or a file with no relevant content. The agent should handle this gracefully, not hallucinate findings or crash.

Example: review an empty diff. Expected: "No changes to review."

### Test 3: Large File

Give the agent a file with 1000+ lines. Verify it does not exceed context limits, does not truncate analysis, and still produces structured output.

### Test 4: Missing File

Reference a file path that does not exist. The agent should report the missing file, not hallucinate its contents.

### Test 5: Multi-File Task

Give the agent a task spanning 3-5 files with dependencies between them. Verify it discovers and reads the related files, not just the ones explicitly listed.

**Smoke test output:** Pass/fail for each test with notes on any failures to fix.

### Extension-Robustness Gate

For agents that edit existing code—especially refactoring and migration agents—one-shot smoke tests are necessary but insufficient. Before readiness, run at least one sequence of three or more checkpoints in which the external specification evolves:

1. Begin checkpoint 1 from an empty or controlled baseline workspace.
2. At every later checkpoint, preserve the same workspace produced by the agent; do not replace it with a reference solution.
3. Start a fresh conversation/context for each checkpoint so the agent must recover design intent from the current code rather than hidden transcript memory.
4. Add the new behavior without revealing internal interfaces or test implementation details.
5. Retain and rerun every prior checkpoint's regression tests alongside the new checkpoint tests.
6. Record correctness, cost, and maintainability signals at each checkpoint rather than only the final pass/fail result.

Passing the first checkpoint or all current tests does not establish extension robustness. SlopCodeBench found that planning- and quality-oriented prompt interventions improved initial structure but did not halt degradation across repeated edits; use them as setup aids, not as substitutes for the carried-workspace sequence.

For detailed benchmark construction and hidden-test design, use [`../../qa-agent-testing/SKILL.md`](../../qa-agent-testing/SKILL.md). For checkpoint lineage, trajectory metrics, regression packs, and cost telemetry, use [`../../ai-coding-agents-observability-evals/SKILL.md`](../../ai-coding-agents-observability-evals/SKILL.md).

---

## Step 11: Iteration Loop

After the initial smoke tests, deploy the agent on real tasks and iterate.

### Observe Real Behavior

Run the agent on 5-10 real tasks. For each run, note:
- Did it produce the correct output?
- Did it use tools it did not need?
- Did it miss files it should have read?
- Did it exceed maxTurns?
- Did it produce output in the wrong format?

### Identify Failure Patterns

Common failure categories for coding agents:

| Failure | Cause | Fix |
|---------|-------|-----|
| Hallucinated files/functions | Missing context | Add exploration phase, read imports |
| Scope creep (touched unrelated files) | Vague constraints | Add explicit owned_files list |
| Output format drift | Weak output contract | Add a concrete example in the prompt |
| Exceeded maxTurns | Task too large | Split into sub-tasks or increase maxTurns |
| Missed edge cases | No edge case examples | Add edge cases to prompt examples |
| Tests pass vacuously | Mocked the module under test | Add constraint: "import from real source" |

### Tighten or Expand

- If the agent does too much: add constraints, reduce tools, lower maxTurns
- If the agent does too little: add exploration steps, increase maxTurns, add tools
- If the output is inconsistent: add a concrete output example, not just a format description

### Re-Test After Changes

After modifying the agent definition, re-run the smoke tests from Step 10. Regressions in agent behavior are common after prompt changes.

### When to Stop Iterating

The agent is ready when:
- It passes all 5 smoke tests consistently
- If it edits, refactors, or migrates code, it passes at least one 3+ checkpoint evolving-spec sequence with fresh context, a carried workspace, and all prior regression tests retained
- It produces correct output on 8/10 real tasks
- Failures are at the boundary of the task (genuinely hard cases), not at the core
- The output format is consistent across runs

---

## Quick Reference: Creation Checklist

```
[ ] Task classified (scope, input/output, deterministic/open-ended)
[ ] Single vs multi-agent decided
[ ] Archetype selected
[ ] Platform selected
[ ] Template instantiated with correct frontmatter
[ ] Tools scoped to minimum needed
[ ] Context strategy defined
[ ] System prompt written (identity, constraints, workflow, output, verification)
[ ] Self-verification approach built into workflow
[ ] Smoke tests passed (happy path, empty, large, missing, multi-file)
[ ] Edit/refactor/migration agent passed a 3+ checkpoint evolving-spec sequence
[ ] Iterated on 5+ real tasks
```
