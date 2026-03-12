```markdown
# CI/CD Pipeline Template (DevOps)

*Purpose: A complete, production-ready CI/CD template for building, testing, securing, deploying, promoting, and rolling back software changes safely and repeatably.*

---

# 1. Overview

**Service / Application:**  
[name]

**Pipeline Type:**  
- [ ] Build-only  
- [ ] Build + deploy  
- [ ] Full promotion (dev → stage → prod)  
- [ ] GitOps (ArgoCD/Flux)  

**Deployment Target:**  
- [ ] Kubernetes  
- [ ] VM / Server  
- [ ] Serverless  
- [ ] Container registry only  
- [ ] Multi-region  

**Build Artifacts:**  
- [ ] Docker image  
- [ ] Binary  
- [ ] Package (npm/pip/etc.)  
- [ ] Terraform plan  
- [ ] Helm chart  

---

# 2. Pipeline Structure

A standard end-to-end CI/CD pipeline follows:

```

1. Source Control Trigger
2. Static Analysis
3. Build
4. Unit Tests
5. Integration Tests
6. Security Scans
7. Artifact Packaging
8. Deploy to Staging
9. Smoke Tests
10. Approval Gate
11. Deploy to Production
12. Verification & Monitoring
13. Rollback if required

```

---

# 3. Pipeline Triggers

### 3.1 CI (Build/Test)

Triggered on:
- Pull requests  
- Commits to main  
- Scheduled nightly tests  
- Dependency/security updates  

### 3.2 CD (Deploy)

Triggered on:
- Merge to main  
- Tag creation (e.g., `v1.2.3`)  
- Manual approval  
- GitOps reconciliation  

---

# 4. Build Stage

### Commands

```

npm ci
npm run build
go build
mvn package
docker build -t app:$SHA .

```

### Build Checklist

- [ ] Deterministic builds  
- [ ] Version embedded into artifact  
- [ ] Build cache enabled  
- [ ] Build reproducibility validated  

---

# 5. Test Stage

## 5.1 Unit Tests

```

npm test -- --coverage
pytest
go test ./...

```

Checklist:
- [ ] Test coverage target met  
- [ ] No flaky tests  
- [ ] Test time < target  

---

## 5.2 Integration Tests

- Run using docker-compose or ephemeral environment  
- Services mocked only when needed  

Checklist:
- [ ] API endpoints tested  
- [ ] Database setup isolated  
- [ ] Cleanup script runs on failure  

---

## 5.3 Smoke Tests (Staging)

```

curl -f <https://staging.example.com/healthz>

```

Checklist:
- [ ] Deployment healthy  
- [ ] Basic functionality validated  
- [ ] Errors logged to CI console  

---

# 6. Security Scans

## 6.1 Dependency Scans
- Snyk  
- Dependabot  
- Trivy  

## 6.2 Code Scans
- SAST (e.g., CodeQL)  
- Linting (flake8, eslint)  

## 6.3 Container Scans
```

trivy image app:$SHA

```

## 6.4 IaC Scans
- Checkov  
- Tfsec  

### Security Checklist

- [ ] No critical vulnerabilities  
- [ ] SBOM generated  
- [ ] Secrets scan clean  
- [ ] Image signed  

---

# 7. Artifact Packaging

## 7.1 Docker

```

docker build -t registry/app:$SHA .
docker push registry/app:$SHA

```

## 7.2 Package Repos

```

npm publish
pip upload
mvn deploy

```

Checklist:
- [ ] Artifact immutable  
- [ ] Tagged with commit SHA  
- [ ] Stored in registry  
- [ ] Retention policies configured  

---

# 8. Staging Deployment

## Deployment Strategies

- [ ] Rolling  
- [ ] Blue/Green  
- [ ] Canary  
- [ ] GitOps (ArgoCD/Flux)  

Example command:

```

helm upgrade --install app ./charts/app --namespace staging \
  --set image.tag=$SHA

```

Checklist:
- [ ] Staging auto-deployed  
- [ ] Smoke tests pass  
- [ ] Monitoring dashboard green  

---

# 9. Promotion & Approval

## 9.1 Approval Gate

Required for production:

- [ ] SRE/DevOps approval  
- [ ] Product approval  
- [ ] Security approval (if sensitive)  

Checklist:
- [ ] Error budgets respected  
- [ ] Release notes published  
- [ ] Rollback plan validated  

---

# 10. Production Deployment

### Example K8s Production Deploy

```

helm upgrade --install app ./charts/app \
  --namespace prod \
  --set image.tag=$SHA

```

### Example GitOps Deployment

```

git commit -am "prod deploy: $SHA"
git push

```

ArgoCD/Flux syncs automatically.

### Production Checklist

- [ ] Health checks passing  
- [ ] p99 latency stable  
- [ ] No spike in error rate  
- [ ] Logs clean  
- [ ] Capacity within thresholds  

---

# 11. Deployment Strategies

## 11.1 Rolling Update

- Minimal risk  
- Good default  

Checklist:
- [ ] Readiness probe correct  
- [ ] MaxSurge/MaxUnavailable tuned  

---

## 11.2 Blue/Green

```

blue = live
green = new version

```

Checklist:
- [ ] Full validation of green  
- [ ] Traffic switch atomic  
- [ ] Blue preserved for rollback  

---

## 11.3 Canary

```

1% → 5% → 20% → 50% → 100%

```

Checklist:
- [ ] Automated rollback  
- [ ] Metrics compared between cohorts  
- [ ] SLO-based gating  

---

# 12. Rollback

### Rollback Methods

- [ ] Deploy previous image  
- [ ] Revert Git commit (GitOps)  
- [ ] Helm rollback  
- [ ] Restore previous config  
- [ ] Disable feature flags  

### Rollback Plan Template

```

Rollback Trigger:
Rollback Method:
Rollback Steps:
Validation After Rollback:

```

### Rollback Checklist

- [ ] Rollback < 2 minutes  
- [ ] No schema-incompatible changes  
- [ ] Post-rollback monitoring verified  

---

# 13. CI/CD Security

- [ ] No long-lived tokens  
- [ ] Use OIDC to cloud for access  
- [ ] Secrets in CI vaults only  
- [ ] Principle of least privilege  
- [ ] Logs don’t include secrets  
- [ ] Scoped permissions for pipelines  

---

# 14. Example Full Pipeline (Generic YAML)

```

stages:

- build
- test
- security
- deploy

build:
  script:
    - npm ci
    - npm run build

test:
  script:
    - npm test

security:
  script:
    - snyk test
    - trivy fs .

deploy:
  script:
    - helm upgrade --install app .
  when: manual

```

---

# 15. Final Review Checklist

### Pipeline Quality
- [ ] Build deterministic  
- [ ] Tests reliable  
- [ ] Security checks automated  
- [ ] Promotion flow clear  

### Deployment Safety
- [ ] Rollback tested  
- [ ] Canary or rolling strategy  
- [ ] No manual steps in prod deploy  

### Reliability
- [ ] Observability integrated  
- [ ] Dashboards updated  
- [ ] Alerts tuned post-deploy  

---

# END
```
