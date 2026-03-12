# Domain-Specific Patterns (Claude 4+)

*Purpose: Claude 4-optimized patterns for specialized domains (frontend, research, agentic coding).*

## Contents
- Frontend / visual code patterns
- Research task patterns
- Agentic coding patterns
- Cross-domain best practices
- Claude 4.5 communication adaptations

---

## 1. Frontend / Visual Code Patterns

### 1.1 Encourage Maximum Creativity

**Pattern**:

Frame frontend requests with strong encouragement:

"Don't hold back. Give it your all. Create the most polished, creative interface possible."

**Why This Works** (Claude 4):

- Claude 4.x responds to quality modifiers in prompts
- Explicit encouragement produces more ambitious outputs
- Reduces conservative, minimal implementations

### 1.2 Request Multiple Design Options

**Pattern**:

```

Create 3 design variations for this component:
1. Minimal/clean
2. Bold/modern
3. Playful/creative

For each variation, include:
- Color scheme
- Typography choices
- Animation/interaction patterns

```

**Benefits**:

- Provides user choice
- Showcases Claude's design range
- Facilitates A/B testing

### 1.3 Specify Aesthetic Direction

**Be Explicit About**:

- Design system (Material, Tailwind, custom)
- Color palette constraints
- Animation preferences
- Accessibility requirements (WCAG level)
- Responsive breakpoints

**Example**:

```

Design a dashboard using:
- Tailwind CSS for styling
- Dark mode with purple accent (#8B5CF6)
- Smooth transitions (300ms ease-in-out)
- WCAG AA compliance minimum
- Mobile-first responsive (320px → 1440px)

Include micro-interactions on hover and click states.

```

### 1.4 Request Specific Features

**Anti-Pattern**:

"Make it interactive."

**Better**:

```text
Include these interactions:
- Hover: Scale card 1.05x with shadow increase
- Click: Ripple effect from click point
- Load: Stagger-fade children (100ms delay each)
- Scroll: Parallax header at 0.5x speed
```

### 1.5 Avoid "AI Slop" (2025)

**Problem**: AI-generated UIs often have recognizable, generic aesthetics that lack personality.

**Anti-Slop Checklist**:

| Avoid | Instead Use |
|-------|-------------|
| Default system fonts | Expressive, non-standard font choices |
| Flat, solid colors | Gradients, patterns, or textured backgrounds |
| No animations | Meaningful, selective animations |
| Generic layouts | Distinctive visual direction |
| Standard color palettes | Custom CSS variables defining unique themes |

**Pattern**:

```text
Frontend Design Requirements:
- Use expressive, non-standard font choices (not just Inter/Roboto)
- Define visual direction through CSS variables
- Include meaningful animations (not gratuitous)
- Build atmosphere with gradients or patterns, not flat colors
- Vary themes and design languages across outputs
- Avoid "AI look" - make it feel human-designed
```

**Example Prompt**:

```text
Create a dashboard that feels distinctive and human-designed.

Avoid:
- Generic AI aesthetics
- Default fonts and colors
- Flat, lifeless backgrounds

Include:
- A unique visual identity with custom color palette
- Typography with personality (consider: Space Grotesk, Instrument Serif, Clash Display)
- Subtle texture or gradient backgrounds
- Purposeful micro-interactions that feel natural
```

---

## 2. Research Task Patterns

### 2.1 Define Success Criteria

**Pattern**:

```

Research Task: [Topic]

Success Criteria:
- At least 3 sources from [timeframe]
- Primary sources preferred over secondary
- Must include [specific data types]
- Conflicting information must be noted
- Confidence level (high/medium/low) for each finding

```

### 2.2 Verification Across Sources

**Instruction Template**:

```

For each claim:
1. Identify the source
2. Check for corroboration in other sources
3. Note any contradictions
4. Assign confidence:
   - HIGH: 3+ sources agree
   - MEDIUM: 2 sources agree, or single authoritative source
   - LOW: Single source, no corroboration

```

### 2.3 Hypothesis Tracking

**Structure**:

```

Track hypotheses in structured format:

{
  "hypothesis": "statement",
  "evidence_for": ["source1", "source2"],
  "evidence_against": ["source3"],
  "confidence": "medium",
  "status": "partially_supported"
}

```

### 2.4 Explicit Missing Information

**Requirement**:

"If information is not found after thorough search, explicitly state:
- What was searched
- Where it was searched
- Why it might be unavailable
- Suggested alternative approaches"

---

## 3. Agentic Coding Patterns

### 3.1 No Speculation Rule

**Critical Instruction**:

"Never speculate about code you have not opened. You MUST read the file before answering questions about its implementation."

**Why This Matters**:

- Prevents hallucinated code structure
- Ensures accurate refactoring
- Avoids breaking existing patterns

**Pattern**:

```

Before answering:
1. Read the relevant files
2. Understand the actual implementation
3. Provide answer based on what exists, not assumptions

If file cannot be read → state explicitly: "Cannot access [file], need read permission to answer accurately."

```

### 3.2 Principled Implementation

**Anti-Pattern**:

"Implement a solution that passes the test cases."

**Better**:

"Implement a solution that works correctly for all valid inputs, not just test cases. Provide a principled implementation based on the problem requirements, not optimized for specific test inputs."

**Why**:

- Prevents overfitting to test cases
- Encourages general solutions
- Reduces brittle implementations

### 3.3 Avoid Test-Driven Hallucination

**Pattern**:

```

Implementation Requirements:
1. Understand the problem domain first
2. Design solution based on requirements, not tests
3. Ensure tests validate correctness, not define it
4. Handle edge cases beyond provided tests

Quality Check:
- Does this work for inputs not in test suite?
- Is the logic sound independent of test cases?
- Are edge cases handled properly?

```

### 3.4 Explicit Investigation Request

**Pattern for Complex Codebases**:

```

Investigation Steps:
1. Read [entry point file]
2. Trace execution path to [feature]
3. Identify all related files
4. Document actual behavior
5. Compare to expected behavior
6. Propose changes based on findings

Report Format:
- Files read: [list]
- Current behavior: [description]
- Root cause: [analysis]
- Proposed solution: [implementation]

```

---

## 4. Cross-Domain Best Practices

### 4.1 Quality Modifiers

Use descriptive adjectives to set expectations:

**Frontend**:

- "polished", "modern", "accessible", "responsive", "animated"

**Research**:

- "thorough", "verified", "cited", "comprehensive", "authoritative"

**Coding**:

- "production-ready", "maintainable", "tested", "documented", "performant"

### 4.2 Feature Explicitness

Never rely on Claude to infer what you want. State it explicitly:

**Vague**: "Make it better"
**Explicit**: "Improve performance by implementing memoization for expensive calculations and lazy loading for images"

### 4.3 Output Format Matching Domain

**Frontend**: Prefer complete code files over snippets
**Research**: Prefer structured data (JSON) with citations
**Coding**: Prefer diffs or full file replacements, not pseudocode

---

## 5. Claude 4.5 Communication Adaptations

### 5.1 Request Summaries When Needed

Claude 4.5 is more concise by default. If you need visibility:

"After completing this task involving tool use, provide a quick summary of your work including:
- What was changed
- Why it was changed
- Any trade-offs or decisions made"

### 5.2 Multi-Window Fresh Starts

**Pattern for Complex Tasks**:

"This is a multi-session task. After completing each major milestone:
1. Commit changes to git with descriptive message
2. Update progress.json with status
3. Document any blockers or open questions
4. Suggest next concrete step"

---

## Quick Reference

| Domain | Key Pattern | Critical Instruction |
|--------|-------------|---------------------|
| **Frontend** | Encourage creativity + specific features | "Don't hold back. Include [animations, interactions, etc.]" |
| **Research** | Success criteria + verification | "Verify across 3+ sources, note confidence level" |
| **Agentic Coding** | No speculation + principled solutions | "Never speculate. Read files first. Work for all inputs, not just tests." |

---

## Integration with Core Patterns

These domain-specific patterns **extend** (not replace) core patterns:

- Still use structured outputs (Section 4, best-practices-core.md)
- Still require explicit constraints (Section 2.2, best-practices-core.md)
- Still validate against quality checklists (quality-checklists.md)
- Still follow agent patterns for tool use (agent-patterns.md)

Domain patterns add **domain-specific guidance** on top of operational foundations.
