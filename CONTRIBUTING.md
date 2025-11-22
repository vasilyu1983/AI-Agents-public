# Contributing to AI Agents Library

Thank you for your interest in contributing to the AI Agents Library! This document provides guidelines for contributing new agents, skills, and improvements.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Contributing Custom GPT Agents](#contributing-custom-gpt-agents)
- [Contributing Claude Code Skills](#contributing-claude-code-skills)
- [Quality Standards](#quality-standards)
- [Submission Process](#submission-process)

## Code of Conduct

This project follows a professional code of conduct. Please be respectful, constructive, and collaborative in all interactions.

## How Can I Contribute?

### Reporting Bugs

- Use the [GitHub Issues](https://github.com/vasilyu1983/AI-Agents-public/issues) tracker
- Check if the issue already exists before creating a new one
- Provide clear reproduction steps
- Include relevant agent name, platform (ChatGPT/Claude/etc.), and error messages

### Suggesting Enhancements

- Use [GitHub Discussions](https://github.com/vasilyu1983/AI-Agents-public/discussions) for feature ideas
- Explain the use case and value proposition
- Consider if the enhancement aligns with the repository's focus

### Contributing Code

We welcome contributions of:
- New Custom GPT agents
- New Claude Code skills
- Improvements to existing agents
- Documentation enhancements
- Bug fixes

## Contributing Custom GPT Agents

### Prerequisites

Before creating a new agent:

1. **Check for duplicates**: Search existing agents to avoid overlap
2. **Validate use case**: Ensure the agent serves a clear, practical purpose
3. **Review Master Template**: Familiarize yourself with `Productivity/Prompt Engineer/02_master-template.md` structure

### Agent Requirements

Every Custom GPT agent must include:

1. **Main Prompt File** (`01_agent-name.md`)
   - Must be under 8000 characters (strict requirement)
   - Follow Master Template v3.5 structure (13 sections)
   - Use clear, concise language
   - Include real-world examples in EXEMPLARS section

2. **Configuration File** (`agent-name.yaml`)
   - Define role title and scope
   - List all slash commands with clear descriptions
   - Specify constraints (max_chars, framework, tone)
   - Match command names exactly with markdown COMMANDS section

3. **Sources File** (`02_sources-agent-name.json`)
   - Include at least 10 curated web resources
   - Group by logical categories
   - Add descriptions for each source
   - Flag frequently-updated sources with `add_as_web_search: true`

### File Structure

```text
custom-gpt/category/Agent Name/
├── 01_agent-name.md           # Main prompt (<8000 chars)
├── 02_sources-agent-name.json # Curated resources
└── agent-name.yaml            # Configuration
```

### Character Count Validation

Before submitting, validate character count:

```bash
wc -c "custom-gpt/category/Agent Name/01_agent-name.md"
# Output must be < 8000
```

### Categories

Choose the appropriate category:
- `education/` - Educational and learning agents
- `lifestyle/` - Health, fitness, entertainment, personal development
- `productivity/` - Business, productivity, professional tools
- `programming/` - Software development and technical agents
- `research-n-analysis/` - Strategic consulting and analysis
- `writing/` - Content creation and writing assistance

## Contributing Claude Code Skills

### Skill Requirements

Every Claude Code skill must include:

1. **Skill Definition** (`SKILL.md`)
   - Clear description of what the skill does
   - Activation triggers (file patterns, keywords)
   - List of resources and templates
   - Usage examples

2. **Resources Directory** (`resources/`)
   - Best practices guides
   - Pattern documentation
   - Reference materials

3. **Templates Directory** (`templates/`)
   - Code scaffolds
   - Configuration templates
   - Example implementations

4. **Data Directory** (`data/` - optional)
   - `sources.json` with curated references
   - Structured data files

### Skill Structure

```text
frameworks/claude-code-kit/initial-setup/skills/skill-name/
├── SKILL.md              # Skill definition
├── resources/            # Guides and references
│   ├── best-practices.md
│   └── patterns.md
├── templates/            # Code templates
│   ├── template-1.md
│   └── template-2.md
└── data/                 # Optional structured data
    └── sources.json
```

### Skill Categories

Choose the appropriate category:
- Software Development (frontend, backend, architecture, mobile, UI/UX)
- AI/ML Engineering (LLM, agents, data science, ML ops)
- DevOps & Platform (DevOps, database, document automation)
- Quality & Testing (code review, testing, debugging, refactoring)
- Documentation (API design, technical writing, codebase audit)

## Quality Standards

### All Contributions Must:

- [ ] **Follow existing patterns**: Match repository structure and naming conventions
- [ ] **Be tested**: Verify functionality on target platform
- [ ] **Include documentation**: Clear descriptions and usage examples
- [ ] **Pass validation**: Character limits, syntax checks, no placeholders
- [ ] **Be production-ready**: No incomplete or work-in-progress submissions
- [ ] **Cite sources**: Include references for methodologies and best practices

### Custom GPT Specific:

- [ ] Under 8000 characters (hard requirement)
- [ ] All 13 template sections included
- [ ] No `{{placeholder}}` variables remaining
- [ ] Commands match between YAML and markdown
- [ ] Tested in ChatGPT Custom GPT builder

### Claude Code Skills Specific:

- [ ] SKILL.md includes activation triggers
- [ ] Resources directory has meaningful content
- [ ] Templates are tested and functional
- [ ] Skill activates correctly in Claude Code

## Submission Process

### 1. Fork the Repository

```bash
git clone https://github.com/vasilyu1983/AI-Agents-public
cd AI-Agents-public
git checkout -b feature/your-agent-name
```

### 2. Create Your Contribution

Follow the structure and requirements above.

### 3. Validate Your Work

**For Custom GPT Agents:**
```bash
# Check character count
wc -c "custom-gpt/category/Agent Name/01_agent-name.md"

# Verify no placeholders
grep "{{.*}}" "custom-gpt/category/Agent Name/01_agent-name.md"

# Test in ChatGPT
# Copy content and create a test Custom GPT
```

**For Claude Code Skills:**
```bash
# Copy to Claude Code
cp -r frameworks/claude-code-kit/initial-setup/skills/your-skill ~/.config/claude-code/skills/

# Test activation
# Open Claude Code and verify skill activates
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add [Agent/Skill Name] - [brief description]"
```

Use clear commit messages:
- "Add Fitness Coach agent - workout programming and nutrition"
- "Add Python testing skill - pytest and coverage patterns"
- "Fix character count in Prompt Engineer agent"

### 5. Submit Pull Request

1. Push your branch to your fork
2. Create a Pull Request on GitHub
3. Fill in the PR template with:
   - Description of the agent/skill
   - Use cases and value proposition
   - Testing performed
   - Character count validation (for Custom GPT)
   - Screenshots or examples (optional)

### 6. Code Review

Maintainers will review your submission for:
- Adherence to quality standards
- Character count compliance (Custom GPT)
- Functionality and usefulness
- Documentation completeness
- No security issues or inappropriate content

You may be asked to make revisions. Please respond to feedback promptly.

## Development Setup

### Tools

Recommended tools for development:
- **Character counter**: `wc -c filename.md`
- **YAML validator**: `yamllint filename.yaml`
- **JSON validator**: `python3 -m json.tool filename.json`
- **Markdown linter**: `markdownlint-cli2`

### Testing Custom GPT Agents

1. Copy the `01_agent-name.md` content
2. Go to [ChatGPT Custom GPTs](https://chat.openai.com/gpts/editor)
3. Create a new GPT
4. Paste instructions
5. Test with various queries
6. Verify all slash commands work
7. Check output quality and adherence to constraints

### Testing Claude Code Skills

1. Copy skill to Claude Code workspace:
   ```bash
   cp -r frameworks/claude-code-kit/initial-setup/skills/your-skill \
         ~/.config/claude-code/skills/
   ```
2. Open Claude Code
3. Create test files matching activation triggers
4. Verify skill auto-activates
5. Test templates and resources are accessible
6. Check for any errors in Claude Code logs

## Style Guidelines

### Markdown

- Use `#` for H1, `##` for H2, etc.
- Add blank lines around headings and code blocks
- Use code fences with language tags: ` ```python `
- Keep line length reasonable (120 chars max)
- Use bullet points for lists of items

### YAML

- Use 2-space indentation
- Quote string values with special characters
- Use descriptive command names (e.g., `/analyze` not `/a`)
- Keep consistent formatting with existing files

### JSON

- Use 2-space indentation
- Always validate with `python3 -m json.tool`
- Include `metadata` section with title, description, last_updated
- Group sources by logical categories

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/vasilyu1983/AI-Agents-public/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/vasilyu1983/AI-Agents-public/issues)
- **Twitter**: [@vasilyu](https://twitter.com/vasilyu)

## Recognition

Contributors will be recognized in:
- Repository README (for significant contributions)
- Release notes
- Commit history

Thank you for helping make AI Agents Library better! 🚀
