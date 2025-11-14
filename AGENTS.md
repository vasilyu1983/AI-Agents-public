# Repository Guidelines

See also: `README.md` (entry point), `CLAUDE.md` (Claude-specific notes), `GEMINI.md` (Gemini-specific notes), and [docs/agents framework/README.md](docs/agents framework/README.md) (AI Agent Communication Protocols).

**AI Agent Protocols** (NEW):
- [docs/agents framework/mcp/](docs/agents framework/mcp/) - Model Context Protocol (connect agents to data/tools)
- [docs/agents framework/a2a/](docs/agents framework/a2a/) - Agent-to-Agent Protocol (enable agent collaboration)


## CRITICAL PLATFORM CONSTRAINTS

**Custom GPT**: 8000 character hard limit (OpenAI platform restriction). Non-negotiable for Custom GPT deployment. Use `wc -c` to check character count (not word count). Target 7500-7900 characters maximum to maintain safety margin. For additional context, use knowledge files or attachments—never exceed 8000 characters in the instruction field.

**Claude Projects**: 200k token context window (soft limit). While significantly higher than Custom GPT, optimization still improves performance. Leverage Claude-specific features: artifacts for long outputs, <thinking> tags for reasoning, multi-file knowledge base references.

**Platform-Specific Versions**: When platform differences are significant (features, limits, capabilities), maintain separate optimized versions with naming pattern `01_agent-name-PlatformName.md`. Example: Prompt Engineer has both `01_prompt-engineer-CustomGPT.md` (7,918 chars, ChatGPT optimized) and `01_prompt-engineer-claude.md` (11,165 chars, Claude Projects optimized).

**Multi-file splitting strategy**: When initial prompt content exceeds 8000 characters even after optimization, split it into multiple numbered files rather than oversimplifying the concept. Example: Prompt Engineer uses 6 files with platform-specific versions (`01_prompt-engineer-CustomGPT.md` at 7,918 chars, `01_prompt-engineer-claude.md` at 11,165 chars for Claude's extended context), plus `04_guides-and-modes.json` at 22,418 characters for structured data. The structure follows fileformat_guide.md principles: JSON for data recall, MD for reasoning. Each file is self-contained while cross-referencing related files when necessary.

## Project Structure & Module Organization
AI Agents groups domain-specific assistants by discipline. Domain folders such as `Education/`, `Lifestyle/`, `Productivity/`, `Programming/`, `Research & Analysis/`, and `Writing/` each contain agent directories with:

**Standard Agent Files** (Three-File Deliverable Pattern, established 2025-10-28):
1. `01_agent-name.md` - Main prompt file (always numbered 01)
2. `02_sources-agent-name.json` - **NEW STANDARD**: Curated web resources for agent's domain with categorized links, descriptions, and `add_as_web_search` flags
3. `agent-name.yaml` - Configuration with role parameters, commands, and constraints

**Optional Files**:
- `03_supplemental.md` - Additional documentation or guides
- `0X_data.json` - Structured data for compact lookups, mode definitions, behavioral maps
- `sources/` - Git-ignored research materials
- `archive/` - Git-ignored version history

**JSON Sources Structure**:
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

**Existing Examples**:
- `Programming/AI Agents/02_sources-ai-agents.json` - Agent frameworks
- `Programming/LLM/02_sources-llm-engineer.json` - LLM engineering
- `Programming/DS/02_sources-data-scientist.json` - Data science

Client-specific work lives in `[altery]/`; limit edits there to scoped requests. Shared templates and reference docs sit in `Productivity/Prompt Engineer/02_master-template.md`, `CLAUDE.md`, and `docs/` directory. Use `docs/testing/customgpt-knowledge-base-audit.md` or `docs/testing/prompt-engineer-audit.md` when validating finished agents.

**File Format Strategy**: See [docs/formatting/README.md](docs/formatting/README.md) for format selection and [docs/formatting/formatting-standards.md](docs/formatting/formatting-standards.md) for TOON and formatting standards. Rule of thumb: think → `.md`, recall → `.json`, detect → `.txt`; use TOON for LLM-internal instructions, schemas, and examples as defined in `formatting-standards.md`.

**CRITICAL**: The 8000 character limit applies ONLY to `.md` instruction files. Supporting files (`.json`, `.txt`) have NO character limits.

## YAML Alignment Rules (Prompt ⇄ YAML)
When you update any `01_agent-name.md` prompt, you must keep its sibling `agent-name.yaml` in sync. Treat Markdown as the source of truth; update YAML to match.

Required checks before handoff:
- Commands parity: every slash command listed in `## COMMANDS` of the md must appear in `commands:` of the yaml with the same name; remove extras not in md.
- Hard cap: set `max_chars` in yaml to match the md “Hard cap” under OUTPUT CONTRACT.
- Platform notes: keep `framework`, `tone`, `answer_shape` consistent with the md.
- Links: if the md mandates specific link lines (e.g., CineMatch IMDb/Kinopoisk), reflect that in `answer_shape`.

Helpful commands:
- List md/yaml pairs: `find . -type f -name '01_*.md' -not -path '*/archive/*'`
- Diff commands: `awk '/^## COMMANDS/{f=1;next}/^## /{f=0}f' Agent/01_x.md | rg -o '/[A-Za-z0-9:_-]+' | sort -u` vs `rg -N 'name:\s*/[A-Za-z0-9:_-]+' Agent/x.yaml -o | sed 's/.*name:\s*//' | sort -u`
- Check max cap: `awk '/^## OUTPUT CONTRACT/{f=1} f&&/Hard cap:/{print;f=0}' Agent/01_x.md`

Policy: Do not reduce md content to fit yaml; instead, update yaml to align. If platform versions diverge (CustomGPT/Claude), keep separate md files and keep each yaml aligned with the md it couples to.

## Archive Directories (Skip By Default)
To conserve tokens and speed up repository operations, do not read, index, or traverse any archive directories unless the user explicitly requests a specific file.

- Exclude globs: `**/archive/**`, `**/Archive/**`
- Notable paths to skip: `docs/archive/`, `docs/customisations/archive/`, `docs/profile/archive/`, all agent `sources/archive/` folders
- Behavior: skip by default in listings, searches, and bulk scans; only read when the user provides an explicit file path
- Rationale: archive folders hold large, low-signal materials (videos, PDFs, historical notes) that exhaust context tokens

Recommended search patterns:
- `rg <pattern> -g '!**/archive/**' -g '!**/Archive/**'`
- `find . -type f ! -path '*/archive/*' ! -path '*/Archive/*'`


## Build, Test, and Development Commands
There is no compile step; focus on fast text diffing. Common helpers:
- `rg 'IDENTITY' AgentFolder -n` confirms required template sections.
- `rg "{{[^}]+}}" AgentFolder/agent_name.md` surfaces un-resolved variables.
- `rg --files -g '*.yaml' Programming/` lists configs you may need to update together.
- `rg "^---$" -g "*.md" Productivity/` checks for unnecessary horizontal dividers (should return empty for optimized templates).
- `rg "v3\." -g "*.md"` validates version consistency across documentation.
- `wc -w "Productivity/Prompt Engineer/02_master-template.md"` tracks token efficiency (target: <1300 words post-optimization).
- When a shell command fails with `failed in sandbox`, rerun it through the permission request tool using `with_escalated_permissions` and include a one-sentence justification before retrying the command.

## Coding Style & Naming Conventions
Keep Markdown headings capitalized and aligned with the master template's section order. YAML files use two-space indentation, lowercase keys, and quoted strings only when necessary. File and directory names stay in PascalCase or snake_case as already established; do not rename without cause. Maintain safety, precedence, and workflow sections verbatim unless the task explicitly calls for changes.

**Text formatting standards**:
- No emojis or decorative Unicode symbols in documentation or prompts
- Use plain text labels for clarity: "REQUIRED" instead of "✅", "AVOID" instead of "❌"
- Clean bullet points without checkmarks or special characters
- Professional, text-only appearance for better cross-platform compatibility and character efficiency

## Testing Guidelines
Before handing work off, walk the checklist in `docs/testing/customgpt-knowledge-base-audit.md` or `docs/testing/prompt-engineer-audit.md`, verify every template variable in the YAML is referenced in the Markdown, and rerun the `rg "{{[^}]+}}"` scan until it is clean. When editing automation-oriented agents, document any required external credentials in the YAML `commands` section and ensure placeholders remain descriptive.
Cross-check the slash commands advertised in the Markdown against the YAML `commands` list so they match verbatim; mismatches surface as missing-command errors inside the CLI.

**Template optimization checklist** (for Master Template or derivative prompts):
- **Character count ≤8000** (hard GPT platform limit) — verify with `wc -c agent_name.md`
- No `---` horizontal dividers between sections (use blank lines)
- No emojis or special Unicode symbols (e.g., ✅ 🟡 ❌ 📋 ⚙️ 💡 ✓ ⏸️ 1️⃣ 2️⃣ 3️⃣ 🔹)
- Use plain text labels: "REQUIRED", "CONDITIONAL", "OMIT", "AVOID", "BEST", "INCLUDE"
- VARS section has consolidated defaults line (not inline comments)
- QA checklist is inline (not multi-line)
- Verbose phrases tightened ("Reference {{context}} when provided" → "Use {{context}} as background only")
- No placeholders in outputs (e.g., "ISBN: [TO BE CONFIRMED]", "TBD", hedged values)
- All 13 standard sections present: VARS, IDENTITY, CONTEXT, CONSTRAINTS, PRECEDENCE & SAFETY, OUTPUT CONTRACT, FRAMEWORKS, WORKFLOW, ERROR RECOVERY, TOOLS & UI, MEMORY, COMMANDS, EXEMPLARS
- Word count <1300 for production templates (approximately 7500-7900 characters)

## Commit & Pull Request Guidelines
Follow the repository style of short, imperative commit subjects (for example, `Add lifecycle QA checklist`). Group related edits into a single commit with focused scope. Pull requests should state the affected agent(s), link any related briefs or issues, call out safety-sensitive modifications, and include screenshots or diff notes when adjusting long prompts.

**Documentation commits**: When updating `README.md`, `CLAUDE.md`, or `AGENTS.md`, commit separately from implementation:
```bash
# After template changes
git add Productivity/Prompt\ Engineer/master\ template.md
git commit -m "optimize: consolidate VARS defaults, inline QA checklist (10-13% token reduction)"

# Then update docs
git add README.md CLAUDE.md AGENTS.md
git commit -m "docs: update for v3.5 template optimizations (2024-10-12)"
```

When modifying a prompt file, include yaml sync in the same commit or follow-up immediately:
```bash
# Example after editing Lifestyle/CineMatch/01_cinematch.md
git add Lifestyle/CineMatch/cinematch.yaml Lifestyle/CineMatch/01_cinematch.md
git commit -m "cinematch: sync yaml commands + answer_shape with prompt"
```

**DO NOT create summary/report files**:
- **NEVER proactively create documentation files** (OPTIMIZATION_NOTES.md, CHANGELOG.md, MIGRATION.md, REORGANIZATION_SUMMARY.md, SUMMARY.md, etc.) unless explicitly requested by the user
- **NEVER create summary/report files** after completing tasks - update existing documentation instead
- **NEVER create new README or guide files** in existing documented directories - update existing files instead
- After completing work, do NOT create summary documents - just confirm completion
- Instead of creating new docs, update existing files (README.md "Recent Improvements" section, CLAUDE.md if architecture changed, relevant agent files directly)

## Security & Configuration Tips
Do not paste client data or secrets into versioned files. Preserve OAuth scopes, safety rails, and guardrail language verbatim unless provided with a revised policy. When adding integrations, note required environment variables and storage expectations in the YAML so downstream users can configure agents deterministically.
