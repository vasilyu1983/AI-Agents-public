# Cache Migrations And Install Channels

Local state is part of the product surface for a coding-agent CLI.

## Version what matters

Version these independently when needed:

- session-state schema
- plugin cache schema
- tool-registry cache schema
- settings or policy schema
- binary or package version

One app version number is rarely enough to reason about all local state safely.

## Migration rules

- Prefer additive migrations where possible.
- Keep startup checks fast and deterministic.
- Make destructive cache resets explicit when they are unavoidable.
- Support downgrade detection, not only upgrade migration.
- Separate “must migrate now” from “best-effort cleanup.”

## Install-channel behavior

Different channels may justify different migration posture:

- stable should bias toward conservative compatibility
- beta may run migrations earlier but must still surface risk clearly
- nightly can invalidate caches aggressively, but only if the product makes that expectation explicit

## Edge cases

- **Old session resumes on new binary**: decide whether resume is supported, migrated, or blocked with an explanation.
- **Plugin cache from incompatible channel**: a stable binary should not blindly trust a nightly-generated cache.
- **Rollback after partial migration**: if rollback is possible, keep enough version metadata to refuse unsafe startup.
- **Local footprint growth**: logs, traces, session histories, and downloaded registries need retention limits.

## Practical tip

The cleanest migration system is the one that can explain, in one sentence, why a given local artifact is reused, migrated, or discarded.
