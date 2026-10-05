# ML/LLM Threat Model Index

Use during design reviews, audits and incident preparation to name trust boundaries, attack paths and the owner of each control. Detailed defenses live with their owners below; this file is the map.

## Build The Model In Four Steps

1. **Assets:** system prompt and tool definitions, user data, model weights, logs and traces, embeddings and vector-store content, credentials the system holds.
2. **Attack surfaces:** user input, retrieved documents, tool outputs, logs and monitoring pipelines, third-party models and packages, the public inference API.
3. **Threats per surface:** attack type, likelihood, impact, attacker skill needed.
4. **Controls and residual risk:** at least one control per threat, an owner, and the residual risk after it. Sign off with engineering and security.

Record each row as: asset, threat, surface, risk, controls, residual risk.

## Threats And Where The Controls Live

| Threat | Enters through | Control owner |
|--------|---------------|---------------|
| Prompt injection (direct and indirect), jailbreaks, multi-turn escalation | User input, retrieved text, tool output | Design and layered guardrails: [ai-agents guardrails-implementation](../../ai-agents/references/guardrails-implementation.md). Testing: [qa-agent-testing prompt-injection-testing](../../qa-agent-testing/references/prompt-injection-testing.md) |
| Unauthorized tool use, runaway plans, cross-user state leakage, cascading side effects | Agent plans and tools | [ai-agents guardrails-implementation](../../ai-agents/references/guardrails-implementation.md#layer-3-execution-guardrails) |
| Unsafe or leaking output (PII, secrets, system prompt) | Model output | [ai-agents guardrails-implementation](../../ai-agents/references/guardrails-implementation.md#layer-4-output-filtering), [privacy-protection.md](privacy-protection.md) |
| Retrieval injection, corpus poisoning, cross-tenant retrieval, metadata manipulation | Documents and index | [ai-rag security-red-team-cases](../../ai-rag/references/security-red-team-cases.md) |
| Model extraction and query abuse | Public inference API | [extraction-defense.md](extraction-defense.md) |
| Poisoned models, packages, drivers and index snapshots | Supply chain | [software-security-appsec supply-chain-security](../../software-security-appsec/references/supply-chain-security.md#ml-model-and-data-artifacts) |
| Sensitive data in logs and traces | Monitoring pipeline | [privacy-protection.md](privacy-protection.md), [governance-checklists.md](governance-checklists.md) |
| Safety regressions between releases | Model, prompt or provider change | [safety-evaluation.md](safety-evaluation.md) |

## Scenarios Every Model Must Cover

Unauthorized access; instruction override; context poisoning; safety-filter bypass; sensitive data in output; document injection; high-volume abuse; sensitive data in logs; exposed prompt templates and tool definitions.

## Checklist

- [ ] Assets and attack surfaces enumerated
- [ ] Each threat mapped to a control with a named owner
- [ ] Residual risk recorded per threat
- [ ] Signed off by engineering and security
