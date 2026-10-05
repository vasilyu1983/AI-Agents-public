```markdown
# Platform Team API / Self-Service Template

*Purpose: A template for defining an internal platform team’s API: services, self-service flows, SLAs, onboarding, and expectations between platform and product teams.*

---

# 1. Platform Overview

**Platform Name:**  
[e.g., “Internal Dev Platform”, “K8s Platform”, “Data Platform”]

**Owning Team:**  
[Platform team name]

**Supported Environments:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  

**Primary Customers:**  
- [ ] Product teams  
- [ ] Data teams  
- [ ] SRE  
- [ ] Other platform teams  

---

# 2. Platform Services Catalog

List platform capabilities as services.

| Service | Description | Interface | SLA | Owner |
|--------|-------------|-----------|-----|--------|
| app-runtime | run containerized services | GitOps / APIs | 99.9% | |
| ci-pipeline | standard CI templates | YAML/Actions | best effort | |
| db-provisioning | managed databases | ticket/API | 99.9% | |

---

# 3. Self-Service Flows

## 3.1 Service Onboarding Flow

Steps:
1. Product team submits service definition (name, team, runtime, SLOs)  
2. Platform team reviews and approves  
3. CI/CD template provisioned  
4. K8s namespace or tenancy created  
5. Observability baseline deployed  

Checklist:
- [ ] Minimal required info clear  
- [ ] Automated bootstrap where possible  
- [ ] Docs link for onboarding  

---

## 3.2 Standard “Golden Path” Pipeline

Templates provided:
- Build & test  
- Security scan  
- Deployment to K8s/ECS  
- Observability wiring (metrics/logs/traces)  

Checklist:
- [ ] Golden path documented  
- [ ] Deviations understood and approved  

---

# 4. Platform API Definition

## 4.1 Interface Types

- [ ] GitOps repo conventions  
- [ ] CLI  
- [ ] REST/GraphQL APIs  
- [ ] Service catalog UI  

For each API:

| Endpoint / Path | Method | Purpose | Auth |
|-----------------|--------|---------|------|
| `/services/register` | POST | register service | SSO/Token |

---

# 5. SLAs / SLOs for Platform

## Example SLOs:

- Control plane uptime: 99.9%  
- Build pipeline availability: 99.5%  
- New environment creation: < 1 hour  
- Incident response: < 15 minutes for P1  

Checklist:
- [ ] Platform SLOs defined  
- [ ] Error budgets in place  
- [ ] Communication when SLOs breached  

---

# 6. Responsibilities & Expectations

## 6.1 Platform Team Responsibilities

- Provide secure, reliable runtimes  
- Maintain tooling and workflows  
- Document usage and constraints  
- Offer enablement / consulting  

## 6.2 Product Team Responsibilities

- Build and own their services  
- Integrate with observability baselines  
- Use golden path where possible  
- Participate in incident resolution  

---

# 7. Onboarding & Documentation

Checklist:
- [ ] “Getting Started” guide  
- [ ] Service onboarding guide  
- [ ] CI/CD templates documented  
- [ ] Platform APIs documented  
- [ ] Runbooks provided  

---

# 8. Support & Escalation

Define channels:

- Slack: `#platform-support`  
- Ticket queue: [link]  
- Office hours: [times]  

Checklist:
- [ ] SLAs for response times  
- [ ] Routing of issues to correct team  

---

# 9. Operational Metrics

Track:

- Time to onboard new service  
- # services on golden path vs custom  
- Platform incidents / downtime  
- Feedback from product teams  

---

# 10. Completed Example

**Platform:** Cloud App Platform  
**Services:**  
- Runtime-as-a-Service (K8s)  
- CI/CD pipeline library  
- Database-as-a-Service  

**API:** GitOps + portal UI  
**SLO:** 99.9% platform availability  

---

# END
```
