```markdown
# Security Hardening Template (DevOps)

*Purpose: A comprehensive template for securing infrastructure, CI/CD, Kubernetes, containers, secrets, IAM, and runtime environments.*

---

# 1. Overview

**System / Component:**  
[name]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  

**Security Context:**  
- [ ] New service onboarding  
- [ ] Hardening review  
- [ ] Incident-driven improvement  
- [ ] Compliance requirement (PCI/GDPR/SOC2/HIPAA)  

**Reviewer:**  
[name]  
**Date:**  
[YYYY-MM-DD]

---

# 2. Identity & Access Management (IAM)

## 2.1 IAM Checklist

- [ ] Principle of least privilege  
- [ ] No wildcard permissions (“\*”)  
- [ ] Role separation: admin vs deployer vs read-only  
- [ ] No long-lived credentials  
- [ ] Use IAM roles, not static keys  
- [ ] CI/CD uses OIDC + cloud IAM  
- [ ] MFA required for privileged accounts  
- [ ] Access logs enabled  

## 2.2 IAM Role Table

| Role | Purpose | Allowed Actions | Denied Actions | Notes |
|------|----------|------------------|-----------------|--------|
| | | | | |

---

# 3. Secrets Management

## 3.1 Approved Secret Storage

- AWS Secrets Manager  
- AWS SSM Parameter Store (SecureString)  
- HashiCorp Vault  
- GCP Secret Manager  
- Azure Key Vault  
- Kubernetes SealedSecrets/SOPS  

## 3.2 Checklist

- [ ] No plaintext secrets in repo  
- [ ] No secrets in Terraform vars/tfvars  
- [ ] Secrets encrypted at rest and in transit  
- [ ] Secret rotation configured  
- [ ] Access only for services that require it  
- [ ] K8s secrets encrypted using KMS  

---

# 4. Network Security

## 4.1 Ingress/Egress Rules

- [ ] Default deny egress  
- [ ] Only required ports allowed  
- [ ] Restrict public IP access  
- [ ] Enforce TLS everywhere  
- [ ] WAF enabled for web workloads  
- [ ] NetworkPolicies configured (K8s)  

## 4.2 Firewall Checklist

- [ ] No open ports to world  
- [ ] VPC/VNet segmentation enforced  
- [ ] Internal-only services protected  
- [ ] LB security groups tightened  
- [ ] Bastion host hardened or removed  

---

# 5. Container Security

## 5.1 Dockerfile Hardening

```

FROM alpine:3.19
RUN adduser -D appuser
USER appuser
ENTRYPOINT ["./app"]

```

Checklist:
- [ ] Use minimal base images (alpine/distroless)  
- [ ] Multi-stage builds  
- [ ] Run as non-root  
- [ ] No sensitive data copied into image  
- [ ] Pin image tags to digests  
- [ ] Avoid curl | bash  
- [ ] Avoid ADD (use COPY)  

## 5.2 Image Scanning

- Trivy  
- Grype  
- Docker Scout  
- Snyk  

Checklist:
- [ ] Critical vulnerabilities remediated  
- [ ] SBOM generated  
- [ ] Images signed (cosign/notary)  

---

# 6. Kubernetes Security

## 6.1 Pod Security

Checklist:
- [ ] runAsNonRoot: true  
- [ ] readOnlyRootFilesystem: true  
- [ ] drop capabilities (NET_RAW, etc.)  
- [ ] no host filesystem mounts  
- [ ] no privileged pods  
- [ ] limit memory/CPU to avoid DOS  
- [ ] use Pod Security Admission or Kyverno/OPA  

## 6.2 RBAC

Checklist:
- [ ] No cluster-admin usage  
- [ ] Namespace-scoped roles preferred  
- [ ] ServiceAccounts per workload  
- [ ] Token automount disabled  
- [ ] RoleBindings reviewed  

```

automountServiceAccountToken: false

```

---

# 7. CI/CD Security

## 7.1 Pipeline Hardening

- [ ] OIDC → cloud IAM, no static secrets  
- [ ] Repo secrets stored in encrypted vault  
- [ ] PR builds cannot access prod secrets  
- [ ] Artifact signing required  
- [ ] No untrusted code executed in privileged containers  

## 7.2 Required Security Scans

- [ ] SAST (static code analysis)  
- [ ] DAST (runtime scanning)  
- [ ] Dependency scanning (Snyk/Trivy)  
- [ ] IaC scanning (Checkov/Tfsec)  
- [ ] Secret scanning  

---

# 8. OS & Host Security (EC2/VM/Bare Metal)

Checklist:
- [ ] Patching automated  
- [ ] SSH disabled or keyless-only  
- [ ] Use SSM Session Manager  
- [ ] Filesystem encrypted  
- [ ] No root login  
- [ ] Audit logs enabled  
- [ ] Disk space monitoring  

---

# 9. Logging & Monitoring Security

Checklist:
- [ ] Logs do not contain secrets  
- [ ] Structured logs (JSON)  
- [ ] TLS for log ingestion  
- [ ] Alerting tied to SLO thresholds  
- [ ] SIEM integration (Splunk/ELK/Sentinel)  
- [ ] Access logs kept according to retention policy  

---

# 10. Disaster Recovery Security

Checklist:
- [ ] Backups encrypted in transit & at rest  
- [ ] Backups stored cross-region  
- [ ] RPO/RTO validated  
- [ ] Backup access restricted  
- [ ] DR failover tested quarterly  
- [ ] Snapshots immutable (WORM/S3 Object Lock)  

---

# 11. Compliance Alignment

Compliance Required:  
- [ ] SOC 2  
- [ ] PCI  
- [ ] GDPR  
- [ ] HIPAA  
- [ ] FedRAMP  

Checklist:
- [ ] Data classification completed  
- [ ] Access policies documented  
- [ ] Retention policies implemented  
- [ ] PII minimization confirmed  
- [ ] Encryption policies compliant  

---

# 12. Risk Assessment Table

| Risk | Severity | Probability | Mitigation | Owner |
|------|----------|-------------|------------|--------|
| | | | | |

---

# 13. Final Hardening Checklist

### Critical
- [ ] Least privilege everywhere  
- [ ] No plaintext secrets  
- [ ] No privileged containers  
- [ ] Images scanned & signed  
- [ ] TLS enforced  
- [ ] Backups validated  

### Recommended
- [ ] Runtime security (Falco, Cilium Tetragon)  
- [ ] eBPF-based monitoring  
- [ ] Automated SOAR playbooks  

---

# 14. Completed Example

**Service:** Payments API  
**Findings:**  
- Docker image running as root → fixed  
- Environment variables contained secret tokens → moved to SSM  
- IAM role overly permissive → tightened  
- TLS missing on staging ingress → added cert-manager  
- No IaC scanning → added tfsec + Checkov  

**Status:** Hardened  
**Next Review:** 90 days  

---

# END
```
