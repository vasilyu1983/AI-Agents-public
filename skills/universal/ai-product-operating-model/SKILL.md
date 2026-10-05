---
name: ai-product-operating-model
description: "Designs operating models for AI in product teams. Use when planning platform ownership, provider strategy, data boundaries, evals, or sensitive-data controls."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# AI Product Operating Model

Design a company-wide operating model for AI in product when the question is bigger than one prompt, one feature, or one model choice.

This skill is for organizations that need to align:

- product AI feature design
- agent and tool-using workflow posture
- data boundaries across product, context, and analytics
- provider and deployment posture
- public-cloud handling of PI or sensitive data
- evaluation, rollout, and governance

Default posture:

- external model APIs first
- central platform ownership before federated sprawl
- explicit data-plane separation
- provider abstraction instead of hard vendor lock-in
- risk-tiered controls for sensitive data
- evals, telemetry, and rollback before broad rollout
- model-lifecycle governance: provider model deprecations treated as planned product events, not surprises
- multi-model ops: running more than one frontier provider in production as a standing operating concern

## When to Use This Skill

Use this skill when the user asks for:

- an AI in product operating model
- a company AI platform strategy
- an LLM or agent governance model
- how product teams should work with central AI/data/platform teams
- how to handle PI or sensitive data with public-cloud model providers
- how to split analytics, runtime context, and operational truth
- how to sequence workstreams for AI platform foundations

## Use Other Skills for Depth

- Architecture and provider choice (API vs self-host, model class, build ladder) -> [../ai-architecture-advisor/SKILL.md](../ai-architecture-advisor/SKILL.md)
- Eval design, graders, and eval sets -> [../ai-evals/SKILL.md](../ai-evals/SKILL.md)
- Model adaptation (fine-tuning, distillation) -> [../ai-llm/SKILL.md](../ai-llm/SKILL.md)
- Agent architecture, MCP vs A2A, approval patterns -> [../ai-agents/SKILL.md](../ai-agents/SKILL.md)
- Product integration, streaming UX, structured outputs -> [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md)
- App context layer, memory, retrieval, grounding -> [../ai-context-layer/SKILL.md](../ai-context-layer/SKILL.md)
- Analytics semantics, marts, metric governance -> [../data-analytics-engineering/SKILL.md](../data-analytics-engineering/SKILL.md)
- Product instrumentation and AI/agent telemetry -> `marketing-product-analytics`
- Production controls, privacy, incidents, auditability -> [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md)
- AppSec and application-layer security boundaries -> [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md)
- Platform infra, workload identity, CI/CD, policy-as-code -> [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)
- Agent eval harnesses and regression gates -> [../qa-agent-testing/SKILL.md](../qa-agent-testing/SKILL.md)

## Quick Reference

| Need | Default move | Where to go next |
| --- | --- | --- |
| Company wants "AI in product" direction | Start with central platform ownership + external APIs first | `assets/company-ai-operating-model-template.md` |
| Teams mix product AI, internal copilots, and agents | Split surfaces by workflow shape and risk tier | [references/data-boundaries-and-risk-tiers.md](references/data-boundaries-and-risk-tiers.md) |
| Data is used for both analytics and runtime AI | Separate operational truth, AI context, and analytics planes | [../ai-context-layer/SKILL.md](../ai-context-layer/SKILL.md), [../data-analytics-engineering/SKILL.md](../data-analytics-engineering/SKILL.md) |
| PI or sensitive data must go through public cloud | Apply minimization, redaction, tenant isolation, audit, and provider allowlists | [references/data-boundaries-and-risk-tiers.md](references/data-boundaries-and-risk-tiers.md) |
| Teams want agents everywhere | Default to non-agentic product flows until agent value is explicit | [../ai-agents/SKILL.md](../ai-agents/SKILL.md) |
| Platform needs rollout control | Standardize evals, telemetry, canaries, and rollback before scale | [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md), [../qa-agent-testing/SKILL.md](../qa-agent-testing/SKILL.md) |
| Provider announces model deprecation | Treat as planned product event: migration runbook, eval-parity gate, cutover comms | Section 6 — Model-Lifecycle Governance |
| Running multiple frontier providers in production | Define routing policy, fallback chain, eval parity, and per-provider cost attribution at platform level | Section 7 — Multi-Model Ops |
| EU AI Act applicability check | Screen for Art 5 prohibited practices and Art 50 transparency duties; classify against high-risk categories; assign compliance owner and look up the phase-in date | Section 8 — EU AI Act Compliance Checkpoint |
| Leadership wants to report "AI adoption" | Separate usage/activation metrics from downstream cycle-time, cost, or quality outcomes with a pre-AI baseline | Section 9 — Adoption Signal vs Adoption Theater |
| Usage or approval-rate metrics look strong but value is unclear | Check for survivorship bias, automation bias, and Goodhart risk before trusting the number | Section 10 — Measurement Pitfalls Beyond the Eval Suite |

## Default Workflow

1. Classify the company scope: product AI only, internal copilots only, or mixed platform.
2. Classify the current posture: greenfield, retrofit, or fragmented existing systems.
3. Choose the org model: central platform first, hybrid, or federated.
4. Separate the data planes:
   - operational product truth
   - AI context layer
   - analytics and semantic metrics
5. Choose the model posture:
   - external APIs first
   - managed private endpoints
   - mixed by risk tier
6. Define shared platform contracts:
   - `ModelRequest`
   - `ModelResponse`
   - `ContextBundle`
   - `SafetyDecision`
   - `ToolInvocation`
   - `EvalRun`
   - `AuditEvent`
7. Define risk tiers and minimum controls for each tier before feature work spreads.
8. Define rollout gates: split eval function into two distinct roles — **capability evals** (does the new model/prompt meet the quality bar?) owned by the platform/ML team on a per-change cadence, and **regression evals** (did we break anything already shipped?) owned by each feature team on every deployment. Different owners, different cadence, different suite.
9. Define model-lifecycle governance: deprecation runbook, eval-parity gate, cutover comms, and rollback plan before the first provider model ID is hardcoded in production config.
10. Assess EU AI Act applicability: check Art 5 prohibitions and Art 50 transparency duties as well as high-risk categories; assign a compliance owner and look up the applicable date in the [Commission's enforcement timeline](https://digital-strategy.ec.europa.eu/en/policies/enforcement-ai-act).
11. Name the downstream metric each "AI adoption" initiative is meant to move (cycle time, cost per unit, defect rate, conversion) and its pre-AI baseline before rollout — not after. No named metric means the work is an experiment, not a rollout.
12. Sequence workstreams: foundation -> data/context -> product AI features -> governance and reliability.

## Canonical Operating Model

### 1. Central Platform Before Federated Sprawl

- A central AI platform function owns provider policy, model routing, prompt/config versioning, eval standards, telemetry, and approval patterns.
- Product teams own feature UX, business workflows, instrumentation, and outcome metrics.
- High-impact decisions stay centralized: provider allowlist, risk-tier policy, shared contracts, audit posture, and incident escalation.
- **Org-design evidence grade (hedged):** The enabling-team / platform-team pattern (Skelton & Pais, Team Topologies) is widely cited but evidence of superior outcomes specifically in AI platform contexts is limited and contested; do not cite a formal evidence grade for it. Treat it as a useful default heuristic, not a settled best practice. Adjust ownership structures to your actual org scale and delivery rhythm.

### 2. External APIs First

- Do not make self-hosting the default planning assumption.
- Optimize first for provider abstraction, policy control, data handling, and rollback.
- Reserve stronger isolation paths for higher-risk tiers instead of forcing every workflow into one expensive posture.

### 3. Three Explicit Data Planes

- **Operational truth**: users, orgs, billing, permissions, product state, and other live business facts.
- **AI context layer**: retrieved evidence, derived memory, reusable context bundles, and task-scoped grounding.
- **Analytics layer**: event taxonomy, identity resolution, semantic metrics, marts, and BI or NLQ consumption.

Do not collapse all three into one warehouse, one vector DB, or one prompt log.

### 4. Workflow Shape Before Tooling

Classify every AI surface as one of:

- `LLM feature`: request/response or streaming generation inside product UX
- `Tool workflow`: bounded tool use with explicit control flow
- `Agent system`: longer-running or ambiguous work where autonomy has measurable value

Default to the simplest shape that can work.

### 5. Risk Tiers Before Provider Selection

Use the tier model in [references/data-boundaries-and-risk-tiers.md](references/data-boundaries-and-risk-tiers.md) before choosing model providers or deployment posture. Provider choice follows data and action sensitivity, not the other way around.

### 6. Model-Lifecycle Governance

Frontier model deprecations are a planned product event, not an infrastructure surprise. The platform team owns the deprecation runway, not individual feature teams.

- **Deprecation triggers**: provider sunset announcement, capability regression on your eval suite, or model ID retiring in provider docs.
- **Migration runbook**: (1) identify all features calling the deprecating model ID, (2) select the candidate replacement, (3) run capability evals against your production eval suite on the replacement, (4) run regression evals to confirm no shipped behavior breaks, (5) canary-roll the replacement behind a feature flag, (6) execute comms to dependent teams with the cutover date.
- **Eval-parity gate**: block cutover until the replacement clears your capability eval threshold and your regression eval suite. "Roughly equivalent on public benchmarks" is not a gate — your task-specific evals are.
- **Comms**: treat a model migration as a minor product release — changelog entry, dependent-team notification, rollback plan documented before cutover starts.
- **Current model IDs** are volatile: verify active IDs and deprecation notices on the provider's models page before setting platform config.

### 7. Multi-Model Ops

Running more than one frontier provider or model in production is now a standing operating concern, not an edge case. Address it explicitly in the platform design.

- **Routing policy**: define at the platform level — which features route to which model, and why (cost, capability, latency, data-residency, risk tier). Do not let routing decisions leak into feature code.
- **Fallback chain**: every Tier-1 and Tier-2 feature must have an explicit fallback (a secondary provider or a graceful degraded response). Define the trigger condition (error rate, latency threshold, provider outage signal) and the fallback target before first production traffic.
- **Eval parity across providers**: before routing a feature to a secondary provider, establish that it meets your capability eval threshold on your task-specific suite — not just on public benchmarks.
- **Cost attribution by provider and model**: per-feature cost telemetry must be tagged by provider and model ID so spend is visible and routing decisions are accountable.
- **Provider contract hygiene**: verify data-residency and handling terms for every allowed provider. Where personal data is processed, review GDPR controller/processor roles and the applicable DPA separately from AI Act provider/deployer roles; recheck terms when they change.
- **A2A protocol (agent-to-agent delegation)**: MCP defines tool/context boundaries; A2A (Agent2Agent) defines agent-to-agent task handoff. Spec: https://a2a-protocol.org/latest/specification/. Check its current version, governance, and adoption footprint before committing to it as a routing backbone. Full pattern detail and MCP-vs-A2A design guidance -> [../ai-agents/SKILL.md](../ai-agents/SKILL.md).

### 8. EU AI Act Compliance Checkpoint

Dates live in the canonical owner, ../startup-compliance-enterprise-readiness/references/regulatory-overlays.md; this skill keeps only the checkpoint rules. Check the [Commission's enforcement timeline](https://digital-strategy.ec.europa.eu/en/policies/enforcement-ai-act) for each feature before committing to a roadmap.

The EU AI Act phases in by obligation type, not by product. Place each feature in every bucket it touches:

- **Art 5 prohibited practices**: a block, not a risk tier. Stop the work until legal review confirms the use case is outside the applicable prohibitions. The [2026 amendment](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32026R1744) covering non-consensual intimate material and child sexual abuse material has a later application date; until then, flag it for legal review without calling it an already-applicable Art 5 prohibition.
- **Art 50 transparency**: assess at any risk tier. Providers have interaction-disclosure and synthetic-output marking duties; deployers have duties for exposed people, deepfakes and certain public-interest text. Check each paragraph's scope and exceptions before specifying a disclosure or marking control.
- **High-risk, Annex III use cases** (biometrics, critical infrastructure, education/exam scoring, employment/recruitment, essential services incl. credit and benefits, law enforcement, migration/border, justice/democratic processes) and **Annex I** (AI embedded in regulated products) have different start dates.
- **GPAI model obligations** have their own dates. Classify your provider/deployer role, system use, and GPAI dependencies per feature before assigning any obligation.
- The first market-placement date can change the deadline (grace periods for systems already on the market), so record it per feature.
- Art 4 still requires providers and deployers to take measures supporting staff AI literacy; the amended text does not mandate a specific level for each person. Check the [Commission's AI literacy guidance](https://digital-strategy.ec.europa.eu/en/policies/ai-talent-skills-and-literacy) before turning that duty into a control.

Operating-model checkpoints to add to your planning cadence:

- Classify each AI feature against Annex III and the other applicable buckets. `scripts/risk_tier_classifier.py` is a triage aid: it maps recognized use-case terms to Tier 2, blocks a possible applicable Art 5 practice (exit 3), flags the later-applying amendment for review before its effective date (exit 2), and lists Art 50 signals separately. Unrecognized input exits 2 with `needs_review`, never a silent Tier 0.
- If any feature qualifies as GPAI or high-risk, assign a named compliance owner and include the applicable obligation date in the roadmap.
- Do not treat EU AI Act compliance as a one-time gate: design changes, new data classes, and new action types can change the classification.
- Verify exact dates and provider/deployer role classification against the canonical source above before finalizing a roadmap.

### 9. Adoption Signal vs Adoption Theater

Executive pressure to "show AI adoption" creates a predictable failure mode: usage metrics rise while delivered value stays flat. Distinguish the two before reporting either to leadership.

- **Adoption theater markers**: seat counts or license activations reported as the primary success metric; mandatory-use policies for AI tools with no measurement of what changed downstream; hackathon or pilot output celebrated without a path to production; a rising "% of engineers with AI assistant access" metric substituting for a rising output or quality metric.
- **Real-leverage markers**: cycle-time or lead-time change on shipped work, defect-escape rate, support-deflection rate, or revenue/cost outcomes tied to specific AI-enabled workflows — each with a pre-AI baseline and a comparable post-AI measurement window.
- **The self-report trap**: developer or agent self-reported "time saved" and satisfaction surveys are a weak proxy for delivered value and are prone to social-desirability bias; they are a useful leading indicator, never the headline metric in a board or leadership update.
- **Short-window bias**: early satisfaction can differ from durable use. Measure a later cohort before reporting sustained adoption.
- **Operating-model implication**: require every "AI adoption" initiative to name the downstream business metric it is meant to move (cycle time, cost per ticket, conversion, defect rate) and the baseline before rollout — not after. If no such metric exists, treat the initiative as an experiment, not a rollout, and gate spend accordingly.

### 10. Measurement Pitfalls Beyond the Eval Suite

Passing the eval suite is necessary but not sufficient evidence that an AI feature or platform investment is working. Watch for these measurement failure modes specifically:

- **Survivorship bias in usage data**: usage or satisfaction telemetry from users who kept using the feature says nothing about the (often larger) group who tried it once and silently reverted to the old workflow. Instrument abandonment and reversion, not only active usage.
- **Local optimization, global regression**: a team-level win (faster ticket resolution, higher self-reported productivity) that offloads verification, review, or rework cost onto another team or onto production incident rates is not a net win — attribute cost as well as benefit across the full workflow, not just the AI-touched step.
- **Automation bias in human-in-the-loop metrics**: "human approval rate" on AI-generated output is not a quality metric once approvers learn to trust the tool and stop reading carefully — pair it with periodic blind spot-checks (compare a sample of approved output against an independent quality rubric) rather than trusting the approval rate alone.
- **Goodhart risk on any single north-star metric**: once "AI-assisted PR count" or "agent task completion rate" becomes a target tied to performance review or team funding, it will be gamed (trivial PRs, loosely-scoped "completed" tasks). Pair every adoption or throughput metric with a paired quality or outcome metric before it becomes a target.

## Required Shared Contracts

Every company-wide AI platform should standardize these contracts before scale:

- `ModelRequest`: caller, task type, risk tier, input schema, allowed providers/models
- `ModelResponse`: output payload, schema validation result, citations or evidence refs where relevant
- `ContextBundle`: live facts, memory, retrieved evidence, tenant scope, freshness, provenance
- `SafetyDecision`: allowed, redacted, blocked, or escalate-to-human with reason
- `ToolInvocation`: principal, requested tool, approved scope, result, side-effect status
- `EvalRun`: eval type (`capability` | `regression`), suite version, judged dimensions, score, status, regression notes, owner team
- `AuditEvent`: trace ID, actor, feature, provider, data class, approval event, retention class

Without these contracts, teams will re-implement incompatible local wrappers and the platform becomes impossible to govern.

## Minimum Platform Controls

- Model/provider calls go through an abstraction or gateway layer with traceable policy decisions.
- Sensitive fields are minimized or redacted before model submission.
- Logs and traces mask raw PI by default.
- Retrieval and tools enforce tenant isolation and action scoping.
- Mutating tools require stronger approval than read-only tools.
- Every production feature has cost, latency, refusal, and fallback telemetry.
- High-risk launches require offline evals and staged rollout.

## Stage Promotion Contract

Classify each use case as `prototype`, `pilot`, or `production`, and name the decision owner. Promotion must attach evidence for user outcome, data authority and retention, eval coverage, failure handling, unit economics, operational ownership, and rollback; risk-tier controls are blocking conditions rather than weighted score inputs. If any required owner or artifact is absent, keep the use case in its current stage and state the missing decision. Count adoption only when the intended user completes the target task under the governed path.

## Known Traps

- Central platform ownership that becomes a product-team ticket queue instead of a standards, contracts, and guardrails layer.
- "One AI gateway for everything" designs that erase risk-tier differences between low-risk summarization, tool-using workflows, and high-sensitivity agent actions.
- Reusing the analytics warehouse as the live context plane for product features with no freshness, tenancy, or provenance controls.
- Declaring sensitive-data safety based on provider marketing language instead of verifying the actual request path, logging path, and retention settings.
- Shipping tool-using or agentic experiences before evals, telemetry, rollback, and human-escalation paths exist.
- Building a nominal provider-abstraction layer that still leaks provider-specific prompts, JSON schemas, and tool semantics into every product surface.
- Treating a provider's model deprecation as an infrastructure surprise rather than a planned product event with a migration runbook.
- Conflating capability evals (is this new model good enough?) with regression evals (did we break what ships?): they have different owners, different suites, and different cadences — collapsing them into one "eval run" hides both regressions and capability gaps.
- Running multiple frontier providers in production without explicit routing policy, eval-parity gates across providers, and per-provider cost attribution.
- Reporting seat counts, license activations, or week-one satisfaction as "AI adoption" success without a downstream cycle-time, quality, or cost metric and a pre-AI baseline.
- Treating "human approved it" as a durable quality signal once approvers have habituated to trusting the tool's output.

## Output Shape

When this skill is the primary skill, the default deliverable should include:

- target org model
- target data-plane architecture
- provider and risk-tier posture
- shared platform contracts
- rollout workstreams
- acceptance gates and residual risks

Use [assets/company-ai-operating-model-template.md](assets/company-ai-operating-model-template.md) as the starting scaffold.

## Navigation

### References

- [references/patterns-catalog.md](references/patterns-catalog.md) — P1–P12 named patterns
- [references/anti-patterns-catalog.md](references/anti-patterns-catalog.md) — A1–A12 with detection signals
- [references/data-boundaries-and-risk-tiers.md](references/data-boundaries-and-risk-tiers.md) — Risk tier model and data-plane boundaries

### Assets

- [assets/company-ai-operating-model-template.md](assets/company-ai-operating-model-template.md) — Operating model scaffold

### Scripts

- `python3 scripts/contract_validator.py --input contract.json` — Validates typed shared-contract JSON against required field schemas
- `python3 scripts/risk_tier_classifier.py --input feature-spec.json` — Reads a feature spec and emits Tier 0/1/2 classification with minimum controls, an Art 5 block flag, and Art 50 transparency duties

Related skills:

- [../ai-llm/SKILL.md](../ai-llm/SKILL.md)
- [../ai-agents/SKILL.md](../ai-agents/SKILL.md)
- [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md)
- [../ai-context-layer/SKILL.md](../ai-context-layer/SKILL.md)
- `marketing-product-analytics`
- [../data-analytics-engineering/SKILL.md](../data-analytics-engineering/SKILL.md)
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md)
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md)
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)
- [../qa-agent-testing/SKILL.md](../qa-agent-testing/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
