#!/usr/bin/env bash
# deployment_smoke_test.sh — Shadow/canary deployment smoke verifier
#
# Runs fast HTTP health and inference checks against a shadow or canary
# endpoint (OpenAI-compatible chat API) before it receives live traffic.
#
# Usage:
#   ./deployment_smoke_test.sh --endpoint http://localhost:8000 --model my-model
#   ./deployment_smoke_test.sh --endpoint http://shadow:8000 --model my-model \
#       --api-key "$API_KEY" --rounds 3
#   ./deployment_smoke_test.sh --help
#
# Checks: /health returns 200; /v1/models has a "data" list; a chat completion
# returns choices[0].message.content (a string) and choices[0].finish_reason
# (non-null), within --max-latency-ms. Responses are parsed as JSON (python3),
# not grepped. Portable on GNU and BSD/macOS (no `date +%N`).
#
# Fails closed: every expected check must report. A check that crashes or never
# reports counts as a failure, so the summary cannot say "all passed" for less.
#
# Exit codes:
#   0 — every expected check ran and passed
#   1 — a check failed or did not report
#   2 — bad arguments or missing python3

set -euo pipefail

ENDPOINT=""
MODEL=""
API_KEY="${OPENAI_API_KEY:-}"
ROUNDS=1
TIMEOUT=30
MAX_LATENCY_MS=5000
VERBOSE=false
OUTPUT_FILE=""

usage() {
  grep '^#' "$0" | sed -E 's/^# ?//' | head -30
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --endpoint)   ENDPOINT="${2:-}"; shift 2 ;;
    --model)      MODEL="${2:-}"; shift 2 ;;
    --api-key)    API_KEY="${2:-}"; shift 2 ;;
    --rounds)     ROUNDS="${2:-}"; shift 2 ;;
    --timeout)    TIMEOUT="${2:-}"; shift 2 ;;
    --max-latency-ms) MAX_LATENCY_MS="${2:-}"; shift 2 ;;
    --output)     OUTPUT_FILE="${2:-}"; shift 2 ;;
    --verbose|-v) VERBOSE=true; shift ;;
    --help|-h)    usage ;;
    *) echo "[ERROR] Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$ENDPOINT" || -z "$MODEL" ]]; then
  echo "[ERROR] --endpoint and --model are required." >&2
  exit 2
fi
for pair in "rounds:$ROUNDS" "timeout:$TIMEOUT" "max-latency-ms:$MAX_LATENCY_MS"; do
  if ! [[ "${pair#*:}" =~ ^[1-9][0-9]*$ ]]; then
    echo "[ERROR] --${pair%%:*} must be a positive integer, got '${pair#*:}'" >&2
    exit 2
  fi
done
if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is required to parse JSON responses and time requests." >&2
  exit 2
fi

BASE_URL="${ENDPOINT%/}"
EXPECTED=$((3 + ROUNDS))
PASS=0
FAIL=0
RESULTS_FILE="$(mktemp)"
trap 'rm -f "$RESULTS_FILE"' EXIT

log() { [[ "$VERBOSE" == true ]] && echo "[INFO] $*" || true; }

check_pass() {
  PASS=$((PASS + 1))
  printf 'PASS\t%s\t\n' "$1" >> "$RESULTS_FILE"
  echo "[PASS] $1"
}

check_fail() {
  FAIL=$((FAIL + 1))
  printf 'FAIL\t%s\t%s\n' "$1" "$2" >> "$RESULTS_FILE"
  echo "[FAIL] $1 — $2"
}

now_ms() { python3 -c 'import time; print(int(time.time() * 1000))'; }

auth_args() {
  if [[ -n "$API_KEY" ]]; then
    printf '%s\n' "-H" "Authorization: Bearer $API_KEY"
  fi
}

# json_check <mode> reads a response body on stdin, prints a reason on failure, exits non-zero.
#   models  -> top-level "data" must be a list
#   chat    -> choices[0].message.content must be a string, finish_reason non-null
json_check() {
  python3 -c '
import json, sys
mode = sys.argv[1]
try:
    body = json.load(sys.stdin)
except Exception as e:
    print(f"response is not JSON ({e.__class__.__name__})"); sys.exit(1)
if mode == "models":
    if not isinstance(body, dict) or not isinstance(body.get("data"), list):
        print("no \"data\" list in response"); sys.exit(1)
    sys.exit(0)
choices = body.get("choices") if isinstance(body, dict) else None
if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
    print("no choices[0] in response"); sys.exit(1)
c0 = choices[0]
msg = c0.get("message")
if not isinstance(msg, dict) or not isinstance(msg.get("content"), str):
    print("choices[0].message.content missing or not a string"); sys.exit(1)
if c0.get("finish_reason") in (None, ""):
    print("choices[0].finish_reason missing or null"); sys.exit(1)
' "$1"
}

post_chat() {
  local payload="$1"
  local -a auth=()
  while IFS= read -r line; do auth+=("$line"); done < <(auth_args)
  curl -sf --max-time "$TIMEOUT" -X POST "$BASE_URL/v1/chat/completions" \
    -H "Content-Type: application/json" ${auth[@]+"${auth[@]}"} -d "$payload" 2>/dev/null || true
}

run_health_check() {
  local url="$BASE_URL/health" status
  log "GET $url"
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || true)
  if [[ "$status" == "200" ]]; then
    check_pass "health-endpoint ($url)"
  else
    check_fail "health-endpoint" "HTTP ${status:-none} from $url"
  fi
}

run_models_check() {
  local url="$BASE_URL/v1/models" body reason
  local -a auth=()
  while IFS= read -r line; do auth+=("$line"); done < <(auth_args)
  log "GET $url"
  body=$(curl -sf --max-time "$TIMEOUT" ${auth[@]+"${auth[@]}"} "$url" 2>/dev/null || true)
  if reason=$(printf '%s' "$body" | json_check models); then
    check_pass "models-list ($url)"
  else
    check_fail "models-list" "$reason"
  fi
}

run_finish_reason_check() {
  local body reason
  body=$(post_chat "$(printf '{"model":"%s","messages":[{"role":"user","content":"Say one word"}],"max_tokens":5}' "$MODEL")")
  if reason=$(printf '%s' "$body" | json_check chat); then
    check_pass "finish-reason-present"
  else
    check_fail "finish-reason-present" "$reason"
  fi
}

run_inference_check() {
  local round="$1" start_ms end_ms latency_ms body reason
  start_ms=$(now_ms)
  body=$(post_chat "$(printf '{"model":"%s","messages":[{"role":"user","content":"Reply with the single word: HEALTHY"}],"max_tokens":10}' "$MODEL")")
  end_ms=$(now_ms)
  if ! [[ "$start_ms" =~ ^[0-9]+$ && "$end_ms" =~ ^[0-9]+$ ]]; then
    check_fail "inference-round-$round" "clock returned non-numeric value ('$start_ms', '$end_ms')"
    return
  fi
  latency_ms=$((end_ms - start_ms))
  if [[ -z "$body" ]]; then
    check_fail "inference-round-$round" "empty response or HTTP error"
  elif ! reason=$(printf '%s' "$body" | json_check chat); then
    check_fail "inference-round-$round" "$reason"
  elif (( latency_ms > MAX_LATENCY_MS )); then
    check_fail "inference-round-$round" "${latency_ms}ms > threshold ${MAX_LATENCY_MS}ms"
  else
    check_pass "inference-round-$round (${latency_ms}ms)"
  fi
}

echo "Smoke test: $BASE_URL  model=$MODEL  rounds=$ROUNDS"
echo "---"

# Each check runs even if an earlier one crashed; a crash leaves it unreported.
run_health_check || true
run_models_check || true
run_finish_reason_check || true
for i in $(seq 1 "$ROUNDS"); do
  run_inference_check "$i" || true
done

REPORTED=$((PASS + FAIL))
MISSING=$((EXPECTED - REPORTED))
if (( MISSING > 0 )); then
  FAIL=$((FAIL + MISSING))
  printf 'FAIL\tunreported-checks\t%s of %s checks did not report\n' "$MISSING" "$EXPECTED" >> "$RESULTS_FILE"
  echo "[FAIL] unreported-checks — $MISSING of $EXPECTED checks did not report"
fi

echo ""
echo "Results: $PASS/$EXPECTED passed"

if [[ -n "$OUTPUT_FILE" ]]; then
  python3 - "$RESULTS_FILE" "$BASE_URL" "$MODEL" "$EXPECTED" "$PASS" "$FAIL" > "$OUTPUT_FILE" <<'PY'
import json, sys
path, endpoint, model, expected, passed, failed = sys.argv[1:]
checks = []
for line in open(path):
    status, name, reason = (line.rstrip("\n").split("\t") + ["", ""])[:3]
    checks.append({"status": status, "name": name, "reason": reason})
print(json.dumps({"endpoint": endpoint, "model": model, "expected": int(expected),
                  "passed": int(passed), "failed": int(failed), "checks": checks}, indent=2))
PY
  echo "Report written to: $OUTPUT_FILE"
fi

[[ "$FAIL" -eq 0 && "$PASS" -eq "$EXPECTED" ]]
