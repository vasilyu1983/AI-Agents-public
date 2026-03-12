# The Complete Guide to Building Skills for Claude — Reference

Distilled from Anthropic's official 30-page PDF guide (2026). Source: `frameworks/shared-skills/The-Complete-Guide-to-Building-Skill-for-Claude.pdf`

## What Is a Skill

A folder containing SKILL.md (required) plus optional scripts/, references/, assets/ directories. Skills teach Claude *how* to do things — workflows, best practices, domain expertise. They complement MCP servers, which provide *what* Claude can access (tools, data).

**MCP = connectivity (kitchen), Skills = knowledge (recipes).**

## Progressive Disclosure (3 Levels)

| Level | Content | When Loaded | Token Cost |
|-------|---------|-------------|------------|
| 1. Discovery | name + description (YAML frontmatter) | Always in system prompt | ~50 tokens |
| 2. Activation | Full SKILL.md body | When Claude decides skill is relevant | 2-5K tokens |
| 3. Execution | references/, scripts/, assets/ | On-demand when agent reads them | Variable |

**Key**: Description budget = 2% of context window (~16K chars fallback) shared across ALL enabled skills. If total descriptions exceed budget, skills are silently excluded.

## Three Skill Categories

### 1. Document & Asset Creation
Creating consistent output (documents, presentations, code, designs). Key techniques: embedded style guides, template structures, quality checklists, uses Claude's built-in capabilities.

### 2. Workflow Automation
Multi-step processes benefiting from consistent methodology. Key techniques: step-by-step workflow with validation gates, templates, built-in review suggestions, iterative refinement loops.

### 3. MCP Enhancement
Workflow guidance layered on top of MCP tool access. Key techniques: coordinates multiple MCP calls in sequence, embeds domain expertise, provides context users would otherwise specify, error handling for common MCP issues.

## Technical Requirements

### File Structure
```
your-skill-name/
├── SKILL.md              # Required - main skill file
├── scripts/              # Optional - executable code
├── references/           # Optional - documentation
├── assets/               # Optional - templates, etc.
└── data/
    └── sources.json      # Recommended - external references
```

### Critical Rules
- `SKILL.md` must be exactly that name (case-sensitive, no variations)
- Folder name: kebab-case only, no spaces, capitals, or underscores
- No README.md inside skill folders (use SKILL.md or references/)
- No XML angle brackets (`<` `>`) in frontmatter (security: frontmatter appears in system prompt)
- No `claude` or `anthropic` in skill name (reserved)

### Frontmatter (Required Fields)
```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

- `name`: kebab-case, must match folder name
- `description`: MUST include WHAT + WHEN, under 1024 chars, no XML tags
- See [frontmatter-reference.md](frontmatter-reference.md) for all optional fields

### Description: The Most Important Part

The description is how Claude decides whether to load a skill. Structure:

```
[What it does] + [When to use it] + [Key capabilities]
```

**Good examples:**
```yaml
# Specific and actionable
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff".

# Includes trigger phrases
description: Manages Linear project workflows including sprint planning, task creation, and status tracking. Use when user mentions "sprint", "Linear tasks", "project planning", or asks to "create tickets".

# Clear value proposition
description: End-to-end customer onboarding workflow for PayFlow. Handles account creation, payment setup, and subscription management. Use when user says "onboard new customer", "set up subscription", or "create PayFlow account".
```

**Bad examples:**
```yaml
# Too vague
description: Helps with projects.

# Missing triggers
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

**For large libraries (50+ skills):** Target ~150 chars per description to stay within the 16K shared budget.

## Writing Effective Instructions

### Be Specific and Actionable
```
# Good
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)

# Bad
Validate the data before proceeding.
```

### Reference Bundled Resources Clearly
```
Before writing queries, consult `references/api-patterns.md` for:
- Rate limiting guidance
- Pagination patterns
- Error codes and handling
```

### Keep SKILL.md Focused
Move detailed documentation to `references/` and link to it. Keep SKILL.md under 5,000 words.

### Include Error Handling
```markdown
## Common Issues

### MCP Connection Failed
If you see "Connection refused":
1. Verify MCP server is running
2. Confirm API key is valid
3. Try reconnecting
```

## Success Metrics

### Quantitative
- Skill triggers on 90% of relevant queries (test with 10-20 queries)
- Completes workflow in X tool calls (compare with/without skill)
- 0 failed API calls per workflow

### Qualitative
- Users don't need to prompt Claude about next steps
- Workflows complete without user correction (test same request 3-5 times)
- Consistent results across sessions
- New users accomplish task on first try with minimal guidance

## Testing Approach

### 1. Triggering Tests
Does the skill load when it should?
- Triggers on obvious tasks
- Triggers on paraphrased requests
- Does NOT trigger on unrelated topics

### 2. Functional Tests
Does it produce correct output?
- Valid outputs generated
- API calls succeed
- Error handling works
- Edge cases covered

### 3. Performance Comparison
Is it better than no skill?
Compare same task with and without skill — count tool calls, tokens consumed, user corrections needed.

**Pro tip**: Iterate on a single task before expanding. Extract the winning approach into a skill.

## Iteration Signals

### Undertriggering (skill doesn't load when it should)
- Users manually enabling it
- Support questions about when to use it
- **Fix**: Add more detail and trigger phrases to description

### Overtriggering (skill loads for irrelevant queries)
- Skill loads for unrelated queries
- Users disabling it
- **Fix**: Add negative triggers ("Do NOT use for..."), be more specific, clarify scope

### Instructions Not Followed
- **Too verbose**: Keep concise, use bullet points
- **Buried**: Put critical instructions at top, use `## Important` / `## Critical` headers
- **Ambiguous**: Be specific (e.g., "CRITICAL: Before calling create_project, verify: - Project name is non-empty")
- **Model laziness**: Add explicit encouragement ("Take your time", "Do not skip validation steps")

### Large Context Issues
- **Optimize SKILL.md size**: Move to references/, link instead of inline, keep under 5,000 words
- **Reduce enabled skills**: Evaluate if you have 20-50+ enabled simultaneously; consider selective enablement or skill packs

## Patterns (from Early Adopters)

### Problem-First vs Tool-First
- **Problem-first**: "I need to set up a project workspace" — skill orchestrates the right tools
- **Tool-first**: "I have Notion MCP connected" — skill teaches optimal workflows and best practices

### Pattern 1: Sequential Workflow Orchestration
Multi-step processes in specific order. Key: explicit step ordering, dependencies between steps, validation at each stage, rollback instructions.

### Pattern 2: Multi-MCP Coordination
Workflows spanning multiple services. Key: clear phase separation, data passing between MCPs, validation before next phase, centralized error handling.

### Pattern 3: Iterative Refinement
Output improves with iteration. Key: explicit quality criteria, validation scripts, know when to stop.

### Pattern 4: Context-Aware Tool Selection
Same outcome, different tools depending on context. Key: clear decision criteria, fallback options, transparency about choices.

### Pattern 5: Domain-Specific Intelligence
Specialized knowledge beyond tool access. Key: domain expertise embedded in logic, compliance before action, comprehensive documentation, clear governance.

## Distribution

### Current Model (January 2026)
1. Download skill folder
2. Zip if needed
3. Upload via Claude.ai Settings > Capabilities > Skills, or place in Claude Code skills directory

### Organization-Level
Admins deploy skills workspace-wide with automatic updates and centralized management.

### Skills API
- `/v1/skills` endpoint for listing and managing
- `container.skills` parameter in Messages API
- Version control through Claude Console
- Works with Agent SDK

### Open Standard
Skills are designed as a portable, open standard across platforms (Claude.ai, Claude Code, API). Use the `compatibility` field to note platform requirements.

## Quick Checklist (Reference A)

### Before You Start
- [ ] Identified 2-3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Reviewed guide and example skills
- [ ] Planned folder structure

### During Development
- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] name field: kebab-case, no spaces, no capitals
- [ ] description includes WHAT and WHEN
- [ ] No XML tags (< >) in frontmatter
- [ ] Instructions are clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked

### Before Upload
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integration works (if applicable)
- [ ] Compressed as .zip file

### After Upload
- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions
- [ ] Update version in metadata

## Official Resources

- Best Practices Guide (Anthropic docs)
- Skills Documentation (Anthropic docs)
- API Reference (Anthropic docs)
- MCP Documentation (Anthropic docs)
- Example skills: `anthropic/skills` on GitHub
- Bug reports: `anthropic/skills/issues` on GitHub
- Community: Claude Developers Discord
- Built-in tool: `skill-creator` in Claude.ai and Claude Code
