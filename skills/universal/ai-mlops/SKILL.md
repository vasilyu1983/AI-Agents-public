---
name: ai-mlops
description: "Runs production ML and LLM systems. Use when deploying, canarying, rolling back, monitoring drift or feature skew, promoting champions, migrating providers, or handling incidents."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-08-21
---

# MLOps & LLMOps - Production Operations Hub

**Operating posture:** version every changeable artifact, gate every release with a regression-eval suite in CI, instrument the whole path with OpenTelemetry (pin the GenAI semantic-convention schema version you emit), treat tool/RAG context as untrusted input, and ship rollback plus incident playbooks before launch.

## When To Use This Skill

Activate this skill when the user asks for:

- Deploying an ML, LLM, RAG, or agent-backed system to production
- Designing serving, batch, hybrid, or multi-region runtime architecture
- Adding observability, drift detection, alerting, retraining, or release gates
- Writing incident runbooks, rollback plans, or go/no-go checklists
- Migrating an LLM system to a new model, model version, provider, or API surface
- Hardening an AI system against prompt injection, RAG poisoning, tool abuse, or data leakage
- Building governance artifacts for privacy, auditability, or regulated rollout
- Choosing how to operate prompts, model artifacts, feature definitions, or agent graphs safely
- Diagnosing why changes to an ML system keep rippling: entanglement, correction cascades, undeclared consumers, pipeline jungles, or config sprawl
- Operating fairness, privacy-budget, human-oversight, appeal, watermark/provenance, copyright/memorization, or environmental controls
- Deploying multimodal image, document, audio, video, vision-language, or diffusion systems with bounded media ingestion, safety, latency, and cost

## Scope Boundaries

- **EDA, feature engineering, training, SQL transformation** -> [ai-ml-data-science](../ai-ml-data-science/SKILL.md)
- **Prompt strategy** -> [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md); **eval design** -> [ai-evals](../ai-evals/SKILL.md)
- **Fine-tuning and fine-tuning ROI** -> [ai-llm](../ai-llm/SKILL.md); **preference / RL post-training** -> [ai-post-training](../ai-post-training/SKILL.md)
- **Retrieval architecture, chunking, reranking, search quality** -> [ai-rag](../ai-rag/SKILL.md)
- **Latency, batching, quantization, GPU serving internals** -> [ai-llm-inference](../ai-llm-inference/SKILL.md)
- **Deep agent architecture, MCP server design, handoffs, memory** -> [ai-agents](../ai-agents/SKILL.md)

Keep this skill focused on **operating** production systems after the architecture exists or while defining production controls for it.

## Quick Reference

| Task | Default Tooling / Pattern | When to Use |
|------|---------------------------|-------------|
| Data ingestion | dlt + contracts + lineage | APIs, CDC, warehouse loading, incremental syncs |
| Batch scoring | Airflow, Dagster, Prefect | High-volume scoring, backfills, delayed labels |
| Real-time serving | FastAPI, gRPC, KServe, BentoML | Low-latency APIs with explicit SLOs |
| LLM serving | vLLM; SGLang when the model or feature needs it | High-throughput text generation endpoints; TGI is in maintenance mode, so do not start new deployments on it |
| Registry / promotion | MLflow, W&B, ZenML; promote by alias (champion/challenger), not stage | Versioning, approvals, rollbacks, lineage |
| Feature consistency | Feast / managed feature stores | Batch + online parity and point-in-time correctness |
| Observability | OpenTelemetry + Prometheus/Grafana | Traces, metrics, alerts, cost and latency budgets |
| OTel GenAI conventions | Pin the semconv schema version you emit | Before relying on attribute names, check the conventions' stability status and location in the OpenTelemetry semantic-conventions project |
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
    │   ├─ Latency-sensitive API -> online service with SLOs, timeouts, rollback target
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

## Operating Rules

- **OpenTelemetry first**: standardize traces and metrics for requests, prompts, models, tools, and MCP interactions, using the OTel GenAI (and, where relevant, MCP) semantic conventions. Pin the exact convention schema version or commit you emit and record it with the telemetry; before shipping, check the conventions' stability status in the OpenTelemetry project, because experimental attribute names change and dashboards keyed on them break silently.
- **Eval-as-CI-gate**: every model, prompt, feature, retrieval, or agent-graph change must pass a regression-eval suite before deployment. This skill owns the wiring: where the gate runs in CI, what blocks a deploy, and the rollback path ([online-evaluation-patterns.md](references/online-evaluation-patterns.md)). Suite design, LLM-judge calibration against human labels, and threshold setting belong to [ai-evals](../ai-evals/SKILL.md).
- **Treat retrieved content and tools as untrusted**: RAG context, tool outputs, external APIs, and MCP servers all need containment, validation, and audit logs.
- **Version the full runtime**: model artifact, feature definitions, prompt/config, safety policies, tool schemas, and agent graphs.
- **Promote by alias, not stage**: point serving at a registry alias (`@champion`, `@challenger`) and promote or roll back by moving the alias; never let a lifecycle stage or "latest version" decide what serves. Check your registry's docs for how it names and protects aliases.
- **Serving-engine versions are migration work**: engine flags, deprecated execution paths, and semantic differences (log-probabilities, sampling defaults) belong to [ai-llm-inference](../ai-llm-inference/SKILL.md); here, treat an engine upgrade like a model change and put it through the same eval gate and canary.
- **Regulatory timing is a lookup, not a memory**: before committing a compliance roadmap, read the regulation's official journal text and the regulator's implementation timeline for the obligations that apply to the system's risk class, and treat "politically agreed" or "adopted" as distinct from "in force". The canonical AI Act statement and its lookup steps live in startup-compliance-enterprise-readiness regulatory-overlays.

## Canary Promotion Gate

Define offline blockers, shadow checks, canary cohort, observation window, rollback trigger, and accountable owner before changing production traffic. Promote only when model quality, feature or retrieval skew, latency, error, cost, and safety metrics clear their slice-specific bounds and the rollback path has restored the previous full runtime in rehearsal. A healthy endpoint or registry alias change is deployment evidence, not production-behavior evidence.

## Known Traps

- Shipping a model, prompt, or agent change before instrumentation is in place to tell you what broke.
- Versioning only the model artifact while prompt config, tool schema, safety policy, or retrieval contract changes out-of-band.
- Treating safety incidents as ordinary runtime failures with no dedicated escalation path, evidence capture, or owner.
- Building retraining triggers with no gated promotion step, rollback target, or shadow evaluation.
- Assuming one global runbook covers ML, RAG, and agent failures equally well when the blast radius and evidence requirements differ.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/drift_check.py` | PSI and KL on per-bin counts, with sparse-bin pooling, smoothing, and a per-feature no-drift noise floor (PSI noise shrinks as windows grow). Exit 1 on ALERT, 2 on invalid input. |
| `scripts/deployment_smoke_test.sh` | Shadow/canary smoke verifier for an OpenAI-compatible endpoint: health, models list, JSON-parsed chat content and finish_reason, latency. Fails closed: every expected check must report. |

## Navigation

### Release & Architecture

- **[Data Ingestion Patterns](references/data-ingestion-patterns.md)** - Use for contracts, CDC, incremental loading, lineage, replay, and schema evolution.
- **[Deployment Patterns](references/deployment-patterns.md)** - Use to choose batch, online, hybrid, or streaming deployment modes.
- **[Deployment Lifecycle](references/deployment-lifecycle.md)** - Use for promotion, rollout, rollback, and decommissioning workflow.
- **[Model & Provider Migration](references/model-provider-migration.md)** - Use when swapping an LLM model, version, provider, or API surface: contract inventory, API-surface comparison, eval replay, canary, and rollback triggers.
- **[Model Registry Patterns](references/model-registry-patterns.md)** - Use for metadata, artifact packaging, and promotion governance.
- **[Feature Store Patterns](references/feature-store-patterns.md)** - Use for batch/online parity, latency budgets, and point-in-time correctness.
- **[Multi-Region Patterns](references/multi-region-patterns.md)** - Use for residency, failover, disaster recovery, and regional rollback.
- **[ML Technical Debt Taxonomy](references/ml-technical-debt-taxonomy.md)** - Use to diagnose boundary erosion/CACHE, correction cascades, undeclared consumers, data/config/pipeline debt, and feedback loops, each with a detection signal and mitigation.

### Observability, Evals & Cost

- **[Monitoring Best Practices](references/monitoring-best-practices.md)** - Use for SLOs, alert routing, dashboards, and production metric coverage. Includes OTel GenAI maturity caveat.
- **[Drift Detection Guide](references/drift-detection-guide.md)** - Use for feature, label, concept, and embedding drift response.
- **[Automated Retraining Patterns](references/automated-retraining-patterns.md)** - Use for trigger selection, validation gates, safe retraining rollout, and training job queue/scheduler guidance.
- **[Online Evaluation Wiring](references/online-evaluation-patterns.md)** - Use for eval-gate placement in CI/CD, rollout and rollback wiring, and feedback logging; experiment and judge design link out to ai-evals.
- **[Experiment Tracking Patterns](references/experiment-tracking-patterns.md)** - Use for run naming, artifact retention, registry handoff, and auditability.
- **[ML Cost Levers](references/cost-management-finops.md)** - Use for ML-specific cost levers (tagging, spot checkpoint interval, retraining cadence, tuning budgets, GPU utilization); commitments, budgets, and chargeback live in ops-cost-optimization.
- **[Incident Response Playbooks](references/incident-response-playbooks.md)** - Use for first-response steps, triage flow, and postmortem coverage.
- **[AgentOps Patterns](references/agentops-patterns.md)** - Use for agent traces, replay, tool-call telemetry, and runtime debugging.

### Security & Governance

- **[Threat Models](references/threat-models.md)** - Use first for trust boundaries; maps each threat to its owning reference.
- **Tool governance, approval paths, state isolation, output filtering** -> [ai-agents guardrails-implementation](../ai-agents/references/guardrails-implementation.md)
- **Prompt injection and jailbreak test coverage** -> [qa-agent-testing prompt-injection-testing](../qa-agent-testing/references/prompt-injection-testing.md)
- **RAG poisoning, retrieval ACLs, context sanitization** -> [ai-rag security-red-team-cases](../ai-rag/references/security-red-team-cases.md)
- **[Model Extraction Defense](references/extraction-defense.md)** - Use for query-abuse detection, rate shaping, and capability theft defenses.
- **[Privacy Protection](references/privacy-protection.md)** - Use for PII handling, retention, redaction, and minimization.
- **Model and data artifact supply chain (hash pinning, safe formats, signing)** -> [software-security-appsec supply-chain-security](../software-security-appsec/references/supply-chain-security.md#ml-model-and-data-artifacts)
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

For responsible and multimodal operations, start with [references/responsible-multimodal-operations.md](references/responsible-multimodal-operations.md): release evidence, privacy/fairness controls, poisoning response, oversight and appeals, provenance, environmental accounting, media ingestion, multimodal safety, capacity, and incidents.

## Related Skills

- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** - Build and validate the model or feature pipeline.
- **[ai-llm](../ai-llm/SKILL.md)** - Adapt a model (SFT, PEFT, distillation).
- **[ai-post-training](../ai-post-training/SKILL.md)** - Preference optimization and RL on a reward signal.
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** / **[ai-evals](../ai-evals/SKILL.md)** - Prompt strategy and eval design.
- **[ai-rag](../ai-rag/SKILL.md)** - Design retrieval and search quality systems.
- **[ai-llm-inference](../ai-llm-inference/SKILL.md)** - Optimize low-level serving performance.
- **[ai-agents](../ai-agents/SKILL.md)** - Design agent control flow, MCP servers, handoffs, and memory.
- **[data-lake-platform](../data-lake-platform/SKILL.md)** - Broader lakehouse, Kafka, and warehouse infrastructure.
- **[qa-observability](../qa-observability/SKILL.md)** - Cross-system observability implementation depth.
- **[ops-devops-platform](../ops-devops-platform/SKILL.md)** - Platform operations and infra rollout depth.
- **[ops-cost-optimization](../ops-cost-optimization/SKILL.md)** - Commitments, budgets, anomaly alerts, chargeback/showback, and API cost control.
- **huggingface-trackio** (external `huggingface-skills:` plugin) - Hugging Face experiment tracking with Trackio.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
