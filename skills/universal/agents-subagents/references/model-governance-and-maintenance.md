---
description: Durable per-role model policy: audit cadence, drift checks, promotion and demotion rules.
last_verified: 2026-09-16
status: stable
---

# Model Governance And Maintenance

## Table of Contents

- [Purpose](#purpose)
- [Default Policy](#default-policy)
- [Claude-Specific Rules](#claude-specific-rules)
- [Codex-Specific Rules](#codex-specific-rules)
- [Promotion And Demotion Rules](#promotion-and-demotion-rules)
- [What To Audit Monthly](#what-to-audit-monthly)
- [What To Audit After Any Provider Update](#what-to-audit-after-any-provider-update)
- [Drift Checks](#drift-checks)
- [Maintenance Workflow](#maintenance-workflow)
- [Anti-Patterns](#anti-patterns)
- [Practical Baseline](#practical-baseline)
- [When To Update This Guide](#when-to-update-this-guide)

Use this guide when you need to change, audit, or defend the model and reasoning settings used by shared subagents. This is the maintenance runbook for both Claude Code and Codex subagent catalogs.

## Purpose

The goal is not "make every subagent cheaper." The goal is:

- keep simple work cheap
- keep hard work reliable
- avoid paying flagship-model cost for mechanical, low-ambiguity tasks
- avoid degrading reviewer and architect roles until they stop catching real mistakes

The current operating stance is:

- do not use one model tier for every role
- use role-based model selection
- use reasoning effort as a secondary lever, not the only lever
- review orchestration behavior and model settings together, because extra workers often cost more than a stronger single worker

## Default Policy

Use a role matrix, not a blanket override.

Recommended categories:

- `cheap/read-only`: searchers, context packet builders, inventory collectors, file mappers, straightforward extract-transform summarizers
- `standard/execution`: implementers, editors, focused debuggers, bounded test fixers
- `heavy/review`: reviewers, architects, security reviewers, complex migration planners, synthesis roles that reconcile conflicting evidence

Recommended default stance:

- narrow mechanical workers should be the first candidates for the cheapest tier in the active catalog (read the provider's models overview for which model that is); read-only review and research can still require critical judgment
- execution workers use the selected platform policy below; validate outcome quality before generalizing that model and effort combination
- reviewer and architect roles should be downgraded only after they prove they still catch regressions at the same quality bar

For Codex and Claude, the operator's tier policy (model and effort per tier, the general fallback, the main agent, and the concurrency cap) is read from [data/model-policy.json](../data/model-policy.json); do not restate it here. Before changing it, read the provider's models guide and pricing page for current models and rates, then decide per tier on your own task outcomes and rework. Explicit agent fields override the corresponding fallback fields; the fallback does not flatten the pinned role tiers. The policy reflects the operator's explicit preference, not a measured optimum or a provider mandate: no equivalence between a stronger model at low effort and a weaker one at high effort is established until your evals show it, and maximum effort can raise latency and reasoning-token use. Runtime configuration and agent files apply the policy; user-authorized changes should update those artifacts together rather than treating the validator as an independent reason to select a model.

## Claude-Specific Rules

Primary levers:

- per-agent `model` frontmatter
- global `CLAUDE_CODE_SUBAGENT_MODEL`
- launch discipline so the runtime is not flooded with unnecessary workers

Preferred maintenance rule:

- use `CLAUDE_CODE_SUBAGENT_MODEL` only as a global floor or temporary safety rail
- pin exceptional roles explicitly in agent files when they need stronger or weaker models than the global default
- do not leave the system in a state where the global override silently masks bad per-role definitions

This repository has one explicit exception: `data/model-policy.json` allowlists
the operator's selected models as deliberate global subagent overrides (read the file for which). The effective-runtime
audit accepts only those exact declared models and still verifies the underlying
per-tier catalog. Any other global override remains a failing, value-withheld
configuration drift signal. The allowlist records operator choices, not measured quality;
review cost and task outcomes before choosing another override.

Known trap:

- a global cheaper override looks clean, but it hides whether the role catalog itself is well designed

## Codex-Specific Rules

Primary levers:

- per-agent `model`
- `model_reasoning_effort`
- optionally `plan_mode_reasoning_effort`
- `model_verbosity`
- profile-level defaults

Preferred maintenance rule:

- tune `.toml` role definitions first
- use profile defaults as the broad platform baseline
- reserve global parent-session changes for deliberate platform-wide changes, not subagent-only intent

Known traps:

- lowering the parent config and assuming only subagents changed
- treating the flagship tier plus `medium` as the final optimization when the better move may be a smaller model for narrow roles
- changing reasoning effort without checking whether the role was actually over-scoped

## Promotion And Demotion Rules

Promote a role when the user deliberately chooses a higher quality baseline, or when one of these is repeatedly true:

- it misses important edge cases in review
- it fails to reconcile conflicting evidence
- it produces unstable plans for the same class of work
- human cleanup cost is higher than the model-cost savings

Demote a role to a smaller model or lower reasoning only when all of these are true:

- the work is narrow and repeatable
- the role rarely needs repo-wide synthesis
- failures are cheap to detect
- there is a clear acceptance contract or artifact template

Do not demote just because the role runs often. High-frequency roles are sometimes exactly the ones that need stronger quality controls.

## What To Audit Monthly

Review these questions once per month or after any noticeable usage spike:

- Which roles are used most often?
- Which roles are read-only versus write-heavy?
- Which roles routinely hand back weak output that then gets reworked by another agent?
- Which roles are frequently launched together even though one could absorb the work?
- Which roles use a strong model but almost never perform strong-model work?

If you cannot answer these questions, the problem is governance and observability before it is model cost.

## What To Audit After Any Provider Update

Re-check these items whenever OpenAI or Anthropic updates their model lineup or guidance:

- whether a newly released low-cost tier is now good enough for explorer or researcher roles, and whether the current cheap tier in `data/model-policy.json` is still served (check the provider's deprecation page)
- whether flagship defaults changed for code review or long-context synthesis
- whether new built-in subagents overlap with your custom shared roles
- whether the runtime now exposes new controls for subagent-only routing

Do not assume a previous "best" model matrix is still correct after a catalog refresh.

## Drift Checks

Run a simple audit over the shared agent files whenever you change defaults.

For Codex `.toml` roles:

```bash
rg -n '^(model|model_reasoning_effort|plan_mode_reasoning_effort)\s*=' \
  "$(git rev-parse --show-toplevel)/skills/universal/agents-subagents/assets"
```

For Claude agent markdown frontmatter:

```bash
rg -n '^model:\s' \
  "$(git rev-parse --show-toplevel)/skills/universal/agents-subagents/assets"
```

Use these checks to confirm:

- there are no accidental `high` holdouts after a bulk downgrade
- reviewer and architect roles that should remain stronger are still explicitly pinned
- canonical members and repository team recipes do not drift apart

## Maintenance Workflow

When you change shared subagent settings, follow this order:

1. classify roles by job shape: read-only, execution, review, synthesis
2. decide whether the change is role-scoped, team-scoped, or platform-wide
3. update the actual agent definitions, not just the parent runtime config
4. audit for drift across canonical members and repository team recipes
5. refresh linked docs if the operating rule changed
6. verify that orchestration guidance still matches the new role matrix

Do not skip step 6. Cheap agents used in an undisciplined swarm are still expensive.

## Anti-Patterns

- setting every shared agent to the same flagship model and calling it governance
- setting every shared agent to the same cheaper model and calling it optimization
- using reasoning effort as the only cost lever
- changing team YAMLs and assuming runtime behavior changed
- documenting a model matrix in prose without aligning the actual agent files
- downgrading reviewers before explorers

## Practical Baseline

If you need a stable starting point:

- keep review, architecture, and security roles on the strongest justified lane
- move narrow search and extraction roles first when reducing cost
- apply the role matrix in `data/model-policy.json`; change effort when task outcomes justify it
- treat the lowest-cost tier in the active catalog as the primary candidate for low-risk read-only roles; read the tier-to-model mapping from `data/model-policy.json` and the current lineup from the provider's models overview
- check whether the cheap-tier model supports effort at all (a model absent from the effort table does not, so the saving comes from the model choice alone) and read its retirement date on the provider's deprecation page; name a fallback before that date

## When To Update This Guide

Update this file when:

- the default subagent model policy changes
- the supported model catalog changes materially
- new built-in workers make custom shared roles redundant
- your audit cadence or drift checks change

Do not store temporary one-off experiments here. This file is for durable operating policy.
