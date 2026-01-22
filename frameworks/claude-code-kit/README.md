# Claude Code Kit - Complete Guide

**Last Updated**: 2025-12-20
**Official Documentation**: [Claude Code Overview](https://docs.claude.com/en/docs/claude-code/overview)
**Skills Format**: [Agent Skills Specification](https://agentskills.io/specification) - Open format maintained by Anthropic
**Status**: PORTABLE - Works for any repository

Production-ready Claude Code setup with 21 agents + 28 commands + 7 hooks.

**Skills**: 79 skills in `frameworks/shared-skills/` (shared with Codex Kit)

**NEW in v3.7**: Skills moved to shared source. Framework now contains agents, commands, hooks only.

**v3.6**: Skills aligned with [agentskills.io](https://agentskills.io) open format specification. Directory structure follows official standard (`scripts/`, `references/`, `assets/`). Progressive disclosure model with <5000 token SKILL.md bodies.

**v3.5**: December 2025 skill refresh with explicit modern best practices headers, authoritative external references (OWASP, OpenTelemetry, Google eng practices), and operational focus ("No theory. No narrative. Only what Claude can execute.").

---

## What is Claude Code?

Claude Code is Anthropic's official CLI tool for AI-assisted software development. It provides six powerful features:

1. **[Agents](docs/agents.md)** - Specialized AI subagents for specific tasks
2. **[Skills](docs/skills.md)** - Knowledge bases with progressive disclosure
3. **[Commands](docs/commands.md)** - Slash-triggered prompt templates
4. **[Hooks](docs/hooks.md)** - Event-driven bash automation
5. **[CLAUDE.md](docs/claudemd.md)** - Project memory and instructions
6. **[MCP](docs/mcp.md)** - External data source integration
7. **[Workflows](docs/workflows.md)** - End-to-end development workflows

---

## Quick Start

### 5-Minute Setup

1. **Install Claude Code** (if not already installed)
2. **Create `.claude/` structure**:
   ```bash
   mkdir -p .claude/{agents,skills,commands,hooks}
   ```
3. **Create your first agent** - [Agents Guide](docs/agents.md)
4. **Create your first skill** - [Skills Guide](docs/skills.md)
5. **Create a command** - [Commands Guide](docs/commands.md)

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

**NEW**: This repository includes a **complete Claude Code framework** in [framework/](framework/) with production-ready files that you can copy directly to your `.claude/` directory and use immediately.

### Quick Install (1 minute)

```bash
cd your-project/

# Create .claude directories
mkdir -p .claude/{agents,skills,commands,hooks}

# Copy framework files (agents, commands, hooks)
cp /path/to/framework/agents/*.md .claude/agents/
cp /path/to/framework/commands/*.md .claude/commands/
cp /path/to/framework/hooks/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
cp /path/to/framework/settings/settings-template.json .claude/settings.json

# Copy skills from shared source
cp -r /path/to/frameworks/shared-skills/skills/* .claude/skills/
```

### What's Included

| Component | Count | Source |
| --------- | ----- | ------ |
| **Agents** | 21 | `framework/agents/` |
| **Commands** | 28 | `framework/commands/` |
| **Hooks** | 7 | `framework/hooks/` |
| **Skills** | 76 | `shared-skills/skills/` (separate) |

Skills are maintained in a shared source (`frameworks/shared-skills/`) used by both Claude Code Kit and Codex Kit.

### Key Agents

**AI/ML Specialists (3)**:
- [**ai-agents-builder**](framework/agents/ai-agents-builder.md) - AI agent architecture & patterns
- [**data-scientist**](framework/agents/data-scientist.md) - ML workflows, EDA, modeling, deployment
- [**llm-engineer**](framework/agents/llm-engineer.md) - LLM development, RAG, fine-tuning

**Software Engineers (7)**:
- [**backend-engineer**](framework/agents/backend-engineer.md) - REST/GraphQL APIs, databases, auth
- [**frontend-engineer**](framework/agents/frontend-engineer.md) - Multi-framework (Next.js, Vue/Nuxt, Angular, Svelte, Remix, Vite+React)
- [**mobile-engineer**](framework/agents/mobile-engineer.md) - iOS, Android, React Native
- [**crypto-engineer**](framework/agents/crypto-engineer.md) - Web3, blockchain, smart contracts
- [**devops-engineer**](framework/agents/devops-engineer.md) - IaC, CI/CD, Kubernetes
- [**sql-engineer**](framework/agents/sql-engineer.md) - SQL optimization, query tuning
- [**security-specialist**](framework/agents/security-specialist.md) - AppSec, OWASP, threat modeling

**Quality & Architecture (5)**:
- [**code-reviewer**](framework/agents/code-reviewer.md) - Code quality & security review
- [**test-architect**](framework/agents/test-architect.md) - Test strategy & QA planning
- [**system-architect**](framework/agents/system-architect.md) - System design & architecture
- [**product-manager**](framework/agents/product-manager.md) - Product strategy & roadmaps
- [**prd-architect**](framework/agents/prd-architect.md) - Product requirements & specs

**Specialized (2)**:
- [**prompt-engineer**](framework/agents/prompt-engineer.md) - Prompt design & optimization
- [**smm-strategist**](framework/agents/smm-strategist.md) - Social media marketing

**New in v3.5** (2025-12-18): **December 2025 Skill Refresh**

All 79 skills updated with:

- Explicit "Modern Best Practices (December 2025)" headers with authoritative URLs
- Operational focus: "No theory. No narrative. Only what Claude can execute."
- Cross-skill linking with relative paths
- Progressive disclosure (SKILL.md as navigation hub, references/ for depth)

**v3.4** (2025-12-09): **Three-Router Architecture**

- [**router-engineering**](../shared-skills/skills/router-engineering/SKILL.md) - Routes technical questions through 33 engineering + AI/ML skills
- [**router-operations**](../shared-skills/skills/router-operations/SKILL.md) - Routes QA, DevOps, testing through 19 operations skills
- Enhanced [**router-startup**](../shared-skills/skills/router-startup/SKILL.md) - Now includes marketing (4 skills), document creation (4 skills), and cross-router orchestration patterns

**v3.3** (2025-12-09):

- [**startup-validator**](framework/agents/startup-validator.md) - Startup idea validation, competitive analysis, GTM strategy
- [**ux-researcher**](framework/agents/ux-researcher.md) - UX research, usability testing, accessibility auditing
- [**data-engineer**](framework/agents/data-engineer.md) - Data pipelines, lakehouse architecture, SQL optimization
- [**qa-engineer**](framework/agents/qa-engineer.md) - Quality assurance, debugging, observability, LLM agent testing

**v3.2** (2025-12-09): **Startup Validation Machine** - Complete startup skill suite with 8 new skills for idea validation, competitive analysis, business models, fundraising, GTM, trend prediction, review mining, plus `qa-agent-testing` for LLM agent testing protocols.

**v3.1** (2025-12-08): UX skills updated with WCAG 3.0 preview, React Aria recommendations, AI design tools (Figma AI, Visily), LLM-assisted UX evaluation research, shadcn/ui 2025 components.

**v3.0** (2025-11-20): Expanded to 17 agents + 50 skills + 22 commands + 7 automation hooks with complete four-layer architecture (hooks → commands → agents → skills).

See [framework/README.md](framework/README.md) for complete documentation, usage examples, and [ARCHITECTURE-DIAGRAM.md](framework/ARCHITECTURE-DIAGRAM.md) for visual architecture overview.

### Three-Router Architecture

Intelligent skill orchestration across 79 skills through three domain-specific routers:

```text
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│    router-startup     │  │  router-engineering   │  │  router-operations    │
│  Business & Startup   │  │  Technical & AI/ML    │  │   QA & DevOps         │
│  23 skills            │  │  33 skills            │  │   19 skills           │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
```

| Router | Skills | Domain |
| ------ | ------ | ------ |
| [**router-startup**](../shared-skills/skills/router-startup/SKILL.md) | 23 | Business validation, marketing, documents, product |
| [**router-engineering**](../shared-skills/skills/router-engineering/SKILL.md) | 33 | AI/ML, software, data, Claude Code framework |
| [**router-operations**](../shared-skills/skills/router-operations/SKILL.md) | 19 | QA, testing, DevOps, git, observability |

**Cross-router handoffs**: Routers automatically hand off to each other based on query domain:

- "Build an API" → `router-engineering`
- "Price my product" → `router-startup`
- "Deploy and test" → `router-operations`

See [router-startup](../shared-skills/skills/router-startup/SKILL.md) for cross-router workflow patterns.

### Startup Validation Suite

Complete startup validation workflow with 8 specialized skills:

| Skill | Description |
| ----- | ----------- |
| [**startup-idea-validation**](../shared-skills/skills/startup-idea-validation/SKILL.md) | 9-dimension scoring with Go/No-Go decisions |
| [**startup-competitive-analysis**](../shared-skills/skills/startup-competitive-analysis/SKILL.md) | Deep competitive intelligence, market mapping, positioning |
| [**startup-business-models**](../shared-skills/skills/startup-business-models/SKILL.md) | Revenue model design, unit economics, pricing strategy |
| [**startup-fundraising**](../shared-skills/skills/startup-fundraising/SKILL.md) | Fundraising strategy, pitch prep, investor targeting |
| [**startup-go-to-market**](../shared-skills/skills/startup-go-to-market/SKILL.md) | GTM strategy, PLG/sales-led motion, growth loops |
| [**startup-review-mining**](../shared-skills/skills/startup-review-mining/SKILL.md) | Pain extraction from G2, Capterra, App Store, Reddit, HN |
| [**startup-trend-prediction**](../shared-skills/skills/startup-trend-prediction/SKILL.md) | 2-3yr lookback → 1-2yr forward trend analysis |

### Agent Testing

| Skill | Description |
| ----- | ----------- |
| [**qa-agent-testing**](../shared-skills/skills/qa-agent-testing/SKILL.md) | LLM agent/persona testing: 10-task test suites, refusal edge cases, 6-dimension scoring rubric |

### Product Management Suite ⭐

**NEW**: Complete product management workflow with 5 dedicated commands + 120 curated sources:

```bash
/pm-strategy [product]    # Generate product strategy (vision, diagnosis, bets, OKRs)
/pm-roadmap [timeframe]   # Create outcome-based roadmap (Now/Next/Later)
/pm-discovery [problem]   # Plan discovery sprint (interviews, experiments, OST)
/pm-okrs [quarter]        # Define OKRs and metric trees
/pm-positioning [product] # Create strategic positioning (Dunford framework)
```

**Powered by [product-management skill](../shared-skills/skills/product-management/SKILL.md)**:

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

You: "/startup-validate AI writing assistant for sales teams"
Claude: [Runs 9-dimension validation with GO/NO-GO recommendation]

You: "/startup-compete CRM market for SMBs"
Claude: [Generates competitive analysis with battlecards and positioning]

You: "/startup-gtm developer documentation platform"
Claude: [Creates GTM strategy with ICP, channels, launch plan]

You: "/ux-research onboarding flow optimization"
Claude: [Creates research plan with interview guide, usability test protocol]

You: "/agent-test customer-support-bot"
Claude: [Runs 10-task test suite with 6-dimension scoring]

You: "/data-pipeline customer analytics from Stripe and product events"
Claude: [Designs data pipeline with ingestion, transformation, serving layers]
```

---

## Documentation Structure

### Guides (Learn by Doing)

- **[Architecture](docs/claude-architecture.md)** - How components work together
- **[Examples](docs/claude-examples.md)** - Complete working examples

### Reference (Look Up Details)

- **[Agents Reference](docs/agents.md)** - Agent YAML frontmatter, tools, models
- **[Skills Reference](docs/skills.md)** - Progressive disclosure, references/
- **[Commands Reference](docs/commands.md)** - $ARGUMENTS, best practices
- **[Hooks Reference](docs/hooks.md)** - Events, environment variables, exit codes
- **[CLAUDE.md Reference](docs/claudemd.md)** - Project vs user, precedence
- **[MCP Reference](docs/mcp.md)** - Database, filesystem, git integration
- **[Workflows Reference](docs/workflows.md)** - Development workflows
- **[Clean Code Standard](../shared-skills/skills/software-clean-code-standard/)** - Canonical clean code rules (`CC-*`) and operational checklists
- **[Code Review Resources](../shared-skills/skills/software-code-review/references/)** - Review workflow resources and practice checklists

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

See [Agents Reference](docs/agents.md)

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

See [Skills Reference](docs/skills.md)

```
.claude/skills/
└── skill-name/
    ├── SKILL.md           # Main reference
    └── references/         # Detailed docs
```

```markdown
---
name: skill-name
description: What this provides
---

# Skill Name

High-level concepts...

See `references/` for details.
```

### Create a Command

See [Commands Reference](docs/commands.md)

`.claude/commands/command-name.md`:
```markdown
# Command Title

Instructions for: $ARGUMENTS

Use `agent-name` agent to...
```

**Usage**: `/command-name some arguments`

### Create a Hook

See [Hooks Reference](docs/hooks.md)

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

See [CLAUDE.md Reference](docs/claudemd.md)

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

See [MCP Reference](docs/mcp.md)

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

See [Examples Guide](docs/claude-examples.md#pattern-1-automated-code-quality-pipeline)

### Pattern 2: Security-First Development

**Components**:
- `security` skill → OWASP guidelines
- `security-auditor` agent → Vulnerability scanning
- `/security-audit` command → Easy invocation

See [Examples Guide](docs/claude-examples.md#pattern-2-secure-feature-development)

### Pattern 3: Test-Driven Development

**Components**:
- `testing` skill → TDD best practices
- `test-engineer` agent → Test generation
- `/test` command → Quick test creation
- Stop hook → Auto-run tests

See [Examples Guide](docs/claude-examples.md#pattern-3-api-development-workflow)

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

See [Agents Reference](docs/agents.md#best-practices)

### Skill Creation

Per [agentskills.io/specification](https://agentskills.io/specification):

✅ **DO**:

- Keep SKILL.md under 500 lines (<5000 tokens)
- Use `references/` for detailed content (progressive disclosure)
- Use `scripts/` for executable code, `assets/` for static files
- Include practical code examples
- Write action-oriented descriptions with keywords

❌ **DON'T**:
- Put everything in SKILL.md (thousands of lines)
- Create overlapping skills
- Write generic content without examples
- Use nested file reference chains

See [Skills Reference](docs/skills.md#best-practices)

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

See [Commands Reference](docs/commands.md#best-practices)

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

See [Hooks Reference](docs/hooks.md#best-practices)

---

## Security

### Critical Security Rules

1. **Hooks run with your user permissions** - No sandboxing
2. **Validate all hook inputs** - Prevent injection attacks
3. **Use environment variables** - Never hardcode credentials
4. **Limit MCP permissions** - Minimal necessary access
5. **Review third-party code** - Understand what runs

See [Hooks Reference - Security](docs/hooks.md#security)

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

Complete working examples available in [Examples Guide](docs/claude-examples.md):

1. **Security Audit Agent** - Full security scanning setup
2. **API Design Skill** - RESTful API knowledge base
3. **Code Review Command** - Automated review workflow
4. **Auto-format Hook** - Automatic code formatting
5. **E-commerce CLAUDE.md** - Project instructions
6. **PostgreSQL MCP** - Database integration

---

## Official Resources

### Agent Skills Open Format

- **[Agent Skills Specification](https://agentskills.io/specification)** - Complete format specification for SKILL.md
- **[What Are Skills?](https://agentskills.io/what-are-skills)** - Conceptual overview and progressive disclosure
- **[Integrate Skills](https://agentskills.io/integrate-skills)** - Implementation patterns for agents
- **[Anthropic Skills Repository](https://github.com/anthropics/skills)** - Official example skills
- **[Agent Skills Library](https://github.com/agentskills/agentskills)** - Reference library for validation

### Claude Code Documentation

- **[Claude Code Overview](https://docs.claude.com/en/docs/claude-code/overview)** - Official overview
- **[Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents)** - Agents documentation
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
2. **Review [Architecture](docs/claude-architecture.md)** - Understand how it all works
3. **Explore [Examples](docs/claude-examples.md)** - See real implementations
4. **Reference docs as needed** - Detailed specifications for each feature

---

## Quick Links

**Learn**:

- [Architecture](docs/claude-architecture.md)
- [Examples](docs/claude-examples.md)

**Reference**:

- [Agents](docs/agents.md) | [Skills](docs/skills.md) | [Commands](docs/commands.md)
- [Hooks](docs/hooks.md) | [CLAUDE.md](docs/claudemd.md) | [MCP](docs/mcp.md) | [Workflows](docs/workflows.md)

**Official**:

- [Agent Skills Specification](https://agentskills.io/specification)
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/overview)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

**This documentation covers official Claude Code features** and skills aligned with the [Agent Skills open format](https://agentskills.io) maintained by Anthropic.
