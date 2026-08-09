# Metrics & Optimization

## Table of Contents

- [Contents](#contents)
- [Metric Design Rules](#metric-design-rules)
- [Core Metrics](#core-metrics)
- [AI-Specific Metrics](#ai-specific-metrics)
- [Instrumentation Patterns](#instrumentation-patterns)
- [ROI Modeling](#roi-modeling)
- [Optimization Loop](#optimization-loop)

Measurement framework for help centers, support AI, and AI-consumable docs.

## Contents

- Metric design rules
- Core metrics
- AI-specific metrics
- Instrumentation patterns
- ROI modeling
- Optimization loop

## Metric Design Rules

- Define the outcome before the metric.
- Use the organization's own support-cost and resolution definitions.
- Separate search success from issue resolution.
- Separate AI containment from successful resolution.
- Do not use fixed benchmark numbers unless they are freshly verified and relevant to the user's context.

## Where Deflection Targets Backfire

Deflection rate and containment rate are the metrics most likely to be gamed, and a target set on them alone will get hit in ways that hurt the customer. This is the single most important judgment call in help-center measurement.

Failure patterns to watch for:

- **Hidden contact paths.** Teams under a deflection target quietly remove or bury the "contact support" link so users cannot escalate, mistaking suppressed contact volume for resolved issues. Deflection went up; resolution did not.
- **Confident non-answers.** An AI assistant tuned to minimize escalations learns to give a plausible-sounding answer rather than say "I don't know" or hand off — containment rises while unresolved-intent and reopen-after-AI quietly rise with it.
- **Friction-as-deflection.** Adding steps before a contact form (long FAQ gauntlets, forced search before a ticket can be filed) reduces contact volume without improving the underlying self-service experience; it selects for user persistence, not for resolution.
- **Survivorship in feedback.** Users who got a bad self-service experience and gave up do not appear in helpfulness ratings or reopen data — they simply churn or go to a competitor's community forum. A clean-looking deflection curve can coexist with rising silent attrition.

Guardrail: never report deflection or containment without a paired resolution-quality metric (reopen rate, escalation-after-view, CSAT on self-service sessions, or a sampled human review of "resolved" AI conversations). If a team can only report one number, it should be resolution quality, not volume avoided.

## Core Metrics

### Search and Content Metrics

| Metric | What It Measures | Notes |
|--------|------------------|-------|
| Search success rate | Whether users found a relevant result | Usually requires click plus downstream validation |
| Zero-result rate | Missing coverage in search | Review by query volume and intent |
| Content gap rate | High-volume intents without a good answer | More useful than raw page-view counts |
| Freshness coverage | Share of high-impact content reviewed on time | Tie to category owners |
| Escalation after article view | Content failed to unblock the user | Strong signal for rewrite priority |

### Support Outcome Metrics

| Metric | What It Measures | Notes |
|--------|------------------|-------|
| Self-service completion | User resolved issue without assisted support | Define completion carefully |
| Assisted support deflection | Support load avoided through self-service | Keep separate from AI-only containment |
| Time to useful answer | Speed to first relevant answer | Better than raw time on page |
| Repeat-contact rate | Whether the user came back for the same issue | Important quality signal |
| Reopen-after-resolution | Weak resolution quality | Useful for AI and human flows |

## AI-Specific Metrics

| Metric | What It Answers |
|--------|-----------------|
| Citation rate | Are answers grounded in sources? |
| Correct-source rate | Did the answer cite the right source, not just any source? |
| Unresolved-intent rate | Which requests still fail despite retrieval? |
| Clarification rate | How often the assistant needed more detail |
| Escalation quality | Did handoff happen at the right time with enough context? |
| Tool-call success rate | Did agentic actions complete correctly? |
| Stale-source hit rate | Is retrieval leaning on old content? |

## Instrumentation Patterns

### Event Model

Track at least these event families:

```
CONTENT
- article_view
- related_article_click
- article_feedback
- article_stale_flagged

SEARCH
- search_performed
- search_result_click
- zero_results
- search_refined

AI
- ai_answer_rendered
- ai_citation_clicked
- ai_clarification_asked
- ai_escalated
- ai_task_attempted
- ai_task_succeeded
- ai_task_failed

SUPPORT
- contact_support_started
- ticket_created
- ticket_reopened
- assisted_resolution_completed
```

### Suggested Dimensions

- article_id
- category
- locale
- product_version
- user_role
- plan_tier
- source_type
- answer_mode
- escalation_reason

## ROI Modeling

Use organization-specific inputs:
- average cost per assisted contact by channel
- average time saved per successful self-service resolution
- content production and maintenance cost
- AI platform cost and inference cost
- QA, review, and governance overhead

### Recommended ROI Formula

```
net_benefit =
  avoided_assisted_support_cost
  + productivity_gain_from_faster_resolution
  - content_operations_cost
  - platform_and_ai_cost
  - quality_and_governance_cost
```

Do not hard-code per-ticket cost assumptions in the skill. Ask for them or state that they are unknown.

## Optimization Loop

### Weekly Review

- review zero-result and low-success queries
- review escalation-after-view and unresolved-intent clusters
- review new stale-content flags
- review AI task failures and weak handoffs

### Monthly Review

- update content backlog by impact
- measure whether top intents improved after changes
- retire duplicate or low-value pages
- confirm source freshness for high-risk topics

### Experiment Design

Good experiment targets:
- article title and search snippet quality
- chunking and reranking strategy
- citation formatting
- escalation triggers
- in-app placement of contextual help

Poor experiment targets:
- vanity page-view increases
- containment lifts without resolution-quality checks
- AI volume growth without escalation-quality review
