# Backend template maintenance guide

Load this file only when maintaining a template in `assets/`. For implementation, use the selected stack template from [SKILL.md](../SKILL.md#templates); this guide does not select a runtime or repeat framework basics.

## Before editing a template

1. Confirm the stack belongs to software-backend. C#/.NET belongs to [software-csharp-backend](../../software-csharp-backend/SKILL.md); API contracts to [dev-api-design](../../dev-api-design/SKILL.md); managed data/auth choices to [software-baas-platforms](../../software-baas-platforms/SKILL.md).
2. Check the selected runtime and database release policies against their official docs. Keep version pins in the runnable manifest or Dockerfile, with a link to the lookup; do not call an old version “latest.”
3. Compare the candidate template with the default for its language. A non-default ORM/framework file should contain only the difference, a migration warning where needed, and a test of that difference.
4. Inspect inbound links before changing headings or examples; a linked reference must still load at the decision step that needs it.

## Required contract

| Area | Keep in the template |
|------|----------------------|
| Boundary | Request validation, principal/tenant derivation, authorization point, structured error response |
| Effects | Transaction and idempotency scope, outcome-unknown handling, outbox or receiver dedupe when effects cross systems |
| Dependencies | Explicit deadlines, cancellation, bounded concurrency and retry ownership |
| Data | Supported PostgreSQL major, reviewed migration, pool limit, hot-query plan check |
| Operations | Readiness/liveness, structured traces/logs, drain on shutdown, rollback and smoke step |
| Tests | One failed dependency, one concurrent retry, and one rollback or crash-history case appropriate to the stack |

Make a runnable example honest: name placeholders, state which modules are illustrative, and do not claim that a snippet is production-ready without an executable fixture. A Docker stage must use a supported builder toolchain and compatible target architecture; derive the version from the project's manifest and the official release policy. Avoid embedding prices, cloud limits or current package versions in the prose.

## Source checks

- [PostgreSQL versioning and support](https://www.postgresql.org/support/versioning/)
- [Go release policy](https://go.dev/doc/devel/release)
- [Node release schedule](https://github.com/nodejs/Release#release-schedule)
- [Python status](https://devguide.python.org/versions/)
- [Rust release notes](https://doc.rust-lang.org/releases.html)
- Consult the selected framework, ORM and hosting provider's primary migration and runtime documentation before changing executable samples.
