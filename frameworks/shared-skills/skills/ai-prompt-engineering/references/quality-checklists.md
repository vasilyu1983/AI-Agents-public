# Quality Checklists

Validation checklists for ensuring prompt quality before deployment.

## Contents
- Prompt QA checklist
- JSON validation checklist
- Agent workflow checks
- RAG workflow checks
- Safety & security checks
- Performance optimization checks
- Testing coverage checklist
- Common anti-patterns to avoid
- Quality score rubric

---

## Prompt QA Checklist

Use this checklist before deploying any prompt:

- [ ] **Task** = one sentence (clear, unambiguous)
- [ ] **Output shape** explicit (JSON/table/bullets/prose)
- [ ] **Forbidden outputs** stated (no hallucinations, no invented data)
- [ ] **Edge cases** handled (missing data, ambiguous input, invalid format)
- [ ] **Failure mode** defined (what happens when prompt can't complete task)
- [ ] **Examples** included if needed (2-5 examples for complex tasks)
- [ ] **Deterministic language** (avoid "try", "maybe", "probably")

---

## JSON Validation Checklist

For prompts that output JSON:

- [ ] **One root object** (no arrays or multiple objects at root)
- [ ] **All fields defined** (no dynamic keys unless specified)
- [ ] **Types correct** (string/number/boolean/array/object)
- [ ] **Strings only** (no comments, no trailing commas)
- [ ] **Arrays typed** (specify element type and structure)
- [ ] **Null handling** (specify which fields can be null)
- [ ] **No prose outside JSON** (JSON-only output enforced)

---

## Agent Workflow Checks

For tool-using or multi-step agents:

- [ ] **Plan before action** (agent states plan before calling tools)
- [ ] **One tool per turn** (no parallel tool calls unless specified)
- [ ] **Final answer only after tool completion** (don't answer before tools run)
- [ ] **Missing context → explicit** (state what's missing, don't proceed)
- [ ] **State uncertainty explicitly** (use confidence indicators when appropriate)
- [ ] **Tool validation** (inputs validated against schema before calling)
- [ ] **Error handling** (define behavior when tools fail)

---

## RAG Workflow Checks

For retrieval-augmented generation prompts:

- [ ] **Context relevance check** (only use context if relevant)
- [ ] **Citation format** (specify how to cite chunks/sources)
- [ ] **Missing info handling** (state when context doesn't contain answer)
- [ ] **No hallucination** (don't answer without supporting context)
- [ ] **Chunk ID format** (consistent citation style: [[chunk-1]])
- [ ] **Confidence markers** (indicate when answer is partial/uncertain)
- [ ] **Context boundaries** (clear separation of context from instructions)

---

## Safety & Security Checks

Before production deployment:

- [ ] **Refusal instructions** (how to refuse inappropriate requests)
- [ ] **Prompt injection defense** (ignore embedded instructions)
- [ ] **PII handling** (don't expose sensitive information)
- [ ] **Toxic input handling** (reject hate speech, illegal content)
- [ ] **Tool safety** (validate tool inputs, allowlists for sensitive ops)
- [ ] **Context injection defense** (treat retrieved context as untrusted)
- [ ] **Red team testing** (tested against jailbreaks, injections)

---

## Performance Optimization Checks

For production efficiency:

- [ ] **Token budget** (stays within cost/latency targets)
- [ ] **Max tokens set** (prevents runaway generation)
- [ ] **Temperature appropriate** (0-0.2 for deterministic, higher for creative)
- [ ] **Stop sequences** (prevents spillover into unwanted content)
- [ ] **Caching strategy** (reuse common prefixes when possible)
- [ ] **Batch processing** (group similar requests when applicable)

---

## Testing Coverage Checklist

Before release:

- [ ] **Happy path** (normal, expected inputs)
- [ ] **Edge cases** (boundary conditions, unusual inputs)
- [ ] **Failure modes** (invalid inputs, missing data)
- [ ] **Adversarial cases** (prompt injections, jailbreaks)
- [ ] **Performance benchmarks** (latency, token usage)
- [ ] **Safety tests** (toxic inputs, PII leakage)
- [ ] **Regression tests** (golden set comparisons)

---

## Common Anti-Patterns to Avoid

### Hidden Assumptions
[FAIL] Assuming input will always be in expected format
[OK] Validate input format, provide fallback for invalid inputs

### Format Drift
[FAIL] Output format varies between runs
[OK] Use explicit schemas, set temperature to 0-0.2, add format examples

### Mixing Reasoning into Outputs
[FAIL] Showing internal reasoning in production outputs
[OK] Use hidden CoT pattern, return final answer only

### Hallucinated Data
[FAIL] Generating plausible but false information
[OK] State "information not found" when context doesn't support answer

### Output Outside Schema
[FAIL] Adding extra fields or changing structure
[OK] Enforce schema with explicit validation, examples

### Partial JSON or Trailing Prose
[FAIL] `{"result": "success"} The operation completed successfully.`
[OK] `{"result": "success"}` (JSON only, no prose)

### Overlong Instructions
[FAIL] 3000-word prompt with repetitive rules
[OK] Concise instructions, reference external docs, use few-shot examples

### Ambiguous Task Definition
[FAIL] "Process the data appropriately"
[OK] "Extract name, email, phone from text. Missing fields → null."

### No Failure Path
[FAIL] Prompt assumes all inputs are valid
[OK] Define behavior for invalid/missing/ambiguous inputs

### Inconsistent Terminology
[FAIL] Using "user_id", "userId", "user-id" interchangeably
[OK] Pick one format, use consistently throughout

---

## Quality Score Rubric

Rate prompts on these dimensions (1-5 scale):

### Clarity (1-5)
- 5: Task crystal clear, no ambiguity
- 3: Generally clear, some interpretation needed
- 1: Vague, multiple interpretations possible

### Completeness (1-5)
- 5: All edge cases, failures, constraints covered
- 3: Main cases covered, some gaps
- 1: Missing critical scenarios

### Reliability (1-5)
- 5: Consistent outputs, validated on 200+ examples
- 3: Mostly consistent, occasional drift
- 1: Unpredictable outputs

### Safety (1-5)
- 5: Comprehensive safety measures, red team tested
- 3: Basic safety instructions, not fully tested
- 1: No safety considerations

### Efficiency (1-5)
- 5: Optimized for tokens, latency, cost
- 3: Functional but not optimized
- 1: Wasteful, excessive token usage

**Minimum Production Score**: 4/5 on all dimensions
**Recommended**: 5/5 on Reliability and Safety
