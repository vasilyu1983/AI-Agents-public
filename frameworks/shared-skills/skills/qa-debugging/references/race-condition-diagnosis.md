# Race Condition Diagnosis

Systematic approaches for detecting, reproducing, and fixing race conditions and concurrency bugs across languages and system layers.

---

## Contents

- [Race Condition Taxonomy](#race-condition-taxonomy)
- [Detection Tools](#detection-tools)
- [Reproduction Strategies](#reproduction-strategies)
- [Debugging Techniques](#debugging-techniques)
- [Common Concurrency Patterns](#common-concurrency-patterns)
- [Async/Await Pitfalls](#asyncawait-pitfalls)
- [Database-Level Race Conditions](#database-level-race-conditions)
- [Distributed System Races](#distributed-system-races)
- [Prevention Patterns](#prevention-patterns)
- [Testing Concurrent Code](#testing-concurrent-code)
- [Race Condition Diagnosis Checklist](#race-condition-diagnosis-checklist)
- [Related Resources](#related-resources)

---

## Race Condition Taxonomy

| Type | Description | Example | Difficulty |
|------|-------------|---------|-----------|
| Data race | Unsynchronized concurrent access to shared memory | Two threads incrementing a counter | Medium |
| TOCTOU | Time-of-check to time-of-use gap | Check file exists, then read (file deleted between) | Medium |
| Atomicity violation | Assumed-atomic operation is interruptible | Read-modify-write without lock | Medium |
| Order violation | Expected execution order not guaranteed | Initialize-then-use with no synchronization | Hard |
| Deadlock | Circular wait on locks | Thread A holds lock 1, waits for lock 2; Thread B holds lock 2, waits for lock 1 | Medium |
| Livelock | Threads actively working but making no progress | Two threads repeatedly yielding to each other | Hard |
| Starvation | Thread never gets access to shared resource | Low-priority thread always preempted | Hard |
| ABA problem | Value changes A->B->A, appears unchanged | CAS loop on pointer that was freed and reallocated | Very Hard |

---

## Detection Tools

### ThreadSanitizer (TSan)

```bash
# C/C++ - compile with TSan
gcc -fsanitize=thread -g -O1 my_program.c -o my_program
./my_program

# Go - built-in race detector
go test -race ./...
go run -race main.go

# Rust (nightly)
RUSTFLAGS="-Z sanitizer=thread" cargo +nightly test
```

**TSan output example:**

```text
WARNING: ThreadSanitizer: data race (pid=12345)
  Write of size 8 at 0x7f8a3c000000 by thread T2:
    #0 increment_counter counter.c:15
    #1 worker_thread main.c:42

  Previous read of size 8 at 0x7f8a3c000000 by thread T1:
    #0 get_counter counter.c:10
    #1 reader_thread main.c:37

  Location is global 'shared_counter' of size 8
```

### Go Race Detector

```go
// The Go race detector instruments memory accesses at compile time.
// It detects actual races during execution.

// Example: detected race
package main

import (
    "fmt"
    "sync"
)

func main() {
    counter := 0
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter++ // DATA RACE: unsynchronized write
        }()
    }
    wg.Wait()
    fmt.Println(counter)
}

// Fix: use atomic or mutex
import "sync/atomic"

func main() {
    var counter int64
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            atomic.AddInt64(&counter, 1)
        }()
    }
    wg.Wait()
    fmt.Println(atomic.LoadInt64(&counter))
}
```

### Java: FindBugs / SpotBugs

```xml
<!-- pom.xml - SpotBugs plugin -->
<plugin>
    <groupId>com.github.spotbugs</groupId>
    <artifactId>spotbugs-maven-plugin</artifactId>
    <version>4.8.3</version>
    <configuration>
        <effort>Max</effort>
        <threshold>Low</threshold>
        <includeFilterFile>spotbugs-include.xml</includeFilterFile>
    </configuration>
</plugin>
```

```bash
# Run SpotBugs
mvn spotbugs:check

# Relevant bug patterns:
# - DC_DOUBLECHECK: Double-checked locking
# - IS2_INCONSISTENT_SYNC: Inconsistent synchronization
# - RU_INVOKE_RUN: Calling Thread.run() instead of Thread.start()
# - STCAL_INVOKE_ON_STATIC_DATE_FORMAT_INSTANCE: Shared DateFormat
```

### Python: Threading Debug Tools

```python
import threading
import sys

# Enable verbose threading debug
threading._VERBOSE = True

# Detect deadlocks with faulthandler
import faulthandler
faulthandler.enable()
# If deadlocked, send SIGUSR1 to get traceback:
# kill -USR1 <pid>

# Custom lock wrapper to detect lock ordering violations
class TrackedLock:
    _lock_order = threading.local()

    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()
        self.order = id(self)

    def acquire(self):
        held = getattr(self._lock_order, 'held', [])
        for h in held:
            if h.order > self.order:
                print(f"LOCK ORDER VIOLATION: {h.name} held while acquiring {self.name}")
        self.lock.acquire()
        held.append(self)
        self._lock_order.held = held

    def release(self):
        self.lock.release()
        held = getattr(self._lock_order, 'held', [])
        held.remove(self)
```

---

## Reproduction Strategies

### Strategy 1: Stress Testing

```python
import concurrent.futures
import time

def stress_test_concurrent_operation(
    operation,
    n_threads: int = 50,
    n_iterations: int = 1000,
    stagger_ms: float = 0,
):
    """Run operation under high concurrency to surface races."""
    failures = []
    barrier = threading.Barrier(n_threads)

    def worker(thread_id):
        barrier.wait()  # All threads start simultaneously
        for i in range(n_iterations):
            try:
                if stagger_ms:
                    time.sleep(stagger_ms / 1000 * (thread_id % 3))
                result = operation()
                if not validate(result):
                    failures.append((thread_id, i, result))
            except Exception as e:
                failures.append((thread_id, i, str(e)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = [pool.submit(worker, tid) for tid in range(n_threads)]
        concurrent.futures.wait(futures)

    return {
        "total_operations": n_threads * n_iterations,
        "failures": len(failures),
        "failure_rate": len(failures) / (n_threads * n_iterations),
        "details": failures[:10],  # First 10 failures
    }
```

### Strategy 2: Delay Injection

```python
import functools
import random
import time

def inject_delay(target_function, delay_range=(0.001, 0.01)):
    """Wrap a function to inject random delays, increasing race window."""
    @functools.wraps(target_function)
    def wrapper(*args, **kwargs):
        delay = random.uniform(*delay_range)
        time.sleep(delay)
        result = target_function(*args, **kwargs)
        time.sleep(delay)
        return result
    return wrapper

# Usage: monkey-patch the suspected racy function
original_read = database.read
database.read = inject_delay(original_read, delay_range=(0.005, 0.05))
# Now run the test - the wider timing window makes races more likely
```

### Strategy 3: Controlled Scheduling

```python
import threading

class ControlledScheduler:
    """Force specific thread interleavings to reproduce races."""

    def __init__(self):
        self.checkpoints = {}

    def checkpoint(self, name: str):
        """Block until checkpoint is released."""
        event = self.checkpoints.setdefault(name, threading.Event())
        event.wait()

    def release(self, name: str):
        """Release a blocked checkpoint."""
        event = self.checkpoints.setdefault(name, threading.Event())
        event.set()

# Usage: force specific interleaving
scheduler = ControlledScheduler()

def thread_a():
    value = read_balance()           # Step 1: Read
    scheduler.checkpoint("a_read")   # Wait here
    write_balance(value + 100)       # Step 3: Write (stale value!)

def thread_b():
    scheduler.release("a_read")      # Let A proceed after read
    time.sleep(0.01)                 # Give A time to hit checkpoint
    value = read_balance()           # Step 2: Read (same value as A)
    write_balance(value + 50)        # Step 2.5: Write

# This forces: A reads -> B reads -> B writes -> A writes (lost update)
```

---

## Debugging Techniques

### Happens-Before Analysis

```text
Happens-before defines the ordering guarantees in concurrent execution.

Key rules:
1. Program order: Within a thread, earlier statements happen-before later ones
2. Lock rule: unlock(m) happens-before subsequent lock(m)
3. Volatile/atomic: Write to volatile happens-before read of same volatile
4. Thread start: Thread.start() happens-before any action in the started thread
5. Thread join: All actions in a thread happen-before join() returns
6. Transitivity: If A happens-before B, and B happens-before C, then A happens-before C

Debugging with happens-before:
1. Identify the shared variable(s) involved in the bug
2. Trace all accesses to those variables across threads
3. For each pair of conflicting accesses:
   - Is there a happens-before relationship?
   - If not → data race
4. Add synchronization to establish happens-before
```

### Lockset Analysis

```text
Lockset algorithm:
1. For each shared variable, maintain a "candidate lockset" (all locks)
2. On each access to the variable, intersect the candidate lockset
   with the locks currently held by the accessing thread
3. If the candidate lockset becomes empty → potential race condition

Example:
  Variable: shared_counter
  Initial candidate lockset: {lock_a, lock_b, lock_c}

  Thread 1 accesses shared_counter holding {lock_a, lock_b}
    → candidate = {lock_a, lock_b, lock_c} ∩ {lock_a, lock_b} = {lock_a, lock_b}

  Thread 2 accesses shared_counter holding {lock_b, lock_c}
    → candidate = {lock_a, lock_b} ∩ {lock_b, lock_c} = {lock_b}

  Thread 3 accesses shared_counter holding {lock_a}
    → candidate = {lock_b} ∩ {lock_a} = {}
    → WARNING: No consistent lock protects shared_counter
```

---

## Common Concurrency Patterns

### Double-Checked Locking (Broken and Fixed)

```java
// BROKEN: Double-checked locking without volatile
class Singleton {
    private static Singleton instance; // Missing volatile!

    public static Singleton getInstance() {
        if (instance == null) {              // First check (no lock)
            synchronized (Singleton.class) {
                if (instance == null) {      // Second check (with lock)
                    instance = new Singleton(); // May be seen partially constructed
                }
            }
        }
        return instance;
    }
}

// FIXED: Use volatile
class Singleton {
    private static volatile Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

### Read-Modify-Write

```python
# RACE: Non-atomic read-modify-write
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1  # Read + Modify + Write = NOT atomic

# FIX: Use lock
import threading

class Counter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.value += 1
```

### Producer-Consumer

```python
import queue
import threading

# SAFE: Using thread-safe queue
class ProducerConsumer:
    def __init__(self, max_size=100):
        self.queue = queue.Queue(maxsize=max_size)
        self.shutdown = threading.Event()

    def produce(self, item):
        while not self.shutdown.is_set():
            try:
                self.queue.put(item, timeout=1.0)
                return True
            except queue.Full:
                continue
        return False

    def consume(self):
        while not self.shutdown.is_set():
            try:
                item = self.queue.get(timeout=1.0)
                self.process(item)
                self.queue.task_done()
            except queue.Empty:
                continue

    def graceful_shutdown(self):
        self.shutdown.set()
        self.queue.join()  # Wait for all items to be processed
```

---

## Async/Await Pitfalls

### Shared Mutable State in Async Code

```javascript
// RACE: Shared state in async handlers
let requestCount = 0;

app.get('/api/data', async (req, res) => {
  requestCount++;         // Non-atomic in theory, but single-threaded in Node.js
  const current = requestCount;

  const data = await fetchFromDB(); // Yields execution here!

  // After await, another request may have changed requestCount
  if (requestCount !== current) {
    console.log('Concurrent modification detected');
  }

  res.json(data);
});

// RACE: Async check-then-act
async function transferFunds(from, to, amount) {
  const balance = await getBalance(from);  // Check
  // Another transfer could happen here!
  if (balance >= amount) {
    await deductBalance(from, amount);      // Act
    await addBalance(to, amount);
  }
}

// FIX: Use database transaction
async function transferFunds(from, to, amount) {
  await db.transaction(async (tx) => {
    const balance = await tx.getBalance(from, { forUpdate: true });
    if (balance >= amount) {
      await tx.deductBalance(from, amount);
      await tx.addBalance(to, amount);
    }
  });
}
```

### Python Async Races

```python
import asyncio

# RACE: Shared state across coroutines
balance = 100

async def withdraw(amount):
    global balance
    current = balance          # Read
    await asyncio.sleep(0)     # Yield! Other coroutine runs
    balance = current - amount # Write (stale value)

async def main():
    # Both read balance=100, both write 100-50=50 instead of 0
    await asyncio.gather(withdraw(50), withdraw(50))
    print(f"Balance: {balance}")  # Expected: 0, Actual: 50

# FIX: Use asyncio.Lock
lock = asyncio.Lock()

async def withdraw(amount):
    global balance
    async with lock:
        if balance >= amount:
            current = balance
            await asyncio.sleep(0)
            balance = current - amount
```

---

## Database-Level Race Conditions

### Lost Update Problem

```sql
-- RACE: Two transactions read, then update
-- Transaction A
SELECT balance FROM accounts WHERE id = 1;  -- Returns 100
-- Transaction B
SELECT balance FROM accounts WHERE id = 1;  -- Returns 100
-- Transaction A
UPDATE accounts SET balance = 100 + 50 WHERE id = 1;  -- Sets 150
-- Transaction B
UPDATE accounts SET balance = 100 - 30 WHERE id = 1;  -- Sets 70 (lost A's +50!)

-- FIX: Use SELECT FOR UPDATE
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- Locks row
UPDATE accounts SET balance = balance + 50 WHERE id = 1;
COMMIT;

-- FIX: Use atomic update
UPDATE accounts SET balance = balance + 50 WHERE id = 1;
```

### Optimistic Concurrency Control

```python
# Using a version column for optimistic locking
async def update_with_optimistic_lock(item_id: int, updates: dict):
    """Retry on version conflict."""
    max_retries = 3

    for attempt in range(max_retries):
        # Read current version
        item = await db.fetch_one(
            "SELECT * FROM items WHERE id = $1", item_id
        )
        current_version = item["version"]

        # Attempt update with version check
        result = await db.execute(
            """UPDATE items
               SET data = $1, version = version + 1
               WHERE id = $2 AND version = $3""",
            updates, item_id, current_version,
        )

        if result.rowcount == 1:
            return True  # Success
        # Version mismatch: someone else updated. Retry.

    raise ConflictError(f"Failed to update item {item_id} after {max_retries} retries")
```

### Database Race Condition Summary

| Race | Symptom | Fix |
|------|---------|-----|
| Lost update | Concurrent writes overwrite each other | `SELECT FOR UPDATE`, atomic operations |
| Dirty read | Reading uncommitted data from other transaction | Use READ COMMITTED or higher isolation |
| Non-repeatable read | Same query returns different results in one transaction | Use REPEATABLE READ |
| Phantom read | New rows appear between queries in same transaction | Use SERIALIZABLE |
| Insert race (duplicate) | Two processes insert same unique record | Unique constraint + ON CONFLICT |
| Counter race | Concurrent increments lose counts | `UPDATE SET count = count + 1` (atomic) |

---

## Distributed System Races

Race conditions amplified by network latency and partial failures.

```text
Common distributed races:
1. Split-brain: Two nodes think they are the leader
   Fix: Fencing tokens, distributed consensus (Raft/Paxos)

2. Stale cache: Cache updated before database write propagates
   Fix: Cache invalidation + short TTL, event-driven cache update

3. Event ordering: Events arrive out of order across services
   Fix: Sequence numbers, vector clocks, event sourcing

4. Distributed lock expiry: Lock TTL expires while holding work
   Fix: Lock extension (watchdog), fencing tokens

5. Idempotency failure: Retry creates duplicate side effects
   Fix: Idempotency keys, exactly-once processing
```

---

## Prevention Patterns

| Pattern | When to Use | Overhead |
|---------|------------|---------|
| Immutable data | Shared read-only state | Low |
| Message passing (channels) | Goroutines, actors | Low-medium |
| Mutex/Lock | Protecting critical sections | Medium |
| Atomic operations | Simple counters, flags | Low |
| STM (Software Transactional Memory) | Complex shared state (Clojure, Haskell) | Medium |
| Actor model (Akka, Erlang) | Isolated concurrent entities | Medium |
| Database transactions | Data integrity across operations | Medium-high |
| Optimistic locking | Low-contention updates | Low |
| Pessimistic locking (FOR UPDATE) | High-contention critical data | High |

---

## Testing Concurrent Code

### Deterministic Concurrency Testing

```python
import pytest
import threading
import time

def test_counter_thread_safety():
    """Verify counter is correct under concurrent access."""
    counter = ThreadSafeCounter()
    n_threads = 20
    n_increments = 10000
    barrier = threading.Barrier(n_threads)

    def worker():
        barrier.wait()
        for _ in range(n_increments):
            counter.increment()

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = n_threads * n_increments
    assert counter.value == expected, (
        f"Race condition: expected {expected}, got {counter.value}"
    )

def test_no_deadlock_with_timeout():
    """Verify operation completes without deadlock."""
    result = [None]
    def worker():
        result[0] = perform_concurrent_operation()

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=10.0)  # 10 second timeout

    assert not t.is_alive(), "Operation deadlocked (thread still alive)"
    assert result[0] is not None, "Operation did not complete"
```

---

## Race Condition Diagnosis Checklist

- [ ] Shared mutable state identified across all threads/coroutines
- [ ] Thread sanitizer or race detector run against codebase
- [ ] Stress tests execute concurrent operations (50+ threads, 1000+ iterations)
- [ ] Delay injection used to widen race windows during testing
- [ ] Database queries use appropriate locking (FOR UPDATE, atomic updates)
- [ ] Async/await code reviewed for shared state across yield points
- [ ] Lock ordering documented and enforced (deadlock prevention)
- [ ] All read-modify-write sequences protected by locks or atomic ops
- [ ] TOCTOU patterns replaced with atomic check-and-act
- [ ] Distributed system operations are idempotent
- [ ] Optimistic or pessimistic concurrency control used at data layer
- [ ] Concurrent test suite runs in CI

---

## Related Resources

- **[debugging-methodologies.md](debugging-methodologies.md)** - General debugging approaches
- **[memory-leak-detection.md](memory-leak-detection.md)** - Memory profiling and leak detection
- **[distributed-debugging.md](distributed-debugging.md)** - Cross-service debugging
- **[production-debugging-patterns.md](production-debugging-patterns.md)** - Production diagnostics
- **[SKILL.md](../SKILL.md)** - QA Debugging skill overview
