# AI Product Patterns  

*Operational guide for building AI, GenAI, and Agentic AI products.*

This file includes ONLY:

- Templates  
- Checklists  
- Step-by-step processes  
- Decision trees  
- No theory  

---
## Table of Contents

- [Phase 1 — Problem Framing](#phase-1-—-problem-framing)
- [Phase 2 — Data Readiness](#phase-2-—-data-readiness)
- [Phase 3 — Model Approach Selection](#phase-3-—-model-approach-selection)
- [Phase 4 — Build & Evaluate](#phase-4-—-build-&-evaluate)
- [AI Evaluation Methodology](#ai-evaluation-methodology)
- [Phase 5 — Pilot & Iterate](#phase-5-—-pilot-&-iterate)
- [Phase 6 — Launch & Monitor](#phase-6-—-launch-&-monitor)
- [2. Agentic AI Patterns](#2-agentic-ai-patterns)
- [2.1 Agent Role Template](#21-agent-role-template)
- [2.2 Common Agent Patterns](#22-common-agent-patterns)
- [Pattern A — Planner → Executor](#pattern-a-—-planner-→-executor)
- [Pattern B — Multi-Agent Collaboration](#pattern-b-—-multi-agent-collaboration)
- [Pattern C — Guardrail Critic](#pattern-c-—-guardrail-critic)
- [2.3 Multi-Agent Orchestration](#23-multi-agent-orchestration)
- [3. RAG (Retrieval-Augmented Generation) Patterns](#3-rag-retrieval-augmented-generation-patterns)
- [3.1 RAG Template](#31-rag-template)
- [3.2 RAG Checklist](#32-rag-checklist)
- [4. AI Risk & Governance](#4-ai-risk-&-governance)
- [4.1 AI Risk Checklist](#41-ai-risk-checklist)
- [4.2 Governance Template](#42-governance-template)
- [5. AI Experiment Types](#5-ai-experiment-types)
- [5.1 Offline Evaluation](#51-offline-evaluation)
- [5.2 Online Experiments](#52-online-experiments)
- [5.3 Agentic Experiments](#53-agentic-experiments)
- [6. AI Discovery Patterns](#6-ai-discovery-patterns)
- [6.1 AI Opportunity Assessment Template](#61-ai-opportunity-assessment-template)
- [6.2 When NOT to Use AI](#62-when-not-to-use-ai)
- [7. Decision Trees](#7-decision-trees)
- [7.1 Should You Use AI?](#71-should-you-use-ai)
- [7.2 Should You Use Agentic AI?](#72-should-you-use-agentic-ai)
- [8. Definition of Done (AI Product)](#8-definition-of-done-ai-product)
- [9. AI PM Tools](#9-ai-pm-tools)
- [9.1 Tool Categories](#91-tool-categories)
- [9.2 AI Tool Selection Checklist](#92-ai-tool-selection-checklist)
- [9.3 Hybrid Decision Loop Pattern](#93-hybrid-decision-loop-pattern)
- [9.4 AI Product Evaluation Checklist](#94-ai-product-evaluation-checklist)
- [9.4 Product Explainability](#94-product-explainability)


# 1. AI Product Development Lifecycle (Operational Version)

Use this as the core workflow for any AI product.

## Phase 1 — Problem Framing

**Checklist**

- [ ] Clear target user & job-to-be-done  
- [ ] Pain severity validated (interviews)  
- [ ] Non-AI alternatives documented  
- [ ] Success metric identified (accuracy, latency, cost, engagement, etc.)

**Template**
User:
Problem:
Current workaround:
Why AI is needed:
Core success metric:
Risks (value / feasibility / viability):

---

## Phase 2 — Data Readiness

**Checklist**

- [ ] Source data identified (internal / external)  
- [ ] Data labeling strategy defined  
- [ ] Bias risks identified  
- [ ] Data quality score (completeness, consistency, timeliness)  
- [ ] Legal/permission constraints mapped  

**Data Readiness Score (1–5)**
1 = No usable data
3 = Needs labeling/cleanup
5 = Ready for model training

---

## Phase 3 — Model Approach Selection

Use the simplest viable model first.

**Menu**

- Predictive ML  
- Generative LLM  
- Agentic multi-step model  
- Retrieval-augmented generation (RAG)  
- Hybrid (retrieval + action-taking agent)

**Selection Checklist**

- [ ] Problem needs classification/recommendation → predictive  
- [ ] Problem needs content creation → generative  
- [ ] Problem requires planning/action → agentic  
- [ ] Data is structured → predictive  
- [ ] Facts must be grounded → add RAG  

---

## Phase 4 — Build & Evaluate

**Operational Metrics**

- **Accuracy / Precision / Recall** (prediction tasks)  
- **Factuality** (LLMs)  
- **Hallucination rate**  
- **Latency** (ms)  
- **Cost-per-inference**  
- **Agent task success rate**  
- **Step efficiency** (# steps per successful task)  

**Evaluation Checklist**

- [ ] Offline test set  
- [ ] Human review sample (20–100 examples)  
- [ ] Red-team evaluation (edge cases)  
- [ ] Bias & fairness tests  

---

## AI Evaluation Methodology

Evaluation is a first-class PM artifact, not a QA handoff. The eval set is the spec; if it does not exist, the feature is not defined.

### Evaluation-First Development (Evals as Unit Tests)

Write evaluation cases before building the feature. The eval set encodes what "good" means and serves as the acceptance criteria. Capture real failure cases from production back into the eval set on a rolling basis — production failures are the highest-quality test cases.

**Workflow**

1. Define the task and success criteria with stakeholders.
2. Collect or construct representative inputs covering normal, edge, and adversarial cases.
3. Label expected outputs (ground truth or rubric).
4. Run the eval suite on every model, prompt, or tool change before shipping.
5. Add every production failure to the eval set within 48 hours of discovery.

### LLM-as-Judge

Use a capable model to grade outputs at scale when human review is the bottleneck. The judge is not free — it has known failure modes and requires calibration before it can be trusted.

**Design the judge prompt**

- Include an explicit, enumerated rubric (e.g., faithfulness, completeness, conciseness scored 1–5).
- Add few-shot anchors: 2–3 examples per score level so the judge calibrates to your rubric rather than its own priors.
- Return a score and a brief reasoning chain — the chain enables audit and catches obvious errors.

**Calibrate before scaling**

- Label a sample of 50–100 outputs with human raters.
- Measure judge-human agreement (Cohen's kappa target: ≥ 0.7 before trusting the judge at scale).
- Re-calibrate when the judge model, prompt, or task distribution changes.

**Known judge biases**

| Bias | Description | Mitigation |
|------|-------------|------------|
| Position bias | Prefers the first or last option in pairwise comparisons | Randomize order; average both orderings |
| Verbosity bias | Rates longer answers higher regardless of quality | Rubric must score precision, not length |
| Self-preference | Model rates its own outputs higher | Use a different model as judge where possible |

**Pairwise comparison**

When absolute scoring is noisy (e.g., two responses both seem "good"), use pairwise comparison: ask the judge which of two outputs is better on a specific dimension. Pairwise agreement tends to be higher than absolute-score agreement and surfaces meaningful rank differences between model versions.

### Minimum Eval Suite Size by Risk Level

Coverage (case diversity) matters more than raw count. A 200-case suite with identical inputs is weaker than a 50-case suite spanning diverse user intents, edge cases, and adversarial inputs.

| Risk Level | Minimum Cases | Notes |
|------------|---------------|-------|
| Low — informational, easily corrected | 20–50 | Cover happy path and 3–5 edge cases |
| Medium — workflow-integrated, moderate correction cost | 100 | Cover edge cases, at least 10% adversarial inputs |
| High / regulated — consequential decisions, compliance overlap | 200+ | Explicit coverage matrix required; adversarial inputs mandatory |

Every suite at medium risk or above should include: out-of-distribution inputs, language or locale variation if relevant, and inputs designed to elicit known failure modes of the underlying model.

### RAG Evaluation (RAGAS-Style)

For retrieval products, retrieval quality and generation quality fail independently. Measure them separately.

| Metric | What It Measures | Failure Signal |
|--------|-----------------|----------------|
| Context precision | What fraction of retrieved chunks are actually relevant | High noise in retrieval; irrelevant context dilutes the answer |
| Context recall | What fraction of needed information was retrieved | Missing context causes incomplete or wrong answers |
| Faithfulness / groundedness | Is the answer supported by the retrieved context | Low score means hallucination even when retrieval is good |
| Answer relevance | Does the answer address the question asked | Model ignores retrieved context and drifts off-topic |

A low faithfulness score is a hallucination signal regardless of retrieval quality. Retrieval and generation pipelines must be tuned and monitored independently.

### Regression Evaluation

Define exactly what runs when a model, prompt, or tool changes.

**Trigger conditions**

- [ ] Model version changes (major or minor)
- [ ] System prompt or instruction changes
- [ ] Tool schema or tool availability changes
- [ ] Retrieval index or embedding model changes

**What runs**

- Re-run the full eval suite against the new configuration.
- Compare pass rate and per-category scores against the prior baseline.
- Flag any regression (pass rate drop or score decline in any high-severity category).
- Block deploy on regression in any category tagged high-severity.

**Reporting format**

| Category | Baseline | Current | Delta | Status |
|----------|----------|---------|-------|--------|
| Faithfulness | 0.87 | 0.83 | -0.04 | BLOCK |
| Task success | 0.91 | 0.92 | +0.01 | PASS |

### Human-Baseline Comparison

Establish the human performance ceiling on the task before or alongside the first model eval. Report AI performance relative to the human baseline — not as an absolute — so stakeholders understand how close the system is to "good enough" and where the gap justifies further investment.

**Process**

1. Sample 50–100 representative task instances.
2. Have qualified human raters complete the task independently.
3. Score human output on the same rubric as the model.
4. Report: human baseline, AI score, gap, and whether the gap is acceptable for the use case.

Do not launch a feature without this reference point. An AI system scoring 0.78 on faithfulness sounds reasonable in isolation; knowing the human ceiling is 0.95 changes the investment decision.

---

## Phase 5 — Pilot & Iterate

**Checklist**

- [ ] Soft launch to < 5% traffic  
- [ ] Human-in-the-loop workflow defined  
- [ ] Guardrails (rate limits, content filters)  
- [ ] Logging & monitoring (fail cases, retries)  
- [ ] User-facing feedback loop  

---

## Phase 6 — Launch & Monitor

**Checklist**

- [ ] On-call processes for model issues  
- [ ] Drift detection  
- [ ] Feedback retraining pipeline  
- [ ] Incident response playbook  
- [ ] Business KPI tracking  

---

# 2. Agentic AI Patterns

Agentic systems = AI that can take multi-step actions, use tools, and plan.

## 2.1 Agent Role Template

Agent Name:
Goal:
Tools/APIs it can call:
Constraints:
Success criteria:
Failure modes:
Human oversight needed:

## 2.2 Common Agent Patterns

### Pattern A — Planner → Executor

Use for workflows requiring decomposition.

Planner:

Breaks goal into tasks
Determines order
Monitors progress
Executor(s):

Perform individual steps
Report back to planner

### Pattern B — Multi-Agent Collaboration

Use for complex domains.

Agents:

- Researcher (info retrieval)  
- Synthesizer (summaries)  
- Critic (validate outputs)  
- Executor (actions)  

### Pattern C — Guardrail Critic

Use when hallucination risk is high.

Critic does:

- [ ] Factuality checks  
- [ ] Policy violations  
- [ ] Bias detection  
- [ ] Harmful output classification  

---

## 2.3 Multi-Agent Orchestration

Rather than one large LLM handling everything, use "puppeteer" orchestrators that coordinate specialist agents.

**Architecture**

```text
┌─────────────────────────────────────────────────┐
│              Orchestrator Agent                 │
│  (Plan-and-Execute pattern, frontier model)     │
└────────────┬────────────┬────────────┬──────────┘
             │            │            │
     ┌───────▼───┐  ┌─────▼─────┐  ┌───▼───────┐
     │ Researcher│  │   Coder   │  │  Analyst  │
     │   Agent   │  │   Agent   │  │   Agent   │
     │ (mid-tier)│  │(mid-tier) │  │(mid-tier) │
     └───────────┘  └───────────┘  └───────────┘
```

**Plan-and-Execute Pattern**

Use a more capable model for planning and cheaper models for execution when the workflow benefits from decomposition. This can lower cost and latency, but verify the trade-off with task-level evals before assuming savings.

```text
Planner (frontier model):
├─ Decomposes goal into tasks
├─ Determines execution order
├─ Monitors progress
└─ Handles exceptions

Executor(s) (mid-tier models):
├─ Perform individual steps
├─ Report status back
└─ Request help if stuck
```

**Protocols**

- **MCP** (Model Context Protocol) — open protocol for context and tool integration. The PM owns which tools and data sources the agent may access and the permission boundary (e.g., read-only vs. write access to a CRM); engineering owns the MCP server implementation.
- **A2A** (Agent-to-Agent Protocol) — open agent interoperability protocol launched by Google with partners. The PM owns which tasks are safe to delegate between agents and the escalation or human-in-loop path when a delegated task fails or reaches low-confidence; engineering owns the protocol wiring.

**Checklist**

- [ ] Clear agent boundaries (each agent has single responsibility)
- [ ] Inter-agent communication protocol defined
- [ ] State management across agent boundaries
- [ ] Conflict resolution mechanism
- [ ] Cost-per-inference tracked per agent type
- [ ] Model selection based on task complexity
- [ ] Task success, groundedness, latency, and cost metrics defined
- [ ] Regression suite for core flows
- [ ] Failure review process for agent errors and escalations
- [ ] Human escalation path for all agents

**Cost Optimization Pattern**

| Task Type | Model Tier | Example |
|-----------|------------|---------|
| Complex reasoning / orchestration | Top-tier reasoning model | Planning, strategy |
| Standard tasks | Mid-tier generalist model | Coding, analysis |
| High-frequency execution | Small/fast model | Formatting, extraction, simple queries |

---

# 3. RAG (Retrieval-Augmented Generation) Patterns

## 3.1 RAG Template

Retriever:

Vector DB
Search parameters
Filters
Generator:

Model (GPT, Claude, etc.)
Context window
Safety constraints
Evaluation:

Relevance@K
Factuality score
Latency

## 3.2 RAG Checklist

- [ ] Chunking strategy defined  
- [ ] Embedding model selected  
- [ ] Max tokens per chunk optimized  
- [ ] Prompt includes citations  
- [ ] Retrieval fallback flow  
- [ ] Timeout and retry logic  

---

# 4. AI Risk & Governance

## 4.1 AI Risk Checklist

**Value Risks**

- [ ] Users don’t trust output  
- [ ] Hallucinations harm experience  
- [ ] Output not actionable  

**Usability Risks**

- [ ] Too slow (latency > accepted threshold)  
- [ ] Confusing UI for errors/edge cases  

**Feasibility Risks**

- [ ] Missing or dirty data  
- [ ] Model not robust enough  

**Viability Risks**

- [ ] Legal/ethical exposure  
- [ ] Customer data retention risk  
- [ ] Excessive cost per inference  

---

## 4.2 Governance Template

Usage Policy:
Safety Constraints:
Human Oversight:
Data Privacy Rules:
Logging Policy:
Escalation Path:
Retraining Frequency:

---

# 5. AI Experiment Types

## 5.1 Offline Evaluation

- Use test sets  
- Human review panel  
- Robustness tests  
- Prompt variation tests  

## 5.2 Online Experiments

- **A/B tests**  
- **Interleaving tests** (ranking use cases)  
- **Shadow mode** (run model behind the scenes)  
- **Human override tracking**  

## 5.3 Agentic Experiments

- Task completion rate  
- Unexpected action detection  
- Step count deviation  
- Human-in-the-loop approval rate  

---

# 6. AI Discovery Patterns

## 6.1 AI Opportunity Assessment Template

User segment:
Task:
Pain:
AI value type:

Predict
Generate
Decide
Take Action
Evidence problem exists:
Why AI is needed:
Risks:
Success metrics:

## 6.2 When NOT to Use AI

- Problem does not require variability or intelligence  
- Deterministic rules handle it well  
- Data insufficient  
- High-stakes with no oversight  
- Speed/latency constraints too strict  

---

# 7. Decision Trees

## 7.1 Should You Use AI?

Is the problem high-value and high-frequency?
├─ No → Do not use AI
└─ Yes
↓
Does AI outperform rules/manual?
├─ No → Prototype rule-based approach
└─ Yes
↓
Do you have (or can get) the data?
├─ No → Data project first
└─ Yes → Move to design

---

## 7.2 Should You Use Agentic AI?

Does the task require multi-step planning?
├─ Yes → Agentic candidate
└─ No
↓
Does the model need to use external tools/APIs?
├─ Yes → Agentic candidate
└─ No
↓
Is hallucination risk manageable with guardrails?
├─ No → Wait / redesign
└─ Yes → Agentic approved

---

# 8. Definition of Done (AI Product)

A model or agent is **ready** when:

- [ ] Problem validated through interviews  
- [ ] Data readiness confirmed  
- [ ] Evaluation metrics pass thresholds  
- [ ] Safety guardrails implemented  
- [ ] Cost-per-inference acceptable  
- [ ] Human-in-the-loop path defined  
- [ ] Drift monitoring in place  
- [ ] Success metric tied to business KPI  

---

# 9. AI PM Tools

Tools to augment PM workflows. AI assists; human decides.

## 9.1 Tool Categories

| Category | Example Tools | Use Case |
|----------|---------------|----------|
| PRD Generation | ChatPRD, Notion AI, Coda AI | Draft specs, user stories, acceptance criteria |
| Feedback Analysis | Productboard AI, Chisel, Dovetail | Synthesize customer signals, sentiment analysis |
| Roadmapping | ProdPad CoPilot, Linear | Initiative descriptions, prioritization assist |
| Analytics | Amplitude, PostHog, Mixpanel | Product usage insights, experiment analysis |
| Research | Maze AI, UserTesting | Usability test synthesis, interview summaries |

Treat these as examples only. Verify current fit, pricing, security posture, and roadmap against live sources before recommending a tool.

## 9.2 AI Tool Selection Checklist

- [ ] Integrates with existing stack (Jira, Slack, Figma, etc.)
- [ ] Output is editable and auditable
- [ ] Human review built into workflow
- [ ] Data stays within compliance boundaries
- [ ] Cost per seat justified by time savings
- [ ] No vendor lock-in on generated content
- [ ] Evaluation and audit trails exist for critical workflows

## 9.3 Hybrid Decision Loop Pattern

AI and human have distinct roles:

```text
AI Role:
├─ Surface anomalies in data
├─ Identify patterns across feedback
├─ Generate forecasts and scenarios
├─ Draft artifacts (PRDs, stories, roadmaps)
└─ Flag outliers for review

Human Role:
├─ Apply business context
├─ Make ethical judgment calls
├─ Set long-term strategy
├─ Approve customer-facing decisions
└─ Own accountability
```

## 9.4 AI Product Evaluation Checklist

- [ ] Task success rate measured on representative workflows
- [ ] Groundedness or factuality checks defined where retrieval or knowledge claims matter
- [ ] Latency budget and cost-per-task targets documented
- [ ] Failure review loop captures high-severity errors and recurring misses
- [ ] Regression suite exists for top user journeys before major prompt/model/tool changes
- [ ] Human escalation path is explicit for low-confidence, high-risk, or blocked states

**Checklist**

- [ ] AI output always reviewed before shipping
- [ ] Human approval gate for customer-impacting changes
- [ ] Disagreements resolved by human, not AI
- [ ] AI recommendations include confidence level
- [ ] Audit trail of AI suggestions vs. human decisions

## 9.4 Product Explainability

Products are increasingly evaluated by AI systems (search, recommendations, assistants) before humans interact.

**Checklist**

- [ ] Product purpose is machine-readable (structured data, clear metadata)
- [ ] Value proposition stated in plain language (no jargon)
- [ ] Limitations and constraints documented
- [ ] API/integration surface is self-describing
- [ ] Documentation optimized for both human and AI consumption

---

**End of file.**
