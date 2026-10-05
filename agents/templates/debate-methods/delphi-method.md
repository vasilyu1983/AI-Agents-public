# Method: Delphi (Anonymous Iterative Estimation)

## Purpose

Anonymous iterative estimation for forecasting questions. Agents submit estimates independently, see statistical summaries (median, range, IQR — not who said what), and revise. 2–3 rounds until convergence. The original Rand Corporation technique from the 1950s, now validated in Human-AI Hybrid Delphi workflows achieving >90% consensus with 6 agents and 95% agreement with expert panels.

## When To Use

- Revenue projections (ARR, MRR forecasting)
- User growth estimates (DAU, MAU, activation rates)
- Sample size calculations for experiments (MDE/power analysis)
- Timeline estimation (sprint planning, launch dates, migration windows)
- Cost estimation (infra spend, hiring budget, CAC projections)
- Market sizing (TAM/SAM/SOM, willingness-to-pay ranges)
- Any question where the answer is a NUMBER, not a POSITION

## When NOT To Use

- When the question is a binary decision (use debate — Delphi estimates, it doesn't decide)
- When creative alternatives are needed (use Six Hats — Delphi converges, it doesn't diverge)
- When adversarial testing is needed (use Devil's Advocate — Delphi seeks consensus, not opposition)
- When the question has no numeric answer ("should we pivot?" is not a Delphi question)

## Protocol

### Integration With Existing Debate Rounds

**Round 1 (anonymous estimation)**: All agents submit their estimate + reasoning + confidence level independently. Each agent writes in their stakeholder role but does NOT see other agents' estimates. Anonymity is enforced — no names attached to estimates.

**Aggregation (new step, between rounds)**: Orchestrator computes median, mean, IQR, and range from all Round 1 estimates. Only the statistical summary is shared — never the individual estimates or which agent submitted what.

**Round 2 (informed revision)**: Each agent sees the statistical summary and may revise their estimate. If they change their number, they must explain what new information or reasoning caused the revision. If they hold, they must explain why.

**Convergence check**: If IQR < 20% of median, stop. The group has converged. Otherwise, proceed to Round 3.

**Round 3 (if needed — final revision)**: Agents see updated summary stats from Round 2. Outliers (estimates outside 1.5× IQR) must explicitly justify their position. Final estimates are collected.

**Synthesis**: Report the median as the point estimate, the IQR as the confidence range, and note any persistent outlier reasoning that the decision-maker should consider even if the group converged away from it.

## Launch Prompt

```text
DEBATE METHOD: Delphi (Anonymous Iterative Estimation)

Question to estimate: [THE NUMERIC QUESTION — e.g., "What ARR will we reach
by Q4 2026?"]

Round 1 instruction for each agent:

"You are estimating independently. Do NOT coordinate or reference other agents.

Provide:
1. Your point estimate (a single number with units)
2. Your confidence range (low–high, 80% interval)
3. Your reasoning (3–5 sentences, key assumptions named)
4. Your confidence level (low / medium / high) with one sentence explaining why

Your estimate is anonymous. Other agents will see summary statistics only, not
your individual number or identity."

Aggregation instruction (orchestrator):
"Compute and share with all agents:
- Median estimate
- Mean estimate
- Interquartile range (Q1–Q3)
- Full range (min–max)
- Number of agents
Do NOT share individual estimates. Do NOT name which agent submitted what."

Round 2 instruction for each agent:
"You now see the group's summary statistics. You may revise your estimate.

If you revise: state your new estimate and explain what changed your thinking.
If you hold: state that you hold and explain why the summary stats did not
change your view.

Convergence rule: if the IQR after this round is less than 20% of the median,
the estimation is complete."

Round 3 instruction (if IQR >= 20% of median after Round 2):
"Final revision round. Summary stats from Round 2 are shared.

If your estimate is an outlier (outside 1.5× IQR), you MUST justify your
position with specific evidence or assumptions that the group may be missing.
Otherwise you may hold or revise."

Synthesis owner instruction:
"Report:
- Point estimate: median of final round
- Confidence range: IQR of final round
- Convergence: did the group converge (IQR < 20% of median)?
- Outlier reasoning: if any agent remained an outlier, summarize their
  justification — this is signal, not noise
- Key assumptions: list the 3 most common assumptions across agents
- Decision guidance: what would change the estimate most (sensitivity)"
```

## Team Mapping

Delphi maps to estimation-heavy teams:
- **`expert-board` monetization mode**: revenue forecasting, pricing sensitivity
- **`expert-board` growth mode**: metric estimation, growth-rate projections
- **expert-board (growth-experiments)**: MDE calculations, sample size estimation, test duration
- **expert-board (data-analytics)**: capacity planning, infrastructure cost projections

## Integration With The 3-Of-5 Pattern

Delphi does NOT use 3-of-5. All agents estimate in every round. The power comes from independent estimation — reducing to 3 agents reduces the statistical signal. Run it as:
1. All 5 members estimate independently in Round 1
2. All 5 see summary stats and revise in Round 2
3. All 5 participate in Round 3 if needed
4. Synthesis owner reports the final statistics

Five estimates is the minimum for meaningful IQR. Dropping to 3 makes the convergence check unreliable.

## Evidence

- Rand Corporation, original Delphi method (1950s) — developed for Cold War technology forecasting, now standard in policy, healthcare, and business estimation.
- [Speed & Metwally, "The Human-AI Hybrid Delphi Model"](https://arxiv.org/abs/2508.09349), arXiv 2508.09349, 2025: the AI "replicated 95% of published expert consensus conclusions", and "compact panels of six senior experts achieved >90% consensus coverage". The six panellists were human experts, not agents.
- Real-Time AI Delphi (RT-AID) enables generative AI support for convergence acceleration in multi-agent estimation workflows.
- [Rowe & Wright, "The Delphi Technique as a Forecasting Tool"](https://doi.org/10.1016/S0169-2070(99)00018-7), International Journal of Forecasting, 1999 — meta-analysis showing Delphi outperforms unstructured group estimation across 27 studies.

## Key Finding

Anonymity prevents anchoring bias. Agents that see WHO estimated what anchor to authority — the most senior or most confident voice pulls the group toward their number. Agents that see only summary stats converge on evidence, not status. This is why sharing individual estimates destroys the method's primary benefit.

## Common Mistakes

- **Using Delphi for binary decisions**: Delphi estimates numbers. "Should we launch?" is not a Delphi question. "How many users will activate in the first 30 days?" is.
- **Sharing individual estimates**: destroys the anonymity benefit. The entire point is that agents see stats, not names. Once you share "Agent 3 estimated $2M," everyone anchors to Agent 3's authority.
- **Running too many rounds**: 3 rounds maximum. Beyond that, agents regress to the mean — they stop reasoning and start averaging. If IQR hasn't converged by Round 3, report the disagreement as meaningful signal.
- **Ignoring persistent outliers**: an outlier who holds through 3 rounds with clear reasoning is not noise — they are seeing something the group is missing. Always surface their justification in synthesis.
- **Skipping the convergence check**: running a fixed number of rounds regardless of IQR wastes tokens when the group converges in Round 2 and misses the signal when they don't.
