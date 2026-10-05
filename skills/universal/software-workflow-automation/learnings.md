# software-workflow-automation — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] Major-version drift caught the skill flat-footed on three platforms at once: n8n had moved from the 1.x line to 2.0 (task runners on by default, Code-node env access blocked, SQLite pooled-by-default, `--tunnel` removed); Trigger.dev v3 was fully shut down 2026-07-01 (v4 is GA and collapses the old provider/coordinator/trigger-worker self-host split into one supervisor); and Hatchet reached 1.0 on 2026-04-24, retiring its "pre-1.0, accept API flux" caveat. [Correction 2026-09-23: no Hatchet 1.0 release exists — the v1 engine became default in mid-2025 while release tags remain v0.x; n8n 2.x still supports SQLite (pooled driver) with Postgres recommended, and MySQL/MariaDB support was removed.] Lesson: version-pinned platform facts in a fast-moving automation-tooling skill go stale within a single quarter — treat any "current version" claim older than ~60 days as suspect and re-verify before advising, even when the skill's own `last_validated` date looks recent.
- [2026-07-11] Langflow's ownership chain is two acquisitions deep (DataStax acquired it in 2024; IBM's acquisition of DataStax then closed), and the DataStax-hosted *managed* Langflow product was deprecated 2026-03-09 and shut down 2026-04-09 — the open-source repo continues under IBM. A skill that says "Langflow is DataStax-owned" without checking for a second acquisition layer will recommend a dead managed-hosting path.

## Open Questions

## Consolidated Principles
