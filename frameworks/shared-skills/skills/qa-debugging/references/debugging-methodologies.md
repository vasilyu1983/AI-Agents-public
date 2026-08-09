# Debugging Methodologies - Systematic Approaches

This guide provides operational debugging methodologies for systematic problem-solving in production environments.

## Contents

- [The Scientific Method for Debugging](#the-scientific-method-for-debugging)
- [Binary Search Debugging (Divide & Conquer)](#binary-search-debugging-divide--conquer)
- [Delta Debugging (Comparing States)](#delta-debugging-comparing-states)
- [Rubber Duck Debugging](#rubber-duck-debugging)
- [Time-Travel Debugging](#time-travel-debugging)
- [Observability-First Debugging (Production)](#observability-first-debugging-production)
- [Debugging Retrospectives (Team Practice)](#debugging-retrospectives-team-practice)
- [Debugging Decision Matrix](#debugging-decision-matrix)
- [Anti-Patterns (What NOT to Do)](#anti-patterns-what-not-to-do)
- [AI-Native Root-Cause Analysis (Agent/LLM-Driven RCA)](#ai-native-root-cause-analysis-agentllm-driven-rca)
- [Debugging Checklist (Universal)](#debugging-checklist-universal)

---

## The Scientific Method for Debugging

**Core Principle**: Debugging is hypothesis testing. Form testable predictions, verify them systematically, iterate until root cause is found.

### Step-by-Step Process

**1. Observe & Reproduce**
```
CHECKLIST:
[ ] Document exact error message or symptoms
[ ] Write reproduction steps (manual or automated)
[ ] Identify minimal conditions needed to trigger issue
[ ] Verify issue reproduces consistently (80%+ success rate)
[ ] Record environment details (OS, versions, config)
```

**2. Form Hypothesis**
```
CHECKLIST:
[ ] Based on symptoms, predict where issue occurs
[ ] Consider recent changes (code, config, data, infra)
[ ] Review similar past issues
[ ] Identify 2-3 most likely causes
[ ] Rank hypotheses by probability
```

**3. Test Hypothesis**
```
CHECKLIST:
[ ] Design minimal test case
[ ] Predict expected outcome if hypothesis is correct
[ ] Execute test with instrumentation (logs, breakpoints)
[ ] Compare actual vs predicted outcome
[ ] Document results
```

**4. Iterate or Fix**
```
If hypothesis is correct:
  [ ] Implement fix
  [ ] Verify fix resolves issue
  [ ] Add regression test
  [ ] Document root cause and solution

If hypothesis is incorrect:
  [ ] Form new hypothesis based on test results
  [ ] Return to step 2
```

---

## OODA Loop (Fast-Cycle Incident Variant)

**Use when**: An active incident demands continuous action faster than you can stop to write formal hypotheses. OODA collapses the scientific method into four tight, repeatable cycles so you keep moving without losing structure.

**Observe** — pull the freshest signal (metrics spike, error rate, trace ID).
**Orient** — classify what changed: code, config, data, infra, or external dependency.
**Decide** — pick the single most reversible action: rollback, flag off, shed load, or targeted instrumentation.
**Act** — execute, then immediately loop back to Observe to confirm the effect.

Cycle time goal: under two minutes per loop during active impact. Switch to the full scientific method once the incident is mitigated and you are doing root-cause analysis.

---

## Binary Search Debugging (Divide & Conquer)

**Use when**: Issue could be in many places; need to narrow down quickly.

### Strategy

**1. Define Boundaries**
```
Working State:       Where does it work?
Broken State:        Where does it fail?
Search Space:        All code between working and broken
```

**2. Split in Half**
```
Add instrumentation at midpoint
Run test
If issue occurs before midpoint -> Search first half
If issue occurs after midpoint -> Search second half
```

**3. Repeat**
```
Continue splitting until issue isolated to single function/line
```

### Example: API Request Debugging

```
Step 1: Add logs at entry and exit
  -> Issue is inside handler

Step 2: Add log in middle of handler
  -> Issue is in second half

Step 3: Add log in middle of second half
  -> Issue is in database query

Step 4: Log query parameters
  -> Found: null parameter causing SQL error
```

### Implementation Checklist

```
[ ] Define working vs broken boundaries
[ ] Add instrumentation at midpoint
[ ] Test and observe where failure occurs
[ ] Split failing section in half
[ ] Repeat until isolated to 10-20 lines
[ ] Identify exact line causing issue
```

---

## Delta Debugging (Comparing States)

**Use when**: Issue started recently; need to identify what changed.

### Technique 1: Git Bisect

```bash
# Find commit that introduced bug
git bisect start
git bisect bad HEAD              # Current state is broken
git bisect good v1.2.3           # v1.2.3 was working
git bisect run ./test-script.sh  # Automated binary search

# Result: Commit abc123 introduced the bug
```

### Technique 2: Environment Comparison

```
PRODUCTION (broken)      vs      DEVELOPMENT (working)
=======================          =======================
Node.js 18.20.2                  Node.js 18.20.1       <- Version difference
DATABASE_POOL_SIZE=50            DATABASE_POOL_SIZE=10  <- Config difference
1M users                         100 test users        <- Load difference
```

**Action**: Test each difference in isolation to identify cause.

### Technique 3: Configuration Diff

```bash
# Compare production vs staging config
diff <(env | sort) <(ssh staging 'env | sort')

# Common findings:
#   Missing environment variables
#   Wrong API endpoints
#   Feature flags flipped
```

### Checklist

```
[ ] Identify when issue started (deployment, date, version)
[ ] List all changes since last working state
[ ] Test each change in isolation
[ ] Use git bisect for code changes
[ ] Compare environment configs
[ ] Check infrastructure changes
[ ] Review data migrations
```

---

## Rubber Duck Debugging

**Use when**: Stuck on a problem; need fresh perspective.

### How It Works

**Explain the problem to an inanimate object (rubber duck, colleague, AI)**

1. **Describe what the code should do**
2. **Explain what it actually does**
3. **Walk through logic line by line**
4. **Identify assumptions**

**Why it works**: Articulating the problem forces you to organize your thoughts and often reveals flawed assumptions.

### Example

```
"This function should calculate the average of an array.
It loops through all elements, adds them up, and divides by length.

Wait... if the array is empty, length is 0, so we divide by zero.
That's the bug!"
```

### Checklist

```
[ ] Explain expected behavior out loud
[ ] Describe actual behavior
[ ] Walk through code line by line
[ ] Question every assumption
[ ] Explain to someone unfamiliar with code
[ ] Write down your explanation
```

---

## Time-Travel Debugging

**Use when**: Need to understand how state changed over time.

### Tools

**JavaScript/Node.js**: Chrome DevTools, Node.js inspector, timeline/profiler recordings
**Python**: `pdb`, post-mortem debugging, `faulthandler` snapshots
**Go**: Delve
**Java**: IntelliJ IDEA debugger, Java Flight Recorder
**Low-level replay (Linux, native workloads)**: `rr` — records all kernel inputs and nondeterministic CPU effects for bit-for-bit deterministic replay with reverse-execution in gdb or (forward-only) lldb. For cloud VMs or Linux VMs on Apple Silicon, use `rr.soft` (software-counter mode: `rr record -W`). See `references/systems-debugging-tools.md` for rr, rr.soft, and Pernosco detail.

### When deterministic replay beats re-running

Re-running is unreliable when the failure is timing-dependent, environment-dependent, or only manifests in CI. Use `rr record` whenever:

- The bug disappears under a normal debugger (heisenbug).
- The failure rate is < 50% — you need to capture it once, then replay without re-flaking.
- The failure is a CI-only repro that cannot be replicated locally.
- The bug is a data race or memory corruption that corrupts state silently before crashing.

Once recorded, `rr replay` gives you unlimited reverse-execution passes over the identical execution.

### Technique

```
1. Capture the failing state (breakpoint, crash dump, trace, or profiler sample)
2. Reconstruct the execution timeline from earlier signals
3. Compare the last known good state to the first bad state
4. Inspect the variable, event, or side-effect that changed unexpectedly
5. Identify when state became incorrect
```

With rr, replace steps 1–2 with a single recording:
```
rr record ./my-binary         # step 1: capture everything
rr replay                     # steps 2–5: navigate in gdb with reverse-continue / reverse-next
(gdb) watch -l badVar         # jump backward to exactly when badVar last changed
```

### Example: React State Debugging

```javascript
// React DevTools - Component Timeline
[Time 0ms]  count: 0
[Time 100ms] count: 1  <- User clicked increment
[Time 200ms] count: 0  <- BUG: Reset to 0
[Time 300ms] count: 1

// Step backward to Time 200ms
// Examine call stack: componentDidUpdate called setState(0)
// Root cause: Incorrectly resetting state in side effect
```

---

## Observability-First Debugging (Production)

**Use when**: Debugging production issues without local reproduction.

### The Four Signals

**1. Logs** - What happened
**2. Metrics** - How much/how fast
**3. Traces** - Path through system
**4. Profiles** - Where CPU, memory, or lock time was actually spent

### Workflow

```
1. Start with metrics -> Identify affected service/endpoint
2. Check logs -> Filter by request ID or timestamp
3. Follow traces -> See full request path across services
4. Check profiles -> Confirm where time or memory was spent
5. Correlate -> Combine all four to understand context
```

### Example: Slow API Response

```
STEP 1 - METRICS:
  GET /api/orders latency spike: P95 went from 200ms to 2500ms

STEP 2 - TRACES (find slow request):
    Trace ID: abc-123
    Total: 2500ms
    - API Gateway: 10ms
    - Order Service: 2000ms <- Bottleneck
    - Database: 450ms

STEP 3 - LOGS (filter by trace ID):
  [order-service] "Executing query: SELECT * FROM orders WHERE user_id = ?"
  [order-service] "Query took 2000ms" <- N+1 query problem

ROOT CAUSE: Missing database index on user_id column
```

### Checklist

```
[ ] Check monitoring dashboard for anomalies
[ ] Identify affected service/component
[ ] Filter logs by time window or request ID
[ ] Examine distributed traces
[ ] Correlate logs, metrics, and traces
[ ] Form hypothesis from combined evidence
```

---

## Debugging Retrospectives (Team Practice)

**Use when:** Building team debugging capability and reducing MTTR across the organization.

### What Are Debugging Retrospectives?

Regular team sessions (weekly/biweekly) where engineers share interesting bugs they've encountered and how they resolved them. This builds pattern recognition across the team.

### Format (30-45 minutes)

```text
1. BUG PRESENTATION (10 min per bug, 2-3 bugs per session)
   - What was the symptom?
   - What was the hypothesis?
   - What was the actual root cause?
   - What made it tricky?

2. PATTERN DISCUSSION (10 min)
   - Have we seen similar bugs before?
   - What signals should we watch for?
   - Can we add detection/prevention?

3. ACTION ITEMS (5 min)
   - Add to runbook?
   - Create monitoring alert?
   - Update documentation?
```

### Bug Presentation Template

```markdown
## Bug Presentation Template

**Symptom:** What users/systems observed
**Impact:** Severity, affected users/systems
**Time to Resolution:** How long it took

**Initial Hypothesis:** What we first thought
**Actual Root Cause:** What it really was
**Why It Was Tricky:** What made diagnosis difficult

**Fix:** What we changed
**Prevention:** How we'll catch it earlier next time

**Key Learning:** One sentence takeaway
```

### Benefits

- **Reduced MTTR:** Team recognizes patterns faster
- **Knowledge sharing:** Junior engineers learn from senior debugging
- **Documentation:** Builds institutional knowledge
- **Proactive fixes:** Often surfaces related issues

### Checklist

```text
[ ] Schedule recurring 30-45 min session
[ ] Rotate facilitator each session
[ ] Collect 2-3 interesting bugs before session
[ ] Use presentation template for consistency
[ ] Track action items in ticket system
[ ] Archive presentations for future reference
```

---

## Debugging Decision Matrix

| Scenario | Method | Tools | Time to Resolution |
|----------|--------|-------|-------------------|
| Recent regression | Delta debugging, git bisect | Git, diff | 15-30 min |
| Intermittent failure | Observability-first, logs | APM, logs | 1-2 hours |
| Memory leak | Heap profiling | Chrome DevTools Memory tab, memray, heap snapshots | 2-4 hours |
| Performance issue | CPU/DB profiling | pprof, py-spy, EXPLAIN ANALYZE | 1-2 hours |
| Crash/exception | Stack trace analysis | Error tracking (Sentry) | 15-60 min |
| Logic error | Rubber duck, unit tests | Debugger, IDE | 30-90 min |
| Unknown cause | Binary search, systematic method | Logs, debugger | 2-8 hours |

---

## Anti-Patterns (What NOT to Do)

**1. Random Changes**
```
[FAIL] Bad:  Try changing this timeout value
[FAIL] Bad:  Let's restart the service
GOOD: Hypothesis: Timeout too short. Evidence: Logs show requests take 5s but timeout is 3s
```

**2. Skipping Reproduction**
```
[FAIL] Bad:  User reported error, deploying fix without testing
GOOD: Write reproduction test case, verify fix locally, deploy
```

**3. Insufficient Logging**
```
[FAIL] Bad:  try { ... } catch(e) { console.log('error') }
GOOD: logger.error('Failed to process payment', { orderId, error, stack })
```

**4. Ignoring Stack Traces**
```
[FAIL] Bad:  "It's crashing somewhere"
GOOD: "Stack trace shows user.js:42 tries to access null.email"
```

**5. Debugging in Production**
```
[FAIL] Bad:  Add debug logs directly to prod, restart service multiple times
GOOD: Export prod data to staging, reproduce locally, use feature flags
```

**6. Not Adding Tests**
```
[FAIL] Bad:  Fix bug, move on
GOOD: Fix bug, add regression test, prevent recurrence
```

---

## AI-Native Root-Cause Analysis (Agent/LLM-Driven RCA)

**Use when**: An agent or LLM is helping drive RCA from a recorded trace, logs, or a diff — common in agentic debugging workflows.

### Pattern: Hypothesis-First, Evidence-from-Replay

When an agent drives RCA, the process should mirror the scientific method:

```
1. Ingest evidence: recording artifact (rr trace), structured logs, git diff, error context.
2. Form a ranked list of hypotheses from the evidence — not from training priors alone.
3. For each top hypothesis, identify the specific moment in the recording or log line that would confirm or refute it.
4. Verify: replay the trace (or point to the exact log line/frame) that shows the cause.
5. Only after verification: state the root cause as a finding, with the supporting evidence cited.
6. Produce: fix recommendation + regression test target + prevention guardrail.
```

The key constraint: **a finding must be traceable to a specific artifact location** (replay timestamp, log line + correlation ID, stack frame). Anything not traceable is a hypothesis, not a finding.

### Anti-Pattern: LLM-Asserted Root Cause Without a Reproduced Trace

**The failure mode**: An LLM examines a stack trace and a description, then asserts "the root cause is X" based on pattern-matching from training data — without checking whether X is actually present in the recording or logs.

```
[FAIL] "Based on this stack trace, the likely root cause is a race condition
        in the connection pool. Fix by adding a lock."
→ This is a hypothesis, not a finding. No event in the trace was inspected.

GOOD: "Hypothesis: race condition in connection pool.
       Verification: rr replay shows thread 2 acquiring pool lock at t=1240ms
       while thread 1 holds it (frame 7 in backtrace). Confirmed race.
       Fix: add lock around pool.acquire(); regression test: reproduce two
       concurrent callers in a unit test."
```

**Rule**: An agent must either (a) reproduce the cause from the recorded trace or logs, or (b) explicitly label the output as an unverified hypothesis and state what evidence would confirm it. Presenting a training-data-derived pattern as a confirmed finding is a silent failure.

### Checklist for Agent-Driven RCA

```
[ ] Evidence collected before hypotheses formed (trace, logs, diff)?
[ ] Each hypothesis tied to a specific inspectable artifact location?
[ ] At least the top hypothesis verified by navigating the trace or log?
[ ] Root cause statement includes the specific event/line/frame that confirms it?
[ ] Unverified hypotheses labeled explicitly as hypotheses?
[ ] Fix and regression test target derived from the verified cause (not the hypothesis)?
```

---

## Debugging Checklist (Universal)

**Before Debugging**:
```
[ ] Can you reproduce it consistently?
[ ] Do you have logs/error messages?
[ ] Do you have a minimal test case?
[ ] Do you know when it started?
```

**During Debugging**:
```
[ ] Form hypothesis before making changes
[ ] Test one variable at a time
[ ] Document what you've tried
[ ] Use version control (commit working states)
[ ] Take breaks when stuck (rubber duck time)
```

**After Debugging**:
```
[ ] Fix verified in all environments?
[ ] Regression test added?
[ ] Root cause documented?
[ ] Similar issues elsewhere addressed?
[ ] Team notified of findings?
```

---

> **Remember**: Debugging is a skill that improves with practice. The best debuggers are systematic, patient, and document their findings.
