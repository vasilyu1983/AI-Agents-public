# AI Coding Tool Adoption Metrics

Operational reference for measuring how AI coding tools spread through an engineering organization. Covers what to measure, where to get the data, and how to diagnose stalls.

---

## Core Adoption Metrics

Track these 10 metrics to understand adoption depth and breadth.

| # | Metric | Formula | Good | Warning | Source |
|---|--------|---------|------|---------|--------|
| 1 | License Utilization Rate | Active users / Purchased licenses | > 80% | < 50% | License admin dashboard |
| 2 | DAU/WAU Ratio | Daily active users / Weekly active users | > 0.6 | < 0.3 | Tool telemetry |
| 3 | Session Frequency | Sessions per developer per week | > 4 | < 1 | Session logs |
| 4 | Repo Coverage | Repos with AI enabled / Total repos | > 70% | < 30% | Config audit |
| 5 | Feature Breadth Index | Distinct features used / Total features available | > 0.5 | < 0.2 | Feature usage logs |
| 6 | Acceptance Rate | Suggestions accepted / Suggestions shown | > 30% | < 15% | Tool-specific API |
| 7 | Organic vs Mandated Ratio | Self-initiated sessions / Total sessions | > 0.7 | < 0.4 | Session origin tracking |
| 8 | Time-in-Tool per Session | Median minutes per active session | 15-60 min | < 5 min or > 120 min | Session duration logs |
| 9 | Retention Rate (30-day) | Users active in month N who are active in month N+1 | > 85% | < 60% | Monthly cohort analysis |
| 10 | First-Week Activation | Users who complete 5+ sessions in first 7 days / New users | > 60% | < 30% | Onboarding funnel |

### Metric Definitions

**License Utilization Rate** — The percentage of purchased seats that had at least one active session in the measurement period (typically 30 days). Licenses sitting unused are pure cost. Track monthly and set a reallocation policy for licenses unused for 60+ days.

**DAU/WAU Ratio** — Measures habit strength. A ratio of 0.6 means the average weekly user opens the tool on 3 of 5 workdays. Below 0.3 suggests the tool is a novelty, not a habit.

**Session Frequency** — Count distinct sessions (gap of 30+ minutes of inactivity = new session). Developers using AI as a core workflow tool average 5-8 sessions per week. One session per week indicates occasional experimentation.

**Repo Coverage** — Percentage of active repositories (committed to in last 90 days) where AI tooling is configured and available. Low coverage often signals policy or compatibility gaps, not developer disinterest.

**Feature Breadth Index** — Tracks whether developers use only code completions or also leverage chat, agent mode, code review, test generation, and documentation features. Narrow usage (completions only) leaves the majority of value untapped.

**Acceptance Rate** — The primary signal for suggestion quality. Rates below 15% indicate poor model fit to the codebase, bad prompt context, or developer distrust. Rates above 45% may indicate developers are accepting without reviewing.

**Organic vs Mandated Ratio** — Distinguishes genuine adoption from compliance. Track whether sessions originate from developer-initiated actions or from mandated workflow steps (e.g., required AI review before merge).

**Time-in-Tool per Session** — Very short sessions (< 5 min) suggest the tool failed to help. Very long sessions (> 120 min) may indicate the developer is struggling with the tool rather than being productive.

---

## Adoption Curve Phases

| Phase | Dev Coverage | Timeline | Key Targets | Leading Indicators | Lagging Indicators |
|-------|-------------|----------|-------------|-------------------|-------------------|
| **Pilot** | 0-5% | Months 1-3 | Validate security, measure initial acceptance rate, identify champion developers | Number of volunteers, setup completion rate | Acceptance rate, qualitative feedback scores |
| **Early Adoption** | 5-25% | Months 3-6 | Expand to 3+ teams, establish training program, collect first productivity data | Training enrollment, cross-team requests | DAU/WAU ratio > 0.4, feature breadth > 0.3 |
| **Majority** | 25-75% | Months 6-12 | Default-on for new repos, integrate into onboarding, standardize workflows | Repo coverage growth rate, organic usage ratio | License utilization > 70%, retention > 80% |
| **Scaling** | 75-95% | Months 12-18 | Address holdout teams, optimize for advanced use cases, measure ROI | Holdout team engagement, advanced feature adoption | Productivity delta measurable, quality stable |
| **Mature** | 95%+ | Months 18+ | Continuous optimization, cost management, next-gen tool evaluation | Feature breadth > 0.6, workflow integration depth | Cost per developer stabilized, measurable business impact |

### Phase Transition Criteria

**Pilot to Early Adoption** — Move when:
- Security review complete and approved
- Acceptance rate > 20% among pilot users
- At least 3 developers voluntarily using daily
- No critical incidents in pilot period

**Early Adoption to Majority** — Move when:
- DAU/WAU ratio > 0.4 across early adopter teams
- Training materials validated and scalable
- IT provisioning automated (< 1 day to activate new user)
- At least one quantitative productivity metric shows improvement

**Majority to Scaling** — Move when:
- License utilization > 70%
- Organic usage ratio > 0.6
- No team-level adoption below 30%
- Quality metrics stable or improving

**Scaling to Mature** — Move when:
- Coverage > 95% of eligible developers
- Feature breadth index > 0.5 org-wide
- ROI calculation validated by finance
- Continuous improvement loop operational

---

## Tool-Specific Tracking

### GitHub Copilot

**Data Sources:**
- Copilot Metrics API: `GET /orgs/{org}/copilot/metrics` (requires org admin)
- Copilot Usage API: `GET /orgs/{org}/copilot/usage` (seat-level data)
- Audit log API: `GET /orgs/{org}/audit-log?action=copilot`

**Key Fields:**
| Field | Description | Endpoint |
|-------|-------------|----------|
| `total_active_users` | Users with at least one event | Metrics API |
| `total_suggestions_count` | Completions shown | Metrics API |
| `total_acceptances_count` | Completions accepted | Metrics API |
| `total_lines_suggested` | Lines of code suggested | Metrics API |
| `total_lines_accepted` | Lines of code accepted | Metrics API |
| `total_active_chat_users` | Users who used Copilot Chat | Metrics API |
| `breakdown` by language, editor | Per-language and per-editor splits | Metrics API |

**Collection Cadence:** Daily aggregation available. Pull weekly for dashboards, monthly for reports.

### Claude Code

**Data Sources:**
- Session logs (local): `~/.claude/projects/` session history
- API usage: Anthropic Console usage dashboard or API (`/v1/usage`)
- Token consumption: per-session and per-conversation token counts

**Key Fields:**
| Field | Description | Source |
|-------|-------------|--------|
| Session count | Number of CLI sessions | Session logs |
| Token usage (input/output) | Tokens consumed per session | API billing |
| Tool call patterns | Which tools invoked (Read, Edit, Bash, Grep) | Session logs |
| Session duration | Wall-clock time per session | Session timestamps |
| Files modified per session | Count of unique files edited | Git diff correlation |
| Task completion rate | Sessions ending with successful outcome | Manual tagging or heuristic |

**Collection Cadence:** Aggregate from session logs daily. Token usage from billing API weekly.

### Cursor

**Data Sources:**
- Cursor telemetry: built-in analytics dashboard (Team/Business plans)
- Extension telemetry: VS Code extension usage events
- Session metrics: tab completion, chat, and composer usage

**Key Fields:**
| Field | Description | Source |
|-------|-------------|--------|
| Active users | Users with sessions in period | Admin dashboard |
| Tab completions accepted | Inline completions accepted | Telemetry |
| Chat messages sent | Composer/chat interactions | Telemetry |
| Composer sessions | Multi-file edit sessions | Telemetry |
| Lines generated | Total lines from AI | Telemetry |
| Model usage split | Requests per model (GPT-4, Claude, etc.) | Telemetry |

### Codex (OpenAI)

**Data Sources:**
- Codex dashboard: task history and status
- Audit logs: API-level request/response logging
- Git integration: branch/PR creation events

**Key Fields:**
| Field | Description | Source |
|-------|-------------|--------|
| Tasks submitted | Total tasks sent to Codex | Dashboard |
| Task completion rate | Tasks completed successfully / Total | Dashboard |
| Task types | Feature, bugfix, refactor, test distribution | Task metadata |
| PR merge rate | Codex PRs merged / Codex PRs created | Git integration |
| Iteration count | Human feedback rounds per task | Task history |
| Time-to-completion | Wall-clock from submit to done | Task timestamps |

### ChatGPT / API Direct Usage

**Data Sources:**
- OpenAI usage API: token consumption and request counts
- Workspace analytics (Team/Enterprise plans)
- API key attribution for programmatic usage

**Key Fields:**
| Field | Description | Source |
|-------|-------------|--------|
| Token consumption | Input + output tokens per period | Usage API |
| Request count | API calls per period | Usage API |
| Active users | Unique users in workspace | Workspace admin |
| Conversation length | Messages per conversation | Analytics |
| Model distribution | Requests per model variant | Usage API |
| Cost per user | Monthly spend / active users | Billing |

---

## Segmentation Strategies

### By Team / Department

Slice adoption data by organizational unit to identify:
- **Champion teams** — High adoption, high acceptance rate. Use as internal case studies.
- **Lagging teams** — Low adoption despite access. Diagnose: training gap, workflow mismatch, or cultural resistance.
- **Divergent teams** — High usage but low acceptance rate. Investigate: model fit to their stack, prompt quality, or code style conflicts.

Minimum team size for meaningful segmentation: 5 developers. Below that, individual variance dominates.

### By Seniority Level

| Level | Expected Pattern | Watch For |
|-------|-----------------|-----------|
| Junior (0-2 yr) | High acceptance rate, high session frequency, narrow feature use | Over-reliance, accepting without understanding, reduced learning |
| Mid (2-5 yr) | Moderate acceptance rate, broad feature use | Productivity ceiling if not using advanced features |
| Senior (5-10 yr) | Lower acceptance rate, selective usage, heavy chat/agent use | Rejection without fair evaluation, influence on team adoption |
| Staff+ (10+ yr) | Lowest acceptance rate, strategic use (architecture, review) | Blocking team adoption, or conversely championing it |

Seniors and staff often have the lowest acceptance rates because they write more novel/architectural code where suggestions are less applicable. This is expected, not a problem.

### By Repo Type

| Repo Type | Expected Adoption | Notes |
|-----------|------------------|-------|
| Frontend (React, Vue, etc.) | High — repetitive patterns, strong training data | Watch for copy-paste component proliferation |
| Backend (APIs, services) | Medium-High — business logic reduces suggestion quality | Monitor security of generated auth/data-access code |
| Infrastructure (Terraform, K8s) | Medium — smaller corpus, config-heavy | High risk for misconfiguration, extra review needed |
| Data (pipelines, ML) | Medium — specialized patterns | Model may lack domain context |
| Mobile (iOS, Android) | Medium — platform-specific APIs | Check for deprecated API suggestions |
| Embedded / Systems | Low — niche patterns, safety-critical | Acceptance rate naturally lower, quality gates critical |

### By Task Type

| Task Type | AI Impact Potential | Measurement Approach |
|-----------|-------------------|---------------------|
| Greenfield development | High — boilerplate, scaffolding, patterns | Time-to-first-PR for new features |
| Maintenance / bug fixes | Medium — context-dependent | Fix time comparison (with/without AI) |
| Debugging | Medium-High — log analysis, hypothesis generation | Time-to-root-cause |
| Code review | High — automated review comments, consistency | Review turnaround time, defect escape rate |
| Testing | High — test generation, edge case discovery | Test coverage delta, mutation score |
| Documentation | High — docstring generation, README creation | Documentation coverage ratio |
| Refactoring | Medium — pattern recognition, but risky | Rework rate on AI-assisted refactors |

### By Context Maturity Level

If using the dev-context-engineering skill's L0-L4 model:

| Level | Description | Expected AI Effectiveness |
|-------|-------------|--------------------------|
| L0 — No context | Raw model, no project knowledge | Low — generic suggestions only |
| L1 — Basic context | README, file structure provided | Medium — reasonable scaffolding |
| L2 — Rich context | Architecture docs, coding standards, examples | Medium-High — style-consistent suggestions |
| L3 — Deep context | Full codebase indexed, dependency graph, test patterns | High — project-aware suggestions |
| L4 — Living context | Continuously updated context, feedback loops | Highest — adaptive, improving over time |

Track adoption metrics at each context level separately. Organizations at L0-L1 will see lower acceptance rates and may incorrectly conclude the tools are ineffective.

---

## Adoption Stall Patterns

### Pattern 1: "Tried it, didn't stick"

**Signal:** High initial activation, steep drop in 30-day retention (< 50%).

**Root Cause:** Training gap. Developers tried the tool with default settings, got mediocre results, and concluded it was not useful.

**Fixes:**
- Structured onboarding: 30-minute hands-on workshop with real codebase examples
- Context engineering: set up project-specific context (CLAUDE.md, .cursorrules, etc.)
- Buddy system: pair each new user with a power user for first 2 weeks
- Quick-win catalog: curated list of tasks where AI excels in your stack

### Pattern 2: "Works for me, not my team"

**Signal:** 1-2 power users per team with high usage; rest of team at near-zero.

**Root Cause:** Champion dependency. Knowledge concentrated in individuals who discovered effective workflows on their own.

**Fixes:**
- Document and share champion workflows as team playbooks
- Rotate "AI tool of the week" demos in team standups (5 min max)
- Create shared prompt libraries and context configurations
- Make champions responsible for onboarding their teammates (with allocated time)

### Pattern 3: "IT blocked it"

**Signal:** Adoption stalls at pilot phase. Long procurement/security review cycles.

**Root Cause:** Security and compliance friction. Legitimate concerns about code leaving the network, IP exposure, or data residency.

**Fixes:**
- Pre-build security assessment package (SOC2, data flow diagrams, retention policies)
- Start with self-hosted or zero-retention options where available
- Create a tiered access model: basic completions (low risk) before agent mode (higher risk)
- Involve security team from day 1, not as an afterthought
- Document data flow explicitly: what code leaves the machine, where it goes, how long it persists

### Pattern 4: "Too slow for my workflow"

**Signal:** Low time-in-tool per session (< 3 min). High abandonment mid-session.

**Root Cause:** Integration friction. Tool latency, awkward UX, or context-switching cost exceeds perceived benefit.

**Fixes:**
- Measure and optimize latency: suggestion latency > 500ms kills flow state
- Ensure IDE integration is native (not browser-based workaround)
- Keyboard shortcut training: accept, reject, cycle suggestions without mouse
- Pre-warm context: configure repos so tool indexes on startup, not first query
- Proxy/network optimization for API-based tools

### Pattern 5: "Doesn't work with our stack"

**Signal:** High adoption in some teams, near-zero in others. Correlates with language/framework.

**Root Cause:** Compatibility gap. Model training data under-represents the team's stack (niche language, internal framework, proprietary DSL).

**Fixes:**
- Fine-tune context: provide framework docs, coding patterns, and examples as context
- Custom instructions: write tool-specific rules for the stack
- Evaluate alternative models: some models perform better on specific languages
- Hybrid approach: use AI for the parts it handles well (tests, docs, boilerplate), manual for domain-specific logic
- Track acceptance rate by language/framework to quantify the gap

---

## Privacy-Respecting Data Collection

### Principles

1. **Aggregate only** — Never track individual developer metrics for performance evaluation
2. **Minimum team size** — Team-level dashboards require minimum 5 developers to prevent identification
3. **Opt-in detail** — Individual developers can opt in to see their own detailed metrics; managers cannot access individual data
4. **Transparent collection** — Developers know exactly what is collected and why
5. **Right to delete** — Individual data deletable on request

### Architecture

```
Individual Device           Aggregation Layer           Dashboard
┌─────────────┐            ┌──────────────┐           ┌──────────┐
│ Session logs │──anonymize─│ Team-level   │──publish──│ Adoption │
│ Token counts │            │ aggregates   │           │ metrics  │
│ Accept/reject│            │ (min size 5) │           │ dashboard│
└─────────────┘            └──────────────┘           └──────────┘
       │                                                    │
       ▼                                                    ▼
┌─────────────┐                                    ┌──────────────┐
│ Individual  │ (opt-in, visible                   │ Org-level    │
│ developer   │  only to the developer)            │ trend reports│
│ self-view   │                                    │ (quarterly)  │
└─────────────┘                                    └──────────────┘
```

### Data Collection Tiers

| Tier | Data Collected | Visibility | Consent |
|------|---------------|------------|---------|
| **Tier 1: Billing** | License usage, token consumption, cost | Finance + Eng leadership | Implicit (part of license) |
| **Tier 2: Aggregate** | Team-level acceptance rate, session counts, feature usage | Team leads + Eng leadership | Org policy (communicated) |
| **Tier 3: Individual** | Per-developer session details, prompt patterns, workflow analysis | Developer only (self-service) | Explicit opt-in |

### Data Retention Policies

| Data Type | Retention | Justification |
|-----------|-----------|---------------|
| Raw session logs | 30 days | Debugging and support |
| Aggregated team metrics | 2 years | Trend analysis |
| Billing/cost data | Per finance policy | Compliance |
| Individual opt-in data | Until opt-out or 90 days | Developer self-improvement |

### Anti-Patterns to Avoid

- **Leaderboards** — Never rank developers by AI usage. This incentivizes gaming, not productivity.
- **Usage mandates** — "You must use AI for X% of tasks" creates compliance theater.
- **Acceptance rate targets** — Setting targets for acceptance rate encourages accepting bad suggestions.
- **Individual metrics in reviews** — AI tool usage is not a performance metric. Outcomes are.
- **Surveillance framing** — If developers feel watched, they will game metrics or avoid the tool.

### Communication Template

When rolling out tracking, communicate:

> We are collecting aggregate adoption data to understand how AI tools are being used across teams. This data helps us make better tooling decisions — which tools to invest in, where to provide more training, and how to improve our setup.
>
> What we track: team-level usage patterns (acceptance rate, session frequency, feature breadth). Minimum team size of 5 for any reporting.
>
> What we do NOT track: individual developer usage for performance evaluation. Your manager cannot see your personal metrics.
>
> You can opt in to see your own detailed metrics for self-improvement.

---

## Measurement Cadence

| Metric Category | Collection | Review | Action Threshold |
|----------------|------------|--------|-----------------|
| License utilization | Daily | Monthly | < 50% utilization triggers seat reallocation |
| Acceptance rate | Daily | Weekly | < 15% triggers context/training review |
| DAU/WAU ratio | Daily | Bi-weekly | < 0.3 triggers engagement investigation |
| Feature breadth | Weekly | Monthly | < 0.2 triggers feature awareness campaign |
| Retention (30-day) | Monthly | Monthly | < 60% triggers onboarding review |
| Repo coverage | Weekly | Monthly | < 30% triggers enablement sprint |
| Adoption phase assessment | — | Quarterly | Phase regression triggers intervention plan |
