# Git Hooks & Automation

Setup and automation patterns for Git hooks, covering Husky, lefthook, lint-staged, commitlint, and custom hook scripts.

## Contents

- Hook Types and Use Cases
- Husky Setup (v9+)
- lefthook Setup
- lint-staged Integration
- commitlint Integration
- Custom Hooks: Secrets, File Size, Branch Naming
- Bypassing Hooks
- Team Distribution Strategies
- Example Configuration: Husky + lint-staged + commitlint
- Do / Avoid
- Related Resources

---

## Hook Types and Use Cases

| Hook | Trigger | Common Use Cases |
|------|---------|-----------------|
| `pre-commit` | Before commit is created | Linting, formatting, type checking, secrets scanning |
| `prepare-commit-msg` | After default message, before editor opens | Auto-insert ticket number, template enforcement |
| `commit-msg` | After message is written | Validate commit message format (commitlint) |
| `pre-push` | Before push to remote | Run tests, check branch naming, prevent push to main |
| `post-merge` | After merge completes | Auto-install dependencies, rebuild, notify |
| `post-checkout` | After checkout completes | Install deps if lockfile changed, environment setup |

---

## Husky Setup (v9+)

Husky v9+ uses a `.husky/` directory with plain shell scripts. No more `.huskyrc` or package.json config.

```bash
# Install
npm install --save-dev husky

# Initialize (creates .husky/ directory and sets prepare script)
npx husky init

# This adds to package.json:
# "scripts": { "prepare": "husky" }
```

### Creating hooks

```bash
# pre-commit hook
echo "npx lint-staged" > .husky/pre-commit

# commit-msg hook
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg

# pre-push hook
echo "npm test" > .husky/pre-push
```

Hook files are plain shell scripts. They must be executable (`chmod +x` is handled by Husky on init).

### Directory structure

```
.husky/
  pre-commit       # Runs before each commit
  commit-msg       # Validates commit message
  pre-push         # Runs before push
```

---

## lefthook Setup

lefthook is a Go-based hook manager. Faster than Husky, language-agnostic, uses a single YAML config.

```bash
# Install (multiple options)
brew install lefthook          # macOS
npm install --save-dev lefthook  # Node projects
go install github.com/evilmartians/lefthook@latest  # Go

# Initialize
npx lefthook install
```

### Configuration

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: "*.{js,ts,tsx}"
      run: npx eslint {staged_files}
    format:
      glob: "*.{js,ts,tsx,json,md}"
      run: npx prettier --check {staged_files}
    typecheck:
      run: npx tsc --noEmit

commit-msg:
  commands:
    commitlint:
      run: npx commitlint --edit {1}

pre-push:
  commands:
    test:
      run: npm test
```

**Why choose lefthook over Husky**:
- Parallel command execution by default
- Single YAML config instead of multiple shell files
- Built-in glob filtering (no need for lint-staged)
- Works for non-Node projects without npm

---

## lint-staged Integration

Run linters only on staged files. Prevents full-project linting on every commit.

```bash
npm install --save-dev lint-staged
```

### Configuration

```json
// package.json or .lintstagedrc.json
{
  "*.{js,ts,tsx}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{json,md,yml}": [
    "prettier --write"
  ],
  "*.css": [
    "stylelint --fix"
  ]
}
```

### How it works

1. `pre-commit` hook triggers lint-staged
2. lint-staged collects staged files
3. Matches files against glob patterns
4. Runs configured commands only on matched staged files
5. Re-stages any auto-fixed files
6. Commit proceeds if all commands exit 0

```bash
# Wired into Husky pre-commit:
# .husky/pre-commit
npx lint-staged
```

---

## commitlint Integration

Validate commit messages against Conventional Commits or a custom schema.

```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
```

### Configuration

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'refactor', 'perf', 'test',
      'docs', 'chore', 'ci', 'build', 'revert'
    ]],
    'scope-empty': [1, 'never'],       // Warn if no scope
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [1, 'always', 100]
  }
};
```

### Wiring to commit-msg hook

```bash
# .husky/commit-msg
npx --no -- commitlint --edit $1
```

### What gets validated

```bash
# Passes
git commit -m "feat(auth): add OAuth2 login"
git commit -m "fix(api): handle null response body"

# Fails
git commit -m "added stuff"        # No type prefix
git commit -m "feat: "             # Empty subject
git commit -m "FEAT(auth): login"  # Type must be lowercase
```

---

## Custom Hooks: Secrets, File Size, Branch Naming

### Secrets Scanning with gitleaks

```bash
# Install gitleaks
brew install gitleaks

# Pre-commit hook
# .husky/pre-commit (append or add to lefthook config)
gitleaks protect --staged --verbose
```

### File Size Limit

Prevent accidentally committing large binaries:

```bash
#!/bin/sh
# .husky/pre-commit or custom script

MAX_SIZE=5242880  # 5 MB in bytes
LARGE_FILES=$(git diff --cached --name-only --diff-filter=ACM | while read f; do
  size=$(wc -c < "$f" 2>/dev/null || echo 0)
  if [ "$size" -gt "$MAX_SIZE" ]; then
    echo "$f ($(( size / 1024 / 1024 )) MB)"
  fi
done)

if [ -n "$LARGE_FILES" ]; then
  echo "ERROR: Files exceed ${MAX_SIZE} byte limit:"
  echo "$LARGE_FILES"
  exit 1
fi
```

### Branch Naming Enforcement

```bash
#!/bin/sh
# .husky/pre-push

BRANCH=$(git rev-parse --abbrev-ref HEAD)
PATTERN="^(feat|fix|refactor|chore|docs|test|hotfix)/[a-z0-9._-]+$"

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "develop" ]; then
  exit 0  # Protected branches are fine
fi

if ! echo "$BRANCH" | grep -qE "$PATTERN"; then
  echo "ERROR: Branch name '$BRANCH' does not match pattern: $PATTERN"
  echo "Examples: feat/user-auth, fix/login-error, chore/update-deps"
  exit 1
fi
```

---

## Bypassing Hooks

```bash
# Skip all hooks for a single commit
git commit --no-verify -m "WIP: debugging, will squash"

# Skip pre-push hooks
git push --no-verify
```

### When bypassing is acceptable

- [OK] WIP commits on a feature branch you will squash before PR
- [OK] Emergency hotfix when hooks depend on a broken tool
- [OK] CI/CD automation where hooks already ran locally

### When bypassing is not acceptable

- [FAIL] Routinely skipping to avoid fixing lint errors
- [FAIL] Skipping secrets scanning
- [FAIL] Skipping on shared/protected branches
- [FAIL] Bypassing commit message validation to use vague messages

---

## Team Distribution Strategies

### Via package manager (recommended for Node projects)

Husky and lefthook both auto-install hooks when developers run `npm install` via the `prepare` script.

```json
// package.json
{
  "scripts": {
    "prepare": "husky"
  }
}
```

### Via committed scripts (language-agnostic)

For non-Node projects, commit hook scripts and provide a setup command:

```bash
# Makefile
setup-hooks:
	cp scripts/hooks/* .git/hooks/
	chmod +x .git/hooks/*

# Or use git config
setup-hooks:
	git config core.hooksPath scripts/hooks
```

### Via lefthook (any language)

```bash
# Developers run once after cloning
npx lefthook install
# Or: lefthook install (if installed globally)
```

---

## Example Configuration: Husky + lint-staged + commitlint

Complete setup for a TypeScript project:

```bash
# Install all dependencies
npm install --save-dev husky lint-staged \
  @commitlint/cli @commitlint/config-conventional

# Initialize Husky
npx husky init

# Create pre-commit hook
echo "npx lint-staged" > .husky/pre-commit

# Create commit-msg hook
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg

# Create pre-push hook
echo "npm test" > .husky/pre-push
```

```json
// package.json (relevant sections)
{
  "scripts": {
    "prepare": "husky",
    "test": "vitest run",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "lint-staged": {
    "*.{js,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional']
};
```

### Verification

```bash
# Test pre-commit (stage a file with lint errors)
echo "const x = 1;;" > test.ts && git add test.ts
git commit -m "test: verify hooks"
# Should auto-fix the double semicolon via eslint --fix

# Test commit-msg (bad message)
git commit --allow-empty -m "bad message"
# Should reject: "type may not be empty"

# Test commit-msg (good message)
git commit --allow-empty -m "chore: verify commitlint hook"
# Should succeed
```

---

## Do / Avoid

**DO**:
- [OK] Use lint-staged to run linters only on staged files (fast feedback)
- [OK] Enforce commit message format with commitlint
- [OK] Scan for secrets in pre-commit (gitleaks or similar)
- [OK] Distribute hooks via package manager prepare scripts
- [OK] Keep hook execution under 10 seconds for pre-commit
- [OK] Run heavier checks (full test suite) in pre-push, not pre-commit

**AVOID**:
- [FAIL] Running the entire test suite in pre-commit (too slow, developers will bypass)
- [FAIL] Hooks that modify files without re-staging them (causes silent partial commits)
- [FAIL] Relying solely on hooks for enforcement (CI must also validate)
- [FAIL] Making `--no-verify` a team habit
- [FAIL] Complex hooks that are hard to debug when they fail
- [FAIL] Forgetting to commit hook config files (`.husky/`, `lefthook.yml`, `.lintstagedrc`)

---

## Related Resources

- [Commit Conventions](commit-conventions.md) - Conventional commit message standards
- [Automated Quality Gates](automated-quality-gates.md) - CI/CD enforcement beyond local hooks
- [Validation Checklists](validation-checklists.md) - Pre-merge validation patterns
- [Common Mistakes](common-mistakes.md) - Includes committing secrets and skipping tests
