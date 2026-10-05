# Adoption Metrics for AI Coding Programs

Operational guidance for measuring whether developers are actually using AI coding tools, in which mode, and with what degree of stickiness. This reference covers both assistant-style tools and coding agents.

---
## Table of Contents

- [What Adoption Measurement Should Answer](#what-adoption-measurement-should-answer)
- [The Two Funnels](#the-two-funnels)
- [Assistant Funnel](#assistant-funnel)
- [Agent Funnel](#agent-funnel)
- [Core Adoption Metrics](#core-adoption-metrics)
- [Metric Definitions](#metric-definitions)
- [Assistant vs Agent Interpretation](#assistant-vs-agent-interpretation)
- [Tool-Specific Data Sources](#tool-specific-data-sources)
- [GitHub Copilot](#github-copilot)
- [ChatGPT Enterprise / OpenAI API Usage](#chatgpt-enterprise-openai-api-usage)
- [Claude Code and Similar CLI Agents](#claude-code-and-similar-cli-agents)
- [Amazon Q Developer](#amazon-q-developer)
- [Internal Agents](#internal-agents)
- [Segmentation Rules](#segmentation-rules)
- [Stall Patterns](#stall-patterns)
- [Pattern: Seat Bloat](#pattern-seat-bloat)
- [Pattern: Completion-Only Plateau](#pattern-completion-only-plateau)
- [Pattern: Agent Curiosity Without Trust](#pattern-agent-curiosity-without-trust)
- [Pattern: Mandated Adoption with DX Backlash](#pattern-mandated-adoption-with-dx-backlash)
- [Privacy and Governance](#privacy-and-governance)
- [What to Do Next](#what-to-do-next)


## What Adoption Measurement Should Answer

Adoption is not "how many seats did we buy?" It should answer:

- who is using the tool regularly
- which capabilities they use
- whether usage is voluntary or forced
- whether usage is shallow, sticky, or expanding
- whether agent invocation is producing accepted outcomes

If adoption is weak, do not over-interpret delivery or ROI metrics.

## The Two Funnels

Use different funnels for assistants and agents.

### Assistant Funnel

```
licensed seat
  -> activated account
  -> weekly active user
  -> repeated usage across 4+ weeks
  -> feature breadth beyond autocomplete
  -> retained/accepted output
```

### Agent Funnel

```
agent access granted
  -> task submitted
  -> task runs to completion
  -> human accepts output for review
  -> PR merges
  -> low revert / low exception rate
```

Do not collapse those funnels into one "usage" number.

---

## Core Adoption Metrics

| Metric | What It Answers | Good Default Slice |
|--------|-----------------|--------------------|
| License utilization | are purchased seats active | org, team, business unit |
| WAU / MAU or active-user rate | is usage recurring | team, role, seniority band |
| Feature breadth | are teams using more than one surface | completions, chat, edit, review, agent |
| Suggestion acceptance or persistence | is inline output useful enough to keep | language, repo, editor |
| Organic usage ratio | do developers choose the tool without pressure | pilot cohort, optional vs mandated |
| Agent invocation rate | are teams actually trying autonomous flows | workflow, task type |
| Agent completion rate | does invocation turn into finished work | task type, repo, team |
| PR merge rate of AI-created work | does usage create accepted outcomes | agent, reviewer group, task type |

### Metric Definitions

**License utilization**

```
active_users / licensed_seats
```

Use a rolling 28-day window, not point-in-time daily counts.

**Feature breadth**

```
distinct_capabilities_used / capabilities_available
```

Capabilities are tool-specific. For assistants, they usually include completions, chat, edit, code review, docs, test generation. For agents, they include task execution, branch creation, test runs, PR generation, and follow-up remediation.

**Suggestion acceptance**

```
accepted_suggestions / shown_suggestions
```

Treat this as a weak signal unless you can pair it with persistence or retained-code metrics.

**Agent completion rate**

```
tasks_marked_complete / tasks_started
```

Only count "complete" when the task exits the agent workflow successfully, not when a run stops without an error.

**PR merge rate for AI-created work**

```
merged_prs / prs_created_by_tool_or_agent
```

This is often more useful than raw invocation count.

---

## Assistant vs Agent Interpretation

| Pattern | Likely Meaning | Next Check |
|---------|----------------|-----------|
| High seat utilization, low feature breadth | shallow trial behavior | onboarding, docs, workflow fit |
| High acceptance, low persistence | suggestions look good but are later removed | quality and rework metrics |
| High invocation, low completion | agents are interesting but unreliable | handoff, exception, tool stability |
| High completion, low merge rate | agents finish tasks but reviewers reject them | review burden, architecture fit |
| High adoption, flat delivery | tool used mostly on low-value work | task mix, delivery decomposition |
| High adoption, falling satisfaction | usage may be coerced or frustrating | survey, trust burden, give-up rate |

---

## Tool-Specific Data Sources

Use first-party telemetry when available. Tool docs change often, so prefer current admin/usage docs over blog posts and old API examples.

### GitHub Copilot

Default:

- use the current GitHub Copilot admin metrics documentation and dashboards
- prefer the official "About metrics for GitHub Copilot" docs for metric meanings
- treat older REST examples found in blogs and gists as potentially stale

Track:

| Metric | Use |
|--------|-----|
| active users | recurring adoption |
| engaged users by feature | breadth across completions, chat, review, etc. |
| suggestion counts and acceptance | inline relevance |
| editor / language splits | where value is concentrated |
| seat and entitlement data | procurement hygiene |

### ChatGPT Enterprise / OpenAI API Usage

For ChatGPT workspace adoption:

- use admin analytics for active users, engagement trends, and feature usage
- separate chat workspace activity from API-driven agent or tooling activity

For API-driven AI coding usage:

- attribute requests by service, repo, or workflow
- tag assistant-style requests separately from autonomous runs
- pair token usage with accepted outcomes, not just request count

Track:

| Metric | Use |
|--------|-----|
| unique active users | workspace adoption |
| conversations or sessions | recurring engagement |
| requests / tokens by workflow | operational cost and usage split |
| tasks or runs created from API integrations | agent-style automation adoption |

### Claude Code and Similar CLI Agents

Tool surfaces change quickly. Prefer local session logs, audit/billing logs, and SCM events over undocumented assumptions.

Track:

| Metric | Use |
|--------|-----|
| sessions started | top-of-funnel usage |
| tasks completed | outcome-level adoption |
| tools invoked per session | how deeply the agent is used |
| files touched or repos touched | scope of work |
| human feedback rounds | supervision overhead |
| follow-on PRs merged | accepted downstream value |

### Amazon Q Developer

Use current Amazon Q Developer docs and admin reporting, not historical CodeWhisperer naming.

Track:

| Metric | Use |
|--------|-----|
| active users | seat utilization |
| accepted suggestions | inline value |
| chat / assistant usage | breadth |
| security scan or remediation usage | workflow coverage |

### Internal Agents

For in-house agents, define the event model yourself. Minimum recommended events:

- task_created
- task_started
- task_completed
- task_failed
- human_takeover
- pr_opened
- pr_merged
- pr_reverted
- policy_exception

Without this event model, you cannot measure adoption cleanly.

---

## Segmentation Rules

Segment adoption or the averages will mislead you.

Recommended slices:

- team or org unit
- repo or service
- task type: bugfix, test, refactor, feature, incident
- tool surface: completion, chat, edit, review, agent
- seniority band
- language / stack
- optional vs mandated cohort

Avoid cross-team comparisons unless stack, task mix, and delivery environment are roughly comparable.

---

## Stall Patterns

### Pattern: Seat Bloat

Signal:

- high purchased-seat count
- falling active-user ratio
- low repeated usage

Interpretation:

- procurement got ahead of workflow value
- rollout outpaced enablement

Action:

- reclaim seats
- focus on power-user teams
- stop treating purchased seats as success

### Pattern: Completion-Only Plateau

Signal:

- lots of autocomplete usage
- almost no chat, edit, review, or agent usage

Interpretation:

- users see the tool as a typing accelerator, not a workflow tool

Action:

- teach 2-3 high-value patterns by task type
- measure breadth monthly

### Pattern: Agent Curiosity Without Trust

Signal:

- agent invocation rises
- completion or merge rate stays low

Interpretation:

- teams are curious but do not trust the output

Action:

- measure reviewer effort and handoff rate
- narrow agents to smaller task envelopes

### Pattern: Mandated Adoption with DX Backlash

Signal:

- active-user rate looks good
- satisfaction and trust fall
- give-up rate rises

Interpretation:

- usage is being driven by policy rather than value

Action:

- separate voluntary and mandated cohorts
- redesign enablement before expanding the mandate

---

## Privacy and Governance

Adoption dashboards can become surveillance systems unless you set boundaries.

Rules:

1. Report to management at team level by default.
2. Use a minimum team size of 5 before publishing named team comparisons.
3. Keep any individual-level dashboard self-service and invisible to managers.
4. State explicitly that metrics are for tooling and workflow improvement, not performance review.
5. If task-level agent data is sensitive, anonymize before analysis.

Suggested language:

> We track tool and workflow effectiveness at team level. We do not use individual AI-usage metrics for performance management.

---

## What to Do Next

- If the question is "why aren't people using the tool?", pair this file with `developer-experience-metrics.md`.
- If the question is "are agents actually helping?", go to `agent-execution-metrics.md`.
- If the question is "what outcome did adoption create?", go to `productivity-metrics.md` and `quality-metrics.md`.
