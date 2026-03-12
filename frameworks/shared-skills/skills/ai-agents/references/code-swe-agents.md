# Code Agents & Software Engineering Agents

Production patterns for autonomous coding agents that perform end-to-end software engineering tasks.

---

## Overview

Code/SWE agents represent a distinct category of AI agents that autonomously:
- Resolve GitHub issues and implement features
- Navigate codebases and understand context
- Edit files, run tests, and iterate on failures
- Create pull requests with proper documentation

**Key Distinction**: Unlike code completion tools (Copilot autocomplete), SWE agents operate autonomously across entire repositories with multi-step planning and execution.

---

## SE 3.0 Paradigm (Agentic Software Engineering)

Software engineering is evolving through three paradigms:

| Era | Paradigm | Developer Role | AI Role |
|-----|----------|----------------|---------|
| SE 1.0 | Manual | Write all code | None |
| SE 2.0 | Assisted | Write with suggestions | Autocomplete, snippets |
| **SE 3.0** | **Agentic** | **Review and guide** | **Autonomous implementation** |

**SE 3.0 Definition**: Intent-driven, conversational development where developers collaborate with autonomous AI teammates.

**Scale**: OpenAI Codex alone created 400,000+ PRs in open-source GitHub repositories within 2 months of release (May 2025).

---

## Architecture Patterns

### 1. Multi-Agent SWE Architecture (HyperAgent Pattern)

```
┌─────────────────────────────────────────────────────────────┐
│                      PLANNER AGENT                          │
│  - Decomposes issue into subtasks                          │
│  - Creates execution plan                                   │
│  - Coordinates other agents                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ NAVIGATOR AGENT │ │ CODE EDITOR     │ │ EXECUTOR AGENT  │
│ - Search code   │ │ AGENT           │ │ - Run tests     │
│ - Find files    │ │ - Write/edit    │ │ - Execute cmds  │
│ - Understand    │ │   code          │ │ - Verify fixes  │
│   structure     │ │ - Refactor      │ │ - Capture output│
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 2. Minimal Agent Pattern (Lita/Mini-SWE)

Research shows "light" agent philosophies can achieve 68% of full-agent performance with ~100 lines of code:

```python
class MinimalSWEAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {
            "read_file": read_file,
            "write_file": write_file,
            "run_command": run_command,
            "search_code": search_code
        }

    def solve(self, issue: str) -> str:
        """Single ReAct loop with file tools"""
        context = f"Issue: {issue}\n"

        for step in range(MAX_STEPS):
            action = self.llm.decide(context, self.tools)
            result = self.execute(action)
            context += f"\nAction: {action}\nResult: {result}"

            if action.type == "submit":
                return action.patch

        return None
```

**Key Insight**: Architectural complexity doesn't always correlate with performance. Start minimal, add complexity only when needed.

---

## Production Considerations

### 1. Beyond Test Passing

**Critical Finding**: 29.6% of "plausible" SWE-Bench fixes (those passing tests) introduce behavioral regressions.

**Implication**: Passing tests is necessary but insufficient. Production deployments require:

- Behavioral regression testing
- Code review by humans
- Integration testing beyond unit tests
- Semantic diff analysis

### 2. Guardrails for Code Agents

```yaml
code_agent_guardrails:
  execution_limits:
    max_steps: 50
    max_file_edits: 20
    timeout_minutes: 30

  allowed_operations:
    - read_file
    - write_file
    - search_code
    - run_tests
    - git_operations: [add, commit, diff, status]

  forbidden_operations:
    - delete_repository
    - force_push
    - modify_ci_config
    - access_secrets

  review_triggers:
    - changes_to_security_files
    - more_than_10_files_modified
    - changes_to_deployment_config
```

### 3. Human-in-the-Loop Checkpoints

```
Issue Assigned → Agent Plans → [HUMAN REVIEW] → Agent Implements
                                     ↓
                              Reject / Modify
                                     ↓
                              Agent Re-plans

Agent Implements → Agent Tests → [HUMAN REVIEW] → Merge/Deploy
                                      ↓
                               Request Changes
                                      ↓
                               Agent Iterates
```

---

## Tool Design for Code Agents

### File Operations

```json
{
  "name": "edit_file",
  "description": "Edit a file by replacing specific content",
  "parameters": {
    "file_path": {
      "type": "string",
      "description": "Path relative to repository root"
    },
    "old_content": {
      "type": "string",
      "description": "Exact content to replace (must be unique in file)"
    },
    "new_content": {
      "type": "string",
      "description": "Content to insert"
    }
  }
}
```

**Design Principle**: Use search-and-replace over line numbers. Line numbers shift; content patterns are stable.

### Code Search

```json
{
  "name": "search_codebase",
  "description": "Search for code patterns across repository",
  "parameters": {
    "query": {
      "type": "string",
      "description": "Search query (supports regex)"
    },
    "file_pattern": {
      "type": "string",
      "description": "Glob pattern for files to search"
    },
    "context_lines": {
      "type": "integer",
      "default": 3,
      "description": "Lines of context around matches"
    }
  }
}
```

### Test Execution

```json
{
  "name": "run_tests",
  "description": "Execute test suite and return results",
  "parameters": {
    "test_path": {
      "type": "string",
      "description": "Specific test file/directory or empty for full suite"
    },
    "timeout": {
      "type": "integer",
      "default": 300,
      "description": "Timeout in seconds"
    }
  },
  "returns": {
    "passed": "integer",
    "failed": "integer",
    "errors": "array of failure details"
  }
}
```

---

## Benchmarks & Evaluation

### SWE-Bench

The primary benchmark for code agents:

| Metric | Description |
|--------|-------------|
| **Resolved** | Issue fully fixed, all tests pass |
| **Plausible** | Tests pass but may have regressions |
| **Attempted** | Agent produced a patch |

**Current Leaders** (as of Nov 2025):
- HyperAgent, Devin, Claude Code variants leading
- GPT-4o, Claude 3.5 Sonnet as base models
- Multi-agent architectures outperforming single-agent

### Beyond SWE-Bench

Additional evaluation dimensions:

1. **Code Quality**: Does generated code follow project conventions?
2. **Explanation Quality**: Can the agent explain its changes?
3. **Iteration Efficiency**: How many attempts to reach solution?
4. **Scope Creep**: Does the agent make unnecessary changes?

### 2025 Agent Benchmarks to Watch

- **Tool Use**: BFCL (iterative, multi-turn function calling) raises bar beyond ToolBench/API-Bank.
- **Deep Research**: BrowseComp / BrowseComp-ZH / BrowseComp-Plus track evidence synthesis across web; top models still near-zero success.
- **GUI**: WebGen-Bench (full multi-file site generation) and Web-Bench (sequential UI coding tasks) stress multi-step reasoning.
- **OS/Terminal**: Terminal-Bench measures full-system CLI autonomy (build kernels, deploy servers) vs repo-bounded SWE-Bench.

---

## Configuration Patterns

Based on analysis of 328 Claude Code project configurations:

### Common CLAUDE.md Patterns

```markdown
## Code Style
- Follow existing patterns in the codebase
- Run linter before committing
- Add tests for new functionality

## Boundaries
- Do not modify CI/CD configuration
- Do not access external APIs without approval
- Keep changes focused on the specific issue

## Review Requirements
- All changes require human review
- Security-sensitive files need explicit approval
```

### Effective Configurations

1. **Explicit boundaries** outperform implicit ones
2. **Examples** improve adherence to style
3. **Tool allowlists** reduce unexpected behaviors
4. **Checkpoints** catch issues early

---

## Integration with MCP

Code agents benefit from MCP servers for:

```yaml
mcp_servers:
  filesystem:
    purpose: "Read/write project files"
    capabilities: [read, write, search]

  git:
    purpose: "Version control operations"
    capabilities: [status, diff, commit, branch]

  terminal:
    purpose: "Run commands (tests, linters, builds)"
    capabilities: [execute_command]

  github:
    purpose: "PR/issue management"
    capabilities: [create_pr, comment, request_review]
```

---

## Anti-Patterns

### 1. Unbounded Autonomy

**Problem**: Agent makes sweeping changes without checkpoints
**Solution**: Implement step limits, change size limits, and review gates

### 2. Test-Only Validation

**Problem**: Agent optimizes for passing tests, not correctness
**Solution**: Human review, behavioral regression tests, semantic analysis

### 3. Context Overload

**Problem**: Feeding entire codebase to agent
**Solution**: Progressive context loading, relevant file retrieval

### 4. Ignoring Agent Uncertainty

**Problem**: Treating all agent outputs as equally confident
**Solution**: Confidence scoring, escalation for low-confidence actions

---

## References

- [The Rise of AI Teammates in SE 3.0](https://arxiv.org/abs/2507.15003) - 456K PR analysis
- [HyperAgent: Generalist SWE Agents](https://arxiv.org/abs/2409.16299) - Multi-agent architecture
- [Agentic Software Engineering: Research Roadmap](https://arxiv.org/abs/2509.06216) - Foundational pillars
- [AI Agentic Programming Survey](https://arxiv.org/abs/2508.11126) - Taxonomy and patterns
- [Claude Code Configuration Study](https://arxiv.org/abs/2511.09268) - Real-world configurations
