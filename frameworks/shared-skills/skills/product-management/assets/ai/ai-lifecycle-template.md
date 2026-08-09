# AI Product Lifecycle Template  

*Purpose: Define, evaluate, and operationalize AI-powered features/products.*

This template aligns with predictive AI, generative AI, and agentic AI workflows.

---

# 1. Overview

Use this template to:

- Frame the AI problem  
- Evaluate data readiness  
- Choose model approach  
- Define evaluation metrics  
- Plan delivery + governance  
- Ensure safety, cost, and feasibility  

---

# 2. AI Lifecycle Template (Copy/Paste)

## 1. Problem Framing

User Segment:
Problem Statement:
Context:
Why AI is needed (vs rules/manual):
Primary Success Metric:
Secondary Metrics:
Guardrails (latency, safety, cost):

---

## 2. Data Readiness

Data Sources:
Data Types (structured / text / images / logs):
Label Availability:
Data Quality Score (1–5):
Gaps or Missing Data:
Privacy Considerations:
Bias Risk Areas:
Data Contract (if needed):

---

## 3. Model Approach

Select one or more:

- Predictive ML (classification/regression)  
- Generative LLM  
- RAG (Retrieval-Augmented Generation)  
- Agentic AI (planner + executor, multi-agent)  
- Hybrid approach  

Chosen Approach:
Why this approach:
Baseline Model (if any):
Constraints (compute, latency, cost):
Expected Accuracy/Factuality:
Fallback Path:

---

## 4. Evaluation Plan

Define measurable, objective tests.

### 4.1 Offline Evaluation

Test Dataset:
Metrics:

Accuracy / Precision / Recall (predictive)
Factuality / Hallucination rate (LLM)
Relevance@K (RAG)
Task success rate (agents)
Target Thresholds:
Reviewer Sample Size:
Edge-Case Handling:

### 4.2 Online Evaluation (Once Launched)

A/B Test Plan:
Primary Online Metric:
Secondary Metrics:
Guardrail Metrics:
User Feedback Loop:

---

## 5. Safety & Risk

Safety Filters Required (YES/NO):
Types (PII removal, toxicity, hallucination guardrails):

Bias Checks:
Legal/Compliance Risks:
Failure Modes:
Human-in-the-Loop Needed? (YES/NO)
Escalation Path:

---

## 6. System Design

Inputs:
Model(s) Used:
Retrieval Layer (if RAG):
Orchestration Layer (if agentic):
Tools/APIs Used:
Output Format:
Timeout Rules:
Retry Logic:
Versioning Approach:

---

## 7. Latency & Cost Targets

Latency Target (ms):
Max Cost per Request ($):
Expected Volume:
Caching Strategy:
Monitoring Plan:

---

## 8. Deployment Plan

Rollout Strategy (beta / gated / % traffic):
Observability:
Logging:
Alerts:
Drift Detection:
Retraining Frequency:

---

## 9. Open Questions & Dependencies

Outstanding Risks:
Team Dependencies:
Tech Dependencies:
Data Dependencies:
Decision Needed By:

---

# 3. Example (Editable)

1. Problem Framing

Segment: Customer support reps
Problem: Reps spend 3–6 min searching for answers
AI Need: Summarize internal docs and propose draft replies
Primary Metric: Avg handle time (AHT)
Guardrails: Factuality > 85%, Latency < 800ms

2. Data Readiness

Sources: Knowledge base, CRM tickets
Data Types: Text
Label Availability: Partial
Data Quality Score: 3/5
Privacy: Redact customer data

3. Model Approach

Chosen: RAG + LLM
Why: Must ground answers in internal docs
Constraints: Latency, cost
Fallback: Show top search results if model uncertain

4. Evaluation Plan

Offline:

Factuality > 85%
Hallucination rate < 10%
Online:
AHT reduction 10–20%
CSAT/QA scores stable
5. Safety & Risk

Safety Filters: Enabled (PII, hallucination guardrails)
Failure Modes: Wrong advice, outdated docs
Human-in-the-loop: YES for red flag cases

6. System Design

Retriever: Vector DB
Model: (e.g., Claude, GPT)
Output: Suggested reply + citations
Timeout: 2s
Retry: 1

7. Latency & Cost

Latency Target: 700ms
Cost: <$0.01 per query

8. Deployment Plan

Beta: 10% reps
Monitoring: Latency, factuality, override rate
Drift: Monthly review

9. Dependencies

Need updated KB
Need PII scrubber in place

---

# 4. Checklist (Quality Control)

- [ ] Clear problem + user segment  
- [ ] Data sources validated  
- [ ] Data quality scored  
- [ ] Model approach justified  
- [ ] Offline + online metrics defined  
- [ ] Safety guardrails set  
- [ ] Latency + cost thresholds set  
- [ ] Retraining plan defined  
- [ ] Failure modes documented  
- [ ] Rollout strategy decided  

---

# 5. Definition of Done (AI Lifecycle)

AI spec is **ready** when:

- [ ] Stakeholders understand the problem  
- [ ] Data meets minimum quality  
- [ ] Evaluation metrics exceed thresholds  
- [ ] Guardrails active  
- [ ] Human-in-the-loop defined where needed  
- [ ] Deployment path documented  
- [ ] No open risks blocking progress  

---

**End of file.**
