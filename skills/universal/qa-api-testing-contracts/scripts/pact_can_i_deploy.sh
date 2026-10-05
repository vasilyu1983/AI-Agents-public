#!/usr/bin/env bash
# pact_can_i_deploy.sh — Gate deployment using Pact Broker can-i-deploy.
#
# Required env vars:
#   PACT_BROKER_BASE_URL  — base URL of the Pact Broker or PactFlow instance
#   SERVICE               — pacticipant name (provider or consumer)
#   GIT_SHA               — version to check (usually the current commit SHA)
#
# Optional env vars:
#   PACT_BROKER_TOKEN     — bearer token for PactFlow or authenticated brokers
#   TO_ENVIRONMENT        — target environment (default: production)
#   RETRY_WHILE_UNKNOWN   — retries while provider verification is still running (default: 0, no retry)
#   RETRY_INTERVAL        — seconds between retries, used with RETRY_WHILE_UNKNOWN (default: 10)
#
# Exit codes:
#   0 — safe to deploy (all verifications passed)
#   1 — unsafe to deploy or error

set -euo pipefail

: "${PACT_BROKER_BASE_URL:?PACT_BROKER_BASE_URL is required}"
: "${SERVICE:?SERVICE is required}"
: "${GIT_SHA:?GIT_SHA is required}"

# These client settings can suppress a failed/missing verification or omit a
# pairing. Reject inherited overrides rather than print a false safe-to-deploy.
for setting in PACT_BROKER_CAN_I_DEPLOY_DRY_RUN PACT_BROKER_CAN_I_DEPLOY_IGNORE PACT_BROKER_CAN_I_DEPLOY_EXIT_CODE_BETA; do
  if [[ -n "${!setting:-}" ]]; then
    echo "ERROR: ${setting} must be unset for this deployment gate" >&2
    exit 1
  fi
done

TO_ENVIRONMENT="${TO_ENVIRONMENT:-production}"
RETRY_WHILE_UNKNOWN="${RETRY_WHILE_UNKNOWN:-0}"
RETRY_INTERVAL="${RETRY_INTERVAL:-10}"

AUTH_ARGS=()
if [[ -n "${PACT_BROKER_TOKEN:-}" ]]; then
  AUTH_ARGS=(--broker-token "${PACT_BROKER_TOKEN}")
fi

echo "==> pact can-i-deploy: checking ${SERVICE}@${GIT_SHA} → ${TO_ENVIRONMENT}"

# --retry-while-unknown covers the race where this check runs before the provider's
# contract_requiring_verification_published webhook has triggered and completed verification.
pact-broker can-i-deploy \
  --pacticipant "${SERVICE}" \
  --version "${GIT_SHA}" \
  --to-environment "${TO_ENVIRONMENT}" \
  --broker-base-url "${PACT_BROKER_BASE_URL}" \
  --retry-while-unknown "${RETRY_WHILE_UNKNOWN}" \
  --retry-interval "${RETRY_INTERVAL}" \
  "${AUTH_ARGS[@]+"${AUTH_ARGS[@]}"}"

echo "==> pact can-i-deploy: OK — ${SERVICE}@${GIT_SHA} is safe to deploy to ${TO_ENVIRONMENT}"
