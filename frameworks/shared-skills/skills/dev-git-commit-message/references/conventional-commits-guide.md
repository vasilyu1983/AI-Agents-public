# Conventional Commits Reference Guide

## Format Specification

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

### Primary Types

**feat**: A new feature for the user
- Adds new functionality
- Introduces new API endpoints
- Creates new user-facing capabilities
- Examples: new component, new API route, new CLI command

**fix**: A bug fix
- Corrects incorrect behavior
- Resolves user-reported issues
- Patches security vulnerabilities
- Examples: fix validation, correct calculation, resolve crash

**refactor**: Code change that neither fixes a bug nor adds a feature
- Improves code structure
- Enhances readability
- Optimizes without changing behavior
- Examples: extract function, rename variables, reorganize modules

### Documentation & Formatting

**docs**: Documentation only changes
- README updates
- API documentation
- Code comments
- Wiki pages
- Examples: update README, add JSDoc comments

**style**: Changes that don't affect code meaning
- Formatting (prettier, eslint --fix)
- Whitespace, semicolons
- Code style only (no logic changes)
- Examples: run prettier, fix indentation

### Testing & Build

**test**: Adding or correcting tests
- New test cases
- Test utilities
- Test configuration
- Examples: add unit tests, fix flaky test

**chore**: Changes to build process or auxiliary tools
- Package updates
- Build script changes
- Development tooling
- Examples: update dependencies, configure webpack

### Performance & CI/CD

**perf**: Performance improvements
- Measurable speed improvements
- Memory optimization
- Bundle size reduction
- Examples: optimize algorithm, lazy load component

**ci**: Continuous Integration changes
- GitHub Actions
- CircleCI, Travis CI
- Build pipelines
- Examples: update CI workflow, add deployment step

### Special Cases

**revert**: Reverts a previous commit
- Format: `revert: <reverted commit message>`
- Include commit hash in body

**build**: Changes affecting build system
- Webpack, rollup, vite configuration
- Build dependencies
- Examples: update build config, change bundler

## Scope Guidelines

### What is Scope?

The scope indicates which part of the codebase was modified:
- `feat(auth): add login component`
- `fix(api): correct validation error`
- `docs(readme): update installation steps`

### Scope Best Practices

1. **Use lowercase**: `feat(api)` not `feat(API)`
2. **Be specific but not narrow**: `feat(user-profile)` not `feat(user-profile-avatar-upload-button)`
3. **Match your project structure**: Use module names, directory names, or functional areas
4. **Omit when unclear**: If changes span many areas, scope is optional

### Common Scopes by Project Type

**Web Applications**:
- `ui`, `components`, `layout`, `styles`
- `api`, `routes`, `middleware`, `controllers`
- `auth`, `user`, `admin`
- `db`, `models`, `migrations`
- `config`, `env`, `settings`

**Libraries/Packages**:
- `core`, `utils`, `helpers`
- `types`, `interfaces`
- `cli`, `commands`
- `parser`, `compiler`, `renderer`

**Full-Stack Projects**:
- `frontend`, `backend`, `shared`
- `server`, `client`
- `desktop`, `mobile`, `web`

## Description Guidelines

### The Perfect Description

1. **Use imperative mood**: "add" not "added", "fix" not "fixed"
   - [OK] `feat: add user dashboard`
   - [FAIL] `feat: added user dashboard`

2. **Keep it concise**: 50 characters ideal, 72 maximum
   - [OK] `fix(auth): correct token expiration check`
   - [FAIL] `fix(auth): correct the token expiration check which was causing users to be logged out too early`

3. **Be specific**: Clearly state what changed
   - [OK] `feat(api): add pagination to user list endpoint`
   - [FAIL] `feat: improve API`

4. **No period at the end**
   - [OK] `docs: update README installation section`
   - [FAIL] `docs: update README installation section.`

5. **Focus on what and why, not how**
   - [OK] `perf(images): reduce bundle size with lazy loading`
   - [FAIL] `perf(images): use React.lazy and Suspense to implement code splitting`

## Breaking Changes

### Indicating Breaking Changes

**Option 1**: Exclamation mark
```
feat(api)!: change authentication flow to OAuth2
```

**Option 2**: BREAKING CHANGE footer
```
feat(api): change authentication flow

BREAKING CHANGE: The authentication endpoint now requires OAuth2 tokens
instead of API keys. All clients must update their authentication logic.
```

### When to Use

- API changes that require user updates
- Removed functionality
- Changed behavior of existing features
- Renamed public methods or properties

## Multi-line Commits

### With Body

```
feat(api): add user search endpoint

Implement full-text search across user profiles including
name, email, and bio fields. Uses database indexes for
performance.
```

### With Footer

```
fix(auth): resolve session timeout issue

Closes #123
Refs #456
```

### Common Footers

- `Closes #123`: Closes issue
- `Fixes #123`: Fixes issue
- `Refs #123`: References issue
- `BREAKING CHANGE:`: Describes breaking change
- `Co-authored-by:`: Credits co-authors

## Real-World Examples

### Feature Development

```
feat(chat): add real-time message notifications

Implement WebSocket connection for live message updates.
Includes visual and sound notifications.

Closes #234
```

### Bug Fixes

```
fix(cart): prevent duplicate items on rapid clicks

Add debouncing to "Add to Cart" button to prevent race
condition when user clicks multiple times quickly.

Fixes #567
```

### Refactoring

```
refactor(utils): extract date formatting into shared helper

Move duplicate date formatting logic from components into
centralized utility function. No behavior changes.
```

### Documentation

```
docs(api): add examples for authentication endpoints

Include curl examples and response samples for all auth
endpoints in API documentation.
```

### Dependencies

```
chore(deps): update react to v18.2.0

Update React and React-DOM to latest stable version.
Includes performance improvements and bug fixes.
```

### Performance

```
perf(images): implement progressive image loading

Replace eager loading with progressive JPEG loading to
improve perceived performance on slow connections.
```

### Configuration

```
ci: add automated dependency updates

Configure Dependabot to automatically check for and create
PRs for dependency updates weekly.
```

## Common Patterns to Avoid

### BAD: Too Vague
```
fix: bug fix
feat: new feature
chore: updates
```

### BAD: Too Detailed (save for body)
```
feat: add a new user authentication system with JWT tokens and refresh token rotation using Redis for storage and bcrypt for password hashing
```

### BAD: Wrong Type
```
feat: fix login bug          → fix(auth): resolve login validation
docs: add new API endpoint   → feat(api): add user search endpoint
```

### BAD: Mixed Changes
```
feat: add dashboard and fix auth bug and update docs
→ Split into 3 commits
```

## Tooling

### Commitlint
Enforce conventional commits in CI:
```json
{
  "extends": ["@commitlint/config-conventional"]
}
```

### Commitizen
Interactive commit message wizard:
```bash
npm install -g commitizen
git cz
```

### Husky
Git hooks for commit message validation:
```bash
npm install husky --save-dev
npx husky add .husky/commit-msg 'npx commitlint --edit $1'
```

## Benefits

1. **Automated Changelogs**: Generate from commit history
2. **Semantic Versioning**: Auto-determine version bumps
3. **Better History**: Clear, searchable commit messages
4. **Team Alignment**: Consistent commit style
5. **Code Review**: Easier to understand changes

## Resources

- Specification: https://www.conventionalcommits.org/
- Commitlint: https://commitlint.js.org/
- Commitizen: https://github.com/commitizen/cz-cli
- Semantic Release: https://semantic-release.gitbook.io/
