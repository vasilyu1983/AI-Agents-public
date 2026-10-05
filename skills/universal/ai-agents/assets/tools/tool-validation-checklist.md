# Tool Validation Checklist

*Purpose: Provide a complete, production-grade validation checklist for safe, correct, and deterministic tool use. Apply before and after any tool call.*

---

## When to Use

Use this checklist when:

- Creating a new tool  
- Calling an existing tool  
- Reviewing agent/tool behavior  
- Hardening tool safety  
- Debugging tool failures  
- Enforcing MCP or API tool correctness  

---

# TEMPLATE STARTS HERE

# PRE-FLIGHT VALIDATION (Before Tool Call)

## 1. Tool Name Validation

- [ ] Tool name matches exactly as defined  
- [ ] Tool exists in available tool registry  
- [ ] No hallucinated or inferred tool names  

---

## 2. Intent → Tool Mapping

- [ ] Step requires external data OR external action  
- [ ] Tool selected intentionally for the step  
- [ ] Not using tool when internal reasoning suffices  
- [ ] Tool chosen is the least-privileged valid option  

---

## 3. Input Schema Validation

For each field:

- [ ] Field present if required  
- [ ] Field not present if disallowed  
- [ ] Type matches schema (string/int/bool/object/list)  
- [ ] Format valid (e.g., email/URL/path/date)  
- [ ] Numeric values within allowed range  
- [ ] Enum fields match allowed values  
- [ ] No guessed IDs, paths, or coordinates  
- [ ] No unvalidated user free text flowing into critical fields  

---

## 4. High-Risk Action Check

If tool is high-risk:

- [ ] Confirmation required  
- [ ] Natural-language safety summary generated  
- [ ] User responded with explicit “yes”  
- [ ] Abort if confirmation unclear  

High-Risk Categories:

- OS-level actions  
- File modifications  
- External system writes  
- Financial/legal actions  
- Irreversible operations  

---

## 5. Safety Scan (Pre-Call)

- [ ] Input sanitized  
- [ ] No prompt injection attempts  
- [ ] No disallowed domain requests  
- [ ] No personal or sensitive data  
- [ ] No unsafe parameter combinations  

---

## 6. Context & Dependency Validation

- [ ] Step logically follows previous steps  
- [ ] Required context retrieved or prepared  
- [ ] No stale values reused  
- [ ] No unresolved conflicts in previous steps  

---

# RUNTIME VALIDATION (During Tool Call)

## 7. Call Execution Rules

- [ ] Tool called with validated parameters  
- [ ] Retry only transient errors  
- [ ] Timeout respected  
- [ ] Fatal errors surfaced immediately  
- [ ] All actions logged  

---

# POST-FLIGHT VALIDATION (After Tool Call)

## 8. Output Schema Validation

- [ ] Output present  
- [ ] All required fields present  
- [ ] Types match schema  
- [ ] No unexpected fields  
- [ ] No null or undefined values (unless allowed)  

---

## 9. Output Integrity Checks

- [ ] Output grounded (not hallucinated)  
- [ ] Results plausible for the domain  
- [ ] No missing data that the tool guarantees  
- [ ] No security violations in output  
- [ ] No leaking sensitive data  

---

## 10. Error Handling Review

If error occurred:

- [ ] Classify as transient / soft / fatal  
- [ ] Retry only transient  
- [ ] Request clarification only for soft  
- [ ] Halt for fatal  
- [ ] Produce human-readable error summary  

---

## 11. Plan Continuation Check

- [ ] Step achieved intended effect  
- [ ] Observation updated after tool call  
- [ ] Next plan step depends on validated outputs  
- [ ] If tool output contradicts expectations → replan  

---

# COMPLETE EXAMPLE (Optional)

### Tool Call

```
tool_name: "lookup_customer"
params:
  id: "C842"
```

### Validation Result

- Tool exists: yes  
- Input valid: yes  
- High-risk: no  
- Safety scan: clean  
- Output fields: valid  
- Continue to next step: allowed  

---

# End of Checklist
