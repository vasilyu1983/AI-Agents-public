# Supply Chain & Artifact Integrity

Operational patterns for securing ML/LLM supply chains, artifact integrity, and dependency management.

---

## Overview

ML/LLM systems depend on:
- Model checkpoints and weights
- Embeddings and vector databases
- Python/JS packages and CUDA drivers
- Container images and base images
- Data pipelines and transformation code

Each dependency is a potential attack vector. This guide covers verification, signing, and monitoring patterns.

---

## 1. SBOM + Signing

### Software Bill of Materials (SBOM)

Generate SBOM for all artifacts:
- Model files (.pt, .ckpt, .safetensors)
- Adapter/LoRA weights
- Container images
- Python wheels and requirements.txt
- CUDA drivers and runtime versions

**Tools:**
- **Syft** - SBOM generation for containers
- **CycloneDX** - SBOM standard format
- **SPDX** - Software Package Data Exchange

### Artifact Signing

Sign all production artifacts:
- GPG signatures for model files
- Cosign for container images
- Sigstore for broader artifact signing

**Example workflow:**
```bash
# Sign model checkpoint
gpg --detach-sign model-v1.2.3.pt

# Verify signature
gpg --verify model-v1.2.3.pt.sig model-v1.2.3.pt

# Sign container image with cosign
cosign sign registry.example.com/ml-service:v1.2.3

# Verify container signature
cosign verify registry.example.com/ml-service:v1.2.3
```

### CI/CD Integration

Verify signatures in deployment pipelines:
```yaml
# .github/workflows/deploy.yml
- name: Verify Model Signature
  run: |
    gpg --verify model.pt.sig model.pt

- name: Verify Container Signature
  run: |
    cosign verify $IMAGE_NAME
```

---

## 2. Dependency Scanning

### Python Package Scanning

Scan for known CVEs in dependencies:

**Tools:**
- **Safety** - Python dependency scanner
- **pip-audit** - Audit Python packages
- **Snyk** - Multi-language vulnerability scanning
- **Dependabot** - Automated dependency updates

**Example:**
```bash
# Scan Python dependencies
pip-audit

# Check for known vulnerabilities
safety check --json

# Block deployment on high/critical CVEs
pip-audit --strict
```

### Pin Hashes for Reproducibility

Lock dependency hashes in `requirements.txt`:
```
# requirements.txt
torch==2.0.1 --hash=sha256:abc123...
transformers==4.30.2 --hash=sha256:def456...
```

**Benefits:**
- Prevents dependency confusion attacks
- Ensures reproducible builds
- Detects package tampering

### CUDA and Driver Scanning

Verify GPU driver and CUDA versions:
```bash
# Check NVIDIA driver version
nvidia-smi

# Verify CUDA version
nvcc --version

# Validate against allowlist
./scripts/validate-cuda-version.sh
```

Maintain allowlist of approved versions:
```yaml
# cuda-allowlist.yaml
approved_cuda_versions:
  - "11.8"
  - "12.1"

approved_driver_versions:
  - "525.85.12"
  - "530.41.03"
```

---

## 3. Model & Embedding Integrity

### Model Checkpoint Hashing

Generate and verify SHA256 hashes:
```python
import hashlib

def hash_model(model_path: str) -> str:
    """Generate SHA256 hash of model file."""
    sha256 = hashlib.sha256()
    with open(model_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Generate hash at model save time
model_hash = hash_model("model-v1.2.3.pt")
with open("model-v1.2.3.pt.sha256", "w") as f:
    f.write(model_hash)
```

### Verify on Load

Always validate hash before loading:
```python
def verify_and_load_model(model_path: str, expected_hash: str):
    """Verify model hash before loading."""
    actual_hash = hash_model(model_path)

    if actual_hash != expected_hash:
        raise SecurityError(
            f"Model hash mismatch! Expected {expected_hash}, got {actual_hash}"
        )

    # Safe to load
    return torch.load(model_path)
```

### Embedding Integrity

Hash vector database snapshots:
```bash
# Hash Pinecone/Weaviate backup
sha256sum vectordb-backup-2024-11-22.tar.gz > vectordb-backup-2024-11-22.tar.gz.sha256

# Verify before restore
sha256sum -c vectordb-backup-2024-11-22.tar.gz.sha256
```

### Isolate Untrusted Models

Run untrusted models in sandboxed environments:
- Separate namespaces/containers
- Limited network access
- No access to production data
- Monitor resource usage

---

## 4. Driver/Runtime Attestation

### GPU Driver Verification

Verify driver versions match approved list:
```python
import subprocess
import json

def verify_driver_version() -> bool:
    """Check NVIDIA driver against allowlist."""
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
        capture_output=True,
        text=True
    )
    driver_version = result.stdout.strip()

    with open("cuda-allowlist.yaml") as f:
        allowlist = yaml.safe_load(f)

    if driver_version not in allowlist["approved_driver_versions"]:
        raise SecurityError(f"Unapproved driver version: {driver_version}")

    return True
```

### Log Attestation

Record attestation for every deployment:
```json
{
  "deployment_id": "ml-service-v1.2.3",
  "timestamp": "2024-11-22T10:30:00Z",
  "attestation": {
    "cuda_version": "12.1",
    "driver_version": "530.41.03",
    "model_hash": "abc123...",
    "container_digest": "sha256:def456...",
    "verified": true
  }
}
```

### Runtime Integrity Monitoring

Monitor runtime changes:
```bash
# Check for unexpected driver updates
watch -n 60 nvidia-smi --query-gpu=driver_version --format=csv

# Alert on changes
if [ "$CURRENT_DRIVER" != "$EXPECTED_DRIVER" ]; then
  alert "Driver version changed unexpectedly"
fi
```

---

## 5. Registry Hygiene

### Immutable Tags

Use immutable tags in production:
```yaml
# docker-compose.yml
services:
  ml-service:
    # BAD: Bad: mutable tag
    image: registry.example.com/ml-service:latest

    # GOOD: Good: immutable digest
    image: registry.example.com/ml-service@sha256:abc123...
```

### Promotion via Signed Manifests

Require signed manifests for production promotion:
```bash
# Sign manifest for production
cosign sign registry.example.com/ml-service:v1.2.3

# Policy: only signed images can be deployed to prod
kubectl apply -f pod-security-policy.yaml
```

### Audit Logs

Enable audit logging on container registries:
- Who pulled which image
- When images were pushed/deleted
- Tag mutations

**Example (AWS ECR):**
```json
{
  "eventName": "PutImage",
  "userIdentity": {
    "principalId": "AIDAI23ABC...",
    "userName": "ml-deploy-bot"
  },
  "requestParameters": {
    "repositoryName": "ml-service",
    "imageTag": "v1.2.3"
  },
  "responseElements": {
    "image": {
      "imageId": {
        "imageDigest": "sha256:abc123..."
      }
    }
  }
}
```

### Vulnerability Scanning

Scan container images on push:
```yaml
# .github/workflows/build.yml
- name: Scan container for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: registry.example.com/ml-service:${{ github.sha }}
    severity: HIGH,CRITICAL
    exit-code: 1  # Fail on high/critical
```

---

## Supply Chain Hardening Checklist

- [ ] SBOM generated for all artifacts (models, containers, packages)
- [ ] Artifacts signed (GPG for models, Cosign for containers)
- [ ] Signatures verified in CI/CD before deployment
- [ ] Dependency scanning blocks known CVEs (pip-audit, Snyk, Safety)
- [ ] Dependency hashes pinned in requirements.txt
- [ ] Model and embedding hashes validated at load time
- [ ] Untrusted models isolated in sandboxed environments
- [ ] GPU driver/CUDA versions validated against allowlist
- [ ] Driver/runtime attestation logged per deployment
- [ ] Container registry uses immutable tags (digests, not :latest)
- [ ] Production promotion requires signed manifests
- [ ] Registry audit logs enabled and monitored
- [ ] Container vulnerability scanning on push (Trivy, Snyk)
- [ ] Supply chain security reviewed quarterly

---

## Related Patterns

- **[Threat Models](threat-models.md)** - Supply chain attacks in ML/LLM threat taxonomy
- **[Governance Checklists](governance-checklists.md)** - Compliance requirements for artifact management
- **[Incident Response](incident-response-playbooks.md)** - Responding to supply chain compromises
