# Dependency Audit Checklist

Use this checklist to review a repo's dependency posture without defaulting to ecosystem-specific cargo cult rules.

## 1. Inventory

- [ ] Confirm the active package manager or dependency workflow for each ecosystem root
- [ ] Confirm there is exactly one lockfile for each package graph
- [ ] Snapshot direct dependencies and outdated packages

```bash
# Node.js
npm ls --depth=0
npm outdated
pnpm outdated -r
yarn outdated
bun outdated

# Python
uv tree
uv tree --outdated
poetry show --latest

# Rust / Go / .NET / PHP
cargo tree
go list -m all
dotnet list package
composer show
```

## 2. Lockfile And Toolchain Hygiene

- [ ] Exact install command exists and is used in CI
- [ ] Package-manager or wrapper version is pinned
- [ ] Lockfile matches the manifest and toolchain version
- [ ] No surprise registry or source changes appear in lockfile diffs

## 3. Security Review

- [ ] Run the native audit command for the ecosystem
- [ ] Review install/build scripts or plugins from dependencies
- [ ] Verify whether provenance, signatures, or trusted publishing are available
- [ ] Generate or refresh an SBOM for the release artifact

```bash
npm audit --audit-level=high
npm sbom --sbom-format=spdx
pip-audit
cargo audit
govulncheck ./...
composer audit
dotnet list package --vulnerable --include-transitive
```

## 4. Package Quality Review

- [ ] Check release cadence and changelog quality
- [ ] Check maintainer responsiveness and ownership stability
- [ ] Check dependency graph size and peer/runtime requirements
- [ ] Check whether the package is still the right fit for the current ecosystem

## 5. Monorepo Review

- [ ] Dependency change is scoped to the correct workspace or ecosystem root
- [ ] PR does not mix package-manager migration with ordinary upgrades
- [ ] Only the expected lockfiles changed
- [ ] Task-runner cache or wrapper behavior still matches the dependency graph

## 6. Outcome

- [ ] Remove unnecessary dependencies
- [ ] Record temporary pins and overrides with owner and expiry
- [ ] Define next actions: patch now, batch later, migrate toolchain, or accept risk with review date
