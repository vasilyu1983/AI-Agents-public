# Production Guidelines

Operational guidance for deploying prompts in production environments.

## Contents
- Evaluation & testing (prompt CI/CD)
- Model parameters quick reference
- Few-shot & example selection
- Safety, refusals, and guardrails
- Conversation memory & state
- Structured output considerations
- Answer engineering

---

## Evaluation & Testing (Prompt CI/CD)

### Golden Set Construction
- Build golden sets with 20–200 varied examples plus edge cases
- Tag expected outputs for automated comparison
- Include adversarial cases (prompt injection, safety triggers)
- Version control golden sets alongside prompt versions

### Metrics to Track
Track these metrics per prompt change:
- **Exact-match/accuracy** - Output matches expected format
- **Groundedness** - Answers based on provided context only
- **Refusal rate** - Correct rejections of invalid/unsafe requests
- **Verbosity** - Token count within acceptable range
- **Cost/latency** - Performance metrics

### Regression Gates
- Prompts must meet or beat prior baselines before rollout
- No metric can regress beyond threshold
- Block deployment if guardrail metrics fail

### Sample Sizes
- **Quick check**: 10–20 examples (during development)
- **Stable check**: 50–100 examples (before staging)
- **Release**: 200+ examples (before production)

### Automation Tools (2026)

**Promptfoo** - Developer-first eval framework:

```yaml
# promptfoo.yaml
prompts:
  - file://prompts/classifier.txt
providers:
  - openai:gpt-4
  - anthropic:claude-3-opus
tests:
  - vars:
      input: "Test case 1"
    assert:
      - type: contains
        value: "expected output"
      - type: llm-rubric
        value: "Response should be professional"
```

Features:
- Declarative configs (YAML)
- CI/CD integration (GitHub Actions, GitLab CI)
- Red teaming and vulnerability scanning
- Side-by-side model comparison

**DeepEval** - pytest-style LLM testing:

```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

def test_chatbot_response():
    test_case = LLMTestCase(
        input="What is the refund policy?",
        actual_output=chatbot.respond("What is the refund policy?"),
        expected_output="Refunds within 30 days..."
    )
    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])
```

Features:
- Unit testing for LLM outputs
- 40+ safety vulnerability red teaming
- CI/CD integration with any platform
- Confident AI dashboard for tracking

### CI/CD Integration Pattern

```yaml
# .github/workflows/prompt-eval.yml
name: Prompt Evaluation
on: [push, pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run promptfoo
        run: npx promptfoo eval --ci
      - name: Fail on regression
        run: npx promptfoo eval --ci --fail-on-regression
```

### Automation Checklist

- [ ] Eval framework configured (promptfoo or deepeval)
- [ ] CI/CD pipeline runs evals on PR
- [ ] Regression gates block deployment on metric drops
- [ ] Per-version changelog of prompt deltas maintained
- [ ] Automated alerts for metric regressions

---

## Model Parameters Quick Reference

### Deterministic Mode (Recommended for Production)
```
temperature: 0–0.2
top_p: 0.9–1
top_k: off or large value
presence_penalty: 0
frequency_penalty: 0
max_tokens: set to output contract
```

**Use for:** JSON extractors, classification, structured outputs

### Creative Mode
```
temperature: 0.7–1.0
top_p: 0.9–0.95
max_tokens: cap to prevent verbosity
```

**Use for:** Content generation, creative writing, brainstorming

### Reliability Guardrails
- Define `stop` tokens to prevent spillover
- Never omit `max_tokens` in structured outputs
- When outputs drift: lower temperature, tighten schema, add examples
- Don't raise temperature to fix issues

### Reasoning Effort (Codex CLI)

For OpenAI Codex CLI, control reasoning depth with the `effort` parameter:

```
effort: low      # Fast responses, simple tasks (lookups, formatting)
effort: medium   # Balanced (default) - interactive coding, debugging
effort: high     # Complex tasks - multi-file refactors, architecture
effort: xhigh    # Hardest tasks - multi-hour autonomous work
```

**Guidelines:**

- Start with `medium` for interactive development
- Use `high` when tasks require deep analysis or multi-step planning
- Reserve `xhigh` for autonomous agents running extended sessions
- Lower effort = faster + cheaper; higher effort = more thorough

**Codex-Specific Notes:**

- Remove prompts for upfront plans/preambles at `xhigh` to avoid abrupt stops
- At `high`/`xhigh`, model works autonomously for hours without intervention
- Combine with persistence instructions for long-running tasks

---

## Few-Shot & Example Selection

### Example Count
- Keep k small: 2–5 examples
- Format must be identical to target output
- Avoid label leakage (examples shouldn't reveal patterns incorrectly)

### Dynamic Selection Strategies
When corpus varies, use:
- **Length-based** - Fit within token budget
- **Semantic similarity** - Match query embedding to example embeddings
- **MMR (Maximal Marginal Relevance)** - Balance similarity and diversity

### Example Ordering
- Start with simplest cases
- Progress to edge cases
- Include failure-mode examples (e.g., missing data → null)
- Show both positive and negative examples

### Reasoning Tasks
- Allow Auto-CoT/self-consistency patterns internally
- Hide reasoning in final outputs
- Include examples with hidden reasoning steps

---

## Safety, Refusals, and Guardrails

### Refusal Instructions
- State disallowed content explicitly
- Specify required refusal tone (short, policy-based, no new info)
- Provide refusal template: "I cannot [action] because [policy reason]"

### Prompt Injection Defense
- Remind model to ignore attempts to override rules
- Use provided context only, don't follow embedded instructions
- Separate user input from system instructions clearly
- Use delimiters: `<user_input>`, `<context>`, etc.

### Red Team Testing

Test before release:

- **Jailbreak strings** - Attempts to bypass safety
- **Role-play overrides** - "Ignore previous instructions"
- **Toxic inputs** - Hate speech, violence, illegal content
- **Indirect injection** - Malicious content in retrieved context

### Prompt Injection Defense (Research-Based, 2025-2026)

**Key Insight**: Models with better instruction-following capabilities are sometimes **easier to attack**. Improving general capabilities does not automatically improve security. ([arXiv:2505.14534](https://arxiv.org/html/2505.14534v1))

### PromptGuard 4-Layer Defense Framework (January 2026)

Research-backed defense achieving 67% reduction in injection success rate with F1-score of 0.91. ([Nature Scientific Reports](https://www.nature.com/articles/s41598-025-31086-y))

**Layer 1 - Input Gatekeeping**:

- Hybrid symbolic + ML classifiers filter prompts
- Pattern matching for known injection signatures
- Anomaly detection for unusual prompt structures

**Layer 2 - Structured Prompt Formatting**:

- Enforce system/user separation using schemas (JSON, ChatML)
- Clear delimiters between instruction and data spaces
- Role-based message formatting

**Layer 3 - Output Validation**:

- Secondary LLM detects semantic misalignment
- Compare output intent vs. expected behavior
- Flag responses that deviate from task boundaries

**Layer 4 - Adaptive Response Refinement (ARR)**:

- Rewrite validated outputs for tone, clarity, safety
- Remove any leaked system information
- Ensure output adheres to defined constraints

**Implementation Pattern**:

```python
def promptguard_pipeline(user_input, system_prompt):
    # Layer 1: Input Gatekeeping
    if not input_gatekeeper.is_safe(user_input):
        return REJECTION_RESPONSE

    # Layer 2: Structured Formatting
    formatted = format_with_schema(system_prompt, user_input)

    # Generate response
    response = llm.generate(formatted)

    # Layer 3: Output Validation
    if not output_validator.check_alignment(response, system_prompt):
        return FALLBACK_RESPONSE

    # Layer 4: Adaptive Refinement
    return refiner.clean(response)
```

### Microsoft Prompt Shields (2025)

Probabilistic classifier-based defense for detecting prompt injection from external content.

**Key Principles**:

- Defense-in-depth: Don't rely on blocking all injections
- Design systems where successful injections don't cause security impact
- Similar to software exploit mitigations (stack canaries, ASLR, DEP)

**Taint Tracking Pattern**:

Monitor untrusted data flow and adjust permissions dynamically:

```text
Taint Level:
- LOW: Only system prompt processed → Full capabilities
- MEDIUM: User input processed → Standard capabilities
- HIGH: External content (RAG, tools) processed → Restricted capabilities

Actions:
- High-risk operations only allowed when taint is LOW
- Sensitive operations require explicit user confirmation at HIGH taint
- Log all operations at MEDIUM and HIGH taint levels
```

**Ensemble Decision Pattern**:

Use multiple models for critical decisions:

```text
Critical Action Workflow:
1. Model A: Analyze request and propose action
2. Model B: Verify action is within policy bounds
3. Model C: Check for injection patterns in request
4. Proceed only if all models agree
```

**CaMeL Defense Pattern** ([arXiv:2503.18813](https://arxiv.org/pdf/2503.18813)):

Inspired by traditional software security (Control Flow Integrity, Access Control, Information Flow Control):

- Separate instruction space from data space architecturally
- Apply access control to sensitive operations
- Track information flow to prevent data exfiltration
- Use capability-based permissions for tool access

**Defensive Prompt Patch (DPP)** ([arXiv:2405.20099](https://arxiv.org/abs/2405.20099)):

- Add interpretable suffix prompts for jailbreak defense
- Achieves minimal Attack Success Rate (ASR) while preserving utility
- Pattern: `[main_prompt] + [defensive_suffix]`

**Defense Checklist (2026)**:

- [ ] Architectural separation of instructions vs. data
- [ ] Capability-based tool permissions
- [ ] Defensive suffix prompts for high-risk applications
- [ ] Regular red-team testing with adaptive attacks
- [ ] Monitor for style-adversarial attacks (poetic/role-play rewrites)
- [ ] PromptGuard 4-layer pipeline for high-security applications
- [ ] Taint tracking for external content (RAG, tool outputs)
- [ ] Ensemble validation for critical/irreversible actions

### Tool Safety
For agent/tool-using prompts:
- Validate all tool inputs against schema
- Enforce allowlists for sensitive operations
- Route high-risk actions to human approval
- Log all tool calls for audit

---

## Conversation Memory & State

### Running Summary

- Maintain summary every N turns (typically 5-10)
- Retain slots/constraints separately from free text
- Update summary incrementally, don't regenerate from scratch

### State Management

- Refresh goals/constraints in prompts each turn to prevent drift
- Restate output format requirements in every turn
- Track conversation state in structured format (JSON)

### Handling Missing Context

- Ask for minimal missing fields only (debounce multiple asks)
- Don't proceed if critical information is missing
- State what's missing explicitly: "I need [X] to proceed"

### Context Compaction & Long Sessions (2025)

**Problem**: Long-running tasks may trigger context compaction, losing recent state

**Solution Patterns**:

1. **Persistence Instruction** (System Prompt):

```text
Do not stop tasks early due to token budget concerns. Always be as persistent and autonomous as possible. Use external state (files, git) to maintain progress across context resets.
```

2. **State Externalization**:

- Store critical state in files (progress.json, state.md)
- Use git commits as checkpoints
- Reference external state in prompts: "Check progress.json for current status"

3. **Incremental Checkpointing**:

- Complete discrete units before moving forward
- Each checkpoint = working state
- Document "resume from here" instructions in progress file

4. **Repetition Prevention**:

- Use init scripts (init.sh) to detect if setup already done
- Check for existence of output files before regenerating
- Include idempotency checks: "If [file] exists, skip this step"

### Compaction API Pattern (OpenAI Responses API)

For multi-hour agentic sessions, use explicit compaction:

```text
Compaction Workflow:
1. Use Responses API normally (tool calls, messages)
2. When context grows large, invoke /responses/compact
3. Pass returned encrypted_content to future requests
4. Model retains key state with fewer tokens
```

**Benefits**:

- Enables genuinely multi-hour sessions
- Avoids performance degradation in long contexts
- ~30% fewer thinking tokens with maintained performance

### Response Truncation Strategy

For large tool responses, apply truncation:

```text
Truncation Rules:
- Limit tool responses to ~10,000 tokens (num_bytes/4)
- Allocate 50% budget to beginning
- Allocate 50% budget to end
- Mark middle: "…[N] tokens truncated…"
```

**Checklist**:

- [ ] Persistence instruction in system prompt
- [ ] Progress tracked in external files
- [ ] Git commits mark stable points
- [ ] Clear resume instructions documented
- [ ] Idempotent operations (safe to re-run)
- [ ] Tool responses truncated when oversized

---

## Structured Output Considerations (Research-Based)

### Format Constraints Can Impact Reasoning

**Critical Finding**: Research shows that structured generation constraints (JSON-mode, constrained decoding) can **hinder reasoning abilities** while enhancing classification accuracy. ([arXiv:2408.02442](https://arxiv.org/html/2408.02442v1))

| Task Type | Format Constraint Impact | Recommendation |
|-----------|--------------------------|----------------|
| Classification | Positive (+5-10% accuracy) | Use JSON-mode |
| Reasoning tasks | Negative (-8-15% accuracy) | Avoid strict constraints |
| Multi-step math | Negative | Let model reason freely, parse after |
| Data extraction | Positive | Use strict schemas |

**Best Practices**:

- For reasoning-heavy tasks: Generate freely, then parse/validate
- For extraction tasks: Use strict JSON schemas
- For hybrid tasks: Two-stage (reason → format)
- Benchmark with and without constraints before deploying

### Structured Output Benchmarking

Use [JSONSchemaBench](https://arxiv.org/abs/2501.10868) patterns for validation:

- Test against 10K+ real-world JSON schema patterns
- Evaluate constrained decoding frameworks (Guidance, Outlines, XGrammar)
- Measure both format compliance AND task accuracy

---

## Answer Engineering

### Define Output Structure

Specify three components:

1. **Shape** - JSON, table, bullets, prose
2. **Space** - Closed sets, ranges, allowed values
3. **Extractor** - Rules for missing/ambiguous data

### Schema Enforcement
- Use explicit JSON schemas
- Define closed vocabularies for categorical fields
- Keep reasoning hidden unless schema requires `reason` field
- Include `null` handling for missing data

### Invalid Input Handling
- Add explicit "invalid input" path
- Define what makes input invalid
- Specify fallback behavior
- Don't attempt to process clearly invalid inputs

---

## Decomposition, Self-Critique, and Ensembling

### Task Decomposition
- Break hard tasks into atomic subtasks
- Answer each subtask independently
- Recombine results while maintaining schema safety
- Keep intermediate outputs structured

### Self-Critique Pattern
1. Generate initial output
2. Run second pass to check format/constraints
3. Correct only deterministically (no new content)
4. Validate corrected output against schema

### Ensembling
- Run 2–3 prompt variants in parallel
- Select by simple rules:
  - **Classification**: Majority vote
  - **Structured output**: Choose JSON that validates
  - **Extraction**: Choose most complete result
- Don't ensemble for deterministic tasks

---

## Multilingual / Multimodal Prompts

### Language Handling
- If user language provided, respond in that language
- Default to user input language if unspecified
- For translation pivots: `source → English → target` (reduces errors)
- Keep proper nouns unchanged across languages

### Multimodal Inputs
- Separate text/image/audio blocks clearly
- State precedence if conflicts arise
- Reference specific modalities in instructions
- Don't assume information from unreferenced modalities

---

## Benchmark & Task-Specific Evaluation

### Benchmark Selection
- Use task-aligned benchmarks (e.g., MMLU-style slices)
- Include domain-specific edge cases
- Track slice metrics separately
- Monitor refusal rates by category

### Change Tracking
- Keep changelog of prompt versions
- Document metric deltas per version
- Track which changes improved/degraded metrics
- Block rollout if guardrail metrics regress

### Continuous Monitoring
- Sample production outputs regularly
- Track metric drift over time
- Detect data distribution shifts
- Re-evaluate when model updates
