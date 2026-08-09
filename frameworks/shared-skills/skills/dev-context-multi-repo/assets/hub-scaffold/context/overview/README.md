# context/overview — generated cross-cutting maps

Index of portfolio-wide artifacts the pipeline generates. These are
**derived**: regenerate them, do not hand-edit. Keep this index current as
maps are added.

| Artifact | What it is | Generator |
|----------|-----------|-----------|
| `api-catalog.md` | Every API contract across repos | `../scripts/generate-api-catalog.sh` |
| `integration-matrix.md` | Producer ↔ consumer edge table | `dev-context-multi-repo` (system-edges) |
| `dependency-map.md` | Cross-repo package/dependency map | `dev-context-multi-repo` (profiles) |
| `full-system-diagram.md` | Mermaid of the whole portfolio graph | `query_graph.py --diagram` |
| `platform-summary.md` | The platform in one generated page | knowledge-graph + profiles |

> Add a row whenever a new generated map lands. Each artifact must name
> its rebuild command in its own header (see
> `../docs/documentation-governance.md`).

`.gitkeep` keeps this folder under version control while empty.
