# Core Best Practices

*Purpose: Operational rules for building production-grade prompts for Claude Code.*

## Contents
- Foundation rules
- Content structuring
- Extraction best practices
- Structured output best practices
- RAG best practices
- Agent & tool best practices
- Rewrite & constrain best practices
- Quality validation
- Anti-patterns
- Quick reference table

---

# 1. Foundation Rules

## 1.1 Keep Tasks Atomic

Break complex user requests into micro-tasks.

Checklist:

- [ ] One task per prompt
- [ ] Clear success condition
- [ ] No ambiguous verbs ("analyze," "improve" without criteria)

## 1.2 Bias to Action (2025)

Frame instructions for implementation, not suggestion. Implement solutions using reasonable assumptions rather than requesting clarification.

**Action-Oriented Framing**:

- Replace: "Can you suggest changes to improve this function?"
- With: "Change this function to improve its performance."

**System Prompt Pattern**:

Include in system instructions for proactive behavior:

"By default, implement changes rather than only suggesting them. Take action on user requests unless explicitly asked to provide recommendations only. Use reasonable assumptions rather than asking for clarification."

**Autonomous Execution**:

- Do not prompt for intermediate status updates - this can cause abrupt stops
- Complete the full task end-to-end without waiting for approval between steps
- Work through implementation, verification, and explanation in a single turn

**Benefits**:

- Reduces back-and-forth iterations
- Modern LLMs are optimized for direct action
- More efficient workflows in code generation
- Fewer interruptions in agentic workflows

Checklist:

- [ ] Use imperative verbs (implement, change, create, fix)
- [ ] Avoid tentative language (suggest, consider, might)
- [ ] Specify action clearly in task description
- [ ] Minimize intermediate check-ins

---

## 1.3 Declare Output Format Early
Always specify the output shape before instructions.

Examples:
```

Output format: JSON

```
or
```

Return a Markdown table with these columns: …

```

Checklist:
- [ ] Output format appears before content rules  
- [ ] Format matches final output  
- [ ] No format drift  

---

## 1.4 Force Determinism
Operational prompts require predictable, testable output.

Patterns:
- Explicit schemas  
- Closed sets (e.g., “one of: A, B, C”)  
- Null fallback rules  

Checklist:
- [ ] Deterministic verbs (“must,” “only,” “always”)  
- [ ] No creative language  
- [ ] No synonyms allowed unless specified  

---

# 2. Content Structuring

## 2.1 Use Sections, Not Paragraphs

Operational prompts perform best when chunked.

Recommended order:

1. **Task**
2. **Instructions**
3. **Input**
4. **Constraints**
5. **Output Format**
6. **Quality Check**

Checklist:

- [ ] No blended sections
- [ ] Each structural block isolated in its own fenced code area

---

## 2.2 Use Positive Framing (Claude 4+)

Frame constraints as positive instructions rather than negations.

**Anti-Pattern (Negative)**:

- "Don't use markdown"
- "No invented facts"
- "Avoid vague language"

**Better (Positive)**:

- "Your response should be composed of smoothly flowing prose paragraphs"
- "Use only information provided in the context"
- "Use specific, concrete terms"

**Why This Works**:

- Claude 4.x responds better to explicit direction than prohibition
- Positive framing provides clear target behavior
- Reduces ambiguity about what to do instead

**When Negative Framing Is Acceptable**:

- Safety constraints ("No NSFW content")
- Critical prohibitions ("Never expose API keys")
- Format exclusions when positive alternative is obvious ("No markdown" + "Output: plain text")

Checklist:

- [ ] Constraints describe desired behavior, not just forbidden behavior
- [ ] Instructions specify what to include, not just what to omit
- [ ] Negative constraints reserved for safety/critical rules

---

## 2.3 Declare Constraints Explicitly

Examples (using positive framing where possible):

- "Use only information provided in the context"
- "For missing data, return null"
- "Use short sentences (max 15 words)"

Checklist:

- [ ] Constraints enforceable by a tester
- [ ] Each constraint testable in isolation

---

## 2.4 Reduce Cognitive Load

Guideline: Claude follows short, dense instructions more reliably.

Patterns:

- Bullet rules over prose
- Clear, unambiguous formatting
- Avoid metaphors, analogies

---

## 2.5 Style Matching (Claude 4+)

Your prompt's formatting influences Claude's output style.

**Principle**: The style you use in the prompt affects the style Claude uses in responses.

**Examples**:

- Markdown in prompt → More markdown in output
- Plain prose in prompt → Plain prose in output
- Bullet lists in prompt → Bullet lists in output
- XML tags in prompt → May use structured tags in output

**Application**:

```
If you want:
- Plain text output → Use minimal formatting in prompt
- Structured output → Use structured format in prompt
- Formal tone → Use formal language in prompt
- Conversational tone → Use conversational language in prompt
```

**Practical Use Case**:

For prose-heavy outputs (reports, documentation), reduce markdown and special formatting in your prompt structure. Use simple, clean text blocks.

Checklist:

- [ ] Prompt style matches desired output style
- [ ] Formatting choices are intentional
- [ ] Tone in prompt aligns with desired output tone

---

# 3. Extraction Best Practices

## 3.1 Set Hard Boundaries
Use mandatory schema enforcement:

```

Extract ONLY the fields in this schema:
{
  "field": "string|null"
}

```

Checklist:
- [ ] Missing values → null  
- [ ] Do not infer unstated data  
- [ ] Multi-candidate values → pick clearest or null  

---

## 3.2 No Transformation Without Rules
Examples:
- Dates: preserve original unless explicitly instructed  
- Numbers: preserve raw formatting  
- Text: no paraphrasing unless required  

---

# 4. Structured Output Best Practices

## 4.1 Strict JSON Mode
Always enforce:
- No comments  
- No trailing commas  
- One root object  
- Fields must appear in declared order  

Checklist:
- [ ] Claimed JSON validates via parser  
- [ ] No explanation outside JSON block  

---

## 4.2 Use Placeholders for Templates
Example:
```

{{input_text}}

```

Rules:
- Never mix real and placeholder content  
- One placeholder per conceptual input  

---

# 5. RAG Best Practices

## 5.1 Context Relevance Rules
```

Use retrieved_context ONLY if it contains direct evidence.
If irrelevant → ignore.
If missing → state explicitly.

```

Checklist:
- [ ] Context citations with [[chunk-n]]  
- [ ] No hallucinated references  
- [ ] No mixing memory + retrieval  

---

## 5.2 Evidence-First Reasoning
When grounding:
1. Identify relevant chunks  
2. Extract evidence  
3. Produce answer  
4. Cite  

Decision rules:
- No inference without textual support  
- No blending multiple unrelated chunks  

---

# 6. Agent & Tool Best Practices

## 6.1 One Tool Per Turn
```

If tool needed → produce plan → call tool.
Else → provide answer.

```

Checklist:
- [ ] No parallel tool calls  
- [ ] Plan included even when tool used  
- [ ] Answer only when no tool called  

---

## 6.2 Plan-First Behavior
Plan format:
- Step-by-step  
- Imperative verbs  
- No reasoning exposure  

Checklist:
- [ ] Plan present before action  
- [ ] Clear objective + method  

---

# 7. Rewrite & Constrain Best Practices

## 7.1 Meaning Preservation
Rules:
- Keep semantics  
- Remove filler  
- Maintain factual content  
- Match declared tone  

Checklist:
- [ ] All key information retained  
- [ ] No stylistic drift  

---

## 7.2 Format-Locked Transformations
Examples:
- Forced bullet style  
- Forced sentence length  
- Forced lexical constraints  

Checklist:
- [ ] Format fully matches required output  
- [ ] No extra commentary  

---

# 8. Quality Validation

## 8.1 Pre-flight Checklist
- [ ] Task is one sentence  
- [ ] Output shape unambiguous  
- [ ] Constraints complete  
- [ ] Input placeholder defined  
- [ ] Failure mode specified  
- [ ] Quality-check rules included  

---

## 8.2 Anti-Hallucination Rules
- Never create data not in input or schema  
- Never add sources not provided  
- State “Not found” when information is missing  

---

## 8.3 Regeneration Conditions
Automatic re-run when:
- Missing fields  
- Invalid JSON  
- Format drift  
- Constraint violations  

---

# 9. Anti-Patterns (Do Not Use)

- Open-ended instructions (“analyze”)  
- Visible reasoning unless requested  
- Nested paragraphs  
- Creative prose in operational prompts  
- Optional schemas  
- Soft requirements (“try,” “consider”)  
- Multi-task blending  
- Implicit formatting rules  

---

# Quick Reference Table

| Task | Pattern to Use | Template |
|------|----------------|----------|
| Structured result | JSON Pattern | template-standard.md |
| Entity extraction | Deterministic Extractor | template-json-extractor.md |
| RAG | RAG Workflow | template-rag.md |
| Agent/tool use | Tool Planner | template-agent.md |
| Rewrite/format | Rewrite + Constrain | template-standard.md |
