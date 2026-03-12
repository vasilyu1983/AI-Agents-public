# Structured Output Patterns

> Operational reference for extracting reliable structured data from LLMs — JSON mode, function calling, constrained decoding, schema validation, provider-specific features, and error recovery patterns.

**Freshness anchor:** January 2026 — covers OpenAI Structured Outputs (GA), Anthropic tool use with JSON, Gemini 2.0 function declarations, Outlines 0.1.x, Instructor 1.x.

---

## Provider Feature Comparison

| Feature | OpenAI | Anthropic | Google Gemini | Local (vLLM/Outlines) |
|---|---|---|---|---|
| Native JSON mode | Yes (`response_format`) | No (use tool_use) | Yes (`response_mime_type`) | Yes (constrained) |
| Structured Outputs (schema) | Yes (strict mode) | No | Yes (schema param) | Yes (grammar/regex) |
| Function/tool calling | Yes | Yes (tool_use) | Yes | Depends on model |
| Guaranteed schema compliance | Yes (strict mode) | No (best effort) | Yes (with schema) | Yes (constrained) |
| Partial output streaming | Yes | Yes | Yes | Yes |
| Nested objects | Yes | Yes | Yes | Yes |
| Array outputs | Yes | Yes | Yes | Yes |
| Enum constraints | Yes | Yes | Yes | Yes |
| Regex patterns | No | No | No | Yes (Outlines) |

---

## Method Selection Decision Tree

```
Need structured output from LLM
│
├── Do you need GUARANTEED schema compliance?
│   ├── YES
│   │   ├── Using OpenAI? → Structured Outputs (strict: true)
│   │   ├── Using Gemini? → response_schema parameter
│   │   ├── Using local model? → Outlines / constrained decoding
│   │   └── Using Anthropic? → tool_use + post-validation
│   │
│   └── NO (best-effort is acceptable)
│       ├── Simple JSON → JSON mode + validation
│       ├── Function call → Tool/function calling
│       └── Free text → Regex extraction (last resort)
│
├── Is the output a single function call?
│   ├── YES → Use function/tool calling (all providers)
│   └── NO → Multiple outputs or complex structure
│       ├── Parallel tool calls (OpenAI, Anthropic)
│       └── JSON mode with array schema
│
└── Do you need streaming partial results?
    ├── YES → Stream + incremental JSON parsing
    └── NO → Wait for complete response + validate
```

---

## OpenAI Structured Outputs

### Use When
- Need guaranteed schema compliance with no post-processing
- Complex nested schemas with optional fields
- Production systems where malformed output causes failures

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class ExtractedEntity(BaseModel):
    name: str
    entity_type: str  # "person", "org", "location"
    confidence: float
    context: str

class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity]
    summary: str
    language: str

response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract entities from text."},
        {"role": "user", "content": document_text}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "extraction_result",
            "strict": True,
            "schema": ExtractionResult.model_json_schema()
        }
    }
)

result = ExtractionResult.model_validate_json(response.choices[0].message.content)
```

### OpenAI Strict Mode Limitations

| Limitation | Workaround |
|---|---|
| All fields must have `default` or be required | Design schemas with all required fields |
| No `additionalProperties` allowed | Explicitly define all properties |
| Limited recursion depth (5 levels) | Flatten deeply nested structures |
| Schema must be deterministic | No `oneOf`, `anyOf` with overlapping types |
| First request with new schema is slower | Pre-warm with dummy request |

---

## Anthropic Tool Use for Structured Output

### Use When
- Using Claude models and need structured extraction
- Need to combine structured output with other tool calls
- Schema compliance is important but not 100% guaranteed

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[{
        "name": "extract_data",
        "description": "Extract structured data from the provided text",
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["person", "org", "location"]},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        },
                        "required": ["name", "type", "confidence"]
                    }
                },
                "summary": {"type": "string"}
            },
            "required": ["entities", "summary"]
        }
    }],
    tool_choice={"type": "tool", "name": "extract_data"},
    messages=[
        {"role": "user", "content": f"Extract entities from: {document_text}"}
    ]
)

# Extract tool use result
tool_result = next(
    block.input for block in response.content
    if block.type == "tool_use"
)
```

---

## Gemini Function Declarations

### Use When
- Using Gemini models
- Need schema-enforced output
- Working with Google Cloud infrastructure

```python
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.0-flash")

# Define schema
extraction_schema = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "entities": genai.protos.Schema(
            type=genai.protos.Type.ARRAY,
            items=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "name": genai.protos.Schema(type=genai.protos.Type.STRING),
                    "type": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        enum=["person", "org", "location"]
                    ),
                }
            )
        ),
        "summary": genai.protos.Schema(type=genai.protos.Type.STRING),
    }
)

response = model.generate_content(
    f"Extract entities from: {document_text}",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=extraction_schema
    )
)
```

---

## Constrained Decoding (Local Models)

### Use When
- Running local models (vLLM, llama.cpp, TGI)
- Need absolute schema compliance
- Working with smaller models that struggle with JSON formatting

```python
# Using Outlines with vLLM
from outlines import models, generate
from pydantic import BaseModel

class TaskOutput(BaseModel):
    action: str
    parameters: dict[str, str]
    confidence: float

model = models.vllm("mistral-7b-instruct", gpu_memory_utilization=0.9)
generator = generate.json(model, TaskOutput)

result = generator("Extract the action from: Book a flight to NYC tomorrow")
# result is guaranteed to be a valid TaskOutput instance
```

### Constrained Decoding Comparison

| Library | Backend | Method | Speed Overhead |
|---|---|---|---|
| Outlines | vLLM, transformers | FSM-based masking | 5-10% slower |
| Guidance | transformers | Token healing + masking | 10-15% slower |
| LMQL | OpenAI, local | Query language constraints | Variable |
| llama.cpp | Local GGUF | Grammar (BNF) | <5% slower |
| SGLang | Local | RadixAttention + constrained | <5% slower |

---

## Schema Design for Reliability

### Schema Design Rules

| Rule | Why | Example |
|---|---|---|
| Use enums for categorical fields | Prevents free-text drift | `"type": {"enum": ["a", "b", "c"]}` |
| Set min/max for numbers | Prevents extreme values | `"confidence": {"minimum": 0, "maximum": 1}` |
| Use `required` for all critical fields | Prevents missing data | `"required": ["name", "type"]` |
| Keep nesting < 4 levels | Reduces generation errors | Flatten where possible |
| Use descriptive field names | Model uses names as hints | `"customer_email"` not `"field_3"` |
| Add `description` to fields | Guides model behavior | `"description": "ISO 8601 date"` |
| Prefer arrays of objects | More reliable than nested maps | `[{"key": "a", "value": 1}]` not `{"a": 1}` |

### Schema Complexity vs. Reliability

| Schema Complexity | Reliability (GPT-4o) | Reliability (Claude) | Reliability (7B local) |
|---|---|---|---|
| Flat object, <5 fields | 99.9% | 99.5% | 95% |
| Nested, <10 fields | 99.5% | 98% | 85% |
| Nested, 10-20 fields | 98% | 95% | 70% |
| Deeply nested, >20 fields | 95% | 90% | 50% |
| Array of complex objects | 97% | 93% | 60% |

---

## Validation Pipeline Architecture

```
LLM Response
│
├── Step 1: Parse JSON
│   ├── Success → Continue
│   └── Failure → Attempt repair (see below)
│
├── Step 2: Schema validation (Pydantic / Zod / JSON Schema)
│   ├── Valid → Continue
│   └── Invalid → Attempt coercion or retry
│
├── Step 3: Business rule validation
│   ├── Valid → Continue
│   └── Invalid → Log + retry with corrective prompt
│
├── Step 4: Semantic validation
│   ├── Values make sense → Accept
│   └── Anomalous values → Flag for review
│
└── Final: Return validated object
```

### Partial Output Recovery

- Strip markdown code fences (```` ```json ... ``` ````)
- Fix trailing commas (`},` before `}` or `]`)
- Extract JSON substring from surrounding text (regex `\{[\s\S]*\}`)
- If all repair fails: return `None` to trigger retry with corrective prompt

### Retry Strategy

| Attempt | Strategy | Prompt Modification |
|---|---|---|
| 1 | Direct request | Original prompt |
| 2 | JSON repair | Attempt programmatic fix |
| 3 | Corrective retry | Include validation error in prompt |
| 4 | Simplified schema | Reduce fields, flatten structure |
| 5 | Fail | Return error, escalate |

```python
async def structured_output_with_retry(prompt, schema, max_retries=3):
    for attempt in range(max_retries):
        response = await llm.generate(prompt)
        parsed = repair_json(response)

        if parsed is None:
            prompt = f"{prompt}\n\nYour previous response was not valid JSON. Return ONLY valid JSON."
            continue

        try:
            validated = schema.model_validate(parsed)
            return validated
        except ValidationError as e:
            error_msg = str(e)
            prompt = f"{prompt}\n\nYour previous response had validation errors: {error_msg}\nFix these issues."

    raise StructuredOutputError(f"Failed after {max_retries} attempts")
```

---

## Using Instructor Library

### Use When
- Want a unified API across providers
- Need automatic retry with validation feedback
- Building production extraction pipelines

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

client = instructor.from_openai(OpenAI())

class UserInfo(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: str = Field(pattern=r'^[\w.+-]+@[\w-]+\.[\w.]+$')

# Automatic retry on validation failure
user = client.chat.completions.create(
    model="gpt-4o",
    response_model=UserInfo,
    max_retries=3,
    messages=[
        {"role": "user", "content": "John is 28, email john@example.com"}
    ]
)
# user is a validated UserInfo instance
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Parsing JSON with regex | Fragile, breaks on nesting | Use proper JSON parser + repair pipeline |
| No schema validation | Silent data corruption | Always validate with Pydantic/Zod |
| Overly complex schemas in one call | High failure rate | Split into multiple focused extractions |
| Ignoring partial outputs on stream cancel | Data loss | Implement incremental JSON parsing |
| Using `json.loads()` without try/except | Crashes on malformed output | Always wrap in error handling |
| Same schema for all model sizes | Small models fail on complex schemas | Simplify schemas for smaller models |
| Not including examples in prompt | Model guesses format | Include 1-2 examples of expected output |
| Retrying without error context | Same failure repeated | Include validation error in retry prompt |

---

## Cross-References

- `../ai-agents/references/agent-debugging-patterns.md` — debugging output parsing failures
- `../ai-agents/references/guardrails-implementation.md` — output validation guardrails
- `multimodal-patterns.md` — structured output from vision/audio
- `model-migration-guide.md` — structured output differences across providers
- `../ai-prompt-engineering/references/prompt-testing-ci-cd.md` — testing structured output quality
