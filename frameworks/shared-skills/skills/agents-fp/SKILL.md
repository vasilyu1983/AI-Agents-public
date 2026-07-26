---
name: agents-fp
description: "Finish with Proof — a portable execution protocol for coding agents. Use automatically for engineering work (build, change, diagnose, review, test, operate, or plan). Provides risk-matched routing (Small/Medium/Vague/Large), evidence-first diagnosis, on-demand profiles (live systems, multi-agent, provider compatibility, delegation, continuation), and verification gates. Explicit: \"FP:\" or \"$fp\". Do NOT use for casual conversation."
---

# FP — Finish with Proof

A portable execution protocol for coding agents. 77 lines. 3 core rules. On-demand profiles.

Activate automatically for engineering work; stay dormant for casual conversation.
`FP:` and `$fp` are optional explicit invocations.

## Three Core Rules

**1. Diagnose before patching.**
Gather evidence to identify root cause. Do not guess. Three non-narrowing probes → stop and switch to structural method (bisect, minimal reproduction, causal boundary trace).

**2. Verify before claiming done.**
Never say something is complete without observable evidence. Run the relevant tests. See them pass. "Implemented" is not "done." Unverified work stays unverified.

**3. Be concise and actionable.**
First line = result or current action. Last line = next concrete step or final verdict. No preamble, no filler.

## Reuse Ladder

Before creating anything: does it need to exist? → already in codebase? → standard library? → native platform? → installed dependency? → one line? → only then add minimum new code.

## Routing

Classify the whole task before decomposing. Small is NOT the default.

| Route | Trigger | Output |
|-------|---------|--------|
| **Small** | ALL of: one file, ≤5 lines, cause known, no new interface/dependency/schema | Tiny Brief + verify |
| **Medium** | Multi-file, >5 lines, or added tests; no unresolved product decision | Execution Brief + evidence |
| **Vague** | Requirements or user-owned decisions underspecified | 2-3 Idea Cards → user picks → then Medium |
| **Large** | Architectural, multi-module, breaking, migration-heavy | Decompose into risk-reducing modules |

## On-Demand Profiles

Profiles load only when the condition matches — never by default.

| Condition | Reference |
|-----------|-----------|
| Third-party proxy, gateway, retry/loop/encoding suspect | `{baseDir}/references/provider-compatibility.md` |
| Multi-agent, sub-agent, parallel writers | `{baseDir}/references/multi-agent-review-protocol.md` |
| Remote/stateful target, OpenWrt, embedded, router | `{baseDir}/references/live-system.md` |
| Unknown failure; diagnosis without fix | `{baseDir}/references/debug-incident.md` |
| Cross-session continuation, resume after compaction | `{baseDir}/references/continuation.md` |
| Delegated execution with fresh agents | `{baseDir}/references/delegated-execution.md` |
| Vague/risky/large; requirements challenge needed | `{baseDir}/references/question-requirements.md` |

## Safety

- Redact all secrets from output. Use `<REDACTED>`.
- Destructive ops need explicit boundaries and confirmation.
- Live systems: preserve management path, create rollback, verify with real client path.

## Evidence Basis

1,416 real LLM API calls across 3 models, 8 traits, 3 testing methods. v-final (77 lines) champion on GPT-5.6-Sol (3.57) and DeepSeek-v4-Pro (3.14).

Token -45%, tool calls -57%, template reads -89%.

Repo: https://github.com/MiaoY0uShan/FP
Benchmarks: https://github.com/MiaoY0uShan/FP/blob/main/benchmarks/results/ARTICLE.md