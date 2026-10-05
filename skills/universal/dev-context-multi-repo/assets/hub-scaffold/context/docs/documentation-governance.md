# Documentation Governance

> Template stub. The placement gate every new markdown file must pass
> before it is created. This is what keeps the compiled layer from
> rotting into one-off files.

## Placement test

Before creating a new markdown file, answer:

1. Does this belong in an existing catalog page, domain doc, or report?
2. Will it be linked from an index or domain README?
3. Is it generated from structured inputs? If so, is the rebuild command
   recorded in the file?
4. If it is a point-in-time analysis, does it carry a lifecycle state?

If you cannot answer all four, **do not create the file** — update the
closest canonical doc or keep the result in the task thread.

## Layer ownership

| Layer | Files | Who edits |
|-------|-------|-----------|
| Hot | `AGENTS.md`, `rules/` | Humans |
| Compiled | `context/docs/`, `&lt;domain&gt;/`, catalog pages | LLM, human-reviewed |
| Generated | `context/graphs/`, `context/overview/` | Pipeline scripts only |
| Reports | `context/reports/` | LLM, dated + lifecycle-tagged |

## Lifecycle states for reports

`draft` → `current` → `superseded`. A superseded report links its
successor; it is not deleted (the timeline matters).
