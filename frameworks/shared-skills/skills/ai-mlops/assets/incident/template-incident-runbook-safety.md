# Safety Incident Runbook (LLM)

Used when the model outputs unsafe, harmful, policy-violating, or privacy-leaking content.

---

## 1. Incident Details

**ID:** <id>  
**Detected by:** <filter/monitor/human>  
**Timestamp:** <timestamp>  
**Severity:** <sev1/sev2/sev3>  

---

## 2. Immediate Containment

- [ ] Block output  
- [ ] Disable model endpoint (if severe)  
- [ ] Switch to fallback model  
- [ ] Alert on-call safety engineer  

---

## 3. Diagnosis Steps

### Input review

- Inspect prompt  
- Check for injection patterns  

### Output review

- Identify unsafe text  
- Check filtering failure  

### System review

- Check logs for similar cases  
- Investigate recent prompt/model changes  

---

## 4. Resolution

- Add new blocklist patterns  
- Improve filters  
- Retrain classifier if needed  
- Patch system prompt  

---

## 5. Verification

- [ ] Re-run test suite  
- [ ] Confirm model no longer produces unsafe output  
- [ ] Validate with adversarial prompts  

---

## 6. Postmortem

Document:

- Root cause  
- Fix applied  
- Future prevention steps  
