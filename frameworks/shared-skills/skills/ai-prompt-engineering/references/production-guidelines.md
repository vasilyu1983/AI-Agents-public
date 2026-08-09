# Production Guidelines

## Table of Contents

- [Contents](#contents)
- [Evaluation & Testing (Prompt CI/CD)](#evaluation--testing-prompt-cicd)
- [Prompt Lifecycle Controls](#prompt-lifecycle-controls)
- [Model Parameters Quick Reference](#model-parameters-quick-reference)
- [Few-Shot & Example Selection](#few-shot--example-selection)
- [Safety, Refusals, and Guardrails](#safety-refusals-and-guardrails)
- [Conversation Memory & State](#conversation-memory--state)
- [Structured Output Considerations (Research-Based)](#structured-output-considerations-research-based)
- [Answer Engineering](#answer-engineering)
- [Decomposition, Self-Critique, and Ensembling](#decomposition-self-critique-and-ensembling)
- [Multilingual / Multimodal Prompts](#multilingual--multimodal-prompts)
- [Benchmark & Task-Specific Evaluation](#benchmark--task-specific-evaluation)

Operational guidance for deploying prompts in production environments.

**Freshness anchor:** July 2026. Treat provider product names, exact parameter defaults, and feature availability as volatile. Verify before rollout.

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

### Evaluation Tooling (March 2026)

**Provider-native tooling**:

- **OpenAI**: Evals, graders, prompt optimizer, prompt caching, and structured outputs for schema-first contracts
- **Anthropic**: Eval tool, prompt generator, prompt improver, and templates/variables for reusable prompt families
- **Google**: Prompting and structured-output guides; keep a local eval harness even when provider features are sufficient

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
- Safety vulnerability red teaming
- CI/CD integration with any platform
- Dashboard support for tracking and triage

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

- [ ] Provider-native eval features reviewed for the chosen stack
- [ ] Eval framework configured (provider-native, promptfoo, deepeval, or combination)
- [ ] CI/CD pipeline runs evals on PR
- [ ] Regression gates block deployment on metric drops
- [ ] Per-version changelog of prompt deltas maintained
- [ ] Automated alerts for metric regressions

---

## Prompt Lifecycle Controls

Use prompt lifecycle controls the same way you would use source control for code.

- Keep prompts versioned and named by use case, not by ad hoc model nickname.
- Reuse variables/templates for prompt families instead of duplicating near-identical prompts.
- Tie each shipped prompt version to an eval set, rollback path, and owner.
- Prefer provider-native prompt registries or prompt management surfaces when available.
- Keep a local export or source-of-truth file even if the provider stores prompts remotely.

---

## Model Parameters Quick Reference

### Provider-Aware Defaults

Do not assume one provider's defaults transfer cleanly to another.

| Surface | Starting Point | Use For | Notes |
|---|---|---|---|
| OpenAI structured tasks | Low temperature plus Structured Outputs | JSON extractors, classification, tool I/O | Let schema enforcement carry most of the determinism |
| OpenAI reasoning/coding tasks | Default temperature plus reasoning/effort controls when needed | Coding, planning, multi-step analysis | Prefer effort/reasoning controls over visible chain-of-thought prompts |
| Anthropic Claude (Opus 4.7/4.8, Fable 5) | Omit `temperature`/`top_p`/`top_k` entirely; use `output_config.effort` | Coding, tools, analysis, long-context tasks | Setting sampling params returns 400. Opus 4.8 defaults `effort` to `"high"` on all surfaces — set explicitly only to override. Fable 5 keeps adaptive thinking always on (cannot disable). Avoid redundant "think step-by-step" with adaptive thinking. |
| Anthropic Claude (pre-4.7) | Start from current provider defaults | General tasks | Check docs — behavior differs from Opus 4.7 |
| Gemini 3 | Start from Google's current default temperature (`1.0`) and tune only after evals | General prompting, multimodal, creative or mixed tasks | Do not import low-temperature defaults from other providers without testing |

**Determinism on Claude Opus 4.7:** `temperature=0` cannot be set (400 error). Determinism must be achieved through prompt design: explicit schemas, closed-set output vocabularies, null-fallback rules, and post-generation validation. The old `temperature=0` shortcut is gone; it never guaranteed identical outputs anyway.

### Self-hosted Structured Output Engines (2026-05)

For self-hosted inference (vLLM, SGLang, TensorRT-LLM), **XGrammar** (https://xgrammar.mlc.ai) is widely used for constrained structured output generation. It provides efficient grammar-constrained decoding as an alternative to earlier engines like Outlines (which had reported timeout issues on complex grammars). vLLM's structured output backend defaults to `auto`, which selects an appropriate engine per request — verify the actual default for your version in vLLM's current release notes. Verify against each framework's current documentation before relying on engine-specific behavior; defaults and support status change across minor versions. Freshness: 2026-05.

### Reliability Guardrails
- Set output limits to match the output contract
- Use provider-native structured outputs where available, plus local schema validation
- When outputs drift: tighten task framing, schema, examples, or retrieval context before tuning randomness
- Prefer prompt/version changes gated by evals over ad hoc parameter tweaking
- Treat prompt caching, prompt variables, and versioned prompts as reliability features, not just convenience features

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
- Include examples with private reasoning expectations when the workflow benefits from them

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

**Key insight**: Improving general capabilities does not automatically improve security — a more capable, more instruction-compliant model can follow an injected instruction just as faithfully as a legitimate one. Google DeepMind's applied red-teaming work on Gemini ([arXiv:2505.14534](https://arxiv.org/abs/2505.14534), "Lessons from Defending Gemini Against Indirect Prompt Injections") documents this as a practical finding from adversarial evaluation, not a formal theorem — treat it as directional evidence for defense-in-depth, not a citation for a specific effect size. Verify the current paper text before quoting a numeric claim from it.

### Example Multi-Layer Defense Framework

Use layered defenses and validate them with your own eval corpus. External benchmark numbers are directional, not a production acceptance criterion.

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

### Microsoft Prompt Shields (Example Managed Detector)

Managed classifier-based defense for detecting prompt injection from external content.

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
- [ ] Optional detector layer evaluated for high-security applications
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

**Finding**: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models" ([arXiv:2408.02442](https://arxiv.org/abs/2408.02442)) reports that structured generation constraints (JSON-mode, constrained decoding) cause a measurable decline in reasoning-task performance, with the degradation growing as format constraints get stricter, while classification-style tasks are comparatively unaffected or improved. The paper's own reported numbers vary by model and benchmark — do not carry over a fixed percentage figure without checking the current paper for the specific model/task pair you care about; benchmark your own stack with and without constraints instead of trusting a single quoted delta.

| Task Type | Format Constraint Impact | Recommendation |
|-----------|--------------------------|----------------|
| Classification | Neutral to positive | Use JSON-mode |
| Reasoning tasks | Negative, worsens with stricter constraints | Avoid strict constraints |
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
