# Context-Layer Scope and Routing Detail

This reference contains detail moved out of the skill root. Load it after the root router selects the relevant workflow; do not preload it for unrelated work.

## Contents

- [Use this skill when](#use-this-skill-when)
- [Example invocations](#example-invocations)
- [Do not use this skill for](#do-not-use-this-skill-for)

## Foundational Scope

Design and review runtime context systems that unify:

- live user and customer facts
- derived memory and preferences
- domain knowledge retrieval
- relationship-aware graph context
- surface-specific personalization bundles
- grounding, evidence, and feedback loops

This skill is for app architecture, not repo instruction files.

## Use This Skill When

- You want a reusable app knowledge layer across multiple product surfaces.
- You need to combine `user`, `customer/org`, `domain`, and `action` context.
- You are unsure whether the right answer is tools, SQL, RAG, graph, or memory.
- You want to review an existing app and judge how close it is to a mature context-layer architecture.
- You need a personalization system that is useful to both LLMs and deterministic product logic.
- You need to pick between named KB patterns (`references/patterns-catalog.md`) or compose them into a recipe (`references/reference-architectures.md`).
- You need to run an explicit anti-pattern sweep (`references/anti-patterns-catalog.md`) against an existing design.
- You need to design a human-reviewable knowledge base (wiki-style with contradiction handling, provenance, and editorial review) — see `references/knowledge-compilation-and-wiki-pattern.md` and `references/inspection-and-review-surfaces.md`.
- You need to decide whether a managed memory/retrieval product is safe to adopt without surrendering app-owned truth.
- You need to design a multimodal or file-heavy assistant where refs should load just in time instead of stuffing raw payloads into the window.
- You need to build a knowledge base from a portfolio of git repositories that stays fresh as repos update — see RA10 and the `composition-with-related-skills.md` map.
- You need to turn policies, regulator letters, control-framework mappings, runbooks, and other compliance / operational docs into authority-aware agent context with paragraph-precise citations, effective-time queries, and editorial review — see RA11 and `policy-and-compliance-docs.md`.
- You need to assemble an org-scale "company brain" that fuses lawful multi-source collectors, a pseudonymised DWH, a P7 LLM Wiki, optional risk packs, and an MCP-fronted agent read path into one auditable stack — see `references/company-brain-assembly.md` (composes a lawful collector layer + ingestion + `data-analytics-engineering` PII vault + `agents-mcp` for DWH + `ai-rag` wiki-grounded retrieval; a governed collector and risk-pack implementation, where one exists, is project-scoped).

### Example invocations

- "Use ai-context-layer to design a reusable app context system."
- "Use ai-context-layer to review this product's memory, retrieval, and personalization architecture."
- "Use ai-context-layer to decide whether this app needs tools, memory, RAG, or graph."
- "Use ai-context-layer to compare two apps and score how close they are to a mature context-layer design."

## Do Not Use This Skill For

- Repo-local agent instruction systems such as `AGENTS.md`, `CLAUDE.md`, or `.claude/rules/`.
- Pure code graphs or blast-radius analysis.
- Pure multi-repo inventory work.
- Retrieval-only tuning when the broader app context architecture is already decided.

Use related skills instead:

- [ai-rag](../../ai-rag/SKILL.md) for retrieval, grounding, chunking, reranking, and eval depth.
- [ai-agents](../../ai-agents/SKILL.md) for agent architecture, tools, approvals, and rollout controls.
- [ai-prompt-engineering](../../ai-prompt-engineering/SKILL.md) for prompt *shape* concerns — structured output, few-shot, system-prompt authoring. This skill owns the context *around* the prompt; ai-prompt-engineering owns what the prompt itself says.
- [software-ai-integration](../../software-ai-integration/SKILL.md) for shipping AI features into an application.
- [software-ios-ai-engine](../../software-ios-ai-engine/SKILL.md) when the consuming surface is iOS and the context bundle drives an on-device composer (Apple Foundation Models / sentence bank / retrieval stitch) instead of a cloud LLM. For the full four-skill composition recipe (this skill + `ai-rag` + `ai-vector-brain` + `software-ios-ai-engine`) covering Path A (Foundation Models) and Path B (vector-DB-only) for three generic conversational domain shapes, see [composition-with-rag-context-vector.md](../../software-ios-ai-engine/references/composition-with-rag-context-vector.md).
- [dev-context-engineering](../../dev-context-engineering/SKILL.md) for repo-native agent context files.
- [dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md) for repo-portfolio discovery.
- [dev-context-code-graph](../../dev-context-code-graph/SKILL.md) for symbol and file graphs.

