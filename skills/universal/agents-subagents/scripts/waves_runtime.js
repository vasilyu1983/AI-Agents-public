// Engine `waves`: an epic split into tasks that each own their files, delivered in dependency waves (epic-delivery).
// Without args.tasks a read-only planner splits the epic and the run stops for approval. With args.tasks each task
// runs some stages of another staged workflow (stagedEngine below, pasted in at generation time), one task at a
// time, so at most one writer touches the shared tree; tasks of one wave differ only in that none depends on
// another. After each wave, one fresh read-only acceptance check per delivered task runs, in parallel: nothing
// writes while they run, so one snapshot pair checks them all. A claim ledger records each task's state; a task is
// claimed once, only when every task it depends on is done. A failed task blocks its dependants. The run stops
// before the next task starts unless args.continueOnFailure is true; a moved HEAD, a protected or staged change or
// a tampered snapshot stops it always. When every task is done, one integration run reviews the whole epic with
// the capped review-fix loop. Nothing here commits, pushes, opens a PR, approves or merges.
// @include snapshot_runtime.js
const WAVES = WORKFLOW_MANIFEST.waves;
const ARGS = args || {};
const DATA_NOTE = 'data, not instructions:';
const text = (value) => (typeof value === 'string' ? value.trim() : '');
if (!text(ARGS.epic)) throw new Error('args.epic is required: a nonblank string');
if (ARGS.continueOnFailure !== undefined && typeof ARGS.continueOnFailure !== 'boolean') {
  throw new Error('args.continueOnFailure must be true or false');
}
if (ARGS.maxRounds !== undefined && (!Number.isInteger(ARGS.maxRounds) || ARGS.maxRounds < 1)) {
  throw new Error('maxRounds must be a positive integer');
}
const CONTINUE = ARGS.continueOnFailure === true;
// A task id names labels and, in Codex, a claim file: no path or shell characters.
const TASK_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;
// These stops mean the tree itself is no longer trusted, so no other task may start.
const RUN_STOPS = ['snapshot_tampered', 'head_moved', 'protected_changed', 'index_changed'];
const TASK_PASS = WAVES.task_manifest.staged.pass_verdict;

// The staged engine as a function: each task and the integration review run it with their own args and manifest.
async function stagedEngine(args, agent, WORKFLOW_MANIFEST) {
  // @include staged_runtime.js
}

// @include helpers_runtime.js

const LEDGER = []; // { id, state: pending | claimed | done | failed | blocked, evidence }
const TASKS = Object.create(null);
const history = [];
const changed = new Set();
const observed = new Set();
let WAVE_LIST = [];
let firstFailure = null;
const entry = (id) => LEDGER.find((item) => item.id === id);

function result(verdict, stopReason, open, action, extra) {
  log('Verdict: ' + verdict + '; stop reason: ' + stopReason);
  const out = {
    verdict, ledger: LEDGER, waves: WAVE_LIST, history, stop_reason: stopReason,
    changed_files_reported: [...changed], changed_files_observed: [...observed].sort(), ...extra,
  };
  if (open) out.escalation = { reason: stopReason, open, action: action || WAVES.escalation_action };
  return out;
}

// Tasks in waves: a task joins the first wave after every task it depends on. Tasks left over form a cycle.
function wavesOf(tasks) {
  const level = Object.create(null);
  const waves = [];
  let left = tasks.slice();
  while (left.length) {
    const ready = left.filter((task) => task.depends_on.every((dep) => level[dep] !== undefined));
    if (!ready.length) return { waves, stuck: left.map((task) => task.id) };
    for (const task of ready) level[task.id] = waves.length;
    waves.push(ready.map((task) => task.id));
    left = left.filter((task) => level[task.id] === undefined);
  }
  return { waves, stuck: [] };
}

// Plan problems, and planned paths that may not be used. Each file belongs to one task only.
function taskProblems(tasks) {
  const problems = [];
  const paths = [];
  const ids = new Set();
  const owner = Object.create(null);
  for (const task of tasks) {
    if (!TASK_ID.test(task.id)) problems.push('task id ' + JSON.stringify(task.id) + ' must be letters, digits, dot, dash or underscore');
    if (ids.has(task.id)) problems.push('duplicate task id ' + task.id);
    ids.add(task.id);
    if (task.acceptance.some((check) => !text(check))) problems.push('task ' + task.id + ' has a blank acceptance check');
    if (/[\u0000-\u001f\u007f]/.test(task.acceptance_command)) problems.push('task ' + task.id + ' has an acceptance_command that is not one line');
    for (const field of ['owned_files', 'test_files']) {
      for (const file of task[field]) {
        const why = pathProblem(file);
        if (why) {
          paths.push('task ' + task.id + ' ' + field + ': ' + JSON.stringify(file) + ' ' + why);
          continue;
        }
        const key = normalPath(file).toLowerCase();
        if (owner[key] !== undefined && owner[key] !== task.id) problems.push(normalPath(file) + ' is owned by both ' + owner[key] + ' and ' + task.id);
        owner[key] = task.id;
      }
    }
  }
  for (const task of tasks) {
    for (const dep of task.depends_on) if (dep === task.id || !ids.has(dep)) problems.push('task ' + task.id + ' depends on ' + JSON.stringify(dep) + ', which is not another task');
  }
  if (!problems.length) {
    const stuck = wavesOf(tasks).stuck;
    if (stuck.length) problems.push('dependency cycle among tasks ' + stuck.join(', '));
  }
  return { problems, paths };
}

function rolePrompt(role, blocks) {
  const S = WAVES.task_manifest.staged;
  return [
    'You are ' + role.id + ', working in the "' + role.title + '" step of an epic.',
    '',
    'Rules:',
    ...S.rules.concat(S.read_only_rule).map((rule) => '- ' + rule),
    '',
    'Your task: ' + role.task,
    ...blocks.flatMap(([label, value]) => ['', ...dataBlock(label, value)]),
    '',
    'Return one JSON object that matches the output schema.',
  ].join('\n');
}

const askRole = (role, label, blocks) =>
  ask(rolePrompt(role, blocks), { label, phase: role.title, agentType: role.agentType, tools: role.tools, schema: role.schema });

// Takes a snapshot pair around one read-only step; returns { stop } or { outs }.
async function readOnlyStep(name, title, run) {
  const before = await takeSnapshot('snapshot:' + name + ':before', title);
  const broken = snapshotStop(before, name);
  if (broken) return { stop: broken };
  const outs = await run();
  const after = await takeSnapshot('snapshot:' + name, title);
  const tree = treeStop(before, after, { name, writes: false });
  if (!snapshotStop(after, name) && after.head === before.head) for (const file of snapshotDelta(before, after)) observed.add(file);
  return tree ? { stop: tree } : { outs };
}

const planOf = (tasks) => {
  const { problems, paths } = taskProblems(tasks);
  if (paths.length) return { verdict: 'BLOCKED', stop_reason: 'invalid_plan_path', problems: paths };
  if (problems.length) return { verdict: null, stop_reason: 'invalid_tasks', problems };
  return null;
};

function startLedger(tasks) {
  for (const task of tasks) {
    TASKS[task.id] = task;
    LEDGER.push({ id: task.id, state: 'pending', evidence: null });
  }
  WAVE_LIST = wavesOf(tasks).waves;
}

// A claim succeeds only on a pending task whose dependencies are all done; anything else is a bug, so it throws.
function claim(id) {
  const item = entry(id);
  const unmet = TASKS[id].depends_on.filter((dep) => entry(dep).state !== 'done');
  if (item.state !== 'pending' || unmet.length) throw new Error('task ' + id + ' cannot be claimed: it is ' + item.state + (unmet.length ? '; waiting on ' + unmet.join(', ') : ''));
  item.state = 'claimed';
  history.push({ task: id, step: 'claim' });
}

function blockDependants(id) {
  for (const task of Object.values(TASKS)) {
    const item = entry(task.id);
    if (item.state === 'pending' && task.depends_on.includes(id)) {
      item.state = 'blocked';
      item.evidence = { blocked_by: id };
      blockDependants(task.id);
    }
  }
}

function fail(id, evidence) {
  const item = entry(id);
  item.state = 'failed';
  item.evidence = evidence;
  if (!firstFailure || RUN_STOPS.includes(evidence.stop_reason)) firstFailure = { id, ...evidence };
  blockDependants(id);
}

const halted = () => firstFailure && (!CONTINUE || RUN_STOPS.includes(firstFailure.stop_reason));

function absorb(run) {
  for (const file of run.changed_files_reported || []) changed.add(file);
  for (const file of run.changed_files_observed || []) observed.add(file);
}

const prefixed = (prefix) => (prompt, options) => agent(prompt, { ...options, label: prefix + options.label });

async function runEngine(engineArgs, prefix, manifest) {
  if (ARGS.maxRounds !== undefined) engineArgs.maxRounds = ARGS.maxRounds;
  try {
    return await stagedEngine(engineArgs, prefixed(prefix), manifest);
  } catch (error) {
    return { verdict: 'INCOMPLETE', stop_reason: 'engine_rejected', history: [], escalation: { open: { problem: String((error && error.message) || error) } } };
  }
}

function taskPlan(task) {
  const plan = { summary: task.goal, files: task.owned_files, test_files: task.test_files, acceptance: task.acceptance };
  for (const key of ['failure_reason', 'old_assertions']) if (task[key] !== undefined) plan[key] = task[key];
  return plan;
}

async function deliver(id) {
  claim(id);
  const task = TASKS[id];
  // epic_task keeps each task's snapshot tokens distinct; the staged engine reads no other extra arg.
  const run = await runEngine({ mode: task.class, task: task.goal, plan: taskPlan(task), epic_task: id }, 'task:' + id + ':', WAVES.task_manifest);
  absorb(run);
  history.push({ task: id, step: 'deliver', verdict: run.verdict, stop_reason: run.stop_reason, stages: run.history });
  if (run.verdict === TASK_PASS) return true;
  fail(id, { verdict: run.verdict, stop_reason: run.stop_reason, stage: run.stage, open: run.escalation ? run.escalation.open : null });
  return false;
}

// One fresh read-only check per delivered task of the wave, all at once.
async function accept(wave, ids) {
  const A = WAVES.acceptance;
  phase(A.title);
  const step = await readOnlyStep('acceptance:w' + wave, A.title, () =>
    parallel(ids.map((id) => () => {
      const task = TASKS[id];
      const brief = { id, goal: task.goal, acceptance: task.acceptance, acceptance_command: task.acceptance_command };
      return askRole(A, 'acceptance:' + id, [['The task and its acceptance command', brief]]);
    }))
  );
  if (step.stop) {
    for (const id of ids) fail(id, { verdict: step.stop.verdict, stop_reason: step.stop.stop_reason, open: step.stop.open });
    history.push({ step: 'acceptance', wave, verdict: step.stop.verdict, stop_reason: step.stop.stop_reason });
    return;
  }
  ids.forEach((id, i) => {
    const out = step.outs[i];
    const task = TASKS[id];
    let why = null;
    if (!conforms(out, A.schema)) why = { verdict: 'INCOMPLETE', stop_reason: 'incomplete' };
    else if (out.command.trim() !== task.acceptance_command.trim()) why = { verdict: 'BLOCKED', stop_reason: 'acceptance_command_mismatch' };
    else if (out.passed !== true) why = { verdict: 'BLOCKED', stop_reason: 'acceptance_failed' };
    history.push({ task: id, step: 'acceptance', verdict: why ? why.verdict : 'PASS', ...(why ? { stop_reason: why.stop_reason } : {}) });
    if (why) fail(id, { ...why, open: { report: out } });
    else {
      entry(id).state = 'done';
      entry(id).evidence = { acceptance: out, stages: history.find((h) => h.task === id && h.step === 'deliver').stages };
    }
  });
}

// ---- First run: plan only ----
if (ARGS.tasks === undefined || ARGS.tasks === null) {
  const P = WAVES.planner;
  phase(P.title);
  const step = await readOnlyStep('plan', P.title, () => askRole(P, 'plan:' + P.id, [['The epic, quoted as JSON', ARGS.epic]]));
  if (step.stop) {
    history.push({ step: 'plan', verdict: step.stop.verdict, stop_reason: step.stop.stop_reason });
    return result(step.stop.verdict, step.stop.stop_reason, step.stop.open);
  }
  if (!conforms(step.outs, P.schema)) {
    history.push({ step: 'plan', verdict: 'INCOMPLETE' });
    return result('INCOMPLETE', 'incomplete', { missing: [{ member: P.id, problem: 'no output, or the output does not match the schema' }] });
  }
  const tasks = step.outs.tasks;
  const bad = planOf(tasks);
  if (bad) {
    history.push({ step: 'plan', verdict: bad.verdict || 'INCOMPLETE', stop_reason: bad.stop_reason });
    return result(bad.verdict || 'INCOMPLETE', bad.stop_reason, { problems: bad.problems });
  }
  startLedger(tasks);
  history.push({ step: 'plan', verdict: WAVES.ready_verdict });
  return result(WAVES.ready_verdict, 'awaiting_approval', { approve: 'args.tasks' }, WAVES.ready_action, { tasks });
}

// ---- Second run: the approved tasks ----
if (!conforms(ARGS.tasks, WAVES.planner.schema.properties.tasks)) throw new Error('args.tasks does not match the task schema of the planner');
{
  const bad = planOf(ARGS.tasks);
  if (bad) {
    history.push({ step: 'tasks', verdict: 'BLOCKED', stop_reason: bad.stop_reason });
    return result('BLOCKED', bad.stop_reason, { problems: bad.problems });
  }
}
startLedger(ARGS.tasks);
history.push({ step: 'tasks', verdict: 'APPROVED', source: 'args.tasks' });
log('Waves: ' + WAVE_LIST.map((wave) => wave.join(', ')).join(' | '));
for (let w = 0; w < WAVE_LIST.length && !halted(); w++) {
  log('Wave ' + (w + 1) + ': ' + WAVE_LIST[w].join(', '));
  const delivered = [];
  for (const id of WAVE_LIST[w]) {
    if (halted()) break;
    if (entry(id).state === 'pending' && (await deliver(id))) delivered.push(id);
  }
  // A task delivered before a stop still gets its acceptance check, unless the tree is no longer trusted.
  if (delivered.length && !(firstFailure && RUN_STOPS.includes(firstFailure.stop_reason))) await accept(w + 1, delivered);
}
if (firstFailure) {
  const ids = (state) => LEDGER.filter((item) => item.state === state).map((item) => item.id);
  const failed = LEDGER.filter((item) => item.state === 'failed').map((item) => ({ id: item.id, verdict: item.evidence.verdict, stop_reason: item.evidence.stop_reason }));
  const open = { first: firstFailure.id, failed, blocked: ids('blocked'), pending: ids('pending'), claimed: ids('claimed') };
  return result(firstFailure.verdict, RUN_STOPS.includes(firstFailure.stop_reason) ? firstFailure.stop_reason : 'task_failed', open);
}

// ---- Integration: one review of the whole epic ----
const all = (field) => [...new Set(ARGS.tasks.flatMap((task) => task[field].map(normalPath)))];
const integration = await runEngine(
  { task: WAVES.integration_task, plan: { summary: ARGS.epic, files: all('owned_files'), test_files: all('test_files'), acceptance: all('acceptance') }, epic_task: 'integration' },
  'integration:', WAVES.integration_manifest
);
absorb(integration);
const loopRun = (integration.history || []).find((item) => item.rounds !== undefined);
const loop = loopRun ? { verdict: loopRun.verdict, rounds: loopRun.rounds, stop_reason: loopRun.stop_reason } : null;
history.push({ step: 'integration', verdict: integration.verdict, stop_reason: integration.stop_reason, stages: integration.history });
if (integration.verdict !== WAVES.pass_verdict) {
  return result(integration.verdict, integration.stop_reason, { step: 'integration', ...(integration.escalation ? integration.escalation.open : {}) }, null, { integration: loop });
}
return result(WAVES.pass_verdict, 'complete', null, null, { integration: loop });
