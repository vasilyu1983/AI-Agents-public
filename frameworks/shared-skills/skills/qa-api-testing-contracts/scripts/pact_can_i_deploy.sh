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
#
# Exit codes:
#   0 — safe to deploy (all verifications passed)
#   1 — unsafe to deploy or error

set -euo pipefail

: "${PACT_BROKER_BASE_URL:?PACT_BROKER_BASE_URL is required}"
: "${SERVICE:?SERVICE is required}"
: "${GIT_SHA:?GIT_SHA is required}"

TO_ENVIRONMENT="${TO_ENVIRONMENT:-production}"

AUTH_ARGS=()
if [[ -n "${PACT_BROKER_TOKEN:-}" ]]; then
  AUTH_ARGS=(--broker-token "${PACT_BROKER_TOKEN}")
fi

echo "==> pact can-i-deploy: checking ${SERVICE}@${GIT_SHA} → ${TO_ENVIRONMENT}"

pact-broker can-i-deploy \
  --pacticipant "${SERVICE}" \
  --version "${GIT_SHA}" \
  --to-environment "${TO_ENVIRONMENT}" \
  --broker-base-url "${PACT_BROKER_BASE_URL}" \
  "${AUTH_ARGS[@]+"${AUTH_ARGS[@]}"}"

echo "==> pact can-i-deploy: OK — ${SERVICE}@${GIT_SHA} is safe to deploy to ${TO_ENVIRONMENT}"
