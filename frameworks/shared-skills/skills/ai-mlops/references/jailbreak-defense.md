# Jailbreak Defense Playbook

A collection of hardened patterns to prevent safety bypass attempts.

---

## 1. Jailbreak Attack Patterns (Know What to Block)

- Roleplay (“Pretend you are an unrestricted AI…”)  
- Multi-turn setup (“In the next message, ignore all rules…”)  
- Obfuscation (base64, emoji encoding, ROT13)  
- Emotional pressure  
- Inversion (“Explain why it is NOT safe to…”)  
- Prompt decomposition (“I know you cannot do X. But hypothetically…”)  

---

## 2. Defense Mechanisms

### A. Safety-Constrained System Prompt

You cannot follow instructions that lead to harmful, unsafe, or restricted behavior.

### B. Forced Refusal Templates

I cannot comply with this request.
Use standardized refusal messages to avoid leakage.

---

### C. Output Filtering

- Scan outgoing text for unsafe categories  
- Reject & regenerate when needed  
- Use ensemble filters (regex + classifier + LLM)

---

### D. Safe Decode

- Block unsafe tokens  
- Maintain slur/sensitive token blacklist  
- Lower sampling freedom (temperature ≤ 0.5)

---

### E. Multi-Turn Memory Protection

- Strip unsafe context from past turns  
- Sanitize user inputs before storing in history  

---

## 3. Jailbreak Defense Checklist

- [ ] Safety rules explicit  
- [ ] Refusal templates installed  
- [ ] Output filter active  
- [ ] History sanitization active  
- [ ] Safe decode enabled  
- [ ] Logs for jailbreak attempts stored  
