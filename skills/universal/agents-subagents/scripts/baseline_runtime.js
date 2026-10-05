// Opt-in matched-budget baseline (args.baseline: true). At equal compute a panel often only ties a plain vote
// (arXiv 2604.02460, 2508.17536; foundations-team-theory SKILL.md:36), so the run also asks one agent the same
// question k times, blind, and records the plurality beside the panel verdict. k is the memo count; the panel
// also spends tokens on challenges and synthesis, so the baseline gets less compute, never more. Agreement is not
// correctness: the human label in telemetry/workflow-runs.jsonl decides which side was right.
async function baselineVote(prompt, verdicts, k, options) {
  const schema = {
    type: 'object', required: ['verdict', 'reason'],
    properties: { verdict: { type: 'string', enum: verdicts }, reason: { type: 'string' } },
  };
  const votes = (await parallel(Array.from({ length: k }, (_unused, i) => () =>
    agent(prompt, Object.assign({}, options, { label: 'baseline:' + (i + 1), phase: 'Baseline', schema }))
  ))).filter((vote) => vote && verdicts.includes(vote.verdict));
  const tally = {};
  for (const vote of votes) tally[vote.verdict] = (tally[vote.verdict] || 0) + 1;
  const top = Math.max(0, ...Object.values(tally));
  const leaders = Object.keys(tally).filter((verdict) => tally[verdict] === top);
  log('Baseline: ' + votes.length + ' of ' + k + ' votes ' + JSON.stringify(tally));
  return { k, completed: votes.length, tally, plurality: leaders.length === 1 ? leaders[0] : null };
}
