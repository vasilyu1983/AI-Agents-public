# Method: Dialectical Inquiry

## Purpose

Formal thesis / antithesis / synthesis structure for decisions with two mutually exclusive alternatives. Forces both alternatives to be fully developed before synthesis, preserving insights from each. Hegel's dialectical method, adapted for strategy by Mason & Mitroff in the 1981 *Challenging Strategic Planning Assumptions*.

## When To Use

- Mutually exclusive alternatives: monolith vs microservices, build vs buy, PLG vs sales-led, niche vs horizontal
- Architecture RFCs where the choice is between two concrete paths
- Build-vs-buy decisions for tooling or infrastructure
- GTM model choices with long-horizon consequences
- Any decision framed as "A or B" where the team is defaulting to one without fully developing the other

## When NOT To Use

- Multi-option decisions (more than 2 alternatives — use Scenario 2×2 or Six Hats green mode)
- Decisions where one option is clearly dominant
- Ongoing tensions with no synthesis possible (use Polarity Management)
- Creative exploration (dialectical is rigid; exploration needs flexibility)

## The Three Phases

### Thesis (Position A)

One subset of agents develops Option A as the strongest possible recommendation. They do not balance it with Option B. Their job is to build Option A into its best form — with evidence, preconditions, and rollout plan.

### Antithesis (Position not-A, i.e., Option B)

A different subset of agents independently develops Option B as the strongest possible recommendation. Same rules: no balance, full commitment to B, treat it as the final answer.

### Synthesis

A third role (usually the team's synthesis owner) reads both fully-developed positions and writes a synthesis that:
- Preserves the strongest insight from A
- Preserves the strongest insight from B
- Either picks one option and names explicitly what gets lost from the other, OR
- Proposes a third path that captures insights from both (true Hegelian synthesis)

The synthesis is NOT a compromise. It's a reasoned recommendation that names the tradeoff.

## Protocol

### Integration With Existing Debate Rounds

**Round 0 (new, pre-debate)**: Orchestrator assigns agents to A-side and B-side. In a 3-agent debate, split as 1-1-1 (one for A, one for B, one for synthesis). In a 5-agent debate, split as 2-2-1.

**Round 1**: A-side agents write the strongest case for A. B-side agents write the strongest case for B. No cross-contamination — agents don't see the other side's output during Round 1.

**Round 2**: Both sides exchange written positions. Each side writes a focused critique of the other's position (not a rebuttal of their own, a critique of the opponent). Synthesis owner reads both.

**Round 3**: Synthesis owner writes the final memo. Either picks A, picks B, or proposes a third path.

## Launch Prompt

```text
DEBATE METHOD: Dialectical Inquiry

Pre-condition: The decision has been framed as a choice between Option A and
Option B. Name them explicitly before launching.

Option A: [DESCRIBE]
Option B: [DESCRIBE]

Round 0 assignments:
- A-side: [AGENT NAMES AND ROLES]
- B-side: [AGENT NAMES AND ROLES]
- Synthesis: [AGENT NAME, usually the team's synthesis owner]

A-side Round 1 instruction:
"You are arguing for Option A. Your job is to build the strongest possible
case for A. Do not balance with B's merits. Do not hedge. Assume A is the
final answer and write the recommendation as if you were committing to it.

Return:
1. The core argument for A (one paragraph, sharp)
2. The 3 strongest pieces of evidence supporting A
3. The preconditions that make A succeed
4. The concrete rollout plan for A
5. The strongest objection you anticipate, and how A handles it"

B-side Round 1 instruction: same structure, for Option B.

Round 2 instruction (both sides):
"You now have the other side's Round 1 position. Write a focused critique —
not a rebuttal of your own position, but a concrete critique of the other's:

1. What is their strongest point? Acknowledge it.
2. What is their weakest assumption? Name it specifically.
3. What evidence would strengthen their case that they did not cite?
4. What would have to be true for their position to dominate yours?"

Synthesis owner instruction (Round 3):
"You have both fully-developed positions and both critiques. Your memo either:

(a) Picks A and explicitly names what insight from B gets lost and whether
    that loss is acceptable
(b) Picks B and explicitly names what insight from A gets lost and whether
    that loss is acceptable
(c) Proposes a third path that captures the core insights from both

Do not write a compromise. Compromise loses both sides' strongest points.
Write a decision that names the tradeoff explicitly."
```

## Integration With The 3-Of-5 Pattern

Dialectical Inquiry fits 5-member teams naturally:
1. Split 5 members 2-2-1 (A-side, B-side, synthesis)
2. Each side runs Round 1 in parallel
3. Both sides exchange and critique in Round 2
4. Synthesis owner writes the memo in Round 3
5. No reduction from 5 to 3 needed — the method already organizes the team

## Evidence

- Georg Wilhelm Friedrich Hegel, *Phenomenology of Spirit* (1807) — original dialectical method, though Hegel himself rarely used the exact terms "thesis/antithesis/synthesis."
- Richard Mason and Ian Mitroff, *Challenging Strategic Planning Assumptions* (1981) — formal adaptation for strategic planning, now standard in MBA strategy courses.
- David Schwenk, "Cognitive simplification processes in strategic decision-making" (1984) — empirical evidence that dialectical inquiry produces higher-quality strategic decisions than devil's advocate or consensus approaches in complex domains.

## Common Mistakes

- **Weakening Option A or B during Round 1**: if you hedge, you get two mediocre positions and a mediocre synthesis. Both sides must be developed at full strength.
- **Synthesis as compromise**: the worst outcome is "let's do a bit of A and a bit of B." Compromises lose both sides' strongest points. Pick one or propose a true third path.
- **Using it when A and B aren't really mutually exclusive**: if you can do both, this is the wrong method. Use Polarity Management instead.
- **Skipping the critique round**: without it, the synthesis is based on unchallenged positions.
