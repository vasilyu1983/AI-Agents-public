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
- [Bug: [Short Description]](#bug-short-description)
- [Debugging Decision Matrix](#debugging-decision-matrix)
- [Anti-Patterns (What NOT to Do)](#anti-patterns-what-not-to-do)
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

**JavaScript/Node.js**: Chrome DevTools, ndb
**Python**: pdb with reverse debugging
**Go**: Delve
**Java**: IntelliJ IDEA debugger

### Technique

```
1. Set breakpoint at crash/error
2. Run program to breakpoint
3. Step backward through execution
4. Inspect variable values at each step
5. Identify when state became incorrect
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

### The Three Pillars

**1. Logs** - What happened
**2. Metrics** - How much/how fast
**3. Traces** - Path through system

### Workflow

```
1. Start with metrics -> Identify affected service/endpoint
2. Check logs -> Filter by request ID or timestamp
3. Follow traces -> See full request path across services
4. Correlate -> Combine all three to understand context
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
## Bug: [Short Description]

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
| Memory leak | Heap profiling | Chrome DevTools, memory_profiler | 2-4 hours |
| Performance issue | CPU/DB profiling | pprof, EXPLAIN ANALYZE | 1-2 hours |
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
