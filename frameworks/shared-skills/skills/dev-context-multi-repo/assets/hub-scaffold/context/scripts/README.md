# context/scripts — pipeline runners

This folder holds **thin runners**. The heavy lifting lives in the three
`dev-context-*` skills. Do not copy the skill scripts here; point at them.

## Wiring

Install the three skills (e.g. into `.claude/skills/` of this hub, or any
path), then set:

```bash
export SKILLS=/path/to/skills            # contains dev-context-* folders
export CG="$SKILLS/dev-context-code-graph/scripts"
export MR="$SKILLS/dev-context-multi-repo/scripts"
export CE="$SKILLS/dev-context-engineering/scripts"
```

Clone the source repos next to this hub, e.g. `~/repos/<repo>`, and this
hub at `~/repos/requirements-hub`.

## Recreate the hub — end to end

```bash
# 0. from the hub root
cd ~/repos/requirements-hub

# 1. discover repos → context/graphs/repos.json
python3 "$MR/discover_repos.py" ~/repos --out context/graphs/repos.json

# 2. scan each repo into a normalized profile
python3 "$MR/scan_portfolio.py" --repos context/graphs/repos.json \
        --out context/graphs/

# 3. (optional, per repo) single-repo symbol graph for blast radius
python3 "$CG/scan_code_repo.py"  ~/repos/<repo> --out /tmp/<repo>.profile.json
python3 "$CG/build_code_graph.py" /tmp/<repo>.profile.json \
        --out ~/repos/<repo>/graphs/code-graph.json

# 4. build the cross-repo knowledge graph from profiles
python3 "$MR/build_knowledge_graph.py" --profiles context/graphs/ \
        --out context/graphs/knowledge-graph.json

# 5. sanity-query it (ranked central repos)
python3 "$MR/query_graph.py" context/graphs/knowledge-graph.json --rank

# 6. validate the knowledge graph (auto-repair with --fix)
python3 "$MR/validate_graph.py" context/graphs/knowledge-graph.json

# 7. build/validate THIS hub's own context graph (the dev-context-engineering
#    scripts are reused as-is — do not reimplement them here)
python3 "$CE/scan_context_artifacts.py" . \
        --output context/graphs/context-graph.json
python3 "$CE/validate_context_graph.py" context/graphs/context-graph.json --repo .
```

> **Expected on a blank hub:** `validate_context_graph.py` flags the root
> `AGENTS.md` as an `orphan` (one node, no edges) and exits non-zero. That
> is correct for an empty skeleton — the scanner is repo-native and only
> the hot-layer file exists yet. The orphan clears once you populate the
> hub: as catalog pages, profiles, and `.claude/rules/` (if you add a
> runtime layer) come in and cross-link, edges form. Do not restructure
> the hub to silence this on day one.

Then compile catalog pages from the profiles using the templates in
`../templates/` and the `dev-context-multi-repo` workflow. File generated
cross-cutting maps into `../overview/` and dated analyses into
`../reports/`.

## Local thin runners

- `sync-rules.sh` — copy the hub's `rules/` into each source repo (or a
  per-repo `AGENTS.md` pointer) so tools pick them up locally.
- `audit-agents.sh` — find `AGENTS.md`/`CLAUDE.md` across the portfolio and
  flag missing or stale ones.
- `generate-api-catalog.sh` — collect API contracts (OpenAPI/proto/etc.)
  across repos into a single catalog stub under `../overview/`.

All three are generic and safe to edit for your layout.
