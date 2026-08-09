# Rollout And Observability

Use this file when the request is about safe deployment, cost control, evaluation, or ongoing operations for AI features.

## Rollout Sequence

1. Ship behind a feature flag.
2. Start with internal or trusted-user traffic.
3. Measure cost, latency, refusal/error rate, and user feedback.
4. Expand gradually with a kill switch and clear rollback criteria.

## Core Metrics

- Latency by model and feature
- Tokens in/out per request
- Cost per user, feature, and workflow
- Schema-validation failure rate
- Tool-call failure rate
- User feedback rate and correction rate

### Instrumentation standard: OTel GenAI semantic conventions

For teams wiring these metrics into an existing observability stack (traces/metrics rather than a bespoke log table), OpenTelemetry's GenAI semantic conventions (`gen_ai.*` attributes, `gen_ai.client` spans for chat/embeddings calls) are the emerging standard for representing LLM calls as spans. As of 2026-07-11, sources disagree on stability: some 2026 reports describe `gen_ai.client` spans as having exited experimental status, while the official OpenTelemetry semantic-conventions docs continued to mark the GenAI conventions as **Development** status as recently as mid-2026 with no committed stabilization date. Treat the attribute names and span shape as **not yet a frozen wire contract** — verify current status at https://opentelemetry.io/docs/specs/semconv/gen-ai/ before building dashboards or alerts that assume schema stability. See [qa-observability](../../qa-observability/SKILL.md) for the general OTel setup this integrates with.

## Evaluation Loop

- Use deterministic test cases for regressions.
- Use human-reviewed samples for subjective quality.
- Track prompt/model changes against the same benchmark set.
- Record failures with prompt version, model version, and input class.

## Abuse And Spend Controls

- Per-user and per-feature rate limits
- Budget alerts and hard caps
- Request size limits before model invocation
- Caching for repeated or deterministic queries
