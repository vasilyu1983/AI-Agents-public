# AI Coding Metrics Dashboard Template

**Last Updated**: {{DATE}}
**Owner**: {{NAME}}
**Version**: {{VERSION}}

---

Purpose: provide a three-tier dashboard layout so each audience sees the right metrics at the right cadence. Copy the tier that matches your audience, populate placeholders, and wire up data sources.

## How to Use

1. Pick the tier matching your audience (executive, team lead, developer).
2. Replace every `{{PLACEHOLDER}}` with your organization's values.
3. Connect each metric to its data source using the mapping table at the bottom.
4. Set alert thresholds in the traffic-light table to match your targets.

---

## Tier 1: Executive Dashboard (C-Suite / VP Engineering)

Refresh cadence: **monthly**. Trend lines: 3-month and 6-month rolling.

### KPI Cards

| # | KPI | Current | Prior Month | 3-Mo Trend | 6-Mo Trend | Target | Status |
|---|-----|---------|-------------|------------|------------|--------|--------|
| 1 | AI Tool ROI (%) | {{ROI_CURRENT}} | {{ROI_PRIOR}} | {{TREND}} | {{TREND}} | {{ROI_TARGET}} | {{GREEN/AMBER/RED}} |
| 2 | Adoption Rate (%) | {{ADOPT_CURRENT}} | {{ADOPT_PRIOR}} | {{TREND}} | {{TREND}} | {{ADOPT_TARGET}} | {{GREEN/AMBER/RED}} |
| 3 | Velocity Change (%) | {{VEL_CURRENT}} | {{VEL_PRIOR}} | {{TREND}} | {{TREND}} | {{VEL_TARGET}} | {{GREEN/AMBER/RED}} |
| 4 | Quality Delta (defect rate change %) | {{QUAL_CURRENT}} | {{QUAL_PRIOR}} | {{TREND}} | {{TREND}} | {{QUAL_TARGET}} | {{GREEN/AMBER/RED}} |
| 5 | Developer Satisfaction (x/5) | {{SAT_CURRENT}} | {{SAT_PRIOR}} | {{TREND}} | {{TREND}} | {{SAT_TARGET}} | {{GREEN/AMBER/RED}} |
| 6 | Monthly Cost per Developer ($) | {{COST_CURRENT}} | {{COST_PRIOR}} | {{TREND}} | {{TREND}} | {{COST_TARGET}} | {{GREEN/AMBER/RED}} |

### Traffic-Light Thresholds

| KPI | Green | Amber | Red |
|-----|-------|-------|-----|
| ROI (%) | > {{GREEN_THRESHOLD}} | {{AMBER_LOW}} - {{AMBER_HIGH}} | < {{RED_THRESHOLD}} |
| Adoption Rate (%) | > {{GREEN_THRESHOLD}} | {{AMBER_LOW}} - {{AMBER_HIGH}} | < {{RED_THRESHOLD}} |
| Velocity Change (%) | > {{GREEN_THRESHOLD}} | {{AMBER_LOW}} - {{AMBER_HIGH}} | < {{RED_THRESHOLD}} |
| Quality Delta (%) | > {{GREEN_THRESHOLD}} | {{AMBER_LOW}} - {{AMBER_HIGH}} | < {{RED_THRESHOLD}} |
| Developer Satisfaction | > {{GREEN_THRESHOLD}} | {{AMBER_LOW}} - {{AMBER_HIGH}} | < {{RED_THRESHOLD}} |
| Monthly Cost per Dev | < {{GREEN_THRESHOLD}} | {{AMBER_LOW}} - {{AMBER_HIGH}} | > {{RED_THRESHOLD}} |

### Layout Sketch

```
+-------------------+-------------------+-------------------+
|   ROI (%)         |  Adoption Rate    |  Velocity Change  |
|   [big number]    |  [big number]     |  [big number]     |
|   [sparkline]     |  [sparkline]      |  [sparkline]      |
+-------------------+-------------------+-------------------+
| Quality Delta     | Dev Satisfaction  | Monthly Cost/Dev  |
|   [big number]    |  [big number]     |  [big number]     |
|   [sparkline]     |  [sparkline]      |  [sparkline]      |
+-------------------+-------------------+-------------------+
|        6-Month Trend Chart (all KPIs overlaid)            |
+-----------------------------------------------------------+
```

---

## Tier 2: Team Lead Dashboard

Refresh cadence: **weekly**.

### Metrics Table

| # | Metric | Team: {{TEAM_A}} | Team: {{TEAM_B}} | Team: {{TEAM_C}} | Org Avg | Target | Status |
|---|--------|-------------------|-------------------|-------------------|---------|--------|--------|
| 1 | Deployment Frequency | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 2 | Lead Time for Changes | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 3 | Change Failure Rate (%) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 4 | Mean Time to Recovery | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 5 | Cycle Time (days) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 6 | PR Throughput (PRs/week) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 7 | PR Review Time (hours) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 8 | Test Coverage (%) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 9 | AI Tool Adoption (%) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |
| 10 | Suggestion Accept Rate (%) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{AVG}} | {{TARGET}} | {{STATUS}} |

### Drill-Down Paths

| Metric | Drill-Down View | Data Source |
|--------|----------------|-------------|
| Deployment Frequency | Deployments by service, by day | {{CI_CD_TOOL}} |
| Lead Time for Changes | Commit-to-deploy timeline | {{CI_CD_TOOL}} + {{SCM}} |
| Change Failure Rate | Failed deploys + rollbacks | {{INCIDENT_TOOL}} |
| MTTR | Incident timeline | {{INCIDENT_TOOL}} |
| Cycle Time | Issue open-to-close breakdown | {{PROJECT_TOOL}} |
| PR Throughput | PR list with status, author, size | {{SCM}} |
| PR Review Time | Review request-to-approval duration | {{SCM}} |
| Test Coverage | Coverage by module/service | {{COVERAGE_TOOL}} |
| AI Tool Adoption | Active users / licensed seats | {{AI_TOOL_ADMIN}} |
| Suggestion Accept Rate | Accepted vs dismissed by language | {{AI_TOOL_TELEMETRY}} |

### Team Comparison (Anonymized)

Teams are displayed as Team 1, Team 2, etc. unless team leads opt into named display.

| Rank | Team (Anonymized) | Composite Score | Top Strength | Biggest Gap |
|------|-------------------|----------------|--------------|-------------|
| 1 | {{TEAM_ANON}} | {{SCORE}} | {{STRENGTH}} | {{GAP}} |
| 2 | {{TEAM_ANON}} | {{SCORE}} | {{STRENGTH}} | {{GAP}} |
| 3 | {{TEAM_ANON}} | {{SCORE}} | {{STRENGTH}} | {{GAP}} |

---

## Tier 3: Developer Dashboard (Individual / Opt-In Only)

Refresh cadence: **daily** (self-service). Participation is voluntary; no individual data is shared with management.

### Personal Usage Stats

| Metric | This Week | Last Week | 30-Day Avg |
|--------|-----------|-----------|------------|
| Suggestions Shown | {{COUNT}} | {{COUNT}} | {{AVG}} |
| Suggestions Accepted | {{COUNT}} | {{COUNT}} | {{AVG}} |
| Suggestions Rejected | {{COUNT}} | {{COUNT}} | {{AVG}} |
| Accept Rate (%) | {{RATE}} | {{RATE}} | {{AVG}} |
| Estimated Time Saved (hours) | {{HOURS}} | {{HOURS}} | {{AVG}} |
| Top Language Used with AI | {{LANGUAGE}} | {{LANGUAGE}} | — |
| Most Productive Use Case | {{USE_CASE}} | {{USE_CASE}} | — |

### Learning Resources

| Usage Pattern | Suggested Resource |
|--------------|-------------------|
| Low accept rate in {{LANGUAGE}} | {{TRAINING_LINK}} |
| Not using chat/explain features | {{TUTORIAL_LINK}} |
| High reject rate on tests | {{BEST_PRACTICES_LINK}} |

---

## Data Source Mapping

| Metric | Source System | API / Query | Refresh | Owner |
|--------|-------------|-------------|---------|-------|
| ROI | {{FINANCE_TOOL}} + {{AI_TOOL_ADMIN}} | {{API_ENDPOINT_OR_QUERY}} | Monthly | {{OWNER}} |
| Adoption Rate | {{AI_TOOL_ADMIN}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| Velocity (Deployment Freq) | {{CI_CD_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| Lead Time | {{SCM}} + {{CI_CD_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| Change Failure Rate | {{INCIDENT_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| MTTR | {{INCIDENT_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| Cycle Time | {{PROJECT_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| PR Throughput | {{SCM}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| PR Review Time | {{SCM}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| Test Coverage | {{COVERAGE_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Weekly | {{OWNER}} |
| Suggestion Accept Rate | {{AI_TOOL_TELEMETRY}} | {{API_ENDPOINT_OR_QUERY}} | Daily | {{OWNER}} |
| Developer Satisfaction | {{SURVEY_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Quarterly | {{OWNER}} |
| Quality Delta (Defect Rate) | {{BUG_TRACKER}} | {{API_ENDPOINT_OR_QUERY}} | Monthly | {{OWNER}} |
| Cost per Developer | {{FINANCE_TOOL}} | {{API_ENDPOINT_OR_QUERY}} | Monthly | {{OWNER}} |

---

## Implementation Notes

- Start with Tier 1. Add Tier 2 once data pipelines stabilize. Tier 3 is optional.
- Automate data collection before manual entry becomes a bottleneck.
- Review thresholds quarterly; recalibrate as baselines shift.
- Keep developer-level data aggregated at the team level for management views.
