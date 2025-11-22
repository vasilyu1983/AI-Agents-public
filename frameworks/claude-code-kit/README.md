# Claude Code Kit - Complete Guide

**Last Updated**: 2025-11-20
**Official Documentation**: [Claude Code Overview](https://docs.claude.com/en/docs/claude-code/overview)
**Status**: PORTABLE - Works for any repository

Production-ready Claude Code setup with 17 agents + 34 skills + 20 commands + 7 hooks.

---

## What is Claude Code?

Claude Code is Anthropic's official CLI tool for AI-assisted software development. It provides six powerful features:

1. **[Agents](reference/agents.md)** - Specialized AI subagents for specific tasks
2. **[Skills](reference/skills.md)** - Knowledge bases with progressive disclosure
3. **[Commands](reference/commands.md)** - Slash-triggered prompt templates
4. **[Hooks](reference/hooks.md)** - Event-driven bash automation
5. **[CLAUDE.md](reference/claudemd.md)** - Project memory and instructions
6. **[MCP](reference/mcp.md)** - External data source integration

---

## Quick Start

### 5-Minute Setup

1. **Install Claude Code** (if not already installed)
2. **Create `.claude/` structure**:
   ```bash
   mkdir -p .claude/{agents,skills,commands,hooks}
   ```
3. **Create your first agent** - [Agents Guide](reference/agents.md)
4. **Create your first skill** - [Skills Guide](reference/skills.md)
5. **Create a command** - [Commands Guide](reference/commands.md)

### First Agent Example

`.claude/agents/code-reviewer.md`:
```markdown
---
name: code-reviewer
description: Systematic code review for quality, security, and maintainability
tools: Read, Grep, Bash
model: sonnet
---

# Code Reviewer Agent

You are a senior software engineer performing systematic code reviews.

## Review Checklist

1. **Correctness** - Does the code work as intended?
2. **Security** - Any vulnerabilities?
3. **Performance** - Obvious inefficiencies?
4. **Maintainability** - Is it readable?
5. **Testing** - Adequate test coverage?

Provide specific, actionable feedback with severity ratings.
```

**Usage**:
```
You: "Review the authentication code"
Claude: [Automatically invokes code-reviewer agent]
```

---

## Production-Ready Framework

**NEW**: This repository includes a **complete Claude Code framework** in [initial-setup/](initial-setup/) with 72 production-ready files that you can copy directly to your `.claude/` directory and use immediately.

### Quick Install (1 minute)

```bash
cd your-project/

# Create .claude directories
mkdir -p .claude/{agents,skills,commands,hooks}

# Copy ALL framework files
cp /path/to/initial-setup/agents/*.md .claude/agents/
cp -r /path/to/initial-setup/skills/* .claude/skills/
cp /path/to/initial-setup/commands/*.md .claude/commands/
cp /path/to/initial-setup/hooks/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
cp /path/to/initial-setup/hooks/settings-template.json .claude/settings.json
```

### What's Included

| Component | Count | Purpose |
|-----------|-------|---------|
| **Agents** | 17 | Specialized AI roles (backend, frontend, mobile, LLM, DevOps, PM, crypto, security, etc.) |
| **Skills** | 34 | Domain knowledge bases with templates and curated web resources |
| **Commands** | 20 | Quick workflow access (code review, testing, architecture, deployment, product management) |
| **Hooks** | 7 | Automated guardrails (formatting, security, testing, cost tracking, notifications) |

**Total**: 78 production-ready files

### Key Agents

**AI/ML Specialists (3)**:
- [**ai-agents-builder**](initial-setup/agents/ai-agents-builder.md) - AI agent architecture & patterns
- [**data-scientist**](initial-setup/agents/data-scientist.md) - ML workflows, EDA, modeling, deployment
- [**llm-engineer**](initial-setup/agents/llm-engineer.md) - LLM development, RAG, fine-tuning

**Software Engineers (7)**:
- [**backend-engineer**](initial-setup/agents/backend-engineer.md) - REST/GraphQL APIs, databases, auth
- [**frontend-engineer**](initial-setup/agents/frontend-engineer.md) - Multi-framework (Next.js, Vue/Nuxt, Angular, Svelte, Remix, Vite+React)
- [**mobile-engineer**](initial-setup/agents/mobile-engineer.md) - iOS, Android, React Native
- [**crypto-engineer**](initial-setup/agents/crypto-engineer.md) - Web3, blockchain, smart contracts
- [**devops-engineer**](initial-setup/agents/devops-engineer.md) - IaC, CI/CD, Kubernetes
- [**sql-engineer**](initial-setup/agents/sql-engineer.md) - SQL optimization, query tuning
- [**security-specialist**](initial-setup/agents/security-specialist.md) - AppSec, OWASP, threat modeling

**Quality & Architecture (5)**:
- [**code-reviewer**](initial-setup/agents/code-reviewer.md) - Code quality & security review
- [**test-architect**](initial-setup/agents/test-architect.md) - Test strategy & QA planning
- [**system-architect**](initial-setup/agents/system-architect.md) - System design & architecture
- [**product-manager**](initial-setup/agents/product-manager.md) - Product strategy & roadmaps
- [**prd-architect**](initial-setup/agents/prd-architect.md) - Product requirements & specs

**Specialized (3)**:
- [**prompt-engineer**](initial-setup/agents/prompt-engineer.md) - Prompt design & optimization
- [**smm-strategist**](initial-setup/agents/smm-strategist.md) - Social media marketing

**New in v3.0** (2025-11-20): Expanded to 17 agents + 34 skills + 7 automation hooks with complete four-layer architecture (hooks → commands → agents → skills).

See [initial-setup/README.md](initial-setup/README.md) for complete documentation, usage examples, and [ARCHITECTURE-DIAGRAM.md](initial-setup/ARCHITECTURE-DIAGRAM.md) for visual architecture overview.

### Product Management Suite ⭐

**NEW**: Complete product management workflow with 5 dedicated commands + 120 curated sources:

```bash
/pm-strategy [product]    # Generate product strategy (vision, diagnosis, bets, OKRs)
/pm-roadmap [timeframe]   # Create outcome-based roadmap (Now/Next/Later)
/pm-discovery [problem]   # Plan discovery sprint (interviews, experiments, OST)
/pm-okrs [quarter]        # Define OKRs and metric trees
/pm-positioning [product] # Create strategic positioning (Dunford framework)
```

**Powered by [product-management skill](initial-setup/skills/product-management/SKILL.md)**:

- 120 curated sources (Teresa Torres, April Dunford, SVPG, OpenAI Evals, Anthropic)
- 10 resource guides (discovery, strategy, roadmaps, AI/LLM products, data products)
- 17 copy-paste templates (customer interviews, OKRs, roadmaps, positioning)
- Current best practices (2024-2025 frameworks, agentic AI, responsible AI)

### Example Usage

```
You: "/pm-strategy SalesMate CRM"
Claude: [Generates strategy with vision, competitive analysis, strategic bets, OKRs]

You: "/pm-discovery reduce-cart-abandonment"
Claude: [Creates discovery plan with interview script, OST, experiments]

You: "/prd user authentication feature"
Claude: [Generates complete PRD with requirements, metrics, risks]

You: "/agent-plan customer support chatbot"
Claude: [Creates roadmap with architecture, milestones, risks]

You: "/ds-explore dataset.csv target=churn"
Claude: [Performs EDA with insights, correlations, next steps]

You: "/llm-finetune classify support tickets"
Claude: [Generates fine-tuning plan with config, evaluation, costs]

You: "/sql-optimize slow user query"
Claude: [Analyzes query, suggests indexes, shows improvement]

You: "/devops-pipeline deploy Node.js app"
Claude: [Creates GitHub Actions workflow with K8s deployment]

You: "/prompt-design structured output for user feedback"
Claude: [Creates production-ready prompt with test cases and validation]

You: "/backend-design REST API for task management"
Claude: [Generates backend with Prisma schema, auth, tests, deployment]

You: "/frontend-design dashboard with data table"
Claude: [Creates Next.js components with TypeScript, Tailwind, accessibility]

You: "/mobile-design user profile with image upload"
Claude: [Implements mobile feature for iOS/Android with offline support]
```

---

## Documentation Structure

### Guides (Learn by Doing)

- **[Architecture](guides/claude-architecture.md)** - How components work together
- **[Examples](guides/claude-examples.md)** - Complete working examples

### Reference (Look Up Details)

- **[Agents Reference](reference/agents.md)** - Agent YAML frontmatter, tools, models
- **[Skills Reference](reference/skills.md)** - Progressive disclosure, resources/
- **[Commands Reference](reference/commands.md)** - $ARGUMENTS, best practices
- **[Hooks Reference](reference/hooks.md)** - Events, environment variables, exit codes
- **[CLAUDE.md Reference](reference/claudemd.md)** - Project vs user, precedence
- **[MCP Reference](reference/mcp.md)** - Database, filesystem, git integration

---

## Core Concepts

### The Six Official Features

| Feature | Purpose | Location | When to Use |
|---------|---------|----------|-------------|
| **Agents** | Do complex work | `.claude/agents/*.md` | Multi-step tasks, specialized analysis |
| **Skills** | Provide knowledge | `.claude/skills/*/SKILL.md` | Domain expertise, best practices |
| **Commands** | User shortcuts | `.claude/commands/*.md` | Frequently used prompts |
| **Hooks** | Automate events | `.claude/hooks/*.sh` | Auto-format, validation, testing |
| **CLAUDE.md** | Project memory | `.claude/CLAUDE.md` | Project context, standards |
| **MCP** | External data | `.claude/.mcp.json` | Database, API, filesystem access |

### When to Use What

**Agents** - Complex, multi-step work:
```
You: "Review this code for security issues"
Claude: [Invokes security-auditor agent]
```

**Skills** - Domain knowledge agents can reference:
```
You: "Design a REST API"
Claude: [Consults api-design skill automatically]
```

**Commands** - Quick shortcuts:
```
/review auth.js
/security-audit
/test UserController
```

**Hooks** - Automatic actions:
```
PostToolUse: Auto-format files after editing
Stop: Run tests when Claude finishes
PreToolUse: Block dangerous bash commands
```

**CLAUDE.md** - Project instructions:
```markdown
# Project: E-commerce Platform

## Architecture
Node.js microservices...

## Code Standards
- TypeScript strict mode
- 80% test coverage required
```

**MCP** - External data:
```
You: "Show users from database"
Claude: [Queries PostgreSQL via MCP]
```

---

## Quick Reference

### Create an Agent

See [Agents Reference](reference/agents.md)

```markdown
---
name: agent-name
description: When to use this agent
tools: Read, Grep, Bash
model: sonnet
---

# Agent Name

Agent instructions...
```

### Create a Skill

See [Skills Reference](reference/skills.md)

```
.claude/skills/
└── skill-name/
    ├── SKILL.md           # Main reference
    └── resources/         # Detailed docs
```

```markdown
---
name: skill-name
description: What this provides
---

# Skill Name

High-level concepts...

See `resources/` for details.
```

### Create a Command

See [Commands Reference](reference/commands.md)

`.claude/commands/command-name.md`:
```markdown
# Command Title

Instructions for: $ARGUMENTS

Use `agent-name` agent to...
```

**Usage**: `/command-name some arguments`

### Create a Hook

See [Hooks Reference](reference/hooks.md)

`.claude/hooks/post-tool-use.sh`:
```bash
#!/bin/bash
set -euo pipefail

if [[ "$CLAUDE_TOOL_NAME" == "Edit" ]]; then
  prettier --write "$CLAUDE_FILE_PATHS"
fi
```

**Configure** in `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use.sh"
          }
        ]
      }
    ]
  }
}
```

### Create CLAUDE.md

See [CLAUDE.md Reference](reference/claudemd.md)

`.claude/CLAUDE.md`:
```markdown
# Project Name

## Architecture
System design...

## Code Standards
- Requirement 1
- Requirement 2

## When Working on This Project
1. Instruction 1
2. Instruction 2

## Agent Preferences
- Use `agent-name` for task-type
```

### Configure MCP

See [MCP Reference](reference/mcp.md)

`.claude/.mcp.json`:
```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

---

## Common Patterns

### Pattern 1: Code Quality Pipeline

**Components**:
- PreToolUse hook → Validate commands
- PostToolUse hook → Auto-format files
- Stop hook → Run tests
- `/review` command → Invoke code-reviewer

See [Examples Guide](guides/claude-examples.md#pattern-1-automated-code-quality-pipeline)

### Pattern 2: Security-First Development

**Components**:
- `security` skill → OWASP guidelines
- `security-auditor` agent → Vulnerability scanning
- `/security-audit` command → Easy invocation

See [Examples Guide](guides/claude-examples.md#pattern-2-secure-feature-development)

### Pattern 3: Test-Driven Development

**Components**:
- `testing` skill → TDD best practices
- `test-engineer` agent → Test generation
- `/test` command → Quick test creation
- Stop hook → Auto-run tests

See [Examples Guide](guides/claude-examples.md#pattern-3-api-development-workflow)

---

## Best Practices

### Agent Development

✅ **DO**:
- Give agents clear, specific purposes
- Use minimal tool permissions
- Choose appropriate models (sonnet for most tasks)
- Include structured output formats

❌ **DON'T**:
- Create vague, general-purpose agents
- Grant all tools to every agent
- Use opus for simple tasks (expensive)

See [Agents Reference](reference/agents.md#best-practices)

### Skill Creation

✅ **DO**:
- Keep SKILL.md concise (overview only)
- Use `resources/` for detailed content (progressive disclosure)
- Focus each skill on single domain
- Include practical code examples

❌ **DON'T**:
- Put everything in SKILL.md (thousands of lines)
- Create overlapping skills
- Write generic content without examples

See [Skills Reference](reference/skills.md#best-practices)

### Command Design

✅ **DO**:
- Provide clear, detailed instructions
- Invoke agents for complex tasks
- Use `$ARGUMENTS` for user input
- Specify expected output format

❌ **DON'T**:
- Write vague command prompts
- Duplicate agent logic in commands
- Ignore user input

See [Commands Reference](reference/commands.md#best-practices)

### Hook Development

✅ **DO**:
- Validate all inputs with regex
- Quote variables properly
- Use absolute paths
- Keep hooks fast (<1 second)
- Test manually before deploying

❌ **DON'T**:
- Use `eval` with user input
- Trust unvalidated file paths
- Run slow operations synchronously
- Skip security validation

See [Hooks Reference](reference/hooks.md#best-practices)

---

## Security

### Critical Security Rules

1. **Hooks run with your user permissions** - No sandboxing
2. **Validate all hook inputs** - Prevent injection attacks
3. **Use environment variables** - Never hardcode credentials
4. **Limit MCP permissions** - Minimal necessary access
5. **Review third-party code** - Understand what runs

See [Hooks Reference - Security](reference/hooks.md#security)

### Hook Security Example

```bash
#!/bin/bash
set -euo pipefail

# ✅ Good - Validate input
if [[ "$file" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then
  process_file "$file"
else
  echo "ERROR: Invalid file path" >&2
  exit 2
fi

# ❌ Bad - Command injection risk
eval "$UNTRUSTED_INPUT"
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Agent not loading | Check YAML frontmatter, name matches filename |
| Skill not accessible | Verify `SKILL.md` exists, check frontmatter |
| Command not found | Filename must match command name exactly |
| Hook not running | Make executable: `chmod +x .claude/hooks/*.sh` |
| MCP connection error | Check credentials, verify server exists |

See detailed troubleshooting in each reference guide.

---

## Examples

Complete working examples available in [Examples Guide](guides/claude-examples.md):

1. **Security Audit Agent** - Full security scanning setup
2. **API Design Skill** - RESTful API knowledge base
3. **Code Review Command** - Automated review workflow
4. **Auto-format Hook** - Automatic code formatting
5. **E-commerce CLAUDE.md** - Project instructions
6. **PostgreSQL MCP** - Database integration

---

## Official Resources

### Anthropic Documentation

- **[Claude Code Overview](https://docs.claude.com/en/docs/claude-code/overview)** - Official overview
- **[Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents)** - Agents documentation
- **[Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)** - Skills blog post
- **[Hooks](https://docs.claude.com/en/docs/claude-code/hooks)** - Hooks documentation
- **[Commands](https://docs.claude.com/en/docs/claude-code/commands)** - Commands documentation
- **[CLAUDE.md](https://docs.claude.com/en/docs/claude-code/claudemd)** - Project memory
- **[MCP](https://docs.claude.com/en/docs/claude-code/mcp)** - Model Context Protocol
- **[Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)** - Official best practices

### Community

- **[GitHub Issues](https://github.com/anthropics/claude-code/issues)** - Report issues

---

## Next Steps

1. **Start with Quick Start above** - 5-minute setup with first agent
2. **Review [Architecture](guides/claude-architecture.md)** - Understand how it all works
3. **Explore [Examples](guides/claude-examples.md)** - See real implementations
4. **Reference docs as needed** - Detailed specifications for each feature

---

## Quick Links

**Learn**:
- [Architecture](guides/claude-architecture.md)
- [Examples](guides/claude-examples.md)

**Reference**:
- [Agents](reference/agents.md) | [Skills](reference/skills.md) | [Commands](reference/commands.md)
- [Hooks](reference/hooks.md) | [CLAUDE.md](reference/claudemd.md) | [MCP](reference/mcp.md)

**Official**:
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/overview)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

**This documentation covers official Claude Code features only** and is based entirely on Anthropic's official documentation.
