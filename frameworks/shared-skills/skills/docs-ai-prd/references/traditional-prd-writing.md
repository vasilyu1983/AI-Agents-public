# Traditional PRD Writing Guide

*Purpose: Educational guide for writing Product Requirements Documents following industry best practices (Inspired by Cagan, Software Requirements Essentials by Wiegers, PRD Agent Guidelines).*

**Note**: This guide explains WHY each section matters and HOW to write effective PRDs for human PM teams. For AI-assisted coding workflows, see [agentic-coding-best-practices.md](agentic-coding-best-practices.md).

---

## When to Use This Guide

Use this guide when:

- Writing PRDs for cross-functional teams (PM, engineering, design, leadership)
- Defining new features, products, or major improvements
- Transforming problem statements into structured requirements
- Preparing for discovery validation, prototyping, or planning
- Creating documentation that will evolve through delta-based updates
- Working with human PM teams following traditional product development processes

---

## Structure Overview

A well-structured PRD contains:

1. **Problem Statement** – What user or business issue are we solving?
2. **Goals & Metrics** – Quantitative, outcome-driven targets
3. **User Personas** – Who this is for and their needs
4. **Requirements** – Functional & non-functional, testable
5. **Edge Cases** – Exceptions, boundaries, failures
6. **Success Metrics** – How we measure success
7. **Risks & Mitigations** – What might cause failure + mitigation plans
8. **Appendix** – Out of scope, dependencies, open questions

---

## Section-by-Section Guidance

### 1. Problem Statement

**Purpose:** Define the user or business problem being solved.

**Include:**
- Clear problem statement (avoid solution-oriented language)
- Who is affected and how
- Why this problem matters (business/user impact)
- Evidence (qualitative quotes, quantitative data)

**Example Structure:**
```markdown
## Problem Statement

### Current Situation
Users currently export reports by manually copying data from 5 different screens into spreadsheets. This process takes 15-20 minutes per report.

### Problem
Product managers need to share performance reports with stakeholders who don't have system access, but there's no way to export formatted reports.

### Impact
- 50+ PMs spend 3-4 hours/week on manual report generation
- Delayed decision-making due to data accessibility gaps
- High error rate in manually transcribed data (15% of reports contain errors)

### Evidence
- User interviews: 12/15 PMs cited report export as top pain point
- Support tickets: 47 requests for export feature in Q3 2024
- Time-tracking data: Average 18 minutes per report × 150 reports/week = 45 hours/week
```

**Common Mistakes:**
- AVOID: Describing the solution instead of the problem ("We need a PDF export button")
- AVOID: Vague impact statements ("Users are frustrated")
- AVOID: No quantitative evidence

**Best Practices:**
- BEST: Focus on user tasks and pain points, not features
- BEST: Quantify frequency and severity
- BEST: Include direct user quotes or research findings

---

### 2. Goals & Success Metrics

**Purpose:** Define measurable success outcomes that drive product decisions.

**Guidelines:**
- Tie goals to user behavior change or business outcomes
- Avoid feature-oriented statements ("Build a dashboard")
- Use specific, numeric targets with timeframes
- Follow OKR structure: Objective → Key Results

**Example Structure:**
```markdown
## Goals & Success Metrics

### Primary Objective
Enable PMs to share performance data with external stakeholders efficiently and accurately.

### Key Results
- **KR1 (Adoption):** 70% of active PMs use export feature within 30 days of launch
- **KR2 (Efficiency):** Reduce time spent on report generation by 80% (from 18 min to <4 min)
- **KR3 (Quality):** Achieve <1% error rate in exported reports
- **KR4 (Engagement):** 40% of exported reports are viewed by non-system users

### Timeline Targets
- Launch: Q1 2025
- 30 days post-launch: KR1 & KR2 validated
- 90 days post-launch: KR3 & KR4 validated
```

**Common Mistakes:**
- AVOID: Output-focused goals ("Ship export feature")
- AVOID: No baseline or target numbers
- AVOID: Goals not tied to user value

**Best Practices:**
- BEST: Use "Increase X from A to B by date" format
- BEST: Include both product metrics (adoption, usage) and outcome metrics (efficiency, satisfaction)
- BEST: Make goals falsifiable (you can prove if you hit them or not)

---

### 3. User Personas

**Purpose:** Describe who will use this feature and why, ensuring design decisions align with real user needs.

**Include:**
- Primary persona (main user)
- Secondary personas (if any)
- Demographics, role, experience level
- User goals and motivations
- Pain points relevant to this PRD
- Behavior patterns (frequency, device, environment)

**Example Structure:**
```markdown
## User Personas

### Primary Persona: "Product Manager Paula"

**Demographics:**
- Role: Product Manager, B2B SaaS company
- Experience: 3-5 years in product management
- Industry: Enterprise software
- Team size: Manages 2-3 products, works with 5-8 engineers

**Goals:**
- Share product performance data with executives and customers
- Make data-driven decisions quickly
- Present metrics in stakeholder meetings

**Pain Points:**
- Spends 3-4 hours/week manually creating reports
- Can't give stakeholders self-service access (security/licensing)
- High risk of copy-paste errors in manual reports
- No standardized report format across team

**Behavior:**
- Generates 5-10 reports per week
- Shares reports via email, Slack, presentations
- Needs reports on-demand, not scheduled
- Works on laptop (90%) and mobile (10%)
- Creates reports during late afternoons before meetings

**Quote:** *"I spend more time reformatting spreadsheets than analyzing the data. I just want to click 'export' and share it."*

### Secondary Persona: "Executive Emma"

**Demographics:**
- Role: VP of Product
- Experience: 10+ years
- Needs: High-level summaries, quarterly reviews

**Goals:**
- Review product performance across portfolio
- Share metrics with board and investors

**Pain Points:**
- Inconsistent report formats from different PMs
- Delayed access to data (waits for PM to send report)
```

**Common Mistakes:**
- AVOID: Generic personas ("All users want this feature")
- AVOID: Demographics without goals/pain points
- AVOID: No behavioral insights (when, where, how they work)

**Best Practices:**
- BEST: Base personas on real user research (interviews, surveys, analytics)
- BEST: Include a memorable quote that captures persona's mindset
- BEST: Focus on 1–2 primary personas; avoid "everyone is a user" trap

---

### 4. Requirements

#### Functional Requirements (FR)

**Purpose:** Describe what the system must do.

**Guidelines:**
- One requirement per bullet
- Behavioral, not technical ("System must X" not "Use React framework")
- Must be testable (you can verify if implemented correctly)
- Use "must" for mandatory, "should" for recommended, "may" for optional

**Format:**
```markdown
## Functional Requirements

**FR1. Export Functionality**
- FR1.1: User must be able to export current dashboard view to PDF
- FR1.2: User must be able to export current dashboard view to Excel (.xlsx)
- FR1.3: Export must include all visible charts, tables, and filters
- FR1.4: Export must preserve company branding (logo, colors)

**FR2. Export Configuration**
- FR2.1: User should be able to select date range before export
- FR2.2: User should be able to toggle chart visibility for export
- FR2.3: User may add custom notes/commentary to export

**FR3. Export Delivery**
- FR3.1: Export must complete within 10 seconds for standard reports (<50 data points)
- FR3.2: User must receive in-app notification when export is ready
- FR3.3: User must be able to download export file from notification
- FR3.4: Export file should be available for download for 7 days
```

**Common Mistakes:**
- AVOID: Implementation details ("Use Chart.js library to render charts")
- AVOID: Vague requirements ("System should be fast")
- AVOID: Not testable ("System should feel intuitive")

**Best Practices:**
- BEST: Hierarchical numbering (FR1 → FR1.1, FR1.2)
- BEST: Include acceptance criteria for complex requirements
- BEST: Use Given-When-Then format for workflows (see below)

---

#### Non-Functional Requirements (NFR)

**Purpose:** Define constraints, quality attributes, and performance standards.

**Common Types:**
- **Performance:** Response time, throughput, latency
- **Reliability:** Uptime, error rate, MTTR
- **Security:** Authentication, authorization, data protection
- **Scalability:** Concurrent users, data volume
- **Compliance:** GDPR, SOC 2, HIPAA, industry standards

**Format:**
```markdown
## Non-Functional Requirements

**NFR1. Performance**
- NFR1.1: Export generation must complete in <10 seconds for reports with <50 data points
- NFR1.2: Export generation must complete in <30 seconds for reports with 50-500 data points
- NFR1.3: System must handle 100 concurrent export requests without degradation

**NFR2. Reliability**
- NFR2.1: Export service must have 99.9% uptime (max 43 minutes downtime/month)
- NFR2.2: Failed exports must auto-retry up to 3 times
- NFR2.3: User must receive error notification if export fails after retries

**NFR3. Security**
- NFR3.1: Exported files must only be accessible by the user who generated them
- NFR3.2: Export download links must expire after 7 days
- NFR3.3: Export download links must be one-time use (can't be shared)
- NFR3.4: Exported data must respect user's role-based access control permissions

**NFR4. Scalability**
- NFR4.1: System must support 10,000 exports per day
- NFR4.2: Export file storage must not exceed 100GB per month (auto-cleanup after 7 days)

**NFR5. Compliance**
- NFR5.1: Export functionality must comply with GDPR (user can delete their export history)
- NFR5.2: Export audit logs must be retained for 90 days (who exported what, when)
```

**Common Mistakes:**
- AVOID: No specific targets ("System should be secure")
- AVOID: Conflicting with functional requirements
- AVOID: Missing compliance requirements

**Best Practices:**
- BEST: Include specific numeric targets (99.9% uptime, <10s response time)
- BEST: Define success criteria and failure modes
- BEST: Consider regulatory/compliance requirements early

---

### 5. Edge Cases

**Purpose:** Capture conditions where the system behaves differently or encounters exceptional scenarios.

**Include:**
- Error conditions
- Missing/invalid data scenarios
- Boundary constraints (empty states, max limits)
- Uncommon but important user flows
- Failure modes and recovery strategies

**Example Structure:**
```markdown
## Edge Cases

**Empty State:**
- If dashboard has no data, show "No data to export" message with prompt to adjust filters
- Export button should be disabled when no data is present

**Large Datasets:**
- If report contains >500 data points, show warning: "Large export may take up to 60 seconds"
- If report contains >1000 data points, require user confirmation before export
- If export exceeds 30MB, notify user and offer to email download link instead

**Failed Exports:**
- If export fails (timeout, server error), show retry button
- After 3 failed attempts, show "Export service unavailable. Try again later" + support link
- Log all failed exports for debugging (include user ID, report config, error message)

**Concurrent Exports:**
- If user requests multiple exports simultaneously, queue them (max 3 pending exports per user)
- Show queue status: "Export 1 of 3 in progress..."

**Expired Download Links:**
- If user tries to access expired link (>7 days old), show "Link expired" + regenerate button
- Regenerated exports should reflect current data (not snapshot from 7 days ago)

**Permission Changes:**
- If user's permissions change after export (e.g., loses access to data), block download
- Show "You no longer have access to this data" message

**Browser Compatibility:**
- If user's browser doesn't support file download API, fall back to opening in new tab
- Show browser compatibility warning for IE11 and older
```

**Common Mistakes:**
- AVOID: Ignoring edge cases ("happy path only")
- AVOID: Treating edge cases as afterthoughts (leads to bugs)
- AVOID: No error recovery strategy

**Best Practices:**
- BEST: Think through "what if" scenarios systematically
- BEST: Define user-facing error messages upfront
- BEST: Include fallback/recovery paths
- BEST: Consider cross-browser, mobile, accessibility edge cases

---

### 6. Success Metrics (Detailed)

**Purpose:** Define how success will be measured post-launch with specific tracking mechanisms.

**Include:**
- Product metrics (adoption, engagement, retention)
- Technical metrics (performance, reliability)
- Business metrics (revenue, cost savings, efficiency)
- User satisfaction metrics (NPS, CSAT, qualitative feedback)
- Measurement methodology (how you'll track each metric)

**Example Structure:**
```markdown
## Success Metrics

### Product Metrics

**Adoption (Target: 70% of active PMs within 30 days)**
- Measurement: % of active PMs who used export feature at least once
- Tracking: Analytics event `export_clicked` + user ID
- Success criteria: ≥70% adoption by day 30
- Acceptable: ≥50% adoption by day 30
- Fail: <50% adoption by day 30

**Engagement (Target: 5 exports per user per week)**
- Measurement: Average exports per active user per week
- Tracking: Analytics event `export_completed` + count
- Success criteria: ≥5 exports/user/week by day 60
- Acceptable: ≥3 exports/user/week by day 60
- Fail: <3 exports/user/week by day 60

**Feature Stickiness (Target: 80% week-over-week retention)**
- Measurement: % of users who exported in week N and week N+1
- Tracking: Cohort analysis on `export_completed` events
- Success criteria: ≥80% WoW retention by day 90
- Fail: <60% WoW retention by day 90

### Technical Metrics

**Performance (Target: 95th percentile <10s)**
- Measurement: Time from export click to download ready
- Tracking: Performance logs `export_start` → `export_complete` timestamps
- Success criteria: p95 <10s, p99 <15s
- Fail: p95 >15s or p99 >30s

**Reliability (Target: <1% error rate)**
- Measurement: % of exports that fail (any reason)
- Tracking: Error logs + `export_failed` events
- Success criteria: <1% error rate
- Acceptable: 1-3% error rate
- Fail: >3% error rate

### Business Metrics

**Time Savings (Target: 80% reduction)**
- Measurement: Time spent per report (before: 18 min, target: <4 min)
- Tracking: User survey 30 days post-launch
- Success criteria: ≥80% reduction (≤3.6 min/report)
- Acceptable: 60-80% reduction
- Fail: <60% reduction

**Error Reduction (Target: <1% data errors)**
- Measurement: % of exported reports with data errors
- Tracking: QA spot checks (sample 50 exports/week)
- Success criteria: <1% error rate
- Fail: >5% error rate

### User Satisfaction

**Net Promoter Score (Target: +40)**
- Measurement: "How likely are you to recommend export feature?" (0-10 scale)
- Tracking: In-app survey triggered after 5th export
- Success criteria: NPS ≥+40
- Acceptable: NPS +20 to +39
- Fail: NPS <+20

**Qualitative Feedback**
- Measurement: User interviews with 10 heavy users at day 30
- Focus areas: Feature gaps, usability issues, delight moments
```

**Common Mistakes:**
- AVOID: Vanity metrics ("Total exports generated")
- AVOID: No baseline for comparison
- AVOID: Metrics not tied to goals

**Best Practices:**
- BEST: Define success/acceptable/fail thresholds for each metric
- BEST: Include measurement methodology (how you'll track it)
- BEST: Balance leading indicators (adoption) and lagging indicators (satisfaction)
- BEST: Plan for both quantitative (analytics) and qualitative (interviews) data

---

### 7. Risks & Mitigations

**Purpose:** Identify threats to success and plan proactive mitigation strategies.

**Include:**
- Technical risks (feasibility, performance, integration)
- Product/design risks (usability, adoption, market fit)
- Business risks (resource constraints, dependencies, compliance)
- Mitigation plans (what you'll do to reduce likelihood or impact)

**Example Structure:**
```markdown
## Risks & Mitigations

### Technical Risks

**Risk 1: PDF Generation Performance**
- **Description:** Complex charts may take >10s to render to PDF, violating NFR1.1
- **Likelihood:** High (based on prototype testing with Chart.js → PDF)
- **Impact:** High (poor UX, users abandon exports)
- **Mitigation:**
  - Prototype 3 PDF libraries (Puppeteer, PDFKit, jsPDF) by Sprint 1
  - Implement server-side rendering for complex charts (offload from browser)
  - Add progressive loading: "Generating export... 30%" indicator
  - Fallback: Offer PNG export if PDF generation exceeds 15s

**Risk 2: Third-Party API Dependency**
- **Description:** Export feature relies on ChartService API (external vendor)
- **Likelihood:** Medium (vendor SLA: 99.5% uptime)
- **Impact:** High (if vendor is down, exports fail completely)
- **Mitigation:**
  - Implement circuit breaker pattern (fail fast after 3 timeouts)
  - Cache chart data locally (Redis) for last 24 hours
  - Provide degraded experience: Text-only export if ChartService unavailable
  - Monitor vendor status page + set up alerts

### Product/Design Risks

**Risk 3: Low Adoption (<50%)**
- **Description:** Users don't discover or trust export feature
- **Likelihood:** Medium (new feature, behavior change required)
- **Impact:** High (feature underutilized, goals not met)
- **Mitigation:**
  - In-app onboarding tooltip on first dashboard visit
  - Email campaign to all PMs announcing feature (with video demo)
  - Add "Export" CTA to dashboard header (high visibility)
  - Track `export_button_seen` vs `export_clicked` (conversion funnel)
  - Run user interviews after 14 days to identify friction points

**Risk 4: Exported Reports Don't Meet Stakeholder Needs**
- **Description:** Exported format lacks required details (e.g., no trend lines, missing context)
- **Likelihood:** Medium (based on user interviews, needs vary)
- **Impact:** Medium (users continue manual workarounds)
- **Mitigation:**
  - User testing with 5 PMs and 3 executives before launch
  - Offer 3 export templates: "Executive Summary", "Detailed", "Custom"
  - Add feedback link in exported reports: "Missing something? Tell us"
  - Plan Phase 2: Custom export templates (user-configurable)

### Business Risks

**Risk 5: Resource Constraints (Engineering Bandwidth)**
- **Description:** Team has only 2 engineers; export feature may take 6 weeks (conflicts with Q1 roadmap)
- **Likelihood:** High (team is already at capacity)
- **Impact:** Medium (delayed launch, missed quarterly goals)
- **Mitigation:**
  - De-scope Phase 1: Launch PDF-only (defer Excel to Phase 2)
  - Hire contractor for 4 weeks to accelerate development
  - Negotiate roadmap priorities with leadership (defer Feature X by 2 weeks)

**Risk 6: GDPR Compliance Unknown**
- **Description:** Unclear if exporting user data requires explicit consent (legal review pending)
- **Likelihood:** Low (preliminary legal feedback: likely OK with existing ToS)
- **Impact:** High (if non-compliant, must halt launch)
- **Mitigation:**
  - Fast-track legal review (due by Sprint 2)
  - Design system with consent flags (can enable if required)
  - Worst case: Limit export to aggregated data only (no PII)
```

**Common Mistakes:**
- AVOID: No mitigation plans ("We'll deal with it if it happens")
- AVOID: Only listing technical risks (ignore product/business risks)
- AVOID: Risks identified too late (after implementation starts)

**Best Practices:**
- BEST: Use likelihood plus impact matrix (prioritize high-likelihood, high-impact risks)
- BEST: Assign risk owners (who monitors and executes mitigation)
- BEST: Review risks weekly during development
- BEST: Update the PRD when new risks emerge

---

### 8. Appendix (Optional)

**Purpose:** Capture supporting information that doesn't fit in main sections.

**Include:**
- Out of scope items (what we're NOT doing and why)
- Dependencies (other teams, systems, external factors)
- Open questions (unresolved decisions)
- Research artifacts (user interview summaries, competitive analysis)
- Design mockups or technical diagrams (links, not embedded)

**Example Structure:**
```markdown
## Appendix

### Out of Scope (Phase 1)

**Excel Export**
- Why: PDF addresses 80% of use cases; Excel deferred to Phase 2
- Reasoning: Excel export requires complex formatting logic (Est: +3 weeks dev time)

**Scheduled Exports**
- Why: On-demand exports solve immediate pain; automation is Phase 3
- Reasoning: User research showed "ad-hoc > scheduled" by 4:1 ratio

**Custom Branding**
- Why: Company branding is sufficient for Phase 1
- Reasoning: Only 2/15 interviewed users requested custom logos

### Dependencies

**Engineering Dependencies:**
- Chart Service API v2 must be stable (Owner: Data Platform team, ETA: Dec 15)
- File storage infrastructure must support 100GB/month (Owner: Infra team, Status: In progress)

**Design Dependencies:**
- Export icon + UI copy ready by Sprint 1 (Owner: Design team, Status: Scheduled)

**Legal Dependencies:**
- GDPR compliance review complete by Sprint 2 (Owner: Legal team, Status: Pending)

### Open Questions

1. **Should exports include raw data or only visualizations?**
   - Decision needed by: Sprint 1 (impacts data pipeline design)
   - Stakeholders: PM, Engineering, Users
   - Current thinking: Visualizations only (simpler, faster)

2. **What happens if user deletes dashboard after exporting?**
   - Decision needed by: Sprint 2 (impacts export persistence logic)
   - Options: (A) Export file persists, (B) Export deleted with dashboard
   - Recommendation: (A) Export persists (user intent: "save for later")

3. **Should we support mobile export (iOS/Android apps)?**
   - Decision needed by: Q2 2025 (not blocking Phase 1)
   - Research needed: Mobile usage patterns (current: 10% of sessions)

### Research Artifacts

- [User Interview Summary (Nov 2024)](link-to-doc)
- [Competitive Analysis: Export Features in 5 Competitors](link-to-doc)
- [Prototype Testing Results (Dec 2024)](link-to-doc)
```

**Best Practices:**
- BEST: Link to external docs (do not bloat the PRD with appendices)
- BEST: Keep "out of scope" explicit (avoids scope creep)
- BEST: Track open questions with decision deadlines

---

## Quality Checklist

Before finalizing your PRD, validate against this checklist:

**Problem & Goals:**
- [ ] Problem is clearly defined and user-centric (not solution-oriented)
- [ ] Goals are measurable and outcome-based (not feature lists)
- [ ] Evidence supports problem statement (qualitative + quantitative)

**Users & Requirements:**
- [ ] User personas based on real research (interviews, data, surveys)
- [ ] Requirements are testable (you can verify if implemented correctly)
- [ ] Functional requirements describe behavior, not implementation
- [ ] Non-functional requirements include specific numeric targets

**Completeness:**
- [ ] Edge cases documented (errors, boundary conditions, failures)
- [ ] Success metrics defined with measurement methodology
- [ ] Risks include likelihood, impact, and mitigation plans
- [ ] Out of scope and dependencies explicitly listed

**Clarity & Structure:**
- [ ] Document is concise, scannable (bullet points > prose)
- [ ] Sections follow logical order (Problem → Goals → Requirements → Risks)
- [ ] No jargon or ambiguous terms (define acronyms on first use)
- [ ] Engineers and designers have reviewed and approved

**Collaboration:**
- [ ] Stakeholders aligned on goals and priorities
- [ ] Open questions resolved or have decision deadlines
- [ ] PRD version tracked (1.0, 1.1, etc.) with changelog

---

## Common Anti-Patterns

### AVOID: Anti-Pattern 1 – Solution Before Problem

**Bad:**
```markdown
## Problem
We need a PDF export button so users can download reports.
```

**Why Bad:** Jumps to solution (PDF export) without defining user problem.

**Good:**
```markdown
## Problem
Product managers spend 15-20 minutes manually copying data from 5 screens to create reports for stakeholders who lack system access. This causes delays and introduces a 15% error rate.
```

---

### AVOID: Anti-Pattern 2 – Feature List Disguised as Goals

**Bad:**
```markdown
## Goals
- Build PDF export functionality
- Add Excel export option
- Create export history page
```

**Why Bad:** Lists features, not outcomes. Doesn't explain why these matter or how success is measured.

**Good:**
```markdown
## Goals
**Objective:** Enable PMs to share performance data efficiently and accurately.

**Key Results:**
- Reduce time spent on report generation by 80% (from 18 min to <4 min)
- Achieve <1% error rate in exported reports
- 70% adoption within 30 days
```

---

### AVOID: Anti-Pattern 3 – Vague Requirements

**Bad:**
```markdown
- System should be fast
- Export should look good
- User interface should be intuitive
```

**Why Bad:** Not testable. "Fast" and "good" are subjective.

**Good:**
```markdown
- NFR1.1: Export generation must complete in <10 seconds for reports with <50 data points
- FR1.4: Export must preserve company branding (logo, colors per brand guidelines)
- FR2.3: Export button must be visible in dashboard header (no scrolling required)
```

---

### AVOID: Anti-Pattern 4 – No Edge Cases

**Bad:** PRD assumes happy path only (user clicks export → export succeeds).

**Why Bad:** Edge cases become bugs in production.

**Good:** Document error states, empty states, large datasets, permission changes, browser compatibility, etc. (see Section 5 above).

---

### AVOID: Anti-Pattern 5 – No Mitigation Plans for Risks

**Bad:**
```markdown
## Risks
- PDF generation might be slow
- Vendor API might go down
```

**Why Bad:** Identifies risks but doesn't plan for them. Team is unprepared if risks materialize.

**Good:**
```markdown
## Risks
**Risk 1: PDF Generation Performance**
- Likelihood: High | Impact: High
- Mitigation: Prototype 3 PDF libraries, implement server-side rendering, add progress indicator
```

---

## Related Resources

**Internal Resources:**
- [Agentic Coding Best Practices](agentic-coding-best-practices.md) - AI-assisted development workflows
- [Vibe Coding Patterns](vibe-coding-patterns.md) - Exploratory coding with LLMs
- [Requirements Checklists](requirements-checklists.md) - Validation checklists for requirements

**Templates:**
- [PRD Template](../assets/prd/prd-template.md) - Copy-paste ready PRD structure
- [Tech Spec Template](../assets/spec/tech-spec-template.md) - Technical specification structure
- [Story Mapping Template](../assets/stories/story-mapping-template.md) - User story mapping

**External Resources:**
- See `data/sources.json` for curated PRD frameworks, style guides, and product metrics resources

---

## When to Use This Guide vs. Agentic Coding Workflows

**Use Traditional PRD Writing (this guide) when:**
- Working with cross-functional human teams (PM, design, engineering, leadership)
- Need formal documentation for stakeholder alignment
- Building features following waterfall or hybrid development processes
- Writing specs that will be handed off to engineering team
- Governance/compliance requires formal PRD artifacts

**Use Agentic Coding Workflows when:**
- Building features iteratively with AI coding agents (Claude Code, Cursor, Copilot)
- Working solo or in small teams with high autonomy
- Rapid prototyping or exploratory development
- Requirements evolve through implementation (not defined upfront)
- Need operational checklists for agent-human collaboration

**Hybrid Approach:**
- Use Traditional PRD for initial planning and stakeholder alignment
- Switch to Agentic Coding workflows during implementation
- Update PRD with learnings after each iteration

---

> **Remember:** A great PRD is concise, testable, and outcome-driven. It defines the problem and success criteria clearly, then gets out of the way so the team can build.
