# GitHub Actions CI/CD Template

*Purpose: Build/test, deploy with approvals, and support rollback using a secure, auditable workflow.*

## When to Use

- Application/container build/test/deploy
- IaC workflows (Terraform/OpenTofu, CloudFormation, etc.)
- GitOps changes (manifests/Helm/Kustomize) gated by PR checks

---

# TEMPLATE STARTS HERE

## `.github/workflows/ci-cd.yml` (example)

```yaml
name: CI/CD

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write # For cloud OIDC (optional)

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Replace with your stack (Node/Go/Python/etc.)
      - name: Run tests
        run: ./scripts/test.sh

  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    needs: ci
    environment: production # Configure environment protection rules in GitHub UI
    steps:
      - uses: actions/checkout@v4

      # Optional: authenticate via OIDC (AWS/GCP/Azure) instead of long-lived secrets.
      - name: Deploy
        run: ./scripts/deploy.sh

  rollback:
    if: failure()
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - uses: actions/checkout@v4
      - name: Roll back
        run: ./scripts/rollback.sh
```

## Quality Checklist

- Secrets come from GitHub Actions `secrets`/OIDC (no plaintext in repo/logs)
- Deploys are gated by environment protection rules (approvals, required checks)
- Artifacts are immutable and versioned (image digest/tag, build provenance)
- Rollback is tested (automated where possible) and documented in a runbook
- Notifications exist for deploy/rollback outcomes (Slack/webhook/email)
