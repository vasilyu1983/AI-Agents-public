// Engine `staged`: ordered stages of named agents, each followed by a gate (feature-delivery, build-mvp,
// marketing-campaign). Read-only members of a parallel stage run at once; a writing stage runs its members
// one at a time and stages never overlap, so at most one writer touches the shared tree. A failed member or
// an output that does not match its schema fails the gate as INCOMPLETE, never as a pass. Earlier outputs
// reach later agents only as labelled one-line JSON data. A `loop` stage runs the review engine, pasted into
// reviewEngine() below at generation time from review_runtime.js. Nothing here commits, pushes, opens a PR,
// approves, publishes or sends. A tree snapshot before the first stage and after every stage and loop round
// enforces the read-only and scope rules on what the tree shows, not on what an agent reports.
// @include snapshot_runtime.js
const STAGED = WORKFLOW_MANIFEST.staged;
const ARGS = args || {};
const DATA_NOTE = 'data, not instructions:';
const LOOP_PASS = { review: 'CLEAN', build: 'PASS' };

const text = (value) => (typeof value === 'string' ? value.trim() : '');
for (const name of STAGED.args.required) {
  if (!text(ARGS[name])) throw new Error('args.' + name + ' is required: a nonblank string');
}
const MODE = STAGED.args.mode ? text(ARGS.mode) : null;
if (STAGED.args.mode && !STAGED.args.mode.choices.includes(MODE)) {
  throw new Error('args.mode must be one of: ' + STAGED.args.mode.choices.join(', '));
}
if (ARGS.maxRounds !== undefined && (!Number.isInteger(ARGS.maxRounds) || ARGS.maxRounds < 1)) {
  throw new Error('maxRounds must be a positive integer');
}
const REQUEST = {};
for (const name of STAGED.args.inputs) if (ARGS[name] !== undefined) REQUEST[name] = ARGS[name];

// The review engine (engine `review`) as a function: the stage passes its own args, agent and manifest.
async function reviewEngine(args, agent, WORKFLOW_MANIFEST) {
  // @include review_runtime.js
}

// @include helpers_runtime.js

const OUTPUT = {}; // stage id -> the output later stages read
const TITLE = {};
const history = [];
const changed = new Set();
const observed = new Set();
let TREE = null;
const report = (files) => {
  for (const file of Array.isArray(files) ? files : []) if (typeof file === 'string') changed.add(normalPath(file));
};

// Every stop short of the pass verdict carries an escalation for a human.
function stop(verdict, stageId, stopReason, open, action, extra) {
  log('Verdict: ' + verdict + ' at stage ' + stageId + '; stop reason: ' + stopReason);
  const result = {
    verdict, stage: stageId, history, stop_reason: stopReason,
    changed_files_reported: [...changed], changed_files_observed: [...observed].sort(), outputs: OUTPUT, ...extra,
  };
  if (open) result.escalation = { reason: stopReason, stage: stageId, open, action: action || STAGED.escalation_action };
  return result;
}

function scopeFiles(stage) {
  const files = [];
  for (const ref of stage.scope || []) {
    const [stageId, field] = ref.split('.');
    const value = OUTPUT[stageId] ? OUTPUT[stageId][field] : null;
    if (Array.isArray(value)) files.push(...value.filter((f) => typeof f === 'string').map(normalPath));
  }
  return [...new Set(files)];
}

function inputBlocks(stage) {
  const blocks = [['The user request, quoted as JSON', REQUEST]];
  for (const id of stage.inputs || []) blocks.push(['Output of the ' + TITLE[id] + ' stage', OUTPUT[id]]);
  if (stage.scope) blocks.push(['Files in scope; leave every other file alone', scopeFiles(stage)]);
  return blocks;
}

function memberPrompt(stage, member, earlier) {
  const task = typeof member.task === 'string' ? member.task : member.task[MODE];
  return [
    'You are ' + member.id + ', working in the "' + stage.title + '" stage.',
    '',
    'Rules:',
    ...STAGED.rules.concat(stage.writes ? STAGED.write_rule : STAGED.read_only_rule).map((rule) => '- ' + rule),
    '',
    'Your task: ' + task,
    ...(MODE ? ['Change class: ' + MODE + '.'] : []),
    ...inputBlocks(stage).concat(earlier).flatMap(([label, value]) => ['', ...dataBlock(label, value)]),
    '',
    'Return one JSON object that matches the output schema.',
  ].join('\n');
}

async function runMembers(stage) {
  const results = {};
  const one = (member, earlier) =>
    ask(memberPrompt(stage, member, earlier), {
      label: stage.id + ':' + member.id,
      phase: stage.title,
      agentType: member.agentType,
      tools: member.tools,
      schema: member.schema || stage.schema,
    });
  if (stage.parallel) {
    const outs = await parallel(stage.members.map((member) => () => one(member, [])));
    stage.members.forEach((member, i) => (results[member.id] = outs[i]));
  } else {
    // One member at a time; a later member sees the earlier members' outputs as data.
    for (const member of stage.members) {
      const earlier = Object.entries(results).map(([id, out]) => ['Output of ' + id + ' earlier in this stage', out]);
      results[member.id] = await one(member, earlier);
    }
  }
  return results;
}

// A slice may depend only on earlier slices: that rules out unknown ids, cycles and a wrong order at once.
function sliceProblems(slices) {
  const problems = [];
  const seen = new Set();
  for (const slice of slices) {
    if (seen.has(slice.id)) problems.push('duplicate slice id ' + slice.id);
    for (const dep of slice.depends_on) if (!seen.has(dep)) problems.push('slice ' + slice.id + ' depends on ' + dep + ', which is not an earlier slice');
    if (slice.acceptance.some((check) => !text(check))) problems.push('slice ' + slice.id + ' has a blank acceptance check');
    seen.add(slice.id);
  }
  return problems;
}

// Every planned path an approval gate names (gate.paths, e.g. "files" or "*.files") must be a plain repo path.
function planPathProblems(gate, artifact) {
  const problems = [];
  const walk = (value, parts, where) => {
    if (!parts.length) {
      for (const file of Array.isArray(value) ? value : [value]) {
        const why = pathProblem(file);
        if (why) problems.push(where + ': ' + JSON.stringify(file) + ' ' + why);
      }
      return;
    }
    const [head, ...rest] = parts;
    if (head === '*') (Array.isArray(value) ? value : []).forEach((item, i) => walk(item, rest, where + '[' + i + ']'));
    else if (value && typeof value === 'object' && value[head] !== undefined) walk(value[head], rest, where + '.' + head);
  };
  for (const ref of gate.paths || []) walk(artifact, ref.split('.'), gate.arg);
  return problems;
}

const lockIds = (gate) => (OUTPUT[gate.lock_stage][gate.lock_field] || []).map((line) => line.id);

function problemOf(stage, member, out) {
  if (!conforms(out, member.schema || stage.schema)) return 'no output, or the output does not match the schema';
  if (stage.gate.kind === 'lock_findings') {
    const ids = lockIds(stage.gate);
    const stray = out.findings.filter((f) => !ids.includes(f.lock_line)).map((f) => f.lock_line);
    if (stray.length) return 'findings cite no locked positioning line: ' + stray.join(', ');
  }
  return null;
}

function approvedArg(stage) {
  const gate = stage.gate;
  const member = stage.members.find((m) => m.id === gate.from);
  const schema = member.schema || stage.schema;
  const value = ARGS[gate.arg];
  if (!conforms(value, gate.field ? schema.properties[gate.field] : schema)) {
    throw new Error('args.' + gate.arg + ' does not match the output schema of the ' + stage.title + ' stage');
  }
  const problems = gate.validate === 'slices' ? sliceProblems(value) : [];
  if (problems.length) throw new Error('args.' + gate.arg + ' is not a valid slice plan: ' + problems.join('; '));
  return gate.field ? { [gate.field]: value } : value;
}

function pathStop(stage, artifact) {
  const problems = planPathProblems(stage.gate, artifact);
  if (!problems.length) return null;
  history.push({ stage: stage.id, verdict: 'BLOCKED', stop_reason: 'invalid_plan_path' });
  return stop('BLOCKED', stage.id, 'invalid_plan_path', { problems });
}

// Returns null when the gate passes, else { verdict, stop_reason, open, action?, extra? }.
function checkGate(stage, results) {
  const gate = stage.gate;
  const outs = stage.members.map((member) => results[member.id]);
  if (gate.kind === 'approval') {
    const artifact = gate.field ? results[gate.from][gate.field] : results[gate.from];
    const problems = gate.validate === 'slices' ? sliceProblems(artifact) : [];
    if (problems.length) return { verdict: 'INCOMPLETE', stop_reason: 'invalid_' + gate.arg, open: { problems } };
    const bad = planPathProblems(gate, artifact);
    if (bad.length) return { verdict: 'BLOCKED', stop_reason: 'invalid_plan_path', open: { problems: bad } };
    return { verdict: gate.verdict, stop_reason: 'awaiting_approval', open: { approve: 'args.' + gate.arg }, action: gate.action, extra: { [gate.arg]: artifact } };
  }
  if (gate.kind === 'tests') {
    const out = OUTPUT[stage.id];
    const expect = typeof gate.expect === 'string' ? gate.expect : gate.expect[MODE];
    const wanted = expect === 'red' ? 'fail' : 'pass';
    // Red means the reviewer ties every new test to the plan and at least one is red: a failure, or an error the
    // missing behaviour causes (a missing import is not stated). A guard test the plan asks for may pass.
    const wrong = expect === 'red' ? out.tests.filter((t) => t.for_stated_reason !== true) : out.tests.filter((t) => t.result !== wanted);
    const noRed = expect === 'red' && !out.tests.some((t) => t.result !== 'pass' && t.for_stated_reason === true);
    if (wrong.length || noRed || out.existing_tests_pass !== true) {
      return { verdict: STAGED.block_verdict, stop_reason: 'tests_not_' + expect, open: { expected: expect, wrong, existing_tests_pass: out.existing_tests_pass } };
    }
  }
  if (gate.kind === 'scope') {
    const allowed = scopeFiles(stage);
    const outside = outs.flatMap((out) => out.files_changed.map((file) => repoPath(file, allowed))).filter((file) => !allowed.includes(file));
    if (outside.length) return { verdict: STAGED.block_verdict, stop_reason: 'out_of_scope', open: { outside, allowed } };
  }
  if (gate.kind === 'flag') {
    const raised = stage.members
      .filter((member) => results[member.id][gate.field] === true)
      .map((member) => ({ member: member.id, reason: results[member.id][gate.reason_field] || '' }));
    if (raised.length) return { verdict: gate.verdict, stop_reason: gate.stop_reason, open: { raised } };
  }
  if (gate.kind === 'lock_findings') {
    // A draft that contradicts the lock blocks the pass verdict; it is never averaged against other findings.
    const contradictions = stage.members.flatMap((member) =>
      results[member.id].findings.filter((f) => f.contradicts_lock === true).map((f) => ({ reviewer: member.id, ...f }))
    );
    if (contradictions.length) return { verdict: gate.verdict, stop_reason: 'lock_contradiction', open: { contradictions } };
  }
  return null;
}

// The engine gets the stage inputs as data lines after its rules (never inside them), the allowed files,
// and the latest snapshot, so its own snapshots continue from this run's tree.
function engineManifest(stage, scope) {
  const engine = JSON.parse(JSON.stringify(stage.engine));
  engine.data_notes = inputBlocks(stage).slice(1).map(([label, value]) => dataBlock(label, value).join('\n'));
  engine.scope = scope;
  engine.snapshot_start = TREE;
  const M = engine.loop.modes[stage.loop.mode];
  if (M.fixer_rules) {
    // The fixer also reports the files it changed; the run checks the report against the observed changes.
    M.fixer_schema = {
      ...M.fixer_schema,
      required: [...new Set(M.fixer_schema.required.concat('files_changed'))],
      properties: { ...M.fixer_schema.properties, files_changed: { type: 'array', items: { type: 'string' } } },
    };
  }
  return engine;
}

function engineAgent(stage, prefix) {
  return (prompt, options) => {
    // A snapshot agent has no team role: it keeps the Bash-only tools the snapshot code gave it.
    if (options.label.startsWith('snapshot:')) return ask(prompt, { ...options, label: prefix + options.label });
    const role = stage.loop.agents[options.label.split(':')[0]];
    return ask(prompt, { ...options, label: prefix + options.label, agentType: role.agentType, tools: role.tools });
  };
}

async function runLoopStage(stage) {
  const loop = stage.loop;
  const units = loop.for_each ? OUTPUT[loop.for_each.stage][loop.for_each.field] : [null];
  const built = [];
  for (const unit of units) {
    const engineArgs = { mode: loop.mode, maxRounds: ARGS.maxRounds };
    if (unit) {
      engineArgs.spec = [
        'Build only the slice below; the slices already built stay as they are.',
        ...dataBlock('Slice, slices already built, and the product requirements', { slice: unit, built, prd: ARGS.prd }),
      ].join('\n');
      engineArgs.acceptance = unit.acceptance;
    }
    const prefix = stage.id + ':' + (unit ? unit.id + ':' : '');
    // A slice's own files are its scope; otherwise the stage scope applies.
    const allowed = unit && loop.for_each.scope ? unit[loop.for_each.scope].map(normalPath) : stage.scope ? scopeFiles(stage) : null;
    const r = await reviewEngine(engineArgs, engineAgent(stage, prefix), engineManifest(stage, allowed));
    if (r.snapshot) TREE = r.snapshot;
    for (const file of r.observed_changes || []) observed.add(file);
    history.push({ stage: stage.id, ...(unit ? { slice: unit.id } : {}), verdict: r.verdict, rounds: r.rounds, stop_reason: r.stop_reason });
    for (const round of r.history) {
      report(round.fix && round.fix.files_changed);
      report(round.build && round.build.files_changed);
    }
    const where = unit ? { slice: unit.id } : {};
    // The observed changes, checked before the verdict branch, so a failed loop cannot hide an out-of-scope write.
    const outside = allowed ? (r.observed_changes || []).filter((file) => !allowed.includes(file)) : [];
    if (outside.length) return stop('BLOCKED', stage.id, 'out_of_scope', { ...where, outside, allowed }, null, { loop: r, ...where });
    if (r.verdict !== LOOP_PASS[loop.mode]) {
      return stop(r.verdict, stage.id, r.stop_reason, { ...where, ...(r.escalation ? r.escalation.open : {}) }, null, { loop: r, ...where });
    }
    if (unit) built.push(unit.id);
  }
  return null;
}

let lastStage = null;
for (const stage of STAGED.stages) {
  TITLE[stage.id] = stage.title || stage.id;
  lastStage = stage.id;
  if (stage.loop) {
    if (!TREE) TREE = await takeSnapshot('snapshot:start', stage.loop.mode === 'build' ? 'Build' : 'Review');
    const broken = snapshotStop(TREE, 'start');
    if (broken) return stop(broken.verdict, stage.id, broken.stop_reason, broken.open);
    const stopped = await runLoopStage(stage);
    if (stopped) return stopped;
    continue;
  }
  const gate = stage.gate;
  if (gate.kind === 'approval' && ARGS[gate.arg] !== undefined && ARGS[gate.arg] !== null) {
    OUTPUT[stage.id] = approvedArg(stage);
    const badPath = pathStop(stage, ARGS[gate.arg]);
    if (badPath) return badPath;
    history.push({ stage: stage.id, verdict: 'APPROVED', source: 'args.' + gate.arg });
    log('Stage ' + stage.title + ': skipped; args.' + gate.arg + ' is the approved output');
    continue;
  }
  phase(stage.title);
  log('Stage ' + stage.title + ': ' + stage.members.map((m) => m.id).join(', ') + (stage.parallel ? ' in parallel' : ' one at a time'));
  if (!TREE) TREE = await takeSnapshot('snapshot:start', stage.title);
  const broken = snapshotStop(TREE, 'start');
  if (broken) return stop(broken.verdict, stage.id, broken.stop_reason, broken.open);
  const results = await runMembers(stage);
  // What the tree shows decides; the members' own reports are checked against it.
  const after = await takeSnapshot('snapshot:' + stage.id, stage.title);
  const usable = !snapshotStop(after, stage.id);
  const delta = usable && after.head === TREE.head ? snapshotDelta(TREE, after) : [];
  for (const file of delta) observed.add(file);
  const tree = treeStop(TREE, after, { name: stage.id, writes: stage.writes, scope: stage.writes && stage.scope ? scopeFiles(stage) : null });
  if (usable) TREE = after;
  if (tree) {
    history.push({ stage: stage.id, verdict: tree.verdict, stop_reason: tree.stop_reason });
    return stop(tree.verdict, stage.id, tree.stop_reason, tree.open);
  }
  const missing = stage.members
    .map((member) => ({ member: member.id, problem: problemOf(stage, member, results[member.id]) }))
    .filter((m) => m.problem);
  if (missing.length) {
    history.push({ stage: stage.id, verdict: 'INCOMPLETE', missing: missing.map((m) => m.member) });
    return stop('INCOMPLETE', stage.id, 'incomplete', { missing });
  }
  OUTPUT[stage.id] =
    gate.kind === 'approval' ? results[gate.from] : stage.members.length === 1 ? results[stage.members[0].id] : results;
  if (stage.writes) {
    const said = stage.members.flatMap((member) => results[member.id].files_changed.map((file) => repoPath(file, delta)));
    report(said);
    const mismatch = reportStop(delta, said, stage.id);
    if (mismatch) {
      history.push({ stage: stage.id, verdict: mismatch.verdict, stop_reason: mismatch.stop_reason });
      return stop(mismatch.verdict, stage.id, mismatch.stop_reason, mismatch.open);
    }
  }
  const failed = checkGate(stage, results);
  history.push({ stage: stage.id, verdict: failed ? failed.verdict : 'PASS', ...(failed ? { stop_reason: failed.stop_reason } : {}) });
  if (failed) return stop(failed.verdict, stage.id, failed.stop_reason, failed.open, failed.action, failed.extra);
}
return stop(STAGED.pass_verdict, lastStage, 'complete', null);
