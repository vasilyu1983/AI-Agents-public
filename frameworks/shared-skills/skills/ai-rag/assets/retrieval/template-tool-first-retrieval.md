# Tool-First Retrieval Template

Use when the source of truth is not a document corpus but live tools, APIs, SQL, or MCP resources.

```yaml
retrieval_mode: tool_first
authority_source:
  type: api|sql|mcp|saas
  system: ""
  freshness_requirement: ""

query_router:
  classify_intent: true
  routes:
    - name: exact_lookup
      use_when: "IDs, counts, status, or record lookup"
      path: "sql_or_api"
    - name: document_search
      use_when: "free-text policy or prose search"
      path: "hybrid_search"
    - name: hybrid_answer
      use_when: "needs both record data and explanatory documents"
      path: "tool_plus_search"

tool_contract:
  request_fields: [query, filters, trace_id, tenant_id]
  response_fields: [record_id, title, snippet, source, updated_at, acl]
  treat_output_as_untrusted: true

fallbacks:
  - if: "tool unavailable"
    then: "degrade gracefully or refuse"
  - if: "tool output conflicts with indexed docs"
    then: "prefer authority source and flag inconsistency"
```

Checklist:

- [ ] Authority source defined
- [ ] Tool outputs normalized into evidence objects
- [ ] ACLs enforced before results are returned
- [ ] Conflicting tool/doc answers handled explicitly
- [ ] Observability includes tool latency and failure rate
