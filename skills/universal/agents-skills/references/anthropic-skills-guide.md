# Anthropic Skills Guide

Anthropic-specific reference distilled from Anthropic's skill-building guide. Use this for Claude/Anthropic behavior only, not as the portable base spec for every runtime.

Portable-vs-runtime guidance lives in [frontmatter-reference.md](frontmatter-reference.md).

Source: Anthropic's PDF guide *The Complete Guide to Building Skills for Claude*. The PDF is not stored in this repository, so figures that come only from it (for example the trigger-rate target) are unverified. Check them against the public [Claude Code skills docs](https://code.claude.com/docs/en/skills) and the [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) page before quoting them.

## Table of Contents

- [What Is a Skill](#what-is-a-skill)
- [Progressive Disclosure (3 Levels)](#progressive-disclosure-3-levels)
- [Three Skill Categories](#three-skill-categories)
- [Technical Requirements](#technical-requirements)
- [Writing Effective Instructions](#writing-effective-instructions)
- [Success Metrics](#success-metrics)
- [Testing Approach](#testing-approach)
- [Iteration Signals](#iteration-signals)
- [Patterns (from Early Adopters)](#patterns-from-early-adopters)
- [Distribution](#distribution)
- [Quick Checklist (Reference A)](#quick-checklist-reference-a)
- [Skill Taxonomy (9 Categories)](#skill-taxonomy-9-categories)
- [Operational Patterns (from Anthropic Internal Use)](#operational-patterns-from-anthropic-internal-use)
- [Official Resources](#official-resources)

## What Is a Skill

A folder containing SKILL.md (required) plus optional scripts/, references/, assets/ directories. Skills teach Claude *how* to do things — workflows, best practices, domain expertise. They complement MCP servers, which provide *what* Claude can access (tools, data).

**MCP = connectivity (kitchen), Skills = knowledge (recipes).**

## Progressive Disclosure (3 Levels)

| Level | Content | When Loaded | Token Cost |
|-------|---------|-------------|------------|
| 1. Discovery | name + description (YAML frontmatter) | Always in the skill listing | Small, per skill; shares one listing budget |
| 2. Activation | Full SKILL.md body | When Claude decides skill is relevant | The whole body |
| 3. Execution | references/, scripts/, assets/ | On-demand when agent reads them | Variable |

**Key:** the skill *listing* (every skill's name + description shown to Claude) shares one character budget that scales with the model's context window. Each skill's own `description` + `when_to_use` text also has a per-entry cap, and overflow is truncated from the end, so put the key use case first. When the listing overflows the shared budget, Claude Code drops full descriptions starting with the least-invoked skills (down to name-only); it does not silently exclude the skill outright. The budget share and the per-entry cap are settings (`skillListingBudgetFraction`, `skillListingMaxDescChars`); read their defaults and ranges in the [settings reference](https://code.claude.com/docs/en/settings-reference), and the current per-entry cap in the [skills docs](https://code.claude.com/docs/en/skills) frontmatter table. Run `/doctor` to see the current listing cost.

For shared libraries, use Claude Code `skillOverrides` in settings to choose `on`, `name-only`, `user-invocable-only`, or `off` without editing portable frontmatter. Plugin skills are managed through `/plugin`, not `skillOverrides`. Use `/doctor` and `/context` to check actual listing cost. These controls do not configure Codex; see [skill-context-budgets.md](skill-context-budgets.md).


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

**For large libraries (50+ skills):** Anthropic's guide suggests roughly 150 characters per description; this library's own convention is the audit budget in `scripts/audit_skill_metadata.py` (a character and word ceiling that the ~150 figure sits inside), and `SKILL.md` names it as a convention, not a runtime limit. The shared listing budget scales with the model's context window, so the exact character ceiling is model-dependent — do not hardcode a fixed KB figure; verify with `/doctor` in the target runtime.

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
- Skill triggers on a pre-registered set of should-trigger prompts and stays silent on a pre-registered set of should-not-trigger prompts, written before testing. Report misses as counts, not a rate: a small set only catches gross failures (0 misses in 20 trials still leaves a miss-rate upper bound near 14% by the rule of three, 3/n), so treat a percentage target as unsupported unless the set is large enough to resolve it
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
- **Buried**: Put critical instructions at the top, under a plain heading
- **Ambiguous**: Be specific (e.g., "Before calling create_project, verify that the project name is non-empty")
- **Skipped steps**: Make the step a checkable gate ("Do not skip validation: run X and confirm Y")
- **Emphasis caution (unverified):** the source guide suggested `CRITICAL` headers and encouragement like "Take your time". Newer models may over-apply shouted rules, and later Anthropic guidance favours plain imperatives and judgment framing. Test emphasis against a plain version before keeping it

### Large Context Issues
- **Optimize SKILL.md size**: Move to references/, link instead of inline, and keep the body under the line ceiling in Anthropic's current skill best-practices doc (look it up; this library's own metadata audit flags long skills separately)
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

### Anthropic Distribution (verify in current docs)
1. Download skill folder
2. Zip if needed
3. Upload via Claude.ai Settings > Capabilities > Skills, or place in Claude Code skills directory

Treat this section as date-scoped. Verify current packaging and upload behavior in the official docs before publishing guidance.

### Organization-Level
Admins deploy skills workspace-wide with automatic updates and centralized management.

### Skills API
- `/v1/skills` endpoint for listing and managing
- `container.skills` parameter in Messages API
- Version control through Claude Console
- Works with Agent SDK

### Open Standard
Anthropic participates in the broader open skill ecosystem, but this file documents Anthropic behavior. Do not treat Anthropic-only details here as portable defaults for every runtime.

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

## Skill Taxonomy (9 Categories)

From Anthropic's internal use of hundreds of skills across teams (source: the Claude Code team article *Lessons from Building Claude Code: How We Use Skills*, linked under Official Resources; the author's full name and title are not verified here). Use this taxonomy to identify gaps in your skill portfolio and decide what to build next.

| # | Category | What It Does | Example |
|---|----------|-------------|---------|
| 1 | **Library & API Reference** | Teaches correct usage of libraries/SDKs, common gotchas, idiomatic snippets | "When using Prisma, always use `$transaction` for multi-table writes" |
| 2 | **Product Verification** | Tests and verifies code works via browser automation, programmatic assertions, video recording | Playwright snapshot after every UI change, headless state checks |
| 3 | **Data Fetching & Analysis** | Connects to data/monitoring stacks, embeds query patterns and credential handling | Query Datadog metrics, pull Metabase dashboards, parse CloudWatch logs |
| 4 | **Business Process & Team Automation** | Automates standups, ticket workflows, weekly recaps, Slack-based team rituals | Auto-create Linear tickets from conversation, generate weekly recap |
| 5 | **Code Scaffolding & Templates** | Generates framework boilerplate from natural-language requirements | "Create a Next.js API route with auth, validation, and error handling" |
| 6 | **Code Quality & Review** | Adversarial code review, style enforcement, testing practice checks | Run linting rules, flag untested branches, enforce naming conventions |
| 7 | **CI/CD & Deployment** | PR babysitting, deploy pipelines, cherry-pick workflows, release automation | Watch CI, auto-fix lint failures, manage release branches |
| 8 | **Runbooks** | Symptom → investigation → structured report for known failure modes | "API latency spike" → check DB connections → check queue depth → report |
| 9 | **Infrastructure Operations** | Orphan resource cleanup, dependency management, cost investigation | Find unused ECR images, audit stale IAM roles, check Terraform drift |

**Planning guidance**: Categories 1, 5, 6 are easiest to start with (pure knowledge, no external integrations). Categories 2, 3, 7, 9 require tool access (MCP or scripts). Category 4 is often org-specific and may not generalize to a shared skill.

## Operational Patterns (from Anthropic Internal Use)

### Description as Trigger, Not Summary

The `description` field is not a documentation summary — it is a **trigger description**. Its job is to help the model decide whether to load the skill. Write it from the model's perspective: "What would someone say that should activate this?"

Good: `"Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for 'design specs', 'component documentation', or 'design-to-code handoff'."`

Bad: `"A comprehensive tool for working with design systems and component libraries."`

### Internal Marketplace Model

Anthropic's internal skill lifecycle follows a sandbox → traction → PR pattern:

1. **Sandbox**: Author builds a skill in their personal `.claude/skills/` directory
2. **Traction**: Share informally with teammates, iterate on trigger quality and instructions
3. **PR to shared repo**: Once the skill proves useful across multiple users/sessions, promote it to the team's shared skill repository

This mirrors open-source contribution patterns. Do not over-engineer skills before they have proven value.

### Persistent Skill Data (`${CLAUDE_PLUGIN_DATA}`)

Skills shipped inside a plugin can store persistent state using the `${CLAUDE_PLUGIN_DATA}` directory. This path resolves to the plugin's data directory, which survives sessions and plugin updates. It is substituted only in plugin skills: a standalone project or user skill gets no value, so pick an explicit path (for example under the project or `~/.claude/`) there.

Use cases:

- **Append-only logs**: Audit trails, usage tracking, decision history
- **JSON state files**: Configuration, cached query results, accumulated context
- **SQLite databases**: When structured queries are needed across sessions

```text
${CLAUDE_PLUGIN_DATA}/
├── usage.log          # append-only audit log
├── config.json        # skill-specific configuration
└── cache.db           # SQLite for structured state
```

**Rule**: Treat this as a cache, not a source of truth. Skills should degrade gracefully when the data directory is empty or missing.

### Config.json Self-Bootstrapping

Skills that need configuration should include a setup flow that runs on first activation:

1. Skill checks for `${CLAUDE_PLUGIN_DATA}/config.json`
2. If missing, prompts the user for required values (API keys, project IDs, preferences)
3. Writes the config file
4. Subsequent activations read config silently

This makes skills zero-config for repeat use while remaining explicit about what they need.

### Skill Composition

Skills can reference and invoke other skills by name. Patterns:

- **Delegation**: "For database schema changes, invoke the `software-database-design` skill"
- **Sequencing**: "After scaffolding, run the `qa-testing-strategy` skill to plan test coverage"
- **Conditional**: "If the change touches API routes, also load `dev-api-design`"

**Constraint**: Keep composition shallow (1 level deep). Deep skill chains become hard to debug and inflate context.

### Skill Usage Measurement

Track which skills fire and how often with a `PreToolUse` logging hook whose matcher is `Skill`, recording the skill name from the tool input. Claude Code invokes skills through the `Skill` tool, so a `Read` matcher on `SKILL.md` undercounts or misses invocations; keep a `Read` matcher only for reference files loaded after invocation. Hook code belongs to agents-hooks: use the Skill Usage Measurement Hook in [`../../agents-hooks/references/hook-patterns.md`](../../agents-hooks/references/hook-patterns.md) and its analysis queries. The resulting log shows undertriggering, overtriggering, and unused skills. Where the runtime offers built-in skill diagnostics (see [skill-context-budgets.md](skill-context-budgets.md)), prefer them to a custom hook.

## Official Resources

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (Anthropic docs)
- [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [hooks documentation](https://code.claude.com/docs/en/hooks)
- API Reference (Anthropic docs)
- MCP Documentation (Anthropic docs)
- Example skills: `anthropic/skills` on GitHub
- Bug reports: `anthropic/skills/issues` on GitHub
- Community: Claude Developers Discord
- Built-in tool: `skill-creator` in Claude.ai and Claude Code
- [Lessons from Building Claude Code: How We Use Skills](https://x.com/trq212/article/2033949937936085378) — 9 skill categories and operational patterns from Anthropic internal use
