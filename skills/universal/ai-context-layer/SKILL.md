---
name: ai-context-layer
description: "Designs agent memory that remembers users across sessions: point-in-time facts, consolidation, tenant isolation. Use when auditing long-term user memory, support KBs, or Mem0/Zep."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.6"
last_validated: 2026-09-27
---

# App Context Layer

Design and review the application layer that selects, assembles, grounds, and learns from context for a product surface. Keep operational truth in tools, APIs, SQL, or a system of record; use derived memory only for durable facts or preferences with provenance, retention, and correction paths. This skill covers architecture and runtime contracts, not repo instruction files or prompt wording.

## Quick Reference

| Question | Default | Load when needed |
|---|---|---|
| Where should operational truth live? | Tools, APIs, SQL, or system-of-record services | [context-layer-detail](references/context-layer-detail.md) |
| Is the problem retrieval or context assembly? | Use RAG for corpus retrieval; use this skill when personalization, relationships, action context, or surface bundles change the answer | [ai-rag](../ai-rag/SKILL.md), [context assembly](references/context-assembly.md) |
| Is graph worth it? | Only when relationship traversal changes the answer | [graph and relationship layer](references/graph-and-relationship-layer.md) |
| Which architecture pattern fits? | Select the smallest pattern that meets tenancy, freshness, evidence, and budget needs | [patterns catalog](references/patterns-catalog.md), [reference architectures](references/reference-architectures.md) |
| Relational, graph, or vector storage? | Use the owning database design matrix alongside the context decision | [storage paradigm selection](../software-database-design/references/storage-paradigm-selection.md) |
| Is the scenario known (personal assistant, support/CRM, coding agent, multi-agent, regulated KB, code hub, incident, procedural, voice, analytics, on-device)? | Load its playbook first: R1–R7 defaults, upgrade trigger, acceptance tests | [memory-scenario-playbooks](references/memory-scenario-playbooks.md) |
| Building or auditing a KB or memory system end to end? | Classify the workload first, then audit the seven responsibilities (admission to materialisation) one by one; when precision and coverage both matter, link current state to its evidence (P22) | [memory-responsibilities-audit](references/memory-responsibilities-audit.md) |
| Is a memory/retrieval service safe to adopt? | Keep app-owned truth, provenance, isolation, retention, and rebuild paths; compare engines by representation × output and the responsibilities they implement natively | [managed-memory boundaries](references/managed-memory-boundaries.md), [security threat model](references/security-threat-model.md), [vendor landscape](references/vendor-landscape.md#agent-memory-engines-by-representation-and-output) |

## Use This Skill When

- deciding between tools, SQL, RAG, vector search, graph, or memory for an app surface
- designing or reviewing user, customer/org, domain, action, or multi-surface context
- defining context assembly, typed contracts, freshness, ACL scope, provenance, or token budgets
- designing multimodal context or org-scale context systems, and deciding when to clear or compact context mid-session
- assessing a managed memory/retrieval product without surrendering app-owned truth

## Do Not Use This Skill For

- repo-local instruction systems such as `AGENTS.md`, `CLAUDE.md`, or `.claude/rules/`
- pure code graphs, blast-radius analysis, or multi-repo inventory
- retrieval-only tuning when the broader context architecture is already decided
- prompt shape, structured output, or few-shot authoring

Route elsewhere: retrieval, grounding, citation corpora, and retrieve-vs-preload choices -> [ai-rag](../ai-rag/SKILL.md); pgvector schemas and index builds -> [ai-vector-brain](../ai-vector-brain/SKILL.md); fine-tuning -> [ai-llm](../ai-llm/SKILL.md). Use [ai-agents](../ai-agents/SKILL.md) for agent tools/approvals/rollouts, [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md) for prompt shape, [software-ai-integration](../software-ai-integration/SKILL.md) for shipping a feature, and the `dev-context-*` skills for repo context and graphs.

## Core Workflow

1. **Classify the request.** Choose profile/personalization, memory, retrieval/grounding, relationship context, assembly, multimodal, knowledge-base ingestion, or review/build. Route pure retrieval, repo context, and agent-control work to its owner. When the scenario is known, load [memory-scenario-playbooks](references/memory-scenario-playbooks.md) first and take its stage defaults; otherwise classify the workload with [memory-responsibilities-audit](references/memory-responsibilities-audit.md).
2. **Choose the source of truth.** Keep operational facts in authoritative tools or stores. Separate derived memory, raw episodes, retrieved evidence, and user-supplied context; attach provenance, owner scope, freshness, and retention requirements.
3. **Select the smallest pattern.** Use the decision matrix in [patterns-catalog](references/patterns-catalog.md), then load only the matching reference architecture or layer deep dive. Do not preload the full stance, vendor landscape, or recipe catalog.
4. **Define contracts and lifecycle.** Specify typed projections for `EntityProfile`, `LearnedMemory`, `KnowledgeSource`, `RetrievalResult`, `ContextAssemblyRequest`, `ContextBundle`, feedback, and artifact references. Define `write`, `select`, `compress`, `isolate`, `order`, and `format` behavior for the consuming surface.
5. **Apply admission and threat gates.** Check authority, tenancy/ACL, freshness, provenance, token budget, contradiction handling, prompt-injection/poisoning risk, and deletion or rebuild paths. Keep tool permissions and human approvals in the consuming runtime; this skill does not grant them.
6. **Validate the proposed boundary.** Test retrieval/assembly quality, isolation, freshness, contradiction and erasure paths, context hygiene, and model/provider portability at the relevant evidence level. For staged memory mutations, run the [SQLite lifecycle reference](references/sqlite-memory-lifecycle.md) on disk; then test the selected engine with its actual role and configuration. Report skipped engine suites as untested. For claims that these skills improve an agent, use the [paired skills ablation](../ai-evals/references/memory-skills-ablation.md) with an independent holdout.
7. **Report completion.** State the architecture decision, contracts, assumptions, evidence, checks, unresolved unknowns, and next bounded step. Continue through implementation, inspection, and fixes until the requested local outcome is complete or a named external/runtime gate remains.

## Context Admission Gate

For every candidate item, attach the available envelope metadata: source class (`operational`, `retrieved`, `derived`, or `user-supplied`), owner scope, observed or effective time, provenance ID, and token cost. For a direct user turn, default provenance to the session and turn ID and time to receipt; do not require the user to supply system metadata. Admit an item only when the requesting surface is authorized, freshness is adequate, and it fits the surface budget after higher-authority items. Exclude it for missing metadata only when that missing field is material to authority, isolation, or freshness. Record the item ID, class, and exclusion reason; do not retain rejected raw content unless retention is explicitly authorized.

## Context Mutation

Clearing or compacting context mid-session forces the provider cache to rewrite everything after the edit point. Clear only when `cleared_tokens × read_price × remaining_turns > rewritten_suffix_tokens × (write_price − read_price)`; otherwise keep the tokens and mutate at the next task boundary. Before any compaction, pin a must-survive set and fail the compaction if a recall probe loses any pinned item. Worked example and probe: [context-hygiene](references/context-hygiene.md#context-mutation-economics). Prefix layout itself belongs to [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md#cache-aware-prompt-layout).

## Safety and Portability

- Keep model/provider choices behind vendor-neutral contracts and adapters. Re-verify context limits, cache behavior, managed-memory capabilities, and version-specific claims for the consuming model.
- Never treat raw chat, tool payloads, embeddings, or retrieved documents as trusted durable memory. Extract typed facts, preserve source episodes, and keep a correction, invalidation, erasure, and rebuild path.
- Treat tenant isolation, ACL scope, provenance, freshness, and prompt-injection defenses as runtime controls that must be tested at the relevant boundary. A prose review or local fixture does not prove production isolation; apply scope at candidate generation and run the [cross-tenant canary test](references/tenant-isolation-patterns.md#validation-and-testing) on every assembly, cache-key or filter change.
- Keep irreversible writes, external actions, and human approvals in the consuming runtime’s explicit policy. Existing authorization for the requested local work remains valid; do not repeat it unnecessarily.

## Completion Contract

A design review is complete when the selected pattern, source boundaries, typed contracts, admission rules, validation checks, evidence level, and unresolved assumptions are recorded. A build task is complete only after the changed artifact is inspected, relevant checks pass, failures are fixed, and runtime or external gates are clearly identified. Distinguish static bundle validation, local fixture evidence, runtime loading, observed routing, and production behavior.

## Navigation

- Scope and detailed route examples: [context-scope](references/context-scope.md)
- Stance, context-window failure modes, and runtime verbs: [stance-and-hygiene](references/stance-and-hygiene.md)
- Architecture flow, build kit, templates, and admission detail: [architecture-and-build](references/architecture-and-build.md)
- Full reference map, scripts, data, fact-checking, and operations: [context-navigation](references/context-navigation.md)
- Architecture model and review workflow: [context-layer-detail](references/context-layer-detail.md)
- Scenario playbooks: [memory-scenario-playbooks](references/memory-scenario-playbooks.md)
- Stack crosswalk (storage, maintenance, engine mechanisms, query modes): [memory-stack-crosswalk](references/memory-stack-crosswalk.md)
- Pattern selection: [patterns-catalog](references/patterns-catalog.md) (P4 holds the bitemporal vocabulary), [reference-architectures](references/reference-architectures.md), [architectures-by-organization](references/architectures-by-organization.md), [substrate-combinations](references/substrate-combinations.md)
- Retrieval and grounding: [retrieval-and-grounding](references/retrieval-and-grounding.md), [ai-rag](../ai-rag/SKILL.md), [just-in-time-context-loading](references/just-in-time-context-loading.md), [retrieve-vs-preload-vs-finetune](references/retrieve-vs-preload-vs-finetune.md)
- Memory and assembly: [entity-and-memory-models](references/entity-and-memory-models.md), [context-assembly](references/context-assembly.md), [semantic-caching](references/semantic-caching.md), [managed-memory-boundaries](references/managed-memory-boundaries.md), [multimodal-context-assembly](references/multimodal-context-assembly.md)
- Hygiene, threats, and evaluation: [context-hygiene](references/context-hygiene.md), [security-threat-model](references/security-threat-model.md), [evals-and-operations](references/evals-and-operations.md) (state-maintenance eval), [context-layer-scorecard](assets/eval/context-layer-scorecard.md)
- Ingestion and organisation-scale patterns: [git-anchored-ingestion](references/git-anchored-ingestion.md), [policy-and-compliance-docs](references/policy-and-compliance-docs.md), [company-brain-assembly](references/company-brain-assembly.md), [composition-with-related-skills](references/composition-with-related-skills.md)
- Persistent lifecycle implementation and adversarial cases: [sqlite-memory-lifecycle](references/sqlite-memory-lifecycle.md)
- Architecture alternatives: [architecture-patterns](references/architecture-patterns.md), [long-context-first-architecture](references/long-context-first-architecture.md), [cache-augmented-generation](references/cache-augmented-generation.md), [filesystem-as-memory](references/filesystem-as-memory.md), [operational-brain-pattern](references/operational-brain-pattern.md), [fine-tune-for-behavior-not-facts](references/fine-tune-for-behavior-not-facts.md)
- Wiki and chunking (P7): [knowledge-compilation-and-wiki-pattern](references/knowledge-compilation-and-wiki-pattern.md), [multi-source-wiki-ingestion](references/multi-source-wiki-ingestion.md), [markdown-chunking-patterns](references/markdown-chunking-patterns.md)
- Delivery surfaces: [mcp-context-delivery](references/mcp-context-delivery.md), [conversational-surfaces-cross-platform](references/conversational-surfaces-cross-platform.md), [inspection-and-review-surfaces](references/inspection-and-review-surfaces.md)
- Review aids: [anti-patterns-catalog](references/anti-patterns-catalog.md), [example-assessments](references/example-assessments.md), [agent-memory-benchmarks](references/agent-memory-benchmarks.md), [information-theory-applied](references/information-theory-applied.md)
- Build-grade work: [builds/README](builds/README.md), [builds/TUTORIAL](builds/TUTORIAL.md)
- Contracts and templates: [design templates](assets/design/context-layer-system-design.md), [review template](assets/design/context-layer-review-template.md), [contract templates](assets/contracts/context-bundle-template.md), [entity and memory contract](assets/contracts/entity-memory-contract.md), [feedback outcome contract](assets/contracts/feedback-outcome-contract.md)
- Scripts and data: [score_context_layer.py](scripts/score_context_layer.py), [check_sources.py](scripts/check_sources.py), [sources.json](data/sources.json)

## Learnings Loop

Consult relevant entries in `learnings.consolidated.md` when prior context-layer decisions or known pitfalls matter; otherwise skip it. Read raw `learnings.md` history only when a repeated failure, provenance question, or unresolved decision needs it. After applying the skill, record a dated learning only when an observed pattern or mistake is worth preserving, using `agents-skills-feedback-loop/scripts/append_learning.py`; do not modify this file.
