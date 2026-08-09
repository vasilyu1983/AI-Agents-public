#!/usr/bin/env bash
# Build the infra-free vector-hub artifact set from a compiled context/repo hub.
# Produces inventory.jsonl, documents.jsonl, chunks.jsonl, brain-manifest.json.
# It does NOT embed or load — that needs Postgres+pgvector and a provider key;
# the embed/load command is printed at the end.
#
# Usage: build_vector_hub.sh <hub_root> <out_dir> [source_id] [corpus_type]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -lt 2 ]; then
  echo "usage: build_vector_hub.sh <hub_root> <out_dir> [source_id] [corpus_type]" >&2
  exit 2
fi

HUB="$1"
OUT="$2"
SOURCE_ID="${3:-hub}"
CORPUS_TYPE="${4:-docs}"

if [ ! -d "$HUB" ]; then
  echo "ERROR: hub_root '$HUB' is not a directory" >&2
  exit 1
fi

INDEXABLE_COUNT="$(find "$HUB" \( \
  -name '*.md' -o -name '*.mdx' -o -name '*.txt' -o \
  -name '*.json' -o -name '*.yaml' -o -name '*.yml' -o \
  -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o \
  -name '*.sql' \
  \) -type f | wc -l | tr -d ' ')"
if [ "$INDEXABLE_COUNT" -eq 0 ]; then
  echo "ERROR: no indexable context files under '$HUB' — nothing to build" >&2
  exit 1
fi

mkdir -p "$OUT"

echo "[1/4] inventory ($INDEXABLE_COUNT indexable files)" >&2
python3 "$SCRIPT_DIR/inventory_corpus.py" "$HUB" --source-id "$SOURCE_ID" > "$OUT/inventory.jsonl"

echo "[2/4] prepare documents (metadata preserved)" >&2
python3 "$SCRIPT_DIR/prepare_documents.py" "$OUT/inventory.jsonl" \
  --corpus-type "$CORPUS_TYPE" > "$OUT/documents.jsonl"

# --max-tokens is passed explicitly so the manifest matches reality and does
# not drift with the script default. chunk_corpus_files.py measures words, not
# BPE tokens. Markdown uses parent-child context; non-Markdown files use stable
# line anchors. There is no sliding overlap.
echo "[3/4] chunk corpus files (markdown parent-child + repo artifacts, --max-tokens 512)" >&2
python3 "$SCRIPT_DIR/chunk_corpus_files.py" "$HUB" --unit parent_child --max-tokens 512 > "$OUT/chunks.jsonl"

echo "[4/4] emit + validate manifest scaffold" >&2
HUB="$HUB" OUT="$OUT" CORPUS_TYPE="$CORPUS_TYPE" SOURCE_ID="$SOURCE_ID" python3 - <<'PY'
import json, os
m = {
    "brain_id": os.environ["SOURCE_ID"],
    "backend": "postgres_pgvector",
    "corpus_type": os.environ["CORPUS_TYPE"],
    "embedding_model": "openai/text-embedding-3-small@1024",
    "source_roots": [os.environ["HUB"]],
    "chunking": {"unit": "mixed_parent_child_line_bounded", "max_tokens": 512, "token_unit": "word_estimate", "context": "markdown parent-child; structured/code/sql/text line-bounded"},
    "retrieval": {"mode": "graph_bounded_hybrid", "top_k": 10, "candidates": 50, "rerank": True},
    "freshness": {"strategy": "git_anchored_incremental", "idempotency": "content_hash", "on_delete": "tombstone"},
    "eval": {"seed": "build_eval_seed.py", "gates": ["path_recall@10", "stale_commit_detection"]},
}
open(os.path.join(os.environ["OUT"], "brain-manifest.json"), "w").write(json.dumps(m, indent=2))
PY
python3 "$SCRIPT_DIR/check_brain_manifest.py" "$OUT/brain-manifest.json" >&2

cat >&2 <<EOF

Artifacts written to: $OUT
  inventory.jsonl  documents.jsonl  chunks.jsonl  brain-manifest.json

Next (needs Postgres+pgvector, psycopg, and an embedding-provider key):
  psql "\$DATABASE_URL" -f "$SCRIPT_DIR/../assets/sql/001_schema.sql"   # + 002..00N
  python3 "$SCRIPT_DIR/embed_and_load.py" "$OUT/chunks.jsonl" \\
    --provider openai --model text-embedding-3-small --dim 1024 \\
    --source-id "$SOURCE_ID" --doc-type "$CORPUS_TYPE"

The bundled SQL assets default to 1024-dimensional embeddings. If you choose a
different dimension, update every vector(N)/bit(N) occurrence in assets/sql
before loading data.
EOF
