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
        +-- Severity-based? --> Gap Analysis (resources/ux-audit-framework.md#prioritization)
        +-- Impact-based? --> Effort/Impact Matrix (resources/ux-audit-framework.md#prioritization)
        +-- Feature delight? --> Kano Classification (resources/research-frameworks.md#kano-model)
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

2. EVALUATE (this skill)
   +-- UX audit (heuristics)
   +-- Usability testing
   +-- Journey mapping

3. PRIORITIZE (this skill)
   +-- Severity rating
   +-- Kano classification
   +-- Effort/Impact matrix

4. IMPLEMENT (software-ui-ux-design skill)
   +-- Design system updates
   +-- Component improvements
   +-- Accessibility fixes

5. MEASURE (this skill)
   +-- SUS scores
   +-- Task metrics
   +-- NPS/CSAT tracking
```

---

## Usage Notes

**For Claude**: When user asks to "improve UX" or "fix usability issues":
1. First use this skill to analyze and identify problems
2. Generate recommendations with severity ratings
3. Then switch to `software-ui-ux-design` for implementation

**Output Formats**:
- Audit findings: Severity-rated issue lists
- Journey maps: Visual canvas with touchpoints
- Competitive analysis: Feature/UX comparison tables
- Test results: Findings with video timestamps
- Metrics: Dashboard with benchmarks

**Key Principle**: Research first, implement second. Never skip the analysis phase.
