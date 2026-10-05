# Component Discovery Patterns

This file used to hold per-language `find`/`grep` recipes (.NET, Node.js, Python, Go, Java,
React) for locating controllers, services, and models. That recipe list was generic base-model
knowledge and is superseded by [dev-context-code-graph](../../dev-context-code-graph/SKILL.md),
which builds and validates an actual code graph (callers, imports, entrypoints) instead of
pattern-matching file names.

For a documentation audit, discover what should exist from entrypoints, contracts, jobs, and
config — exclude `.archive/` — then use `dev-context-code-graph`'s graph artifacts, or your own
`grep`/`rg`/IDE search, to find the undocumented components.

A few judgment rules worth keeping here, since they are audit-specific rather than
graph-construction concerns:

1. **Start broad, then narrow**: begin with file patterns or entrypoints, then search for
   specific annotations, decorators, or route declarations.
2. **Check naming conventions**: adjust patterns to the project's actual casing and vocabulary
   (`Service` vs `service`, `Controller` vs `controller`) rather than assuming a convention.
3. **Search for interfaces too**: many projects define contracts in separate interface or type
   files that the implementation file's name won't surface.
4. **Look for tests**: test files often reveal components that were never documented.
5. **Check migrations**: database migration files reveal schema changes that may need a doc
   update even when no application code changed.

See also [audit-workflows.md](audit-workflows.md) for how to use discovery output in a
systematic audit, and [priority-framework.md](priority-framework.md) for how to rank what
discovery turns up.
