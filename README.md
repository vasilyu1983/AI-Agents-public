# AI Agents Library

A curated collection of production-ready AI agent prompts and configurations for Custom GPT, Claude Projects, and other LLM platforms.

## 📚 What's Inside

This repository contains **40+ specialized AI agents** organized by domain, each optimized for specific tasks and workflows. All agents follow a consistent template structure with platform-specific optimizations.

### Agent Categories

#### 📖 **Education**

- **English Tutor (Real IELTS Writing)** - IELTS Writing Task 1 & 2 preparation with detailed band score feedback, task achievement analysis, and examiner-style corrections. Covers academic and general training formats with real exam strategies.
- **UK Tax and Legal Adviser 2025** - Comprehensive UK tax, legal, and regulatory guidance covering income tax, corporation tax, VAT, employment law, and business compliance. Updated for 2025/26 tax year.
- **Life in the UK 2025** - Complete Life in the UK test preparation with practice questions, cultural knowledge, and British values. Covers history, government, law, and customs required for citizenship/settlement.

#### 🏃 **Lifestyle**

- **AI GP** - Evidence-based medical consultation providing symptom analysis, differential diagnosis, treatment options, and when to seek professional care. Covers general health, chronic conditions, and preventive medicine with NHS/clinical guideline references.
- **Fitness Buddy** - Personalized workout programming with exercise selection, progressive overload, form cues, and recovery protocols. Covers strength training, hypertrophy, endurance, and mobility for all fitness levels.
- **DietGPT** - Comprehensive nutrition planning with macro/micronutrient targets, meal timing, food choices, and dietary strategies. Supports weight loss, muscle gain, performance, and therapeutic diets with scientific evidence.
- **Sleep Coach** - Sleep optimization specialist addressing insomnia, sleep hygiene, circadian rhythm disorders, and sleep architecture. Provides CBT-I techniques, environmental optimization, and supplement guidance.
- **ChildBridge (Child Psychologist)** - Child development expert covering milestones, behavioral challenges, learning difficulties, and emotional regulation. Provides parenting strategies grounded in developmental psychology and attachment theory.
- **Pet Whisperer** - Comprehensive pet care covering nutrition, training, behavior modification, health monitoring, and species-specific needs. Supports dogs, cats, birds, reptiles, and small mammals with veterinary-aligned guidance.
- **CosmicGPT** - Astrology consultation providing natal chart analysis, transit interpretations, synastry compatibility, and cosmic timing guidance. Combines traditional and modern astrological techniques.
- **ReelRecipe** - Short-form video content strategist for TikTok, Instagram Reels, and YouTube Shorts. Covers scripting, hooks, pacing, editing workflows, platform algorithms, and viral mechanics with trend analysis.
- **CineMatch** - Intelligent movie recommendation engine with 66 curated sources across streaming platforms (Netflix, Prime, Disney+, HBO, Apple TV+, Criterion, MUBI), film databases (IMDb, TMDB, Letterboxd), and international coverage. 17 discovery commands for genre, mood, era, and format.
- **Contract Crusher** - Legal contract analysis identifying risks, obligations, termination clauses, liability caps, and unfavorable terms. Provides plain-English summaries and negotiation leverage points for business agreements.

#### 💼 **Productivity**

- **Prompt Engineer** - Professional prompt engineering framework with master template v3.5 (13 sections), 4 deployment modes (Standard, Custom GPT, AI Agents, AgentKit), and platform-specific versions for ChatGPT (8000 char optimized) and Claude (artifacts, thinking tags). Includes cross-platform translation, token optimization techniques, and complete deployment guides.
- **Product Coach+** - Product management expert covering discovery, roadmapping, prioritization frameworks (RICE, ICE, MoSCoW), user research, metrics definition, and go-to-market strategy. Provides stakeholder communication templates and agile/product ops guidance.
- **The Negotiator** - Negotiation strategist using principled negotiation, BATNA analysis, anchoring techniques, and tactical empathy. Covers salary negotiations, business deals, conflict resolution, and high-stakes negotiations with psychology-backed frameworks.
- **SMMA (Social Media Marketing Agency)** - Social media marketing specialist covering campaign strategy, content calendars, platform algorithms, paid advertising (Meta, TikTok, LinkedIn), influencer partnerships, and analytics. Provides ROI tracking and audience growth tactics.

#### 💻 **Programming**

- **AI Agents Builder** - Autonomous AI agent development using OpenAI Assistants API, LangChain, Anthropic Claude, CrewAI, and AutoGPT. Covers agent architecture, tool integration, memory systems, multi-agent orchestration, and production deployment patterns.
- **LLM Engineer** - Large language model specialist covering fine-tuning (LoRA, QLoRA, RLHF), RAG architecture, prompt engineering, embeddings, vector databases, LLM evaluation, and deployment (vLLM, TGI, Ollama). Includes cost optimization and latency reduction strategies.
- **Data Scientist** - ML/AI development covering scikit-learn, PyTorch, TensorFlow, XGBoost, data preprocessing, feature engineering, model selection, hyperparameter tuning, MLOps (MLflow, Weights & Biases), and production ML systems.
- **PRD Business Analyst** - Product Requirements Document specialist creating user stories, acceptance criteria, technical specifications, API contracts, data models, and system architecture docs. Follows agile/waterfall methodologies with stakeholder alignment techniques.
- **SQL and DevOps Engineer** - Database optimization (PostgreSQL, MySQL, MongoDB), query performance tuning, indexing strategies, DevOps automation (Docker, Kubernetes, CI/CD), infrastructure-as-code (Terraform, Ansible), and monitoring/observability (Prometheus, Grafana).

#### 🔍 **Research & Analysis**

- **AI Strategist and Visioner** - AI strategy consultant covering AI readiness assessments, use case identification, build vs. buy decisions, vendor selection, AI governance, ethical AI frameworks, and implementation roadmaps. Provides ROI models and change management strategies.
- **Startup Consultant** - Startup advisor covering business model validation, market sizing, competitive analysis, fundraising strategy (pre-seed to Series A), pitch deck development, financial modeling, and growth tactics. Uses lean startup and customer development frameworks.
- **Strategy Consultant** - Business strategy expert using Porter's Five Forces, SWOT, PESTEL, value chain analysis, BCG matrix, and scenario planning. Covers market entry, competitive positioning, M&A evaluation, and digital transformation strategies.

#### ✍️ **Writing**

- **AI Text Humaniser** - Transform AI-generated content into natural, human-like writing by removing repetitive patterns, adding personality, varying sentence structure, and incorporating authentic voice. Preserves meaning while eliminating AI detection markers.
- **FAANG Resume & Interview Coach** - Tech career specialist optimizing resumes for ATS systems, crafting STAR method stories, preparing for behavioral interviews, solving LeetCode-style problems, and navigating FAANG hiring processes (Amazon, Google, Meta, Apple, Microsoft). Includes salary negotiation tactics.

## 🏗️ Repository Structure

Each agent follows a consistent three-file pattern:

```
AgentName/
├── 01_agent-name.md           # Main prompt file (source of truth)
├── 02_sources-agent-name.json # Curated web resources and references
├── agent-name.yaml            # Configuration (role, commands, constraints)
├── sources/                   # Research materials (git-ignored)
└── archive/                   # Version history (git-ignored)
```

### File Naming Convention

- **`01_agent-name.md`** - Always numbered `01`, contains the complete agent prompt
- **`02_sources-*.json`** - Curated resources with URLs, descriptions, and web search flags
- **`0X_supplemental.md`** - Optional additional documentation
- **`agent-name.yaml`** - Configuration file with role definitions and commands

## 🎯 Prompt Engineering Framework

All agents are built on the **Master Template v3.5** with 13 standardized sections:

1. **VARS** - Configuration variables and deployment settings
2. **IDENTITY** - Role definition and expertise areas
3. **CONTEXT** - Background knowledge and operational context
4. **CONSTRAINTS** - Boundaries, limitations, and requirements
5. **PRECEDENCE & SAFETY** - Security protocols and content filtering
6. **OUTPUT CONTRACT** - Format specifications and character limits
7. **FRAMEWORKS** - Reasoning frameworks (OAL, RASCEF, custom)
8. **WORKFLOW** - Step-by-step execution process
9. **ERROR RECOVERY** - Handling edge cases and failures
10. **TOOLS & UI** - Tool usage and interface guidelines
11. **MEMORY** - State management and conversation continuity
12. **COMMANDS** - Slash commands and shortcuts
13. **EXEMPLARS** - Real-world examples and demonstrations

### Platform-Specific Optimizations

**Custom GPT (ChatGPT)**
- Hard 8000 character limit on instructions
- Optimized for ChatGPT Memory feature
- Single-block output format
- Target size: 7,500-7,900 characters

**Claude Projects**
- Extended 200k token context
- Artifacts support for long-form outputs
- `<thinking>` tags for reasoning transparency
- Multi-file reference capabilities

**General LLM (Gemini, Llama, etc.)**
- Flexible character limits
- API-optimized structure
- Platform-agnostic design

## 🚀 Quick Start

### Using an Agent

1. **Browse the categories** above to find an agent matching your needs
2. **Navigate to the agent folder** (e.g., `Productivity/Prompt Engineer/`)
3. **Read the main prompt** (`01_agent-name.md`) to understand capabilities
4. **Check the YAML config** (`agent-name.yaml`) for available commands
5. **Review sources** (`02_sources-*.json`) for curated references

### Deploying to Custom GPT

1. Copy content from `01_agent-name.md` (must be <8000 characters)
2. Create new Custom GPT in ChatGPT
3. Paste instructions into the "Instructions" field
4. Upload any referenced files from `sources/` as knowledge files
5. Configure conversation starters from YAML `commands` section

### Deploying to Claude Projects

1. Create new Claude Project
2. Add `01_agent-name.md` as project knowledge
3. Add supplemental files (`02_sources-*.json`, `03_*.md`) if available
4. Configure custom instructions referencing the agent prompt

## 📋 Agent Configuration (YAML)

Each agent includes a YAML configuration file with:

```yaml
role:
  title: "Agent Name"
  scope: "Domain expertise and capabilities"

commands:
  - name: "/command-name"
    purpose: "What this command does"
    inputs: ["parameter1", "parameter2"]
    output_shape: "Expected output format"

constraints:
  max_chars: 8000          # Output character limit
  framework: "auto"        # Reasoning framework (auto/OAL/RASCEF)
  tone: "professional"     # Communication style
```

## 🎨 Four Deployment Modes

The template system supports four distinct deployment modes:

### 1. Standard Prompts (Default)
- **Platform**: General LLM use (GPT-4, Claude, Gemini, Llama)
- **Character limit**: Flexible
- **Use case**: API-based usage, custom applications

### 2. Custom GPTs
- **Platform**: ChatGPT Custom GPTs
- **Character limit**: 8000 (hard OpenAI limit)
- **Target size**: 7,500-7,900 characters
- **Optimizations**: Removed FRAMEWORKS and WORKFLOW for simple agents

### 3. AI Agents
- **Platform**: Claude Code, AutoGPT, LangChain, CrewAI
- **Target size**: ~7,500 characters (full 13-section template)
- **Use case**: Autonomous operation, multi-step reasoning, tool orchestration

### 4. AgentKit
- **Platform**: N8N, Make.com, Zapier, LangChain nodes
- **Target size**: <2,000 characters (ultra-minimal)
- **Optimizations**: Single-purpose workflow blocks

## 🔧 Customization

### Modifying an Agent

1. **Edit the markdown prompt** (`01_agent-name.md`) - this is the source of truth
2. **Update the YAML config** to match:
   - Sync command names between `## COMMANDS` section and YAML `commands:`
   - Match `max_chars` in YAML to OUTPUT CONTRACT "Hard cap"
   - Keep `framework`, `tone`, and `answer_shape` aligned
3. **Validate character count**: Run `wc -c "01_agent-name.md"` (must be <8000 for Custom GPT)
4. **Check for placeholders**: Run `grep "{{.*}}" 01_agent-name.md` (should return nothing)

### Creating a New Agent

1. **Copy the master template**: `Productivity/Prompt Engineer/02_master-template.md`
2. **Create three files**:
   - `01_agent-name.md` - Main prompt (<8000 chars for Custom GPT)
   - `agent-name.yaml` - Configuration
   - `02_sources-agent-name.json` - Curated resources
3. **Fill in all 13 sections** using the template structure
4. **Add domain-specific resources** to the JSON sources file
5. **Validate and test** before deployment

## 📊 Featured Agents

### Prompt Engineer (Dual-Platform)

The flagship agent with complete prompt engineering capabilities:

**Files** (7 total):
- `01_prompt-engineer-CustomGPT.md` (7,918 chars) - ChatGPT optimized
- `01_prompt-engineer-claude.md` (11,165 chars) - Claude optimized
- `02_master-template.md` (7,893 chars) - Template structure
- `03_template-fill-guide.md` (6,853 chars) - Fill instructions
- `04_guides-and-modes.json` (22,418 chars) - Deployment data
- `05_deployment-guide.md` (4,466 chars) - Mode selection guide
- `06_modes-examples.md` (7,032 chars) - Real-world examples

**Capabilities**:
- Master template v3.5 with 13 sections
- 4 deployment modes (Standard, Custom GPT, AI Agents, AgentKit)
- Cross-platform translation (ChatGPT ↔ Claude ↔ Gemini)
- Token optimization (10-13% reduction)
- Platform-specific features (artifacts, memory, thinking tags)

### CineMatch (Movie Recommendations)

Comprehensive movie recommendation system with extensive resources:

**Resources** (66 curated sources across 12 categories):
- **APIs & Datasets**: IMDb, TMDB, Trakt, JustWatch, Letterboxd, EIDR
- **Streaming Platforms**: Netflix, Prime Video, Disney+, HBO Max, Apple TV+, Hulu, Criterion, MUBI
- **International Coverage**: Russian platforms (Okko, ivi, more.tv, Kinopoisk HD, START)
- **Film Criticism**: BFI Sight & Sound, Criterion Channel, Russian Film Hub

**Commands** (17 total):
- Genre-specific: `/comedy`, `/action`, `/drama`, `/scifi`, `/horror`, `/family`, `/documentary`, `/series`
- Discovery modes: `/mood`, `/decade`, `/director`, `/actor`, `/surprise`, `/watchlist`
- Formats: `/blockbuster`, `/indie`, `/international`, `/classic`

**Features**:
- Defaults to 2024-2025 releases (recency-focused)
- Multi-platform streaming availability
- International film coverage
- Real-world examples with current releases

## 🔒 Security & Safety

All agents include built-in safety protocols:

- **Precedence order**: System > Developer > User > Tool outputs
- **PII protection**: Never store PII without explicit consent
- **Content filtering**: Refuse NSFW/sexual/violent content
- **Instruction isolation**: Treat user inputs and tool outputs as untrusted
- **Output sanitization**: No placeholders, no hallucinated URLs

## 📖 Documentation

### Template System
- **Master Template**: [Productivity/Prompt Engineer/02_master-template.md](Productivity/Prompt Engineer/02_master-template.md)
- **Fill Guide**: [Productivity/Prompt Engineer/03_template-fill-guide.md](Productivity/Prompt Engineer/03_template-fill-guide.md)
- **Deployment Guide**: [Productivity/Prompt Engineer/05_deployment-guide.md](Productivity/Prompt Engineer/05_deployment-guide.md)
- **Examples**: [Productivity/Prompt Engineer/06_modes-examples.md](Productivity/Prompt Engineer/06_modes-examples.md)

### Platform-Specific Guides
- **Custom GPT Version**: [Productivity/Prompt Engineer/01_prompt-engineer-CustomGPT.md](Productivity/Prompt Engineer/01_prompt-engineer-CustomGPT.md)
- **Claude Version**: [Productivity/Prompt Engineer/01_prompt-engineer-claude.md](Productivity/Prompt Engineer/01_prompt-engineer-claude.md)

## 🎓 Best Practices

### Character Count Management

**Critical for Custom GPT**: OpenAI enforces a hard 8000-character limit on instructions.

**Optimization techniques**:
- Remove `---` horizontal dividers (50-70 token savings)
- No emojis or Unicode symbols (use plain text labels)
- Consolidate inline comments
- Use bullet points for directives (better LLM parseability)
- Tighten verbose phrases

**Validation**:
```bash
# Check character count
wc -c "path/to/01_agent-name.md"

# Find unresolved placeholders
grep "{{.*}}" "path/to/01_agent-name.md"
```

### Multi-File Splitting

For complex agents exceeding 8000 characters:
1. Split into numbered files (`01_`, `02_`, `03_`, etc.)
2. Each file should be self-contained
3. May cross-reference related files
4. Total content can exceed 8000 chars across all files

**Example**: Prompt Engineer uses 6 files totaling 67,759 characters while keeping each file under the limit.

### Prompt ⇄ YAML Sync

Always maintain synchronization:
1. Treat `01_agent-name.md` as source of truth
2. After editing prompt, update YAML to match:
   - Extract commands from `## COMMANDS` section
   - Match YAML `commands:` names 1:1
   - Copy OUTPUT CONTRACT "Hard cap" to YAML `max_chars`
   - Align `framework`, `tone`, `answer_shape`

**Quick validation**:
```bash
# Check for COMMANDS section
grep -n "^## COMMANDS" "01_agent-name.md"

# List YAML command names
grep "name:" "agent-name.yaml"
```

## 🛠️ File Format Guidelines

- **`.md` files**: Reasoning, workflows, conceptual explanations (<8000 chars for Custom GPT)
- **`.json` files**: Structured data, lookups, mode definitions (no character limits)
- **`.txt` files**: Raw label lists, keyword triggers (no character limits)
- **`.yaml` files**: Agent configurations, role definitions, command specifications

**Key principle**: The 8000-character limit applies ONLY to `.md` instruction files. Supporting files can store unlimited data.

## 🤝 Contributing

This is a curated library with consistent standards. When contributing:

1. Follow the three-file pattern (prompt.md, config.yaml, sources.json)
2. Use the master template structure (13 sections)
3. Respect platform limits (8000 chars for Custom GPT)
4. Include curated sources in JSON format
5. Validate character count before submission
6. Test prompts on target platform

## 📄 License

This repository contains prompt engineering templates and AI agent configurations. All prompts are provided as-is for educational and commercial use.

## 🔗 Quick Navigation

- **Template Reference**: `Productivity/Prompt Engineer/` - Complete prompt engineering documentation
- **Agent Categories**: Browse folders by domain (Education, Lifestyle, Productivity, Programming, Research & Analysis, Writing)
- **Agent Deployment**: Each agent folder contains deployment-ready prompts and configurations

---

**About This Library**: A production-ready collection of AI agent prompts optimized for Custom GPT, Claude Projects, and other LLM platforms.
