# GEMINI.md - Project Overview

This file provides context for Gemini to understand and interact with the "AI Agents" repository.

## Repository Pattern (Universal Formula)

This repository follows a **three-layer architecture** for multi-AI-agent development:

**Layer 1: AI-Specific Instructions** (Root)
- `README.md` - Universal repository overview
- `CLAUDE.md` - Claude Code-specific instructions
- `GEMINI.md` - Gemini-specific instructions (this file)
- `AGENTS.md` - Repository standards and guidelines
- Pattern: Add `CODEX.md`, `CURSOR.md`, etc. for additional AI agents

**Layer 2: Tool-Specific Workspaces** (Operational files)
- `.claude/` - Claude Code workspace (hooks, skills, commands, prompts)
- `.cursor/` - Cursor AI workspace (rules, configurations)
- Pattern: Add `.codex/`, `.windsurf/`, etc. for additional tools

**Layer 3: Shared Documentation** (Portable guides)
- `docs/` - Universal best practices that work in ANY repository
- `docs/rules/` - Catalogs and quick-reference materials
- `docs/testing/` - QA checklists and test harnesses

**Key Insight**: Files in `docs/` are **repository-agnostic**. Copy them to any project's `.claude/` or `.cursor/rules/` for instant best practices.

## Directory Overview

This repository is a curated library of discipline-specific AI agent prompts, configurations, and reference materials. It is designed for prompt engineering workflows, particularly for creating Custom GPTs and other AI agents. The project is highly structured, with a strong emphasis on consistency, documentation, and adherence to platform constraints (especially the 8000-character limit for OpenAI's Custom GPTs).

This is not a traditional software project with compiled code. Instead, it's a "prompt-as-code" project where the primary artifacts are Markdown (`.md`) prompt files and YAML (`.yaml`) configuration files.

## Key Files

*   `README.md`: The main entry point for understanding the repository. It provides a high-level overview, links to key files, and summarizes recent improvements.
*   `AGENTS.md`: Contains detailed guidelines for working with the repository, including critical platform constraints, project structure, development commands, and coding style.
*   `CLAUDE.md`: Provides specific guidance for the Claude AI model when interacting with this repository. It outlines the architecture, template system, and common development tasks.
*   `Productivity/Prompt Engineer/02_master-template.md`: The master template (v3.5) used as the foundation for all new AI agents.
*   `docs/testing/customgpt-knowledge-base-audit.md`: Quality assurance audit for knowledge bases and agent configurations.
*   `docs/testing/prompt-engineer-audit.md`: Validation checklist for prompt engineering and agent design.
*   `docs/`: This directory contains shared documentation, guides, and reference materials for all AI coding assistants.

**AI Agent Protocols** (NEW):
*   `docs/agents framework/` - Complete guides for AI agent communication protocols
    *   **MCP (Model Context Protocol)** - Connect agents to data sources and tools
        *   `mcp/mcp-architecture.md` - Core concepts and technical architecture
        *   `mcp/mcp-server-development.md` - Step-by-step server building guide
        *   `mcp/mcp-claude-integration.md` - Claude Desktop/Code integration
    *   **A2A (Agent-to-Agent Protocol)** - Enable agent collaboration
        *   `a2a/a2a-architecture.md` - Protocol specification and design
        *   `a2a/a2a-implementation.md` - Implementation guide with code examples
        *   `a2a/a2a-examples.md` - Real-world use cases and patterns

## Project Structure

The repository is organized into domain-specific libraries, each containing multiple AI agents.

*   **Domain Libraries:** Directories like `Education/`, `Lifestyle/`, `Productivity/`, `Programming/`, `Research & Analysis/`, and `Writing/` group agents by their area of expertise.
*   **Agent Directory:** Each agent resides in its own directory and typically consists of the following:
    *   `01_agent-name.md`: The main prompt file, always numbered `01`.
    *   `02_sources-agent-name.json`: **NEW STANDARD (2025-10-28)** - Curated web resources for the agent's domain with categorized links, descriptions, and `add_as_web_search` flags.
    *   `03_supplemental.md`: Optional additional documentation or guides.
    *   `0X_data.json`: Optional structured data for compact lookups, mode definitions, or behavioral maps.
    *   `agent-name.yaml`: A configuration file containing variables (like `role_title`, `scope`, etc.) that are interpolated into the Markdown prompt.
    *   `sources/`: A git-ignored directory for research materials.
    *   `archive/`: A git-ignored directory for version history.

*   **Three-File Deliverable Pattern** (New Standard as of 2025-10-28):
    When creating a new Custom GPT or AI Agent, produce THREE essential files:
    1.  `01_agent-name.md` - Main prompt file (<8000 chars for Custom GPT, flexible for Claude/Gemini)
    2.  `agent-name.yaml` - Configuration with role parameters, commands, and constraints
    3.  `02_sources-agent-name.json` - Comprehensive web resources for the agent's domain

    **JSON Sources Structure:**
    ```json
    {
      "metadata": {
        "title": "Agent Name - Sources",
        "description": "Brief description of curated resources",
        "last_updated": "YYYY-MM-DD"
      },
      "category_name": [
        {
          "name": "Resource Name",
          "url": "https://example.com/docs",
          "description": "What this resource covers",
          "add_as_web_search": true|false
        }
      ]
    }
    ```

    **Existing Examples:**
    *   `Programming/AI Agents/02_sources-ai-agents.json` - Agent frameworks (OpenAI, LangChain, Anthropic)
    *   `Programming/LLM/02_sources-llm-engineer.json` - LLM engineering resources
    *   `Programming/DS/02_sources-data-scientist.json` - Data science and ML resources
    *   `Programming/PRD/03_vibe-coding-references.json` - AI coding assistant documentation

*   **Example - Prompt Engineer** (7 files, platform-specific versions):
    *   `01_prompt-engineer-CustomGPT.md` (7,918 chars) - Custom GPT optimized version
    *   `01_prompt-engineer-claude.md` (11,165 chars) - Claude Projects optimized version
    *   `02_master-template.md` (7,893 chars) - Template structure
    *   `03_template-fill-guide.md` (6,853 chars) - Fill instructions
    *   `04_guides-and-modes.json` (22,418 chars) - Deployment & translation data
    *   `05_deployment-guide.md` (4,466 chars) - Modes & cross-model guide
    *   `06_modes-examples.md` (7,032 chars) - Real-world examples

### Client Programs (`[altery]/`)

Client engagements live under `[altery]/`. Two multi-region compliance suites were refreshed on 2025-10-27:

*   `Hawkeye_FinCrime_Prevention/`
    *   Prompts: `01_uk_fincrime-prevention.md` and `11_eu-cy_fincrime-prevention.md` (both on the full 13-section template)
    *   Configs: jurisdiction-specific YAML files (`01_uk_fincrime-prevention.yaml`, `11_eu-cy_fincrime-prevention.yaml`) with aligned `/scan uk-*` and `/scan eu/cy-*` commands
    *   Sources: normalised UK/EU policy PDF libraries inside `sources/UK` and `sources/EU`
*   `RegLens_Regulatory/`
    *   Prompts: `01_uk_regulatory.md` and `11_eu-cy_regulatory.md` (13-section template with audit tables)
    *   Configs: `01_uk_regulatory.yaml`, `11_eu-cy_regulatory.yaml` advertising `/scan fincrime`, `/scan fca`, `/scan payments`, `/scan data`, `/scan thirdparty`, `/scan dora`, `/scan micar`
    *   Sources: refreshed UK/EU control frameworks in `sources/UK` and `sources/EU`

When updating these agents, keep Markdown and YAML command names in lockstep; mismatches surface as missing commands during execution.

## File Format Strategy

See [docs/formatting/README.md](docs/formatting/README.md) for format selection and [docs/formatting/formatting-standards.md](docs/formatting/formatting-standards.md) for shared formatting and TOON standards. Rule of thumb: think → `.md`, recall → `.json`, detect → `.txt`; use TOON for LLM-internal instructions, schemas, and examples as defined in `formatting-standards.md`.

**Important**: The 8000 character limit applies ONLY to `.md` instruction files. Supporting files (`.json`, `.txt`) have NO character limits.

## Token Budget & Directory Exclusions
- Skip reading or indexing archive directories by default to avoid unnecessary token usage
- Exclude globs: `**/archive/**`, `**/Archive/**`
- Notable paths to skip: `docs/archive/`, `docs/customisations/archive/`, `docs/profile/archive/`, all agent `sources/archive/` folders (including under `[altery]/`)
- Only access archive items when the user provides an explicit file path; avoid broad scans
- Recommended search: `rg <pattern> -g '!**/archive/**' -g '!**/Archive/**'`

## Development Workflow

The development process is centered around creating, customizing, and validating prompt files.

1.  **Create a New Agent:** To create a new agent, copy the master template (`Productivity/Prompt Engineer/02_master-template.md`) and create a corresponding `.yaml` configuration file.
2.  **Customize the Prompt:** Fill in the prompt's template variables (`{{variable}}`) using the values from the `.yaml` file.
3.  **Platform-Specific Optimization:** For agents with significant platform differences, create separate optimized versions:
    *   Custom GPT version: `01_agent-name-CustomGPT.md` (must be <8000 chars)
    *   Claude version: `01_agent-name-claude.md` (optimize for artifacts, <thinking> tags, 200k context)
    *   Gemini version: `01_agent-name-gemini.md` (if platform-specific features warrant separate version)
4.  **Validate the Agent:**
    *   **Character Count:** Ensure Custom GPT prompts are under 8000 characters using `wc -c <file_path>`. Claude and Gemini prompts have higher limits but benefit from optimization.
    *   **Placeholders:** Check for any unresolved template placeholders using `rg "{{[^}]+}}" <file_path>`.
    *   **QA Checklist:** Follow the steps in `QA/QA_check_the_lib.md`.

### Prompt ⇄ YAML Alignment (Gemini Tasks)
- After any prompt change, update the paired yaml to match (md is the source of truth).
- Verify:
  - Commands parity: md `## COMMANDS` list equals yaml `commands:` entries.
  - Hard cap: md OUTPUT CONTRACT “Hard cap” equals yaml `max_chars`.
  - Consistency: `framework`, `tone`, and `answer_shape` match md language.
- Quick commands (excluding archives):
  - Extract md commands: `awk '/^## COMMANDS/{f=1;next}/^## /{f=0}f' 01_x.md | rg -o '/[A-Za-z0-9:_-]+' | sort -u`
  - List yaml commands: `rg -N 'name:\\s*/[A-Za-z0-9:_-]+' x.yaml -o | sed 's/.*name:\s*//' | sort -u`

## Key Commands

This project does not have a traditional build process. Instead, development relies on shell commands for searching, validating, and managing the text-based files.

*   **Search for content:**
    *   `rg 'IDENTITY' AgentFolder -n`: Confirm that required template sections are present.
*   **Validate template variables:**
    *   `rg "{{[^}]+}}" AgentFolder/agent_name.md`: Find unresolved template variables.
*   **List configuration files:**
    *   `rg --files -g '*.yaml' Programming/`: List all YAML files in the `Programming` directory.
*   **Check character count:**
    *   `wc -c "path/to/agent.md"`: Get the character count of a prompt file.
*   **Check word count:**
    *   `wc -w "path/to/agent.md"`: Get the word count of a prompt file.
