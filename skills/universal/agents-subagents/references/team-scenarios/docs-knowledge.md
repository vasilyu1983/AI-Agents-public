---
description: Docs Knowledge — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Docs Knowledge

**Typical scenario**

Your repo has READMEs, runbooks, PRDs, and notes, but nobody trusts the documentation set anymore.

**Claude prompt**

```text
Create an agent team using the installed `docs-knowledge` members.

Scenario: Rebuild trust in the docs for a multi-repo platform by cleaning README structure, turning scattered notes into retrievable context, and writing one implementation-ready PRD for the next core initiative.

Required context:
- current docs folders
- note sources
- target audience: new engineers and tech leads

Instructions:
- docs-codebase-architect proposes the durable doc structure
- docs-ai-prd-writer turns the chosen initiative into an implementation-ready PRD
- docs-notes-retrieval-curator identifies what notes should become retrievable context
- docs-quality-auditor flags stale, duplicated, or risky docs
- Keep the workflow staged and conclude with one documentation improvement plan
- Clean up the team when done
```

**Codex prompt**

```text
Run the installed docs_knowledge members as a staged flow.

Goal: restore trust in repo docs, notes, and planning docs.

Sequence:
- codebase_docs_architect: recommend doc architecture
- notes_retrieval_curator: define retrievable note sources
- ai_prd_writer: draft one implementation-ready PRD
- docs_quality_auditor: audit coverage and freshness

Return:
- target doc structure
- curated note sources
- PRD quality read
- highest-priority doc fixes
```
