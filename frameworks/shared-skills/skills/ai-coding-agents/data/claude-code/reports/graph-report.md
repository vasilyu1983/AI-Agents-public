# Claude Code Graph Report

## Build Metadata

| Field | Value |
| --- | --- |
| Title | Claude Code Graph Report |
| Graph File | ../graphs/knowledge-graph.json |
| Generated At | 2026-04-03T12:00:00+00:00 |
| Graph Contract | 1.1 |
| Build Source | profiles |
| Node Count | 23 |
| Edge Count | 40 |
| Base Commit SHAs | 0 |
| Portfolio Metrics | {"process_count": 7, "provider_count": 6, "repo_count": 1} |

## Validation And Freshness

| Artifact | Status | Details |
| --- | --- | --- |
| Graph Validation | 8/8 checks passed | schema_compliance, dangling_refs, orphans, confidence_floor, duplicates, containment_consistency, staleness, circular_deps |
| Consistency | missing | consistency-report.json not found |
| Incremental Update | missing | incremental-update.json not found |

## Graph Inventory

### Nodes By Type

| Type | Count |
| --- | --- |
| artifact | 8 |
| process | 7 |
| provider | 6 |
| domain | 1 |
| repo | 1 |

### Edges By Relation

| Relation | Count |
| --- | --- |
| documents | 18 |
| contains | 9 |
| implements_process | 7 |
| uses_provider | 6 |

## Top Connected Nodes

| Label | Type | Domain | Fan-In | Weighted | ID |
| --- | --- | --- | --- | --- | --- |
| Transport Recovery | process | Documents | 4 | 3.1 | process-transport-recovery |
| Permission Mediation | process | Documents | 3 | 2.4 | process-permission-mediation |
| Terminal Agent Runtime | process | Documents | 3 | 2.3 | process-terminal-agent-runtime |
| Plugin And Skill Loading | process | Documents | 3 | 2.2 | process-plugin-and-skill-loading |
| Background Agent Execution | process | Documents | 3 | 2.1 | process-background-agent-execution |
| Remote Session Management | process | Documents | 2 | 1.7 | process-remote-session-management |
| Worktree Orchestration | process | Documents | 2 | 1.7 | process-worktree-orchestration |
| Anthropic SDK | provider | Documents | 2 | 1.4 | provider-anthropic-sdk |
| Axios | provider | Documents | 2 | 1.3 | provider-axios |
| Bun | provider | Documents | 2 | 1.3 | provider-bun |
| Git | provider | Documents | 2 | 1.3 | provider-git |
| tmux | provider | Documents | 2 | 1.2 | provider-tmux |
| claude_code | repo | Documents | 1 | 1.0 | claude_code |
| HybridTransport.ts | artifact | Documents | 1 | 0.95 | artifact-hybrid-transport-ts |
| QueryEngine.ts | artifact | Documents | 1 | 0.95 | artifact-query-engine-ts |

## Domains To Repositories

| Source | Relation | Target | Target Type |
| --- | --- | --- | --- |
| Documents | contains | claude_code | repo |

## Repositories To Providers

| Source | Relation | Target | Target Type |
| --- | --- | --- | --- |
| claude_code | uses_provider | Anthropic SDK | provider |
| claude_code | uses_provider | Axios | provider |
| claude_code | uses_provider | Bun | provider |
| claude_code | uses_provider | Git | provider |
| claude_code | uses_provider | Model Context Protocol SDK | provider |
| claude_code | uses_provider | tmux | provider |

## Repositories To Processes

| Source | Relation | Target | Target Type |
| --- | --- | --- | --- |
| claude_code | implements_process | Background Agent Execution | process |
| claude_code | implements_process | Permission Mediation | process |
| claude_code | implements_process | Plugin And Skill Loading | process |
| claude_code | implements_process | Remote Session Management | process |
| claude_code | implements_process | Terminal Agent Runtime | process |
| claude_code | implements_process | Transport Recovery | process |
| claude_code | implements_process | Worktree Orchestration | process |

## Repositories To Storage

_No matching relationships found._

## Diagram Exports

### Platform Overview

Domains, repositories, providers, and processes.

```mermaid
flowchart LR
  %% Platform Overview
  subgraph group_Documents["Domain: Documents"]
    process_background_agent_execution["Background Agent Execution"]
    process_permission_mediation["Permission Mediation"]
    process_plugin_and_skill_loading["Plugin And Skill Loading"]
    process_remote_session_management["Remote Session Management"]
    process_terminal_agent_runtime["Terminal Agent Runtime"]
    process_transport_recovery["Transport Recovery"]
    process_worktree_orchestration["Worktree Orchestration"]
    provider_anthropic_sdk["Anthropic SDK"]
    provider_axios["Axios"]
    provider_bun["Bun"]
    provider_git["Git"]
    provider_mcp_sdk["Model Context Protocol SDK"]
    provider_tmux["tmux"]
    claude_code["claude_code"]
  end
  subgraph group_domain["Domain: domain"]
    documents["Documents"]
  end
  claude_code -->|implements_process| process_background_agent_execution
  claude_code -->|implements_process| process_permission_mediation
  claude_code -->|implements_process| process_plugin_and_skill_loading
  claude_code -->|implements_process| process_remote_session_management
  claude_code -->|implements_process| process_terminal_agent_runtime
  claude_code -->|implements_process| process_transport_recovery
  claude_code -->|implements_process| process_worktree_orchestration
  claude_code -->|uses_provider| provider_anthropic_sdk
  claude_code -->|uses_provider| provider_axios
  claude_code -->|uses_provider| provider_bun
  claude_code -->|uses_provider| provider_git
  claude_code -->|uses_provider| provider_mcp_sdk
  claude_code -->|uses_provider| provider_tmux
  documents -->|contains| claude_code
  classDef type_domain fill:#ede9fe,stroke:#7c3aed,color:#1f2937;
  classDef type_process fill:#dcfce7,stroke:#15803d,color:#14532d;
  classDef type_provider fill:#fef3c7,stroke:#d97706,color:#1f2937;
  classDef type_repo fill:#dbeafe,stroke:#1d4ed8,color:#0f172a;
  classDef type_unknown fill:#ffffff,stroke:#64748b,color:#0f172a;
  class documents type_domain;
  class process_background_agent_execution type_process;
  class process_permission_mediation type_process;
  class process_plugin_and_skill_loading type_process;
  class process_remote_session_management type_process;
  class process_terminal_agent_runtime type_process;
  class process_transport_recovery type_process;
  class process_worktree_orchestration type_process;
  class provider_anthropic_sdk type_provider;
  class provider_axios type_provider;
  class provider_bun type_provider;
  class provider_git type_provider;
  class provider_mcp_sdk type_provider;
  class provider_tmux type_provider;
  class claude_code type_repo;
```

### Data Topology

Repositories and storage relationships.

```mermaid
flowchart LR
  %% Data Topology
  subgraph group_Documents["Domain: Documents"]
    claude_code["claude_code"]
  end
  subgraph group_domain["Domain: domain"]
    documents["Documents"]
  end
  documents -->|contains| claude_code
  classDef type_domain fill:#ede9fe,stroke:#7c3aed,color:#1f2937;
  classDef type_repo fill:#dbeafe,stroke:#1d4ed8,color:#0f172a;
  classDef type_unknown fill:#ffffff,stroke:#64748b,color:#0f172a;
  class documents type_domain;
  class claude_code type_repo;
```

### Documentation Coverage

Artifacts and the nodes they document.

```mermaid
flowchart LR
  %% Documentation Coverage
  subgraph group_artifact["Type: artifact"]
    artifact_hybrid_transport_ts["HybridTransport.ts"]
    artifact_query_engine_ts["QueryEngine.ts"]
    artifact_remote_session_manager_ts["RemoteSessionManager.ts"]
    artifact_sse_transport_ts["SSETransport.ts"]
    artifact_task_ts["Task.ts"]
    artifact_query_ts["query.ts"]
    artifact_remote_permission_bridge_ts["remotePermissionBridge.ts"]
    artifact_setup_ts["setup.ts"]
  end
  subgraph group_domain["Type: domain"]
    documents["Documents"]
  end
  subgraph group_process["Type: process"]
    process_background_agent_execution["Background Agent Execution"]
    process_permission_mediation["Permission Mediation"]
    process_plugin_and_skill_loading["Plugin And Skill Loading"]
    process_remote_session_management["Remote Session Management"]
    process_terminal_agent_runtime["Terminal Agent Runtime"]
    process_transport_recovery["Transport Recovery"]
    process_worktree_orchestration["Worktree Orchestration"]
  end
  subgraph group_provider["Type: provider"]
    provider_anthropic_sdk["Anthropic SDK"]
    provider_axios["Axios"]
    provider_bun["Bun"]
    provider_git["Git"]
    provider_mcp_sdk["Model Context Protocol SDK"]
    provider_tmux["tmux"]
  end
  subgraph group_repo["Type: repo"]
    claude_code["claude_code"]
  end
  artifact_hybrid_transport_ts -->|documents| process_transport_recovery
  artifact_hybrid_transport_ts -->|documents| provider_axios
  artifact_query_engine_ts -->|documents| process_plugin_and_skill_loading
  artifact_query_engine_ts -->|documents| process_terminal_agent_runtime
  artifact_query_ts -->|documents| process_background_agent_execution
  artifact_query_ts -->|documents| process_terminal_agent_runtime
  artifact_query_ts -->|documents| process_transport_recovery
  artifact_query_ts -->|documents| provider_anthropic_sdk
  artifact_remote_permission_bridge_ts -->|documents| process_permission_mediation
  artifact_remote_session_manager_ts -->|documents| process_permission_mediation
  artifact_remote_session_manager_ts -->|documents| process_remote_session_management
  artifact_setup_ts -->|documents| process_plugin_and_skill_loading
  artifact_setup_ts -->|documents| process_worktree_orchestration
  artifact_setup_ts -->|documents| provider_bun
  artifact_setup_ts -->|documents| provider_git
  artifact_setup_ts -->|documents| provider_tmux
  artifact_sse_transport_ts -->|documents| process_transport_recovery
  artifact_task_ts -->|documents| process_background_agent_execution
  claude_code -->|contains| artifact_hybrid_transport_ts
  claude_code -->|contains| artifact_query_engine_ts
  claude_code -->|contains| artifact_query_ts
  claude_code -->|contains| artifact_remote_permission_bridge_ts
  claude_code -->|contains| artifact_remote_session_manager_ts
  claude_code -->|contains| artifact_setup_ts
  claude_code -->|contains| artifact_sse_transport_ts
  claude_code -->|contains| artifact_task_ts
  claude_code -->|implements_process| process_background_agent_execution
  claude_code -->|implements_process| process_permission_mediation
  claude_code -->|implements_process| process_plugin_and_skill_loading
  claude_code -->|implements_process| process_remote_session_management
  claude_code -->|implements_process| process_terminal_agent_runtime
  claude_code -->|implements_process| process_transport_recovery
  claude_code -->|implements_process| process_worktree_orchestration
  claude_code -->|uses_provider| provider_anthropic_sdk
  claude_code -->|uses_provider| provider_axios
  claude_code -->|uses_provider| provider_bun
  claude_code -->|uses_provider| provider_git
  claude_code -->|uses_provider| provider_mcp_sdk
  claude_code -->|uses_provider| provider_tmux
  documents -->|contains| claude_code
  classDef type_artifact fill:#f3f4f6,stroke:#6b7280,color:#111827;
  classDef type_domain fill:#ede9fe,stroke:#7c3aed,color:#1f2937;
  classDef type_process fill:#dcfce7,stroke:#15803d,color:#14532d;
  classDef type_provider fill:#fef3c7,stroke:#d97706,color:#1f2937;
  classDef type_repo fill:#dbeafe,stroke:#1d4ed8,color:#0f172a;
  classDef type_unknown fill:#ffffff,stroke:#64748b,color:#0f172a;
  class documents type_domain;
  class artifact_hybrid_transport_ts type_artifact;
  class artifact_query_engine_ts type_artifact;
  class artifact_remote_session_manager_ts type_artifact;
  class artifact_sse_transport_ts type_artifact;
  class artifact_task_ts type_artifact;
  class artifact_query_ts type_artifact;
  class artifact_remote_permission_bridge_ts type_artifact;
  class artifact_setup_ts type_artifact;
  class process_background_agent_execution type_process;
  class process_permission_mediation type_process;
  class process_plugin_and_skill_loading type_process;
  class process_remote_session_management type_process;
  class process_terminal_agent_runtime type_process;
  class process_transport_recovery type_process;
  class process_worktree_orchestration type_process;
  class provider_anthropic_sdk type_provider;
  class provider_axios type_provider;
  class provider_bun type_provider;
  class provider_git type_provider;
  class provider_mcp_sdk type_provider;
  class provider_tmux type_provider;
  class claude_code type_repo;
```

## Node Index

<details>
<summary>artifact (8)</summary>

| Label | ID | Domain | Summary | Tags |
| --- | --- | --- | --- | --- |
| HybridTransport.ts | artifact-hybrid-transport-ts | Documents | Hybrid transport with WebSocket reads, serialized POST writes, batching, and backpressure. | transport |
| QueryEngine.ts | artifact-query-engine-ts | Documents | Persistent execution coordinator for prompt assembly, query execution, and plugin-aware system prompt composition. | runtime-spine |
| RemoteSessionManager.ts | artifact-remote-session-manager-ts | Documents | Remote session manager with message callbacks and permission request handling. | remote-runtime |
| SSETransport.ts | artifact-sse-transport-ts | Documents | SSE transport with resumable sequence tracking and reconnect behavior. | transport |
| Task.ts | artifact-task-ts | Documents | Task model defining background execution types and lifecycle states. | tasks |
| query.ts | artifact-query-ts | Documents | Main query loop with task-budget accounting and max_output_tokens recovery logic. | runtime-spine |
| remotePermissionBridge.ts | artifact-remote-permission-bridge-ts | Documents | Permission bridge that synthesizes assistant messages and fallback tool stubs for remote tools. | permissions |
| setup.ts | artifact-setup-ts | Documents | Startup lifecycle file covering hooks snapshots, worktree setup, tmux bootstrapping, and file-change watching. | startup |

</details>

<details>
<summary>domain (1)</summary>

| Label | ID | Domain | Summary | Tags |
| --- | --- | --- | --- | --- |
| Documents | documents |  | Local document portfolio grouping for repo snapshots stored under the user's Documents directory. | portfolio-root |

</details>

<details>
<summary>process (7)</summary>

| Label | ID | Domain | Summary | Tags |
| --- | --- | --- | --- | --- |
| Background Agent Execution | process-background-agent-execution | Documents | Task model spanning local shell, local agent, remote agent, teammate, workflow, and MCP monitor execution paths. | tasks, multi-agent |
| Permission Mediation | process-permission-mediation | Documents | Maps remote tool approval requests into locally renderable permission flows and fallback tool stubs. | permissions, approval-flow |
| Plugin And Skill Loading | process-plugin-and-skill-loading | Documents | Loads plugins, skills, and prompt parts while avoiding startup races and stale configuration snapshots. | plugins, skills |
| Remote Session Management | process-remote-session-management | Documents | Control plane for remote sessions with WebSocket reads, HTTP writes, connection lifecycle, and message routing. | remote-runtime, sessions |
| Terminal Agent Runtime | process-terminal-agent-runtime | Documents | Interactive terminal execution loop that assembles prompts, renders UI messages, and coordinates coding-agent behavior. | terminal-ui, agent-loop |
| Transport Recovery | process-transport-recovery | Documents | Stream buffering, serialized writes, reconnect behavior, and bounded recovery paths for network and model output failur… | transport, recovery |
| Worktree Orchestration | process-worktree-orchestration | Documents | Creates or switches isolated worktree sessions, resolves canonical repo roots, and coordinates tmux bootstrapping. | worktrees, session-setup |

</details>

<details>
<summary>provider (6)</summary>

| Label | ID | Domain | Summary | Tags |
| --- | --- | --- | --- | --- |
| Anthropic SDK | provider-anthropic-sdk | Documents | Primary model SDK dependency for message types, streaming, and API error handling. | llm, sdk |
| Axios | provider-axios | Documents | HTTP client used across bridge, analytics, and transport flows. | http, client |
| Bun | provider-bun | Documents | Runtime and build feature provider used by setup and startup code. | runtime, build-tool |
| Git | provider-git | Documents | Repository root and worktree operations depend on Git-aware filesystem behavior. | vcs, worktrees |
| Model Context Protocol SDK | provider-mcp-sdk | Documents | Protocol SDK used for MCP server entrypoints and MCP-aware tool types. | mcp, sdk |
| tmux | provider-tmux | Documents | Optional terminal session isolation layer for worktree and teammate flows. | terminal, session-isolation |

</details>

<details>
<summary>repo (1)</summary>

| Label | ID | Domain | Summary | Tags |
| --- | --- | --- | --- | --- |
| claude_code | claude_code | Documents | Modular TypeScript/Bun coding-agent runtime with a React terminal UI, remote-session bridge, MCP entrypoints, plugin an… | ai-coding-agents, terminal-ui, remote-runtime, mcp, worktrees |

</details>
