```markdown
# Azure Cloud Operations Template (DevOps)

*Purpose: A full operational template for Azure Kubernetes Service (AKS), Azure Functions, networking, identity, monitoring, and infrastructure operations.*

---

# 1. Overview

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  

**Task Type:**  
- [ ] AKS deployment  
- [ ] ACR image push  
- [ ] VMSS scaling  
- [ ] Networking (VNet/Subnets/NSG)  
- [ ] Key Vault operations  
- [ ] App Service / Functions deploy  
- [ ] Azure Monitor setup  
- [ ] Incident response  

---

# 2. Core Azure Architectures

## 2.1 VNet Architecture

Checklist:
- [ ] Hub-and-spoke or flat VNet defined  
- [ ] Private endpoints used  
- [ ] NSGs with least privilege rules  
- [ ] No public IP for internal services  

---

# 3. AKS Operations

## 3.1 Deployment

```

kubectl apply -f deployment.yaml
kubectl rollout status deployment/app

```

Checklist:
- [ ] Managed identity for pods  
- [ ] Azure CNI vs Kubenet decision documented  
- [ ] Autoscaler enabled  
- [ ] Node pools separated (system/user)  
- [ ] Azure Monitor for containers enabled  

---

## 3.2 AKS Node Pool Upgrade

```

az aks nodepool upgrade \
  --resource-group <rg> \
  --cluster-name <cluster> \
  --name <pool> \
  --kubernetes-version <version>

```

Checklist:
- [ ] Zero-downtime validated  
- [ ] PDBs in place  
- [ ] Surge upgrades configured  

---

# 4. Azure Container Registry (ACR)

## Build & Push

```

az acr build --registry <acr-name> --image app:<tag> .

```

Checklist:
- [ ] ACR firewall rules configured  
- [ ] Only managed identities access  
- [ ] Image scanning enabled  

---

# 5. Azure App Service & Functions

## App Service Deploy

```

az webapp deploy \
  --resource-group <rg> \
  --name <app> \
  --src-path app.zip

```

Checklist:
- [ ] Health checks configured  
- [ ] Autoscale rules defined  
- [ ] App Insights enabled  

---

## Azure Functions Deploy

```

func azure functionapp publish <app-name>

```

Checklist:
- [ ] Consumption vs Premium tier selected properly  
- [ ] Cold start impact measured  
- [ ] Logging enabled  

---

# 6. Identity & Key Vault

## Key Vault Checklist

- [ ] Secrets stored in Vault only  
- [ ] RBAC mode enabled  
- [ ] Private endpoints enabled  
- [ ] Soft delete + purge protection  
- [ ] Managed identities for apps  

---

# 7. Azure Monitor & Logging

## Monitor Metrics

- CPU / Memory  
- AKS node/pod health  
- App Insights performance  
- Storage queue length  
- API latency  

## Log Analytics Queries (KQL)

```

ContainerLog
| where LogEntry contains "error"

```

Checklist:
- [ ] Alerts configured  
- [ ] Dashboards created  
- [ ] SLOs tracked  

---

# 8. Scaling & Autoscaling

## VMSS

```

az vmss scale \
  --name <vmss> \
  --new-capacity 5 \
  --resource-group <rg>

```

Checklist:
- [ ] Autoscale rules defined  
- [ ] CPU/memory thresholds correct  
- [ ] Health probe validated  

---

# 9. Incident Response (Azure)

## App Down

- Check App Service health  
- Check logs in App Insights  
- Check regional outage notifications  
- Restart App Service  

## AKS Issues

- `kubectl describe pod`  
- Check ACR access  
- Node pool exhaustion  
- API server throttling  

## Storage Account Issues

- Check firewall/endpoint config  
- Check queue backlog  
- Check availability events  

---

# 10. Final Azure Ops Checklist

- [ ] Use managed identities  
- [ ] Network security (NSG + private endpoints)  
- [ ] ACR + App Services access locked down  
- [ ] Logging + Alerts configured  
- [ ] Application Insights dashboards  
- [ ] Scaling validated  
- [ ] Backups tested  

---

# END
```
