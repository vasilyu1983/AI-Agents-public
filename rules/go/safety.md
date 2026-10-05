---
paths:
  - "**/*.go"
description: Error-wrapping, context, race-test, and vulnerability-scan rules for Go code.
owner: skills/universal/software-backend/SKILL.md
---
Extends common/errors.md.
- Wrap a returned error with the operation and `%w`; test it with `errors.Is` or `errors.As`, never `==` on an error that may be wrapped.
- Take `ctx context.Context` as the first parameter of each function that does I/O, and set a deadline on each outbound call.
- Run tests with `-race` in CI.
- Run `govulncheck ./...` and a static analyser such as `gosec` in CI.
Why and procedure: skills/universal/software-backend/references/go-best-practices.md#error-handling
