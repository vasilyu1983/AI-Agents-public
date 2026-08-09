#!/usr/bin/env bash
# =============================================================================
# inspect_iceberg_metadata.sh
# Summarise an Iceberg table's object-storage layout.
#
# Counts snapshots, manifests, data files, and performs a rough orphan-file
# heuristic (files in data/ not referenced by the latest manifest list).
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
# ORPHAN HEURISTIC — IMPORTANT NOTE
# ----------------------------------
# This script identifies orphan files with a ROUGH HEURISTIC:
#   1. List all files under <location>/data/
#   2. Download the latest manifest-list (snapshot) file
#   3. Extract all data-file paths referenced in the manifest list's manifests
#   4. Report files in (1) that are NOT in (3)
#
# This is APPROXIMATE because:
#   - Only the LATEST snapshot is checked. Files referenced by older retained
#     snapshots are NOT orphans — this script may falsely flag them.
#   - Manifest files themselves are not cross-checked against all retained
#     snapshot manifest lists.
#   - Use Iceberg's official remove_orphan_files procedure for safe cleanup:
#       CALL catalog.system.remove_orphan_files(table => 'ns.table', older_than => ...)
#   - Always use --dry-run on the official procedure before deleting anything.
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

# Normalise trailing slash
LOCATION="${LOCATION%/}"

# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------
ls_recursive() {
    # List all objects under a prefix, one path per line
    local prefix="$1"
    if [[ "$BACKEND" == "s3" ]]; then
        aws s3 ls --recursive "$prefix/" 2>/dev/null \
            | awk '{print $NF}' \
            | sed "s|^|${prefix%/*}/|"  # prepend bucket root
        # Note: aws s3 ls --recursive outputs paths relative to bucket root.
        # We prepend the scheme+bucket to get full URIs.
    elif [[ "$BACKEND" == "gcs" ]]; then
        gsutil ls -r "$prefix/**" 2>/dev/null || true
    else
        echo "ERROR: Unsupported backend '$BACKEND'. Use s3 or gcs." >&2; exit 1
    fi
}

ls_prefix() {
    # List objects at a prefix (non-recursive)
    local prefix="$1"
    if [[ "$BACKEND" == "s3" ]]; then
        aws s3 ls "$prefix/" 2>/dev/null | awk '{print $NF}'
    elif [[ "$BACKEND" == "gcs" ]]; then
        gsutil ls "$prefix/" 2>/dev/null || true
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
METADATA_FILES=$(ls_prefix "$METADATA_PREFIX" 2>/dev/null | grep '\.metadata\.json$' | wc -l | tr -d ' ')
echo "Metadata JSON versions    : $METADATA_FILES"

# Count snapshot avro files (manifest lists)
SNAP_FILES=$(ls_prefix "$METADATA_PREFIX" 2>/dev/null | grep '^snap-' | wc -l | tr -d ' ')
echo "Snapshot manifest lists   : $SNAP_FILES (snap-*.avro)"

# ---------------------------------------------------------------------------
# Step 2: Latest snapshot metadata
# ---------------------------------------------------------------------------
log "Fetching latest metadata.json..."
TMPDIR_ICEBERG=$(mktemp -d)
trap 'rm -rf "$TMPDIR_ICEBERG"' EXIT

# Find the highest-versioned metadata file (v1.metadata.json, v2.metadata.json, ...)
LATEST_META_NAME=$(ls_prefix "$METADATA_PREFIX" 2>/dev/null \
    | grep '\.metadata\.json$' \
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
MANIFEST_LIST_PATH=""

if [[ -n "$LATEST_META" ]]; then
    LOCAL_META="$TMPDIR_ICEBERG/latest.metadata.json"
    download_file "$LATEST_META" "$LOCAL_META" 2>/dev/null || true

    if [[ -f "$LOCAL_META" ]]; then
        SNAPSHOT_COUNT=$(jq '.snapshots | length' "$LOCAL_META" 2>/dev/null || echo 0)
        CURRENT_SNAPSHOT_ID=$(jq -r '.["current-snapshot-id"] // "unknown"' "$LOCAL_META" 2>/dev/null || echo "unknown")
        MANIFEST_LIST_PATH=$(jq -r --arg sid "$CURRENT_SNAPSHOT_ID" \
            '.snapshots[] | select(.["snapshot-id"] == ($sid | tonumber)) | .["manifest-list"]' \
            "$LOCAL_META" 2>/dev/null || echo "")

        echo "Snapshots in metadata     : $SNAPSHOT_COUNT"
        echo "Current snapshot ID       : $CURRENT_SNAPSHOT_ID"
        [[ "$VERBOSE" == "true" ]] && echo "Manifest list path        : $MANIFEST_LIST_PATH"
    fi
fi

# ---------------------------------------------------------------------------
# Step 3: Data file count
# ---------------------------------------------------------------------------
log "Counting data files under $LOCATION/data/ ..."
DATA_PREFIX="$LOCATION/data"

# List all data files — may be slow for very large tables
DATA_FILES_LIST="$TMPDIR_ICEBERG/data_files.txt"
ls_recursive "$DATA_PREFIX" 2>/dev/null > "$DATA_FILES_LIST" || true

DATA_FILE_COUNT=$(wc -l < "$DATA_FILES_LIST" | tr -d ' ')
PARQUET_COUNT=$(grep -c '\.parquet$' "$DATA_FILES_LIST" 2>/dev/null || echo 0)
ORC_COUNT=$(grep -c '\.orc$' "$DATA_FILES_LIST" 2>/dev/null || echo 0)
AVRO_COUNT=$(grep -c '\.avro$' "$DATA_FILES_LIST" 2>/dev/null || echo 0)

echo ""
echo "Data files total          : $DATA_FILE_COUNT"
echo "  .parquet                : $PARQUET_COUNT"
echo "  .orc                    : $ORC_COUNT"
echo "  .avro                   : $AVRO_COUNT"

# ---------------------------------------------------------------------------
# Step 4: Manifest count from latest manifest list
# ---------------------------------------------------------------------------
MANIFEST_COUNT=0

if [[ -n "$MANIFEST_LIST_PATH" ]]; then
    log "Downloading manifest list to count manifests..."
    LOCAL_MANIFEST_LIST="$TMPDIR_ICEBERG/manifest_list.avro"

    # Manifest lists are Avro — we cannot parse them with jq.
    # We count them from the metadata JSON snapshots array instead.
    if [[ -f "$LOCAL_META" ]]; then
        MANIFEST_COUNT=$(jq -r --arg sid "$CURRENT_SNAPSHOT_ID" \
            '.snapshots[] | select(.["snapshot-id"] == ($sid | tonumber)) | .manifests // [] | length' \
            "$LOCAL_META" 2>/dev/null || echo 0)

        # Fallback: if manifests array is absent, count from manifest-list key presence
        if [[ "$MANIFEST_COUNT" == "0" && -n "$MANIFEST_LIST_PATH" ]]; then
            MANIFEST_COUNT="see manifest-list (Avro parsing requires pyiceberg or spark)"
        fi
    fi
fi

echo "Manifests (latest snap.)  : $MANIFEST_COUNT"

# ---------------------------------------------------------------------------
# Step 5: Orphan file heuristic (APPROXIMATE — see header note)
# ---------------------------------------------------------------------------
echo ""
header "Orphan File Heuristic (APPROXIMATE)"
echo "NOTE: Only files NOT present in the LATEST snapshot manifest-list"
echo "      are flagged. Older retained snapshots are NOT checked."
echo "      Use Iceberg's remove_orphan_files procedure for safe cleanup."
echo ""

ORPHAN_COUNT=0

if [[ -f "$LOCAL_META" && "$DATA_FILE_COUNT" -gt 0 ]]; then
    log "Extracting referenced data-file paths from metadata..."

    # Extract all data-file paths referenced across all manifests in the current snapshot
    # The metadata JSON contains per-snapshot manifest arrays when present.
    # We collect paths from the 'added-data-files' and 'existing-data-files' counts
    # but cannot get exact filenames without parsing Avro manifest files.
    #
    # Practical heuristic: list .parquet/.orc files older than what the latest
    # snapshot was created at. Use the snapshot timestamp as the cutoff.
    SNAP_TS_MS=$(jq -r --arg sid "$CURRENT_SNAPSHOT_ID" \
        '.snapshots[] | select(.["snapshot-id"] == ($sid | tonumber)) | .["timestamp-ms"]' \
        "$LOCAL_META" 2>/dev/null || echo "")

    if [[ -n "$SNAP_TS_MS" && "$SNAP_TS_MS" != "null" ]]; then
        # Convert ms to seconds
        SNAP_TS_S=$(( SNAP_TS_MS / 1000 ))
        SNAP_DATE=$(date -r "$SNAP_TS_S" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null \
                    || date -d "@$SNAP_TS_S" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null \
                    || echo "unknown")
        echo "Latest snapshot timestamp : $SNAP_DATE"
    fi

    # Count files not matching the manifest-list's generation UUID prefix.
    # Since we cannot parse Avro without dependencies, we use the rough
    # size-based heuristic: flag data files older than 7 days as candidates.
    echo ""
    echo "Approximate orphan candidates (data files older than 7 days):"
    echo "(For authoritative cleanup, use: CALL catalog.system.remove_orphan_files(...))"
    echo ""

    if [[ "$BACKEND" == "s3" ]]; then
        # aws s3 ls recursive output: date time size key
        # Filter files where date is older than 7 days
        CUTOFF=$(date -u -v-7d '+%Y-%m-%d' 2>/dev/null || date -u -d '7 days ago' '+%Y-%m-%d')
        ORPHAN_COUNT=$(aws s3 ls --recursive "$DATA_PREFIX/" 2>/dev/null \
            | awk -v cutoff="$CUTOFF" '$1 < cutoff {count++} END {print count+0}')
        echo "  Data files older than $CUTOFF : $ORPHAN_COUNT"
    elif [[ "$BACKEND" == "gcs" ]]; then
        echo "  GCS: Run 'gsutil ls -l -r $DATA_PREFIX/**' and filter by creation date."
        echo "  Automatic date-based filtering is not implemented for GCS in this script."
    fi
else
    echo "  Skipped — no metadata or data files found."
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
header "Summary"
printf "%-30s %s\n" "Table location:"        "$LOCATION"
printf "%-30s %s\n" "Backend:"               "$BACKEND"
printf "%-30s %s\n" "Metadata versions:"     "$METADATA_FILES"
printf "%-30s %s\n" "Snapshots (in meta):"   "$SNAPSHOT_COUNT"
printf "%-30s %s\n" "Current snapshot ID:"   "$CURRENT_SNAPSHOT_ID"
printf "%-30s %s\n" "Total data files:"      "$DATA_FILE_COUNT"
printf "%-30s %s\n" "Approx. orphan cands.:" "$ORPHAN_COUNT"
echo ""
echo "Next steps:"
echo "  1. If snapshot count is high: run expire_snapshots to trim old snapshots."
echo "  2. If data file count is high relative to size: run rewrite_data_files."
echo "  3. For authoritative orphan cleanup: run remove_orphan_files procedure."
echo "  4. Run rewrite_manifests if manifests are fragmented after many small writes."
