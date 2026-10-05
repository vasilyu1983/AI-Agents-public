---
paths:
  - "**/package-lock.json"
  - "**/pnpm-lock.yaml"
  - "**/yarn.lock"
  - "**/uv.lock"
  - "**/poetry.lock"
  - "**/Cargo.lock"
  - "**/go.sum"
  - "**/composer.lock"
description: Lockfile handling rules for package-manager lockfiles.
owner: skills/universal/dev-dependency-management/SKILL.md
---
Extends common/dependencies.md.
- Commit application lockfiles.
- Install from the lockfile exactly in CI (the package manager's frozen or locked mode).
- Never edit a lockfile by hand; change the manifest and let the package manager regenerate it.
- Keep one lockfile per package graph.
Why and procedure: skills/universal/dev-dependency-management/SKILL.md#lockfile-and-toolchain-policy
