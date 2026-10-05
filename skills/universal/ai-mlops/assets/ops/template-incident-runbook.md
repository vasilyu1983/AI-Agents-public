# Incident Runbook for ML/LLM Systems

A general-purpose operational runbook for responding to production ML incidents.

---

## 1. Incident Overview

**Incident ID:** <ID>  
**Start Time:** <timestamp>  
**Detected By:** <monitor / alert>  
**Owner:** <team>  
**Severity:** <sev1/sev2/sev3>  

---

## 2. Symptoms

Describe what was observed:

- High latency  
- Low throughput  
- Model predictions incorrect  
- Dropped partitions  
- Spike in errors  

---

## 3. Immediate Containment

Perform within first 5 minutes:

- [ ] Stop routing traffic to impacted model  
- [ ] Roll back to previous stable version  
- [ ] Enable circuit breakers  
- [ ] Turn on safe-mode thresholds  

---

## 4. Diagnosis

Check:

### A. Data Pipeline

- Freshness  
- Volume  
- Schema changes  
- Partition outages  

### B. Model

- Prediction drift  
- Distribution changes  
- Feature parity issues  

### C. System

- GPU/CPU high load  
- Memory pressure  
- Dependency timeouts  

---

## 5. Fix Implementation

Depending on root cause:

- Patch upstream data  
- Rebuild index (LLM/RAG)  
- Redeploy model  
- Tune resource settings  
- Retry failed jobs  

---

## 6. Verification

- [ ] Metrics stable  
- [ ] Errors resolved  
- [ ] Drift cleared  
- [ ] Latency within SLO  

---

## 7. Communication

Send update to:

- Stakeholders  
- On-call  
- Incident manager  

Template:
Incident <ID> resolved at <timestamp>.
Cause: <summary>.
Fix: <summary>.
Next Steps: <summary>.

---

## 8. Postmortem

Complete within 48 hours:

- Timeline  
- Root cause  
- Corrective actions  
- Preventive actions  
