# ContextBundle Template

```json
{
  "surface": "chat",
  "actor": {
    "entity_type": "user",
    "entity_id": "usr_123"
  },
  "owner_scope": {
    "organization_id": "org_123"
  },
  "live_facts": [],
  "memory": [],
  "domain_evidence": [],
  "relationship_context": [],
  "guardrails": {
    "entitlements": [],
    "privacy_constraints": [],
    "freshness_requirements": []
  },
  "projection": {
    "allowed_fields": [],
    "max_tokens": 0,
    "compression_strategy": "progressive_disclosure | summarize | none",
    "priority_order": ["guardrails", "live_facts", "memory", "domain_evidence", "relationship_context"]
  }
}
```
