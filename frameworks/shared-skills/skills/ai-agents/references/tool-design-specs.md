# Tool Design & Validation — Best Practices 

*Purpose: Provide operational patterns, schemas, validation rules, and checklists for defining, selecting, and safely executing tools with Model Context Protocol (MCP) integration.*

**Modern Update**: MCP is now the standard for tool integration (adopted by Anthropic, OpenAI, Google). Use MCP for all new tool implementations.

---

## Model Context Protocol (MCP) Integration

### MCP Architecture

**Three-layer pattern**:
```yaml
MCP Host (AI App) ← MCP Client ← MCP Server
```

**MCP Server provides**:
- Tools (function definitions)
- Resources (data access)
- Prompts (reusable templates)

**When to use MCP**:
- All new tool integrations (standardized over custom APIs)
- Multi-tool orchestration
- Cross-application tool sharing
- Standardized authentication and permissions

**Security requirements**:
- Tool signature verification (Sigstore/Cosign)
- Permission scoping per tool
- Prompt injection defenses
- Audit logging for all tool calls

### MCP Tool Definition Pattern

```yaml
mcp_tool:
  name: "tool_name"
  description: "Operational purpose (what it does)"
  inputSchema:
    type: "object"
    properties:
      param1:
        type: "string"
        description: "Clear parameter description"
      param2:
        type: "integer"
        minimum: 1
    required: ["param1"]
  security:
    require_confirmation: true  # For high-risk operations
    allowed_roles: ["admin", "operator"]
    signature_required: true
```

**MCP vs Custom API Decision Tree**:
```text
New tool integration needed?
→ Is this a standard operation (file access, web search, database)?
  → Yes: Use existing MCP server or create MCP tool
  → No: Is this tool shared across multiple agents/apps?
    → Yes: Implement as MCP server
    → No: Can still use MCP for consistency (recommended)
```

---

## 1. Tool Definition Pattern (Legacy & MCP)

### Standard Tool Schema

```
tool_name:
  description: [operational purpose]
  input_schema:
    field_1: type
    field_2: type
  output_schema:
    result: type
  confirm: yes/no
  error_handling:
    retry: 1
    timeout: 30
```

**Checklist**

- [ ] Description specifies *what the tool does*, not *how*.  
- [ ] Inputs are typed (string/int/boolean/object).  
- [ ] Output schema is deterministic.  
- [ ] Confirm = “yes” for destructive/irreversible actions.  
- [ ] Retry window defined for transient errors.  
- [ ] Timeout specified in seconds.  

**Anti-Patterns**

- AVOID: Leaving parameters untyped.  
- AVOID: Vague descriptions (“fetch stuff”).  
- AVOID: Missing error-handling section.  
- AVOID: Multiple unrelated actions in a single tool.  

---

# 2. Tool Action Pattern

**Use when:** executing any external function, API call, MCP tool, OS action, or integration.

```
prepare_parameters()
validate_parameters()
if high_risk: request_confirmation()
call_tool()
verify_output()
```

**Checklist**

- [ ] Validate type, range, format.  
- [ ] Reject incomplete parameters.  
- [ ] Map user intent → explicit parameters.  
- [ ] Convert natural language to structured fields.  
- [ ] Verify output fields before using downstream.  

---

# 3. Parameter Validation

### Pattern: Strict Validation Layer

```
for each field in input_schema:
    ensure field exists
    ensure type matches
    ensure format valid
```

**Validation Types**

- string (non-empty)  
- number (integer/float)  
- boolean  
- list of X  
- object with child fields  

**Decision Tree**

```
Is the parameter required?
→ Yes → Must appear → Must be valid
→ No → Provide default or null
```

**Examples**

- integer-only → reject floats or strings.  
- path fields → must not be hallucinated; confirm via retrieval.  
- enum fields → match allowed values only.  

---

# 4. High-Risk Tool Handling

### High-Risk Examples

- File deletion / modification  
- Database writes  
- Financial actions  
- OS-level execution  
- Remote system calls  
- External automation (clicking, typing, system control)

### Pattern: Guarded Tool Call

```
if high_risk:
  generate natural-language summary
  request user confirmation
  wait for explicit "yes"
  execute
```

**Checklist**

- [ ] Summaries must list exact parameters.  
- [ ] Confirmation required.  
- [ ] Abort when confirmation unclear.  

---

# 5. Tool Selection Rules

### Pattern: Intent → Tool Choice

```
extract_intent()
match_intent_to_tool()
choose_best_tool()
```

**Decision Tree**

```
Does the step require external data?
→ Yes → choose retriever or API tool
Does the step require external action?
→ Yes → choose action/OS tool
Does the step require computation?
→ Use internal reasoning unless precision tool exists
```

**Checklist**

- [ ] Never hallucinate undeclared tools.  
- [ ] Map intent → tool name exactly as defined.  
- [ ] One step = one tool call.  

---

# 6. Tool Output Validation

### Pattern: Structured Output Check

```
verify(required_fields)
validate_types()
validate_ranges()
assert no unexpected nulls
```

**Checklist**

- [ ] Output matches schema exactly.  
- [ ] Unexpected fields ignored or flagged.  
- [ ] Missing fields = tool failure.  
- [ ] Use output only after validation.  

**Anti-Patterns**

- AVOID: Reasoning from assumed output.  
- AVOID: Skipping verification for “simple” tools.  
- AVOID: Reusing stale tool results.  

---

# 7. Error Handling Patterns

### Pattern: Typed Error Handling

```
if transient:
    retry once
elif soft_failure:
    request clarification
else:
    halt and surface error
```

**Error Types**

- **Transient** (network timeout, rate limit) → retry  
- **Soft failure** (bad parameters, missing fields) → ask user  
- **Fatal** (auth failure, invalid tool name) → halt  

**Checklist**

- [ ] Use max 1–2 retries.  
- [ ] Do not mask errors.  
- [ ] Bubble up fatal issues with clean summary.  

---

# 8. Tool Composition Pattern

### When chaining tools

```
output_1 = tool_A()
validate(output_1)
params_2 = transform(output_1)
tool_B(params_2)
```

**Checklist**

- [ ] Validate output_1 before using it.  
- [ ] Transform intermediate data explicitly.  
- [ ] Abort chain on any invalid output.  

**Anti-Patterns**

- AVOID: Long unbroken tool chains (>3).  
- AVOID: Using tool output as-is without validation.  

---

# 9. MCP Tool Design

### MCP Tool Structure

```
{
  "name": "tool_name",
  "description": "purpose",
  "input_schema": {...},
  "output_schema": {...}
}
```

### MCP-Specific Rules

- Use JSON-RPC message types strictly.  
- Always include error objects when failing.  
- Keep tools granular (one purpose each).  
- Avoid side effects unless required by design.  

---

# 10. Tool Testing Pattern

### Pattern: Test Inputs → Verify → Compare → Log

```
for each test_case:
    run tool with known params
    assert output matches expected
    assert type validity
    assert error returns correctly
```

**Checklist**

- [ ] At least 3 positive test cases.  
- [ ] At least 2 negative test cases.  
- [ ] Logs captured for each call.  
- [ ] Versioned tool definitions.  

---

# 11. Tool Safety Anti-Patterns (Master List)

- AVOID: Using a tool without validating user intent.  
- AVOID: Guessing IDs, paths, or coordinates.  
- AVOID: Performing irreversible actions without confirmation.  
- AVOID: Triggering tools based on partial or ambiguous queries.  
- AVOID: Treating tool errors as “optional”.  
- AVOID: Overloading one tool with multi-purpose behavior.  
- AVOID: Generating synthetic parameters.  

---

# 12. Quick Reference Tables

### Tool Types Table

| Type | Purpose |
|------|---------|
| Retrieval | External data read |
| Action | External effect / OS control |
| Computation | Deterministic processing |
| Integration | API / remote system |
| Transformation | Data shaping |

### Risk Table

| Risk Level | Examples | Requirements |
|------------|----------|--------------|
| Low | read-only retrieval | no confirmation |
| Medium | modifying local data | validation + verification |
| High | destructive/system actions | explicit confirmation |

### Validation Table

| Field Type | Validation Rule |
|------------|------------------|
| string | not empty |
| int | numeric, range-bound |
| bool | true/false only |
| object | must match schema |
| enum | must be allowed value |

---

# End of File
