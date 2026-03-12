# UX Research Frameworks

Comprehensive guide to major UX research frameworks with operational templates and decision guidance.

---

## Framework Selection Guide

| Framework | Best For | Output | Time Investment |
|-----------|----------|--------|-----------------|
| **JTBD** | Understanding user motivations | Job statements, forces diagram | 2-4 weeks (interviews) |
| **Kano Model** | Feature prioritization | Priority matrix | 1-2 weeks (survey) |
| **Double Diamond** | New product/feature design | Research roadmap | Full project lifecycle |
| **Design Thinking** | Innovation, iteration | Prototypes, validated solutions | 2-6 weeks per cycle |
| **Service Blueprint** | End-to-end service design | Visual blueprint | 1-2 weeks |
| **OST** | Continuous discovery | Opportunity tree | Ongoing |

---

## Jobs-to-be-Done (JTBD)

### Core Concept

Users don't buy products - they "hire" them to make progress in their lives. Understanding the job reveals what truly matters.

### Job Statement Format

```text
When [SITUATION/TRIGGER]
I want to [MOTIVATION/ACTION]
So I can [EXPECTED OUTCOME/PROGRESS]
```

**Examples**:
- When **I'm commuting to work**, I want to **catch up on news**, so I can **feel informed for the day ahead**
- When **my team's code breaks production**, I want to **identify the root cause quickly**, so I can **restore service and reduce downtime**
- When **I receive a large document**, I want to **find specific information fast**, so I can **make decisions without reading everything**

### Three Types of Jobs

| Job Type | Definition | Example |
|----------|------------|---------|
| **Functional** | Practical task to accomplish | "Transfer money to a friend" |
| **Emotional** | How user wants to feel | "Feel secure about my finances" |
| **Social** | How user wants to be perceived | "Appear financially responsible" |

### Forces of Progress Diagram

```text
                    PROGRESS (Desired Outcome)
                           ^
                           |
    +----------------------+----------------------+
    |                      |                      |
    |   PUSH               |               PULL   |
    |   (Pain with         |        (Attraction   |
    |   current solution)  |        to new way)   |
    |                      |                      |
    +----------------------+----------------------+
                           |
                           |
    +----------------------+----------------------+
    |                      |                      |
    |   ANXIETY            |             HABIT    |
    |   (Fear of new       |        (Comfort with |
    |   solution)          |        status quo)   |
    |                      |                      |
    +----------------------+----------------------+
                           |
                           v
                    INERTIA (Current State)
```

**Push forces**: Problems with current solution driving change
**Pull forces**: Benefits of new solution attracting user
**Anxiety**: Uncertainty about new solution holding user back
**Habit**: Comfort with current way creating inertia

### JTBD Interview Questions

**Discovering the Job**:
1. "Tell me about the last time you [did the thing]. Walk me through it."
2. "What were you trying to accomplish?"
3. "What triggered you to start looking for a solution?"
4. "What alternatives did you consider?"

**Understanding Forces**:
5. "What wasn't working with your previous approach?" (Push)
6. "What excited you about the new solution?" (Pull)
7. "What concerns did you have before switching?" (Anxiety)
8. "What made it hard to change from your old way?" (Habit)

**Outcome Exploration**:
9. "How do you know when you've done this well?"
10. "What would make this 10x better?"

### JTBD to Opportunity Conversion

```text
Job Statement:
"When I'm reviewing code changes, I want to understand the impact quickly,
so I can approve or request changes confidently."

Opportunities:
1. Reduce time to understand code changes
2. Increase confidence in impact assessment
3. Surface potential issues automatically
4. Provide context from related changes

Solutions per Opportunity:
- Opportunity 1: Automated change summaries, visual diffs
- Opportunity 2: Automated test coverage indicators, risk scoring
- Opportunity 3: Static analysis integration, pattern detection
- Opportunity 4: Related PR linking, historical context
```

---

## Kano Model

### Core Concept

Not all features are equal. The Kano Model classifies features by their impact on satisfaction.

### Five Categories

| Category | If Present | If Absent | Strategy |
|----------|------------|-----------|----------|
| **Must-Have (Basic)** | Expected, no extra satisfaction | Severe dissatisfaction | Implement first, don't over-invest |
| **Performance (Linear)** | More = better satisfaction | Less = lower satisfaction | Invest based on competitive position |
| **Delighters (Attractive)** | Unexpected satisfaction | No dissatisfaction | Differentiate, but don't expect forever |
| **Indifferent** | No impact | No impact | Don't build |
| **Reverse** | Causes dissatisfaction | No issue | Avoid or make optional |

### Visual Model

```text
        Satisfaction
             ^
             |         Delighters
             |        /
             |       /
             |      /
             |-----/------ Performance
             |    /       /
             |   /       /
             |  /       /
-------------+----------+----------> Implementation
             |         /
             |        / Must-Haves
             |       /
             |      /
             |     /
             v
        Dissatisfaction
```

### Kano Questionnaire Design

For each feature, ask TWO questions:

**Functional Question** (if feature exists):
"If [feature] were available, how would you feel?"
- I would like it
- I expect it
- I am neutral
- I can tolerate it
- I dislike it

**Dysfunctional Question** (if feature doesn't exist):
"If [feature] were NOT available, how would you feel?"
- I would like it
- I expect it
- I am neutral
- I can tolerate it
- I dislike it

### Classification Matrix

| | Like | Expect | Neutral | Tolerate | Dislike |
|---|---|---|---|---|---|
| **Like** | Q | A | A | A | O |
| **Expect** | R | I | I | I | M |
| **Neutral** | R | I | I | I | M |
| **Tolerate** | R | I | I | I | M |
| **Dislike** | R | R | R | R | Q |

**Legend**: M=Must-Have, O=Performance, A=Attractive/Delighter, I=Indifferent, R=Reverse, Q=Questionable

### Kano Analysis Output

```text
Feature Prioritization Matrix

| Feature | Category | Satisfaction Impact | Priority |
|---------|----------|---------------------|----------|
| Login functionality | Must-Have | High if missing | P0 - Required |
| Search speed | Performance | Linear improvement | P1 - Optimize |
| Smart suggestions | Delighter | Positive surprise | P2 - Differentiate |
| Dark mode | Indifferent | No strong preference | P3 - Low priority |
| Auto-play videos | Reverse | Negative if present | Don't build |
```

### Kano Evolution Over Time

Features migrate categories over time:
- Yesterday's Delighter becomes today's Performance feature
- Today's Performance becomes tomorrow's Must-Have

**Example**: Mobile app → Delighter (2008) → Performance (2012) → Must-Have (2015)

---

## Double Diamond

### Core Concept

Design process alternates between divergent (exploring) and convergent (focusing) thinking across two phases: Problem and Solution.

### Four Phases

```text
        PROBLEM SPACE                    SOLUTION SPACE

    Discover          Define          Develop          Deliver
    (Diverge)        (Converge)      (Diverge)        (Converge)

       /\              /\              /\              /\
      /  \            /  \            /  \            /  \
     /    \          /    \          /    \          /    \
    /      \        /      \        /      \        /      \
   /        \      /        \      /        \      /        \
  /          \    /          \    /          \    /          \
 /            \  /            \  /            \  /            \
/              \/              \/              \/              \

Research      Problem         Ideation       Final
Insights      Statement       Concepts       Solution
```

### Phase Details

#### Phase 1: Discover (Diverge)
**Goal**: Understand the problem space broadly

**Activities**:
- User interviews
- Contextual inquiry
- Competitive analysis
- Market research
- Data analysis
- Stakeholder interviews

**Deliverables**:
- Research findings
- User personas
- Journey maps
- Problem hypotheses

**Duration**: 2-4 weeks

#### Phase 2: Define (Converge)
**Goal**: Frame the specific problem to solve

**Activities**:
- Affinity mapping
- Insight synthesis
- Problem framing
- Opportunity prioritization
- Design brief creation

**Deliverables**:
- Problem statement (POV)
- Design principles
- Success metrics
- Constraints definition

**Duration**: 1-2 weeks

#### Phase 3: Develop (Diverge)
**Goal**: Generate many possible solutions

**Activities**:
- Brainstorming
- Sketching
- Prototyping (low-fi)
- Concept testing
- Iteration

**Deliverables**:
- Multiple concepts
- Wireframes
- Low-fidelity prototypes
- Concept feedback

**Duration**: 2-4 weeks

#### Phase 4: Deliver (Converge)
**Goal**: Refine and ship the solution

**Activities**:
- High-fidelity prototyping
- Usability testing
- Iteration
- Implementation
- Launch

**Deliverables**:
- Final designs
- Design specs
- Implemented solution
- Success measurement

**Duration**: 4-8 weeks

### When to Use Double Diamond

- New product development
- Major feature redesign
- Entering new market
- Solving complex, ambiguous problems

---

## Design Thinking

### Core Concept

Human-centered design process emphasizing empathy, iteration, and rapid prototyping.

### Five Stages

```text
    EMPATHIZE --> DEFINE --> IDEATE --> PROTOTYPE --> TEST
        |                                              |
        +<-----------------ITERATE<--------------------+
```

#### Stage 1: Empathize
**Goal**: Understand users deeply

**Methods**:
- User interviews (1:1, contextual)
- Observation (shadowing, diary studies)
- Immersion (experience the user's world)

**Output**: Empathy maps, user quotes, observed behaviors

#### Stage 2: Define
**Goal**: Frame the problem clearly

**Point of View (POV) Format**:
```text
[USER] needs [NEED] because [INSIGHT]
```

**Example**:
"Busy parents need a way to quickly understand their child's school progress because they feel disconnected from their education despite caring deeply."

**Output**: POV statement, How Might We questions

#### Stage 3: Ideate
**Goal**: Generate many solutions

**Techniques**:
- Brainstorming (quantity over quality)
- SCAMPER (Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse)
- Worst possible idea (invert thinking)
- Analogous inspiration

**Rules**:
- Defer judgment
- Build on others' ideas
- One conversation at a time
- Go for quantity
- Be visual
- Stay on topic

**Output**: 50-100+ ideas, clustered themes, top concepts

#### Stage 4: Prototype
**Goal**: Make ideas tangible

**Fidelity Levels**:
| Level | Examples | Purpose | Time |
|-------|----------|---------|------|
| Paper | Sketches, paper screens | Quick concept validation | Minutes |
| Low-fi | Wireframes, clickable mockups | Flow validation | Hours |
| Mid-fi | Interactive prototypes | Interaction testing | Days |
| High-fi | Pixel-perfect, functional | Final validation | Weeks |

**Principle**: "If a picture is worth 1,000 words, a prototype is worth 1,000 meetings."

**Output**: Testable prototypes at appropriate fidelity

#### Stage 5: Test
**Goal**: Learn from users

**Methods**:
- Usability testing
- A/B testing
- Concept testing
- Wizard of Oz

**Mindset**:
- Prototype is wrong (you're testing to learn)
- Don't sell, observe
- Ask "why" frequently
- Test with real users

**Output**: Validated learnings, iteration priorities

---

## Service Blueprints

### Core Concept

Visualize the end-to-end service delivery showing both customer experience and operational processes.

### Blueprint Layers

```text
+------------------------------------------------------------------+
|                        PHYSICAL EVIDENCE                          |
| (Website, app, signage, emails, receipts, packaging)              |
+------------------------------------------------------------------+
|                                                                    |
|                        CUSTOMER ACTIONS                            |
| (What the customer does at each touchpoint)                        |
|                                                                    |
+==================================================================+
|                      LINE OF INTERACTION                           |
+==================================================================+
|                                                                    |
|                    FRONTSTAGE ACTIONS                              |
| (Visible employee actions, digital interfaces)                     |
|                                                                    |
+==================================================================+
|                      LINE OF VISIBILITY                            |
+==================================================================+
|                                                                    |
|                    BACKSTAGE ACTIONS                               |
| (Invisible employee actions, internal processes)                   |
|                                                                    |
+==================================================================+
|                   LINE OF INTERNAL INTERACTION                     |
+==================================================================+
|                                                                    |
|                    SUPPORT PROCESSES                               |
| (Systems, policies, third parties)                                 |
|                                                                    |
+------------------------------------------------------------------+
```

### Key Elements

**Physical Evidence**: Tangible elements customers interact with
**Customer Actions**: Steps customers take
**Frontstage**: Customer-facing interactions
**Backstage**: Behind-the-scenes activities
**Support Processes**: Systems and third parties

### Special Markers

| Marker | Symbol | Meaning |
|--------|--------|---------|
| Fail Point | (F) | Where things commonly go wrong |
| Wait Point | (W) | Where customers wait |
| Decision Point | (D) | Where paths diverge |
| Pain Point | (!) | Known friction area |

### Service Blueprint Example (E-commerce Order)

```text
Stage: ORDER PLACEMENT
+------------------------------------------------------------------+
| Evidence: Product page, cart, checkout, confirmation email        |
+------------------------------------------------------------------+
| Customer: Browse -> Add to cart -> Enter details -> Pay -> Confirm|
+==================================================================+
| Frontstage: Display inventory (F) -> Process payment -> Send email|
+==================================================================+
| Backstage: Check stock -> Validate payment -> Queue order (W)     |
+==================================================================+
| Support: Inventory DB -> Payment gateway -> Order management      |
+------------------------------------------------------------------+
```

### When to Use Service Blueprints

- Designing new services
- Improving existing service delivery
- Identifying operational inefficiencies
- Aligning cross-functional teams
- Handoff analysis

---

## Opportunity Solution Trees (OST)

### Core Concept

Visual framework connecting business outcomes to opportunities, solutions, and experiments.

### Tree Structure

```text
                    [OUTCOME]
                   What metric?
                        |
          +-------------+-------------+
          |             |             |
    [OPPORTUNITY] [OPPORTUNITY] [OPPORTUNITY]
    User pain/need  User pain/need  User pain/need
          |             |             |
     +----+----+   +----+----+   +----+----+
     |         |   |         |   |         |
[SOLUTION] [SOLUTION] [SOLUTION] [SOLUTION] [SOLUTION]
     |         |         |         |         |
[EXPERIMENT] [EXPERIMENT] [EXPERIMENT]
```

### Building an OST

**Step 1: Define Outcome**
- Business metric you're trying to move
- Example: "Increase 7-day retention by 15%"

**Step 2: Discover Opportunities**
- User research reveals pain points and unmet needs
- Frame as user needs, not features
- Example: "Users don't understand value in first session"

**Step 3: Generate Solutions**
- Multiple solutions per opportunity
- Don't fall in love with one idea
- Example: "Onboarding tutorial", "Personalized first experience", "Early quick win"

**Step 4: Run Experiments**
- Test assumptions cheaply
- Validate before building
- Example: "Prototype tutorial with 5 users"

### OST Integration with UX Research

| Research Method | OST Application |
|-----------------|-----------------|
| User interviews | Discover opportunities |
| JTBD | Frame opportunities as jobs |
| Usability testing | Validate solutions |
| A/B testing | Run experiments |
| Analytics | Measure outcomes |

**Note**: For detailed OST guidance, see [product-management skill](../../product-management/SKILL.md).

---

## Framework Combination Guide

### JTBD + Kano

Use JTBD to discover what jobs users hire products for, then use Kano to prioritize which job aspects to address first.

```text
JTBD Discovery --> Job Statements --> Kano Survey --> Priority Matrix
```

### Double Diamond + OST

Use Double Diamond for the overall project structure, OST for continuous discovery within each phase.

```text
Discover (DD) --> Opportunity Tree grows
Define (DD)   --> Select opportunities to pursue
Develop (DD)  --> Generate solutions per opportunity
Deliver (DD)  --> Experiment and ship
```

### Service Blueprint + Journey Map

Journey map shows customer experience; service blueprint adds operational reality.

```text
Journey Map (customer perspective)
        +
Service Blueprint (operational perspective)
        =
Complete service design view
```

---

## Framework Selection Decision Tree

```text
What's your primary question?
    |
    +-- "What do users really want?"
    |   +-- Deep motivations? --> JTBD
    |   +-- Feature priorities? --> Kano
    |
    +-- "How should we approach this project?"
    |   +-- New/ambiguous problem? --> Double Diamond
    |   +-- Need rapid iteration? --> Design Thinking
    |   +-- Continuous product? --> OST
    |
    +-- "How does our service work end-to-end?"
        +-- Customer focus? --> Journey Map
        +-- Operations focus? --> Service Blueprint
        +-- Both? --> Blueprint + Journey
```
