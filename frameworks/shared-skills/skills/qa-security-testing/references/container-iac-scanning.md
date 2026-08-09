# Container and IaC Scanning Guide

Scanning container images for CVEs and infrastructure-as-code for misconfigurations. Covers Trivy, Checkov, base image policy, and CI integration patterns.

## Table of Contents

- [Tool Selection](#tool-selection)
- [Container Image Scanning](#container-image-scanning)
- [Trivy CI Integration](#trivy-ci-integration)
- [.github/workflows/container-scan.yml](#githubworkflowscontainer-scanyml)
- [CLI Usage](#cli-usage)
- [Scan a local image](#scan-a-local-image)
- [Scan with severity filter](#scan-with-severity-filter)
- [Scan and generate SBOM](#scan-and-generate-sbom)
- [Scan a remote registry image](#scan-a-remote-registry-image)
- [Ignore unfixed vulnerabilities](#ignore-unfixed-vulnerabilities)
- [Base Image Policy](#base-image-policy)
- [Approved Base Images](#approved-base-images)
- [Enforcement](#enforcement)
- [Check base image in CI](#check-base-image-in-ci)
- [Verify against approved list or scan the base image itself](#verify-against-approved-list-or-scan-the-base-image-itself)
- [Multi-Stage Build Best Practices](#multi-stage-build-best-practices)
- [Build stage: can use full image](#build-stage-can-use-full-image)
- [Runtime stage: minimal image](#runtime-stage-minimal-image)
- [IaC Scanning](#iac-scanning)
- [Trivy for IaC](#trivy-for-iac)
- [Scan Terraform files](#scan-terraform-files)
- [Scan Kubernetes manifests](#scan-kubernetes-manifests)
- [Scan Helm charts](#scan-helm-charts)
- [Checkov CI Integration](#checkov-ci-integration)
- [.github/workflows/iac-scan.yml](#githubworkflowsiac-scanyml)
- [Common IaC Misconfigurations](#common-iac-misconfigurations)
- [Custom Checkov Policies](#custom-checkov-policies)
- [custom_checks/s3_versioning.py](#customcheckss3versioningpy)
- [Registry Scanning](#registry-scanning)
- [Scheduled Registry Scans](#scheduled-registry-scans)
- [.github/workflows/registry-scan.yml](#githubworkflowsregistry-scanyml)
- [Metrics](#metrics)

## Tool Selection

| Tool | Targets | Model | Key Strength |
|------|---------|-------|-------------|
| Trivy | Containers, IaC, SBOM, filesystems | Open source | Single tool for multiple targets |
| Checkov | Terraform, CloudFormation, Kubernetes, Helm | Open source + Prisma Cloud | Deep IaC policy checks, graph-based cross-resource analysis |
| Grype | Container images | Open source (Anchore) | Fast image scanning, SBOM input |

> tfsec is deprecated. Aqua Security merged all tfsec checks into Trivy `config` scanner in 2024. All tfsec check IDs (e.g., `AVD-AWS-0086`) map 1:1 in Trivy, so existing compliance baselines do not require re-mapping. Do not use tfsec for new projects.

**Default recommendation**: Trivy as the primary tool (covers containers, IaC, and SBOM in one binary). Add Checkov for deeper IaC policy enforcement if using Terraform or CloudFormation extensively — its graph-based cross-resource checks and 1,000+ built-in policies remain unmatched for pure IaC scanning.

**Trivy supply chain incident (March 2026)**: On 2026-03-19, a threat actor (attributed to TeamPCP) used compromised credentials to publish a malicious Trivy v0.69.4 release and force-push 75 of 76 version tags in `aquasecurity/trivy-action` plus all 7 tags in `aquasecurity/setup-trivy` to credential-stealing malware. Root cause: an earlier disclosure on 2026-03-01 triggered a non-atomic credential rotation, leaving a valid token active for days. The malicious versions exfiltrated SSH keys, cloud credentials, Kubernetes tokens, and env vars via HTTP POST to a typosquatted domain. Safe versions: Trivy 0.69.2/0.69.3+, `trivy-action` 0.35.0+, `setup-trivy` 0.2.6+ (recreated). **Lessons for any scanner**: because version *tags* themselves were force-pushed, pinning to a tag — even an old one — is not inherently safe from this attack class; pin to a release SHA digest, verify actions with `gh attestation verify` before running in privileged contexts, and rotate any secret accessible to pipelines that ran within the exposure window. See https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23.

## Container Image Scanning

### Trivy CI Integration

```yaml
# .github/workflows/container-scan.yml
name: Container Security Scan
on:
  push:
    paths:
      - 'Dockerfile*'
      - 'docker-compose*.yml'
      - '.github/workflows/container-scan.yml'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Trivy image scan
        # 0.35.0 is the first release confirmed clean after the 2026-03 trivy-action compromise.
        # Pin to its release SHA (not just the tag) — see the incident note above for why tags alone are not safe.
        # Check https://github.com/aquasecurity/trivy/security/advisories for current status before using in production.
        uses: aquasecurity/trivy-action@0.35.0
        with:
          image-ref: myapp:${{ github.sha }}
          format: sarif
          output: trivy-image.sarif
          severity: CRITICAL,HIGH
          exit-code: 1  # Fail on critical/high

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-image.sarif
```

### CLI Usage

```bash
# Scan a local image
trivy image myapp:latest

# Scan with severity filter
trivy image --severity CRITICAL,HIGH --exit-code 1 myapp:latest

# Scan and generate SBOM
trivy image --format cyclonedx --output sbom.json myapp:latest

# Scan a remote registry image
trivy image --severity CRITICAL registry.example.com/myapp:v1.2.3

# Ignore unfixed vulnerabilities
trivy image --ignore-unfixed myapp:latest
```

## Base Image Policy

### Approved Base Images

Define and enforce a list of approved base images:

| Category | Approved Images | Update Cadence |
|----------|----------------|----------------|
| General | `cgr.dev/chainguard/*`, `mcr.microsoft.com/cbl-mariner/*` | Weekly |
| Node.js | `node:22-slim`, `node:22-alpine` | On release |
| Python | `python:3.13-slim`, `python:3.13-alpine` | On release |
| Java | `eclipse-temurin:21-jre-alpine` | On release |
| Distroless | `gcr.io/distroless/*` | On release |

### Enforcement

```bash
# Check base image in CI
BASE_IMAGE=$(head -1 Dockerfile | sed 's/FROM //')
# Verify against approved list or scan the base image itself
trivy image --severity CRITICAL "$BASE_IMAGE"
```

### Multi-Stage Build Best Practices

```dockerfile
# Build stage: can use full image
FROM node:22 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build

# Runtime stage: minimal image
FROM node:22-slim
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER app
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

Scan the final stage image, not the build stage.

## IaC Scanning

### Trivy for IaC

```bash
# Scan Terraform files
trivy config --severity CRITICAL,HIGH ./terraform/

# Scan Kubernetes manifests
trivy config --severity CRITICAL,HIGH ./k8s/

# Scan Helm charts
trivy config ./charts/myapp/
```

### Checkov CI Integration

```yaml
# .github/workflows/iac-scan.yml
name: IaC Security Scan
on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'k8s/**'
      - 'cloudformation/**'

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          framework: terraform
          soft_fail: false
          output_format: sarif
          output_file_path: checkov.sarif
```

### Common IaC Misconfigurations

| Category | Example | Severity |
|----------|---------|----------|
| Public access | S3 bucket with public read, security group 0.0.0.0/0 | Critical |
| Encryption | Unencrypted EBS volumes, RDS without encryption at rest | High |
| Logging | CloudTrail disabled, VPC flow logs off | High |
| IAM | Wildcard permissions, no MFA requirement | Critical |
| Networking | Default VPC usage, overly permissive NACLs | Medium |
| Secrets | Hardcoded credentials in IaC files | Critical |

### Custom Checkov Policies

```python
# custom_checks/s3_versioning.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class S3Versioning(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket has versioning enabled"
        id = "CUSTOM_S3_001"
        supported_resources = ["aws_s3_bucket"]
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories,
                        supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        versioning = conf.get("versioning", [{}])
        if isinstance(versioning, list) and len(versioning) > 0:
            if versioning[0].get("enabled", [False]) == [True]:
                return CheckResult.PASSED
        return CheckResult.FAILED

check = S3Versioning()
```

## Registry Scanning

### Scheduled Registry Scans

Scan images already deployed to catch newly discovered CVEs:

```yaml
# .github/workflows/registry-scan.yml
name: Registry Vulnerability Scan
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

jobs:
  scan-registry:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        image:
          - registry.example.com/app-api:latest
          - registry.example.com/app-web:latest
          - registry.example.com/app-worker:latest
    steps:
      - name: Trivy scan
        uses: aquasecurity/trivy-action@0.35.0 # first safe release after the 2026-03 compromise; pin to its SHA
        with:
          image-ref: ${{ matrix.image }}
          severity: CRITICAL,HIGH
          format: table
```

## Metrics

| Metric | Target |
|--------|--------|
| Base image age | Under 30 days from latest patch |
| Critical CVEs in production images | Zero |
| IaC scan coverage | 100% of IaC directories |
| Mean time to patch base image CVE | Under 7 days |
| Registry scan frequency | Weekly minimum |
