# Tool Design & Validation — Best Practices 

*Purpose: Provide operational patterns, schemas, validation rules, and checklists for defining, selecting, and safely executing tools with Model Context Protocol (MCP) integration.*

**Modern Update**: MCP is now the standard for tool integration (adopted by Anthropic, OpenAI, Google). Use MCP for all new tool implementations.

---
## Table of Contents

- [Model Context Protocol (MCP) Integration](#model-context-protocol-mcp-integration)
- [MCP Architecture](#mcp-architecture)
- [MCP Tool Definition Pattern](#mcp-tool-definition-pattern)
- [1. Tool Definition Pattern (Legacy & MCP)](#1-tool-definition-pattern-legacy--mcp)
- [Standard Tool Schema](#standard-tool-schema)
- [2. Tool Action Pattern](#2-tool-action-pattern)
- [3. Parameter Validation](#3-parameter-validation)
- [Pattern: Strict Validation Layer](#pattern-strict-validation-layer)
- [4. High-Risk Tool Handling](#4-high-risk-tool-handling)
- [High-Risk Examples](#high-risk-examples)
- [Pattern: Guarded Tool Call](#pattern-guarded-tool-call)
- [5. Tool Selection Rules](#5-tool-selection-rules)
- [Pattern: Intent → Tool Choice](#pattern-intent-→-tool-choice)
- [5A. Tool Selection At Scale](#5a-tool-selection-at-scale)
- [The Three Strategies](#the-three-strategies)
- [Escalation Gate: Do Not Decompose Into Agents Yet](#escalation-gate-do-not-decompose-into-agents-yet)
- [6. Tool Output Validation](#6-tool-output-validation)
- [Pattern: Structured Output Check](#pattern-structured-output-check)
- [7. Error Handling Patterns](#7-error-handling-patterns)
- [Pattern: Typed Error Handling](#pattern-typed-error-handling)
- [8. Tool Composition Pattern](#8-tool-composition-pattern)
- [When chaining tools](#when-chaining-tools)
- [Topology Ladder: Bound Every Rung](#topology-ladder-bound-every-rung)
- [9. MCP Tool Design](#9-mcp-tool-design)
- [MCP Tool Structure](#mcp-tool-structure)
- [MCP-Specific Rules](#mcp-specific-rules)
- [10. Tool Testing Pattern](#10-tool-testing-pattern)
- [Pattern: Test Inputs → Verify → Compare → Log](#pattern-test-inputs-→-verify-→-compare-→-log)
- [11. Tool Safety Anti-Patterns (Master List)](#11-tool-safety-anti-patterns-master-list)
- [12. Quick Reference Tables](#12-quick-reference-tables)
- [Tool Types Table](#tool-types-table)
- [Risk Table](#risk-table)
- [Validation Table](#validation-table)
- [End of File](#end-of-file)


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

# 5A. Tool Selection At Scale

Section 5 assumes every tool definition fits in the prompt. That assumption breaks
as the catalog grows: selection accuracy degrades as the number of candidate tools
increases, and semantically overlapping descriptions become the dominant source of
misselection. Pick a selection strategy by tool count and description overlap, not
by framework. (Albada, *Building Applications with AI Agents*, O'Reilly 2025, Ch. 5.)

### The Three Strategies

| Strategy | How it works | Choose it when | Cost of choosing it |
| -------- | ------------ | -------------- | ------------------- |
| **Standard** | All tool definitions go in the prompt; the model picks one | Small toolsets; you want zero extra infrastructure | Scales poorly as tool count rises; description overlap drives misselection |
| **Semantic** | Tool descriptions are embedded into a vector index ahead of time; at runtime the query is embedded and the top-k tools are retrieved and passed to the model | **Default at scale.** Most use cases; large toolsets where latency matters | Semantic collisions between similar descriptions can make accuracy *worse* than standard |
| **Hierarchical** | Two stages: select a tool *group* (each group carries its own description), then select a tool within that group | Large tool counts **and** many semantically similar tools, where accuracy outranks latency | Extra sequential model call per selection; groups must be authored and maintained by hand |

Decision rule:

```text
Do all tool definitions fit comfortably in the prompt?
→ Yes → standard selection; invest in description quality first
→ No  → semantic retrieval (default)
        → still misselecting because tools are semantically similar?
          → hierarchical grouping, accepting the added latency
```

Hierarchical selection is not recommended unless the tool count is genuinely large —
authoring and maintaining the groups is ongoing work, and the second stage costs a
sequential model call that is expensive to parallelize away.

**Description engineering comes first.** At any scale, the cheapest accuracy gain is
in the tool definitions themselves: a specific name over a generic one
(`calculate_sum`, not `process_numbers`), a one-sentence summary of the tool's
*unique* purpose, an example invocation, and explicit input types and ranges so the
model can rule tools out. Retrieval infrastructure does not rescue overlapping
descriptions — semantic collisions are exactly the failure mode it introduces.

### Escalation Gate: Do Not Decompose Into Agents Yet

Degrading tool selection is the most common trigger for splitting one agent into
many. It is usually the wrong first move. Before decomposing, exhaust the
single-agent options above — group tools hierarchically, or retrieve them
semantically from a vector index. Decompose into distinct agents only if those
still fall short, and price in the coordination overhead when you do.
(Albada, O'Reilly 2025, Ch. 8.)

This is the concrete, tool-count-driven form of the skill's general anti-multi-agent
posture. See `SKILL.md` → *Known Traps* (multi-agent topologies before single-agent
failure modes are understood) and [`multi-agent-patterns.md`](multi-agent-patterns.md)
for the handoff contracts required once decomposition is actually justified.

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

### Topology Ladder: Bound Every Rung

Climb from single tool → parallel → chain → graph only when the current rung
genuinely cannot express the task, and bound each rung explicitly:

- **Chains** must have a **maximum length**. Errors compound down the length of a
  chain, so an unbounded chain converts one bad step into a bad result.
- **Graphs** multiply foundation-model calls relative to chains — adding latency and
  cost — so **cap depth and branching factor**. Graphs also admit error classes
  chains do not: cycles, unreachable nodes, and conflicting state merges. Adopt a
  graph only when you must both branch *and* later consolidate; every added node or
  edge multiplies execution paths and error modes.

(Albada, O'Reilly 2025, Ch. 5.) For which *kind* of graph a problem calls for
before picking a runtime, see
[`graph-and-loop-engineering.md`](graph-and-loop-engineering.md).

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
