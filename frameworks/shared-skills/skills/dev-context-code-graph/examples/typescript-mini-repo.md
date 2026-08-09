# TypeScript Mini Repo Example

Input repo:

- `src/math.ts` exports `sum()`
- `src/app.ts` imports `sum()` and calls it
- `src/app.test.ts` imports `runApp()` and asserts behavior

Expected outputs:

- file and function nodes for all three files
- local `imports` edges between files
- `calls` edges from `runApp` to `sum`
- `tests` edges from the test symbol to `runApp`
