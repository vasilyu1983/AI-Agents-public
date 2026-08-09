# Company AI Operating Model Template

Use this template to produce a decision-complete operating model for AI in product.

## 1. Scope

- Company or product area:
- Current state: `greenfield | retrofit | fragmented`
- AI surface mix: `product AI | internal copilots | agents | mixed`
- Priority outcomes:
- Non-goals:

## 2. Org Model

- Default model: `central platform first | hybrid | federated`
- Central team owns:
- Product teams own:
- Security and privacy owners:
- Escalation path for high-risk launches:

## 3. Data Planes

### Operational Truth

- Systems of record:
- Tenant boundary:
- Live facts required at runtime:

### AI Context Layer

- Context sources:
- Memory policy:
- Retrieval sources:
- Provenance and freshness requirements:

### Analytics Layer

- Event taxonomy owner:
- Identity resolution model:
- Semantic metrics or marts:
- AI telemetry fields:

## 4. Model And Provider Posture

- Default posture: `external APIs first | managed private endpoints | mixed by risk tier`
- Provider allowlist:
- Provider abstraction or gateway:
- Fallback strategy:
- Self-hosting rule:

## 4a. Model Lifecycle And Multi-Model Ops

- Production model ID inventory: (list all hardcoded model IDs and their provider-published retirement dates)
- Deprecation monitoring: (how are provider retirement announcements tracked?)
- Migration runbook: (steps — identify affected features, select replacement, capability eval parity gate, regression evals, canary, comms, cutover, rollback plan)
- Eval-parity gate owner: (who signs off that the replacement clears the capability eval threshold?)
- Multi-provider routing policy: (which features route to which model/provider, and why)
- Fallback chain per risk tier: (secondary provider or degraded-response target, with trigger condition)
- Per-provider cost attribution: (how is spend tagged by provider and model ID in telemetry?)

## 5. Risk Tiers

| Tier | Data or action class | Allowed providers | Required controls |
| --- | --- | --- | --- |
| Tier 0 |  |  |  |
| Tier 1 |  |  |  |
| Tier 2 |  |  |  |

## 6. Shared Contracts

- `ModelRequest`
- `ModelResponse`
- `ContextBundle`
- `SafetyDecision`
- `ToolInvocation`
- `EvalRun`
- `AuditEvent`

For each contract, define:

- owner
- versioning rule
- required fields
- validation point

## 7. Delivery Workstreams

### Workstream 1: Foundation

- Provider abstraction
- Prompt/config versioning
- Telemetry baseline
- Risk-tier enforcement

### Workstream 2: Data And Context

- Context-layer contracts
- Tracking plan
- Semantic metrics
- Ownership and quality rules

### Workstream 3: Product Features

- Streaming UX
- Structured outputs
- Tool workflows
- Approval boundaries

### Workstream 4: Reliability And Governance

- Eval harness (split into capability evals and regression evals with distinct owners)
- Security pack
- Canary rollout
- Incident runbooks
- Model lifecycle runbook (deprecation tracking, migration gate, cutover comms)
- EU AI Act compliance classification and owner assignment

## 8. Release Gates

- Offline eval threshold:
- Capability eval owner and pass criteria:
- Regression eval owner and pass criteria:
- Security pack required:
- Canary required:
- Rollback threshold:
- Human approval requirement:
- EU AI Act compliance checkpoint: classify feature against high-risk categories (Annex III); if qualifying, name the compliance owner and applicable obligation date. Verify the exact date for your system at https://artificialintelligenceact.eu/implementation-timeline/ — the phase-in timeline is staged and classification-dependent. (Key verified dates as of 2026-05-17: GPAI obligations began 2025-08-02; main high-risk obligations begin 2026-08-02 for new systems.)

## 9. Risks And Open Questions

- Highest-risk assumptions:
- Known gaps:
- Deferred decisions:
