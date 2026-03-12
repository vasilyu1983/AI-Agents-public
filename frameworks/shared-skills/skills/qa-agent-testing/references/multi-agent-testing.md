# Multi-Agent Testing

Coordination testing patterns for systems with multiple collaborating agents.

## Contents

- [Why Multi-Agent Testing Differs](#why-multi-agent-testing-differs)
- [Error Amplification Patterns](#error-amplification-patterns)
- [Coordination Metrics](#coordination-metrics)
- [Testing Patterns](#testing-patterns)
- [MARBLE Benchmark Framework](#marble-benchmark-framework)
- [Governance Notes (2026)](#governance-notes-2026)
- [Test Suite Template](#test-suite-template)
- [Checklist](#checklist)
- [Related](#related)

## Why Multi-Agent Testing Differs

Single-agent testing validates one agent's behavior. Multi-agent testing must also validate:

- Agent-to-agent communication
- Coordination protocols
- Emergent behaviors
- Error propagation across agents
- Consensus mechanisms

## Error Amplification Patterns

Some reports suggest multi-agent systems can amplify errors based on topology:

| Topology       | Error Amplification | Characteristics                     |
|----------------|---------------------|-------------------------------------|
| Independent    | 17.2x baseline      | Agents work in parallel, no comms   |
| Centralized    | 4.4x baseline       | Single orchestrator controls agents |
| Hierarchical   | 6-8x baseline       | Tree structure with supervisors     |
| Mesh           | 10-12x baseline     | All agents communicate with all     |

Source (non-peer-reviewed): [VentureBeat](https://venturebeat.com/orchestration/research-shows-more-agents-isnt-a-reliable-path-to-better-enterprise-ai)

Key insight: "More agents" is not a reliable path to better outcomes. Centralized architectures contain errors better than distributed ones.

## Coordination Metrics

| Metric                  | What It Measures                              | Target   |
|-------------------------|-----------------------------------------------|----------|
| Cooperation rate        | % of successful handoffs between agents       | > 95%    |
| Consensus time          | Rounds needed to reach agreement              | < 3      |
| Communication efficiency| Messages per task completion                  | Minimize |
| Protocol compliance     | % of messages following defined format        | 100%     |
| Temporal synchronization| Agents operating on consistent state          | < 100ms  |
| Trust score             | Inter-agent reliability rating                | > 0.9    |

## Testing Patterns

### Pattern 1: Pairwise Handoff Testing

Test each agent pair in isolation before full system tests:

```text
Test Matrix (4 agents):
A -> B: handoff test
A -> C: handoff test
A -> D: handoff test
B -> C: handoff test
B -> D: handoff test
C -> D: handoff test

Total: n(n-1)/2 = 6 pairwise tests
```

### Pattern 2: Chaos Injection

Deliberately break coordination to test resilience:

| Injection Type    | Purpose                                  |
|-------------------|------------------------------------------|
| Message delay     | Test timeout handling                    |
| Message drop      | Test retry and recovery                  |
| Agent crash       | Test failover and continuation           |
| State corruption  | Test state reconciliation                |
| Conflicting goals | Test conflict resolution                 |

### Pattern 3: Semantic-Preserving Mutation

Fuzzing approach from multi-agent robustness research:

```python
# Mutation operators that preserve meaning but change form
MUTATION_OPERATORS = [
    "synonym_substitution",    # Replace words with synonyms
    "sentence_reordering",     # Change sentence order
    "detail_expansion",        # Add clarifying details
    "formatting_change"        # Change list to prose, etc.
]

def mutate_input(original: str, operator: str) -> str:
    """Generate semantically equivalent variant."""
    ...

# Test: if agent solved original, should solve mutated
for operator in MUTATION_OPERATORS:
    mutated = mutate_input(original_task, operator)
    result = multi_agent_system.solve(mutated)
    assert result.correct, f"Failed on {operator} mutation"
```

Research finding: Multi-agent systems fail 7.9%-83.3% of questions they initially solved correctly when given semantically equivalent mutations.

Source: [arXiv](https://arxiv.org/html/2510.10460)

## MARBLE Benchmark Framework

MARBLE formalizes multi-agent LLM coordination evaluation:

```text
MARBLE Evaluation Dimensions:
1) Task Completion
   - Milestone achievement rate
   - Final goal success

2) Coordination Quality
   - Message efficiency
   - Role adherence

3) Planning Effectiveness
   - Explicit planning improves outcomes by ~3%
   - Track plan-action alignment

4) Robustness
   - Performance under agent failures
   - Recovery from communication errors
```

Source: [MARBLE Paper](https://arxiv.org/abs/2410.01078)

## Governance Notes (2026)

### Documentation and Auditability

If you operate under formal risk/compliance regimes (for example, NIST AI RMF or EU AI Act obligations), plan to:

- Log inter-agent messages (inputs, outputs, timestamps, and routing)
- Attribute decisions to agent(s) and tool calls where feasible
- Test human intervention/override mechanisms
- Retain reproducible test artifacts (fixtures, configs, and scores)

## Test Suite Template

```markdown
## Multi-Agent Test Suite

### System Under Test
- Agent count: [N]
- Topology: [centralized/hierarchical/mesh]
- Communication protocol: [sync/async]

### Pairwise Handoff Tests
| From | To | Scenario | Expected | Actual | Pass |
|------|-----|----------|----------|--------|------|
| A    | B   | ...      | ...      | ...    | PASS/FAIL  |

### Coordination Tests
| Test | Agents Involved | Scenario | Metrics | Pass |
|------|-----------------|----------|---------|------|
| 1    | A, B, C         | ...      | ...     | PASS/FAIL  |

### Chaos Tests
| Injection | Recovery Expected | Recovery Actual | Pass |
|-----------|-------------------|-----------------|------|
| Agent B crash | Failover to C | ... | PASS/FAIL  |

### Mutation Robustness
| Original Score | Mutated Score | Degradation | Acceptable |
|----------------|---------------|-------------|------------|
| 95%            | 87%           | 8%          | PASS/FAIL  |

### Coordination Metrics Summary
| Metric | Target | Actual | Pass |
|--------|--------|--------|------|
| Cooperation rate | > 95% | ... | PASS/FAIL |
| Consensus time | < 3 rounds | ... | PASS/FAIL |
```

## Checklist

Before deploying multi-agent systems:

- [ ] Pairwise handoff tests pass for all agent pairs
- [ ] Topology-specific error amplification is acceptable
- [ ] Chaos injection tests demonstrate graceful degradation
- [ ] Semantic mutation robustness is > 90%
- [ ] Coordination metrics meet targets
- [ ] Audit logging captures all inter-agent communications
- [ ] Human intervention mechanisms work correctly
- [ ] Regulatory compliance requirements documented

## Related

- [SKILL.md](../SKILL.md) - Main skill overview
- [test-case-design.md](test-case-design.md) - Single-agent test patterns
- [tool-sandboxing.md](tool-sandboxing.md) - Isolation strategies
