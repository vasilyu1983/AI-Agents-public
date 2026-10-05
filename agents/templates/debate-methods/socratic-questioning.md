# Method: Socratic Questioning (Depth Through Questions)

## Purpose

A Socratic Critic asks probing questions instead of arguing positions. Forces depth without adversarial overhead. Six question types: clarification, assumption-probing, evidence-probing, perspective-exploring, consequence-analyzing, meta-questioning. The technique traces to Socrates' *elenchus* method and is now validated in multi-agent AI systems — Princeton's SocraticAI demonstrated that LLMs can extract knowledge from each other through mutual questioning, and the MAPS framework uses a dedicated Socratic Critic for existential, consistency, and boundary checks.

## When To Use

- Assumptions are untested and need surfacing before committing to a direction
- Founder intuition is strong but evidence is weak — need to deepen reasoning, not challenge it
- Before deciding WHETHER to debate (run Socratic first to find if real disagreement exists)
- Lightweight alternative when full debate is overkill but uncritical acceptance is risky
- When the team is confident but has not articulated WHY they are confident
- Early-stage product discovery where the right question matters more than the right answer
- Architecture decisions where "it depends" needs unpacking into "it depends on WHAT"

## When NOT To Use

- When you already know the question and need to decide (use debate — Socratic deepens, it doesn't decide)
- When estimation is needed (use Delphi — Socratic doesn't produce numbers)
- When adversarial challenge is the point (use Devil's Advocate — Socratic is collaborative, not oppositional)
- When time pressure demands a fast binary answer

## The Role

One agent is assigned as Socratic Critic. They do NOT argue a position. They do NOT express agreement or disagreement. They ask questions from six categories:

1. **Clarification**: "What exactly do you mean by X?" / "Can you give an example?" / "How is this different from Y?"
2. **Assumption**: "What are you assuming that you haven't verified?" / "What would have to be true for this to work?" / "What if the opposite assumption held?"
3. **Evidence**: "What evidence supports this? What would contradict it?" / "How would you know if you were wrong?" / "What data are you missing?"
4. **Perspective**: "How would [customer/competitor/investor] see this differently?" / "Who disagrees with this, and what's their strongest argument?"
5. **Consequence**: "If this is true, what follows? What are the second-order effects?" / "What's the worst version of success here?" / "What becomes harder later?"
6. **Meta**: "Why is this the question we're asking? Should we be asking something else?" / "What decision does answering this actually enable?" / "Are we solving the right problem?"

## Protocol

### Integration With Existing Debate Rounds

**Round 0 (new, pre-debate)**: Orchestrator assigns one agent as Socratic Critic. The Critic is briefed on the six question categories. Other agents are told the Critic will ask questions, not argue.

**Round 1 (unchanged)**: Other agents present their positions or analysis in their stakeholder roles, as normal. The Socratic Critic reads all positions but does NOT contribute a position.

**Round 1.5 (new — Socratic round)**: The Critic reads all Round 1 positions and asks 3–5 targeted questions. At least 3 different question categories must be represented. Questions are directed at specific positions or at gaps between positions.

**Round 2 (response round)**: Agents respond to the Critic's questions. The Critic may ask 1–2 follow-up questions if answers reveal new gaps. Agents may revise their positions based on what the questions surfaced.

**Synthesis**: Note which questions changed positions, which revealed gaps that need investigation, and which went unanswered. Unanswered questions are flagged as open risks or research needs.

## Launch Prompt

```text
DEBATE METHOD: Socratic Questioning

Socratic Critic assignment:
- Critic: [AGENT NAME, ROLE]
- All other agents: told that [AGENT] will ask questions, not argue positions

Socratic Critic brief:

"You are the Socratic Critic. You do NOT argue a position. You do NOT express
agreement or disagreement. Your only output is questions.

After reading all Round 1 positions, ask 3–5 targeted questions. Each question
must:
1. Come from one of the six categories: Clarification, Assumption, Evidence,
   Perspective, Consequence, Meta
2. Be directed at a specific claim, gap, or tension you see in the positions
3. Be a genuine question — not a rhetorical question hiding an argument

Cover at least 3 different categories. Prioritize the categories most needed:
- If positions are vague → lead with Clarification
- If positions are confident but ungrounded → lead with Evidence and Assumption
- If positions all agree → lead with Perspective and Meta
- If positions disagree → lead with Consequence and Clarification

After agents respond in Round 2, you may ask 1–2 follow-up questions if the
answers reveal new gaps. Do not ask more than 2 follow-ups."

Other agents' brief:
"Note: [AGENT] is the Socratic Critic. They will ask questions after Round 1.
In Round 2, answer their questions directly. If a question changes your view,
say so and explain what shifted. If it doesn't, explain why your position holds."

Synthesis owner instruction:
"Record:
- Questions that changed at least one agent's position (highest signal)
- Questions that revealed gaps no one had an answer for (open risks)
- Questions that went unanswered or were deflected (flag for follow-up)
- Revised positions after the Socratic round vs original Round 1 positions
The delta between Round 1 and post-Socratic positions IS the value of the
method. Make the delta explicit."
```

## Team Mapping

Socratic Questioning works as a lightweight overlay on any team:
- **`expert-board` founder-blindspot mode**: challenge assumptions before they calcify
- **expert-board (product-discovery)**: deepen user signals before committing to a solution
- **`expert-board` architecture-rfc mode**: challenge design assumptions before locking the RFC
- **expert-board (data-analytics)**: question metric definitions before building dashboards
- **marketing-strategy**: surface positioning assumptions before campaign spend

## Integration With The 3-Of-5 Pattern

Socratic Questioning modifies 3-of-5 slightly:
1. All 5 members do Round 1 positions in their stakeholder roles
2. The Socratic Critic is always one of the 3 selected for Round 2
3. The other 2 are picked for having the most assumption-laden or divergent positions
4. The Critic asks questions; the other 2 respond
5. Synthesis owner collects the delta

The Critic does NOT count against the "debating" slots — they generate questions, not positions. This means you effectively get 2 debaters + 1 questioner, which is cheaper than 3 debaters and often surfaces more insight.

## Evidence

- Princeton SocraticAI — demonstrated that LLMs can extract knowledge from each other through mutual questioning, with question-driven dialogue outperforming direct instruction on knowledge transfer tasks.
- MAPS framework (Multi-Agent Problem Solving) — uses a dedicated Socratic Critic for existential checks ("should we solve this?"), consistency checks ("do these positions contradict?"), and boundary checks ("what's outside our consideration?").
- Paul & Elder, *Critical Thinking: Tools for Taking Charge of Your Professional and Personal Life* (2002) — codified the six Socratic question types used in this protocol.
- [Foundation for Critical Thinking, "The Role of Socratic Questioning in Thinking, Teaching, and Learning"](https://www.criticalthinking.org/) — research base on question-driven depth vs assertion-driven breadth.

## Key Finding

Socratic questioning costs ~2× the token budget of a standard round vs 6–8× for full debate. It is the cheapest way to improve reasoning quality. The cost comes from one extra half-round (Round 1.5) plus shorter Round 2 responses. Full debate requires rebuttals, counter-rebuttals, and synthesis of adversarial positions. Socratic skips all of that and still surfaces the assumptions and gaps that matter most.

## Common Mistakes

- **Letting the Critic argue a position**: the Critic asks questions ONLY. The moment they say "I think..." or "The problem is..." they have broken role. Questions, not assertions.
- **Asking too many questions**: 5 max per round. More than 5 dilutes focus — agents respond superficially to many questions instead of deeply to a few. Quality over quantity.
- **Using it when a decision is already needed**: Socratic deepens understanding, it does not decide. If the team needs a binary answer by end of day, run a debate or Devil's Advocate. Socratic is pre-decision preparation.
- **Asking rhetorical questions**: "Don't you think this will fail?" is an argument disguised as a question. Real Socratic questions are open-ended: "What would have to be true for this to succeed?"
- **Skipping the delta analysis in synthesis**: the entire value is the difference between Round 1 positions and post-Socratic positions. If you don't make the delta explicit, you can't tell whether the questions changed anything.
