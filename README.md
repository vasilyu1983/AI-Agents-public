# AI Agents Library

## Production-Ready AI Agent Prompts & Skills

<div align="center">

A curated collection of **28 Custom GPT agents** and **62 AI coding agent skills** for ChatGPT, Claude Code, Codex CLI, and Gemini CLI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Custom GPTs](https://img.shields.io/badge/Custom%20GPTs-28-blue)](./custom-gpt)
[![Skills](https://img.shields.io/badge/Skills-62-purple)](./frameworks/shared-skills)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Twitter Follow](https://img.shields.io/twitter/follow/vasilyu?style=social)](https://twitter.com/vasilyu)

[Quick Start](#quick-start) • [Custom GPTs](#custom-gpt-agents) • [Skills](#ai-coding-agent-skills) • [Contributing](#contributing)

</div>

---

## What's Inside

This repository contains **28 specialized Custom GPT agents** and **62 AI coding agent skills** organized by domain. All agents follow a consistent template structure. All skills follow the [Agent Skills specification](https://agentskills.io/specification).

### What Makes This Different?

- **Production-Ready**: Every agent and skill tested for real-world use
- **Multi-Platform**: Custom GPTs for ChatGPT; skills for Claude Code, Codex CLI, and Gemini CLI
- **62 Domain Skills**: Software, AI/ML, QA, DevOps, data, agents, and more
- **Curated Resources**: JSON source files with curated references per domain
- **Copy-Paste Ready**: Drop skills directly into your `.claude/skills/` or `.codex/skills/` workspace

## Repository Architecture

```text
AI-Agents-public/
├── custom-gpt/                    # 28 Custom GPT agents
│   ├── education/                 # Learning and tutoring
│   ├── lifestyle/                 # Health, fitness, entertainment
│   ├── productivity/              # Business and professional tools
│   ├── programming/               # Software development
│   ├── research-n-analysis/       # Strategy and consulting
│   └── writing/                   # Content creation
├── frameworks/
│   └── shared-skills/             # 62 AI coding agent skills
│       └── skills/
│           ├── ai-*/              # AI/ML skills (8)
│           ├── agents-*/          # Agent orchestration (6)
│           ├── software-*/        # Software engineering (13)
│           ├── qa-*/              # Quality & testing (13)
│           ├── dev-*/             # Developer tools (8)
│           └── ...                # Data, docs, ops, product
└── CONTRIBUTING.md
```

## Custom GPT Agents

**28 specialized agents** optimized for ChatGPT Custom GPTs (8000 character limit).

### Agent Categories

#### Education (3 agents)

- **English Tutor** - IELTS Writing Task 1 & 2 preparation with band score feedback
- **UK Tax and Legal Adviser 2025** - UK tax, legal, and regulatory guidance (2025/26 tax year)
- **Life in the UK 2025** - Citizenship test preparation with practice questions

#### Lifestyle (7 agents)

- **Fitness Buddy** - Personalized workout programming with progressive overload strategies
- **DietGPT** - Comprehensive nutrition planning with macro/micronutrient targets
- **Sleep Coach** - Sleep optimization with CBT-I techniques and environmental guidance
- **ChildBridge** - Child development expert with parenting strategies
- **Pet Whisperer** - Pet care covering nutrition, training, and species-specific needs
- **ReelRecipe** - Short-form video content strategist for TikTok, Instagram Reels, YouTube Shorts
- **CineMatch** - Movie recommendations with 66+ sources and 17 discovery commands

#### Productivity (5 agents)

- **Prompt Engineer** - Master template v3.5 with 4 deployment modes and platform-specific versions
- **Product Coach** - Product management with discovery, roadmapping, and prioritization frameworks
- **The Negotiator** - Principled negotiation with BATNA analysis and tactical empathy
- **Contract Crusher** - Legal contract analysis with risk identification and plain-English summaries
- **SMMA** - Social media marketing with campaign strategy and paid advertising tactics

#### Programming (5 agents)

- **AI Agents Builder** - OpenAI Assistants API, LangChain, CrewAI with multi-agent orchestration
- **LLM Engineer** - Fine-tuning, RAG architecture, embeddings, and production deployment
- **Data Scientist** - ML/AI with PyTorch, TensorFlow, XGBoost, and MLOps pipelines
- **PRD Business Analyst** - User stories, technical specifications, and API contracts
- **SQL and DevOps Engineer** - Database optimization, Kubernetes, Terraform, and observability

#### Research & Analysis (3 agents)

- **AI Strategist** - AI readiness assessments, use case identification, and governance frameworks
- **Startup Consultant** - Business model validation, fundraising strategy, and financial modeling
- **Strategy Consultant** - Porter's Five Forces, SWOT, PESTEL, and competitive positioning

#### Writing (2 agents)

- **AI Text Humaniser** - Transform AI content into natural writing while eliminating detection markers
- **FAANG Resume Coach** - ATS optimization, STAR stories, and behavioral interview preparation

### Three-File Agent Pattern

Every Custom GPT agent follows a consistent structure:

```text
AgentName/
├── 01_agent-name.md           # Main prompt file (<8000 chars)
├── 02_sources-agent-name.json # Curated web resources and references
└── agent-name.yaml            # Configuration (role, commands, constraints)
```

## AI Coding Agent Skills

**62 production-ready skills** for Claude Code, Codex CLI, and Gemini CLI.

### Installation

```bash
# Clone repository
git clone https://github.com/vasilyu1983/AI-Agents-public
cd AI-Agents-public

# Install to Claude Code workspace
cp -r frameworks/shared-skills/skills/ /path/to/your/repo/.claude/skills/

# Or for Codex CLI
cp -r frameworks/shared-skills/skills/ /path/to/your/repo/.codex/skills/
```

### Skill Domains

| Domain | Count | Highlights |
|--------|-------|------------|
| Software Development | 13 | Frontend, backend, C#/.NET, mobile, architecture, security, payments |
| AI/ML Engineering | 8 | LLMs, agents, RAG, MLOps, data science, prompt engineering |
| Quality & Testing | 13 | Playwright, iOS/Android, NUnit, debugging, observability, resilience |
| Developer Tools | 8 | API design, git workflow, structured logs, context engineering |
| Agents & Orchestration | 6 | Subagents, hooks, MCP, project memory, swarm orchestration |
| Data | 4 | Analytics engineering, data lake, SQL optimization, Metabase |
| Docs & Formats | 6 | PRDs, codebase docs, PDF/DOCX/XLSX/PPTX |
| Operations | 2 | DevOps platform, NUKE CI/CD |
| Product | 2 | Product management, help center |

[See full skills catalog →](./frameworks/shared-skills/skills/INDEX.md)

## Quick Start

### Using a Custom GPT Agent

1. Browse the agent catalog above to find an agent
2. Navigate to the agent folder (e.g., `custom-gpt/productivity/Prompt Engineer/`)
3. Copy content from `01_agent-name.md` (guaranteed <8000 chars)
4. Create new Custom GPT in ChatGPT
5. Paste into Instructions field
6. Upload `02_sources-*.json` as knowledge file (optional)

### Installing AI Coding Agent Skills

```bash
# Clone repository
git clone https://github.com/vasilyu1983/AI-Agents-public

# Install all skills to Claude Code
cp -r frameworks/shared-skills/skills/ /path/to/your/repo/.claude/skills/

# Verify installation
ls /path/to/your/repo/.claude/skills/
```

### Using with Claude Projects

1. Create new Claude Project
2. Add `01_agent-name.md` as project knowledge
3. Add supplemental files (`02_sources-*.json`) if available
4. Reference in custom instructions

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

### Adding a New Agent

1. Fork the repository
2. Create three files following the pattern:
   - `01_agent-name.md` (<8000 chars for Custom GPT)
   - `02_sources-agent-name.json` (curated resources)
   - `agent-name.yaml` (configuration)
3. Test on target platform
4. Submit pull request

### Adding a Skill

1. Create skill directory with `SKILL.md`
2. Add `references/`, `data/`, and `assets/` as needed
3. Follow the [Agent Skills specification](https://agentskills.io/specification)
4. Submit pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

All prompts, skills, and configurations are provided as-is for educational and commercial use.

## Resources

### Official Documentation

- [Agent Skills Specification](https://agentskills.io/specification)
- [OpenAI Custom GPTs](https://help.openai.com/en/articles/8554397-creating-a-gpt)
- [Claude Code Documentation](https://github.com/anthropics/claude-code)

### Community

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/vasilyu1983/AI-Agents-public/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/vasilyu1983/AI-Agents-public/discussions)
- **Twitter**: Follow for updates [@vasilyu](https://twitter.com/vasilyu)

---

<div align="center">

**Production-ready since 2024**

[Custom GPTs](./custom-gpt) • [Skills](./frameworks/shared-skills) • [Contributing](CONTRIBUTING.md)

</div>
