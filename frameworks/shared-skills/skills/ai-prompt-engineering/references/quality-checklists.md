# Quality Checklists

## Table of Contents

- [Contents](#contents)
- [Prompt QA Checklist](#prompt-qa-checklist)
- [JSON Validation Checklist](#json-validation-checklist)
- [Agent Workflow Checks](#agent-workflow-checks)
- [RAG Workflow Checks](#rag-workflow-checks)
- [Safety & Security Checks](#safety--security-checks)
- [Performance Optimization Checks](#performance-optimization-checks)
- [Testing Coverage Checklist](#testing-coverage-checklist)
- [Common Anti-Patterns to Avoid](#common-anti-patterns-to-avoid)
- [Quality Score Rubric](#quality-score-rubric)

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
- [ ] **Tool call discipline** (parallel calls for independent reads only; writes and validation remain serialized)
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
- [ ] **Temperature appropriate** (low for deterministic on providers that support it; omit entirely for Claude Opus 4.7 — sampling params return 400)
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
[OK] Use explicit schemas, add format examples, use post-generation validation (low temperature helps on providers that support it; Claude Opus 4.7 requires schema enforcement instead)

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

## LLM-as-Judge Calibration

Use LLM judges only after error analysis on failure cases — diagnosing what is actually going wrong before writing judge prompts prevents judges that test the wrong thing.

**Scoring format:**

- Use **binary scoring** (pass/fail) rather than Likert scales (1–5). Binary scores are more consistent across judge instances and easier to aggregate into a pass rate.
- For tasks with both positive and negative examples, run **separate judges** for positive alignment (does the output do what it should?) and negative alignment (does the output avoid what it shouldn't?). A combined rubric conflates the two and hides which dimension failed.

**Calibration signals:**

- **100% pass rate is a warning, not a success.** A judge that never fails is under-challenging — either the eval set lacks hard cases or the rubric is too permissive. Add adversarial examples or tighten the rubric until you see a realistic failure rate.
- **Error-analysis-before-judges sequencing:** Before writing or running a judge, manually inspect a sample of outputs. Identify the actual failure modes. Write the judge rubric to detect those specific modes. Do not write a general-purpose judge and expect it to surface your specific problem.

**Checklist:**

- [ ] Ran error analysis on at least a sample of outputs before writing judge criteria
- [ ] Binary (pass/fail) scoring — not Likert
- [ ] Separate positive-alignment and negative-alignment judges where both matter
- [ ] Eval set includes adversarial and edge cases (not only easy examples)
- [ ] 100% pass rate triggers review of rubric and eval set difficulty
- [ ] Judge prompts versioned alongside the prompt under test

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
