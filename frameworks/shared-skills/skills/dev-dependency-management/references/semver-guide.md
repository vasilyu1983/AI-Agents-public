# Semantic Versioning Deep Dive

Comprehensive guide to understanding and using semantic versioning (SemVer) for dependency management.

## Table of Contents

- [SemVer Basics](#semver-basics)
- [Version Constraints Explained](#version-constraints-explained)
- [npm/yarn/pnpm Ranges](#npmyarnpnpm-ranges)
- [Python Version Specifiers](#python-version-specifiers)
- [Cargo Version Requirements](#cargo-version-requirements)
- [Pre-release and Build Metadata](#pre-release-and-build-metadata)
- [Common Pitfalls](#common-pitfalls)
- [Best Practices](#best-practices)

---

## SemVer Basics

Semantic Versioning uses a three-part version number: `MAJOR.MINOR.PATCH`

**Format:** `X.Y.Z` where X, Y, and Z are non-negative integers

### Version Components

```
  2.14.7
  │ │  │
  │ │  └─ PATCH: Bug fixes (backward-compatible)
  │ └──── MINOR: New features (backward-compatible)
  └────── MAJOR: Breaking changes (incompatible API changes)
```

### When to Increment

| Change Type | Example | Version Change |
|-------------|---------|----------------|
| **MAJOR** | Remove deprecated API, change function signature | `1.4.2` → `2.0.0` |
| **MINOR** | Add new optional parameter, new feature | `1.4.2` → `1.5.0` |
| **PATCH** | Fix bug, security patch | `1.4.2` → `1.4.3` |

### Special Version 0.x.y

**Versions starting with 0 (0.x.y) are considered unstable:**

- `0.x.y` - Initial development, anything may change
- `0.0.x` - Extremely unstable
- Breaking changes can happen on **any** update in 0.x.y versions
- Don't use 0.x.y in production without pinning exact versions

---

## Version Constraints Explained

### Exact Version

```json
"lodash": "4.17.21"
```

- **Installs:** Exactly `4.17.21`
- **Use when:** Mission-critical dependencies, reproducibility is paramount
- **Risk:** Miss bug fixes and security patches
- **Recommendation:** Use sparingly

### Caret Range (^) - Recommended

```json
"express": "^4.18.2"
```

- **Installs:** `>=4.18.2 <5.0.0`
- **Allows:** Patch and minor updates
- **Blocks:** Major version changes
- **Use when:** Default for most dependencies
- **Example:**
  - `^4.18.2` allows `4.18.3`, `4.19.0`, `4.99.0`
  - `^4.18.2` blocks `5.0.0`

**Special case for 0.x.y versions:**
```json
"package": "^0.3.2"
```
- **Installs:** `>=0.3.2 <0.4.0` (only patch updates)
- Caret is more conservative for pre-1.0 versions

### Tilde Range (~) - Conservative

```json
"react": "~18.2.0"
```

- **Installs:** `>=18.2.0 <18.3.0`
- **Allows:** Only patch updates
- **Blocks:** Minor and major updates
- **Use when:** You want stability but still need security patches
- **Example:**
  - `~18.2.0` allows `18.2.1`, `18.2.2`, `18.2.99`
  - `~18.2.0` blocks `18.3.0`, `19.0.0`

### Greater Than / Less Than

```json
"next": ">=13.0.0 <14.0.0"
```

- Explicit range specification
- Use for complex version requirements
- Less common than caret/tilde

### Wildcard (x) - Avoid

```json
"axios": "1.x"
```

- **Installs:** `>=1.0.0 <2.0.0`
- **Equivalent to:** `^1.0.0`
- **Recommendation:** Use caret instead for clarity

### Any Version (*) - Never Use

```json
"moment": "*"
```

- **Installs:** Latest version (completely unpredictable)
- **Risk:** Breaking changes without warning
- **Recommendation:** **Never use in production**

---

## npm/yarn/pnpm Ranges

### Comprehensive Examples

```json
{
  "dependencies": {
    "exact-version": "1.2.3",           // Exactly 1.2.3
    "caret-range": "^1.2.3",            // >=1.2.3 <2.0.0
    "tilde-range": "~1.2.3",            // >=1.2.3 <1.3.0
    "greater-than": ">=1.2.3",          // 1.2.3 or higher
    "less-than": "<2.0.0",              // Below 2.0.0
    "range": ">=1.2.3 <2.0.0",          // Between 1.2.3 and 2.0.0
    "wildcard": "1.x",                  // 1.0.0 - 1.99.99
    "wildcard-minor": "1.2.x",          // 1.2.0 - 1.2.99
    "hyphen-range": "1.2.3 - 2.3.4",    // >=1.2.3 <=2.3.4
    "OR-operator": "1.x || 2.x",        // 1.x.x or 2.x.x
    "git-url": "git+https://github.com/user/repo.git#commit-hash",
    "github-shorthand": "user/repo",
    "local-path": "file:../local-package"
  }
}
```

### Advanced Ranges

```json
{
  "dependencies": {
    "latest-tag": "latest",             // Latest npm tag (avoid)
    "dist-tag": "next",                 // Specific distribution tag
    "pre-release": "^1.0.0-beta.1",     // Includes pre-release versions
    "exclude-pre": "^1.0.0",            // Excludes pre-release
    "complex": ">=1.2.3 <2.0.0 || >=3.0.0 <4.0.0"
  }
}
```

---

## Python Version Specifiers

Python uses [PEP 440](https://peps.python.org/pep-0440/) for version specifiers.

### Poetry (pyproject.toml)

```toml
[tool.poetry.dependencies]
# Caret (default in Poetry)
requests = "^2.28.0"           # >=2.28.0 <3.0.0

# Tilde
fastapi = "~0.95.0"            # >=0.95.0 <0.96.0

# Exact version
pydantic = "==2.0.3"           # Exactly 2.0.3

# Greater than or equal
numpy = ">=1.24.0"             # 1.24.0 or higher

# Compatible release (roughly equivalent to caret)
pandas = "~=1.5.0"             # >=1.5.0 <2.0.0

# Wildcard
django = "4.*"                 # Any 4.x version

# Multiple constraints
flask = ">=2.0,<3.0"           # Between 2.0 and 3.0
```

### pip (requirements.txt)

```txt
# Exact version (most common in requirements.txt)
Django==4.2.1

# Greater than or equal
requests>=2.28.0

# Compatible release
numpy~=1.24.0

# Range
fastapi>=0.95.0,<1.0.0

# Not equal (exclude specific versions)
urllib3>=1.26.0,!=1.26.5

# Logical OR (rarely used)
pytest==7.3.1 ; python_version >= "3.8"
```

---

## Cargo Version Requirements

Rust's Cargo uses a slightly different syntax.

### Cargo.toml

```toml
[dependencies]
# Caret (default in Cargo)
serde = "^1.0"              # >=1.0.0 <2.0.0
serde_json = "1.0"          # Same as ^1.0 (caret is implicit)

# Tilde
regex = "~1.7"              # >=1.7.0 <1.8.0

# Exact version (use =)
tokio = "=1.28.0"           # Exactly 1.28.0

# Wildcard
actix-web = "4.*"           # Any 4.x version

# Greater/less than
reqwest = ">=0.11, <0.12"   # Range

# Multiple requirements
hyper = ">= 0.14, < 0.15"   # Equivalent to ~0.14

# Git dependencies
rand = { git = "https://github.com/rust-random/rand.git", branch = "main" }
```

### Cargo Defaults

**Important:** In Cargo, version `"1.0"` is shorthand for `"^1.0"` (caret is implicit).

---

## Pre-release and Build Metadata

### Pre-release Versions

```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-beta.2 < 1.0.0-rc.1 < 1.0.0
```

**Common pre-release identifiers:**
- `alpha` - Early testing
- `beta` - Feature-complete but unstable
- `rc` (release candidate) - Ready for release, final testing
- `next` - Next version preview

**How version constraints handle pre-releases:**

```json
// npm
"package": "^1.0.0"         // Does NOT include 1.1.0-beta
"package": "^1.0.0-beta"    // Includes 1.0.0-beta.1, 1.0.0-rc, 1.0.0

// Explicitly allow pre-releases
"package": "^1.0.0 || ^1.0.0-beta"
```

### Build Metadata

Build metadata is **ignored** for version precedence:

```
1.0.0+20130313144700 == 1.0.0+exp.sha.5114f85
```

- Used for CI build numbers, commit hashes
- Does not affect version sorting
- Rarely used in dependency declarations

---

## Common Pitfalls

### Pitfall 1: Using `*` or `latest`

**Bad:**
```json
"react": "*"
"next": "latest"
```

**Why:** Completely unpredictable. Can break production without warning.

**Fix:**
```json
"react": "^18.2.0"
"next": "^14.0.0"
```

### Pitfall 2: Too Many Exact Versions

**Bad:**
```json
"express": "4.18.2",
"lodash": "4.17.21",
"axios": "1.4.0",
"moment": "2.29.4"
```

**Why:** Misses critical security patches.

**Fix:** Use caret for most dependencies, exact only for mission-critical ones.

```json
"express": "^4.18.2",
"lodash": "^4.17.21",
"axios": "^1.4.0",
"moment": "^2.29.4"   // Or better: remove and use native Date
```

### Pitfall 3: Ignoring 0.x.y Instability

**Bad:**
```json
"some-new-lib": "^0.5.2"  // Assumes stability
```

**Why:** 0.x.y versions can have breaking changes on any update.

**Fix:** Pin exact version or use tilde.

```json
"some-new-lib": "0.5.2"   // Exact
// or
"some-new-lib": "~0.5.2"  // Only patch updates
```

### Pitfall 4: Misunderstanding Caret with 0.x

```json
"package": "^0.3.2"
```

**Expected:** `>=0.3.2 <1.0.0`
**Actual:** `>=0.3.2 <0.4.0` (conservative for 0.x)

### Pitfall 5: Lockfile Conflicts

**Problem:** Merge conflicts in `package-lock.json`

**Wrong fix:** Manually edit lockfile

**Right fix:**
```bash
# Delete lockfile and regenerate
rm package-lock.json
npm install

# Or resolve package.json first, then:
npm install
```

---

## Best Practices

### 1. Default to Caret (`^`)

```json
"express": "^4.18.2"
```

[OK] Gets security patches and new features
[OK] Avoids breaking changes
[OK] Recommended by npm, yarn, pnpm

### 2. Use Exact Versions Strategically

**When to use exact versions:**
- Mission-critical dependencies (payment processing, auth)
- Known stability issues with a package
- Deployment to production (optional, if very conservative)

```json
"stripe": "12.10.0",          // Exact (payment processing)
"express": "^4.18.2"          // Caret (everything else)
```

### 3. Pin 0.x.y Versions

```json
"experimental-lib": "0.5.2"   // Exact for unstable
```

### 4. Use Lockfiles

**Always commit:**
- `package-lock.json` (npm)
- `yarn.lock` (yarn)
- `pnpm-lock.yaml` (pnpm)
- `poetry.lock` (poetry)
- `Cargo.lock` (cargo applications)

### 5. Update Regularly

```bash
# Check for outdated packages
npm outdated

# Update patch versions
npm update

# Update minor/major versions interactively
npx npm-check-updates -i
```

### 6. Document Exact Versions

If you pin an exact version, document why:

```json
{
  "dependencies": {
    "problematic-lib": "2.5.3"
    // Pinned to 2.5.3 due to memory leak in 2.6.0
    // See: https://github.com/lib/issues/123
  }
}
```

### 7. Use Version Constraints Consistently

**Good:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "^14.0.0"
  }
}
```

**Bad (inconsistent):**
```json
{
  "dependencies": {
    "react": "18.2.0",        // Exact
    "react-dom": "^18.2.0",   // Caret
    "next": "*"               // Wildcard
  }
}
```

---

## Quick Reference

### npm/yarn/pnpm

| Syntax | Meaning | Use Case |
|--------|---------|----------|
| `1.2.3` | Exactly 1.2.3 | Mission-critical |
| `^1.2.3` | `>=1.2.3 <2.0.0` | **Default** |
| `~1.2.3` | `>=1.2.3 <1.3.0` | Conservative |
| `1.x` | `>=1.0.0 <2.0.0` | Avoid (use caret) |
| `*` | Latest | **Never use** |

### Python (Poetry)

| Syntax | Meaning | Use Case |
|--------|---------|----------|
| `==1.2.3` | Exactly 1.2.3 | Pin version |
| `^1.2.3` | `>=1.2.3 <2.0.0` | **Default** |
| `~1.2.3` | `>=1.2.3 <1.3.0` | Conservative |
| `~=1.2.3` | `>=1.2.3 <2.0.0` | Compatible release |
| `>=1.2.3` | 1.2.3 or higher | Lower bound |

### Rust (Cargo)

| Syntax | Meaning | Use Case |
|--------|---------|----------|
| `=1.2.3` | Exactly 1.2.3 | Pin version |
| `1.2` | `^1.2` (implicit) | **Default** |
| `^1.2.3` | `>=1.2.3 <2.0.0` | Explicit caret |
| `~1.2.3` | `>=1.2.3 <1.3.0` | Conservative |

---

## Testing Version Constraints

### npm semver calculator

```bash
# Install globally
npm install -g semver

# Test if version satisfies constraint
semver 1.2.3 -r "^1.0.0"  # true
semver 2.0.0 -r "^1.0.0"  # false

# Find max satisfying version
semver -r "^1.0.0" 1.0.0 1.5.0 2.0.0  # 1.5.0
```

### Online tools

- [npm semver calculator](https://semver.npmjs.com/)
- [semver.org](https://semver.org/)

---

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [npm semver documentation](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#dependencies)
- [PEP 440 (Python)](https://peps.python.org/pep-0440/)
- [Cargo version requirements](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html)
- [node-semver library](https://github.com/npm/node-semver)
