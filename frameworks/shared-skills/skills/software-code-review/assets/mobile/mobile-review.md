# Mobile App Code Review Checklist

Use this template when reviewing iOS/Android/React Native changes.

## Core

### Standards

- Clean code standard (cite `CC-*` IDs): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Shared mobile release readiness checklist (pre-release gates): [../../../software-clean-code-standard/assets/checklists/mobile-release-checklist.md](../../../software-clean-code-standard/assets/checklists/mobile-release-checklist.md)
- Shared secure code review checklist (baseline): [../../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)

### Intent & Scope

- [ ] PR description states what/why/scope; risk and rollback plan are present.
- [ ] Diff matches intent; unrelated refactors are split or explicitly justified.

### Platform Correctness

- [ ] Lifecycle and state management align with platform patterns; state restores correctly after background/kill/rotation.
- [ ] UI thread is not blocked; expensive work is moved off main thread with explicit cancellation where supported.
- [ ] Memory/leak risks assessed (listeners, observers, subscriptions, image caching).
- [ ] Permissions, deep links, push notifications, and background work behave correctly (as applicable).

### UX & Accessibility

- [ ] Touch targets, dynamic type/font scaling, and screen reader support are validated for changed flows.
- [ ] Loading/empty/error states are correct and recoverable.

### Security & Privacy

- [ ] Secrets are not hardcoded or logged (cite `CC-SEC-03`, `CC-OBS-02`).
- [ ] Auth/session tokens follow policy (CSPRNG + expiry/rotation) (cite `CC-SEC-07`).
- [ ] Sensitive data is stored using platform secure storage (Keychain/Keystore); errors do not leak sensitive context (cite `CC-ERR-02`).

### Reliability & Performance

- [ ] Work is bounded for untrusted/large inputs (cite `CC-PERF-01`).
- [ ] Obvious hazards avoided (e.g., unbounded list rendering, repeated network calls) (cite `CC-PERF-02`).
- [ ] Network and I/O have explicit timeouts and retry bounds where supported (cite `CC-ERR-03`, `CC-ERR-04`).
- [ ] Offline/poor-network behavior is acceptable for the product (cache, retry UI, backoff).

### Observability

- [ ] Crash reporting and telemetry exist for critical user flows (cite `CC-OBS-03`).
- [ ] Logs are structured where applicable and include correlation identifiers; no sensitive data (cite `CC-OBS-01`, `CC-OBS-02`).

### Tests

- [ ] New behavior is covered; bug fixes include regression tests (cite `CC-TST-01`).
- [ ] Tests are deterministic (no time/network flake) (cite `CC-TST-02`).
- [ ] Critical flows have UI/integration coverage where risk warrants (cite `CC-TST-04`).

## Optional: AI / Automation

- [ ] Static analysis and CI checks are green; automation findings mapped to `CC-*` IDs where possible.
- [ ] If shipping AI features: privacy boundaries, safe fallbacks, and user-visible recovery are explicit [Inference].
