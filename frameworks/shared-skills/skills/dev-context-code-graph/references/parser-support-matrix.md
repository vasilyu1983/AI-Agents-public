# Parser Support Matrix

| Language | Strategy | Symbol support | Import support | Call support | Notes |
|----------|----------|----------------|----------------|--------------|-------|
| Python | `ast` | Strong | Strong | Strong | Preferred v1 parser |
| JavaScript | Heuristic | Medium | Strong | Medium | Regex-backed extraction |
| TypeScript | Heuristic | Medium | Strong | Medium | Handles common import and function patterns |
| TSX | Heuristic | Medium | Strong | Medium | Treats component functions as functions |
| C# | Heuristic | Medium | Medium | Medium | Extracts common class and method shapes |
| Swift | Heuristic | Medium | Medium | Medium | Extracts top-level types, functions, imports, and inheritance/protocol edges while skipping generated Apple build trees |
| Other | File-only | None | None | None | Emit `unsupported` parse status |

Rules:

- Unsupported languages still emit `file` nodes.
- Unsupported files must be labeled with `parse_status: unsupported`.
- Heuristic parsers must use lower confidence than AST-backed extraction.

For the staged plan to upgrade the heuristic languages to tree-sitter while keeping Python on `ast`, see [tree-sitter-migration-plan.md](tree-sitter-migration-plan.md).
