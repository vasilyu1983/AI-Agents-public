---
name: marketing-product-analytics
description: Product analytics instrumentation and strategy covering event taxonomy design, tracking plans, user behavior analysis, activation/retention metrics, and marketing attribution. PostHog-first with multi-platform support (Pendo, Amplitude, Mixpanel, Heap).
---

# Product Analytics - Instrumentation & Measurement OS

**Modern Best Practices (January 2026)**: PostHog-first, session context registration, strict event naming, North Star activation events, privacy-first attribution.

Primary sources live in `data/sources.json`. If web search is available, refresh time-sensitive details against official docs before giving definitive advice.

No fluff. Only executable steps, templates, and checklists.

---

## When to Use This Skill

- **Event taxonomy design**: Naming conventions, event hierarchy, property structure
- **Tracking plan creation**: What to track, where, and why
- **Marketing attribution**: UTM capture, campaign tracking, source attribution
- **Activation metrics**: Defining and measuring user activation
- **Retention analysis**: Cohort analysis, churn prediction, engagement scoring
- **Platform setup**: PostHog, Pendo, Amplitude, Mixpanel, Heap configuration
- **Data quality**: Event validation, debugging, governance

---

## Default Workflow (Use Unless User Overrides)

1. **Clarify goals and constraints**: business questions, lifecycle stages, identity model, privacy/consent requirements, platforms (web/mobile/backend).
2. **Define the North Star value event**: one canonical event that represents value received (plus the smallest set of supporting events).
3. **Write the tracking plan**: use `assets/tracking-plan-saas.md` as the starting template; define required properties and ownership.
4. **Implement instrumentation**: pick the platform guide in Quick Reference (PostHog/Pendo/Amplitude/Mixpanel/Heap; server-side if needed).
5. **QA and harden**: use `assets/analytics-qa-checklist.md` + `references/event-quality-rules.md` + `references/production-hardening.md`.

---

## Core Principles

### 1. North Star Value Event (VITAL)

**Every product must have ONE canonical activation event** - the single event that means "user received real value."

| Product Type | North Star Event | When It Fires |
|--------------|------------------|---------------|
| **Content/Media** | `content_consumed` | Content fully loaded and visible |
| **SaaS Tool** | `workflow_completed` | User completes core workflow |
| **E-commerce** | `purchase_completed` | Transaction successful |
| **Developer Tool** | `integration_working` | First successful API call |

**Rule**: Every feature event should collapse into ONE activation event with properties:

```javascript
// PASS CORRECT: One event, differentiated by property
posthog.capture('value_delivered', { value_type: 'report', value_id: 'rpt_123' });
posthog.capture('value_delivered', { value_type: 'integration', value_id: 'int_456' });

// FAIL WRONG: Fragmented "value" events (harder to unify in retention/funnels)
posthog.capture('report_generated');
posthog.capture('integration_working');
```

### 2. Minimum Viable Analytics (MVA)

**Start with 5-15 events, not 200.** You can always add more.

| Layer | Required Events | Optional |
|-------|-----------------|----------|
| **Acquisition** | `page_viewed`, `signup_completed` | `campaign_landed` |
| **Activation** | Your activation event (1-2 max) | `onboarding_step_completed` |
| **Engagement** | Your engagement signal (1-2 max) | `feature_used` |
| **Conversion** | `purchase_completed` | `checkout_started` |

For auth-heavy products, add email reliability instrumentation early:
- `auth_email_requested` (type: signup_confirm, magic_link, reset_password)
- `auth_email_delivered` / `auth_email_bounced` / `auth_email_complained` (from provider webhooks)
- `auth_email_link_clicked` (completion quality signal, not just send volume)

### 3. Session Context Registration

Register standard context once per session using `posthog.register()`:

```typescript
posthog.register({
  app_env: 'prod',
  platform: 'web',
  landing_path: window.location.pathname,
  traffic_source: deriveTrafficSource(),
  utm_source, utm_medium, utm_campaign
});
```

### 4. Event Naming Convention

| Rule | Correct | Incorrect |
|------|---------|-----------|
| Lowercase only | `user_signed_up` | `User_Signed_Up` |
| Snake_case | `button_clicked` | `buttonClicked` |
| Object_action format | `project_created` | `createProject` |

---

## Quick Reference

| Task | Reference |
|------|-----------|
| PostHog setup | [references/posthog-implementation.md](references/posthog-implementation.md) |
| Pendo setup | [references/pendo-implementation.md](references/pendo-implementation.md) |
| Amplitude setup | [references/amplitude-implementation.md](references/amplitude-implementation.md) |
| Mixpanel setup | [references/mixpanel-implementation.md](references/mixpanel-implementation.md) |
| Heap setup | [references/heap-implementation.md](references/heap-implementation.md) |
| Server-side tracking | [references/server-side-tracking.md](references/server-side-tracking.md) |
| Privacy compliance | [references/privacy-compliance.md](references/privacy-compliance.md) |
| Event quality rules | [references/event-quality-rules.md](references/event-quality-rules.md) |
| Production patterns | [references/production-hardening.md](references/production-hardening.md) |
| Funnel analysis | [references/funnel-analysis.md](references/funnel-analysis.md) |
| Cohort retention | [references/cohort-retention-analysis.md](references/cohort-retention-analysis.md) |
| Experimentation | [references/experimentation-framework.md](references/experimentation-framework.md) |
| User segmentation | [references/user-segmentation.md](references/user-segmentation.md) |
| Data governance | [references/data-governance.md](references/data-governance.md) |
| Session replay & heatmaps | [references/session-replay-heatmaps.md](references/session-replay-heatmaps.md) |
| Attribution modeling | [references/attribution-modeling.md](references/attribution-modeling.md) |
| Tracking plan template | [assets/tracking-plan-saas.md](assets/tracking-plan-saas.md) |
| UTM standards | [assets/utm-naming-standards.md](assets/utm-naming-standards.md) |

---

## Implementation Checklist

```markdown
### Event Correctness
- [ ] Activation event fires only when value is **visible** (not on mount)
- [ ] Event includes required properties defined in the tracking plan (e.g., `object_type`, `object_id`, `surface`, `flow`)
- [ ] Dedupe guard used where re-renders can double-fire (see `references/production-hardening.md`)
- [ ] Event fires in **exactly one place** per feature

### Session Context
- [ ] `registerSessionContext()` called on app init
- [ ] Includes: `app_env`, `platform`, `landing_path`, `traffic_source`, UTMs

### Type Safety
- [ ] `TrafficSource` uses TypeScript enum, not free string
- [ ] All properties use `snake_case`

### Privacy
- [ ] Person properties contain **no PII** by default
- [ ] Email only stored with explicit consent
```

---

## Decision Tree

```
### Not seeing expected events?
├─ PostHog default events visible? ($pageview, autocapture)
│   ├─ Yes -> Custom event bug -> Check component, guards, dedupe
│   └─ No -> SDK issue -> Check env vars, consent, ad blockers
├─ Check DevTools Network -> verify /e/ calls
└─ Check PostHog Live Events (not Activity)

### Can't answer business questions?
├─ Missing events -> Add custom events for key moments
├─ Missing properties -> Enrich with context
├─ No user ID -> Implement identify() calls
└─ Attribution gaps -> Capture UTMs, persist through signup
```

---

## Anti-Patterns Summary

| Anti-Pattern | Instead |
|--------------|---------|
| No North Star event | Define ONE canonical activation event |
| Excessive `*_viewed` events | Collapse into one event with properties |
| PII in identify() | State-based identification only |
| Event spam from re-renders | Use `isPostHogReady()` guard + dedupe |
| Free text `source` | Use TypeScript enum for TrafficSource |
| Non-unique IDs | Use stable domain IDs (`*_id`) or an action_instance_id |
| Tracking everything | Focus on 5-15 key events (MVA) |
| Inconsistent naming | Enforce lowercase snake_case strictly |

See [references/event-quality-rules.md](references/event-quality-rules.md) for detailed examples.

---

## Metrics and Benchmarks

Default to internal baselines and trendlines; use external benchmarks only when comparing like-for-like segments and definitions.

If you need external references, see `data/sources.json` -> `benchmarks_research`.

---

## Templates

| Template | Purpose |
|----------|---------|
| [tracking-plan-saas.md](assets/tracking-plan-saas.md) | Complete SaaS tracking plan |
| [marketing-event-library.md](assets/marketing-event-library.md) | Marketing attribution events |
| [utm-naming-standards.md](assets/utm-naming-standards.md) | UTM parameter guide |
| [activation-metrics-template.md](assets/activation-metrics-template.md) | Activation metric definition |
| [analytics-qa-checklist.md](assets/analytics-qa-checklist.md) | Data quality checklist |

---

## International Markets

This skill uses US/UK market defaults. For international product analytics:

| Need | See Skill |
|------|-----------|
| Regional compliance (GDPR, PIPL, LGPD) | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |
| Regional analytics platforms (Baidu Analytics) | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |
| Privacy requirements by region | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |
| Cookie consent by jurisdiction | [marketing-geo-localization](../marketing-geo-localization/SKILL.md) |

If your query is primarily about GDPR/PIPL/LGPD or consent configuration, use [marketing-geo-localization](../marketing-geo-localization/SKILL.md) alongside this skill.

---

## Related Skills

- [marketing-cro](../marketing-cro/SKILL.md) - A/B testing, conversion optimization
- [marketing-leads-generation](../marketing-leads-generation/SKILL.md) - Lead funnel, B2B attribution
- [qa-agent-testing](../qa-agent-testing/SKILL.md) - LLM agent testing (complements AI analytics)
- [data-sql-optimization](../data-sql-optimization/SKILL.md) - SQL for analytics queries

---

## Data Sources

See [data/sources.json](data/sources.json) for official documentation links.

## Ops Runbook: Instrumentation Gate (Pre-PR)

Use this to keep analytics changes production-safe and queryable.

### Pre-PR Commands

```bash
# 1) Find changed tracking calls
rg -n "capture\(|track\(|analytics\.|posthog\." src app lib

# 2) Enforce event/property naming policy
rg -n "[A-Z]" src | rg "capture\(|track\("  # quick camelCase/PascalCase smell

# 3) Validate tracking plan coverage
# (keep a single source of truth file; fail if event is missing)
rg -n "signup_started|signup_completed|checkout_started|trial_started" docs src

# 4) Run analytics gate test (if project defines one)
npm run test:analytics-gate
```

### Post-Deploy Smoke Query Template

```sql
-- Replace table names for your warehouse/provider
select event,
       count(*) as events,
       count(distinct distinct_id) as users
from events
where timestamp >= now() - interval '24 hour'
  and event in ('signup_started','signup_completed','checkout_started','trial_started')
group by event
order by events desc;
```

### Event Contract Minimum

Each critical event must include:
- stable event name (snake_case)
- actor id (`user_id` or `distinct_id`)
- object id (`*_id`)
- source context (`surface`, `entry_point`, `utm_*` when relevant)
- timestamp from server or trusted client clock

### Gate Failure Policy

- Missing critical event or required property: block merge.
- Non-critical property drift: allow merge only with follow-up issue.
- Silent event rename: block merge until dashboard/query migration is prepared.

