#!/usr/bin/env bash
# =============================================================================
# inspect_iceberg_metadata.sh
# Summarise an Iceberg table's object-storage layout.
#
# Counts metadata versions and object files. Catalog metadata is authoritative
# for the current snapshot; this object listing cannot identify orphan files.
#
# DEPENDENCIES
# ------------
#   aws  — AWS CLI v2 (for --backend s3)
#   gsutil or gcloud storage — Google Cloud SDK (for --backend gcs)
#   jq   — JSON processor (brew install jq / apt-get install jq)
#
# USAGE
# -----
#   # S3 table:
#   ./inspect_iceberg_metadata.sh \
#       --location s3://my-bucket/warehouse/analytics/events \
#       --backend s3
#
#   # GCS table:
#   ./inspect_iceberg_metadata.sh \
#       --location gs://my-bucket/warehouse/analytics/events \
#       --backend gcs
#
# For orphan candidates, use Iceberg's remove_orphan_files procedure with
# dry_run => true. It compares storage with table metadata, including retained
# snapshots; file age by itself does not establish orphan status.
#
# AUTHENTICATION
# --------------
#   S3:  aws configure (or AWS_PROFILE / AWS_ACCESS_KEY_ID env vars)
#   GCS: gcloud auth application-default login
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
LOCATION=""
BACKEND="s3"
VERBOSE=false

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
usage() {
    grep '^#' "$0" | grep -v '^#!/' | sed 's/^# \{0,1\}//'
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --location)
            LOCATION="$2"; shift 2 ;;
        --backend)
            BACKEND="$2"; shift 2 ;;
        --verbose|-v)
            VERBOSE=true; shift ;;
        --help|-h)
            usage ;;
        *)
            echo "Unknown argument: $1" >&2; usage ;;
    esac
done

if [[ -z "$LOCATION" ]]; then
    echo "ERROR: --location is required." >&2
    usage
fi

if [[ "$BACKEND" != "s3" && "$BACKEND" != "gcs" ]]; then
    echo "ERROR: --backend must be s3 or gcs." >&2; exit 1
fi
EXPECTED_SCHEME="$BACKEND"
[[ "$BACKEND" == "gcs" ]] && EXPECTED_SCHEME="gs"
if [[ "$LOCATION" != "$EXPECTED_SCHEME"://* ]]; then
    echo "ERROR: --location must use the $EXPECTED_SCHEME:// scheme." >&2; exit 1
fi
if ! command -v jq >/dev/null; then
    echo "ERROR: jq is required." >&2; exit 1
fi

# Normalise trailing slash
LOCATION="${LOCATION%/}"

# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------
ls_recursive() {
    # List all objects under a prefix, one path per line
    local prefix="$1"
    if [[ "$BACKEND" == "s3" ]]; then
        aws s3 ls --recursive "$prefix/" | awk '{print $NF}'
    elif [[ "$BACKEND" == "gcs" ]]; then
        gsutil ls -r "$prefix/**"
    else
        echo "ERROR: Unsupported backend '$BACKEND'. Use s3 or gcs." >&2; exit 1
    fi
}

ls_prefix() {
    # List objects at a prefix (non-recursive)
    local prefix="$1"
    if [[ "$BACKEND" == "s3" ]]; then
        aws s3 ls "$prefix/" | awk '{print $NF}'
    elif [[ "$BACKEND" == "gcs" ]]; then
        gsutil ls "$prefix/"
    fi
}

download_file() {
    # Download a remote file to a local path
    local remote="$1"
    local local_path="$2"
    if [[ "$BACKEND" == "s3" ]]; then
        aws s3 cp "$remote" "$local_path" --quiet
    elif [[ "$BACKEND" == "gcs" ]]; then
        gsutil cp -q "$remote" "$local_path"
    fi
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() {
    echo "[$(date -u '+%H:%M:%S')] $*" >&2
}

header() {
    echo ""
    echo "============================================================"
    echo "  $*"
    echo "============================================================"
}

# ---------------------------------------------------------------------------
# Step 1: Snapshot count (metadata/snap-*.avro or metadata/v*.metadata.json)
# ---------------------------------------------------------------------------
header "Iceberg Table: $LOCATION"
echo "Backend : $BACKEND"
echo ""

METADATA_PREFIX="$LOCATION/metadata"

log "Listing metadata files..."

# Count metadata.json files (each generation = one table version)
METADATA_LIST=$(ls_prefix "$METADATA_PREFIX") || { echo "ERROR: metadata listing failed." >&2; exit 1; }
METADATA_FILES=$(printf '%s\n' "$METADATA_LIST" | awk '/\.metadata\.json$/ {n++} END {print n+0}')
if [[ "$METADATA_FILES" -eq 0 ]]; then
    echo "ERROR: no metadata JSON files found; cannot inspect table." >&2; exit 1
fi
echo "Metadata JSON versions    : $METADATA_FILES"

# Count snapshot avro files (manifest lists)
SNAP_FILES=$(printf '%s\n' "$METADATA_LIST" | awk '/(^|\/)snap-/ {n++} END {print n+0}')
echo "Snapshot manifest lists   : $SNAP_FILES (snap-*.avro)"

# ---------------------------------------------------------------------------
# Step 2: Highest-named metadata file (not necessarily catalog-current)
# ---------------------------------------------------------------------------
log "Fetching highest-named metadata.json candidate; confirm the current file in the catalog..."
TMPDIR_ICEBERG=$(mktemp -d)
trap 'rm -rf "$TMPDIR_ICEBERG"' EXIT

# Find the highest-versioned metadata file (v1.metadata.json, v2.metadata.json, ...)
LATEST_META_NAME=$(printf '%s\n' "$METADATA_LIST" \
    | awk '/\.metadata\.json$/' \
    | sort -V \
    | tail -1)

LATEST_META=""
if [[ -n "$LATEST_META_NAME" ]]; then
    # ls_prefix returns just the filename for s3, full path for gcs
    if [[ "$BACKEND" == "s3" ]]; then
        LATEST_META="$METADATA_PREFIX/$LATEST_META_NAME"
    else
        LATEST_META="$LATEST_META_NAME"
    fi
fi

SNAPSHOT_COUNT=0
CURRENT_SNAPSHOT_ID=""

if [[ -n "$LATEST_META" ]]; then
    LOCAL_META="$TMPDIR_ICEBERG/latest.metadata.json"
    download_file "$LATEST_META" "$LOCAL_META" || { echo "ERROR: metadata download failed." >&2; exit 1; }
    # The Iceberg spec makes snapshots and current-snapshot-id optional for a
    # newly created table; reject wrong present types without inventing a row.
    jq -e --arg location "$LOCATION" 'type == "object" and
        (. ["format-version"] | type == "number") and .location == $location and
        ((.snapshots // []) | type == "array") and
        (. ["current-snapshot-id"] == null or (. ["current-snapshot-id"] | type) == "number")' \
        "$LOCAL_META" >/dev/null || { echo "ERROR: invalid Iceberg metadata JSON." >&2; exit 1; }

    SNAPSHOT_COUNT=$(jq -er '(.snapshots // []) | length' "$LOCAL_META") || { echo "ERROR: invalid snapshot list." >&2; exit 1; }
    CURRENT_SNAPSHOT_ID=$(jq -er 'if .["current-snapshot-id"] == null or .["current-snapshot-id"] == -1 then "none" else .["current-snapshot-id"] end' "$LOCAL_META") || { echo "ERROR: invalid snapshot ID." >&2; exit 1; }

    echo "Snapshots in candidate    : $SNAPSHOT_COUNT"
    echo "Candidate snapshot ID     : $CURRENT_SNAPSHOT_ID"
    if [[ "$VERBOSE" == "true" ]]; then
        echo "Candidate metadata file   : $LATEST_META"
    fi
fi

# ---------------------------------------------------------------------------
# Step 3: Data file count
# ---------------------------------------------------------------------------
log "Counting data files under $LOCATION/data/ ..."
DATA_PREFIX="$LOCATION/data"

# List all data files — may be slow for very large tables
DATA_FILES_LIST="$TMPDIR_ICEBERG/data_files.txt"
ls_recursive "$DATA_PREFIX" > "$DATA_FILES_LIST" || { echo "ERROR: data listing failed; counts are unavailable." >&2; exit 1; }

DATA_FILE_COUNT=$(wc -l < "$DATA_FILES_LIST" | tr -d ' ')
PARQUET_COUNT=$(awk '/\.parquet$/ {n++} END {print n+0}' "$DATA_FILES_LIST")
ORC_COUNT=$(awk '/\.orc$/ {n++} END {print n+0}' "$DATA_FILES_LIST")
AVRO_COUNT=$(awk '/\.avro$/ {n++} END {print n+0}' "$DATA_FILES_LIST")

echo ""
echo "Data files total          : $DATA_FILE_COUNT"
echo "  .parquet                : $PARQUET_COUNT"
echo "  .orc                    : $ORC_COUNT"
echo "  .avro                   : $AVRO_COUNT"

# A storage listing cannot distinguish live files from files retained by older
# snapshots. Ask Iceberg to compare all referenced metadata before cleanup.

echo ""
echo "Orphan candidates          : unverified (requires Iceberg metadata comparison)"
echo "Use: CALL catalog.system.remove_orphan_files(table => 'ns.table', dry_run => true);"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
header "Summary"
printf "%-30s %s\n" "Table location:"        "$LOCATION"
printf "%-30s %s\n" "Backend:"               "$BACKEND"
printf "%-30s %s\n" "Metadata versions:"     "$METADATA_FILES"
printf "%-30s %s\n" "Snapshots (candidate):"  "$SNAPSHOT_COUNT"
printf "%-30s %s\n" "Candidate snapshot ID:"  "$CURRENT_SNAPSHOT_ID"
printf "%-30s %s\n" "Total data files:"      "$DATA_FILE_COUNT"
echo ""
echo "Next steps:"
echo "  1. If snapshot count is high: run expire_snapshots to trim old snapshots."
echo "  2. If data file count is high relative to size: run rewrite_data_files."
echo "  3. For orphan candidates: run remove_orphan_files with dry_run => true."
echo "  4. Run rewrite_manifests if manifests are fragmented after many small writes."
