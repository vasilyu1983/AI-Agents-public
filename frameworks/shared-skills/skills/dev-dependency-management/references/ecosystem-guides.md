# Dependency Management by Ecosystem

**When to Use**: Ecosystem-specific guidance for Node.js, Python, Rust, Go, and other language ecosystems.

---

## Node.js (npm / yarn / pnpm / Bun)

### Package Manager Comparison (January 2026)

| Feature | npm 11.x | yarn 4.x (Berry) | pnpm 10.x | Bun 1.3 |
|---------|----------|------------------|-----------|---------|
| **Speed** | Slowest | Decent | Fast | **Fastest** (7× npm) |
| **Disk Usage** | High (duplicates) | PnP: None / Classic: High | **Lowest** (hard links) | Low (global cache) |
| **Monorepo Support** | Good (workspaces) | Good (workspaces) | **Best** (strict isolation) | Good (improving) |
| **Security** | Good (audit built-in) | Good | Good | Good |
| **Ecosystem** | Largest | Large | Large | Growing |
| **Lockfile** | package-lock.json | yarn.lock | pnpm-lock.yaml | bun.lock |
| **Install Command** | `npm install` | `yarn install` | `pnpm install` | `bun install` |
| **CI Command** | `npm ci` | `yarn install --frozen-lockfile` | `pnpm install --frozen-lockfile` | `bun install --frozen-lockfile` |
| **Deterministic** | Yes | **Excellent** (PnP) | **Excellent** | Yes |

**Recommendations (January 2026):**

- **New projects:** **pnpm** (fastest stable, best disk efficiency) or **Bun** (7× faster, production-ready)
- **Enterprise monorepos:** **pnpm** (most stable workspace support)
- **Speed-focused experimentation:** **Bun** (bleeding edge performance)
- **Maximum compatibility:** **npm** (most packages tested against it)

### npm Best Practices

**1. Use `npm ci` in CI/CD (not `npm install`):**

```bash
# BAD: Bad (in CI)
npm install

# GOOD: Good (in CI)
npm ci
```

**Why:** `npm ci` installs from lockfile exactly, faster, and fails if package.json and lockfile are out of sync.

**2. Enable `save-exact` for critical applications:**

```bash
npm config set save-exact true
```

Or in `.npmrc`:

```ini
save-exact=true
```

**Effect:**

```json
{
  "dependencies": {
    "express": "4.18.2"  // Exact version (not ^4.18.2)
  }
}
```

**3. Use `.npmrc` for team configuration:**

```ini
# .npmrc (committed to git)
save-exact=false
package-lock=true
engine-strict=true
audit-level=moderate
```

**4. Configure private registry (optional):**

```ini
registry=https://registry.npmjs.org/
@myorg:registry=https://npm.mycompany.com/
```

**5. Audit dependencies monthly:**

```bash
# Check for vulnerabilities
npm audit

# Auto-fix non-breaking
npm audit fix

# Check specific package
npm view <package> vulnerabilities
```

**6. Use workspaces for monorepos:**

```json
{
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```

### pnpm Best Practices

**1. Use `pnpm` for speed and disk efficiency:**

```bash
# Install pnpm globally
npm install -g pnpm

# Migrate from npm
pnpm import  # Converts package-lock.json → pnpm-lock.yaml

# Install dependencies
pnpm install
```

**2. Configure workspaces:**

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
  - '!**/test/**'  # Exclude test directories
```

**3. Use filters for monorepo commands:**

```bash
# Run script in specific package
pnpm --filter @myorg/ui build

# Run script in all packages
pnpm -r test

# Run script in changed packages only
pnpm --filter="...[origin/main]" test
```

**4. Enable strict peer dependencies:**

```ini
# .npmrc
strict-peer-dependencies=true
```

**5. Use overrides for transitive deps:**

```json
{
  "pnpm": {
    "overrides": {
      "axios": "1.6.0"
    }
  }
}
```

### yarn Best Practices

**1. Use Yarn 3+ (Berry) for modern features:**

```bash
# Enable Corepack (Node 16.10+)
corepack enable

# Set Yarn version
yarn set version stable
```

**2. Use workspaces:**

```json
{
  "workspaces": {
    "packages": [
      "packages/*"
    ]
  }
}
```

**3. Use `yarn why` to understand dependencies:**

```bash
yarn why lodash
```

**4. Configure resolutions:**

```json
{
  "resolutions": {
    "lodash": "4.17.21"
  }
}
```

### Bun Best Practices

**1. Install Bun:**

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows (via npm)
npm install -g bun
```

**2. Initialize and install:**

```bash
# New project
bun init

# Install dependencies (7× faster than npm)
bun install

# CI/CD (frozen lockfile)
bun install --frozen-lockfile
```

**3. Add dependencies:**

```bash
# Production dependency
bun add express

# Dev dependency
bun add -d typescript

# Exact version
bun add lodash@4.17.21
```

**4. Use workspaces:**

```json
{
  "workspaces": ["packages/*", "apps/*"]
}
```

```bash
# Run in specific workspace
bun run --filter @myorg/ui build
```

**5. Security auditing:**

```bash
# Currently use npm audit (Bun audit in development)
npm audit
```

**6. Override transitive dependencies:**

```json
{
  "overrides": {
    "axios": "1.6.0"
  }
}
```

**When to use Bun:**

- Greenfield projects where speed is critical
- Development environments (fast feedback)
- Scripts and tooling (fast startup)

**When to prefer pnpm:**

- Enterprise monorepos requiring stable workspace support
- Projects with complex peer dependency requirements
- Maximum ecosystem compatibility needed

---

## Python (pip / poetry / conda / uv)

### Tool Comparison (January 2026)

| Tool | Use Case | Lockfile | Virtual Env | Speed |
|------|----------|----------|-------------|-------|
| **uv** (Astral) | All Python projects | `uv.lock` | Automatic | **10-100× faster** |
| **pip** + **venv** | Simple projects | `requirements.txt` (pinned) | Manual (`venv`) | Baseline |
| **pip-tools** | Production apps | `requirements.txt` (pinned) | Manual (`venv`) | Baseline |
| **poetry** | Modern Python apps | `poetry.lock` | Automatic | Moderate |
| **conda** | Data science, ML | `environment.yml` | Automatic | Slow |

**Recommendations (January 2026):**

- **New projects:** **uv** (10-100× faster than pip, replaces pip/poetry/virtualenv in single tool)
- **Mature projects:** **Poetry** (battle-tested, excellent dependency resolution)
- **Simple scripts:** pip + venv (minimal setup)
- **Data science/ML:** **conda** (binary packages) or **uv** (faster environment setup)

### pip + pip-tools Best Practices

**1. Separate `requirements.in` (loose) from `requirements.txt` (pinned):**

```ini
# requirements.in (loose constraints)
flask>=2.0.0
requests>=2.28.0
```

```bash
# Generate pinned requirements.txt
pip-compile requirements.in
```

**Output (`requirements.txt`):**

```ini
# This file is autogenerated by pip-compile
flask==2.3.2
  via -r requirements.in
requests==2.31.0
  via -r requirements.in
click==8.1.3
  via flask
...
```

**2. Separate dev and production requirements:**

```ini
# requirements-dev.in
-r requirements.txt
pytest>=7.0.0
black>=23.0.0
```

**3. Use virtual environments:**

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Unix
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

**4. Use constraints for transitive deps:**

```ini
# constraints.txt
urllib3==1.26.18  # Pin transitive dependency
```

```bash
pip install -c constraints.txt -r requirements.txt
```

### Poetry Best Practices

**1. Initialize project:**

```bash
poetry new myproject
cd myproject
```

**2. Add dependencies:**

```bash
# Production dependency
poetry add requests

# Dev dependency
poetry add --group dev pytest

# Install all dependencies
poetry install
```

**3. Use dependency groups:**

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"

[tool.poetry.group.test.dependencies]
coverage = "^7.0.0"
```

**4. Lock without installing:**

```bash
poetry lock --no-update
```

**5. Export to requirements.txt:**

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

**6. Configure poetry:**

```bash
# Use in-project virtualenv
poetry config virtualenvs.in-project true

# Don't create virtualenv (use system Python)
poetry config virtualenvs.create false
```

### conda Best Practices

**1. Create environment from file:**

```yaml
# environment.yml
name: myproject
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy=1.24.0
  - pandas=2.0.0
  - scikit-learn=1.2.0
  - pip:
      - custom-package==1.0.0
```

```bash
conda env create -f environment.yml
conda activate myproject
```

**2. Export environment:**

```bash
# Export exact environment
conda env export > environment.yml

# Export cross-platform
conda env export --from-history > environment.yml
```

**3. Update environment:**

```bash
conda env update -f environment.yml --prune
```

**4. Use conda-lock for reproducibility:**

```bash
# Install conda-lock
conda install -c conda-forge conda-lock

# Generate lockfile
conda-lock -f environment.yml -p linux-64
```

### uv Best Practices (NEW - January 2026)

**uv** by Astral is an ultra-fast Python package manager written in Rust. It replaces pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv in a single tool.

**1. Install uv:**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip (if needed)
pip install uv
```

**2. Initialize project:**

```bash
# Create new project
uv init myproject
cd myproject

# Creates pyproject.toml and uv.lock
```

**3. Add dependencies:**

```bash
# Add production dependency
uv add requests

# Add dev dependency
uv add --dev pytest

# Add with version constraint
uv add "flask>=2.0"

# Install all dependencies
uv sync
```

**4. Run scripts and tools:**

```bash
# Run Python script
uv run python script.py

# Run tool (like pipx)
uv tool run ruff check .

# Install tool globally
uv tool install ruff
```

**5. Manage Python versions:**

```bash
# Install Python version
uv python install 3.12

# List available versions
uv python list

# Pin version for project
uv python pin 3.12
```

**6. CI/CD usage:**

```bash
# Install from lockfile (fast, reproducible)
uv sync --frozen

# Export to requirements.txt (for compatibility)
uv export > requirements.txt
```

**7. Workspaces (monorepo):**

```toml
# pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]
```

**Migration from Poetry:**

```bash
# uv can read pyproject.toml from Poetry
# Just run:
uv sync

# This creates uv.lock from existing pyproject.toml
```

**When to use uv:**

- All new Python projects (10-100× faster)
- Existing projects wanting faster installs
- Teams standardizing on single tool
- CI/CD pipelines (massive time savings)

**When Poetry may still be preferred:**

- Complex plugin ecosystem requirements
- Teams with heavy Poetry investment
- Projects requiring Poetry-specific features

---

## Rust (Cargo)

### Best Practices

**1. Commit `Cargo.lock` for applications (not libraries):**

**Applications:**

```bash
git add Cargo.lock  # GOOD: Commit for reproducibility
```

**Libraries:**

```bash
echo "Cargo.lock" >> .gitignore  # BAD: Don't commit (users generate their own)
```

**2. Use `cargo update` to update dependencies:**

```bash
# Update all dependencies
cargo update

# Update specific package
cargo update -p serde

# Preview updates without applying
cargo update --dry-run
```

**3. Use `cargo audit` for security scanning:**

```bash
# Install cargo-audit
cargo install cargo-audit

# Run audit
cargo audit

# Fix vulnerabilities automatically
cargo audit fix
```

**4. Leverage Cargo features for optional dependencies:**

```toml
[features]
default = ["serde"]
full = ["serde", "tokio", "async"]

[dependencies]
serde = { version = "1.0", optional = true }
tokio = { version = "1.0", optional = true }
```

**Usage:**

```bash
# Build with default features
cargo build

# Build with all features
cargo build --all-features

# Build with specific feature
cargo build --features full
```

**5. Use workspaces for multi-crate projects:**

```toml
# Cargo.toml (workspace root)
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli"
]

[workspace.dependencies]
serde = "1.0"  # Shared version
```

**6. Use `cargo-outdated` to check for updates:**

```bash
cargo install cargo-outdated
cargo outdated
```

---

## Go (go mod)

### Best Practices

**1. Use Go modules (standard since 1.11):**

```bash
# Initialize module
go mod init github.com/username/project

# Add dependency (automatic)
go get github.com/pkg/errors

# Download dependencies
go mod download
```

**2. Commit `go.sum` for reproducibility:**

```bash
git add go.mod go.sum
```

**3. Use `go mod tidy` to clean up:**

```bash
# Remove unused dependencies
go mod tidy

# Run before commits
```

**4. Vendor dependencies for enterprise projects:**

```bash
# Create vendor directory
go mod vendor

# Build using vendored deps
go build -mod=vendor
```

**5. Use semantic import versioning for major versions:**

```go
// Import v2+
import "github.com/pkg/errors/v2"
```

```toml
# go.mod
require (
    github.com/pkg/errors/v2 v2.1.0
)
```

**6. Use `go list` to inspect dependencies:**

```bash
# List all dependencies
go list -m all

# List outdated dependencies
go list -u -m all

# View dependency graph
go mod graph
```

---

## Java (Maven / Gradle)

### Maven Best Practices

**1. Use dependency management section:**

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>3.1.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

**2. Use properties for versions:**

```xml
<properties>
  <spring.version>6.0.0</spring.version>
  <jackson.version>2.15.0</jackson.version>
</properties>

<dependencies>
  <dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-core</artifactId>
    <version>${spring.version}</version>
  </dependency>
</dependencies>
```

**3. Use `mvn dependency:tree` to view dependencies:**

```bash
mvn dependency:tree
mvn dependency:tree -Dverbose
```

**4. Check for updates:**

```bash
mvn versions:display-dependency-updates
```

### Gradle Best Practices

**1. Use version catalogs (Gradle 7.0+):**

```toml
# gradle/libs.versions.toml
[versions]
spring = "6.0.0"
jackson = "2.15.0"

[libraries]
spring-core = { module = "org.springframework:spring-core", version.ref = "spring" }
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
```

```groovy
// build.gradle
dependencies {
    implementation libs.spring.core
    implementation libs.jackson.databind
}
```

**2. Use dependency constraints:**

```groovy
dependencies {
    constraints {
        implementation 'org.apache.commons:commons-lang3:3.12.0'
    }
}
```

**3. View dependency tree:**

```bash
./gradlew dependencies
./gradlew dependencies --configuration runtimeClasspath
```

---

## PHP (Composer)

### Best Practices

**1. Commit `composer.lock`:**

```bash
git add composer.lock
```

**2. Use `composer install` (not `composer update`) in production:**

```bash
# Production
composer install --no-dev --optimize-autoloader

# Development
composer install
```

**3. Use version constraints:**

```json
{
  "require": {
    "symfony/http-foundation": "^6.0",
    "guzzlehttp/guzzle": "~7.4"
  }
}
```

**4. Check for security vulnerabilities:**

```bash
composer audit
```

**5. View dependency tree:**

```bash
composer show --tree
```

---

## .NET (NuGet)

### Best Practices

**1. Use Central Package Management:**

```xml
<!-- Directory.Packages.props -->
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>
</Project>
```

**2. Use `packages.lock.json`:**

```bash
dotnet restore --use-lock-file
```

**3. Check for updates:**

```bash
dotnet list package --outdated
```

**4. Audit for vulnerabilities:**

```bash
dotnet list package --vulnerable
```

---

## Summary Table (January 2026)

| Ecosystem | Package Manager | Lockfile | Best Tool | Security Audit |
|-----------|-----------------|----------|-----------|----------------|
| **Node.js** | npm/yarn/pnpm/Bun | `pnpm-lock.yaml` / `bun.lock` | **pnpm** or **Bun** | `npm audit` |
| **Python** | pip/poetry/conda/uv | `uv.lock` / `poetry.lock` | **uv** | `pip-audit` |
| **Rust** | cargo | `Cargo.lock` | cargo | `cargo audit` |
| **Go** | go mod | `go.sum` | go mod | `govulncheck` |
| **Java** | maven/gradle | n/a / lockfile (Gradle 6.8+) | gradle | `mvn dependency-check` |
| **PHP** | composer | `composer.lock` | composer | `composer audit` |
| **.NET** | nuget | `packages.lock.json` | dotnet | `dotnet list package --vulnerable` |

---

## Quick Decision Guide (January 2026)

**Choose package manager based on:**

| Scenario | Recommendation |
|----------|----------------|
| New Node.js project | **pnpm** (stable, fast) or **Bun** (fastest) |
| Enterprise Node.js monorepo | **pnpm** (best workspace support) |
| Speed-focused JS development | **Bun** (7× faster than npm) |
| Existing npm project | Stay with npm or migrate to pnpm |
| New Python project | **uv** (10-100× faster than pip) |
| Python application (mature) | **Poetry** or **uv** |
| Simple Python scripts | pip + venv or uv |
| Data science / ML | **conda** or **uv** |
| Rust project | cargo (default) |
| Go project | go mod (default) |
| Java enterprise | maven or gradle |
| PHP project | composer |
| .NET project | nuget |

---

## Ecosystem-Specific Anti-Patterns

### Node.js

- [FAIL] Using `npm install` in CI (use `npm ci`)
- [FAIL] Not committing lockfiles
- [FAIL] Using `--force` or `--legacy-peer-deps` without understanding why
- [FAIL] Mixing package managers (npm + yarn in same project)

### Python

- [FAIL] Not using virtual environments
- [FAIL] Using `sudo pip install` (system-wide installs)
- [FAIL] Not pinning versions in `requirements.txt`
- [FAIL] Mixing conda and pip aggressively

### Rust

- [FAIL] Committing `Cargo.lock` for libraries (only for binaries)
- [FAIL] Not using `cargo audit` for security
- [FAIL] Ignoring `cargo clippy` warnings

### Go

- [FAIL] Not committing `go.sum`
- [FAIL] Using `go get` to install tools (use `go install`)
- [FAIL] Not running `go mod tidy` regularly

---

**Remember:** Each ecosystem has its own conventions and best practices. Follow the ecosystem's standards for the smoothest experience.
