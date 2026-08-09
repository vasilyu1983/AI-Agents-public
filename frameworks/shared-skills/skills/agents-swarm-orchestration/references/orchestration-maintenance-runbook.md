# Orchestration Maintenance Runbook

## Table of Contents

- [Purpose](#purpose)
- [Operating Stance](#operating-stance)
- [What To Review Monthly](#what-to-review-monthly)
- [What To Review After Any Model Catalog Change](#what-to-review-after-any-model-catalog-change)
- [Surface Selection Rules](#surface-selection-rules)
- [Fan-Out Budgeting](#fan-out-budgeting)
- [Shared-State Checks](#shared-state-checks)
- [Prompt Drift Checks](#prompt-drift-checks)
- [Loop And Schedule Hygiene](#loop-and-schedule-hygiene)
- [Verifier Discipline](#verifier-discipline)
- [Cost Smells](#cost-smells)
- [Audit Commands](#audit-commands)
- [Maintenance Workflow](#maintenance-workflow)
- [Anti-Patterns](#anti-patterns)
- [When To Update This Guide](#when-to-update-this-guide)

Use this guide to maintain multi-agent orchestration over time. This is not the place to decide whether a single task should fan out right now. This is the place to audit whether your swarm patterns are still justified, disciplined, and cost-effective.

## Purpose

Orchestration fails in two common ways:

- too little structure, so workers collide or duplicate work
- too much structure, so the swarm costs more than the problem deserves

The maintenance goal is to keep the system on the narrow path between those two failure modes.

## Operating Stance

The current best-practice stance is:

- default to one agent unless specialization materially helps
- prefer small numbers of independent workers over large broad swarms
- use teams only when direct cross-worker interaction is actually needed
- review orchestration patterns whenever provider model guidance changes

Do not treat multi-agent as a default architecture style.

## What To Review Monthly

Review these questions once per month:

- Which swarm patterns are used most often?
- Which flows consistently need more than one worker?
- Which flows repeatedly spawn unnecessary explorers, reviewers, or follow-up fixers?
- Which teams exist mostly because no one removed them after an experiment?
- Which orchestration prompts have become vague or overloaded?

If a swarm exists but no one can explain its cost or quality advantage, it should be simplified.

## What To Review After Any Model Catalog Change

Provider updates can invalidate yesterday's orchestration shape.

Re-check:

- whether a stronger single agent now replaces an old two-worker pattern
- whether a new cheap mini model makes read-only fan-out viable again
- whether built-in teammates now overlap with custom shared workers
- whether runtime controls for subagents, teams, or handoffs changed

Do not only refresh the model settings. Refresh the orchestration design assumptions too.

## Surface Selection Rules

Keep these boundaries explicit:

- use a single agent when the work is sequential, tightly coupled, or file-collision-prone
- use worker fan-out when tasks are independent and report back to one owner
- use agent teams only when members need direct back-and-forth, not just parallel reporting
- use manager or handoff patterns when routing and arbitration are the actual problem

Known trap:

- teams are often chosen because they sound more advanced, not because the work requires direct inter-agent communication

## Fan-Out Budgeting

Every reusable swarm should have an explicit budget:

- max worker count
- max retries
- max background duration
- max synthesis passes

If those limits are not written down, the swarm will grow until it becomes expensive and noisy.

Recommended default discipline:

- start with the minimum viable worker count
- add a verifier only when there is a real failure mode to catch
- avoid reviewer plus verifier plus summarizer stacks unless each one has a distinct contract

## Shared-State Checks

Audit each swarm for shared-state risk:

- Do multiple workers edit the same files?
- Do they depend on the same unstated assumptions?
- Do they re-read the same broad repo context independently?
- Do they all need the same expensive setup before any useful work starts?

If yes, collapse the flow or introduce a stronger intake artifact before dispatch.

## Prompt Drift Checks

Orchestration quality degrades when prompts drift.

Check whether your worker prompts still:

- define one role clearly
- define a bounded scope
- specify exact inputs
- specify exact outputs
- avoid hidden merge logic inside worker instructions

Known trap:

- prompts that used to be small become catch-all launch templates after repeated edits

## Loop And Schedule Hygiene

Recurring and long-lived orchestration needs stricter maintenance than ad hoc fan-out.

Review:

- whether recurring loops still need to exist
- whether scheduled swarms have stop conditions
- whether failures page the right owner
- whether the loop continues after the business reason disappeared

If a scheduled swarm cannot explain its owner, stop condition, and success metric, it is operational debt.

## Verifier Discipline

Verifiers are useful when they catch a different class of error than the worker.

Keep them only when they provide independent value.

Good verifier cases:

- contract validation
- schema or format enforcement
- policy or security review
- contradiction checking across worker outputs

Bad verifier cases:

- repeating the same prompt with a different title
- re-summarizing without a distinct acceptance contract

## Cost Smells

These are orchestration smells that usually indicate wasted spend:

- broad fan-out for a task that one agent could finish end-to-end
- automatic reviewer attachment to every task
- multiple workers collecting the same repo context independently
- large teams for narrow read-only research
- repeated launch-and-relaunch because contracts are underspecified

When you see these, fix task design before tuning models.

## Audit Commands

Use quick repository checks to spot orchestration drift.

Find the most obvious orchestration references:

```bash
rg -n "team|subagent|worker|verifier|handoff|debate|manager" \
  $(git rev-parse --show-toplevel)/frameworks/shared-skills/skills/agents-swarm-orchestration \
  $(git rev-parse --show-toplevel)/frameworks/shared-skills/skills/agents-subagents
```

Use this to review:

- whether the same scenario is documented in multiple conflicting places
- whether old patterns still point to obsolete models or runtimes
- whether team prompts and maintenance guidance still agree

## Maintenance Workflow

When updating orchestration policy, use this order:

1. review current provider guidance
2. review whether the execution surface is still correct
3. review worker counts and contracts
4. review model assignments
5. review scheduled or background loops
6. refresh the top-level skill links so operators can find the current rule

Do not start at model assignments. Bad orchestration on cheaper models is still bad orchestration.

## Anti-Patterns

- treating "more workers" as "more rigor"
- adding a verifier before defining a clean worker contract
- using teams for tasks that only need parallel reporting
- letting orchestration docs describe surfaces that the actual runtime no longer supports
- updating cost guidance without updating surface-selection guidance
- keeping experimental swarm setups after the experiment ended

## When To Update This Guide

Update this file when:

- the default orchestration surface changes
- provider guidance materially changes the economics of fan-out
- team behavior or runtime support changes
- your audit cadence or budgeting rules change

This file should stay operational and durable. Keep one-off experiments in notes, not here.
