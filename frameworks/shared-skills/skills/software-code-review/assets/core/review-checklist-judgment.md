# Review Checklist (Judgment-Based)

## Core

- Intent: PR description explains what and why; diff matches intent (https://google.github.io/eng-practices/review/developer/cl-descriptions.html).
- Size: if too large to review effectively, request a split (https://google.github.io/eng-practices/review/developer/small-cls.html).
- Correctness: walk the happy path, key error paths, and boundaries.
- Risk: identify blast radius, rollout/rollback, and migration risk if applicable.
- Security/privacy: confirm trust boundaries, authz checks, and safe data handling.
- Operability: confirm diagnosability (logs/metrics/traces) for critical paths (https://opentelemetry.io/docs/).
- Tests: new behavior has tests; bug fixes have regression tests.
- Standards: cite `CC-*` IDs from the clean code standard; do not restate rules ([../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)).

## Optional: AI / Automation

- CI is green and branch protection rules are enforced (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- Review routing uses CODEOWNERS where appropriate (https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).
- Automation output (linters/SAST/SCA) is mapped to `CC-*` IDs when possible.
- AI suggestions are advisory only; human reviewers validate and approve.
