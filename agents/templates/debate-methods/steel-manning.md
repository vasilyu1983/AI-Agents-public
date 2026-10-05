# Method: Steel-Manning

## Purpose

Force each side of a 2-party disagreement to argue the *opposing* view as strongly as possible. The opposite of straw-manning. Resolves ego-locked disagreements by requiring real engagement with the other position. Daniel Dennett's formulation in *Intuition Pumps* (2013), drawing on philosophical rhetoric tradition.

## When To Use

- Two agents have reached genuinely opposed positions in Round 1 and won't move
- User-signal vs business-pressure disagreements in the product-discovery board
- Healthy-growth vs vanity-growth reads in the `expert-board` growth mode
- Any pricing vs packaging disagreement in the `expert-board` monetization mode
- Security vs velocity tradeoffs
- When you suspect both sides are attacking caricatures of each other, not the real argument

## When NOT To Use

- More than 2 agents in genuine disagreement (use Dialectical Inquiry or Six Hats instead)
- One-sided debates where everyone agrees (use Devil's Advocate)
- Execution work with no meaningful disagreement

## The Core Move

After Round 1, the two opposing agents **swap positions** and argue the other side as strongly as they can. Then they return to their original positions and note what they learned.

This is NOT a concession. It's a structural de-biasing move. The goal is to make each side build the version of the opposing argument that the other side would find most compelling — not the version that's easiest to refute.

## Protocol

### Integration With Existing Debate Rounds

**Round 1 (unchanged)**: Two perspective agents read independently and produce opposed positions on the decision.

**Round 2A (swap)**: Each agent receives the OTHER agent's Round 1 position and is instructed to:
1. Steel-man it — build the strongest version of that argument
2. Name the most compelling evidence for the opposing view
3. Identify what the original position was missing or underweighting
4. Do not concede or balance — argue the opposing view as if it were your own

**Round 2B (return)**: Each agent returns to their original position. They write a revised version that:
1. Incorporates what they learned from steel-manning
2. Names the strongest remaining disagreement
3. Proposes what would change their mind

**Round 3 (synthesis)**: Synthesis owner reads both the original and revised positions. The memo explicitly names:
- What both sides agree on after steel-manning (the "true disagreement" is usually narrower than Round 1 suggests)
- What specific evidence would resolve the remaining disagreement
- Whether a decision can be made with current evidence, or whether the debate should pause until evidence arrives

## Launch Prompt

```text
DEBATE METHOD: Steel-Manning

Pre-condition: Round 1 produced two opposed positions. Identify the two agents
whose reads are most opposed. Name them explicitly.

Round 2A instruction for Agent A:

"Read Agent B's Round 1 position. Your job is to steel-man it — build the
strongest version of their argument, not the weakest.

1. What is the most compelling version of Agent B's position? Write it as if
   you were trying to convince an informed skeptic who has read Agent A's
   position and is leaning your way.
2. What specific evidence supports Agent B's position that Agent A underweighted
   or missed?
3. What would Agent A need to know to be persuaded? Name 2-3 concrete pieces of
   evidence that would change their mind.
4. Do NOT hedge. Do NOT balance. Do NOT say 'but of course the other side also
   has a point.' For this round, argue Agent B's view as if it were your own.

Return: a steel-manned version of Agent B's argument that Agent B would endorse
as the strongest statement of their position."

Same instruction to Agent B, with roles swapped.

Round 2B instruction for both agents:

"Return to your original position. Based on the steel-manning exercise, rewrite
your Round 1 position. Specifically:
1. What did you learn from steel-manning the other side?
2. Where do you still disagree, after genuinely engaging with the strongest
   version of the opposing view?
3. What specific evidence or condition would change your mind?
4. Is the real disagreement narrower than Round 1 suggested?"

Synthesis owner instruction:
"Read both the original and revised positions. Your memo names:
- The narrowed disagreement (usually smaller than Round 1 suggested)
- The specific evidence that would resolve it
- Whether a decision can be made now, or whether the debate should pause for
  evidence."
```

## Integration With The 3-Of-5 Pattern

Steel-Manning is inherently 2-agent. In a 5-member team:
1. All 5 members do Round 1 in their stakeholder roles
2. Identify the 2 most opposed positions
3. Those 2 agents do the steel-manning exchange
4. The other 3 members' Round 1 positions pass in as written context
5. Synthesis owner writes the memo incorporating all 5 inputs but centering on the narrowed 2-party disagreement

## Evidence

- Daniel Dennett, *Intuition Pumps and Other Tools for Thinking* (2013), ch. 3: "How to Compose a Successful Critical Commentary" — formalizes the four rules of steel-manning (attempt to re-express so clearly the opponent says "thanks, I wish I'd thought of that"; list points of agreement; mention anything you've learned; then and only then rebut).
- Bryan Caplan's "Ideological Turing Test" (2011) — a related pattern: can you argue the other side well enough that neutral observers can't tell which is your real view?
- [Philosophical rhetoric tradition, back to Aristotle's *Rhetoric*](https://plato.stanford.edu/entries/aristotle-rhetoric/) — the principle of charity in argumentation.

## Common Mistakes

- **Strawmanning the steel-man**: writing a weak version of the other side while pretending to steel-man. The test: would the opposing agent actually endorse this version? If not, you strawmanned.
- **Steel-manning and then immediately refuting**: this breaks the exercise. Round 2A must NOT refute; it can only steel-man. Refutation happens in Round 2B after both sides have steel-manned.
- **Skipping Round 2B**: returning to the original position is essential. Without it, you have two agents arguing each other's positions with no synthesis — the debate never resolves.
- **Using it on one-sided debates**: if both agents already agree, there's nothing to steel-man.
