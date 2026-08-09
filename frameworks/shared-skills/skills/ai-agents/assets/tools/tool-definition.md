# Tool Definition Template

*Purpose: Define a production-ready tool with clear schema, safety rules, validation, and error-handling.*

---

## When to Use

Use this template when:

- Creating a new tool for an agent  
- Connecting MCP or API functions  
- Designing OS actions, retrieval tools, or system integrations  
- Adding high-risk or domain-specific tools  
- Upgrading tool schemas for production readiness  

---

# TEMPLATE STARTS HERE

## 1. Tool Overview

**Tool Name:**  
[tool_name]

**Purpose (1 sentence):**  
[What this tool does operationally]

**Tool Category:**  

- Retrieval  
- Action  
- OS Automation  
- API Integration  
- Computation  
- Transformation  
- Other

---

## 2. Tool Specification (Full YAML)

```yaml
tool_name:
  description: "[Clear operational purpose]"
  input_schema:
    field_1:
      type: string
      required: true
    field_2:
      type: integer
      required: false
    field_3:
      type: object
      required: false
  output_schema:
    result:
      type: object
  confirm: [yes|no]
  error_handling:
    retry: 1
    timeout: 30
    fatal_errors:
      - "auth_failure"
      - "invalid_parameters"
```

---

## 3. Input Parameter Rules

### 3.1 Validation Requirements

Each input must be validated for:

- Presence  
- Type  
- Format  
- Range (if numeric)  
- Allowed values (if enum)  
- Safety constraints  
- Domain constraints  

### 3.2 Validation Template

```yaml
validation:
  - field: field_1
    checks:
      - non_empty
      - type_string
  - field: field_2
    checks:
      - type_integer
      - range: [0, 100]
  - field: field_3
    checks:
      - type_object
      - required_fields: [subfield_a, subfield_b]
```

---

## 4. Tool Execution

### 4.1 Execution Pattern

```
validate_parameters()
apply_safety_checks()
call_tool_function()
verify_output()
```

### 4.2 Execution Rules

- Never guess parameters  
- Reject hallucinated IDs, paths, or coordinates  
- Require explicit values for high-risk fields  
- Use blocking confirmation if `confirm=yes`  
- Validate output strictly against schema  

---

## 5. Output Schema Rules

### Requirements

- Deterministic structure  
- All fields defined  
- No unexpected fields  
- No null/undefined unless allowed  

### Output Validation Template

```yaml
output_validation:
  required_fields:
    - result
  type_checks:
    result: object
```

---

## 6. Error Handling

### 6.1 Typed Error Policy

| Type | Handling |
|------|----------|
| Transient | retry once |
| Soft Failure | ask user for clarification |
| Fatal | halt + return structured error |

### 6.2 Error Response Template

```yaml
error:
  type: [transient|soft|fatal]
  message: "..."
  details: {...}
```

---

## 7. Safety Requirements

### High-Risk Tool Flags

- `confirm: yes`  
- User must approve parameters  
- Natural language safety summary required  
- Abort if confirmation unclear  

### Safety Summary Template

```
You are requesting a high-risk action:
- Action: [tool_name]
- Parameters: [...]
Please confirm "yes" to proceed.
```

---

## 8. Tool Metadata (Optional)

```yaml
metadata:
  owner: "team_name"
  version: "1.0.0"
  last_updated: "YYYY-MM-DD"
  changelog: "Initial release"
```

---

# COMPLETE EXAMPLE (Generic)

```yaml
set_user_permissions:
  description: "Update a user's permission level in the internal system."
  input_schema:
    user_id:
      type: string
      required: true
    new_role:
      type: string
      required: true
    reason:
      type: string
      required: false
  output_schema:
    result:
      type: object
  confirm: yes
  error_handling:
    retry: 0
    timeout: 15
    fatal_errors:
      - "auth_failure"
      - "role_not_allowed"
```

---

# End of Template
