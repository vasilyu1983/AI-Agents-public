# Codex Router — Initial Setup

**Copy these 4 files to your repository's `.codex/` folder to enable Codex CLI to use Claude Code skills.**

## Prerequisites

Before deploying the router, ensure:

1. **`.claude/` folder is set up** in your repository:
   ```bash
   # Copy Claude Code Kit to your repo (if not already done)
   cp -r frameworks/claude-code-kit/initial-setup/skills/ .claude/skills/
   cp -r frameworks/claude-code-kit/initial-setup/agents/ .claude/agents/
   cp -r frameworks/claude-code-kit/initial-setup/commands/ .claude/commands/
   ```

2. **Codex CLI is installed** and configured for your repository

## Deployment Steps

### Step 1: Copy Router Files to `.codex/`

```bash
# From your repository root
mkdir -p .codex

# Copy all 4 router files
cp frameworks/codex-kit/initial-setup/codex-router.md .codex/
cp frameworks/codex-kit/initial-setup/codex-mega-prompt.txt .codex/
cp frameworks/codex-kit/initial-setup/codex-router.yaml .codex/

# Optional: Copy test cases for reference
cp frameworks/codex-kit/initial-setup/router-tests.md .codex/
```

### Step 2: Paste Mega-Prompt into Codex Session

```bash
# Start Codex in your repository
codex

# Then paste the entire contents of .codex/codex-mega-prompt.txt
# This tells Codex how to route requests to Claude skills
```

**Important**: The mega-prompt must be pasted at the **start of each Codex session**. This is a one-time setup per session that configures the routing behavior.

### Step 3: Use Claude Skills from Codex

Once the mega-prompt is loaded, Codex will automatically route requests:

```
User: "Review this React component for security issues"
Codex: Agent: frontend-engineer | Skill: software-frontend
       [provides security review using both frameworks]

User: "Optimize this PostgreSQL query"
Codex: Agent: sql-engineer | Skill: ops-database-sql
       [provides SQL optimization using expertise from both]

User: "Design a RAG pipeline for document retrieval"
Codex: Agent: llm-engineer | Skill: ai-rag
       [provides RAG architecture using combined knowledge]
```

## Files Explained

### codex-mega-prompt.txt (8.5KB) — **ESSENTIAL**
**Purpose**: Paste-ready session starter
**Usage**: Paste into Codex at the start of each session
**Contains**:
- Full skills catalog (50 skills)
- Full agents catalog (18 agents)
- Routing rules with priority order
- 12+ diverse examples covering all domains
- Output format specification (`Agent: X | Skill: Y`)

**This is the ONLY file you need to paste.** The other files are for reference.

### codex-router.md (8.4KB) — Reference
**Purpose**: Structured routing documentation
**Usage**: Lookup reference for understanding routing decisions
**Contains**:
- Detailed skill descriptions
- Agent responsibilities and preferred skills
- Complete routing logic (task-specific + domain-specific + code review)
- Priority order explanation
- Conflict resolution rules

**Use this when**:
- Debugging unexpected routing decisions
- Understanding which agent+skill will be chosen for a task
- Extending routing rules for custom skills

### codex-router.yaml (5.7KB) — Metadata
**Purpose**: Configuration and deployment metadata
**Usage**: Reference for system information
**Contains**:
- Version: 1.2
- Last updated: 2025-12-03
- Source directories (`.claude/skills/`, `.claude/agents/`, `.claude/commands/`)
- Deployment paths
- Counts: 18 agents, 50 skills, 30 routing rules
- Compatibility requirements

**Use this when**:
- Checking version compatibility
- Understanding deployment structure
- Verifying skill/agent counts match your setup

### router-tests.md (11KB) — Validation
**Purpose**: Test cases for routing correctness
**Usage**: Verify routing logic works as expected
**Contains**:
- 18 standard test cases (all agent types, new skills, all priority rules)
- 8 edge cases (overrides, conflicts, ambiguity, missing components)
- Expected routes with rationale and priority rule applied

**Use this when**:
- Validating router behavior after deployment
- Testing routing for specific scenarios
- Debugging incorrect routing decisions

## Setup Nuances

### Same-Repo Architecture

The router creates a bridge between two frameworks in the **same repository**:

```
Your Repository
├── .claude/                    # Claude Code Kit (source of truth)
│   ├── skills/                 # 50 operational skills
│   ├── agents/                 # 18 specialized agents
│   └── commands/               # 15 slash commands
└── .codex/                     # Codex Kit (routing layer)
    ├── codex-router.md         # Reference documentation
    ├── codex-mega-prompt.txt   # Session starter (PASTE THIS)
    ├── codex-router.yaml       # Configuration
    └── router-tests.md         # Validation tests

Routing Chain:
Codex CLI → .codex/mega-prompt → .claude/agents/ → .claude/skills/
```

**Key Point**: The router **references** `.claude/` paths, it doesn't duplicate them. This means:
- Update skills once in `.claude/skills/` → both Claude Code and Codex benefit
- No version conflicts or synchronization issues
- Single source of truth for all agent capabilities

### Routing Priority System (4 Tiers)

The router uses a hierarchical priority system to resolve routing decisions:

**1. Explicit User Override** (Highest Priority)
```
User: "agent: backend-engineer | Review this code"
Codex: Agent: backend-engineer | Skill: software-code-review
```
User explicitly specified the agent, so override all other rules.

**2. Task-Specific Routing**
```
User: "Design a RAG pipeline with reranking"
Codex: Agent: llm-engineer | Skill: ai-rag
```
Task type ("RAG pipeline") matches specific routing rule.

**3. Domain-Specific Routing**
```
User: "Build a Next.js dashboard with shadcn/ui"
Codex: Agent: frontend-engineer | Skill: software-frontend
```
Technology stack (Next.js, shadcn/ui) identifies the domain.

**4. Default Fallback** (Lowest Priority)
```
User: "Help me understand this codebase"
Codex: Agent: backend-engineer | Skill: none
```
Ambiguous request falls back to general-purpose agent.

### Conflict Resolution

When multiple routes could apply:

**Multiple Agents Match**: Choose most specialized
```
User: "Review backend API security"
Options: backend-engineer, security-specialist
Codex: Agent: backend-engineer | Skill: ai-mlops
(backend-engineer is more specialized for API review)
```

**Skill Missing**: Route to agent only
```
User: "Explain this algorithm"
Codex: Agent: backend-engineer | Skill: none
(No specific skill needed, agent handles it)
```

**Agent Missing**: Use skill directly (if self-contained)
```
User: "Show me SQL optimization patterns"
Codex: Skill: ops-database-sql
(Skill has standalone patterns)
```

**Both Missing**: Report "no route found"
```
User: "Design a quantum computing algorithm"
Codex: No clear route - this domain not covered by available agents/skills
(Falls back to general-purpose or asks for clarification)
```

## Updating Router

### When Claude Code Kit Changes

If you update Claude Code Kit (add/remove skills or agents), regenerate the router:

```bash
# Use the router builder prompt
cat frameworks/codex-kit/claude-skill-to-codex/prompt.md

# Follow the 8-step process to regenerate all 4 files
# Then redeploy to .codex/
```

### When Routing Seems Incorrect

1. **Check expected behavior** in `router-tests.md`
   - Find similar test case
   - Compare expected vs actual routing

2. **Verify `.claude/` structure**
   - Ensure all skill directories exist
   - Ensure all agent files exist
   - Check file names match router expectations

3. **Verify mega-prompt was pasted correctly**
   - Paste it again at session start
   - Ensure no truncation occurred

4. **Check priority rules**
   - Review `codex-router.md` routing logic
   - Verify which priority tier should apply
   - Check for explicit overrides in user request

## Troubleshooting

### Router Not Working

**Symptoms**: Codex doesn't show `Agent: X | Skill: Y` format

**Fixes**:
1. Paste `codex-mega-prompt.txt` again at session start
2. Verify Codex CLI is using the correct session
3. Check for paste truncation (file is 8.5KB, ensure all content loaded)

### Wrong Agent/Skill Selected

**Symptoms**: Routing doesn't match expectations

**Fixes**:
1. Check `router-tests.md` for similar scenario
2. Review priority rules in `codex-router.md`
3. Add explicit override: `agent: <desired-agent> | <your request>`

### Skills Not Found

**Symptoms**: Codex says skill doesn't exist

**Fixes**:
1. Verify `.claude/skills/` directory structure
2. Check skill names match router catalog (in mega-prompt)
3. Ensure skills were copied from Claude Code Kit `initial-setup/`

### Version Mismatch

**Symptoms**: Router references skills/agents that don't exist

**Fixes**:
1. Check `codex-router.yaml` version and date
2. Compare with Claude Code Kit version
3. Regenerate router if versions don't match

## Support

**Documentation**:
- Main README: `frameworks/codex-kit/README.md`
- Router builder: `frameworks/codex-kit/claude-skill-to-codex/prompt.md`
- Claude Code Kit: `frameworks/claude-code-kit/README.md`

**Validation**:
- Test cases: `router-tests.md` (23 test scenarios)
- Expected routing: `codex-router.md` (complete routing logic)
- Configuration: `codex-router.yaml` (metadata and counts)

**Common Questions**:

Q: Do I need to paste the mega-prompt every time?
A: Yes, paste at the start of each new Codex session.

Q: Can I modify routing rules?
A: Yes, edit `codex-mega-prompt.txt` and paste the modified version. For permanent changes, update the router builder prompt and regenerate.

Q: How do I add a new skill?
A: Add skill to `.claude/skills/`, then regenerate router using `claude-skill-to-codex/prompt.md`.

Q: Can I use this without Claude Code?
A: No, the router references `.claude/` paths. You need both Claude Code Kit (source) and Codex Kit (router).

Q: Does this work with other tools besides Codex?
A: The router is designed for Codex CLI, but the pattern can be adapted for other AI coding tools that support prompt-based configuration.
