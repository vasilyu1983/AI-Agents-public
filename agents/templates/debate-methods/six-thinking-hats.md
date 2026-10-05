# Method: Six Thinking Hats

## Purpose

Rotate 3 debate agents through structured cognitive modes to prevent single-lens analysis. Originally Edward de Bono's 1985 method for parallel thinking in groups.

## When To Use

- Creative exploration before narrowing (roadmap, experiment selection, feature prioritization)
- Conflicting interpretations of the same analytics data
- Founder blindspot reviews where gut, facts, and creativity need equal time
- Marketing diagnostics where SEO, AEO, analytics, and positioning lenses compete
- Any decision where you notice the team is stuck in one mode (too much caution, too much optimism, too much data without feeling)

## When NOT To Use

- Execution tasks with a clear spec (no creative exploration needed)
- Two-party disagreements (use Steel-Manning instead)
- High-stakes irreversible decisions (use Pre-Mortem or Devil's Advocate)

## The Six Hats

| Hat | Mode | Prompt the agent |
|---|---|---|
| **White** | Facts, data, gaps | "State only what the evidence shows. Separate facts from interpretations. Name missing data explicitly." |
| **Red** | Gut, feelings, hunches | "State your gut reaction without justification. What does this decision *feel* wrong or right about? Name the emotional load." |
| **Black** | Risks, caution, failure modes | "Only name downside risks, failure modes, and reasons this will hurt. Do not balance with upsides. This is pessimism on purpose." |
| **Yellow** | Benefits, optimism, value | "Only name the upside, the payoff, and the reasons this is worth doing. Do not balance with risks. This is optimism on purpose." |
| **Green** | Alternatives, creativity, possibilities | "Generate alternatives. Do not evaluate them. Aim for 5+ options the team has not considered. Wild ideas are welcome." |
| **Blue** | Process, meta, synthesis | "Manage the discussion itself. What's the debate actually about? Are we answering the right question? What's missing?" |

## Protocol

### Integration With Existing Debate Rounds

**Round 1 (unchanged)**: All perspective agents read independently in their assigned stakeholder role.

**Round 2 (hat rotation)**: Pick 3 members from Round 1. Assign each a hat based on what the debate needs:
- If data is contested → white + black + yellow
- If creative exploration matters → green + yellow + red
- If risks are under-examined → black + white + blue
- If the team is stuck in pessimism → yellow + green + red
- If meta confusion exists → blue + white + black

Each agent keeps their original stakeholder role AND puts on the assigned hat. Example: "You are the product-strategist wearing the black hat. Only name failure modes of this roadmap. Do not balance with benefits."

**Round 3 (synthesis)**: Synthesis owner reads all hat outputs and writes a memo that explicitly names what each hat surfaced. The synthesizer does not wear a hat themselves — they stay neutral.

## Launch Prompt

```text
DEBATE METHOD: Six Thinking Hats

Round 2 hat assignments:
- [Agent 1 name, role]: [HAT]
- [Agent 2 name, role]: [HAT]
- [Agent 3 name, role]: [HAT]

Each agent adds this to their Round 2 brief:

"You are wearing the [HAT] hat. Your instruction for this round is:
[exact prompt from the hat table above]

Do not balance your output. Other agents will cover other hats. Your job is to go deep on your assigned mode, not to produce a balanced memo.

Return a position using the perspective-agent Round 2 output contract, with the hat named at the top."

Synthesis owner instruction:
"Read the three hat outputs. Your final memo must explicitly name what each hat
surfaced and what gets lost if any one hat's output is ignored. You stay neutral;
do not wear a hat yourself."
```

## Integration With The 3-Of-5 Pattern

Six Hats stacks cleanly with the 3-of-5 pattern for large debate teams:
1. Round 1: all 5 members read in their stakeholder roles
2. Pick the 3 for the debate round (2 most opposed + synthesis owner)
3. Assign hats to those 3 in Round 2
4. The other 2 members' Round 1 positions pass in as written context

## Evidence

- Edward de Bono, *Six Thinking Hats* (1985). Used at IBM, DuPont, Prudential, and across Fortune 500 strategy work for 40+ years.
- [Harvard Business Review on parallel thinking frameworks (2019)](https://hbr.org/) — structured mode-switching reduces decision reversal rates in strategic reviews.

## Common Mistakes

- **One agent wearing multiple hats**: fragments focus. Use one hat per agent per round.
- **Synthesizer wearing a hat**: undermines synthesis neutrality. Keep blue/synth neutral.
- **All 6 hats in one debate**: too much content; the memo becomes a checklist, not a decision. Use 3 hats matched to what the debate needs.
- **Treating hats as permanent identities**: hats are for this one round only. The same agent can wear different hats in different debates.
