# Container Dependency Patterns

> Operational reference for managing dependencies in containerized environments — multi-stage builds, layer caching, base image selection, vulnerability scanning, and reproducible builds.

**Freshness anchor:** January 2026 — aligned with Docker Engine 27.x, BuildKit 0.17, Trivy 0.58, Grype 0.83, and OCI Image Spec v1.1.

---

## Base Image Selection Decision Tree

```
What runtime do you need?
├── Static binary (Go, Rust)
│   └── Use distroless/static or scratch
├── Minimal runtime (Node.js, Python, Java)
│   ├── Need shell access for debugging?
│   │   ├── YES → Alpine variant (e.g., node:22-alpine)
│   │   └── NO → Distroless (e.g., gcr.io/distroless/nodejs22-debian12)
│   └── Need specific system libraries (native extensions)?
│       ├── YES → Debian slim (e.g., node:22-slim)
│       └── NO → Alpine variant
└── Complex system dependencies (ML, scientific computing)
    └── Use Debian slim or Ubuntu LTS
        └── Pin to specific version tag, never use :latest
```

### Base Image Comparison

| Base | Size (compressed) | Package Manager | Shell | CVE surface | Use when |
|---|---|---|---|---|---|
| `scratch` | 0 MB | None | No | Minimal | Static binaries only |
| `distroless/static` | ~2 MB | None | No | Very low | Go, Rust static binaries |
| `distroless/base` | ~20 MB | None | No | Low | C/C++ with glibc |
| `alpine:3.21` | ~3 MB | apk | Yes (ash) | Low | General minimal containers |
| `debian:bookworm-slim` | ~30 MB | apt | Yes (bash) | Medium | Native extensions needed |
| `ubuntu:24.04` | ~30 MB | apt | Yes (bash) | Medium | Complex dependency chains |

### Alpine Gotchas Checklist

- [ ] Uses musl libc, not glibc — some native extensions may fail
- [ ] Python packages with C extensions may need `apk add build-base`
- [ ] DNS resolution differences (musl resolver) — test thoroughly
- [ ] No locales by default — add if needed for i18n
- [ ] Smaller community for troubleshooting vs Debian

---

## Multi-Stage Build Patterns

### Standard Multi-Stage Pattern

```dockerfile
# ---- Build stage ----
FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

# ---- Production stage ----
FROM node:22-alpine AS production

WORKDIR /app
ENV NODE_ENV=production

# Install production deps only
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force

# Copy built artifacts from builder
COPY --from=builder /app/dist ./dist

# Non-root user
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -D appuser
USER appuser

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Build vs Runtime Dependencies

| Category | Examples | Stage |
|---|---|---|
| Build tools | gcc, make, python3 (node-gyp) | Build stage only |
| Dev dependencies | jest, eslint, typescript | Build stage only |
| Build artifacts | compiled JS, binaries, bundled CSS | Copy to production stage |
| Runtime dependencies | express, pg, redis | Production stage |
| System runtime libs | libssl, libc | Production base image |

### Multi-Stage Checklist

- [ ] Build dependencies NOT present in final image
- [ ] Dev dependencies NOT installed in production stage
- [ ] Only necessary artifacts copied from build stage
- [ ] Final stage uses minimal base image
- [ ] Final stage runs as non-root user
- [ ] npm/pip/apt caches cleaned in the same RUN layer

---

## Layer Caching Optimization

### Layer Ordering Rules

```
Most stable layers first → Least stable layers last

1. Base image (changes rarely)
2. System package installation (changes monthly)
3. Language runtime config (changes per-project)
4. Dependency manifests COPY (changes when deps update)
5. Dependency install RUN (cached if manifests unchanged)
6. Application source COPY (changes every commit)
7. Build command RUN (runs every commit)
```

### Caching Optimization Checklist

- [ ] `COPY package.json package-lock.json ./` BEFORE `COPY . .`
- [ ] Dependency install (`npm ci`) in separate layer from source copy
- [ ] System packages installed in single `RUN` with `&&` chaining
- [ ] `.dockerignore` excludes: `node_modules`, `.git`, `dist`, `*.md`, tests
- [ ] BuildKit cache mounts used for package manager caches

### BuildKit Cache Mounts

```dockerfile
# Node.js - cache npm
RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts

# Python - cache pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-compile -r requirements.txt

# Go - cache module downloads and build cache
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -o /app/server ./cmd/server

# Rust - cache cargo registry and build artifacts
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    cargo build --release
```

### .dockerignore Template

```
.git
.github
node_modules
dist
build
*.md
*.log
.env*
.vscode
.idea
tests
__tests__
coverage
docker-compose*.yml
Makefile
```

---

## Vulnerability Scanning

### Tool Comparison

| Tool | Type | CI Integration | Database | License |
|---|---|---|---|---|
| Trivy | Image + FS + IaC | GitHub Actions, GitLab CI | Multiple (NVD, GHSA) | Apache 2.0 |
| Grype | Image + FS | GitHub Actions | Anchore feed | Apache 2.0 |
| Docker Scout | Image | Docker Desktop, CI | Docker advisory DB | Free tier |
| Snyk Container | Image | CI/CD, IDE | Snyk DB | Free tier |

### Trivy Integration

```bash
# Scan a built image
trivy image --severity HIGH,CRITICAL myapp:latest

# Scan with exit code for CI gating
trivy image --exit-code 1 --severity CRITICAL myapp:latest

# Scan filesystem (lock files)
trivy fs --scanners vuln /app

# Scan and output SARIF for GitHub Security
trivy image --format sarif --output results.sarif myapp:latest

# Ignore unfixed vulnerabilities
trivy image --ignore-unfixed myapp:latest
```

### Grype Integration

```bash
# Scan an image
grype myapp:latest

# Fail on high/critical
grype myapp:latest --fail-on high

# Output JSON for processing
grype myapp:latest -o json > results.json
```

### Scanning Pipeline Checklist

- [ ] Scan on every image build in CI
- [ ] Gate deployments on CRITICAL vulnerabilities (fail the build)
- [ ] HIGH vulnerabilities tracked as tickets, fixed within SLA
- [ ] Base image scanned separately from application layer
- [ ] `.trivyignore` or Grype config for accepted risks (with expiration dates)
- [ ] Weekly scheduled scan of deployed images (catch new CVEs)
- [ ] SBOM generated and stored (`trivy image --format spdx-json`)

### Vulnerability SLA Reference

| Severity | Fix SLA | Action |
|---|---|---|
| CRITICAL | 24-48 hours | Immediate patch or mitigation |
| HIGH | 7 days | Prioritize in current sprint |
| MEDIUM | 30 days | Schedule in backlog |
| LOW | 90 days | Address during maintenance |

---

## Reproducible Builds

### Pinning Strategies

| What to Pin | How | Example |
|---|---|---|
| Base image | SHA256 digest | `FROM node:22-alpine@sha256:abc123...` |
| System packages | Version specifier | `apk add --no-cache curl=8.5.0-r0` |
| Language deps | Lockfile | `package-lock.json`, `poetry.lock` |
| Build tools | Version in Dockerfile | `ARG BUILDKIT_VERSION=0.17.0` |

### Reproducibility Checklist

- [ ] Base images pinned to digest (not just tag)
- [ ] Lockfiles committed and used (`npm ci`, not `npm install`)
- [ ] `--ignore-scripts` flag used during install (run scripts explicitly if needed)
- [ ] No `curl | bash` patterns for installing tools (pin versions instead)
- [ ] `apt-get` uses `--no-install-recommends`
- [ ] Build arguments used for version pins (visible, overridable)
- [ ] Timezone and locale set explicitly if needed
- [ ] `COPY` uses specific paths, not `.` (avoids accidental inclusion)

### Base Image Update Strategy

```
Is there a CRITICAL CVE in the base image?
├── YES → Update immediately
│   ├── Rebuild and test
│   └── Deploy within SLA
└── NO
    ├── Monthly: check for base image updates
    ├── Quarterly: evaluate major version bumps
    └── Automate with Renovate/Dependabot
        └── Auto-PR for digest updates
        └── Manual review for major version changes
```

---

## Language-Specific Patterns

### Node.js

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build && npm prune --production
```

- Use `npm ci` (not `npm install`) for reproducibility
- `npm prune --production` removes dev deps after build
- Set `NODE_ENV=production` in production stage

### Python

```dockerfile
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir poetry==1.8.5
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim
COPY --from=builder /install /usr/local
COPY . /app
WORKDIR /app
```

- Use `poetry export` or `pip-compile` for deterministic installs
- `--prefix=/install` allows clean copy of installed packages

### Go

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /server ./cmd/server

FROM scratch
COPY --from=builder /server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/server"]
```

- `CGO_ENABLED=0` for static binary
- `-ldflags="-s -w"` strips debug info (smaller binary)
- `scratch` base image for minimal surface

### Rust

```dockerfile
FROM rust:1.84-slim AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
COPY src ./src
RUN touch src/main.rs && cargo build --release

FROM gcr.io/distroless/cc-debian12
COPY --from=builder /app/target/release/myapp /
ENTRYPOINT ["/myapp"]
```

- Dummy `main.rs` trick caches dependency compilation
- `touch` forces rebuild of application code only

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Using `:latest` tag | Non-reproducible, unpredictable updates | Pin to version tag or SHA digest |
| Installing dev tools in production image | Larger image, bigger attack surface | Multi-stage build, copy artifacts only |
| Running as root | Security vulnerability | `USER nonroot` or `USER 1001` |
| `COPY . .` before dependency install | Busts cache on every code change | Copy manifests first, install, then copy source |
| `apt-get install` without `--no-install-recommends` | Bloated image with unnecessary packages | Always use `--no-install-recommends` |
| No `.dockerignore` | `.git`, `node_modules` copied into build context | Maintain `.dockerignore` |
| Multiple `RUN apt-get` commands | Wasted layers, cache issues | Chain with `&&` in single `RUN` |
| Ignoring vulnerability scan results | Known CVEs in production | Gate CI on CRITICAL, SLA for HIGH |
| `npm install` instead of `npm ci` | Non-deterministic dependency resolution | Always use `npm ci` with lockfile |
| No health check | Orchestrator cannot detect unhealthy containers | Add `HEALTHCHECK` instruction |

---

## Cross-References

- `dev-dependency-management/references/version-conflict-resolution.md` — resolving conflicts in lockfiles
- `dev-dependency-management/references/license-compliance.md` — scanning container images for license issues
- `software-security-appsec/references/threat-modeling-guide.md` — container threat model
- `software-backend/references/nodejs-best-practices.md` — Node.js containerization specifics
- `qa-observability/references/log-aggregation-patterns.md` — container logging patterns
