# Rollout And Observability

Use this file when the request is about safe deployment, cost control, evaluation, or ongoing operations for AI features.

## Rollout Sequence

1. Ship behind a feature flag.
2. Start with internal or trusted-user traffic.
3. Measure cost, latency, refusal/error rate, and user feedback.
4. Expand gradually with a kill switch and clear rollback criteria.

## Multi-Provider Rollout Steps

| Step | Implementation |
|------|---------------|
| Abstraction | `providerA('<model-id>')` swappable for `providerB('<comparable-model-id>')` behind one interface, without changing call sites — resolve the exact current model IDs at each provider's docs at use-time, never hardcode a "best model" from memory |
| Fallback chain | Primary → fallback → degraded mode; circuit breaker after N failures in M seconds |
| Model variants | Maintain per-model prompt variants when quality differs; test before switching traffic |
| A/B rollout | Route % of traffic to new model; gate on user feedback, task completion, error rates |

## Core Metrics

- Latency by model and feature
- Tokens in/out per request
- Cost per user, feature, and workflow
- Schema-validation failure rate
- Tool-call failure rate
- User feedback rate and correction rate

### Instrumentation standard: OTel GenAI semantic conventions

For teams wiring these metrics into an existing observability stack, represent LLM calls as spans using OpenTelemetry's GenAI semantic conventions (`gen_ai.*` attributes). The [GenAI conventions now live in their own repository](https://github.com/open-telemetry/semantic-conventions-genai); check its `docs/` and stability metadata before hard-coding attribute names in dashboards or alerts. See [qa-observability](../../qa-observability/SKILL.md) for general OTel setup.

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
