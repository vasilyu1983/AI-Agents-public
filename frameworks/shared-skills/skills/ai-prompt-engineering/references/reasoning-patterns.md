# Reasoning Patterns (Hidden CoT)

*Purpose: Provide deterministic reasoning workflows without exposing internal chain-of-thought.*

Claude must reason internally and return **only** the final answer unless explicitly requested otherwise.

## Contents
- When to use chain-of-thought
- Extended thinking and think tool
- Hidden reasoning contract
- Internal reasoning workflow
- Hidden-CoT answer pattern
- Reasoning types & associated patterns
- RAG-compatible hidden reasoning
- Agent-compatible hidden reasoning
- Classification reasoning
- Numeric / computational reasoning
- Decision tree reasoning (hidden)
- Handling uncertainty
- Anti-patterns
- Quick reference table

---

## 0. When to Use Chain-of-Thought (Research-Based Guidance)

**Key Finding**: Meta-analysis of 100+ papers shows CoT provides strong benefits **primarily on math and symbolic reasoning tasks**, with much smaller gains on other task types. ([arXiv:2409.12183](https://arxiv.org/abs/2409.12183))

### Use CoT When

- **Mathematical reasoning** - Arithmetic, algebra, word problems
- **Symbolic/logical reasoning** - Formal logic, puzzles, constraint satisfaction
- **Multi-step computations** - Financial calculations, unit conversions
- **Complex classification** - When decision requires evaluating multiple criteria in sequence

### Avoid CoT When

- **Simple factual retrieval** - Direct knowledge lookup (CoT adds latency, no accuracy gain)
- **Text generation** - Creative writing, summaries (reasoning doesn't improve quality)
- **Single-step classification** - Binary decisions, sentiment analysis
- **Pattern matching** - Named entity recognition, format extraction
- **Direct recall tasks** - Q&A from provided context

### Cost-Benefit Tradeoff

| Task Type | CoT Benefit | Latency Cost | Recommendation |
|-----------|-------------|--------------|----------------|
| Math reasoning | High (+15-30%) | High | Use CoT |
| Symbolic logic | High (+10-25%) | High | Use CoT |
| Complex classification | Medium (+5-10%) | Medium | Conditional |
| Factual Q&A | Low (<3%) | Medium | Skip CoT |
| Text generation | Negligible | High | Skip CoT |
| Simple extraction | Negligible | Medium | Skip CoT |

### Alternative: CoT Without Prompting

Recent research shows CoT reasoning can be elicited through **decoding changes** rather than explicit prompting—by examining top-k alternative tokens. This reveals that reasoning paths are often inherent in the model. ([arXiv:2402.10200](https://arxiv.org/abs/2402.10200))

**Implication**: For production systems, consider whether explicit CoT prompts are necessary, or if the model's native reasoning suffices.

---

## 0.5 Extended Thinking (Claude 4+)

Claude's native extended thinking feature allows deep reasoning before response generation. This is distinct from traditional CoT prompting.

### Extended Thinking vs Think Tool vs CoT Prompting

| Feature | Extended Thinking | Think Tool | CoT Prompting |
|---------|------------------|------------|---------------|
| **When** | Before response generation | During response generation | In response itself |
| **Control** | API parameter (budget_tokens) | Tool call in system prompt | Prompt instructions |
| **Visibility** | Thinking blocks (optional) | Tool output | Visible in response |
| **Best for** | Complex reasoning, math, coding | Multi-step tool use, verification | Simple step-by-step |

### When to Use Extended Thinking

**Use Extended Thinking for**:
- Complex coding and debugging
- Mathematical reasoning
- Multi-step analysis before any tool calls
- Physics and scientific problems
- Tasks requiring deep consideration before action

**Use Think Tool for**:
- Sequential tool use where mid-task reflection helps
- Verifying if enough information gathered before proceeding
- Complex agentic workflows with multiple decision points

### Extended Thinking Best Practices

**1. High-Level Over Prescriptive**:

Claude performs better with high-level instructions than step-by-step prescriptive guidance:

```text
# Good
Think deeply about this problem and find the optimal solution.

# Avoid (wastes tokens with Extended Thinking enabled)
Think step-by-step. First, analyze X. Then, consider Y. Finally, determine Z.
```

**2. Token Budget Management**:

| Task Complexity | Recommended Budget | Notes |
|-----------------|-------------------|-------|
| Simple | 1024 (minimum) | Default starting point |
| Moderate | 4K-8K | Most coding tasks |
| Complex | 16K-32K | Multi-file analysis |
| Very Complex | 32K+ | Use batch processing |

**3. Multishot with Extended Thinking**:

Include few-shot examples using `<thinking>` or `<scratchpad>` tags to demonstrate reasoning patterns:

```text
Example:
<thinking>
First, I'll identify the key constraints...
Then, I'll consider edge cases...
</thinking>
Answer: [result]

Now solve: {{new_problem}}
```

**4. Avoiding Redundancy**:

Do NOT include with Extended Thinking enabled:
- "Think step-by-step" (redundant)
- "Let's work through this" (redundant)
- "First, let me analyze..." (the model manages its own reasoning)

**5. Longer Outputs**:

For detailed responses, increase BOTH:
- Extended thinking budget (max_thinking_tokens)
- Output max tokens

```text
When generating detailed analysis:
1. Set thinking budget: 16K+
2. Set max_tokens: appropriate for output length
3. Explicitly request: "Provide a comprehensive analysis with..."
```

### Think Tool Pattern

For agentic workflows, add a "think" tool to pause and reflect:

```json
{
  "name": "think",
  "description": "Use this tool to stop and think about whether you have all the information needed to proceed, or whether you should gather more information first.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "Your reflection on the current state and next steps"
      }
    },
    "required": ["thought"]
  }
}
```

**When to call think tool**:
- Before making irreversible actions
- When multiple tools could apply
- After receiving unexpected results
- Before completing a complex multi-step task

### Checklist

- [ ] Extended thinking enabled for complex reasoning tasks
- [ ] Token budget appropriate for task complexity
- [ ] No redundant step-by-step instructions
- [ ] Think tool added for agentic workflows requiring mid-task reflection
- [ ] Multishot examples use `<thinking>` tags when demonstrating reasoning

---

## 1. Hidden Reasoning Contract

Rules:
- Perform all reasoning internally.  
- Output only the final result in the required format.  
- Never include `<thinking>` unless the user explicitly demands visible reasoning.  
- Keep answers short, factual, deterministic.  
- No ambiguity, no filler, no narrative.  

Checklist:
- [ ] No visible reasoning markers  
- [ ] Final answer only  
- [ ] Output shape exact  
- [ ] No speculative language  
- [ ] No invented facts  

---

## 2. Internal Reasoning Workflow

Use this multi-step internal workflow for every reasoning task:

1. Parse the task into a single objective  
2. Identify required data  
3. Isolate constraints  
4. Build a silent step-by-step solution  
5. Validate against format + constraints  
6. Produce the final answer only  

**Nothing from steps 1–5 may appear in the output.**

---

## 3. Hidden-CoT Answer Pattern

### 3.1 Structure

```

{{final_answer_only}}

```

Rules:
- No explanation  
- No intermediate steps  
- No justification unless required by schema  
- Keep the tone operational  

---

## 4. Reasoning Types & Associated Patterns

Below are approved reasoning patterns Claude may use internally (never revealed).

---

## 4.1 Deductive Pattern (Internal)
Use when task requires applying rules to facts.

Internal steps (not shown):
- Match fact → rule  
- Apply rule deterministically  
- Produce outcome  

Output:
```

{{final_answer}}

```

---

## 4.2 Analytical Pattern (Internal)
Use for comparisons, evaluations, or transformations.

Internal steps (not shown):
- Break down components  
- Evaluate against criteria  
- Choose deterministic result  

Output:
```

{{final_answer}}

```

---

## 4.3 Multi-Step Logical Pattern (Internal)
Use for multi-operation tasks.

Internal steps (not shown):
- Sequence sub-steps  
- Execute operations  
- Validate intermediate structure  
- Generate final result  

Output:
```

{{result}}

```

---

## 4.4 Evidence-Based Pattern (Internal)
Use when data must be extracted then synthesized.

Internal steps (not shown):
- Identify relevant data  
- Extract verbatim values  
- Produce synthesis strictly from evidence  

Output:
```

{{answer}}

```

---

## 5. RAG-Compatible Hidden Reasoning

When used with RAG:
- Use evidence-only logic  
- Cite only when required  
- No chain-of-thought about relevance  
- No invented connections  

Output pattern:
```

Answer:
...
Sources:

- [[chunk-1]]

```

Checklist:
- [ ] Evidence matches retrieval  
- [ ] No inference beyond context  

---

## 6. Agent-Compatible Hidden Reasoning

When using tools:
- All deliberation internal  
- Plans are allowed (operational, short, no reasoning)  
- Tool decisions cannot reveal why  

Allowed plan pattern:
```

Plan:

- step 1
- step 2

Action:
{...}

Answer:
null

```

Checklist:
- [ ] Plan contains actions only, never reasoning  
- [ ] No heuristics or justification  

---

## 7. Classification Reasoning

Reasoning rules:
- Use closed-set logic internally  
- Default to “unknown” when unclear  
- No probability disclosures  

Output pattern:
```

{
  "class": "A|B|C|unknown"
}

```

Checklist:
- [ ] Class deterministic  
- [ ] No “likely/probably”  

---

## 8. Numeric / Computational Reasoning

Allowed:
- Internal arithmetic  
- Internal validation  
- Internal unit consistency  

Not allowed:
- Showing steps  
- Explaining calculations  

Output:
```

{{numeric_result}}

```

---

## 9. Decision Tree Reasoning (Hidden)

Decision trees must be executed silently.

Internal:
- Evaluate branches in order  
- Pick first true condition  
- Ignore others  

Output:
```

{"class": "..."}

```

Checklist:
- [ ] No branch logic exposed  
- [ ] Result matches deterministic node  

---

## 10. Handling Uncertainty

If input insufficient:
```

"unknown"

```
or schema-defined fallback (e.g., null).

Rules:
- Never guess  
- Never explain  
- Never expose uncertainty rationale  

---

## 11. Anti-Patterns (Forbidden)

Do not:
- Include visible reasoning  
- Mention steps, decisions, logic  
- Say “based on my analysis”  
- Provide long explanations  
- Reveal rule application  
- Reveal evidence selection process  
- Expose internal ambiguity handling  
- Offer probability statements  

---

## 12. Quick Reference Table

| Scenario | Pattern | Output |
|----------|---------|---------|
| Multi-step reasoning | Multi-Step Logical | Final answer only |
| Rule-based | Deductive | Deterministic result |
| Comparison | Analytical | Direct output |
| Evidence-based RAG | RAG Hidden-CoT | Answer + citations |
| Tool use | Agent-Compatible | Plan + action/answer |
| Classification | Closed-set | JSON object |
