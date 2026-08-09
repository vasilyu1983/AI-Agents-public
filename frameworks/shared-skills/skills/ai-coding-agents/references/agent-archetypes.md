# Coding Agent Archetypes

Six single-agent patterns for code-touching tasks. Each archetype defines purpose, tools, frontmatter, prompt structure, context requirements, output contract, verification, and failure modes.

For multi-agent patterns (coordinator teams, fork subagents, peer swarms), see [`multi-agent-coding-patterns.md`](multi-agent-coding-patterns.md).

---

## Table of Contents

- [Archetype Overview](#archetype-overview)
- [1. Code Reviewer](#1-code-reviewer)
- [2. Test Generator](#2-test-generator)
- [3. Refactoring Agent](#3-refactoring-agent)
- [4. Migration Agent](#4-migration-agent)
- [5. Documentation Agent](#5-documentation-agent)
- [6. Security Scanner](#6-security-scanner)
- [Archetype Selection Matrix](#archetype-selection-matrix)
- [Customizing Archetypes](#customizing-archetypes)

---

## Archetype Overview

| Archetype | Mode | Core Tools | maxTurns | Template |
|-----------|------|-----------|----------|----------|
| Code Reviewer | Read-only | Read, Grep, Glob, Bash | 8 | `code-reviewer.md` |
| Test Generator | Read + Write | Read, Write, Edit, Bash, Grep | 15 | `test-generator.md` |
| Refactoring Agent | Edit (behavior-preserving) | Read, Edit, Bash, Grep, Glob | 20 | `refactoring-agent.md` |
| Migration Agent | Batch edit | Read, Write, Edit, Bash, Grep, Glob | 25 | `migration-agent.md` |
| Documentation Agent | Read + Write (docs only) | Read, Write, Grep, Glob | 12 | Universal template |
| Security Scanner | Read-only | Read, Grep, Glob, Bash | 10 | `security-scanner.md` |

---

## 1. Code Reviewer

### Purpose

Analyze diffs, files, or pull requests for correctness, regression risk, missing test coverage, and code quality issues. Produces severity-ordered findings. Modeled on Claude Code's Explore agent pattern: read-only, parallel tool calls, no file modifications.

**When to use:** After code changes, before commits, during PR review, when investigating a reported bug in a diff.

### Required Tools

| Tool | Rationale |
|------|-----------|
| Read | Read changed files and their surrounding context |
| Grep | Search for related usages, callers, type definitions |
| Glob | Discover test files, config files, related modules |
| Bash | Run read-only commands: `git diff`, `git log`, `git show`, `npx tsc --noEmit` |

Bash is constrained to read-only commands. The system prompt explicitly disallows write operations.

### Recommended Frontmatter

```yaml
---
name: code-reviewer
description: "Review code changes for bugs, regressions, and missing tests. Use after code modifications or before commits."
tools: Read, Grep, Glob, Bash
maxTurns: 8
model: sonnet
permissionMode: default
---
```

Model: `sonnet` is sufficient for most review tasks. Use `opus` only for complex architectural review where deep reasoning about system-level implications matters.

### System Prompt Structure

```
1. Identity: "You are a code review agent that..."
2. Constraints:
   - Read-only: must NOT modify files
   - Scope: review only the changed files and directly related code
   - Stop condition: report after reading all changed files, do not explore indefinitely
3. Workflow:
   a. Read the diff or changed file list
   b. For each changed file: read the file, read callers/importers (1 level)
   c. Check for: logic errors, null/undefined risks, type mismatches,
      missing error handling, untested branches
   d. Run type checker if available (npx tsc --noEmit)
4. Output contract: severity-ordered findings (see below)
5. Edge cases: empty diff -> "No changes to review"
```

### Context Requirements

- The diff or list of changed files (provided by user or extracted via `git diff`)
- Surrounding code for each changed file (the agent reads these)
- Type definitions and interfaces imported by changed files (agent discovers via grep)
- Existing test files for the changed modules (agent discovers via glob)

### Output Contract

```markdown
## Review Summary
**Files reviewed**: <count>
**Findings**: <count by severity>

### Findings

#### [CRITICAL] <title>
- **File**: src/auth/validate.ts:42
- **Issue**: Null dereference when token is undefined
- **Evidence**: `const user = token.claims.sub` -- token can be null per line 38
- **Suggestion**: Add null check before accessing claims

#### [HIGH] <title>
...

#### [MEDIUM] <title>
...

#### [LOW] <title>
...

### Verification Gaps
- <list of areas that need manual review or are untestable>
```

Severity levels:
- **CRITICAL**: Will cause runtime errors, data loss, or security vulnerabilities
- **HIGH**: Likely bugs or significant logic errors
- **MEDIUM**: Code quality, maintainability, missing edge case handling
- **LOW**: Style, naming, minor improvements

### Self-Verification Approach

- Compare the number of findings to the number of changed files. Zero findings on a non-trivial diff is suspicious -- re-examine.
- Verify each finding references a real file and line number (not hallucinated).
- Check that suggested fixes are syntactically valid.

### Common Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Hallucinated line numbers | Did not read the actual file | Require Read before any finding |
| Findings outside diff scope | No scope constraint | Add "only review changed lines and their immediate context" |
| All findings are LOW severity | Overly cautious | Add examples of CRITICAL/HIGH findings in prompt |
| Missed type errors | Did not run type checker | Add tsc/mypy step to workflow |
| Too many findings (noise) | No severity filter | Add "report at most 10 findings, prioritized by severity" |

---

## 2. Test Generator

### Purpose

Read existing code, generate test files that exercise real behavior, run the tests, and verify they pass. The key challenge is avoiding vacuous tests that pass by testing mocks instead of real code.

**When to use:** After writing new code, for modules with no test coverage, when backfilling tests before a refactor.

### Required Tools

| Tool | Rationale |
|------|-----------|
| Read | Read source files to understand what to test |
| Write | Create new test files |
| Edit | Fix failing tests (modify the test, not the source) |
| Bash | Run test runner (jest, pytest, vitest, go test) |
| Grep | Find exports, function signatures, existing test patterns |

### Recommended Frontmatter

```yaml
---
name: test-generator
description: "Generate tests for source files and verify they pass. Use when adding test coverage for new or untested code."
tools: Read, Write, Edit, Bash, Grep
maxTurns: 15
model: sonnet
permissionMode: acceptEdits
---
```

maxTurns is higher (15) because the agent needs turns for: read source, read deps, write tests, run tests, fix failures, re-run.

### System Prompt Structure

```
1. Identity: "You are a test generator that creates [framework] tests for [language] code."
2. Constraints:
   - Only create test files (*.test.ts, *.spec.ts, *_test.py, *_test.go)
   - Never modify source files
   - Every test must import from the real module -- no mocking the module under test
   - Mock only external dependencies (network, DB, filesystem)
   - If a function has no testable behavior, skip it and explain why
3. Workflow:
   Phase 1 - Understand:
   a. Read the target source file
   b. Read imported types and dependencies
   c. Identify public exports and their signatures
   d. Check for existing tests (glob for test files nearby)
   Phase 2 - Generate:
   e. Create test file with proper imports
   f. For each export: happy path test, edge case test, error case test
   g. Use real function calls, not mocked implementations
   Phase 3 - Verify:
   h. Run tests: npx jest <file> or pytest <file>
   i. If tests fail: read error, fix the test (not the source), re-run
   j. Repeat until all tests pass (max 3 fix cycles)
4. Output contract: test summary with coverage info
```

### Context Requirements

- Target source file path (provided by user)
- Dependencies imported by the target (agent discovers via reading imports)
- Type definitions used by the target (agent reads these)
- Existing test files in the same directory (agent discovers via glob to match patterns)
- Test framework config (jest.config, pytest.ini -- agent reads to understand test setup)

### Output Contract

```markdown
### Test Summary
- **File created**: tests/auth/validate.test.ts
- **Tests**: 12 passing, 0 failing
- **Functions covered**: validateToken, refreshToken, parseJWT, isExpired
- **Skipped**: internalHelper (private, no direct testable surface)
- **Edge cases tested**: null token, expired token, malformed JWT, empty claims
```

### Self-Verification Approach

1. Run the generated tests -- they must all pass.
2. Verify each test calls the real function (grep for actual function name in test file).
3. Check that test assertions are non-trivial (not just `expect(true).toBe(true)`).
4. If the test file has zero assertions, it is vacuous -- re-generate.

### Common Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Tests pass but test nothing (vacuous) | Mocked the module under test | Constraint: "import from real module, never mock it" |
| Tests import nonexistent functions | Hallucinated API | Require reading the file first, test only exports found |
| Tests fail on setup (not the code) | Wrong test framework config | Read jest.config/pytest.ini before writing tests |
| Tests pass locally, fail in CI | Environment-dependent setup | Use only relative imports, no hardcoded paths |
| Too many tests, exceeds token budget | Testing every line | Limit to public exports and critical paths |

---

## 3. Refactoring Agent

### Purpose

Make structural changes to code while preserving existing behavior. Must run the existing test suite before AND after changes to prove behavior is preserved.

**When to use:** Extracting functions/classes, renaming across a module, restructuring file layout, reducing code duplication, simplifying complex functions.

### Required Tools

| Tool | Rationale |
|------|-----------|
| Read | Read files to understand current structure |
| Edit | Make targeted changes to existing files (not Write -- refactoring modifies, not creates) |
| Bash | Run tests before/after, run linter, run type checker |
| Grep | Find all usages of renamed/moved symbols |
| Glob | Discover related files, test files, config files |

Edit is preferred over Write for refactoring because Edit makes targeted changes while preserving the rest of the file. Write replaces the entire file, increasing the risk of accidental deletions.

### Recommended Frontmatter

```yaml
---
name: refactoring-agent
description: "Refactor code structure while preserving behavior. Use for extraction, renaming, deduplication, or simplification tasks."
tools: Read, Edit, Bash, Grep, Glob
maxTurns: 20
model: sonnet
permissionMode: acceptEdits
isolation: worktree
---
```

`isolation: worktree` is recommended. The agent works in a git worktree so changes can be discarded if tests fail. This is the safest pattern for structural changes.

### System Prompt Structure

```
1. Identity: "You are a refactoring agent that restructures code while preserving behavior."
2. Constraints:
   - Only modify files in owned_files list
   - Behavior must be identical before and after (test suite is the proof)
   - No new features, no bug fixes -- structural changes only
   - If tests fail after changes, revert and report
3. Workflow:
   Phase 1 - Baseline:
   a. Read all files in owned_files
   b. Run existing tests: capture pass/fail state
   c. Run type checker: capture error count
   d. If tests already fail, stop and report -- do not refactor broken code
   Phase 2 - Refactor:
   e. Plan changes (list what moves where)
   f. Make changes one logical step at a time
   g. After each step: run tests, run type checker
   h. If any step breaks tests, revert that step
   Phase 3 - Verify:
   i. Run full test suite -- must match baseline
   j. Run type checker -- error count must not increase
   k. Grep for any TODO/FIXME introduced
   l. Report changes made and verification results
4. Output contract: change summary with before/after test results
```

### Context Requirements

- owned_files list (provided by user or coordinator)
- All imports and importers of owned files (agent discovers via grep)
- Test files for owned modules (agent discovers via glob)
- Type definitions used by owned files

### Output Contract

```markdown
### Refactoring Summary
- **Files modified**: src/auth/validate.ts, src/auth/helpers.ts
- **Changes**:
  - Extracted `parseTokenClaims` from `validateToken` (was 45 lines, now 12 + 15)
  - Moved shared helpers to `src/auth/helpers.ts`
- **Tests before**: 24 passing, 0 failing
- **Tests after**: 24 passing, 0 failing
- **Type errors before**: 0
- **Type errors after**: 0
```

### Self-Verification Approach

1. Run tests before changes (baseline).
2. Run tests after each logical change step.
3. Run tests after all changes (final).
4. Test count must not decrease. Test pass count must not decrease.
5. Type checker error count must not increase.

### Common Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Scope creep -- modified unrelated files | No owned_files constraint | Add explicit file list, grep to verify no other files changed |
| Tests pass but behavior changed | Tests are incomplete | Note this risk in output; cannot fully mitigate with tests alone |
| Introduced circular imports | Moved code without checking import graph | Read importers before moving, trace dependency chain |
| Forgot to update re-exports | Renamed symbol but index file still exports old name | Grep for old symbol name across entire module after rename |
| Broke tests by changing internal detail | Tests couple to implementation, not behavior | Report as pre-existing test fragility, do not "fix" the tests |

---

## 4. Migration Agent

### Purpose

Apply a systematic pattern transformation across many files. Examples: upgrading an API version, replacing a deprecated library, migrating a framework (React class components to hooks, Express to Fastify routes).

Uses a checkpoint-and-resume pattern: process files in batches, commit after each batch, so partial progress is preserved.

**When to use:** API version upgrades, framework migrations, library replacements, deprecation cleanup across 10+ files.

### Required Tools

| Tool | Rationale |
|------|-----------|
| Read | Read files to identify migration targets |
| Write | Create new files when migration requires new file structure |
| Edit | Transform existing files with the new pattern |
| Bash | Run tests, build, commit after each batch |
| Grep | Find all files matching the old pattern |
| Glob | Discover migration candidates by file name/extension |

### Recommended Frontmatter

```yaml
---
name: migration-agent
description: "Apply pattern transformation across files in batches with checkpoints. Use for API upgrades, library replacements, or framework migrations."
tools: Read, Write, Edit, Bash, Grep, Glob
maxTurns: 25
model: sonnet
permissionMode: acceptEdits
isolation: worktree
---
```

maxTurns is 25 because migrations touch many files and need cycles for: discover targets, process batch, test batch, commit, repeat.

### System Prompt Structure

```
1. Identity: "You are a migration agent that transforms [old pattern] to [new pattern] across a codebase."
2. Constraints:
   - Process files in batches of 3-5
   - After each batch: run tests, commit if passing
   - If a batch fails tests, revert that batch and report the problematic files
   - Never modify files outside the migration scope
   - Preserve all existing behavior -- this is a pattern change, not a feature change
3. Workflow:
   Phase 1 - Discover:
   a. Grep/glob for all files containing the old pattern
   b. Count total migration targets
   c. Read 2-3 examples to understand variations in the old pattern
   d. Plan the transformation rule
   Phase 2 - Migrate (per batch):
   e. Read next batch of 3-5 files
   f. Apply transformation to each file
   g. Run tests for affected modules
   h. If tests pass: git add + git commit with message "[migration] Batch N: <files>"
   i. If tests fail: revert batch, log problematic files, continue to next batch
   Phase 3 - Report:
   j. Summary: files migrated, files skipped, files failed
   k. List any files that need manual migration (too complex for pattern match)
4. Output contract: migration progress report
```

### Context Requirements

- The old pattern and new pattern (provided by user, ideally with a before/after example)
- Discovery scope (which directories/file types to search)
- Test command for verification
- The agent discovers migration candidates via grep/glob

### Output Contract

```markdown
### Migration Report
- **Pattern**: `oldApi.fetch(url)` to `newApi.request({ url })`
- **Total candidates**: 47 files
- **Migrated**: 42 files (batches 1-9, all committed)
- **Failed**: 3 files (tests broke -- see details below)
- **Skipped**: 2 files (pattern too complex for automated migration)

### Failed Files
- `src/legacy/connector.ts`: Uses dynamic pattern construction, needs manual review
- `src/api/batch.ts`: Circular dependency exposed by new import
- `src/api/stream.ts`: Streaming API has no equivalent in new library

### Commits
- `abc1234` [migration] Batch 1: src/api/users.ts, src/api/posts.ts, src/api/comments.ts
- `def5678` [migration] Batch 2: ...
```

### Self-Verification Approach

1. Run tests after each batch -- only commit if passing.
2. After all batches: run the full test suite.
3. Grep for any remaining instances of the old pattern -- these are missed migrations.
4. Run the build to catch import/compilation errors.

### Common Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Partial migration leaves inconsistent state | No checkpoint pattern | Commit after each passing batch |
| Missed variations of the old pattern | Single grep query too narrow | Use multiple grep patterns, review a sample first |
| Tests pass but runtime breaks | Tests don't cover the migrated paths | Note this risk; recommend manual testing of migrated paths |
| Import graph breaks | New library has different module structure | Read new library's exports before migrating imports |
| Token budget exceeded | Too many files in context | Process in small batches, clear context between batches |

---

## 5. Documentation Agent

### Purpose

Read source code and generate or update documentation. All documentation claims must be anchored to actual source code. The agent must never invent functions, parameters, or behaviors that do not exist in the code.

**When to use:** Generating API docs from source, updating README after code changes, creating onboarding docs for a module, syncing docs with current code state.

### Required Tools

| Tool | Rationale |
|------|-----------|
| Read | Read source files to extract documentation content |
| Write | Create or overwrite documentation files |
| Grep | Find function signatures, exports, types, existing doc references |
| Glob | Discover source files, existing docs, README locations |

No Bash or Edit. Documentation agents create/replace doc files (Write) and do not need to run tests or edit source code.

### Recommended Frontmatter

```yaml
---
name: documentation-agent
description: "Generate or update documentation from source code. Use when docs are missing, stale, or need to match current code state."
tools: Read, Write, Grep, Glob
maxTurns: 12
model: sonnet
---
```

### System Prompt Structure

```
1. Identity: "You are a documentation agent that generates [type of docs] from source code."
2. Constraints:
   - Every documented function, type, or API must exist in the source code
   - Never invent parameters, return types, or behaviors
   - Include file:line references for every documented item
   - If source code is ambiguous, note uncertainty rather than guessing
   - Do not modify source code
3. Workflow:
   Phase 1 - Discover:
   a. Glob for source files in the target directory
   b. Read package.json/pyproject.toml for project metadata
   c. Grep for public exports, function signatures, class definitions
   Phase 2 - Read:
   d. Read each source file, extract: function name, parameters, return type, JSDoc/docstring
   e. Read existing docs to understand current state and format
   Phase 3 - Write:
   f. Generate documentation following the project's existing doc format
   g. Anchor every claim to a source file and line number
   h. Flag undocumented exports that need human attention
4. Output contract: documentation files with source anchors
```

### Context Requirements

- Target directory or file list (provided by user)
- Existing documentation format and location (agent discovers via glob)
- Project metadata (package.json, README -- agent reads)
- Source files with exports (agent discovers via grep for `export`, `def`, `func`, `class`)

### Output Contract

```markdown
### Documentation Summary
- **Files documented**: 5 source files, 1 API reference document generated
- **Functions documented**: 23
- **Types documented**: 8
- **Undocumented exports**: 3 (flagged for manual documentation)
- **Source anchors**: Every entry links to file:line in source
```

### Self-Verification Approach

1. For every documented function: grep the source to confirm it exists with the documented signature.
2. For every documented parameter: verify it appears in the function signature.
3. For every documented return type: verify it matches the source.
4. Count documented items vs actual public exports -- flag any gap.

### Common Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Hallucinated functions/APIs | Did not read source first | Require Read before writing any docs |
| Documented private internals | No filter for public vs private | Grep for `export` keyword, ignore un-exported symbols |
| Docs drift from code | One-time generation, no update workflow | Include source file:line anchors for future verification |
| Wrong parameter types | Inferred instead of reading | Read type annotations, JSDoc, or docstrings |
| Inconsistent format | No format reference | Read existing docs first, match their structure |

---

## 6. Security Scanner

### Purpose

Read-only security analysis of source code. Produces severity-ordered findings with evidence (code snippets, vulnerability category, CWE reference where applicable, and remediation guidance).

**When to use:** Pre-deployment security review, dependency audit, checking for hardcoded secrets, reviewing authentication/authorization logic, input validation audit.

### Required Tools

| Tool | Rationale |
|------|-----------|
| Read | Read source files for detailed analysis |
| Grep | Search for security-sensitive patterns (passwords, tokens, SQL concatenation, unsafe DOM writes) |
| Glob | Discover configuration files, environment files, dependency manifests |
| Bash | Run read-only commands: `npm audit`, `pip audit`, `git log --oneline` for recent changes |

Bash is constrained to read-only security commands. No file modification.

### Recommended Frontmatter

```yaml
---
name: security-scanner
description: "Scan code for security vulnerabilities with severity-ordered findings. Use before deployments or when reviewing security-sensitive changes."
tools: Read, Grep, Glob, Bash
maxTurns: 10
model: sonnet
---
```

### System Prompt Structure

```
1. Identity: "You are a security scanning agent that identifies vulnerabilities in [language/framework] code."
2. Constraints:
   - Read-only: must NOT modify files
   - Report only findings with evidence (code snippet + explanation)
   - Do not report style issues as security findings
   - If severity is uncertain, err toward reporting with a "needs-review" flag
   - False positives erode trust -- include reasoning for each finding
3. Workflow:
   Phase 1 - Discovery:
   a. Glob for sensitive file types: .env*, *config*, *secret*, *.key, *.pem
   b. Grep for high-signal patterns: password, secret, token, api_key,
      SQL string concatenation, unsafe DOM manipulation APIs
   c. Read dependency manifest (package.json, requirements.txt, go.mod)
   d. Run dependency audit: npm audit --json or pip audit --format json
   Phase 2 - Analysis:
   e. For each finding from discovery: read the file, understand context
   f. Determine if the pattern is a real vulnerability or a false positive
   g. Classify: injection, auth bypass, data exposure, misconfiguration, dependency
   h. Assign severity based on exploitability and impact
   Phase 3 - Report:
   i. Produce severity-ordered findings with evidence
   j. Separate confirmed findings from needs-review items
4. Output contract: security report (see below)
```

### Context Requirements

- Target directory or file list (provided by user, or scan entire project)
- Dependency manifests (package.json, requirements.txt, go.mod)
- Configuration files (.env, docker-compose, terraform)
- Authentication and authorization modules (agent discovers via grep)

### Output Contract

```markdown
## Security Scan Report
**Scope**: <directory or file list>
**Files scanned**: <count>
**Findings**: <count by severity>

### Confirmed Findings

#### [CRITICAL] Hardcoded database credentials
- **File**: src/config/database.ts:15
- **Category**: CWE-798 (Hard-coded Credentials)
- **Evidence**: `const DB_PASSWORD = "prod_secret_123"`
- **Impact**: Database credentials exposed in source control
- **Remediation**: Move to environment variable, rotate credential immediately

#### [HIGH] SQL injection via string concatenation
- **File**: src/api/users.ts:42
- **Category**: CWE-89 (SQL Injection)
- **Evidence**: `db.query("SELECT * FROM users WHERE id = " + userId)`
- **Impact**: Arbitrary SQL via user-controlled input
- **Remediation**: Use parameterized query: `db.query("SELECT * FROM users WHERE id = $1", [userId])`

### Needs Review
- <items where the agent could not determine if the pattern is exploitable>

### Dependency Vulnerabilities
- <output from npm audit / pip audit, summarized>
```

### Self-Verification Approach

1. Every finding must include a real file path and line number -- grep to confirm.
2. Every code snippet in evidence must match the actual file content.
3. Cross-check: if a hardcoded secret is found, grep for it elsewhere in the codebase.
4. Compare finding count against grep hit count -- large discrepancies suggest missed items.

### Common Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| False positives (test data flagged as secrets) | No context awareness | Read surrounding code -- test fixtures and examples are not vulnerabilities |
| Missed context-dependent vulnerabilities | Pattern matching without data flow analysis | Note limitation: "static analysis only, no data flow tracing" |
| Dependency audit output too large | Hundreds of vulnerabilities in transitive deps | Summarize by severity, show only critical/high in detail |
| Missed .env files in .gitignore | Only scanned tracked files | Explicitly glob for .env* regardless of git tracking |
| Stale findings on dead code | Scanned files no longer imported | Note: "verify this code path is reachable" |

---

## Archetype Selection Matrix

Use this matrix when the task does not clearly match one archetype.

| Signal | Best Archetype |
|--------|---------------|
| "Find bugs in this diff" | Code Reviewer |
| "Add tests for this module" | Test Generator |
| "Extract this into a separate function/class" | Refactoring Agent |
| "Upgrade all X calls to Y" | Migration Agent |
| "Write API docs for this module" | Documentation Agent |
| "Check this for security issues" | Security Scanner |
| "Review and fix this code" | Two agents: Code Reviewer then Refactoring Agent |
| "Add tests and fix the bugs they find" | Two agents: Test Generator then Refactoring Agent |
| "Migrate and verify security" | Two agents: Migration Agent then Security Scanner |

For tasks requiring two archetypes, use a coordinator-led team or sequential execution. See [`multi-agent-coding-patterns.md`](multi-agent-coding-patterns.md).

---

## Customizing Archetypes

Archetypes are starting points. Common customizations:

**Narrowing scope:** Restrict to a specific language, framework, or directory. Example: a Code Reviewer that only reviews React component files.

**Changing model:** Use `opus` for agents that need deep reasoning about complex code interactions. Use `sonnet` for most straightforward tasks. Use `haiku` for high-volume, simple pattern matching.

**Adjusting maxTurns:** If the agent consistently finishes early, lower maxTurns to save tokens. If it runs out of turns, increase -- but also check if the task should be split.

**Adding domain knowledge:** Include framework-specific rules in the system prompt. Example: for a React Code Reviewer, add rules about hook dependencies, key props, and effect cleanup.

**Combining archetypes:** If a task requires both reading and writing in a way that spans two archetypes, start from the more complex one and add constraints from the simpler one. Do not create a "super agent" that tries to do everything.
