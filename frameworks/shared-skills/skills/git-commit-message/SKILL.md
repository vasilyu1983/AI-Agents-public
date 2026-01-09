---
name: git-commit-message
description: Auto-generates conventional commit messages from git diffs with tiered format enforcement. Analyzes staged changes to produce meaningful commit messages following Conventional Commits specification.
---

# Git Commit Message Generator

**Auto-generates conventional commit messages from git diffs with tiered format enforcement**

## Purpose

Analyze staged git changes and generate concise, meaningful commit messages following a tiered Conventional Commits specification. This skill examines file modifications, additions, and deletions to infer the type and scope of changes, producing commit messages that match the importance of the change - from detailed documentation for critical features to concise messages for minor updates.

**Key Innovation**: Three-tier format system that balances thoroughness for critical commits (feat, fix, security) with efficiency for routine changes (docs, chore, style).

## When This Skill Activates

- When `/commit-msg` command is invoked
- When pre-commit hook is triggered (before git commit)
- When user requests commit message suggestions
- When analyzing changes before creating a commit

## Core Capabilities

**1. Diff Analysis**
- Parse `git diff --staged` output
- Identify modified, added, and deleted files
- Analyze code changes (additions, deletions, modifications)
- Detect patterns across multiple files

**2. Change Classification**
- Determine commit type from changes:
  - `feat`: New features or functionality
  - `fix`: Bug fixes
  - `refactor`: Code restructuring without behavior change
  - `docs`: Documentation changes
  - `style`: Formatting, whitespace, code style
  - `test`: Adding or modifying tests
  - `chore`: Build process, dependencies, tooling
  - `perf`: Performance improvements
  - `ci`: CI/CD configuration changes
  - `revert`: Reverting previous commits

**3. Scope Detection**
- Infer scope from file paths and patterns:
  - Directory names (e.g., `api`, `auth`, `ui`)
  - File name patterns (e.g., `*.test.js` → `tests`)
  - Framework conventions (e.g., `components/`, `services/`)

**4. Message Generation**
- Format: `type(scope): description`
- Keep description under 50 characters (ideal) or 72 characters (max)
- Use imperative mood ("add" not "added")
- Focus on "what" and "why", not "how"
- Provide 2-3 alternative suggestions

## Tier System: Smart Format Enforcement

This skill uses a **three-tier format system** that matches message detail to commit criticality:

### Tier 1: Critical Commits (feat, fix, perf, security)

**Requirements**: Detailed documentation with impact statement

**Format**:
```
type(scope): summary line (max 50 chars)

- Detailed description point 1
- Detailed description point 2
- Detailed description point 3

This change [impact statement describing user-facing benefit or risk addressed].

Affected files/components:
- path/to/file1
- path/to/file2
```

**Why**: Features, fixes, and performance changes affect users directly and need thorough documentation for future reference and changelog generation.

### Tier 2: Standard Commits (refactor, test, build, ci)

**Requirements**: Brief context and file list

**Format**:
```
type(scope): summary line (max 72 chars)

Brief explanation of what changed and why (1-2 sentences).

Files: path/to/file1, path/to/file2
```

**Why**: Internal improvements need context for maintainability but don't require extensive documentation.

### Tier 3: Minor Commits (docs, style, chore)

**Requirements**: Summary line, optional description

**Format**:
```
type(scope): summary line (max 72 chars)

[Optional: Additional context if helpful]
```

**Why**: Documentation and routine maintenance are self-explanatory from the diff; verbose messages add noise.

## Workflow

```text
1. Get staged changes → git diff --staged
2. Analyze changes:
   - Count files modified/added/deleted
   - Identify primary change type using analysis patterns
   - Detect scope from project structure (config.yaml)
   - Determine tier (1/2/3) based on commit type
   - Extract key modifications
3. Generate commit messages:
   - Apply tier-appropriate format
   - Primary suggestion (best match)
   - Alternative 1 (different scope/angle)
   - Alternative 2 (broader/narrower focus)
4. Validate against rules:
   - Check forbidden patterns
   - Verify required elements present
   - Ensure length limits
5. Present to user with explanation and tier info
```

## Output Format

```
[NOTE] Suggested Commit Messages (based on X files changed)

PRIMARY:
feat(api): add user authentication endpoints

ALTERNATIVES:
1. feat(auth): implement JWT token validation
2. feat: add user authentication system

ANALYSIS:
- 3 files modified in src/api/
- New functions: authenticateUser, generateToken
- Primary change: new feature (authentication)
- Scope detected: api/auth
```

## Conventional Commits Quick Reference

**Type Guidelines**:
- `feat`: User-facing features or API additions
- `fix`: Corrects incorrect behavior
- `refactor`: Improves code without changing behavior
- `docs`: README, comments, documentation files
- `style`: Formatting only (prettier, eslint --fix)
- `test`: Test files or test utilities
- `chore`: Build scripts, package updates, config
- `perf`: Measurable performance improvements
- `ci`: GitHub Actions, CircleCI, build pipelines

**Scope Guidelines**:
- Use lowercase
- Be specific but not too narrow
- Match your project's module structure
- Omit if changes span multiple unrelated areas

**Description Guidelines**:
- Start with lowercase verb
- No period at the end
- Be specific and concise
- Focus on user impact for `feat` and `fix`

## Edge Cases

**Multiple unrelated changes**:
- Suggest splitting into separate commits
- If forced to combine, use broader scope or omit scope

**Breaking changes**:

- Append exclamation mark after type/scope (example: feat(api)!: change auth flow)
- Include BREAKING CHANGE in body (handled by user)

**WIP or experimental**:
- Use `chore(wip): description` or `feat(experimental): description`

**No meaningful changes**:
- Detect and warn: "No staged changes detected"
- Suggest `git add` commands

## Integration Points

**Pre-commit hook**: Automatically triggered before commit
**Slash command**: Manual invocation via `/commit-msg`
**Direct skill call**: From other skills or tools

## Best Practices

1. **Analyze context**: Look at file paths, function names, import statements
2. **Prioritize clarity**: Prefer obvious descriptions over clever ones
3. **Respect conventions**: Follow project's existing commit patterns if detected
4. **Avoid hallucination**: Only describe what's actually in the diff
5. **Be concise**: 50 chars is ideal, 72 is maximum for first line

## Example Analyses

**Scenario 1**: New React component
```
Files: src/components/UserProfile.tsx, src/components/UserProfile.test.tsx
Changes: +120 lines, component definition, props interface, tests
Message: feat(components): add UserProfile component
```

**Scenario 2**: Bug fix in API
```
Files: src/api/auth.ts
Changes: -5 +8 lines, fix token expiration check
Message: fix(auth): correct token expiration validation
```

**Scenario 3**: Documentation update
```
Files: README.md, docs/api.md
Changes: +45 lines documentation
Message: docs: update API documentation and README
```

**Scenario 4**: Dependency update
```
Files: package.json, package-lock.json
Changes: version bumps for eslint, typescript
Message: chore(deps): update eslint and typescript
```

## Analysis Patterns: Smart Type Detection

The skill uses pattern matching to intelligently detect commit types from diffs:

### feat Detection
- **New files created** (especially in src/, components/, api/)
- **New functions/classes exported** (`export function`, `export class`)
- **New API routes** (`app.get`, `router.post`, etc.)
- **New templates/skills** (in .claude/, custom-gpt/, etc.)
- **Threshold**: 20+ lines added typically indicates feature

### fix Detection
- **Test file changes** (often indicates bug reproduction)
- **New conditionals** (validation fixes)
- **Error handling additions** (`try`, `catch`, `throw`)
- **Input validation** (`validate`, `sanitize`, `check`)
- **Commit message hints**: Words like "bug", "issue", "error", "crash"

### refactor Detection
- **Balanced changes** (similar additions and deletions)
- **Function renames/moves** (same logic, different location)
- **No new features or fixes**
- **Test coverage unchanged**
- **Keywords**: "extract", "move", "rename", "reorganize"

### docs Detection
- **File patterns**: `.md`, `.txt`, `README`, `CHANGELOG`, `/docs/`
- **Pure documentation changes** (no code modifications)
- **Mixed code+docs**: Prefer code type, note docs in description

### test Detection
- **File patterns**: `test.js`, `spec.ts`, `__tests__/`, `/tests/`
- **Test framework patterns**: `describe`, `it`, `test`, `expect`, `assert`

### style Detection
- **CSS/styling files**: `.css`, `.scss`, `.sass`, `.less`
- **Formatter configs**: `prettier`, `eslint`
- **Whitespace-only changes**
- **Keywords**: "formatting", "indent", "whitespace"

### chore Detection
- **Dependency files**: `package.json`, `requirements.txt`, `Gemfile`
- **Lock files**: `package-lock.json`, `yarn.lock`
- **Config files**: `.gitignore`, `.env`
- **Keywords**: "dependency", "deps", "upgrade", "bump"

## Configuration

**Project-specific configuration** loaded from `config.yaml`:

- **Scope mapping**: Maps directory patterns to scope names (e.g., `frameworks/claude-code-kit/**` → `claude-kit`)
- **Tier rules**: Defines which commit types require which tier format
- **Forbidden patterns**: Blocks commits with generic messages or assistant/tool attribution
- **Analysis patterns**: Customizes type detection logic for your codebase
- **Validation mode**: `strict` (block), `warning` (warn), or `disabled`

**Legacy options** (git config or .commit-template):

- `commit.type.prefer`: Preferred type for ambiguous changes
- `commit.scope.detect`: Enable/disable automatic scope detection
- `commit.length.max`: Maximum description length (default: 72)
- `commit.alternatives.count`: Number of alternatives (default: 2)

## Forbidden Patterns (Validation)

The skill automatically blocks commits with these patterns:

### Generic/Vague Messages

- [FAIL] "Update files" → [OK] "docs: update API reference"
- [FAIL] "Fix stuff" → [OK] "fix(auth): correct token validation"
- [FAIL] "Change code" → [OK] "refactor(utils): simplify date formatting"

### Assistant/Tool Attribution (Per Repository Policy)

- [FAIL] "Generated with Claude Code"
- [FAIL] "Co-Authored-By: Claude <noreply@anthropic.com>"
- [FAIL] Any assistant/tool attribution in commit messages

### Work-in-Progress Markers

- [WARNING] "WIP: feature" (warning - should be squashed before merge)
- [WARNING] "temp: quick fix" (warning - should be squashed)

### Missing Type

- [FAIL] Commits without type prefix (feat, fix, docs, etc.)

## Error Handling

- **No staged changes**: Run `git status` and guide user to `git add` files
- **Binary files only**: Note that commit message should mention file types
- **Merge conflicts**: Detect and suggest `chore: resolve merge conflicts`
- **Git not available**: Graceful failure with helpful error message
- **Forbidden pattern detected**: Show error with examples and block commit (strict mode)
- **Missing required elements**: List what's missing based on tier requirements
- **Length exceeded**: Show character count and suggest shortening

## Integration with Repository

This skill integrates with the AI-Agents repository standards:

- **CLAUDE.md reference**: Mandatory skill usage before commits
- **config.yaml**: Project-specific scope mappings and rules
- **Pre-commit hook**: Automatic activation before git commits
- **CONTRIBUTING.md**: Commit guidelines for contributors

---

## Commit Message Template

**[templates/template-commit-message.md](templates/template-commit-message.md)** — Copy-paste template and good/bad examples.

Use it to standardize `type(scope): summary` messages and keep history automation-friendly.

---

## Security-Sensitive Commits

**[templates/template-security-commits.md](templates/template-security-commits.md)** — Guide for handling security-sensitive changes.

### Key Sections

- **Pre-Commit Security Checklist** — Secrets detection, prohibited patterns
- **Security-Related Commit Types** — Security fix, enhancement, configuration
- **Accidental Secret Commits** — Immediate response, rotation, history cleanup
- **Sensitive File Patterns** — .gitignore templates, files that should never be committed
- **Audit Trail Requirements** — CVE, CVSS, CWE metadata for security commits

### Do / Avoid

#### GOOD: Do

- Run secrets scan before every commit
- Rotate secrets immediately if exposed
- Use environment variables for credentials
- Document security fixes with CVE/CVSS
- Require security team review for auth changes
- Keep .gitignore updated for secret patterns

#### BAD: Avoid

- Committing secrets "temporarily"
- Using hardcoded credentials in tests
- Storing real credentials in example files
- Assuming deleted secrets are safe
- Committing before secrets scan completes
- Using generic commit messages for security fixes

### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **"Add secrets later"** | Secrets committed accidentally | Use env vars from start |
| **Secrets in tests** | Real credentials in repo | Use mocks/test credentials |
| **Force push to hide** | History still recoverable | Rotate + document |
| **Vague security commits** | No audit trail | Include CVE/CVSS |
| **No pre-commit scan** | Secrets reach remote | Install gitleaks hook |

---

## Optional: AI/Automation

> **Note**: AI suggestions should preserve human intent.

- **Commit message suggestions** — Draft from diff analysis
- **Type detection** — Pattern-based commit type inference
- **Scope detection** — Auto-detect from changed paths

### Bounded Claims

- AI-generated messages need human review and modification
- Automated type detection may miss context
- Security commits always need human judgment

---

**Version**: 2.1.0
**Last Updated**: 2025-12-17
**Repository**: AI-Agents (documentation repository)
**Conventional Commits Spec**: <https://www.conventionalcommits.org/>
