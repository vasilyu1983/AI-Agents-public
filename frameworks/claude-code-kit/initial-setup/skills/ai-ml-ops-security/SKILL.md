---
name: ai-ml-ops-security
description: >
  Operational patterns for ML/LLM/RAG security (modern defense-in-depth): multi-layered defenses
  (90%+ bypass rate for single-layer), prompt injection mitigation, jailbreak resistance,
  adaptive attack defense, AI-powered guardrails (Llama Prompt Guard 2), privacy protection,
  RAG injection hardening, continuous monitoring. Emphasizes evolving defenses and operational safeguards.
---

# ML Security, Privacy & Safety – Quick Reference

This skill provides **practical, implementable safeguards** for production ML/LLM systems:

- **Multi-layered defense** (single-layer defenses have 90%+ bypass rates)
- **Prompt injection & RAG injection** mitigation with modern guardrails
- **Jailbreak resistance** using adaptive detection (Layer-Specific Editing)
- **Data privacy** patterns (PII handling, anonymization, differential privacy)
- **AI-powered guardrails** (Llama Prompt Guard 2, toxicity detection)
- **Supply chain security** (SBOM, signing, vulnerability scanning)
- **Output filtering** with safety classifiers and LLM post-filters
- **Agentic security** (tool governance, human oversight, auditability)
- **Continuous monitoring** with incident response playbooks

**Critical Insight:** Defense must evolve alongside adversarial creativity; static filtering offers only limited protection.

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Prompt Injection Defense | Llama Prompt Guard 2, structured interfaces | `guard.classify()`, input validation | Detecting and blocking injection attempts |
| PII Detection | Microsoft Presidio, regex | `analyzer.analyze()`, custom patterns | Identifying and redacting sensitive data |
| Output Filtering | Safety classifiers, LLM Guard | `classifier.predict()`, content moderation | Blocking unsafe/harmful outputs |
| Jailbreak Detection | Fine-tuned classifiers, LED | Pattern matching, model hardening | Detecting bypass attempts |
| RAG Security | Document sanitization, metadata filtering | HTML/JS stripping, source validation | Preventing retrieval injection |
| Supply Chain Security | Syft, Cosign, SBOM tools | `cosign sign`, `syft scan` | Artifact integrity and vulnerability scanning |
| Governance Audits | Audit templates, compliance checklists | Risk assessment, model cards | SOC2, GDPR, HIPAA compliance |
| Agentic Security | Tool governance, approval workflows | Rate limits, human-in-loop | Securing autonomous agent systems |
| Incident Response | Runbooks, logging | Alert routing, forensic analysis | Handling security breaches |

---

## When to Use This Skill

Claude should invoke this skill when the user asks:

- "How do I prevent prompt injection?"
- "How do we secure our RAG pipeline?"
- "Design LLM safety filters"
- "Detect jailbreak attempts"
- "Help write a safety audit checklist"
- "Protect training data / user data / PII"
- "Mitigate data leakage or model extraction"
- "Secure agentic AI systems with tool governance"
- "Implement supply chain security for ML artifacts"

If the user instead asks for:

- **Deployment/serving** → use `ai-ml-ops-production`
- **Prompting/fine-tuning** → use `ai-llm-development`
- **RAG design** → use `ai-llm-rag-engineering`
- **Serving performance** → use `ai-llm-ops-inference`

---

## Decision Tree: Choosing Security Defense

```text
User needs to secure: [ML/LLM System]
    ├─ Prompt Injection?
    │   ├─ LLM inputs? → Multi-layer defense (Llama Prompt Guard 2 + structured interfaces + system prompt hardening)
    │   ├─ RAG documents? → Document sanitization + metadata filtering + grounding constraints
    │   └─ Multimodal inputs? → Validate all modalities (images can hide instructions)
    │
    ├─ Data Privacy?
    │   ├─ PII in training data? → Detection + redaction (Presidio) + differential privacy
    │   ├─ User data logging? → Data minimization + anonymization + access controls
    │   └─ GDPR/HIPAA compliance? → Governance templates + audit trails
    │
    ├─ Output Safety?
    │   ├─ Harmful content? → Safety classifiers + toxicity detection + refusal templates
    │   ├─ Jailbreak attempts? → Layer-specific editing (LED) + pattern blocking
    │   └─ Data leakage? → Output filtering + watermarking + rate limiting
    │
    ├─ RAG Security?
    │   ├─ Poisoned documents? → Source validation + chunk sanitization + integrity checks
    │   └─ Injection via retrieval? → Grounding constraints + context isolation
    │
    ├─ Supply Chain?
    │   ├─ Model integrity? → SBOM + signing + hash verification
    │   └─ Dependency vulnerabilities? → CVE scanning + pinned hashes
    │
    ├─ Agentic Systems?
    │   ├─ Tool misuse? → Tool governance + approval workflows + rate limits
    │   └─ Runaway loops? → Step/time caps + watchdog + human oversight
    │
    └─ Governance?
        ├─ Risk assessment? → Threat modeling + model cards + audit checklists
        └─ Incident response? → Runbooks + containment + forensic logging
```

---

## Core Security Patterns Overview

This skill provides **11 comprehensive security patterns** organized into detailed guides:

### Threat Intelligence & Planning

**Pattern 1: ML/LLM Threat Modeling**
→ See [Threat Models](resources/threat-models.md)

- Threat categories (prompt injection, jailbreaking, data leakage, model extraction)
- Threat model construction framework (4-step process)
- Asset identification and attack surface mapping
- Control definition and residual risk assessment

### Input & Prompt Security

**Pattern 2: Prompt Injection Defense (Modern Multi-Layered)**
→ See [Prompt Injection Mitigation](resources/prompt-injection-mitigation.md)

- **Critical:** Single-layer defenses bypassed at 90%+ rates
- Multi-layer defense strategy (7 layers minimum)
- AI-powered guardrails (Llama Prompt Guard 2)
- System prompt hardening and context isolation
- Continuous monitoring with adaptive defenses

**Pattern 3: Jailbreak Resistance**
→ See [Jailbreak Defense](resources/jailbreak-defense.md)

- Constraint reinforcement in system prompts
- Adversarial pattern blocking (regex, embeddings)
- Refusal shaping with template responses
- Layer-Specific Editing (LED) fine-tuning for inherent resistance

### Data & Privacy Protection

**Pattern 4: Data Privacy Protection**
→ See [Privacy Protection](resources/privacy-protection.md)

- PII detection and redaction (Microsoft Presidio)
- Differential privacy for training data
- Data minimization and anonymization strategies
- Access control and masked views

**Pattern 5: Supply Chain & Artifact Integrity**
→ See [Supply Chain Security](resources/supply-chain-security.md)

- SBOM generation and artifact signing (Cosign, Syft)
- Dependency scanning (pip-audit, Snyk, Safety)
- Model and embedding hash verification
- Driver/runtime attestation and registry hygiene

### Retrieval & RAG Security

**Pattern 6: RAG Security Hardening**
→ See [RAG Security](resources/rag-security.md)

- Document sanitization (HTML/JS stripping)
- Metadata filtering and source validation
- Guarded chunk ingestion with validation
- Grounding constraints in prompts
- Output grounding validation

### Output & Response Security

**Pattern 7: Model Output Filtering**
→ See [Output Filtering](resources/output-filtering.md)

- Multi-layer filtering (classifiers, rules, LLM post-filters)
- Safety classifiers (OpenAI Moderation, Perspective API, Azure Content Safety)
- PII and banned word detection
- Composite safety scoring with escalation

### Testing & Validation

**Pattern 8: Safety Evaluation**
→ See [Safety Evaluation](resources/safety-evaluation.md)

- Adversarial prompt testing (harmful requests)
- Jailbreak test suites (DAN, role-play, encoding)
- Toxicity benchmarks (Perspective API, Detoxify)
- PII leakage tests and training data extraction
- RAG injection testing

### Model Protection

**Pattern 9: Model Extraction Defense**
→ See [Extraction Defense](resources/extraction-defense.md)

- Rate limiting and query similarity tracking
- Repetitive probing pattern detection
- Output watermarking for attribution
- Noise injection and throttling
- Logit hiding (only return top prediction)

### Governance & Compliance

**Pattern 10: Governance & Compliance**
→ See [Governance Checklists](resources/governance-checklists.md)

- Data retention policies and audit trails
- Explainability requirements and model cards
- Risk assessment frameworks (SOC2, GDPR, HIPAA)
- Monitoring for harmful outputs
- Fail-safe behaviors

### Agentic AI Security

**Pattern 11: Agentic Trust & Human Oversight**
→ See [Agentic Security](resources/agentic-security.md)

- Tool governance (allowlists, approval workflows, rate limits)
- Plan and step caps with watchdog monitoring
- Full auditability (logs for every plan, tool call, approval)
- Safety layering (input/output filters, state isolation, memory pruning)
- Human-in-the-loop for sensitive tasks

### Incident Management

**Pattern 12: Incident Response (Safety/Security)**
→ See existing templates in `templates/incident/`

- Incident types and detection
- Containment and diagnosis procedures
- Resolution and communication protocols
- Prevention and continuous improvement

---

## Resources (Detailed Guides)

For comprehensive operational patterns, see:

**Core Security:**

- **[Threat Models](resources/threat-models.md)** - ML/LLM threat modeling frameworks, attack surfaces, control mapping
- **[Prompt Injection Mitigation](resources/prompt-injection-mitigation.md)** - Multi-layer defense, guardrails, system prompt hardening
- **[Jailbreak Defense](resources/jailbreak-defense.md)** - Attack patterns, constraint reinforcement, LED fine-tuning
- **[Privacy Protection](resources/privacy-protection.md)** - PII detection, differential privacy, data minimization
- **[Supply Chain Security](resources/supply-chain-security.md)** - SBOM, signing, CVE scanning, artifact integrity

**Advanced Defenses:**

- **[RAG Security](resources/rag-security.md)** - Document sanitization, metadata filtering, grounding validation
- **[Output Filtering](resources/output-filtering.md)** - Safety classifiers, rule-based filters, LLM post-processing
- **[Safety Evaluation](resources/safety-evaluation.md)** - Adversarial testing, jailbreak suites, toxicity benchmarks
- **[Extraction Defense](resources/extraction-defense.md)** - Rate limiting, watermarking, query pattern detection

**Governance & Operations:**

- **[Governance Checklists](resources/governance-checklists.md)** - Compliance frameworks, audit templates, model cards
- **[Agentic Security](resources/agentic-security.md)** - Tool governance, human oversight, plan validation

---

## Templates

Use these as copy-paste starting points for security implementations:

### Guardrails & Filtering

- **[Guardrail config](templates/safety/template-guardrail-config.md)** - Multi-layer input/output filtering
- **[Output filter](templates/safety/template-output-filter.md)** - Safety scoring and content moderation
- **[Safety prompt](templates/safety/template-safety-prompt.md)** - System prompt hardening patterns

### Privacy

- **[PII handling](templates/privacy/template-pii-handling.md)** - Detection, redaction, anonymization
- **[Data anonymization](templates/privacy/template-data-anonymization.md)** - Differential privacy, data masking

### Governance & Audits

- **[Risk assessment](templates/governance/template-risk-assessment.md)** - ML/LLM security risk assessment
- **[Security audit](templates/governance/template-security-audit.md)** - Comprehensive audit checklist
- **[Policy checklist](templates/governance/template-policy-checklist.md)** - Compliance validation

### Incident Response

- **[Incident runbook](templates/incident/template-incident-runbook-safety.md)** - Safety incident procedures
- **[Jailbreak investigation](templates/incident/template-jailbreak-investigation.md)** - Investigation playbook

## Navigation

**Resources**
- [resources/jailbreak-defense.md](resources/jailbreak-defense.md)
- [resources/governance-checklists.md](resources/governance-checklists.md)
- [resources/safety-evaluation.md](resources/safety-evaluation.md)
- [resources/threat-models.md](resources/threat-models.md)
- [resources/prompt-injection-mitigation.md](resources/prompt-injection-mitigation.md)
- [resources/supply-chain-security.md](resources/supply-chain-security.md)
- [resources/privacy-protection.md](resources/privacy-protection.md)
- [resources/output-filtering.md](resources/output-filtering.md)
- [resources/rag-security.md](resources/rag-security.md)
- [resources/extraction-defense.md](resources/extraction-defense.md)
- [resources/agentic-security.md](resources/agentic-security.md)

**Templates**
- [templates/privacy/template-data-anonymization.md](templates/privacy/template-data-anonymization.md)
- [templates/privacy/template-pii-handling.md](templates/privacy/template-pii-handling.md)
- [templates/safety/template-guardrail-config.md](templates/safety/template-guardrail-config.md)
- [templates/safety/template-output-filter.md](templates/safety/template-output-filter.md)
- [templates/safety/template-safety-prompt.md](templates/safety/template-safety-prompt.md)
- [templates/governance/template-risk-assessment.md](templates/governance/template-risk-assessment.md)
- [templates/governance/template-policy-checklist.md](templates/governance/template-policy-checklist.md)
- [templates/governance/template-security-audit.md](templates/governance/template-security-audit.md)
- [templates/incident/template-jailbreak-investigation.md](templates/incident/template-jailbreak-investigation.md)
- [templates/incident/template-incident-runbook-safety.md](templates/incident/template-incident-runbook-safety.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## External Resources

See [data/sources.json](data/sources.json) for:

- **Safety toolkits:** OpenAI Moderation API, Anthropic Claude safety features, Azure Content Safety
- **PII detection:** Microsoft Presidio, spaCy NER, AWS Comprehend
- **Guardrail frameworks:** NeMo Guardrails, Guardrails AI, LLM Guard, Llama Guard 2
- **Jailbreak research:** Garak, PyRIT, PromptInject, adversarial prompt datasets
- **Governance:** SOC2, ISO27001, NIST AI RMF, EU AI Act, model card templates
- **RAG security:** LangChain security guides, vector DB security best practices
- **Differential privacy:** Opacus (PyTorch), TensorFlow Privacy, PySyft
- **Red teaming:** Microsoft AI Red Team, MITRE ATLAS framework
- **Monitoring:** Arize AI, WhyLabs, Fiddler AI, Evidently AI

---

## Related Skills

For adjacent topics, reference these skills:

- **[ai-llm-development](../ai-llm-development/SKILL.md)** - Fine-tuning with safety alignment, prompt engineering for safety
- **[ai-llm-engineering](../ai-llm-engineering/SKILL.md)** - Agentic workflows with safety guardrails, multi-agent orchestration
- **[ai-llm-rag-engineering](../ai-llm-rag-engineering/SKILL.md)** - RAG pipeline security, document sanitization, grounding
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Prompt injection patterns, system prompt hardening
- **[ai-ml-ops-production](../ai-ml-ops-production/SKILL.md)** - Production deployment with security monitoring, incident response
- **[ai-llm-ops-inference](../ai-llm-ops-inference/SKILL.md)** - Secure model serving, rate limiting, extraction defense
- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** - Data privacy in ML pipelines, bias detection and fairness

---

## Usage Notes

**When to apply this skill:**

- User explicitly asks about security, privacy, or safety
- System involves LLM/RAG with user-generated content
- Production deployment requires compliance (SOC2, GDPR, HIPAA)
- Agentic systems with tool execution
- High-risk applications (financial, healthcare, legal)

**Multi-layer defense philosophy:**

- Always combine ≥3 layers (input filter + guardrail + output filter minimum)
- Static defenses are insufficient; use adaptive monitoring
- Test defenses with adversarial suites before deployment
- Continuous monitoring detects novel attacks

Use this skill to **harden ML/LLM systems against adversarial attacks and ensure responsible AI deployment**.
