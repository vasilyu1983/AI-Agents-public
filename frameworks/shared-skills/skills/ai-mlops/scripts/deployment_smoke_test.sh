#!/usr/bin/env bash
# deployment_smoke_test.sh — Shadow/canary deployment smoke verifier
#
# Runs a suite of fast HTTP health and inference checks against a shadow or
# canary endpoint to verify a deployment before it receives live traffic.
#
# Usage:
#   ./deployment_smoke_test.sh --endpoint http://localhost:8000 --model my-model
#   ./deployment_smoke_test.sh --endpoint http://shadow:8000 --model gpt-4o-mini \
#       --api-key $OPENAI_API_KEY --rounds 3
#   ./deployment_smoke_test.sh --help
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed
#   2 — missing required arguments

set -euo pipefail

# --------------------------------------------------------------------------
# Defaults
# --------------------------------------------------------------------------
ENDPOINT=""
MODEL=""
API_KEY="${OPENAI_API_KEY:-}"
ROUNDS=1
TIMEOUT=30
MAX_LATENCY_MS=5000
VERBOSE=false
OUTPUT_FILE=""

# --------------------------------------------------------------------------
# Parse args
# --------------------------------------------------------------------------
usage() {
  grep '^#' "$0" | sed 's/^# \?//' | head -40
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --endpoint)   ENDPOINT="$2"; shift 2 ;;
    --model)      MODEL="$2"; shift 2 ;;
    --api-key)    API_KEY="$2"; shift 2 ;;
    --rounds)     ROUNDS="$2"; shift 2 ;;
    --timeout)    TIMEOUT="$2"; shift 2 ;;
    --max-latency-ms) MAX_LATENCY_MS="$2"; shift 2 ;;
    --output)     OUTPUT_FILE="$2"; shift 2 ;;
    --verbose|-v) VERBOSE=true; shift ;;
    --help|-h)    usage ;;
    *) echo "[ERROR] Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$ENDPOINT" || -z "$MODEL" ]]; then
  echo "[ERROR] --endpoint and --model are required." >&2
  exit 2
fi

BASE_URL="${ENDPOINT%/}"
PASS=0
FAIL=0
RESULTS=()

# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------
log() { [[ "$VERBOSE" == true ]] && echo "[INFO] $*" || true; }

check_pass() {
  local name="$1"
  PASS=$((PASS + 1))
  RESULTS+=("PASS|$name")
  echo "[PASS] $name"
}

check_fail() {
  local name="$1" reason="$2"
  FAIL=$((FAIL + 1))
  RESULTS+=("FAIL|$name|$reason")
  echo "[FAIL] $name — $reason"
}

auth_header() {
  if [[ -n "$API_KEY" ]]; then
    echo "Authorization: Bearer $API_KEY"
  else
    echo "X-No-Auth: true"
  fi
}

# --------------------------------------------------------------------------
# Check 1: Health endpoint
# --------------------------------------------------------------------------
run_health_check() {
  local url="$BASE_URL/health"
  log "GET $url"
  local status
  status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
  if [[ "$status" == "200" ]]; then
    check_pass "health-endpoint ($url)"
  else
    check_fail "health-endpoint" "HTTP $status from $url"
  fi
}

# --------------------------------------------------------------------------
# Check 2: Models list endpoint
# --------------------------------------------------------------------------
run_models_check() {
  local url="$BASE_URL/v1/models"
  log "GET $url"
  local body
  body=$(curl -sf --max-time "$TIMEOUT" \
    -H "$(auth_header)" \
    "$url" 2>/dev/null || echo "")
  if echo "$body" | grep -q "\"data\""; then
    check_pass "models-list ($url)"
  else
    check_fail "models-list" "No 'data' field in response from $url"
  fi
}

# --------------------------------------------------------------------------
# Check 3: Chat completions inference
# --------------------------------------------------------------------------
run_inference_check() {
  local round="$1"
  local url="$BASE_URL/v1/chat/completions"
  local payload
  payload=$(printf '{"model":"%s","messages":[{"role":"user","content":"Reply with the single word: HEALTHY"}],"max_tokens":10}' "$MODEL")

  local start_ms end_ms latency_ms
  start_ms=$(date +%s%3N 2>/dev/null || python3 -c "import time; print(int(time.time()*1000))")

  local body
  body=$(curl -sf --max-time "$TIMEOUT" \
    -X POST "$url" \
    -H "Content-Type: application/json" \
    -H "$(auth_header)" \
    -d "$payload" 2>/dev/null || echo "")

  end_ms=$(date +%s%3N 2>/dev/null || python3 -c "import time; print(int(time.time()*1000))")
  latency_ms=$((end_ms - start_ms))

  if [[ -z "$body" ]]; then
    check_fail "inference-round-$round" "Empty response from $url"
    return
  fi

  if ! echo "$body" | grep -q "\"choices\""; then
    check_fail "inference-round-$round" "No 'choices' in response"
    return
  fi

  if [[ "$latency_ms" -gt "$MAX_LATENCY_MS" ]]; then
    check_fail "inference-latency-round-$round" "${latency_ms}ms > threshold ${MAX_LATENCY_MS}ms"
  else
    check_pass "inference-round-$round (${latency_ms}ms)"
  fi
}

# --------------------------------------------------------------------------
# Check 4: Non-streaming response has finish_reason
# --------------------------------------------------------------------------
run_finish_reason_check() {
  local url="$BASE_URL/v1/chat/completions"
  local payload
  payload=$(printf '{"model":"%s","messages":[{"role":"user","content":"Say one word"}],"max_tokens":5}' "$MODEL")
  local body
  body=$(curl -sf --max-time "$TIMEOUT" \
    -X POST "$url" \
    -H "Content-Type: application/json" \
    -H "$(auth_header)" \
    -d "$payload" 2>/dev/null || echo "")

  if echo "$body" | grep -q "\"finish_reason\""; then
    check_pass "finish-reason-present"
  else
    check_fail "finish-reason-present" "Missing 'finish_reason' in response"
  fi
}

# --------------------------------------------------------------------------
# Run all checks
# --------------------------------------------------------------------------
echo "Smoke test: $BASE_URL  model=$MODEL  rounds=$ROUNDS"
echo "---"

run_health_check
run_models_check
run_finish_reason_check

for i in $(seq 1 "$ROUNDS"); do
  run_inference_check "$i"
done

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
TOTAL=$((PASS + FAIL))
echo ""
echo "Results: $PASS/$TOTAL passed"

if [[ -n "$OUTPUT_FILE" ]]; then
  {
    echo "{"
    echo "  \"endpoint\": \"$BASE_URL\","
    echo "  \"model\": \"$MODEL\","
    echo "  \"total\": $TOTAL,"
    echo "  \"passed\": $PASS,"
    echo "  \"failed\": $FAIL,"
    echo "  \"checks\": ["
    first=true
    for r in "${RESULTS[@]}"; do
      IFS='|' read -r status name reason <<< "$r"
      [[ "$first" == false ]] && echo "    ,"
      echo "    {\"status\":\"$status\",\"name\":\"$name\",\"reason\":\"${reason:-}\"}"
      first=false
    done
    echo "  ]"
    echo "}"
  } > "$OUTPUT_FILE"
  echo "Report written to: $OUTPUT_FILE"
fi

[[ "$FAIL" -eq 0 ]]
