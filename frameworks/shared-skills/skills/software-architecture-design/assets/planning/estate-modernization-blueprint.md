# Platform Estate Modernization Blueprint

Use this when the user is dealing with many repos, too many services, or a platform that has become harder to operate than to change.

- **Estate scope:** Repo count, runtime count, domains, critical journeys, regulatory boundaries, legacy dependencies
- **Current-state diagnosis:** Why the estate feels broken: runtime sprawl, ownership drift, mixed messaging, weak contracts, observability gaps, duplicated patterns
- **Repo classification:** For every repo, classify as runtime-platform, runtime-edge, provider-adapter, shared-library, channel-client, platform-tooling, absorption-candidate, or retirement-candidate
- **Runtime decision rule:** State which runtimes stay separate and why: scale, release cadence, trust boundary, compliance boundary, failure isolation
- **Target platform map:** Bounded-context platforms, shared platform services, BFF/edge layer, provider-adapter layer, legacy compatibility boundaries
- **API and event governance:** Registry ownership, versioning, contract tests, deprecation windows, schema evolution, consumer ownership
- **Data and consistency:** Sources of truth, outbox, idempotency, replayable DLQ, orchestration boundaries, reconciliation jobs
- **Platform defaults:** Golden-path templates, OpenTelemetry, health checks, secret handling, policy gates, rollback patterns, scorecards
- **Migration waves:** Standards first, backbone hardening second, consolidation third, adapter normalization fourth, legacy strangling last
- **What not to build:** Patterns to defer, services to avoid creating, infrastructure not yet justified
- **Success metrics:** Runtime count, change lead time, deployment frequency, incident rate, MTTR, trace coverage, golden-path adoption, contract-test coverage
