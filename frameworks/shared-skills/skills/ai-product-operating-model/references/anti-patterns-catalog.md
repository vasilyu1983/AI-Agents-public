# AI Product Operating Model — Anti-Patterns Catalog

**Purpose.** Numbered catalog of the durable May 2026 anti-patterns for AI product operating models, each with detection signals and the blocking pattern from `patterns-catalog.md`. Run this sweep against any operating model design before presenting recommendations.

## Table of Contents

- [Anti-Pattern Index](#anti-pattern-index)
- [A1 — Federated-before-contracts](#a1--federated-before-contracts)
- [A2 — Self-hosting-as-default](#a2--self-hosting-as-default)
- [A3 — Collapsed-data-planes](#a3--collapsed-data-planes)
- [A4 — Abstraction-that-leaks](#a4--abstraction-that-leaks)
- [A5 — Per-team-auth-sprawl](#a5--per-team-auth-sprawl)
- [A6 — Quality-only-metrics](#a6--quality-only-metrics)
- [A7 — Provider-first-tier-second](#a7--provider-first-tier-second)
- [A8 — Shipping-before-evals](#a8--shipping-before-evals)
- [A9 — Marketing-language-safety](#a9--marketing-language-safety)
- [A10 — Agent-as-default](#a10--agent-as-default)
- [A11 — Model-deprecation-surprise](#a11--model-deprecation-surprise)
- [A12 — Single-provider-dependency](#a12--single-provider-dependency)

## Anti-Pattern Index

| ID | Name | Detection signal | Blocked by |
|----|------|-----------------|------------|
| A1 | Federated-before-contracts | Each team has its own provider wrapper | P1, P6 |
| A2 | Self-hosting-as-default | Infrastructure plan assumes GPU cluster before value proof | P2 |
| A3 | Collapsed-data-planes | Single warehouse serves analytics, context, and operational truth | P3 |
| A4 | Abstraction-that-leaks | Product code contains provider-specific prompt templates or JSON schemas | P8 |
| A5 | Per-team-auth-sprawl | Multiple teams hold direct provider API keys with no central policy | P1 |
| A6 | Quality-only-metrics | Eval tracks output quality only; cost, latency, refusals invisible | P10 |
| A7 | Provider-first-tier-second | Provider selected before risk tier is defined | P5 |
| A8 | Shipping-before-evals | Feature reaches production without an eval suite | P7 |
| A9 | Marketing-language-safety | Provider data handling assessed from landing page, not DPA or primary docs | P9 |
| A10 | Agent-as-default | "Agent" is the default AI feature shape regardless of autonomy value | P4 |
| A11 | Model-deprecation-surprise | Provider retires a model ID and platform discovers it from a production error | P7, P11 |
| A12 | Single-provider-dependency | Platform has no fallback chain, routing policy, or eval parity for a second provider | P8, P12 |

---

## A1 — Federated-before-contracts

**Description**: product teams independently build their own provider wrappers, prompt libraries, and safety postures before shared contracts, eval standards, and policy boundaries exist.

**Detection signals**:
- Three or more teams have separate `llm_client.py` or equivalent files.
- No shared `ModelRequest` / `ContextBundle` / `AuditEvent` types.
- Model calls are not routed through a central gateway or policy layer.

**Resolution**: establish P1 (central platform) and P6 (shared contracts) before additional feature teams ship; backfill existing features to the shared contract shape.

---

## A2 — Self-hosting-as-default

**Description**: teams assume that self-hosting model weights is the mature, secure, or cost-effective default, planning GPU infrastructure before the value of the feature is proven.

**Detection signals**:
- Architecture diagrams show GPU cluster or on-prem model server before any production traffic exists.
- Self-hosting is chosen to avoid provider data-processing terms without verifying that the workload actually requires it.
- Infrastructure costs are planned before feature evals have shown positive signal.

**Resolution**: apply P2 (external-APIs-first); reserve self-hosting for proven features with explicit risk-tier, latency, or data-residency requirements that cannot be met via managed options.

---

## A3 — Collapsed-data-planes

**Description**: operational product truth, AI context (retrieved evidence, derived memory, session state), and analytics are stored in one warehouse, one vector DB, or one prompt log.

**Detection signals**:
- AI features query the analytics warehouse for live context.
- Memory or retrieval systems contain raw operational records (user accounts, billing state).
- Prompt logs are the primary source of both product metrics and AI context.

**Resolution**: apply P3 (three-data-planes); separate ownership, access controls, and SLAs for each plane.

---

## A4 — Abstraction-that-leaks

**Description**: a nominal provider-abstraction layer exists but provider-specific prompt templates, JSON schemas, tool semantics, or response-parsing logic leaks into product-feature code.

**Detection signals**:
- Product feature code imports from provider SDK directly (e.g., `from openai import ...`).
- Prompt templates contain provider-specific tags (e.g., `<|im_start|>`, `Human:` / `Assistant:`).
- Switching providers requires editing product feature files, not only the gateway.

**Resolution**: apply P8 (provider-abstraction-layer); the abstraction must translate provider-neutral contracts into provider-specific wire format at the boundary only.

---

## A5 — Per-team-auth-sprawl

**Description**: multiple product teams hold direct provider API keys and manage their own authentication, rate limits, and spend controls independently.

**Detection signals**:
- Provider dashboard shows multiple API keys with team-name suffixes and no central rotation policy.
- Rate-limit or overspend incidents are reported per-team rather than managed centrally.
- No central inventory of which teams are calling which providers.

**Resolution**: apply P1; centralize API key management, spend controls, and rate-limit policies through the platform team.

---

## A6 — Quality-only-metrics

**Description**: feature evaluation tracks output quality (accuracy, user ratings, task completion) but cost per call, latency percentiles, refusal rates, and fallback behavior are not instrumented.

**Detection signals**:
- Eval dashboard shows quality scores only.
- No per-feature cost-per-conversation or token-cost metric.
- Latency spikes and refusal rate increases are discovered through user complaints, not telemetry.

**Resolution**: apply P10; add cost, latency (p50/p95/p99), refusal rate, and fallback trigger rate to the standard feature instrumentation template.

---

## A7 — Provider-first-tier-second

**Description**: a model provider is selected (typically the most capable or most popular) before the risk tier of the data and actions involved is defined.

**Detection signals**:
- Provider is chosen based on benchmark rankings or brand preference.
- Data classification for the feature is done after provider integration begins.
- Sensitive data reaches a provider whose DPA has not been reviewed.

**Resolution**: apply P5 (risk-tier-before-provider); complete the risk-tier classification before shortlisting providers.

---

## A8 — Shipping-before-evals

**Description**: AI features go to production without an eval suite, telemetry, rollback plan, or staged rollout process.

**Detection signals**:
- No eval suite exists for the feature at launch.
- First quality signal comes from user complaints post-launch.
- No canary or feature-flag mechanism for the AI feature.

**Resolution**: apply P7 (rollout-gates); block production launch until the minimum gate requirements are met.

---

## A9 — Marketing-language-safety

**Description**: the safety and privacy posture of a model provider is assessed from the provider's marketing site, product page, or sales pitch rather than from the actual DPA, Terms of Service, retention settings, and request logging configuration.

**Detection signals**:
- Privacy review cites provider blog posts or feature pages rather than the DPA.
- "Zero data retention" or "no training on your data" claim is not verified against the specific API endpoint and account tier.
- Provider selection was made without reviewing the actual request path and log retention settings.

**Resolution**: apply P9; verify data handling against primary sources — DPA, API docs, account-tier documentation — before handling sensitive data.

---

## A10 — Agent-as-default

**Description**: "agent" is treated as the upgrade path for all AI features, regardless of whether autonomous multi-step execution adds measurable value over a bounded request/response or tool-workflow design.

**Detection signals**:
- Features described as "AI agent" that complete in one or two deterministic steps.
- Agents are deployed for tasks where the action space is fully known upfront and no planning is needed.
- Agent complexity is cited as a reason not to add evals or rollback paths.

**Resolution**: apply P4 (workflow-shape-classification); default to the simplest shape that works; add agent autonomy only when the planning value is explicit and measurable.

---

## A11 — Model-deprecation-surprise

**Description**: a provider retires or sunsets a model ID and the platform team discovers this from a production 4xx error, a degraded response, or a provider announcement with a short runway — rather than from a managed migration process with a defined runbook.

**Detection signals**:
- Model IDs are hardcoded in production config with no tracking of provider-published retirement dates.
- No process exists to monitor provider deprecation announcements for models in use.
- Migration planning starts after a deprecation notice, not before.
- There is no eval-parity gate — migrations are completed when "it seems to work," not when the replacement clears the capability eval threshold on task-specific suites.

**Resolution**: apply P11 (model-lifecycle-governance); treat every production model ID as an asset with a known deprecation risk; track provider retirement schedules; execute migrations through a runbook with capability eval parity and regression eval gates before cutover.

---

## A12 — Single-provider-dependency

**Description**: the platform routes all production AI traffic to a single provider with no fallback chain, no routing policy for alternatives, and no eval-parity baseline for a second provider — making any provider outage, pricing change, or capability gap a platform-wide incident.

**Detection signals**:
- All production features point to one provider; no fallback target is defined.
- Provider outage results in full feature degradation with no graceful fallback.
- Adding a second provider requires changes in feature code, not only in the gateway.
- No cost attribution exists by provider — total spend is not decomposable if routing changes.

**Resolution**: apply P8 (provider-abstraction-layer) and P12 (multi-model-ops); define at least one fallback provider per feature at risk tier 1+; establish routing policy and eval-parity baseline before routing any feature to a secondary provider in production.
