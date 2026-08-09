# Jailbreak Investigation Template

A structured workflow for investigating jailbreak attempts.

---

## 1. Event Details

**Prompt:** <redacted>  
**Time:** <timestamp>  
**User ID:** <hashed/anon>  
**Model:** <model_version>  

---

## 2. Categorize Attempt

Which type?

- Roleplay jailbreak  
- System override attempt  
- Encoded jailbreak (ROT13/Base64)  
- Multi-turn staged jailbreak  
- Emotional manipulation  
- Safety evasions  

---

## 3. Investigation Steps

1. Reproduce attack with identical inputs  
2. Inspect system prompt isolation  
3. Review input sanitization logs  
4. Analyze output filter behavior  
5. Compare to prior similar attempts  

---

## 4. Findings

Describe:

- Input flaw  
- Processing flaw  
- Guardrail deficiency  

---

## 5. Mitigation Steps

- Add or update blocklist patterns  
- Harden system prompt  
- Improve rewriting  
- Update safety classifier  
- Expand test suite  

---

## 6. Prevention

Add to:

- Red-team test suite  
- Policy documentation  
- Guardrail configs  
