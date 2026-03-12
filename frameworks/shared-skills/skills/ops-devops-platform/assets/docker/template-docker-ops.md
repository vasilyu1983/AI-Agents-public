```markdown
# Docker Operations Template (DevOps)

*Purpose: A complete operational template for building, securing, optimizing, distributing, running, and debugging Docker containers in production environments.*

---

# 1. Overview

**Service / Component:**  
[name]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  

**Task Type:**  
- [ ] Build image  
- [ ] Optimize Dockerfile  
- [ ] Scan / security harden  
- [ ] Publish to registry  
- [ ] Debug container  
- [ ] Multi-stage build  
- [ ] Runtime troubleshooting  

**Registry:**  
- [ ] Docker Hub  
- [ ] GHCR  
- [ ] ECR  
- [ ] GCR  
- [ ] ACR  
- [ ] Self-hosted  

---

# 2. Dockerfile Standards

## 2.1 Recommended Minimal Base Image

```

FROM alpine:3.20
RUN adduser -D appuser
USER appuser

```

OR

```

FROM gcr.io/distroless/base

```

Checklist:
- [ ] Minimal base image  
- [ ] Multi-stage build used  
- [ ] Non-root user  
- [ ] No secrets copied into image  
- [ ] No `curl | bash`  
- [ ] Avoid `ADD` (use `COPY`)  
- [ ] Pin versions for deterministic builds  

---

## 2.2 Multi-Stage Build Template

```

# Build Stage

FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN go build -o app .

# Runtime Stage

FROM alpine:3.20
RUN adduser -D appuser
USER appuser
COPY --from=builder /src/app /app
ENTRYPOINT ["/app"]

```

Checklist:
- [ ] Build & runtime stages separate  
- [ ] No build tools in final image  
- [ ] Final image size small (<100MB preferred)  

---

# 3. Image Scanning & SBOM

## 3.1 Vulnerability Scan

```

trivy image registry/app:$VERSION

```

Checklist:
- [ ] No critical vulnerabilities  
- [ ] Medium vulns triaged  
- [ ] Image updated to latest patches  

## 3.2 SBOM (Software Bill of Materials)

```

syft registry/app:$VERSION -o json > sbom.json

```

## 3.3 Image Signing

```

cosign sign --key cosign.key registry/app:$VERSION

```

Checklist:
- [ ] Signature stored  
- [ ] Verification in CI/CD  
- [ ] Policy: unsigned images blocked (Kyverno/OPA)  

---

# 4. Build & Push Workflow

## 4.1 Build

```

docker build -t registry/app:$SHA .

```

## 4.2 Tag

```

docker tag registry/app:$SHA registry/app:latest

```

## 4.3 Push

```

docker push registry/app:$SHA
docker push registry/app:latest

```

### Checklist

- [ ] Tag includes commit SHA  
- [ ] Immutable tags used for deploys  
- [ ] Avoid floating tags in prod  
- [ ] Use registry-side retention policies  

---

# 5. Local Development

## 5.1 Run Container

```

docker run -p 8080:8080 registry/app:$TAG

```

## 5.2 Mount Code for Live Reload

```

docker run -p 8080:8080 -v $(pwd):/workspace app-dev

```

Checklist:
- [ ] Environment parity maintained  
- [ ] App logs visible locally  

---

# 6. Runtime Operations (Production)

## 6.1 Health Check

Add to Dockerfile:

```

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -f <http://localhost:8080/healthz> || exit 1

```

Checklist:
- [ ] Healthcheck lightweight  
- [ ] App exposes proper health endpoint  

---

## 6.2 Resource Limits (Docker Compose)

```

deploy:
  resources:
    limits:
      cpus: "1"
      memory: 512M
    reservations:
      cpus: "0.25"
      memory: 256M

```

Checklist:
- [ ] Avoid unbounded resource usage  
- [ ] Reserve enough memory to avoid OOMKilled  

---

# 7. Debugging Containers

## 7.1 Check Logs

```

docker logs <container>

```

## 7.2 Exec In

```

docker exec -it <container> sh

```

## 7.3 Inspect Container Metadata

```

docker inspect <container>

```

## 7.4 Check Resource Usage

```

docker stats

```

Checklist:
- [ ] No CrashLoop events  
- [ ] EntryPoint correct  
- [ ] Ports exposed correctly  
- [ ] Env vars match expected config  

---

# 8. Networking

## 8.1 View Networks

```

docker network ls
docker network inspect <network>

```

## 8.2 Connect Container to Network

```

docker network connect <network> <container>

```

Checklist:
- [ ] No open ports unintentionally exposed  
- [ ] Network separation applied (frontend/backend/db)  

---

# 9. Storage & Volumes

## 9.1 Create Volume

```

docker volume create app-data

```

## 9.2 Mount Volume

```

docker run -v app-data:/data registry/app

```

Checklist:
- [ ] Avoid ephemeral data for stateful apps  
- [ ] Volume permissions correct  
- [ ] Volume drivers documented  

---

# 10. Compose / Swarm / Local Orchestration

## 10.1 docker-compose Example

```

version: '3.9'
services:
  app:
    image: registry/app:$TAG
    ports: ["8080:8080"]
    environment:
      - ENV=prod
    depends_on:
      - db

```

Checklist:
- [ ] Services start in correct order  
- [ ] Health checks configured  
- [ ] Resource limits present  

---

# 11. Docker Registry Best Practices

Checklist:
- [ ] Use private registry for production  
- [ ] Enforce pull authentication  
- [ ] Enable vulnerability scans  
- [ ] Enforce retention policies  
- [ ] Delete old tags safely  
- [ ] Use digest pinning in K8s deploys  

---

# 12. Container Security Hardening

Checklist:
- [ ] Run as non-root  
- [ ] Read-only root filesystem  
- [ ] Drop all capabilities except required  
- [ ] No SSH inside container  
- [ ] No sensitive env vars (tokens/passwords)  
- [ ] Disable inter-container network if not needed  

---

# 13. Docker Troubleshooting Guide

## 13.1 Cannot Pull Image

- [ ] Check registry auth  
- [ ] Check tag exists  
- [ ] Check network/DNS  

## 13.2 App Crashing on Start

- [ ] Inspect logs  
- [ ] Validate ENTRYPOINT / CMD  
- [ ] Validate config files present  
- [ ] Validate required env vars  

## 13.3 High Memory Usage

- [ ] Memory leak in app  
- [ ] Missing resource limits  
- [ ] Large image causing startup overhead  

## 13.4 Permission Errors

- [ ] File ownership mismatch  
- [ ] Running as non-root missing permissions  
- [ ] Volume mounted with wrong uid/gid  

---

# 14. Final Operational Checklist

### Build
- [ ] Image reproducible  
- [ ] Multi-stage build  
- [ ] Minimal base image  
- [ ] No secrets in layers  

### Security
- [ ] Image scanned (Trivy/Grype)  
- [ ] SBOM generated  
- [ ] Image signed  
- [ ] Non-root user  
- [ ] Read-only FS  

### Deployment
- [ ] Immutable tag  
- [ ] Registry health checked  
- [ ] K8s digest pinned  
- [ ] Health checks enabled  

### Runtime
- [ ] Logs correct format  
- [ ] Metrics exported  
- [ ] Alerts configured  

---

# 15. Completed Example

**Service:** Orders API  
**Image:** `registry/orders-api:sha256:cb1a…`  
**Base Image:** Distroless  
**Security:**  
- No critical vulns  
- Signed with Cosign  
- SBOM generated  

**Dockerfile:** Multi-stage, non-root, minimal runtime  
**Deployment:** K8s using pinned digest  
**Outcome:** Fast startup, small image size (26MB), zero vulnerabilities.

---

# END
```
