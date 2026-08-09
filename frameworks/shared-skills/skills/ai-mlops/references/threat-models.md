# ML/LLM Threat Models

A practical threat-modeling guide for ML, LLM, and RAG systems. Use during system design,
security reviews, audits, and incident response preparation.

Use this when the user needs to identify trust boundaries, attack paths, and control owners before choosing mitigations.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [1. Core Threat Categories](#1-core-threat-categories)
- [A. Prompt Injection](#a-prompt-injection)
- [B. Jailbreaking](#b-jailbreaking)
- [C. Data Leakage](#c-data-leakage)
- [D. Retrieval Injection (RAG)](#d-retrieval-injection-rag)
- [E. Model Extraction](#e-model-extraction)
- [F. Infrastructure Attacks](#f-infrastructure-attacks)
- [2. Threat Model Construction Framework](#2-threat-model-construction-framework)
- [Step 1. Identify Assets](#step-1-identify-assets)
- [Step 2. Identify Attack Surfaces](#step-2-identify-attack-surfaces)
- [Step 3. Analyze Threats](#step-3-analyze-threats)
- [Step 4. Define Controls](#step-4-define-controls)
- [3. Standard ML/LLM Threat Model Template](#3-standard-mlllm-threat-model-template)
- [4. Required Threat Scenarios to Cover](#4-required-threat-scenarios-to-cover)
- [5. Threat Model Checklist](#5-threat-model-checklist)

## Quick Navigation

- [Core Threat Categories](#1-core-threat-categories)
- [Threat Model Construction Framework](#2-threat-model-construction-framework)
- [Standard ML/LLM Threat Model Template](#3-standard-mlllm-threat-model-template)
- [Required Threat Scenarios to Cover](#4-required-threat-scenarios-to-cover)
- [Threat Model Checklist](#5-threat-model-checklist)

---

## 1. Core Threat Categories

### A. Prompt Injection
Attacker tries to override instructions or insert malicious instructions through:
- Direct prompts
- Indirect RAG-sourced content
- Hidden instructions in documents

### B. Jailbreaking
Attacker attempts to bypass safety rules:
- Roleplay
- Multi-turn trap prompting
- Encoding tricks

### C. Data Leakage
Model surfaces:
- Training data items
- Sensitive input content
- Internal system prompts or unpublished details

### D. Retrieval Injection (RAG)
Malicious documents manipulate:
- Model behavior
- Prompt content
- Context used during generation

### E. Model Extraction
Repeated queries used to:
- Reconstruct model outputs
- Steal capabilities
- Infer system instructions

### F. Infrastructure Attacks
- High-volume abuse (DoS)
- Dependency failures
- Unauthorized access
- Supply-chain poisoning (models, embeddings, packages)

---

## 2. Threat Model Construction Framework

Use these 4 steps:

### Step 1. Identify Assets
Examples:
- System prompt
- User data
- Model weights
- Logs & embeddings
- Vector DB content

### Step 2. Identify Attack Surfaces
- User input → API  
- Retrieved documents → RAG  
- Logs and monitoring pipelines  
- 3rd party model or library imports  

### Step 3. Analyze Threats
For each surface, document:
- Attack type  
- Likelihood  
- Impact  
- Required skills  

### Step 4. Define Controls
Match each threat to one or more defenses (guardrails, filters, audits).

---

## 3. Standard ML/LLM Threat Model Template

Asset: <what needs protection>
Threat: <attack technique>
Attack Surface: <where attack enters>
Risk: <low/med/high>
Controls:
<control_1>
<control_2>
<control_3>
Residual Risk: <low/med/high>

---

## 4. Required Threat Scenarios to Cover

- Unauthorized access  
- Prompt override  
- Context poisoning  
- Safety filter bypass  
- Sensitive data output  
- Document injection (RAG)  
- High-volume exploit  
- Logging of sensitive data  
- Exposed prompt templates  

---

## 5. Threat Model Checklist

- [ ] Assets enumerated  
- [ ] Attack surfaces identified  
- [ ] Threats mapped  
- [ ] Controls documented  
- [ ] Residual risks evaluated  
- [ ] Signed-off by engineering + security  
