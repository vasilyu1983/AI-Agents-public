---
name: startup-mega-router
description: Master orchestration for routing startup problems through 60+ skills for comprehensive analysis and validation
version: "1.1"
---

# Startup Mega Router

Master orchestrator that routes startup problems, ideas, and opportunities through the complete skill set for comprehensive analysis.

---

## Decision Tree: Where to Start?

```
USER INPUT
    |
    +---> "I have an idea" ---------------> startup-idea-validation
    |                                        |-> 9-dimension scoring
    |
    +---> "Find opportunities in X" ------> startup-review-mining
    |                                        |-> Pain extraction from reviews
    |
    +---> "What's trending in X" ---------> startup-trend-prediction
    |                                        |-> 2-3yr lookback -> 1-2yr forward
    |
    +---> "Analyze competitors" ----------> startup-competitive-analysis
    |                                        |-> Positioning, moats, battlecards
    |
    +---> "Pricing / business model" -----> startup-business-models
    |                                        |-> Unit economics, pricing tiers
    |
    +---> "Build X feature/product" ------> Technical Skills Chain
    |                                        |-> Architecture -> Implementation
    |
    +---> "Go to market with X" ----------> startup-go-to-market
    |                                        |-> Positioning -> Channels -> Launch
    |
    +---> "Raise funding" ----------------> startup-fundraising
    |                                        |-> Pitch, valuation, term sheets
    |
    +---> "Scale agent fleet" ------------> agent-fleet-operations
    |                                        |-> Orchestration, monitoring, costs
    |
    +---> "UX research / user feedback" --> software-ux-research
    |                                        |-> Pain patterns, feedback mining
    |
    +---> "UI design / design system" ----> software-ui-ux-design
    |                                        |-> Components, accessibility, patterns
    |
    +---> "Full analysis of X" -----------> COMPREHENSIVE ANALYSIS
                                             |-> All relevant skills in parallel
```

---

## Stage Detection

### Stage 1: OPPORTUNITY DISCOVERY

**Triggers**: "opportunity", "gap", "problem", "pain point", "market", "whitespace"

**Primary Skills**:
- `startup-review-mining` - Extract pain from reviews
- `startup-trend-prediction` - Identify rising trends
- `software-ux-research` - User research methods

**Skill Chain**:
```
Review Mining --> Pain Points --> Trend Alignment --> Opportunity Score
```

### Stage 2: IDEA VALIDATION

**Triggers**: "idea", "validate", "test", "hypothesis", "should I build"

**Primary Skills**:
- `startup-idea-validation` - 9-dimension scoring
- `product-management` - Discovery, OST, customer interviews

**Skill Chain**:
```
Hypothesis Canvas --> RAT Testing --> Scorecard --> Go/No-Go
```

### Stage 3: MARKET & COMPETITIVE ANALYSIS

**Triggers**: "market size", "competitors", "TAM", "landscape", "industry", "positioning"

**Primary Skills**:
- `startup-competitive-analysis` - Competitive intelligence, positioning
- `startup-idea-validation` - Market sizing worksheet
- `startup-trend-prediction` - Market cycle patterns

**Skill Chain**:
```
Market Sizing --> Competitive Analysis --> Positioning --> Battlecards
```

### Stage 4: BUSINESS MODEL & PRICING

**Triggers**: "pricing", "monetization", "revenue model", "unit economics", "business model"

**Primary Skills**:
- `startup-business-models` - Revenue models, unit economics
- `startup-competitive-analysis` - Competitive pricing analysis

**Skill Chain**:
```
Revenue Model Selection --> Unit Economics --> Pricing Strategy --> Tier Design
```

### Stage 5: TECHNICAL PLANNING

**Triggers**: "build", "architecture", "implement", "technical", "stack"

**Primary Skills**:
- `software-architecture` - System design
- `software-backend-*` - Backend frameworks
- `software-frontend-*` - Frontend frameworks
- `ai-*` skills - AI/ML components

**Skill Chain**:
```
Requirements --> Architecture --> Technology Selection --> Implementation Plan
```

### Stage 6: UX & DESIGN

**Triggers**: "UX", "user experience", "design", "UI", "interface", "usability", "accessibility"

**Primary Skills**:
- `software-ux-research` - User research, pain pattern extraction
- `software-ui-ux-design` - Design systems, components, accessibility

**Skill Chain**:
```
User Research --> Pain Patterns --> Design System --> Components --> Testing
```

### Stage 7: GO-TO-MARKET

**Triggers**: "launch", "GTM", "marketing", "sales", "growth", "channels"

**Primary Skills**:
- `startup-go-to-market` - GTM strategy, channels, launch planning
- `product-management` - Positioning, roadmap
- `marketing-*` skills - Channels, content

**Skill Chain**:
```
ICP Definition --> Positioning --> Channel Strategy --> Launch Plan --> Growth Loops
```

### Stage 8: FUNDRAISING

**Triggers**: "funding", "raise", "investors", "pitch", "term sheet", "valuation"

**Primary Skills**:
- `startup-fundraising` - Pitch prep, valuation, term sheets
- `startup-business-models` - Unit economics for investors

**Skill Chain**:
```
Stage Assessment --> Materials Prep --> Investor Targeting --> Pitch --> Negotiation
```

### Stage 9: AGENT OPERATIONS

**Triggers**: "agent fleet", "multi-agent", "agent service", "orchestration", "agent costs"

**Primary Skills**:
- `agent-fleet-operations` - Fleet management, economics
- `ai-agents` - Agent architecture

**Skill Chain**:
```
Service Design --> Agent Config --> Orchestration --> Monitoring --> Cost Optimization
```

---

## Comprehensive Analysis Mode

For full opportunity analysis, invoke skills in parallel:

### Layer 1: Discovery (Parallel)

| Skill | Output | Purpose |
|-------|--------|---------|
| `startup-review-mining` | Pain points, feature gaps | What customers hate |
| `startup-trend-prediction` | Rising/peaking trends | Market timing |
| `software-ux-research` | User research insights | Deep user understanding |
| `startup-competitive-analysis` | Competitor weaknesses | Where to attack |

### Layer 2: Validation (Sequential)

| Skill | Input From | Output |
|-------|-----------|--------|
| `startup-idea-validation` | Layer 1 outputs | Validation scorecard |
| `startup-business-models` | Validation | Unit economics model |

### Layer 3: Planning (Based on Verdict)

**If GO (80+)**:
- `startup-business-models` - Revenue model design
- `startup-go-to-market` - GTM strategy
- `product-management` - Roadmap
- `software-architecture` - Technical plan
- Technical implementation skills

**If Conditional (60-79)**:
- Focus on riskiest assumptions
- Targeted experiments
- `startup-competitive-analysis` - Deeper competitive intel

**If Pivot/No-Go (<60)**:
- Alternative direction analysis
- New opportunity discovery
- `startup-review-mining` - Different market

---

## Skill Registry

### Startup Validation Suite (9 skills)

| Skill | Purpose | Key Outputs |
|-------|---------|-------------|
| `startup-mega-router` | Orchestration | Routing decisions, skill chains |
| `startup-idea-validation` | Systematic scoring | 9-dimension scorecard, Go/No-Go |
| `startup-review-mining` | Pain extraction | Pain points, opportunities |
| `startup-trend-prediction` | Future prediction | Trend analysis, timing |
| `startup-competitive-analysis` | Competitive intel | Positioning, moats, battlecards |
| `startup-business-models` | Revenue design | Unit economics, pricing |
| `startup-go-to-market` | GTM strategy | Channels, launch, growth |
| `startup-fundraising` | Capital raising | Pitch, valuation, terms |
| `agent-fleet-operations` | Agent services | Fleet management, economics |

### Product & UX (3 skills)

| Skill | Purpose | Key Outputs |
|-------|---------|-------------|
| `product-management` | Product strategy | Discovery, OST, roadmaps |
| `software-ux-research` | User research | Pain patterns, feedback mining |
| `software-ui-ux-design` | Design systems | UI patterns, accessibility |

### Technical Implementation (15+ skills)

| Category | Skills |
|----------|--------|
| Backend | `software-backend-nodejs`, `software-backend-python`, `software-backend-go`, etc. |
| Frontend | `software-frontend-nextjs`, `software-frontend-nuxt`, `software-frontend-angular`, etc. |
| Mobile | `software-mobile` (iOS, Android, React Native) |
| Data | `software-database-sql`, `software-data-engineering` |
| DevOps | `software-devops`, `software-cicd` |

### AI/ML (5+ skills)

| Skill | Purpose |
|-------|---------|
| `ai-agents` | Multi-agent systems |
| `ai-llm-development` | LLM applications, RAG |
| `ai-ml-data-science` | ML workflows, modeling |
| `ai-prompt-engineering` | Prompt design |
| `ai-fine-tuning` | Model customization |

### Marketing & Growth (4+ skills)

| Skill | Purpose |
|-------|---------|
| `marketing-social-media` | Social strategy |
| `marketing-leads-generation` | Acquisition |
| `marketing-copywriting` | Content |
| `marketing-seo` | Organic growth |

### Specialized (10+ skills)

| Skill | Purpose |
|-------|---------|
| `software-security` | AppSec, OWASP |
| `software-testing` | QA, test strategy |
| `blockchain-solidity` | Smart contracts |
| `foundation-documentation` | Technical writing |

See `data/skill-registry.json` for complete registry.

---

## Routing Logic

### Keyword-Based Routing

```
KEYWORDS -> SKILL MAPPING

"pain point", "frustration", "complaint" -> startup-review-mining
"trend", "predict", "future", "rising" -> startup-trend-prediction
"validate", "test", "hypothesis", "idea" -> startup-idea-validation
"competitor", "competitive", "positioning", "moat" -> startup-competitive-analysis
"pricing", "revenue model", "unit economics" -> startup-business-models
"GTM", "go to market", "launch", "channels" -> startup-go-to-market
"funding", "raise", "investors", "pitch" -> startup-fundraising
"agent fleet", "orchestration", "agent service" -> agent-fleet-operations
"discovery", "interview", "OST" -> product-management
"user research", "feedback", "pain patterns" -> software-ux-research
"design", "UI", "components", "accessibility" -> software-ui-ux-design
"API", "backend", "database" -> software-backend-*
"frontend", "React", "Vue", "Angular" -> software-frontend-*
"mobile", "iOS", "Android", "app" -> software-mobile
"AI", "ML", "LLM", "agent" -> ai-*
"deploy", "CI/CD", "infrastructure" -> software-devops
"security", "OWASP", "vulnerability" -> software-security
"marketing", "growth", "acquisition" -> marketing-*
```

### Context-Based Routing

| User Context | Primary Skill | Supporting Skills |
|--------------|---------------|-------------------|
| Pre-idea (exploring) | `startup-review-mining` | `startup-trend-prediction`, `software-ux-research` |
| Has idea (validating) | `startup-idea-validation` | `product-management`, `startup-competitive-analysis` |
| Validated (planning) | `startup-business-models` | `startup-go-to-market` |
| Planning (building) | Technical skills | `software-architecture`, `software-ui-ux-design` |
| Built (launching) | `startup-go-to-market` | `marketing-*` |
| Growing (scaling) | All relevant | Based on bottleneck |
| Raising (funding) | `startup-fundraising` | `startup-business-models` |
| Scaling agents | `agent-fleet-operations` | `ai-agents` |

---

## Skill Chain Patterns

### Pattern 1: Idea-to-Validation

```
START
  |
  v
startup-review-mining -----> Pain Points Extracted
  |
  v
startup-trend-prediction --> Timing Assessment
  |
  v
startup-competitive-analysis -> Competitive Position
  |
  v
startup-idea-validation ----> 9-Dimension Score
  |
  v
GO/NO-GO DECISION
```

### Pattern 2: Opportunity-to-Product

```
START
  |
  v
startup-review-mining ------> Opportunity Identified
  |
  v
startup-competitive-analysis -> Positioning
  |
  v
startup-business-models -----> Revenue Model
  |
  v
product-management ----------> PRD + Roadmap
  |
  v
software-ui-ux-design -------> Design System
  |
  v
software-architecture -------> Technical Design
  |
  v
Implementation Skills -------> Built Product
```

### Pattern 3: Market-to-Launch

```
START
  |
  v
startup-trend-prediction ----> Market Timing
  |
  v
startup-idea-validation -----> Market Sizing
  |
  v
startup-competitive-analysis -> Positioning
  |
  v
startup-business-models -----> Pricing Strategy
  |
  v
startup-go-to-market --------> GTM Plan
  |
  v
marketing-* skills ----------> GTM Execution
```

### Pattern 4: Validation-to-Funding

```
START
  |
  v
startup-idea-validation -----> Validated Idea
  |
  v
startup-business-models -----> Unit Economics
  |
  v
startup-competitive-analysis -> Moat Analysis
  |
  v
startup-fundraising ---------> Pitch Materials
  |
  v
INVESTOR MEETINGS
```

### Pattern 5: Agent Service Launch

```
START
  |
  v
ai-agents -------------------> Agent Architecture
  |
  v
agent-fleet-operations ------> Service Design
  |
  v
startup-business-models -----> Pricing Model
  |
  v
startup-go-to-market --------> Launch Strategy
  |
  v
AGENT SERVICE LIVE
```

---

## Output Templates

### Quick Analysis Output

```markdown
## Analysis: {{TOPIC}}

**Stage Detected**: {{STAGE}}
**Primary Skill**: {{SKILL}}
**Supporting Skills**: {{LIST}}

### Key Findings
1. {{FINDING_1}}
2. {{FINDING_2}}
3. {{FINDING_3}}

### Recommended Next Steps
1. {{ACTION_1}} - Use {{SKILL}}
2. {{ACTION_2}} - Use {{SKILL}}

### Skills to Invoke Next
- {{SKILL_1}}: {{WHY}}
- {{SKILL_2}}: {{WHY}}
```

### Comprehensive Analysis Output

See `templates/comprehensive-analysis-report.md`

---

## Resources

| Resource | Purpose |
|----------|---------|
| [routing-logic.md](resources/routing-logic.md) | Detailed decision trees |
| [skill-chain-patterns.md](resources/skill-chain-patterns.md) | Sequential/parallel patterns |
| [opportunity-detection-rules.md](resources/opportunity-detection-rules.md) | Opportunity scoring |

## Templates

| Template | Purpose |
|----------|---------|
| [comprehensive-analysis-report.md](templates/comprehensive-analysis-report.md) | Full analysis |
| [skill-routing-decision.md](templates/skill-routing-decision.md) | Routing documentation |
| [hypothesis-test-plan.md](templates/hypothesis-test-plan.md) | Experiment planning |

## Data

| File | Purpose |
|------|---------|
| [skill-registry.json](data/skill-registry.json) | Complete skill index |
| [sources.json](data/sources.json) | Reference sources |
