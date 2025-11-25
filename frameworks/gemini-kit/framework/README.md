# Gemini Router — Initial Setup

**Copy these files to your repository's `.gemini/` folder to enable Gemini CLI to use Claude Code Kit skills and agents via the `/claude-router` command.**

## Prerequisites

Before deploying the router, ensure:

1. **`.claude/` folder is set up** in your repository:

   ```bash
   # Copy Claude Code Kit to your repo (if not already done)
   mkdir -p .claude/{agents,skills,commands}

   cp frameworks/claude-code-kit/initial-setup/agents/*.md .claude/agents/
   cp -r frameworks/claude-code-kit/initial-setup/skills/* .claude/skills/
   cp frameworks/claude-code-kit/initial-setup/commands/*.md .claude/commands/
   ```

2. **`GEMINI.md` exists at the repository root** and describes your project context.

3. **Gemini CLI is installed** and configured for your repository.

## Deployment Steps

### Step 1: Copy Router Files to `.gemini/`

```bash
# From your repository root
mkdir -p .gemini/commands

# Copy router command and docs
cp frameworks/gemini-kit/initial-setup/gemini-router.toml .gemini/commands/claude-router.toml
cp frameworks/gemini-kit/initial-setup/gemini-router.md .gemini/
cp frameworks/gemini-kit/initial-setup/gemini-router.yaml .gemini/

# Optional: Copy test cases for reference
cp frameworks/gemini-kit/initial-setup/router-tests.md .gemini/
```

### Step 2: Use the `/claude-router` Command

Once the router command is installed, you can ask Gemini to route tasks to Claude agents and skills.

#### Example 1: Backend API Development

```bash
gemini run /claude-router "Create a REST API for user authentication with JWT and PostgreSQL"
```

Expected route:
- Agent: backend-engineer
- Skill: software-backend

#### Example 2: SQL Query Optimization

```bash
gemini run /claude-router "Optimize this slow PostgreSQL query and suggest indexes" \
  src/db/slow-query.sql \
  .claude/skills/ops-database-sql/SKILL.md
```

Expected route:
- Agent: sql-engineer
- Skill: ops-database-sql

#### Example 3: RAG Pipeline Design

```bash
gemini run /claude-router "Design a RAG system for legal document retrieval with reranking"
```

Expected route:
- Agent: llm-engineer
- Skill: ai-llm-rag-engineering

### Step 3: Interpret Router Output

For every request, the router command should:

1. Print a routing line on the first line of the response:
   - `Route: Agent: <agent-id> | Skill: <skill-id or none> | Priority: <1-4>`
2. Then provide the full answer from the chosen agent’s perspective, using the chosen skill as the primary knowledge base.

Users can override routing by including explicit hints in their prompt:

- `agent: backend-engineer | ...`
- `skill: ai-llm-rag-engineering | ...`
- `agent: frontend-engineer | skill: ops-devops-platform | ...`

See `.gemini/gemini-router.md` for the full routing catalog and rules.

## Files Explained

### `gemini-router.toml` — `/claude-router` Command

**Purpose**: Defines the Gemini CLI command that performs routing.  
**Location after install**: `.gemini/commands/claude-router.toml`

Contains:
- Description and persona for the router
- Catalog of agents and skills from `.claude/`
- Routing rules and priority system
- Output format specification (`Route: Agent: X | Skill: Y | Priority: N`)

### `gemini-router.md` — Routing Reference

**Purpose**: Human-readable documentation of routing rules.  
**Location after install**: `.gemini/gemini-router.md`

Contains:
- Detailed skill descriptions
- Agent responsibilities and preferred skills
- Task-specific and domain-specific routing rules
- Override and conflict-resolution rules

### `gemini-router.yaml` — Metadata

**Purpose**: Configuration and deployment metadata.  
**Location after install**: `.gemini/gemini-router.yaml`

Contains:
- Version and last-updated date
- Source directories (`.claude/skills/`, `.claude/agents/`, `.claude/commands/`)
- Deployment paths for router files
- Counts: 17 agents, 34 skills, 28 routing rules

### `router-tests.md` — Validation

**Purpose**: Test cases to verify routing correctness.  
**Location after install**: `.gemini/router-tests.md` (optional)

Contains:
- 15 standard test cases (all agent types, all priority rules)
- 8 edge cases (overrides, conflicts, ambiguity, missing components)
- Expected routes with rationale and priority rule applied
