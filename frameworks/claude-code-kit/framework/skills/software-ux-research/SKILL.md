---
name: software-ux-research
description: UX research and analysis for identifying gaps, mapping customer journeys, benchmarking against top companies (OpenAI, Apple, Stripe, Notion), and measuring UX success using frameworks like JTBD, Kano Model, Double Diamond, and Service Blueprints.
---

# UX Research & Analysis Skill - Quick Reference

Use this skill when the focus is **analyzing and improving user experience** rather than implementing UI components. This skill identifies problems and opportunities; use `software-ui-ux-design` to implement solutions.

**Key Distinction**:
- `software-ux-research` (this skill) = Analysis, research, recommendations
- `software-ui-ux-design` = Implementation, components, code

---

## When to Use This Skill

Invoke when users ask for:

- UX audits and gap analysis (heuristic evaluation, cognitive walkthrough)
- Customer journey mapping and touchpoint analysis
- Competitive UX benchmarking against top companies
- Usability testing planning and synthesis
- UX metrics definition (SUS, NPS, HEART framework)
- Research frameworks (JTBD, Kano Model, Double Diamond)
- Service blueprint creation
- Pain point identification and prioritization
- User research methodology guidance
- **User feedback analysis** (App Store, Play Store, G2, Capterra, TrustRadius reviews)
- **Review mining** for competitive intelligence and pain point extraction
- **Feedback loop patterns** from BigTech and unicorns (Linear, Figma, Airbnb)

---

## Quick Reference Table

| Research Task | Framework/Method | Template | Output |
|---------------|------------------|----------|--------|
| **UX Audit** | Heuristic + Cognitive Walkthrough | [heuristic-evaluation-template.md](templates/audits/heuristic-evaluation-template.md) | Gap report with severity ratings |
| **Journey Mapping** | 5-Stage + Service Blueprint | [customer-journey-canvas.md](templates/journeys/customer-journey-canvas.md) | Visual journey map |
| **Competitive Analysis** | Feature + UX Pattern Matrix | [competitive-ux-matrix.md](templates/competitive/competitive-ux-matrix.md) | Benchmark report |
| **Problem Discovery** | JTBD + Opportunity Solution Tree | See [product-management](../product-management/SKILL.md) | Opportunity map |
| **Feature Prioritization** | Kano Model | [research-frameworks.md](resources/research-frameworks.md#kano-model) | Priority matrix |
| **Usability Testing** | Think-aloud + Task Analysis | [usability-test-plan.md](templates/testing/usability-test-plan.md) | Findings report |
| **UX Measurement** | SUS + HEART + Task Metrics | [ux-metrics-dashboard.md](templates/metrics/ux-metrics-dashboard.md) | Metrics dashboard |
| **Process Planning** | Double Diamond | [research-frameworks.md](resources/research-frameworks.md#double-diamond) | Research roadmap |
| **Pain Point Extraction** | Review Mining + Sentiment Analysis | [pain-point-report-template.md](templates/feedback/pain-point-report-template.md) | Prioritized pain points |
| **Competitor Reviews** | B2B/B2C Review Mining | [competitor-review-matrix-template.md](templates/feedback/competitor-review-matrix-template.md) | Competitive gaps |

---

## Decision Tree: Choosing UX Research Approach

```text
UX Research Need: [What do you want to learn?]
    |
    +-- Evaluating existing product?
    |   +-- Systematic assessment needed? --> Heuristic Evaluation (resources/ux-audit-framework.md)
    |   +-- Understanding user behavior? --> Usability Testing (resources/usability-testing-guide.md)
    |   +-- Measuring satisfaction? --> UX Metrics (resources/ux-metrics-framework.md)
    |
    +-- Understanding user needs?
    |   +-- What job are users hiring product for? --> JTBD (resources/research-frameworks.md#jtbd)
    |   +-- What features matter most? --> Kano Model (resources/research-frameworks.md#kano-model)
    |   +-- End-to-end experience? --> Journey Mapping (resources/customer-journey-mapping.md)
    |
    +-- Comparing to competitors?
    |   +-- Feature gaps? --> Competitive Matrix (resources/competitive-ux-analysis.md)
    |   +-- UX patterns to adopt? --> Case Studies (resources/competitive-ux-analysis.md#case-studies)
    |   +-- Industry benchmarks? --> Baymard/NNg Data (data/sources.json)
    |
    +-- Planning research process?
    |   +-- New product/feature? --> Double Diamond (resources/research-frameworks.md#double-diamond)
    |   +-- Iterating existing? --> Design Thinking (resources/research-frameworks.md#design-thinking)
    |   +-- Service design? --> Service Blueprint (resources/customer-journey-mapping.md#service-blueprints)
    |
    +-- Prioritizing improvements?
    |   +-- Severity-based? --> Gap Analysis (resources/ux-audit-framework.md#prioritization)
    |   +-- Impact-based? --> Effort/Impact Matrix (resources/ux-audit-framework.md#prioritization)
    |   +-- Feature delight? --> Kano Classification (resources/research-frameworks.md#kano-model)
    |
    +-- Analyzing user feedback?
        +-- App Store/Play Store reviews? --> Review Mining (resources/review-mining-playbook.md#b2c)
        +-- B2B reviews (G2/Capterra/TrustRadius)? --> Review Mining (resources/review-mining-playbook.md#b2b)
        +-- Support tickets/NPS? --> Pain Point Extraction (resources/pain-point-extraction.md)
        +-- Which tools to use? --> Feedback Tools Guide (resources/feedback-tools-guide.md)
        +-- How do BigTech companies do it? --> BigTech Patterns (resources/bigtech-feedback-patterns.md)
```

---

## Navigation: Resources (Best Practices & Guides)

### Research Frameworks
- [resources/research-frameworks.md](resources/research-frameworks.md) - Comprehensive guide to JTBD, Kano Model, Double Diamond, Design Thinking, Service Blueprints, and Opportunity Solution Trees with actionable templates

### UX Evaluation
- [resources/ux-audit-framework.md](resources/ux-audit-framework.md) - Extended heuristic evaluation (Nielsen + Gerhardt-Powals), cognitive walkthrough protocol, severity rating system, gap analysis, and prioritization frameworks

### Customer Journey
- [resources/customer-journey-mapping.md](resources/customer-journey-mapping.md) - Persona development, 5-stage touchpoint mapping, pain point identification, emotional mapping, and service blueprint methodology

### Competitive Analysis
- [resources/competitive-ux-analysis.md](resources/competitive-ux-analysis.md) - Competitor selection, UX pattern analysis, case studies (OpenAI, Apple, Stripe, Notion, Linear, Figma, X, Spotify), and benchmarking frameworks

### Usability Testing
- [resources/usability-testing-guide.md](resources/usability-testing-guide.md) - Test type selection, task design, think-aloud protocol, remote testing tools, analysis and synthesis methods

### UX Metrics
- [resources/ux-metrics-framework.md](resources/ux-metrics-framework.md) - Task metrics (success rate, time-on-task), SUS scale, HEART framework, NPS/CSAT/CES, behavioral metrics, North Star identification

### User Feedback Analysis (NEW)

- [resources/pain-point-extraction.md](resources/pain-point-extraction.md) - Extract actionable pain points from any feedback source (App Store, Play Store, G2, support tickets, NPS) with prioritization scoring
- [resources/review-mining-playbook.md](resources/review-mining-playbook.md) - Practical guide to mining B2B (G2, Capterra, TrustRadius) and B2C (App Store, Play Store) reviews for competitive intelligence
- [resources/feedback-tools-guide.md](resources/feedback-tools-guide.md) - Tool setup tutorials for AppFollow, Appbot, G2 Seller, Linear Customer Requests, Dovetail, Hotjar, and GPT analysis prompts
- [resources/bigtech-feedback-patterns.md](resources/bigtech-feedback-patterns.md) - How Linear, Figma, Airbnb, OpenAI, Stripe, and unicorns handle user feedback (modular reference by problem type)

### AI-Assisted Research (2025)

AI tools can reduce qualitative analysis time by up to 80%. Key use cases:

| Task | AI Tool Category | Example Tools |
|------|------------------|---------------|
| **Interview transcription** | Speech-to-text | Otter.ai, Grain |
| **Thematic analysis** | Auto-tagging | Dovetail, Notably |
| **Pattern recognition** | Insight synthesis | Speak, Condens |
| **Research repository** | Knowledge management | Marvin, Dovetail |
| **Synthetic research** | User simulation | Synthetic Users |

**Best Practice**: AI assists analysis, not replaces human judgment. Always validate AI-generated insights against primary data.

See [data/sources.json](data/sources.json) `ai_assisted_research` category for tool links.

### External References

- [data/sources.json](data/sources.json) - 118 curated sources (Nielsen Norman Group, Baymard Institute, UXPA, top company design blogs, AI research tools, thought leaders)

---

## Navigation: Templates by Category

### Audit Templates
- [templates/audits/heuristic-evaluation-template.md](templates/audits/heuristic-evaluation-template.md) - Extended heuristic checklist with severity ratings
- [templates/audits/ux-audit-report-template.md](templates/audits/ux-audit-report-template.md) - Full audit report structure with prioritized recommendations

### Journey Templates
- [templates/journeys/customer-journey-canvas.md](templates/journeys/customer-journey-canvas.md) - 5-stage journey map with emotional curve
- [templates/journeys/service-blueprint-template.md](templates/journeys/service-blueprint-template.md) - Frontstage/backstage service design template

### Competitive Templates
- [templates/competitive/competitive-ux-matrix.md](templates/competitive/competitive-ux-matrix.md) - Feature and UX pattern comparison matrix

### Testing Templates
- [templates/testing/usability-test-plan.md](templates/testing/usability-test-plan.md) - Complete test plan with tasks, metrics, and script
- [templates/testing/think-aloud-protocol.md](templates/testing/think-aloud-protocol.md) - Facilitator guide and probing questions

### Metrics Templates

- [templates/metrics/ux-metrics-dashboard.md](templates/metrics/ux-metrics-dashboard.md) - UX health score dashboard with SUS, task metrics, and trends

### Feedback Templates (NEW)

- [templates/feedback/pain-point-report-template.md](templates/feedback/pain-point-report-template.md) - Structured pain point report with priority tiers, action items, and UI pattern mapping
- [templates/feedback/competitor-review-matrix-template.md](templates/feedback/competitor-review-matrix-template.md) - Competitive review analysis with switching triggers, feature gaps, and opportunity summary

---

## Related Skills (Cross-Functional)

- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) - **Implementation sibling**: Use after research to implement UI improvements (components, accessibility, design systems)
- [../product-management/SKILL.md](../product-management/SKILL.md) - **Discovery integration**: Shared frameworks (OST, customer interviews, strategy)
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) - **Implementation consumer**: Frontend applies UX research findings
- [../software-mobile/SKILL.md](../software-mobile/SKILL.md) - **Mobile UX**: Platform-specific UX patterns (iOS, Android)

---

## Operational Workflow

### Typical Research-to-Implementation Flow

```text
1. DISCOVER (this skill)
   +-- Stakeholder interviews
   +-- Competitive analysis
   +-- User research (JTBD)
   +-- Feedback analysis (reviews, support tickets)

2. EVALUATE (this skill)
   +-- UX audit (heuristics)
   +-- Usability testing
   +-- Journey mapping
   +-- Pain point extraction

3. PRIORITIZE (this skill)
   +-- Severity rating
   +-- Kano classification
   +-- Effort/Impact matrix
   +-- Frequency × Severity × Business Impact scoring

4. IMPLEMENT (software-ui-ux-design skill)
   +-- Design system updates
   +-- Component improvements
   +-- Accessibility fixes
   +-- Pain Point → UI Pattern mapping

5. MEASURE (this skill)
   +-- SUS scores
   +-- Task metrics
   +-- NPS/CSAT tracking
   +-- Review sentiment trends
```

### Feedback-Driven Development Flow

```text
USER ASKS                          SKILL FLOW
─────────────────────────────────────────────────────────────────
"Find pain points in reviews"   → pain-point-extraction.md → Pain Point Report
                                     ↓
"Find UI patterns for issues"   → Pain Points → software-ui-ux-design → Pattern Recommendations
                                     ↓
"How do BigTech handle this?"   → bigtech-feedback-patterns.md → Company Pattern Reference
```

---

## Usage Notes

**For Claude**: When user asks to "improve UX" or "fix usability issues":
1. First use this skill to analyze and identify problems
2. Generate recommendations with severity ratings
3. Then switch to `software-ui-ux-design` for implementation

**For Claude**: When user asks to "analyze reviews" or "find pain points":

1. Use `pain-point-extraction.md` for methodology
2. Use `review-mining-playbook.md` for platform-specific extraction
3. Output using `pain-point-report-template.md` format
4. Feed results to `software-ui-ux-design` for pattern selection

**Output Formats**:
- Audit findings: Severity-rated issue lists
- Journey maps: Visual canvas with touchpoints
- Competitive analysis: Feature/UX comparison tables
- Test results: Findings with video timestamps
- Metrics: Dashboard with benchmarks
- Pain point reports: Priority-tiered issues with UI pattern mapping
- Competitor reviews: Gap analysis with switching triggers

**Key Principle**: Research first, implement second. Never skip the analysis phase.
