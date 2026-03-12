# AI Product Patterns  

*Operational guide for building AI, GenAI, and Agentic AI products.*

This file includes ONLY:

- Templates  
- Checklists  
- Step-by-step processes  
- Decision trees  
- No theory  

---

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

## 2.3 Multi-Agent Orchestration (2026 Pattern)

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

Use capable model for planning, cheaper models for execution. Can reduce costs by 90%.

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

**Protocols (2026)**

- **MCP** (Model Context Protocol) — Anthropic standard for agent tools
- **A2A** (Agent-to-Agent Protocol) — Google standard for agent communication

**Checklist**

- [ ] Clear agent boundaries (each agent has single responsibility)
- [ ] Inter-agent communication protocol defined
- [ ] State management across agent boundaries
- [ ] Conflict resolution mechanism
- [ ] Cost-per-inference tracked per agent type
- [ ] Model selection based on task complexity
- [ ] Human escalation path for all agents

**Cost Optimization Pattern**

| Task Type | Model Tier | Example |
|-----------|------------|---------|
| Complex reasoning / orchestration | Frontier (Claude Opus, GPT-4) | Planning, strategy |
| Standard tasks | Mid-tier (Claude Sonnet, GPT-4o) | Coding, analysis |
| High-frequency execution | Small (Haiku, GPT-4o-mini) | Formatting, simple queries |

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

# 9. AI PM Tools (Jan 2026)

Tools to augment PM workflows. AI assists; human decides.

## 9.1 Tool Categories

| Category | Tools | Use Case |
|----------|-------|----------|
| PRD Generation | ChatPRD, Notion AI, Coda AI | Draft specs, user stories, acceptance criteria |
| Feedback Analysis | Productboard AI, Chisel, Dovetail | Synthesize customer signals, sentiment analysis |
| Roadmapping | ProdPad CoPilot, Linear | Initiative descriptions, prioritization assist |
| Analytics | Amplitude, PostHog, Mixpanel | Product usage insights, experiment analysis |
| Research | Maze AI, UserTesting | Usability test synthesis, interview summaries |

## 9.2 AI Tool Selection Checklist

- [ ] Integrates with existing stack (Jira, Slack, Figma, etc.)
- [ ] Output is editable and auditable
- [ ] Human review built into workflow
- [ ] Data stays within compliance boundaries
- [ ] Cost per seat justified by time savings
- [ ] No vendor lock-in on generated content

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
