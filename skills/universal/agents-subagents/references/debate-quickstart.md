---
description: Debate setup across Claude Code, Codex, Agent Teams; 10 debate methods and team/situation mapping.
last_verified: 2026-09-16
status: stable
---

# Debate Pattern Quickstart

Step-by-step setup for running multi-persona debates in Claude Code, Codex, and Claude Code Agent Teams.

Debate is one mode of the broader `agents-subagents` system. Use it when:
- installed global agents already give you strong domain perspectives
- a repo-local agent should challenge project-specific decisions
- a shared team has `debate.enabled: true` and should argue before synthesis
- the parent thread needs a decision log rather than immediate implementation

Default rule: debate is not the starting posture. Run it when the decision is high-blast-radius, evidence is conflicting, or the team is likely to disagree for real. For low-stakes or clearly owned work, keep orchestration in the parent thread or use a single bounded subagent.

## Table of Contents

- [When NOT to Debate](#when-not-to-debate)
- [Adaptive Stopping (Non-Numeric Debates)](#adaptive-stopping-non-numeric-debates)
- [Prerequisites](#prerequisites)
- [Option A: Claude Code Subagents (works today)](#option-a-claude-code-subagents-works-today)
- [Option B: Codex Custom Agents](#option-b-codex-custom-agents)
- [Option C: Claude Code Agent Teams (experimental)](#option-c-claude-code-agent-teams-experimental)
- [Option D: MCP Debate Server (protocol-enforced)](#option-d-mcp-debate-server-protocol-enforced)
- [Example Prompts](#example-prompts)
- [What To Expect](#what-to-expect)
- [Customizing Personas](#customizing-personas)
- [Troubleshooting](#troubleshooting)
- [3-Of-5 Pattern For Large Debate Teams](#3-of-5-pattern-for-large-debate-teams)
- [Layering Methods And Masks On Top Of Role Debate](#layering-methods-and-masks-on-top-of-role-debate)
- [Framework → Team, Workflow Mode, Situation, Or Scenario Mapping](#framework--team-workflow-mode-situation-or-scenario-mapping)
- [Method Reference Files](#method-reference-files)

## When NOT to Debate

Debate is **not** universally beneficial. Recent research (2025–26) shows multi-agent debate sometimes performs **worse** than a single strong agent. Skip debate or restructure the team when any of these anti-triggers fire:

| Anti-Trigger | Why debate fails | Source |
|---|---|---|
| All members are fine-tunes of the same base model | Correlated biases produce convergent-but-wrong consensus that looks reliable | Wynn, Satija & Hadfield, *Talk Isn't Always Cheap* ([arXiv:2509.05396](https://arxiv.org/abs/2509.05396)) [unverified as of 2026-09-16: the abstract documents capability-asymmetry and sycophancy failures, not same-base-model correlated bias — check the paper before citing it for this row] |
| Mixing weak + strong agents on the same question | Weak agent's reasoning persuades the strong agent off the correct answer (sycophancy hazard) | *When collaboration fails: persuasion-driven adversarial influence in multi-agent large language model debate*, Scientific Reports (2026), [s41598-026-42705-7](https://www.nature.com/articles/s41598-026-42705-7) — reports 10–40% accuracy loss and >30% more consensus on wrong answers from a single adversarial persuader; verified 2026-09-16 |
| Sycophancy bias is high in the base model and not patched | Agents prioritize agreement over accuracy → false consensus | Cemri et al. MAST 2025 §FC2.5 |
| Question is **factual with a verifiable answer** (math, lookup, deterministic computation) | Single agent + verifier outperforms debate; debate adds noise. **Use Self-MoA instead** (single strong model × N samples + aggregator) — beats heterogeneous debate on verifiable tasks. See [`foundations-team-theory: 02-adversarial-debate.md` §"Self-MoA Conditional"](../../foundations-team-theory/assets/templates/team-theory/02-adversarial-debate.md#self-moa-conditional--when-heterogeneity-isnt-required) | Du et al. 2023; Self-MoA arxiv 2502.00674 |
| Stakes are low and the cost of being wrong is bounded | Coordination cost > expected quality gain | GitHub Blog, [*Multi-agent workflows often fail. Here's how to engineer ones that don't.*](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/) (2026-02-24) |
| You can't afford 3+ rounds of token spend | Debate is expensive; one strong agent + reflection is usually 60–80% of the value at 20% of the cost | Anthropic, [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) (general guidance that added agent complexity must earn its cost) [unverified as of 2026-09-16: the "85% of quality lift in the first 2 iterations" figure does not appear on that page — treat the 60–80%/20% numbers as an operator rule of thumb, not a published measurement] |

**If you debate anyway under these conditions**, add explicit safeguards:
- Force **heterogeneous models** across members (different families, not just different prompts).
- Add a **devil's advocate seat** with non-hedging mandate to break sycophancy spirals.
- Require **evidence citations per claim** (mechanism #14, credibility scoring) so peer pressure can't substitute for evidence.
- Run a **single-agent baseline** in parallel; if debate output disagrees with baseline, treat as a flag, not a win.

For the structured failure-mode taxonomy, see [`mast-failure-taxonomy.md`](mast-failure-taxonomy.md).

## Adaptive Stopping (Non-Numeric Debates)

Delphi (mechanism: numeric forecasts) stops when IQR < 20% of median. For non-numeric debates, use **adaptive stability detection** instead of fixed round counts:

- Compute pairwise judge-agreement rate after each round.
- Treat agreement as a Beta-Binomial process; stop when the distribution is stable round-over-round (Kolmogorov-Smirnov test on successive rounds) [unverified as of 2026-09-16: the specific `p > 0.10` threshold and the two-consecutive-rounds rule are this skill's operating defaults, not values stated in the source paper].
- Practical proxy if you don't want to compute KS: stop when **two consecutive rounds produce no new arguments** AND **no member changes position**. New evidence or position shift → keep going. Stagnation → stop.
- Hard cap: 5 rounds. Beyond that, agents stop reasoning and start restating.

Source: Hu et al., "Multi-Agent Debate for LLM Judges with Adaptive Stability Detection," NeurIPS 2025 — [openreview.net/forum?id=Vusd1Hw2D9](https://openreview.net/forum?id=Vusd1Hw2D9), [arXiv:2510.12697](https://arxiv.org/abs/2510.12697). The paper models judge consensus as a time-varying Beta-Binomial mixture with adaptive stopping on distributional similarity (Kolmogorov-Smirnov test); verified 2026-09-16. The Beta-Binomial framing is the formal version; the "no new arguments + no position change" rule is the cheap operator approximation.

### EMS — Efficient Majority-then-Stopping

For *vote-based* synthesis (best-of-N where the answer is discrete), EMS is the cheap stopping rule:

```text
After each new sample (or each new round of N samples):
  Count current vote distribution.
  If the leader has > N/2 + sqrt(N) votes, STOP — further sampling cannot flip the outcome.
  If the leader has > N/2 but margin is thin, sample one more.
  Otherwise continue up to the budget.
```

The `sqrt(N)` margin is a Hoeffding-style safety buffer on top of the paper's exact rule (halt once the agents still unpolled cannot change the leader) [unverified as of 2026-09-16: the `sqrt(N)` buffer is this skill's conservative variant, not the published criterion]. The paper reports that EMS preserves majority-voting accuracy while cutting invoked agents by 35% and token consumption by 44%.

Source: [arXiv:2604.02863](https://arxiv.org/abs/2604.02863) — *EMS: Multi-Agent Voting via Efficient Majority-then-Stopping* (verified 2026-09-16). Stack with G18 (BMV) when you want both adaptive stopping AND minority-correctness recovery — EMS decides "are we done?", BMV decides "what's the answer?".

**When to use which stopping rule:**

| Synthesis shape | Stopping rule |
|---|---|
| Discrete answer space (yes/no, A/B/C, classification label) | **EMS** |
| Open-ended generation, multiple wordings | Adaptive stability (KS p > 0.10) or RCS centroid-converged |
| Numeric forecast | Delphi IQR < 20% of median |
| Soft judgment, no clear oracle | Position-stability (no new arguments, no shifts) |

## Prerequisites

Decide which platform you are using:

| Platform | Min version | Debate type |
|----------|------------|-------------|
| Claude Code | Any current | Subagent-based (orchestrator routes messages) |
| Claude Code | a build with Agent Teams (check the agent-teams docs; they may state no minimum version) | Agent Teams (teammates debate directly) — experimental |
| Codex | Any current | Custom agents (user triggers explicitly) |
| Any + MCP | TypeScript runtime | Protocol-enforced via MCP server |

Also decide which agent source you want to use:
- global installed agents in `~/.claude/agents/` or `~/.codex/agents/`
- repo-local agents in `.claude/agents/` or `.codex/agents/`
- shared team members installed from `agents/` and `agents/teams/`

Also decide which runtime surface fits the debate:
- Claude project/global/session-scoped agents, whole-session `--agent`, or interactive teams
- Codex project/global agents, CLI workers, app/IDE supervision, or automation/background runs

Debate-on-trigger is the preferred operating mode:
- round 1: independent reads first
- round 2: selective rebuttal only when a trigger is present
- synthesis: one owner writes the decision log and closes the worker set

For the universal selection logic, see [../SKILL.md](../SKILL.md).
For the broader runtime verification matrix, see [runtime-smoke-tests.md](runtime-smoke-tests.md).

## Option A: Claude Code Subagents (works today)

### Step 0: Check existing agents

Before copying templates, check if suitable agents already exist:

```bash
# List personal agents
ls ~/.claude/agents/*.md 2>/dev/null | head -20

# List project agents
ls .claude/agents/*.md 2>/dev/null | head -20
```

**For debates**: Existing domain agents often work better than generic perspective-agent wrappers. For example, if you have `product-strategist`, `startup-growth-specialist`, and `software-solution-architect` installed globally, use them directly as debate participants — they carry preloaded skills.

**If suitable agents exist**: Skip to Step 3 and reference them by name in your debate prompt. You may only need the `debate-synthesizer` template (or none at all if you orchestrate the debate from the main thread).

**If agents are missing**: Decide placement before creating:
- **Global** (`~/.claude/agents/`): for reusable roles you'll use across projects
- **Local** (`.claude/agents/`): for project-specific overrides or one-off customizations

Then proceed to Step 1 to copy only the templates you actually need.

### Step 1: Copy agent files (only if needed)

> Skip this step if Step 0 found existing agents that cover your debate roles.

Copy three files from the templates into your project:

```bash
# From repo root
mkdir -p .claude/agents

cp agents/templates/debate-orchestrator.md .claude/agents/
cp agents/templates/perspective-agent.md .claude/agents/
cp agents/templates/debate-synthesizer.md .claude/agents/
```

Or create them manually. The templates are starting points — customize for your domain.

### Step 2: Verify agents are recognized

In Claude Code, type `@` and check typeahead — you should see `debate-orchestrator`, `perspective-agent`, and `debate-synthesizer`.

Alternatively, run `/agents` to see all registered agents.

### Step 3: Trigger a debate

Option 1 — Direct request (Claude auto-delegates to the orchestrator):

```
I need to decide between a monolith and microservices for our new payments system.
Run a debate with architect, developer, and product manager perspectives.
```

Option 2 — @-mention the orchestrator:

```
@debate-orchestrator Should we use server-side rendering or client-side rendering
for the dashboard? Context: 50K daily users, SEO matters for public pages,
team is stronger in React than Next.js.
```

Option 3 — Quick single-perspective check (no full debate):

```
@perspective-agent Evaluate this migration plan as a security engineer.
[paste plan or reference files]
```

### Step 4: Review the decision log

The orchestrator produces a structured decision log with:
- Recommendation
- Key tradeoff (what you are giving up)
- Dissent (steelmanned minority position)
- Conditions (guardrails)
- Action items (ready for implementation)

Use the decision log as input for implementation workers.

## Option B: Codex Custom Agents

### Step 1: Create agent files

```bash
mkdir -p .codex/agents
```

Create `.codex/agents/perspective-architect.toml`:

```toml
name = "perspective_architect"
description = "Evaluates decisions from a system architecture lens."
model = "<model-id>"  # tier model from data/model-policy.json
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
You are a senior software architect evaluating a decision.
Be genuinely opinionated — hedging weakens the debate.
Return: stance (support/oppose/conditional), max 3 arguments
with evidence, risks with severity, suggested modifications.
Known bias: you tend to over-engineer.
"""
```

Create similar files for each persona you need (e.g., `perspective-marketer.toml`, `perspective-user.toml`).

Create `.codex/agents/debate-synthesizer.toml`:

```toml
name = "debate_synthesizer"
description = "Synthesizes debate positions into a decision log."
model = "<model-id>"  # tier model from data/model-policy.json
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
You are a judge, not a diplomat. Pick a direction.
Name what is being traded away.
Weight arguments by evidence quality, not vote count.
Never fabricate consensus.
Return: recommendation, rationale, key tradeoff,
dissent (steelmanned), conditions, action items.
"""
```

### Step 2: Trigger the debate

Codex delegates after a direct request or applicable `AGENTS.md`/skill policy. Keep the main thread focused on requirements, decision framing, and final synthesis. Start with read-heavy workers unless file ownership and verification rules are already explicit.

```
Spawn perspective_architect, perspective_marketer, and perspective_user agents
to debate whether we should build a custom CMS or use Contentful.
Context: 200 articles/month, 3 content editors, need localization.
Wait for all three, then spawn debate_synthesizer with their positions.
```

### Step 3: Switch between agents

Use `/agent` in the Codex CLI to view and switch between active agent threads.

### Step 4: Close the loop in the parent thread

After the worker outputs return:
- name the recommendation explicitly in the parent thread
- record the key tradeoff and dissent
- decide whether any implementation worker should be launched next
- close or stop the debate workers once synthesis is complete

## Option C: Claude Code Agent Teams (experimental)

### Step 1: Enable agent teams

Add to your Claude Code settings (`.claude/settings.json` or user settings):

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Requires a Claude Code build with Agent Teams; check the agent-teams docs for your version.

### Step 2: Trigger a team debate

Agent teams support direct inter-agent messaging — no orchestrator routing needed:

```
Spawn 3 agent teammates:
1. Architect perspective — optimizes for long-term technical health
2. Product manager perspective — optimizes for shipping the right thing fast
3. End user perspective — optimizes for minimum friction

Have them debate: Should we add a configuration wizard or keep the current
YAML-based setup? Our users are developers, but 40% of support tickets
are config errors.

Rules:
- Each teammate states their position independently first
- Then they challenge each other's weakest arguments
- After 2 rounds, produce a decision log with consensus and dissent
```

### Step 3: Monitor the debate

- In in-process mode, use the up and down arrow keys in the agent panel to select a teammate, then press Enter to open its transcript; Esc clears the selection (verified 2026-09-16 against the [agent-teams docs](https://code.claude.com/docs/en/agent-teams#talk-to-teammates-directly))
- Or use split panes in tmux/iTerm2 for simultaneous visibility
- The lead session sees task list updates as teammates claim and complete work

Operational guidance:
- teammates start from fresh task context plus project context; they do not inherit the lead session's full conversation history
- teammate runs should prefer review, diagnosis, and bounded decision work before parallel write-heavy implementation
- if the debate ends in a clear recommendation, have the lead synthesize and clean up the team before starting a new team

### Quality Gates With Hooks

Agent Teams support three hook events for enforcing quality during debates:

| Hook | Fires when | Exit code 2 effect |
|------|-----------|-------------------|
| `TeammateIdle` | A teammate is about to go idle | Sends feedback, keeps teammate working |
| `TaskCreated` | A task is being created | Prevents creation, sends feedback |
| `TaskCompleted` | A task is being marked complete | Prevents completion, sends feedback |

Use these to enforce debate discipline — for example, reject a "completed" task if the decision log is missing the mandatory dissent section:

```json
{
  "hooks": {
    "TaskCompleted": [{
      "matcher": "debate|decision",
      "hooks": [{
        "type": "command",
        "command": "grep -q 'Dissent:' /tmp/task_output || exit 2"
      }]
    }]
  }
}
```

### Plan Approval for Teammates

For high-stakes debates, require teammates to plan before implementing:

```
Spawn an architect teammate to analyze the migration.
Require plan approval before they make changes.
Only approve plans that include rollback strategy and test coverage.
```

The lead reviews plans autonomously based on your criteria. Rejected teammates stay in plan mode and revise.

### Limitations

- Experimental — may change or break
- Disabled by default
- No session resumption for in-process teammates
- One team per session
- No nested teams
- `skills` from a subagent definition are never applied to a teammate (it loads skills from project and user settings); `mcpServers` are applied only to a split-pane teammate — an in-process teammate ignores the field (verified 2026-09-16)
- High token cost (each teammate = separate Claude instance)
- Split panes not supported in VS Code terminal, Windows Terminal, or Ghostty

## Option D: MCP Debate Server (protocol-enforced)

For teams that want formal argue/rebut/judge protocol:

### Step 1: Stage and review the MCP server

This is an optional third-party server. Do not clone the moving default branch
and immediately run its package lifecycle. Before installation:

1. Select an immutable upstream release or commit and record its exact identity.
2. Download that source into a disposable staging directory without executing
   its scripts, hooks, or binaries.
3. Review the source, dependency lockfile, package lifecycle scripts, network
   behavior, requested filesystem access, and published security history.
4. Verify the downloaded artifact against an upstream signature or digest when
   one is published. If upstream publishes neither, record that provenance gap.
5. Build and smoke-test only inside a restricted sandbox with no credentials and
   no access to production or user configuration.
6. Obtain explicit operator approval for the reviewed immutable revision before
   adding its built entry point to Claude Code settings.

No revision is pinned here because this repository has not independently
reviewed and approved one. Re-review before every revision change.

### Step 2: Add to Claude Code settings

In `.claude/settings.json`:

```json
{
  "mcpServers": {
    "debate": {
      "command": "node",
      "args": ["/path/to/multi-agent-debate-mcp/dist/index.js"]
    }
  }
}
```

### Step 3: Use the protocol

The MCP server provides structured actions: `register`, `argue`, `rebut`, `judge`. Each call includes agent ID, round number, content, and a `needsMoreRounds` flag. A designated judge agent issues a verdict.

## Example Prompts

### Architecture decision

```
@debate-orchestrator
Decision: Should we use PostgreSQL with JSONB or MongoDB for our event store?
Context: 500K events/day, need complex queries on event metadata,
team has strong PostgreSQL experience but limited MongoDB experience.
Personas: architect, developer, ops engineer.
```

### Feature design

```
@debate-orchestrator
Decision: Free trial (14 days, full access) vs freemium (limited features, unlimited time)?
Context: B2B SaaS, $49/mo starting price, 2% current trial-to-paid conversion.
Personas: product manager, marketer, end user.
```

### Security tradeoff

```
@debate-orchestrator
Decision: OAuth2 + PKCE vs session-based auth with CSRF tokens for our SPA?
Context: public-facing app, 10K DAU, team has implemented both before.
Personas: security engineer, frontend developer, product manager.
```

### Quick single-perspective

```
@perspective-agent
Evaluate our new pricing page design as an end user who is comparing us
to three competitors. Be honest about what would make you leave.
[paste or reference the design]
```

## What To Expect

### Timeline

| Debate type | Rounds | Agents | Approximate duration |
|------------|--------|--------|---------------------|
| Quick (1 round, no rebuttal) | 1 | 2-3 | 1-2 minutes |
| Standard (1 round + synthesis) | 2 | 3-4 | 2-4 minutes |
| Full (positions + rebuttal + synthesis) | 3 | 3-4 | 4-8 minutes |

### Cost

Each perspective agent is a separate context window. Rough multipliers vs single-agent analysis:

| Setup | Cost multiplier |
|-------|----------------|
| 2 personas, 1 round | ~3x |
| 3 personas, 1 round + synthesis | ~4-5x |
| 3 personas, 2 rounds + synthesis | ~7-8x |
| Agent Teams (3 teammates, 2 rounds) | ~8-10x |

Use full debates for decisions where the cost of a wrong choice exceeds the debate cost. For routine decisions, a single-agent tradeoff analysis is enough.

### Debate-On-Trigger Defaults

Use free-form independent reads by default. Escalate to a rebuttal round only when one of these is true:
- round-1 positions materially disagree
- the decision is costly to reverse
- evidence points in different directions
- the team recipe already names a trigger such as rollback-vs-fix-forward, cutover sequencing, or go/no-go

If none of those are true, skip Round 2 and go straight to synthesis.

### Output

The final output is a **decision log** (not a transcript). It contains:

1. **Recommendation** — what to do
2. **Rationale** — why, referencing the debate
3. **Key tradeoff** — what you are giving up
4. **Dissent** — the strongest argument against the recommendation
5. **Conditions** — what must remain true for this to be the right call
6. **Action items** — concrete next steps for implementation

## Customizing Personas

### Add a new persona

Edit `.claude/agents/perspective-agent.md` to add to the Persona Examples section, or create a dedicated agent file:

```markdown
---
name: perspective-finance
description: Evaluate decisions from a financial and unit economics lens. Use when cost, margin, or runway implications matter.
tools: Read, Grep, Glob
maxTurns: 6
model: sonnet
---

# Finance Perspective

Evaluate the proposal as a CFO or finance lead.

## Focus
- Unit economics impact
- Implementation and maintenance cost
- Revenue and margin implications
- Cash flow and runway effects

## Known Bias
You tend to over-weight short-term cost savings over long-term strategic value.
```

### Adjust the number of rounds

In the debate-orchestrator template, Round 2 (rebuttal) is optional. To always skip it, remove the Round 2 section. To always run it, remove the "skip when" guidance.

### Change the synthesizer's behavior

Edit `debate-synthesizer.md` to adjust:
- Whether it must pick a side or can recommend "more research needed"
- How strongly it steelmans dissent
- Whether it includes implementation effort estimates in action items

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agents not appearing in `@` typeahead | Verify files are in `.claude/agents/` with correct frontmatter |
| Claude does not delegate to the orchestrator | Check the `description` field — it drives auto-delegation. Try `@debate-orchestrator` to force it |
| Agents hedge instead of taking positions | Strengthen the "be genuinely opinionated" instruction. Add: "If your position is the same as another agent's, find the point where you disagree" |
| Debate runs too long | Reduce `maxTurns`. Skip Round 2. Use 2 personas instead of 4 |
| Token cost too high | Apply the per-role model matrix in [cost-control.md](cost-control.md) §Signal 1 rather than a tier picked here — it owns the model-to-role mapping. In short: debaters and perspective agents on the standard tier, synthesizers on the critical tier, and the mechanical tier for read-only reviewers and bulk fan-out (tier → model in [data/model-policy.json](../data/model-policy.json)) |
| Codex agents not spawning | Restart after installing definitions, then issue a named spawn request or confirm applicable `AGENTS.md`/skill delegation policy is loaded. |
| Agent Teams not available | Verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings and that you are on a recent Claude Code build |

## 3-Of-5 Pattern For Large Debate Teams

When a team has 5 members and `debate: enabled: true`, do not run Round 2 with all 5. The house rule for this skill is 3-of-5: all 5 read independently, then only 3 debate. This keeps the rebuttal round focused and lowers the risk that agents spend their context budget summarizing peers instead of adding new analysis.

### The Pattern

**Round 1 — All 5 members read independently.** Each member produces their lens independently from the same intake pack. This is the divergent phase where breadth matters.

**Round 2 — Debate with 3 members only.** Pick:
- 2 members whose round-1 reads are most opposed (the pair with the strongest disagreement)
- 1 synthesis owner (named in the team recipe as `synthesis_owner`)

The other 2 members pass their round-1 output into the debate as written context but do not actively argue. They can be re-invited for round 3 if the synthesizer needs a tiebreaker.

### Teams This Applies To

Four manifest-defined workflow modes currently qualify (5 lenses, debate enabled):

- `expert-board` (`startup-strategy`) — synthesis owner: parent synthesis using the manifest's locked criteria
- `expert-board` (`growth`) — synthesis owner: parent synthesis using the manifest's locked criteria
- `expert-board` (`monetization`) — synthesis owner: parent synthesis using the pricing-advisor lens
- `expert-board` (`founder-blindspot`) — synthesis owner: parent synthesis using the manifest's locked criteria

### Why

This matches the operating discipline used elsewhere in the skill library: divergent reads are cheap, but convergent debate is expensive. Keep breadth in Round 1 and keep the rebuttal round narrow.

### When Not To Use It

- Three-member teams: run all three through debate. No sampling needed.
- Debate-disabled teams: the pattern does not apply.
- Single-round decisions with no strong disagreement in round 1: skip round 2 entirely and let the synthesizer write the memo from the independent reads.

### Practical Launch Prompt

```text
Team: [TEAM NAME]
Members: [all 5 names]
Synthesis owner: [NAMED IN MANIFEST]

Round 1 (parallel):
Each member reads the intake pack independently and produces their round-1 lens.

Round 2 (debate, 3 participants only):
After round 1, identify the 2 members whose reads are most opposed. Invite those 2 plus the synthesis owner into a debate round. The other 2 members pass their round-1 output as written context; they do not argue.

Output: single synthesized memo with the strongest dissent explicitly recorded.
```

## Layering Methods And Masks On Top Of Role Debate

The existing Round 1/2/3 protocol uses stakeholder-role personas (architect, PM, security engineer, etc.). Debate methods and decision masks layer on top without replacing the role system. Three orthogonal layers compose cleanly:

- **Layer 1 — WHO**: stakeholder role (existing perspective-agent personas in `agents/templates/perspective-agent.md` and team member files)
- **Layer 2 — HOW**: cognitive mode or structural method (new `agents/templates/debate-methods/`)
- **Layer 3 — LENS**: decision heuristic mask (new `agents/templates/decision-masks/`)

Each layer answers a different question. Layer 1 asks "who am I?" Layer 2 asks "how am I thinking right now?" Layer 3 asks "what decision heuristic am I running?"

### Example Stack For A Pricing Decision

- **Layer 1**: pricing-advisor, product-analytics-lead, and operating-system-reviewer (from the `expert-board` monetization panel)
- **Layer 2**: Round 2 uses **Pre-Mortem** — all three agents write the autopsy 12 months out
- **Layer 3**: Synthesis owner applies **Regret Minimization mask** to classify the decision as a one-way or two-way door before recommending

### Choosing A Method By Decision Shape

| Decision shape | Best method | Why |
|---|---|---|
| High uncertainty, long horizon | Scenario 2×2 | Tests decision against 4 futures |
| Ongoing tension, no "solution" | Polarity Management | Manages the tension, doesn't pick a side |
| Groupthink risk | Devil's Advocate | Pre-assigned opposition |
| 2-agent disagreement won't resolve | Steel-Manning | Each side argues the other's position |
| Mutually exclusive alternatives (A vs B) | Dialectical Inquiry | Formal thesis/antithesis/synthesis |
| Pre-launch risk review | Pre-Mortem | Imagine failure backwards |
| Creative / alternatives-generation | Six Thinking Hats | Rotates cognitive modes |
| Evidence quality is key, needs audit trail | Courtroom (PROClaim) | Progressive evidence retrieval, role-switching consistency test |
| Estimation / forecasting needed | Delphi Method | Anonymous iterative convergence on numbers, not positions |
| Assumptions untested, need depth before deciding | Socratic Questioning | Fewer roles than a full debate; measure actual calls and usage |
| Answer is a compromise, not a winner | Negotiation Protocol (ZOPA) | BATNA/ZOPA finds the blend; see `references/negotiation-protocol.md` |

### Choosing A Mask By Reasoning Bias

| Reasoning bias showing up | Mask | Why |
|---|---|---|
| Over-weighted happy path | Inversion | Reframes as "how to guarantee failure" |
| Legacy analogies dominate | First-Principles | Strips precedent and reasons from ground truth |
| Decision reversibility unclear | Regret Minimization | Classifies one-way vs two-way door |
| Team celebrating first-order win only | Second-Order | Forces "and then what?" chains |

## Framework → Team, Workflow Mode, Situation, Or Scenario Mapping

This is the primary lookup. Pick by team, by situation, or by specific scenario.

### By Retained Team Or Expert-board Mode

| Team | Primary method | Secondary method | Mask | Why this fit |
|---|---|---|---|---|
| `expert-board` (`ai-systems`) | Dialectical Inquiry | Scenario 2×2 | First-Principles | Architecture choices are mutually exclusive; agent/RAG topologies benefit from stripping framework analogies |
| `dev-migration-map` | Pre-Mortem | Devil's Advocate | Inversion | Migrations fail predictably; inversion catches cutover blind spots |
| `expert-board` (`marketing-diagnostics`) | Six Thinking Hats | Steel-Manning | — | Conflicting interpretations of the same analytics data; hat rotation forces each lens |
| `expert-board` (`growth-experiments`) | Scenario 2×2 | Six Thinking Hats | Regret Minimization | Channel prioritization under uncertainty; test bets against 4 futures |
| `expert-board` (`incident`) | Devil's Advocate | Pre-Mortem | Second-Order | Rollback vs fix-forward needs assigned opposition + cascade-risk check |
| `expert-board` (`ops-platform`) | Polarity Management | Dialectical Inquiry | — | Reliability vs cost is a permanent polarity, not a solvable problem |
| `expert-board` (`product-discovery`) | Steel-Manning | Six Thinking Hats | — | User-signal vs business-pressure disagreements need each side to argue the other's view |
| `expert-board` (`release-readiness`) | Pre-Mortem | Devil's Advocate | Second-Order | Binary go/no-go needs failure-mode surfacing + happy-path challenge |
| `expert-board` (`architecture-rfc`) | Dialectical Inquiry | Scenario 2×2 | First-Principles | Architecture is usually A vs B; first-principles strips legacy analogies |
| `expert-board` (`payments-platform`) | Pre-Mortem | Devil's Advocate | Inversion | High-blast-radius, hard to reverse; inversion catches compliance gaps |
| `expert-board` (`enterprise-readiness`) | Devil's Advocate | Pre-Mortem | — | Customer diligence is adversarial by design |
| `expert-board` (`founder-blindspot`) | Six Thinking Hats | Pre-Mortem | Inversion | Founder intuition strong but unvalidated; hats force uncomfortable lenses |
| `expert-board` (`growth`) | Steel-Manning | Scenario 2×2 | Second-Order | Healthy vs vanity growth needs real engagement; scenario tests 10× world |
| `expert-board` (`monetization`) | Pre-Mortem | Steel-Manning | Regret Minimization | Pricing changes are often irreversible; regret-min classifies the door |
| `expert-board` (`startup-strategy`) | Scenario 2×2 | Polarity Management | First-Principles | GTM under uncertainty fits scenario planning; ongoing tensions fit polarity management |

### By Situation (works on any team, including ad-hoc compositions)

| Situation | Best method | Why |
|---|---|---|
| Groupthink suspected; team converges too fast | **Devil's Advocate** | Pre-assigns opposition regardless of organic disagreement |
| Two stakeholders won't agree after Round 1 | **Steel-Manning** | Forces each to argue the other's position |
| High uncertainty about the future (12+ month horizon) | **Scenario 2×2** | Tests decision against 4 contrasting futures |
| Ongoing tension that keeps recurring | **Polarity Management** | Recognizes the "problem" as unsolvable; manages the tension |
| Creative exploration; need alternatives before narrowing | **Six Thinking Hats** | Rotates cognitive modes; explicit green-hat time for alternatives |
| Mutually exclusive alternatives (monolith vs microservices, build vs buy) | **Dialectical Inquiry** | Formal A / not-A / synthesis preserving both insights |
| Pre-launch risk review or major release gate | **Pre-Mortem** | Imagines failure backwards; catches 30% more risks than forward brainstorming (Klein 2007, citing Mitchell, Russo & Pennington 1989 on prospective hindsight) |
| Incident or urgent rollback under time pressure | **Devil's Advocate** + **Second-Order mask** | Fast adversarial check + cascade-risk surfacing |
| Founder intuition strong but evidence weak | **Pre-Mortem** + **Inversion mask** | Both structures force the bias into the open |
| Legacy analogies dominate ("we always do X") | **First-Principles mask** | Strips precedent and reasons from ground truth |
| Happy-path thinking baked in | **Inversion mask** | Reframes "how do we succeed?" to "how do we guarantee failure?" |
| Reversible-cheap vs irreversible-expensive confusion | **Regret Minimization mask** | Clarifies one-way vs two-way door before structuring debate |
| 2nd/3rd-order consequences matter (strategy, platform) | **Second-Order mask** | Forces "and then what?" chains |

### By Scenario (concrete decision types)

| Scenario | Stack (Method + Optional Mask) |
|---|---|
| "Should we raise prices on existing customers?" | Pre-Mortem + Steel-Manning + Regret Minimization mask |
| "Monolith vs microservices for the new service?" | Dialectical Inquiry + First-Principles mask |
| "Rollback or fix-forward on the incident from 20 minutes ago?" | Devil's Advocate + Second-Order mask |
| "Should we pivot the product in a new direction?" | Scenario 2×2 + Regret Minimization mask |
| "Is our growth healthy or vanity?" | Steel-Manning + Second-Order mask |
| "Should we ship this release candidate tonight?" | Pre-Mortem + Devil's Advocate |
| "PLG vs sales-led GTM for the new product?" | Scenario 2×2 + Polarity Management (because it's often both) |
| "Are we enterprise-ready for this customer?" | Devil's Advocate + Pre-Mortem |
| "Should we build this feature or buy a vendor?" | Dialectical Inquiry + First-Principles mask |
| "Why is our AEO/SEO ranking dropping?" | Six Thinking Hats (white/black/green) |
| "What's the smallest next experiment to run?" | Six Thinking Hats + Scenario 2×2 |
| "What are we missing in our product-market fit read?" | Pre-Mortem + Inversion mask |
| "Should we raise a round or stay lean?" | Scenario 2×2 + Regret Minimization mask |
| "How do we respond to this competitor's launch?" | Steel-Manning + Second-Order mask |
| "Will this architecture decision bite us in 2 years?" | Pre-Mortem + First-Principles mask |
| "Reliability vs delivery speed — how do we balance?" | Polarity Management |
| "What's the real bottleneck in our funnel?" | Six Thinking Hats (rotate through data/gut/risks/alternatives) |
| "Is this claim/assumption actually true?" | Courtroom (PROClaim) — plaintiff argues for, defense argues against, critic evaluates |
| "Should we kill this underperforming feature?" | Courtroom + Second-Order mask — formal for/against + cascade analysis |
| "How many users will we have in 6 months?" | Delphi Method — anonymous estimation, not debate |
| "What assumptions haven't we tested?" | Socratic Questioning — probing questions, not positions |
| "Can we find middle ground on this pricing tradeoff?" | Negotiation Protocol (ZOPA) — BATNA mapping, not winner/loser |
| "Is our security posture catching real issues?" | Purple Team (continuous red+blue) — see `references/purple-team-pattern.md` |

### Disambiguation: When Multiple Methods Could Fit

Some decisions appear in multiple method recommendations. The distinguishing factor is what KIND of answer you need:

| Question | If you need a YES/NO | If you need a NUMBER | If you need a BLEND |
|----------|---------------------|---------------------|---------------------|
| Pricing change | Pre-Mortem ("should we?") | Delphi ("what price?") | Negotiation ("what's acceptable to both growth and revenue?") |
| Architecture decision | Dialectical ("monolith vs micro?") | Delphi ("how long will migration take?") | Negotiation ("performance vs maintainability tradeoff?") |
| Feature scope | Devil's Advocate ("should we ship this?") | Delphi ("effort estimate?") | Negotiation ("what to cut vs keep?") |

Rule: if the answer is binary → debate method. If the answer is a number → Delphi. If the answer is a compromise → Negotiation.

### Stack Rules

1. **One method per debate, maximum two masks.** Stacking more creates noise that overwhelms synthesis.
2. **Method first, then mask.** Pick the structural method for the team shape, then add a mask only if the reasoning frame matters.
3. **Masks are per-agent, methods are team-wide.** Three agents can wear three different masks in the same debate.
4. **Default to no method on low-stakes decisions.** Free-form Round 1/2/3 is correct when cost of being wrong < cost of structured debate.
5. **Escalate to Polarity Management when a decision keeps returning.** If the team debates the same question more than twice in a quarter, the underlying issue is probably a polarity.

### Methods Stack With The 3-Of-5 Pattern

The 3-of-5 pattern (for large debate teams) determines WHO debates in Round 2. Methods determine HOW they debate. They compose:

1. All 5 members read independently (3-of-5 Round 1)
2. Pick the 2 most opposed members + synthesis owner (3-of-5 Round 2 selection)
3. In Round 2, the selected 3 run the chosen method — e.g., wearing hats, steel-manning, or running a pre-mortem
4. Synthesis owner writes the final memo with the chosen mask applied

Exception: **Pre-Mortem runs with all 5 members, not 3.** The power comes from independent autopsies, and parallel writing is cheap. Debate cost scales poorly; parallel writing does not.

## Method Reference Files

Full protocols, launch prompts, and common mistakes for each:

- [agents/templates/debate-methods/six-thinking-hats.md](../../../../agents/templates/debate-methods/six-thinking-hats.md)
- [agents/templates/debate-methods/pre-mortem.md](../../../../agents/templates/debate-methods/pre-mortem.md)
- [agents/templates/debate-methods/devils-advocate.md](../../../../agents/templates/debate-methods/devils-advocate.md)
- [agents/templates/debate-methods/steel-manning.md](../../../../agents/templates/debate-methods/steel-manning.md)
- [agents/templates/debate-methods/dialectical-inquiry.md](../../../../agents/templates/debate-methods/dialectical-inquiry.md)
- [agents/templates/debate-methods/scenario-2x2.md](../../../../agents/templates/debate-methods/scenario-2x2.md)
- [agents/templates/debate-methods/polarity-management.md](../../../../agents/templates/debate-methods/polarity-management.md)
- [agents/templates/debate-methods/courtroom.md](../../../../agents/templates/debate-methods/courtroom.md)
- [agents/templates/debate-methods/delphi-method.md](../../../../agents/templates/debate-methods/delphi-method.md)
- [agents/templates/debate-methods/socratic-questioning.md](../../../../agents/templates/debate-methods/socratic-questioning.md)

## Overlay and Protocol Reference Files

- [../references/multi-agent-reflexion.md](multi-agent-reflexion.md)
- [../references/purple-team-pattern.md](purple-team-pattern.md)
- [../references/prediction-market-confidence.md](prediction-market-confidence.md)
- [../references/negotiation-protocol.md](negotiation-protocol.md)

## Mask Reference Files

- [agents/templates/decision-masks/inversion.md](../../../../agents/templates/decision-masks/inversion.md)
- [agents/templates/decision-masks/first-principles.md](../../../../agents/templates/decision-masks/first-principles.md)
- [agents/templates/decision-masks/regret-minimization.md](../../../../agents/templates/decision-masks/regret-minimization.md)
- [agents/templates/decision-masks/second-order.md](../../../../agents/templates/decision-masks/second-order.md)
- [agents/templates/decision-masks/anchoring-mask.md](../../../../agents/templates/decision-masks/anchoring-mask.md)
- [agents/templates/decision-masks/base-rate-mask.md](../../../../agents/templates/decision-masks/base-rate-mask.md)
- [agents/templates/decision-masks/constitutional-mask.md](../../../../agents/templates/decision-masks/constitutional-mask.md)
