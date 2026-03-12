# Agent Maturity & Governance — Fleet Management Framework

**Purpose**: Capability maturity levels, identity management, policy enforcement, and fleet-wide governance for production agent systems.

---

## Capability Maturity Levels

**Five-Level Progression**:

| Level | Name | Capabilities | Governance Requirements |
|-------|------|--------------|------------------------|
| **L0** | Static Reasoning | Fixed responses, no tools | Basic content filtering |
| **L1** | Tool-Using | API/function calls | Tool allowlist, parameter validation |
| **L2** | Strategic Planner | Multi-step planning, ReAct loop | Approval gates, trajectory logging |
| **L3** | Collaborative Multi-Agent | Task delegation, handoffs | Contract validation, trace propagation |
| **L4** | Self-Evolving | Policy learning, self-improvement | Sandbox testing, promotion gates |

**Governance Scaling**:

- **L0**: Content filters only
- **L1**: Add tool permissions, input validation
- **L2**: Add approval workflows, observability
- **L3**: Add handoff validation, multi-agent tracing
- **L4**: Add sandbox isolation, promotion reviews

**Pattern**:
```yaml
agent:
  id: "agent-research-001"
  maturity_level: "L2"
  capabilities:
    - "web_search"
    - "document_retrieval"
    - "multi_step_planning"
  governance:
    approvals_required: ["irreversible_actions"]
    observability_depth: "full_trajectory"
    tool_allowlist: ["search_api", "retrieval_api"]
```

---

## Persona + Domain Knowledge

**What**: Encode persona and domain expertise as versioned, testable assets

**Best Practices**:

1. **Versioned assets**: Treat persona/domain as code (version control, changelogs, reviews)
2. **Ahead of tools**: Load persona/domain before tool initialization
3. **Testable**: Create test suites for persona behavior
4. **Documented**: Maintain clear documentation of persona characteristics
5. **Evolvable**: Plan for persona updates and migrations

**Persona Definition**:
```yaml
persona:
  version: "v2.1.0"
  name: "Research Assistant"
  domain: "Academic Research"
  expertise:
    - "Literature review"
    - "Citation management"
    - "Data synthesis"
  tone: "Professional, precise, academic"
  constraints:
    - "Never speculate beyond evidence"
    - "Always cite sources"
    - "Flag uncertainty clearly"
  updated_at: "2024-01-15"
  changelog_url: "docs/personas/research-assistant-changelog.md"
```

**Domain Knowledge**:
```yaml
domain:
  name: "Academic Research"
  version: "v1.3.0"
  knowledge_sources:
    - name: "PubMed API"
      type: "tool"
      priority: "high"
    - name: "ArXiv"
      type: "retrieval"
      priority: "medium"
  validation_rules:
    - "Verify publication dates"
    - "Check citation formats"
    - "Validate DOIs"
```

---

## Identity & Policy

**What**: Each agent is a principal with scopes, roles, permissions, and audit trail

**Agent Identity**:
```yaml
agent_identity:
  agent_id: "agent-financial-001"
  agent_type: "financial_advisor"
  version: "v1.2.0"
  principal_id: "svc-account-agents-prod"
  scopes:
    - "read:market_data"
    - "read:user_portfolio"
  roles:
    - "advisor"
  created_at: "2024-01-01T00:00:00Z"
  updated_at: "2024-01-15T12:00:00Z"
```

**Policy Enforcement**:

1. **Tool allowlist**: Explicitly enumerate permitted tools
2. **Data access policy**: Define what data agent can access
3. **Approval matrix**: Map actions to approval requirements
4. **trace_id propagation**: Mandatory for all agent interactions

**Policy Schema**:
```yaml
policy:
  agent_id: "agent-financial-001"
  tool_allowlist:
    - "market_data_api"
    - "portfolio_api"
  data_access:
    allowed_scopes: ["user_portfolio", "market_data"]
    denied_scopes: ["admin", "pii"]
  approval_matrix:
    trades: "human_approval_required"
    read_only: "auto_approved"
  trace_propagation: "mandatory"
```

**Audit Trail**:
```json
{
  "trace_id": "req-abc-123",
  "agent_id": "agent-financial-001",
  "action": "execute_trade",
  "timestamp": "2024-01-15T12:00:00Z",
  "inputs": {"symbol": "AAPL", "shares": 10},
  "approval": {"approved_by": "user-001", "approved_at": "2024-01-15T11:59:00Z"},
  "result": "success"
}
```

---

## Fleet Control

**What**: Centralized registry and lifecycle management for agent fleet

**Agent Registry**:
```yaml
registry:
  agents:
    - agent_id: "agent-001"
      name: "Customer Support Agent"
      version: "v1.2.0"
      status: "active"
      contract_url: "contracts/customer-support-v1.2.json"
      deprecated: false
      kill_switch: "enabled"

    - agent_id: "agent-002"
      name: "Legacy Support Agent"
      version: "v1.0.0"
      status: "deprecated"
      deprecation_date: "2024-06-01"
      replacement: "agent-001"
      kill_switch: "enabled"
```

**Contract Management** (JSON Schemas):
```json
{
  "agent_id": "agent-001",
  "contract_version": "v1.2.0",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "user_id": {"type": "string"}
    },
    "required": ["query", "user_id"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "response": {"type": "string"},
      "confidence": {"type": "number"}
    }
  }
}
```

**Deprecation Rules**:

1. **Sunset timeline**: 90-day deprecation notice
2. **Migration path**: Provide clear upgrade instructions
3. **Backward compatibility**: Support old contracts during transition
4. **Communication**: Notify all consumers before deprecation
5. **Forced migration**: Hard cutoff after grace period

**Kill Switches**:

```yaml
kill_switch:
  agent_id: "agent-001"
  enabled: true
  triggers:
    - "error_rate > 10%"
    - "safety_violation_detected"
    - "manual_override"
  action: "halt_all_requests"
  fallback: "return_error_503"
  notification: ["oncall", "sre_team"]
```

**Override Paths**:

```yaml
override:
  agent_id: "agent-001"
  conditions:
    - condition: "high_confidence_required"
      override: "escalate_to_human"

    - condition: "safety_critical"
      override: "require_approval"

    - condition: "production_incident"
      override: "use_fallback_agent"
```

---

## Version Management

**Semantic Versioning**:

- **Major**: Breaking contract changes (v1 → v2)
- **Minor**: New capabilities, backward compatible (v1.1 → v1.2)
- **Patch**: Bug fixes, no behavior change (v1.2.0 → v1.2.1)

**Deployment Strategy**:

1. **Canary**: Route 5-10% traffic to new version
2. **Monitor**: Track metrics (error rate, latency, quality)
3. **Rollback**: Instant rollback if metrics degrade
4. **Gradual rollout**: Increase traffic gradually (10% → 25% → 50% → 100%)
5. **Deprecate old**: Sunset old version after validation

**Pattern**:
```yaml
deployment:
  agent_id: "agent-001"
  versions:
    - version: "v1.2.0"
      traffic: 10  # percent
      status: "canary"
      metrics:
        error_rate: 0.02
        p95_latency: 150ms

    - version: "v1.1.0"
      traffic: 90  # percent
      status: "stable"
      metrics:
        error_rate: 0.01
        p95_latency: 120ms
```

---

## Fleet Metrics

**Track Fleet-Wide**:

- **Active agents**: Count by type, version, status
- **Total requests**: Volume per agent
- **Error rates**: By agent, tool, handoff
- **Cost**: Token usage, tool calls, infrastructure
- **Quality**: Evaluation scores, user satisfaction
- **Safety**: Policy violations, escalations

**Dashboard Schema**:
```yaml
fleet_metrics:
  timestamp: "2024-01-15T12:00:00Z"
  active_agents: 42
  total_requests_24h: 15000
  avg_error_rate: 0.015
  total_cost_24h: "$125.00"
  safety_violations_24h: 2
  agents_by_maturity:
    L0: 5
    L1: 20
    L2: 15
    L3: 2
    L4: 0
```

---

## Compliance & Auditing

**Audit Requirements**:

1. **Request logs**: All agent requests with trace_id
2. **Tool usage**: Every tool call with parameters and results
3. **Approvals**: Human-in-the-loop decisions
4. **Policy checks**: All guardrail evaluations
5. **Handoffs**: Agent-to-agent transfers with schemas

**Retention Policy**:
```yaml
retention:
  request_logs: 90_days
  tool_usage: 365_days
  approvals: 7_years  # regulatory requirement
  policy_violations: 7_years
  handoff_traces: 90_days
```

**Compliance Frameworks**:

- **NIST AI RMF**: Risk management framework
- **OWASP GenAI Top 10**: Security vulnerabilities
- **SOC 2**: Security and availability controls
- **GDPR**: Privacy and data protection
- **HIPAA**: Healthcare data (if applicable)

---

## Related Resources

**Deployment**: [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md)
**Observability**: [`evaluation-and-observability.md`](evaluation-and-observability.md)
**Multi-Agent**: [`multi-agent-patterns.md`](multi-agent-patterns.md)
**API Design**: [`api-contracts-for-agents.md`](api-contracts-for-agents.md)

---

## Usage Notes

- **Start at L0/L1**: Begin with simple agents, graduate to higher levels
- **Governance scales with capability**: More powerful = more controls
- **Registry is source of truth**: All agents must be registered
- **Kill switches are mandatory**: Every production agent needs a kill switch
- **Audit everything**: Compliance requires comprehensive logging
