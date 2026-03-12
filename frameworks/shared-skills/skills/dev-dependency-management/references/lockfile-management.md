# Lockfile Management Deep Dive

Comprehensive guide to understanding, managing, and troubleshooting lockfiles across package managers.

## Table of Contents

- [What Are Lockfiles?](#what-are-lockfiles)
- [Lockfiles by Package Manager](#lockfiles-by-package-manager)
- [Lockfile Anatomy](#lockfile-anatomy)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## What Are Lockfiles?

**Lockfiles** are automatically generated files that record the **exact version** of every dependency (direct and transitive) installed in a project.

### Purpose

1. **Reproducibility:** Ensure identical dependency versions across dev, CI, and production
2. **Consistency:** Prevent "works on my machine" issues
3. **Security:** Lock known-good versions, avoid surprise updates
4. **Performance:** Faster installs (no version resolution needed)

### Without Lockfiles (Bad)

```json
// package.json
{
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

**Developer A installs (Jan 2024):** `express@4.18.2` with `body-parser@1.20.1`

**Developer B installs (Mar 2024):** `express@4.18.2` with `body-parser@1.20.2` (new patch release)

**Result:** Different dependency trees, potential bugs

### With Lockfiles (Good)

```
// package-lock.json (committed to git)
"body-parser": {
  "version": "1.20.1",  // Exact version locked
  "resolved": "https://registry.npmjs.org/body-parser/-/body-parser-1.20.1.tgz",
  "integrity": "sha512-..."
}
```

**Both developers:** Install identical `body-parser@1.20.1`

**Result:** Reproducible builds

---

## Lockfiles by Package Manager

### npm: package-lock.json

**Format:** JSON
**Introduced:** npm v5 (2017)
**Location:** Project root

**Key fields:**

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "node_modules/express": {
      "version": "4.18.2",
      "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
      "integrity": "sha512-...",
      "dependencies": {
        "body-parser": "1.20.1"
      }
    }
  }
}
```

**Commands:**

```bash
# Generate/update lockfile
npm install

# Install from lockfile (exact versions)
npm ci

# Update specific package
npm update express

# Regenerate lockfile
rm package-lock.json && npm install
```

### pnpm: pnpm-lock.yaml

**Format:** YAML
**Introduced:** pnpm v1 (2017)
**Location:** Project root

**Key fields:**

```yaml
lockfileVersion: '6.0'

dependencies:
  express:
    specifier: ^4.18.2
    version: 4.18.2

packages:
  /express@4.18.2:
    resolution: {integrity: sha512-...}
    dependencies:
      body-parser: 1.20.1
```

**Advantages:**

- Human-readable YAML
- Smaller file size
- Content-addressable storage

**Commands:**

```bash
# Generate/update lockfile
pnpm install

# Install from lockfile
pnpm install --frozen-lockfile

# Update specific package
pnpm update express

# Regenerate lockfile
pnpm install --force
```

### Yarn: yarn.lock

**Format:** Custom (YAML-like)
**Introduced:** Yarn v1 (2016)
**Location:** Project root

**Key fields:**

```
# Yarn v1 format
express@^4.18.2:
  version "4.18.2"
  resolved "https://registry.yarnpkg.com/express/-/express-4.18.2.tgz#..."
  integrity sha512-...
  dependencies:
    body-parser "1.20.1"
```

**Commands:**

```bash
# Generate/update lockfile
yarn install

# Install from lockfile (exact versions)
yarn install --frozen-lockfile

# Update specific package
yarn upgrade express

# Regenerate lockfile
rm yarn.lock && yarn install
```

### Poetry: poetry.lock

**Format:** TOML
**Introduced:** Poetry v0.1 (2018)
**Location:** Project root

**Key fields:**

```toml
[[package]]
name = "requests"
version = "2.28.2"
description = "HTTP library"
category = "main"
optional = false
python-versions = ">=3.7"

[package.dependencies]
certifi = ">=2017.4.17"
charset-normalizer = ">=2,<4"
```

**Commands:**

```bash
# Generate/update lockfile
poetry lock

# Install from lockfile
poetry install

# Update specific package
poetry update requests

# Regenerate lockfile
poetry lock --no-update
```

### Cargo: Cargo.lock

**Format:** TOML
**Introduced:** Cargo v0.1 (2014)
**Location:** Project root

**Key fields:**

```toml
[[package]]
name = "serde"
version = "1.0.160"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "bb2f3770c8bce3bcda7e149193a069a0f4365bda1fa5cd88e03bca26afc1216c"
dependencies = [
 "serde_derive",
]
```

**When to commit:**

- [OK] Applications: Always commit
- [FAIL] Libraries: Do NOT commit (allows consumers to use latest compatible versions)

**Commands:**

```bash
# Generate/update lockfile
cargo build

# Update specific dependency
cargo update serde

# Update all dependencies
cargo update
```

---

## Lockfile Anatomy

### Dependency Tree Flattening

**package.json (logical tree):**

```
my-app
├── express@^4.18.2
│   └── body-parser@^1.20.0
└── body-parser@^1.20.0
```

**package-lock.json (flattened):**

```json
{
  "dependencies": {
    "express": {
      "version": "4.18.2",
      "requires": {
        "body-parser": "1.20.1"
      }
    },
    "body-parser": {
      "version": "1.20.1"  // Single copy (deduplicated)
    }
  }
}
```

### Integrity Hashes

**Purpose:** Verify package hasn't been tampered with

**SHA-512 hash format:**

```json
"integrity": "sha512-5tK7EtrZ0N+OLFMthtqOj4fI2Jeb88C4CAZPu25LDVUvVLBaVsx3DdvKmjchNCd/6+Iq3YDDtdT1VrUrL8lPLg=="
```

**Verification:**

```bash
# npm verifies automatically on install
npm ci

# Manual verification
shasum -a 512 -b downloaded-package.tgz
```

### Lockfile Versions

**npm lockfileVersion:**

- `1` - npm 5-6 (legacy)
- `2` - npm 7+ (supports workspaces)
- `3` - npm 9+ (current, optimized format)

**Backwards compatibility:** npm 9 can read all versions

---

## Common Workflows

### Adding a New Dependency

```bash
# npm
npm install lodash
# Automatically updates package.json + package-lock.json

# pnpm
pnpm add lodash
# Updates package.json + pnpm-lock.yaml

# yarn
yarn add lodash
# Updates package.json + yarn.lock

# poetry
poetry add requests
# Updates pyproject.toml + poetry.lock
```

**What happens:**

1. Package manager resolves version from range
2. Downloads package + dependencies
3. Updates lockfile with exact versions
4. Installs to `node_modules`

**Commit:**

```bash
git add package.json package-lock.json
git commit -m "feat: add lodash for utility functions"
```

### Updating Dependencies

**Update all patch/minor versions:**

```bash
# npm
npm update

# pnpm
pnpm update

# yarn
yarn upgrade

# poetry
poetry update
```

**Update specific package:**

```bash
# npm
npm update express

# pnpm
pnpm update express

# yarn
yarn upgrade express

# poetry
poetry update requests
```

**Update to latest (including major versions):**

```bash
# npm
npm install express@latest

# pnpm
pnpm update express --latest

# yarn
yarn upgrade express --latest

# poetry
poetry add requests@latest
```

### CI/CD: Installing from Lockfile

**Principle:** CI should install **exact** versions from lockfile, not resolve versions

**npm:**

```bash
# BAD: Wrong (resolves versions from package.json)
npm install

# GOOD: Correct (installs exact versions from lockfile)
npm ci
```

**pnpm:**

```bash
# GOOD: Use frozen lockfile
pnpm install --frozen-lockfile
```

**yarn:**

```bash
# GOOD: Use frozen lockfile
yarn install --frozen-lockfile
```

**poetry:**

```bash
# GOOD: Install without updating lockfile
poetry install --no-root
```

### Resolving Lockfile Conflicts

**Scenario:** Two developers add different dependencies, merge conflict in lockfile

**BAD: Wrong approach:**

```bash
# Manually edit lockfile to resolve conflict
# (will cause corruption)
```

**GOOD: Correct approach:**

```bash
# 1. Resolve package.json conflicts first
git checkout --ours package.json
# or
git checkout --theirs package.json
# or manually merge

# 2. Delete lockfile
rm package-lock.json

# 3. Regenerate from resolved package.json
npm install

# 4. Commit
git add package.json package-lock.json
git commit -m "chore: resolve dependency conflicts"
```

---

## Troubleshooting

### Issue: "Lockfile out of sync"

**Error:**

```
npm ERR! code EUSAGE
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json are in sync.
```

**Cause:** `package.json` was modified without updating lockfile

**Fix:**

```bash
# Regenerate lockfile
npm install

# Or delete and reinstall
rm package-lock.json && npm install
```

### Issue: "Different lockfile versions"

**Error:**

```
npm WARN old lockfile
npm WARN old lockfile The package-lock.json file was created with an old version of npm
```

**Cause:** Lockfile created with npm 6, now using npm 9

**Fix:**

```bash
# Update to latest lockfile format
npm install --lockfile-version=3
```

### Issue: "Integrity checksum failed"

**Error:**

```
npm ERR! Integrity check failed for express
npm ERR! sha512-... !== sha512-...
```

**Cause:** Package was modified/corrupted, or lockfile is stale

**Fix:**

```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Cannot find module after install"

**Error:**

```
Error: Cannot find module 'express'
```

**Cause:** Lockfile and `node_modules` out of sync

**Fix:**

```bash
# Clean install
rm -rf node_modules
npm ci
```

### Issue: "Peer dependency conflicts"

**Error:**

```
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^18.0.0" from react-dom@18.2.0
```

**Fix Option 1: Update dependencies**

```bash
npm install react@18 react-dom@18
```

**Fix Option 2: Use legacy peer deps (temporary)**

```bash
npm install --legacy-peer-deps
```

**Fix Option 3: Override (npm 8.3+)**

```json
{
  "overrides": {
    "react": "^18.0.0"
  }
}
```

---

## Best Practices

### 1. Always Commit Lockfiles

```bash
# GOOD: Commit lockfiles
git add package-lock.json
git commit -m "chore: update dependencies"

# BAD: Never add to .gitignore
# echo "package-lock.json" >> .gitignore  # DON'T DO THIS
```

**Exception:** Rust libraries (Cargo.lock should NOT be committed for libraries)

### 2. Use CI-Specific Install Commands

```yaml
# GitHub Actions
- name: Install dependencies
  run: npm ci  # NOT npm install

# GitLab CI
script:
  - npm ci
```

### 3. Keep Lockfile Format Consistent

**Enforce npm version in CI:**

```json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

**Use .nvmrc:**

```bash
echo "18.16.0" > .nvmrc
nvm use
```

### 4. Don't Manually Edit Lockfiles

```bash
# BAD: Wrong
vi package-lock.json  # Manual edits will be overwritten

# GOOD: Correct
npm install <package>  # Let package manager update lockfile
```

### 5. Regenerate Lockfile After Major Changes

```bash
# After switching branches with different dependencies
rm package-lock.json
npm install

# After upgrading Node.js major version
rm package-lock.json
npm install
```

### 6. Use Lockfile in Docker Builds

**Dockerfile:**

```dockerfile
# Copy lockfile first (better caching)
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Then copy source code
COPY . .
RUN npm run build
```

### 7. Verify Lockfile in CI

```yaml
# GitHub Actions
- name: Verify lockfile
  run: |
    npm ci
    git diff --exit-code package-lock.json
```

### 8. Use Lockfile Analysis Tools

```bash
# Check for known vulnerabilities
npm audit

# Analyze lockfile size
npx lockfile-lint --path package-lock.json

# Check for malicious packages
npx socket-cli report create
```

---

## Lockfile Format Comparison

| Feature | npm | pnpm | yarn | poetry | cargo |
|---------|-----|------|------|--------|-------|
| **Format** | JSON | YAML | Custom | TOML | TOML |
| **Human-readable** | No | Yes | Yes | Yes | Yes |
| **File size** | Large | Small | Medium | Medium | Medium |
| **Merge conflicts** | Frequent | Rare | Moderate | Rare | Rare |
| **Integrity hashes** | Yes | Yes | Yes | Yes | Yes |
| **Workspace support** | Yes | Yes | Yes | Yes | Yes |

---

## Resources

- [npm package-lock.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json)
- [pnpm lockfile](https://pnpm.io/git#lockfiles)
- [Yarn lockfile](https://classic.yarnpkg.com/en/docs/yarn-lock)
- [Poetry lockfile](https://python-poetry.org/docs/basic-usage/#installing-with-poetrylock)
- [Cargo lockfile](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html)
