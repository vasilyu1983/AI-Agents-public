---
name: ai-mlops
description: Operates production MLOps for ML, LLM, and agent systems. Use when designing deployment, monitoring, retraining, incident response, or GenAI security workflows.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# MLOps & LLMOps - Production Operations Hub

**July 2026 posture:** version every changeable artifact, gate every release with a regression-eval suite in CI, instrument the whole path with OpenTelemetry (pin GenAI convention version — the spec now lives in its own repo and is still evolving), treat tool/RAG context as untrusted input, and ship rollback plus incident playbooks before launch.

This skill is the execution hub for **operating AI systems in production**:

- **Classical ML ops**: ingestion, registries, feature stores, drift, retraining, promotion
- **LLMOps**: serving, prompt/config lifecycle, online evals, cost controls, safety gates
- **Agent runtime ops**: tracing, tool governance, approval paths, MCP-aware telemetry, rollback
- **Governance**: privacy, supply chain, auditability, AI Act readiness, safety incident handling

Use this skill for **production architecture, release gates, monitoring, incidents, and governance**. Use adjacent skills for modelling, retrieval depth, agent design, or inference internals.

## When To Use This Skill

Activate this skill when the user asks for:

- Deploying an ML, LLM, RAG, or agent-backed system to production
- Designing serving, batch, hybrid, or multi-region runtime architecture
- Adding observability, drift detection, alerting, retraining, or release gates
- Writing incident runbooks, rollback plans, or go/no-go checklists
- Hardening an AI system against prompt injection, RAG poisoning, tool abuse, or data leakage
- Building governance artifacts for privacy, auditability, or regulated rollout
- Choosing how to operate prompts, model artifacts, feature definitions, or agent graphs safely

## Scope Boundaries

- **EDA, feature engineering, training, SQL transformation** -> [ai-ml-data-science](../ai-ml-data-science/SKILL.md)
- **Prompt strategy, tuning, eval design, fine-tuning ROI** -> [ai-llm](../ai-llm/SKILL.md)
- **Retrieval architecture, chunking, reranking, search quality** -> [ai-rag](../ai-rag/SKILL.md)
- **Latency, batching, quantization, GPU serving internals** -> [ai-llm-inference](../ai-llm-inference/SKILL.md)
- **Deep agent architecture, MCP server design, handoffs, memory** -> [ai-agents](../ai-agents/SKILL.md)

Keep this skill focused on **operating** production systems after the architecture exists or while defining production controls for it.

## ASCII Flow

```text
AI system ready for operation
  |
  v
release artifact
  model/prompt/retrieval/tool versions + owner + eval report + rollback target
  |
  v
production controls
  CI/CD + registry + telemetry + policy gates + security review
  |
  v
rollout
  shadow -> canary -> gradual promotion -> rollback on SLO/eval breach
  |
  v
operate
  monitor drift/cost/latency/safety + incident response + retrain/retire loop
```

## Quick Reference

| Task | Default Tooling / Pattern | When to Use |
|------|---------------------------|-------------|
| Data ingestion | dlt + contracts + lineage | APIs, CDC, warehouse loading, incremental syncs |
| Batch scoring | Airflow, Dagster, Prefect | High-volume scoring, backfills, delayed labels |
| Real-time serving | FastAPI, gRPC, KServe, BentoML | Low-latency APIs with explicit SLOs |
| LLM serving | vLLM, TGI, BentoML | High-throughput text generation endpoints |
| Registry / promotion | MLflow 3 (alias-based: champion/challenger), W&B, ZenML | Versioning, approvals, rollbacks, lineage |
| Feature consistency | Feast / managed feature stores | Batch + online parity and point-in-time correctness |
| Observability | OpenTelemetry + Prometheus/Grafana | Traces, metrics, alerts, cost and latency budgets |
| OTel GenAI conventions | Pin the semconv version — spec moved to its own repo, still evolving as of July 2026 | Expect churn; verify at github.com/open-telemetry/semantic-conventions-genai (opentelemetry.io/docs/specs/semconv/gen-ai/ is now a stub redirect) |
| Drift / retraining | Statistical monitors + gated CT | Detect shifts and trigger controlled retraining |
| Training job orchestration | Ray, Slurm, cloud training queues (SageMaker Jobs, Vertex) | Queue/schedule fine-tune + eval jobs; avoid runaway GPU spend |
| Cost chargeback / showback | Resource tagging + cost dashboards per team or per model | Allocate LLM API + GPU + storage costs to business units |
| Eval-as-CI-gate | Regression-eval suite blocking model/prompt deploy in CI | LLM-as-judge: calibrate against human-labeled gold set (judges drift) |
| Agent runtime ops | Trace spans + tool approvals + audit logs | Tool-using agents, MCP tools, approval flows |
| Security / governance | Threat model + policy checklists + runbooks | GenAI hardening, privacy, AI Act, incident prep |

## Default Workflow

1. Pick the runtime pattern with the decision tree below.
2. Define release artifacts: model/prompt version, owner, rollback target, eval report, runbook.
3. Instrument first: traces, request IDs, model/prompt/tool versions, latency/cost budgets.
4. Add policy gates: security review, privacy controls, AI risk notes, approval path.
5. Roll out gradually: shadow -> canary -> promoted traffic, with automatic rollback criteria.
6. Close the loop: alerts, incident runbook, feedback collection, retraining or retirement triggers.

## Decision Tree: Choose The Operating Pattern

```text
Need to operate an AI system in production:
    ├─ Primary workload is data movement?
    │   ├─ APIs / SaaS syncs -> dlt ingestion + contracts + freshness alerts
    │   ├─ Database replication -> CDC / incremental sync + lineage + replay plan
    │   └─ Streaming events -> queue/stream path + backpressure + schema control
    │
    ├─ Primary workload is inference?
    │   ├─ Scheduled / offline -> batch scoring pipeline
    │   ├─ <500 ms API -> online service with SLOs, timeouts, rollback target
    │   └─ Mix of both -> hybrid deployment + shared registry + feature parity
    │
    ├─ System includes LLM or RAG?
    │   ├─ Yes -> prompt/config versioning + token/cost budgets + safety gates
    │   └─ RAG -> retrieval ACLs + poisoning defenses + answerability / citation checks
    │
    ├─ System includes tool-using agents?
    │   ├─ Yes -> approval gates + least-privilege tools + trace tool calls
    │   └─ MCP tools -> auth + audit + semantic telemetry for MCP sessions and tools
    │
    └─ Need regulated or multi-region rollout?
        ├─ Yes -> residency, tenant isolation, audit evidence, rollback by region
        └─ No -> single-region rollout with standard incident and rollback controls
```

## May 2026 Operating Rules

- **OpenTelemetry first**: standardize traces and metrics for requests, prompts, models, tools, and MCP interactions. Prefer OTel GenAI semantic conventions and, where relevant, MCP semantic conventions. **Caveat:** as of mid-2026, `gen_ai.*` attributes, metrics, events, and spans (including MCP-specific conventions) moved out of the core `open-telemetry/semantic-conventions` repo into a dedicated `open-telemetry/semantic-conventions-genai` repo, which as of July 2026 has no tagged releases and no published docs site — treat it as pre-release and pin an exact commit/schema version, not a package tag. The old opentelemetry.io/docs/specs/semconv/gen-ai/ page is now only a "moved" stub. Verify current convention state at https://github.com/open-telemetry/semantic-conventions-genai before shipping.
- **Eval-as-CI-gate (canonical pattern)**: every model, prompt, feature, retrieval, or agent-graph change must pass a regression-eval suite before deployment. Gate CI on this suite. When using LLM-as-judge scoring, calibrate the judge against a human-labeled gold set — judge scores drift as model versions change and must be periodically re-calibrated. This skill is the canonical owner of this pattern; cross-links from other skills are fine.
- **Treat retrieved content and tools as untrusted**: RAG context, tool outputs, external APIs, and MCP servers all need containment, validation, and audit logs.
- **Version the full runtime**: model artifact, feature definitions, prompt/config, safety policies, tool schemas, and agent graphs.
- **MLflow 3 alias-based registry**: prefer model aliases (e.g., `@champion`, `@challenger`) over lifecycle stages for promotion governance. Stages are soft-deprecated in MLflow 3 in favor of aliases. Verify current MLflow docs at https://mlflow.org/docs/latest/ before advising.
- **vLLM V1 engine only**: V1 has been the default since v0.8.0 and, per the project's deprecation plan, V0 code was slated for removal starting v0.10 — by mid-2026 V0 is gone, not just deprecated. If a codebase still references V0 flags (`VLLM_USE_V1=0`, legacy `LLMEngine` args), treat it as unmaintained and migrate. Reference: https://docs.vllm.ai/en/stable/usage/v1_guide/
- **Document regulatory timing explicitly**: as of March 13, 2026, general AI Act obligations apply from **August 2, 2026**, while general-purpose AI model obligations already started on **August 2, 2025**. Verify exact applicability for the user’s system before final advice.
- **EU AI Act deadline extension — formally adopted**: negotiators reached political agreement on May 7, 2026 to extend high-risk compliance deadlines; the European Parliament formally endorsed the package on June 16, 2026 and the Council gave final green light on June 29, 2026, per a legal briefing updated June 30, 2026. It takes legal effect three days after Official Journal publication (pending at time of writing). High-risk systems under Annex III (biometrics, critical infrastructure, employment, credit, public sector functions) that are new or substantially modified get a 16-month extension to December 2, 2027; AI safety components in regulated products (Annex I) get a 12-month extension to August 2, 2028. General transparency obligations for interactive AI and the general-purpose-AI-model rules are unaffected and still apply from August 2, 2026 / August 2, 2025 respectively. **Always verify current Official Journal publication status** at https://artificialintelligenceact.eu/implementation-timeline/ before committing any compliance roadmap — treat "adopted by Parliament and Council" as distinct from "in force," since the latter depends on publication date. Source: DLA Piper GENIE briefing, updated June 30, 2026 (https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act).

## Known Traps

- Shipping a model, prompt, or agent change before instrumentation is in place to tell you what broke.
- Versioning only the model artifact while prompt config, tool schema, safety policy, or retrieval contract changes out-of-band.
- Treating safety incidents as ordinary runtime failures with no dedicated escalation path, evidence capture, or owner.
- Building retraining triggers with no gated promotion step, rollback target, or shadow evaluation.
- Assuming one global runbook covers ML, RAG, and agent failures equally well when the blast radius and evidence requirements differ.

## Common Anti-Patterns

- Folding LLMOps or AgentOps into generic DevOps dashboards and losing the model, prompt, tool, or retrieval dimensions needed for triage.
- Running canaries without explicit acceptance criteria for cost, latency, quality, and safety.
- Treating untrusted retrieved content or tool output as trusted internal state once it crosses one service boundary.
- Waiting to define governance evidence until a regulated customer or auditor asks for it.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/drift_check.py` | Compute PSI and KL divergence between baseline and current distributions from JSON inputs. Threshold-based exit code for CI integration. |
| `scripts/deployment_smoke_test.sh` | Shadow/canary deployment smoke verifier — health check, models-list, inference latency, and finish_reason assertions against an OpenAI-compatible endpoint. |

## Navigation

### Release & Architecture

- **[Data Ingestion Patterns](references/data-ingestion-patterns.md)** - Use for contracts, CDC, incremental loading, lineage, replay, and schema evolution.
- **[Deployment Patterns](references/deployment-patterns.md)** - Use to choose batch, online, hybrid, or streaming deployment modes.
- **[Deployment Lifecycle](references/deployment-lifecycle.md)** - Use for promotion, rollout, rollback, and decommissioning workflow.
- **[Model Registry Patterns](references/model-registry-patterns.md)** - Use for metadata, artifact packaging, and promotion governance.
- **[Feature Store Patterns](references/feature-store-patterns.md)** - Use for batch/online parity, latency budgets, and point-in-time correctness.
- **[Multi-Region Patterns](references/multi-region-patterns.md)** - Use for residency, failover, disaster recovery, and regional rollback.

### Observability, Evals & Cost

- **[Monitoring Best Practices](references/monitoring-best-practices.md)** - Use for SLOs, alert routing, dashboards, and production metric coverage. Includes OTel GenAI maturity caveat.
- **[Drift Detection Guide](references/drift-detection-guide.md)** - Use for feature, label, concept, and embedding drift response.
- **[Automated Retraining Patterns](references/automated-retraining-patterns.md)** - Use for trigger selection, validation gates, safe retraining rollout, and training job queue/scheduler guidance.
- **[Online Evaluation Patterns](references/online-evaluation-patterns.md)** - Use for shadowing, canaries, A/B tests, HITL loops, promotion criteria, and **eval-as-CI-gate pattern** (canonical location).
- **[Experiment Tracking Patterns](references/experiment-tracking-patterns.md)** - Use for run naming, artifact retention, registry handoff, and auditability.
- **[Cost Management & FinOps](references/cost-management-finops.md)** - Use for GPU/token budgets, chargeback/showback per team or model, and spend guardrails.
- **[Incident Response Playbooks](references/incident-response-playbooks.md)** - Use for first-response steps, triage flow, and postmortem coverage.
- **[AgentOps Patterns](references/agentops-patterns.md)** - Use for agent traces, replay, tool-call telemetry, and runtime debugging.

### Security & Governance

- **[Threat Models](references/threat-models.md)** - Use first for trust boundaries and control mapping.
- **[Agentic Security](references/agentic-security.md)** - Use for tool governance, approval paths, state isolation, and human oversight.
- **[Prompt Injection Mitigation](references/prompt-injection-mitigation.md)** - Use for input hardening and instruction separation.
- **[RAG Security](references/rag-security.md)** - Use for retrieval poisoning, access control, and context sanitization.
- **[Model Extraction Defense](references/extraction-defense.md)** - Use for query-abuse detection, rate shaping, and capability theft defenses.
- **[Jailbreak Defense](references/jailbreak-defense.md)** - Use for refusal hardening and bypass pattern coverage.
- **[Output Filtering](references/output-filtering.md)** - Use for layered post-generation filtering and rewrite/block strategy.
- **[Privacy Protection](references/privacy-protection.md)** - Use for PII handling, retention, redaction, and minimization.
- **[Supply Chain Security](references/supply-chain-security.md)** - Use for SBOMs, artifact signing, dependency policy, and provenance.
- **[Safety Evaluation](references/safety-evaluation.md)** - Use for red-team suites, leakage tests, and refusal evaluation.
- **[Governance Checklists](references/governance-checklists.md)** - Use for model cards, policy evidence, audit artifacts, and compliance handoff.

### API & Runtime Interfaces

- **[API Design Patterns](references/api-design-patterns.md)** - Use for inference contracts, JSON/gRPC interfaces, and reliability controls.
- **[LLM & RAG Production Patterns](references/llm-rag-production-patterns.md)** - Use for prompt/config lifecycle, caching, fallback strategy, and runtime monitoring.
- **[Edge MLOps Patterns](references/edge-mlops-patterns.md)** - Use for TinyML, OTA rollouts, device telemetry, and intermittent connectivity.

## Templates

### Ingestion & Deployment

- **[dlt basic pipeline setup](../data-lake-platform/assets/ingestion/dlt/template-dlt-pipeline.md)** - Basic extraction and load pipeline.
- **[dlt REST API sources](../data-lake-platform/assets/ingestion/dlt/template-dlt-rest-api.md)** - REST ingestion with pagination, auth, and rate-limit handling.
- **[dlt database sources](../data-lake-platform/assets/ingestion/dlt/template-dlt-database-source.md)** - Database replication patterns.
- **[dlt incremental loading](../data-lake-platform/assets/ingestion/dlt/template-dlt-incremental.md)** - Timestamp, ID, merge, and lookback patterns.
- **[dlt warehouse loading](../data-lake-platform/assets/ingestion/dlt/template-dlt-warehouse-loading.md)** - Warehouse destination patterns.
- **[Deployment & MLOps template](assets/deployment/template-deployment-mlops.md)** - Full production operating spec.
- **[Deployment readiness checklist](assets/deployment/deployment-readiness-checklist.md)** - Go/no-go gate before release.
- **[API service template](assets/deployment/template-api-service.md)** - Real-time inference API skeleton.
- **[Batch scoring pipeline template](assets/deployment/template-batch-pipeline.md)** - Orchestrated offline scoring workflow.

### Monitoring & Incidents

- **[Monitoring & alerting template](assets/monitoring/template-monitoring-plan.md)** - Dashboards, SLOs, and alerts.
- **[Drift detection & retraining template](assets/monitoring/template-drift-retraining.md)** - Trigger, validate, and promote retraining flow.
- **[Incident runbook template](assets/ops/template-incident-runbook.md)** - General reliability incident response.
- **[Safety incident runbook](assets/incident/template-incident-runbook-safety.md)** - GenAI safety escalation workflow.
- **[Jailbreak investigation template](assets/incident/template-jailbreak-investigation.md)** - Post-incident analysis for prompt/safety bypasses.

### Safety, Privacy & Governance

- **[Safety prompt template](assets/safety/template-safety-prompt.md)** - Base safety system prompt scaffold.
- **[Output filter template](assets/safety/template-output-filter.md)** - Post-generation filtering policy.
- **[Guardrail config template](assets/safety/template-guardrail-config.md)** - Guardrail wiring for pre/post filters and severity handling.
- **[PII handling template](assets/privacy/template-pii-handling.md)** - Data handling and logging rules for sensitive inputs.
- **[Data anonymization template](assets/privacy/template-data-anonymization.md)** - Masking and de-identification workflow.
- **[Risk assessment template](assets/governance/template-risk-assessment.md)** - Delivery-time risk register.
- **[Policy checklist template](assets/governance/template-policy-checklist.md)** - Operational policy controls and evidence tracking.
- **[Security audit template](assets/governance/template-security-audit.md)** - Security review worksheet for AI deployments.

## Recency Protocol For Recommendations

When the user asks for the **best**, **latest**, **current**, or **still relevant** MLOps/LLMOps tooling:

1. Start from [data/sources.json](data/sources.json).
2. Verify current state using official docs and recent maintenance/release signals.
3. Confirm volatile facts such as release cadence, hosted-vs-self-hosted posture, pricing model, and managed-service availability.
4. Separate stable guidance from time-sensitive recommendations in the answer.

Minimum things to verify for tooling comparisons:

- Latest active documentation or release signal
- Current maintenance / ecosystem momentum
- Managed vs self-hosted deployment posture
- Telemetry, eval, and governance support
- Lock-in or data residency constraints

## External Sources

See [data/sources.json](data/sources.json) for curated references, including:

- EU AI Act and NIST governance baselines
- OpenTelemetry GenAI and MCP semantic conventions
- MCP authorization guidance
- OWASP GenAI and agentic AI security references
- Vendor docs for registries, feature stores, orchestration, serving, and observability

## Related Skills

- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** - Build and validate the model or feature pipeline.
- **[ai-llm](../ai-llm/SKILL.md)** - Choose prompting, tuning, or evaluation strategy.
- **[ai-rag](../ai-rag/SKILL.md)** - Design retrieval and search quality systems.
- **[ai-llm-inference](../ai-llm-inference/SKILL.md)** - Optimize low-level serving performance.
- **[ai-agents](../ai-agents/SKILL.md)** - Design agent control flow, MCP servers, handoffs, and memory.
- **[data-lake-platform](../data-lake-platform/SKILL.md)** - Broader lakehouse, Kafka, and warehouse infrastructure.
- **[qa-observability](../qa-observability/SKILL.md)** - Cross-system observability implementation depth.
- **[ops-devops-platform](../ops-devops-platform/SKILL.md)** - Platform operations and infra rollout depth.
- **huggingface-trackio** (external `huggingface-skills:` plugin) - Hugging Face experiment tracking with Trackio.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify volatile facts, versions, pricing, regulations, and product recommendations with live web sources before final answers.
- Prefer primary sources and include links when the answer depends on current state.
- If web access is unavailable, say so and mark vendor or regulatory guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

