# The Practice of Programming Operational Checklist

Concrete habits from Kernighan & Pike for robust, clear programs.

## Design and Interfaces
- Keep interfaces small, orthogonal, and predictable; avoid optional params/flags when a separate function is clearer.
- Choose simple data representations first; convert to richer structures only when needed.
- Separate mechanism from policy; isolate IO and environment details from core logic.

## Coding Style and Readability
- Prefer clear, consistent formatting; one idea per line; keep line length reasonable.
- Use descriptive names and comments for intent or constraints; delete redundant comments and dead code.
- Replace magic numbers/strings with named constants; document units and assumptions.

## Defensive Coding
- Validate inputs and outputs; check error returns and exceptional conditions immediately.
- Handle resources deterministically: close/free in the same scope; guard against leaks.
- Avoid hidden state and side effects; keep functions pure where possible.

## Algorithms and Data
- Pick algorithms and structures for correctness first, then simplicity, then performance.
- Avoid premature optimization; measure before tuning and after changes.
- Use assertions to document invariants; fail fast with actionable messages.

## Debugging and Testing
- Reproduce bugs, simplify the failing case, and add a test that fails before the fix.
- Use binary search/printf/logging to isolate faults; change one variable at a time.
- Build regression tests for each fixed bug; keep tests deterministic and fast.

## Performance Tuning
- Profile to find hot spots; optimize only where measurements show value.
- Prefer algorithmic improvements over micro-optimizations; keep tuned code documented and tested.

## Portability and Robustness
- Avoid non-portable assumptions (endianness, path separators, locale/timezone quirks).
- Check boundary conditions: null/empty, off-by-one, overflow/underflow, encoding.
- Log key decisions and failures with enough context to debug without rerunning.***
