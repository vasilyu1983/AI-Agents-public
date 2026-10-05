# Incident Response Playbooks for ML, LLM & RAG Systems

Operational runbooks for major categories of production failures.

Use this when the user needs first-response steps, triage flow, or postmortem coverage for AI production incidents.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [1. Model Performance Degradation](#1-model-performance-degradation)
- [2. Data Pipeline Failure](#2-data-pipeline-failure)
- [3. API Outage / Latency Spikes](#3-api-outage-latency-spikes)
- [4. RAG / LLM-Specific Incidents](#4-rag-llm-specific-incidents)
- [A. Retrieval Failure](#a-retrieval-failure)
- [B. Hallucination Spike](#b-hallucination-spike)
- [C. Token Cost Spike](#c-token-cost-spike)
- [D. Abuse Detected](#d-abuse-detected)
- [5. Incident Response Checklist](#5-incident-response-checklist)

## Quick Navigation

- [Model Performance Degradation](#1-model-performance-degradation)
- [Data Pipeline Failure](#2-data-pipeline-failure)
- [API Outage / Latency Spikes](#3-api-outage--latency-spikes)
- [RAG / LLM-Specific Incidents](#4-rag--llm-specific-incidents)
- [Incident Response Checklist](#5-incident-response-checklist)

---

## 1. Model Performance Degradation

**Symptoms**

- Metrics drop
- KPI changes
- Increase in false positives/negatives

**Immediate Actions**

- Switch to fallback model or baseline
- Freeze traffic routing to new version
- Pull recent logs & slice metrics

**Root Cause Investigation**

- Check drift metrics
- Check data delays or corruption
- Check distribution shifts
- Check recent deployments

**Resolution**

- Retrain or fix data pipeline  
- Re-release stable model  

**Postmortem**

- Add monitoring gaps to backlog  

---

## 2. Data Pipeline Failure

**Symptoms**

- Missing features
- Missing partitions
- Data not updated
- Freshness alerts triggered

**Immediate Actions**

- Backfill missing data
- Trigger job retry
- Activate fallback logic (cached features)

**Root Cause Analysis**

- Orchestration logs
- DB/warehouse outages
- Schema change upstream

---

## 3. API Outage / Latency Spikes

**Symptoms**

- P99 latency up
- Error rate spike
- Dependency timeout

**Immediate Actions**

- Enable circuit breaker
- Scale replicas
- Reduce per-request max_tokens (LLM)
- Retry with exponential backoff

**Investigation**

- Check GPU/CPU usage
- Check request volume spikes
- Investigate dependency health

---

## 4. RAG / LLM-Specific Incidents

### A. Retrieval Failure

- Wrong/missing context  
- Slow vector DB  

**Actions**

- Rebuild index  
- Restart vector DB nodes  
- Reduce K or rerank window  

### B. Hallucination Spike

- Context missing  
- Prompt drift  

**Actions**

- If the spike started after a prompt, model, or index change, roll that artifact back to the
  last known-good version first; diagnose afterwards
- Route affected query types to a grounded (retrieval-backed) mode
- Tighten retrieval and trim low-value context
- Add grounding constraints
- Enforce citations
- Reduce temperature

### C. Token Cost Spike

- Spend or tokens per request above baseline; often a prompt/context change, a retry loop, or
  an agent without a step cap

**Actions**

- Find the driver first: per-endpoint and per-user token counts, retry and tool-call counts
- Cap context size and max output tokens; route eligible traffic to a cheaper model tier
- Disable non-critical LLM features; enable autoscaling limits rather than unbounded scale-out

### D. Abuse Detected

**Actions**

- Block the source, log the event with evidence, alert on-call
- Escalate critical cases through the safety runbook
  ([template](../assets/incident/template-incident-runbook-safety.md)); then patch prompts and
  filters and add the case to the regression suite

---

## 5. Incident Response Checklist

- [ ] Incident classified (severity)
- [ ] Containment applied
- [ ] Diagnosis documented
- [ ] Fix verified in lower env
- [ ] Communication sent to stakeholders
- [ ] Postmortem written
