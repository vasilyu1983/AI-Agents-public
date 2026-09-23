# AGENTS.md Inclusion Checklist

Use this review before adding a line to `AGENTS.md` or a nested instruction
file. Project memory is a small operating contract for repeatable mistakes;
it is not a task diary, tool manual, or second configuration file.

## Table of Contents

- [Four editorial tests](#four-editorial-tests)
- [Worked decisions](#worked-decisions)
- [Compact file map](#compact-file-map)
- [Final pass](#final-pass)

## Four editorial tests

### 1. Necessary and non-obvious

- Keep a line when it prevents a plausible or observed high-impact wrong action
  caused by a boundary an agent cannot easily infer.
- If code, tests, config, or the README exposes the fact, link to that source
  or remove the duplicate.
- Preserve the exception, boundary, or source-of-truth relationship; omit
  ordinary detail. A prior incident is evidence, not a prerequisite.

### 2. Durable

- Prefer guidance that remains true across ordinary refactors, sessions, and
  model updates.
- Move versions, counts, temporary workarounds, open questions, and task
  progress to the owning release note, issue, plan, or runbook.
- If a changing fact earns a signpost, name its owner and add a last-verified
  date or a check that exposes staleness.

### 3. Scoped and actionable

- Name the directory, file pattern, action, or condition; a nested file is
  often better than a broad root rule.
- State the observable action and verification concisely. Prefer a positive
  example over a slogan or a long `Do not` list.
- Keep a concise, successfully verified command when it protects a high-impact
  boundary; link to the full procedure elsewhere.

### 4. Correct owner

Put the rule where the next agent can discover it and act on it:

| Question | Owner |
| --- | --- |
| Repo workflow, non-obvious boundary, or durable convention? | `AGENTS.md` or a narrower scoped instruction file |
| Sandbox, approval, command allow/deny, model, MCP, or other capability? | Runtime configuration, permission profile, or executable rules |
| Current intent, acceptance criteria, rollout decision, or temporary exception? | User turn, issue/PR, plan, or runbook |
| Behavior, interface, path, or generated-file relationship encoded in the repo? | Code, config, tests, or canonical document |

Current user direction has precedence over standing project memory within the
host's rules. `AGENTS.md` may describe a workflow boundary, but cannot grant
permissions or override runtime policy.

## Worked decisions

These examples are illustrative; check every path and command before reuse.

| Decision | Example | Placement and rationale |
| --- | --- | --- |
| Keep | `packages/api-client/generated/` is committed output from `schema/openapi.yaml`; edit the schema, run `pnpm codegen`, regenerate output, run the package contract test, and do not edit generated files directly. | Keep in that package's instructions when the source/output boundary and required check are not visible from the generated file. |
| Move | “The agent may run deploy commands without asking.” | Put capability and approval policy in trusted host configuration or command policy. Memory does not authorize changing runtime policy; follow the explicitly authorized configuration scope. |
| Move | “The migration is paused until the data backfill is complete.” | Put task state in the issue, plan, or runbook with an owner and end condition; it becomes stale when intent changes. |
| Remove | “Use TypeScript interfaces from `src/types/` for API responses.” | Remove when compiler, lint, or existing code already enforces it; retain only an exception those checks do not reveal. |

The Keep example captures a non-obvious source-of-truth boundary. A concise
verified gate can also stay in memory: “From `frameworks/shared-skills/`, run
`python3 scripts/graph-export.py` and the scoped validators; the generated
catalog must match skill bodies.” Link detailed flags to the owning runbook.
Do not turn this into a universal “always plan, ask, or spawn” rule.

## Compact file map

Use a small map when agents repeatedly edit the wrong owner. Each row answers
*where*, *why*, and *how to detect drift*:

```markdown
| Path | Owns the non-obvious fact | Freshness/path check |
| --- | --- | --- |
| `packages/api-client/` | schema and generated-client boundary | `test -d packages/api-client` |
| `scripts/verify-contracts.py` | contract gate named above | `git ls-files --error-unmatch scripts/verify-contracts.py` |
```

Before publishing a row, resolve paths from the repository root, run each
check, and confirm the command or owner exists. Link to the canonical source
for details; delete rows that only restate directory names and refresh rows
when the owner or check changes.

## Final pass

- [ ] The line prevents a specific, non-obvious repeat or high-impact mistake.
- [ ] It is durable, scoped, and written as an observable action.
- [ ] Its path, command, owner, and source-of-truth claims were checked.
- [ ] Permissions/configuration and temporary task state live in their owners.
- [ ] A shorter pointer or repository check cannot replace the needed boundary.

This checklist is an original local synthesis informed by Daniel Vaughan,
*Agentic Coding with OpenAI Codex CLI*, chapter 4, and official OpenAI
guidance: [Best practices](https://learn.chatgpt.com/guides/best-practices),
[Codex skills](https://developers.openai.com/codex/skills), and [agent
approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security).

Local validation covers the reference, links, and skill packaging; recheck
vendor behavior before publishing platform-specific claims.
