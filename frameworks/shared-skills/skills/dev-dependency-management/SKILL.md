---
name: dev-dependency-management
description: Package and dependency management patterns across ecosystems (npm, pip, cargo, maven). Covers lockfiles, semantic versioning, dependency security scanning, update strategies, monorepo workspaces, transitive dependencies, and avoiding dependency hell.
---

# Dependency Management — Production Patterns

**Modern Best Practices (January 2026)**: Lockfile-first workflows, automated security scanning (Dependabot, Snyk, Socket.dev), semantic versioning, minimal dependencies principle, monorepo workspaces (pnpm, Nx, Turborepo), supply chain security (SBOM, AI BOM, Sigstore), reproducible builds, and AI-generated code validation.

---

## When to Use This Skill

The agent should invoke this skill when a user requests:

- Adding new dependencies to a project
- Updating existing dependencies safely
- Resolving dependency conflicts or version mismatches
- Auditing dependencies for security vulnerabilities
- Understanding lockfile management and reproducible builds
- Setting up monorepo workspaces (pnpm, npm, yarn)
- Managing transitive dependencies and overrides
- Choosing between similar packages (bundle size, maintenance, security)
- Dependency version constraints and semantic versioning
- Dependency security best practices and supply chain security
- Troubleshooting "dependency hell" scenarios
- Package manager configuration and optimization
- Creating reproducible builds across environments

---

## Quick Reference

| Task | Tool/Command | Key Action | When to Use |
|------|--------------|------------|-------------|
| **Install from lockfile** | `npm ci`, `poetry install`, `cargo build` | Clean install, reproducible | CI/CD, production deployments |
| **Add dependency** | `npm install <pkg>`, `poetry add <pkg>` | Updates lockfile automatically | New feature needs library |
| **Update dependencies** | `npm update`, `poetry update`, `cargo update` | Updates within version constraints | Monthly/quarterly maintenance |
| **Check for vulnerabilities** | `npm audit`, `pip-audit`, `cargo audit` | Scans for known CVEs | Before releases, weekly |
| **View dependency tree** | `npm ls`, `pnpm why`, `pipdeptree` | Shows transitive dependencies | Debugging conflicts |
| **Override transitive dep** | `overrides` (npm), `pnpm.overrides` | Force specific version | Security patch, conflict resolution |
| **Monorepo setup** | `pnpm workspaces`, `npm workspaces` | Shared dependencies, cross-linking | Multi-package projects |
| **Check outdated** | `npm outdated`, `poetry show --outdated` | Lists available updates | Planning update sprints |

---

## Decision Tree: Dependency Management

```text
User needs: [Dependency Task]
    ├─ Adding new dependency?
    │   ├─ Check: Do I really need this? (Can implement in <100 LOC?)
    │   ├─ Check: Is it well-maintained? (Last commit <6 months, >10k downloads/week)
    │   ├─ Check: Bundle size impact? (Use Bundlephobia for JS)
    │   ├─ Check: Security risks? (`npm audit`, Snyk)
    │   └─ If all checks pass → Add with `npm install <pkg>` → Commit lockfile
    │
    ├─ Updating dependencies?
    │   ├─ Security vulnerability? → `npm audit fix` → Test → Deploy immediately
    │   ├─ Routine update?
    │       ├─ Patch versions → `npm update` → Safe, do frequently
    │       ├─ Minor/major → Check CHANGELOG → Test in staging → Update gradually
    │       └─ All at once → [FAIL] RISKY → Update in batches instead
    │
    ├─ Dependency conflict?
    │   ├─ Transitive dependency issue?
    │       ├─ View tree: `npm ls <package>`
    │       ├─ Use overrides sparingly: `overrides` in package.json
    │       └─ Document why override is needed
    │   └─ Peer dependency mismatch?
    │       └─ Check version compatibility → Update parent or child
    │
	├─ Monorepo project?
	│   ├─ Use pnpm workspaces (recommended default)
	│   ├─ Shared deps → Root package.json
	│   ├─ Package-specific → Package directories
	│   └─ Use Nx or Turborepo for task caching
	│
	└─ Choosing package manager?
	    ├─ New JS project → **pnpm** (recommended default) or **Bun** (often faster; verify ecosystem maturity)
	    ├─ Enterprise monorepo → **pnpm** (mature workspace support)
	    ├─ Speed-focused experimentation → **Bun** (verify ecosystem maturity)
	    ├─ Existing npm project → Migrate to pnpm or stay (check team preference)
	    ├─ Python → **uv** (fast), Poetry (mature), pip+venv (simple)
	    └─ Data science → **conda** or **uv** (faster environment setup)
```

---

## Navigation: Core Patterns

### Lockfile Management

**[`references/lockfile-management.md`](references/lockfile-management.md)**

Lockfiles ensure reproducible builds by recording exact versions of all dependencies (direct + transitive). Essential for preventing "works on my machine" issues.

- Golden rules (always commit, never edit manually, regenerate on changes)
- Commands by ecosystem (npm ci, poetry install, cargo build)
- Troubleshooting lockfile conflicts
- CI/CD integration patterns

### Semantic Versioning (SemVer)

**[`references/semver-guide.md`](references/semver-guide.md)**

Understanding version constraints (`^`, `~`, exact) and how to specify dependency ranges safely.

- SemVer format (MAJOR.MINOR.PATCH)
- Version constraint syntax (caret, tilde, exact)
- Recommended strategies by project type
- Cross-ecosystem version management

### Dependency Security Auditing

**[`references/security-scanning.md`](references/security-scanning.md)**

Automated security scanning, vulnerability management, and supply chain security best practices.

- Automated tools (Dependabot, Snyk, GitHub Advanced Security)
- Running audits (npm audit, pip-audit, cargo audit)
- CI integration and alert configuration
- Incident response workflows

### Dependency Selection

**[`references/dependency-selection-guide.md`](references/dependency-selection-guide.md)**

Deciding whether to add a new dependency and choosing between similar packages.

- Minimal dependencies principle (best dependency is the one you don't add)
- Evaluation checklist (maintenance, bundle size, security, alternatives)
- Choosing between similar packages (comparison matrix)
- When to reject a dependency

### Update Strategies

**[`references/update-strategies.md`](references/update-strategies.md)**

Keeping dependencies up to date safely while minimizing breaking changes and security risks.

- Update strategies (continuous, scheduled, security-only)
- Safe update workflow (check outdated, categorize risk, test, deploy)
- Automated update tools (Dependabot, Renovate, npm-check-updates)
- Handling breaking changes and rollback plans

### Monorepo Management

**[`references/monorepo-patterns.md`](references/monorepo-patterns.md)**

Managing multiple related packages in a single repository with shared dependencies.

- Workspace tools (pnpm, npm, yarn workspaces)
- Monorepo structure and organization
- Build optimization (Nx, Turborepo)
- Versioning and publishing strategies

### Transitive Dependencies

**[`references/transitive-dependencies.md`](references/transitive-dependencies.md)**

Dealing with dependencies of your dependencies (indirect dependencies).

- Viewing dependency trees (npm ls, pnpm why, pipdeptree)
- Resolving transitive conflicts (overrides, resolutions, constraints)
- Security risks and version conflicts
- Best practices (use sparingly, document, test)

### Ecosystem-Specific Guides

**[`references/ecosystem-guides.md`](references/ecosystem-guides.md)**

Language and package-manager-specific best practices.

- Node.js (npm, yarn, pnpm comparison and best practices)
- Python (pip, poetry, conda)
- Rust (cargo), Go (go mod), Java (maven, gradle)
- PHP (composer), .NET (nuget)

### Anti-Patterns

**[`references/anti-patterns.md`](references/anti-patterns.md)**

Common mistakes to avoid when managing dependencies.

- Critical anti-patterns (not committing lockfiles, wildcards, ignoring audits)
- Dangerous anti-patterns (never updating, deprecated packages)
- Moderate anti-patterns (overusing overrides, ignoring peer deps)

---

## Navigation: Templates

### Node.js

**[`assets/nodejs/`](assets/nodejs/)**

- [`package-json-template.json`](assets/nodejs/package-json-template.json) - Production-ready package.json with best practices
- `npmrc-template.txt` - Team configuration for npm
- [`pnpm-workspace-template.yaml`](assets/nodejs/pnpm-workspace-template.yaml) - Monorepo workspace setup

### Python

**[`assets/python/`](assets/python/)**

- [`pyproject-toml-template.toml`](assets/python/pyproject-toml-template.toml) - Poetry configuration with best practices

### Automation

**[`assets/automation/`](assets/automation/)**

- [`dependabot-config.yml`](assets/automation/dependabot-config.yml) - GitHub Dependabot configuration
- [`renovate-config.json`](assets/automation/renovate-config.json) - Renovate Bot configuration
- [`audit-checklist.md`](assets/automation/audit-checklist.md) - Security audit workflow
- **[`template-supply-chain-security.md`](assets/automation/template-supply-chain-security.md)** - **NEW** SBOM, provenance, vulnerability management
- [`template-dependency-upgrade-playbook.md`](assets/automation/template-dependency-upgrade-playbook.md) - Upgrade batching, rollout, rollback
- [`template-sbom-vuln-triage-checklist.md`](assets/automation/template-sbom-vuln-triage-checklist.md) - SBOM mapping + vulnerability triage

---

## Supply Chain Security

**[assets/automation/template-supply-chain-security.md](assets/automation/template-supply-chain-security.md)** — Production-grade dependency security.

Related templates:
- [assets/automation/template-dependency-upgrade-playbook.md](assets/automation/template-dependency-upgrade-playbook.md)
- [assets/automation/template-sbom-vuln-triage-checklist.md](assets/automation/template-sbom-vuln-triage-checklist.md)

### Key Sections

- **SBOM Generation** — CycloneDX, SPDX formats; CI/CD integration
- **AI BOM (Emerging)** — Extended SBOM for AI-native systems (models, datasets, training artifacts)
- **Provenance & Attestation** — SLSA levels, Sigstore signing, npm provenance
- **Vulnerability Management** — Triage workflow, severity SLAs, scanning tools
- **Upgrade Playbooks** — Batching strategy, rollback procedures
- **Pinning & Reproducibility** — Lockfiles, hash pinning, version constraints
- **EU Cyber Resilience Act** — SBOM requirements effective Dec 2027

### Do / Avoid

#### GOOD: Do

- Generate SBOM for every release
- Sign release artifacts (Sigstore/cosign)
- Run vulnerability scans in CI/CD
- Fix critical vulnerabilities within 24 hours
- Use lockfiles for reproducible builds
- Verify npm package provenance
- Batch non-security updates by risk level

#### BAD: Avoid

- Publishing without SBOM
- Using unsigned packages in production
- Ignoring vulnerability scanner output
- Updating all dependencies at once
- Using wildcard version ranges (`*`, `>=`)
- Committing without updating lockfile
- Bypassing security gates "just this once"

### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No SBOM** | Can't respond to supply chain attacks | Generate SBOM in CI/CD |
| **Unsigned artifacts** | Tampering undetectable | Sign with Sigstore |
| **Floating versions** | Build not reproducible | Use lockfiles + exact versions |
| **All-at-once updates** | Hard to bisect regressions | Batch by risk level |
| **npm install in CI** | Non-deterministic | Use `npm ci` |
| **No audit gate** | Vulnerabilities ship to prod | Gate deployments on audit |

---

## AI-Generated Dependency Risks

> **WARNING**: AI coding agents can introduce vulnerable or non-existent packages at scale (Endor Labs, 2025).

### The Problem

AI tools accelerate coding but introduce supply chain risks:

- **Hallucinated packages** — AI suggests packages that don't exist (typosquatting vectors)
- **Vulnerable dependencies** — AI recommends outdated or CVE-affected versions
- **Unnecessary dependencies** — AI over-relies on packages for simple tasks

### Best Practices

| Do | Don't |
| --- | --- |
| Treat AI-generated code as untrusted third-party input | Blindly accept AI dependency suggestions |
| Enforce same SAST/SCA scanning for AI-generated code | Skip security review for "AI-written" code |
| Verify all AI-suggested packages actually exist | Trust AI to know current package versions |
| Integrate security tools into AI workflows (MCP) | Allow AI to add dependencies without review |
| Vet MCP servers as part of supply chain | Use unvetted AI integrations |

### Validation Checklist

Before accepting AI-suggested dependencies:

- [ ] Package exists on registry (npm, PyPI, crates.io)
- [ ] Package name is spelled correctly (no typosquatting)
- [ ] Version is current and maintained
- [ ] `npm audit` / `pip-audit` shows no vulnerabilities
- [ ] Weekly downloads >1000 (established package)
- [ ] Last commit <6 months (actively maintained)

---

## Optional: AI/Automation

> **Note**: AI assists with triage but security decisions need human judgment.

- **Automated PR triage** — Categorize dependency updates by risk
- **Changelog summarization** — Summarize breaking changes in updates
- **Vulnerability correlation** — Link CVEs to affected packages

### Bounded Claims

- AI cannot determine business risk acceptance
- Automated fixes require security team review
- Vulnerability severity context needs human validation

---

## Quick Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Adding new dependency | Check Bundlephobia, npm audit, weekly downloads, last commit |
| Updating dependencies | Use `npm outdated`, update in batches, test in staging |
| Security vulnerability found | Use `npm audit fix`, review CHANGELOG, test, deploy immediately |
| Monorepo setup | Use **pnpm workspaces** or Nx/Turborepo for build caching |
| Transitive conflict | Use `overrides` sparingly, document why, test thoroughly |
| Choosing JS package manager | **pnpm** (fastest, disk-efficient), **Bun** (7× faster), npm (most compatible) |
| Python environment | **uv** (10-100× faster), Poetry (mature), pip+venv (simple), conda (data science) |

---

## Core Principles

### 1. Always Commit Lockfiles

Lockfiles ensure reproducible builds across environments. Never add them to `.gitignore`.

**Exception**: Don't commit `Cargo.lock` for Rust libraries (only for applications).

### 2. Use Semantic Versioning

Use caret (`^`) for most dependencies, exact versions for mission-critical, avoid wildcards (`*`).

```json
{
  "dependencies": {
    "express": "^4.18.0",  // Allows patches and minors
    "critical-lib": "1.2.3"  // Exact for critical
  }
}
```

### 3. Audit Dependencies Regularly

Run security audits weekly, fix critical vulnerabilities immediately.

```bash
npm audit
npm audit fix
```

### 4. Minimize Dependencies

The best dependency is the one you don't add. Ask: Can I implement this in <100 LOC?

### 5. Update Regularly

Update monthly or quarterly. Don't let technical debt accumulate.

```bash
npm outdated
npm update
```

### 6. Use Overrides Sparingly

Only override transitive dependencies for security patches or conflicts. Document why.

```json
{
  "overrides": {
    "axios": "1.6.0"  // CVE-2023-xxxxx fix
  }
}
```

---

## Related Skills

For complementary workflows and deeper dives:

- [`dev-api-design`](../dev-api-design/SKILL.md) - API versioning strategies, dependency injection patterns
- [`git-workflow`](../git-workflow/SKILL.md) - Git workflows for managing lockfile conflicts, branching strategies
- [`qa-testing-strategy`](../qa-testing-strategy/SKILL.md) - Testing strategies for dependency updates, integration testing
- [`software-security-appsec`](../software-security-appsec/SKILL.md) - OWASP Top 10, cryptography standards, authentication patterns
- [`ops-devops-platform`](../ops-devops-platform/SKILL.md) - CI/CD pipelines, Docker containerization, DevSecOps, deployment automation
- [`docs-codebase`](../docs-codebase/SKILL.md) - Documenting dependency choices, ADRs, changelogs

---

## External Resources

See [`data/sources.json`](data/sources.json) for curated resources:

- **Package managers**: npm, pnpm, Yarn, pip, Poetry, Cargo, Go modules, Maven, Composer
- **Semantic versioning**: SemVer spec, version calculators, constraint references
- **Security tools**: Snyk, Dependabot, GitHub Advanced Security, OWASP Dependency-Check, pip-audit, cargo-audit, Socket.dev, Renovate
- **Lockfile management**: Official docs for package-lock.json, poetry.lock, Cargo.lock, pnpm-lock.yaml
- **Monorepo tools**: pnpm workspaces, npm workspaces, Yarn workspaces, Nx, Turborepo, Lerna, Bazel
- **Analysis tools**: Bundlephobia, npm-check-updates, depcheck, pipdeptree, cargo tree
- **Supply chain security**: SLSA framework, SBOM (CISA), Sigstore, npm provenance, OpenSSF Scorecard
- **Best practices**: npm/Poetry/Cargo guides, ACM Queue articles, dependency hell references
- **Version management**: nvm, pyenv, rustup, asdf
- **Learning resources**: npm guides, Python Packaging User Guide, Rust Book, Monorepo.tools

---

## Usage Notes

**For Codex / Claude Code:**

- Use this skill when users need dependency management guidance
- Reference specific resources based on the task (lockfiles, security, updates)
- Provide ecosystem-specific guidance (Node.js, Python, Rust)
- Always recommend security audits and reproducible builds
- Encourage minimal dependencies and regular updates
- Link to templates for common configurations

**Best Practices:**

- Always commit lockfiles (except Cargo.lock for libraries)
- Use semantic versioning (caret for most deps, exact for critical)
- Audit dependencies weekly (`npm audit`, `pip-audit`, `cargo audit`)
- Update dependencies monthly or quarterly (not all at once)
- Choose package manager based on project needs (pnpm for speed, Poetry for Python apps)
- Document dependency choices in ADRs (Architecture Decision Records)

---

> **Success Criteria:** Dependencies are minimal, well-maintained, secure, reproducible across environments, and regularly audited for vulnerabilities.

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about package managers, dependency tools, or supply chain security, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best package manager for [ecosystem]?"
- "What should I use for [dependency management/security]?"
- "What's the latest in dependency management?"
- "Current best practices for [npm/pnpm/Poetry]?"
- "Is [tool/approach] still relevant in 2026?"
- "[pnpm] vs [npm] vs [yarn]?"
- "Best dependency security scanner?"

### Required Searches

1. Search: `"dependency management best practices 2026"`
2. Search: `"[specific tool] vs alternatives 2026"`
3. Search: `"supply chain security trends January 2026"`
4. Search: `"[package manager] features 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What dependency tools are popular NOW
- **Emerging trends**: New package managers, security tools, or patterns gaining traction
- **Deprecated/declining**: Tools/approaches losing relevance or support
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- Package managers (pnpm, npm, yarn, Poetry, uv for Python)
- Security scanning (Snyk, Dependabot, Socket.dev)
- Supply chain security (SBOM, Sigstore, SLSA)
- Monorepo tools (Nx, Turborepo, Bazel)
- Lockfile and reproducibility patterns
- Automated dependency updates (Renovate, Dependabot)
