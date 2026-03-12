```markdown
# Google Cloud Operations Template (DevOps)

*Purpose: A production-ready GCP operations template for compute, GKE, networking, IAM, Cloud Logging/Monitoring, scaling, and incident response.*

---

# 1. Overview

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  

**Task Type:**  
- [ ] GKE deployment  
- [ ] IAM config  
- [ ] VPC networking  
- [ ] Cloud Run deployment  
- [ ] Cloud Functions  
- [ ] Load balancer config  
- [ ] Artifact Registry  
- [ ] Incident response  

---

# 2. Core GCP Architecture Patterns

## 2.1 VPC Design

Checklist:
- [ ] Regional VPC  
- [ ] Separate subnets per tier  
- [ ] Private service access for databases  
- [ ] Firewall rules least-privilege  
- [ ] Cloud NAT for egress  
- [ ] No public IPs unless needed  

---

# 3. GKE Operations

## 3.1 Deployment

```

kubectl apply -f deployment.yaml
kubectl rollout status deployment/app

```

Checklist:
- [ ] Use Workload Identity  
- [ ] Autopilot vs Standard decision documented  
- [ ] Node pool autoscaling enabled  
- [ ] PodDisruptionBudgets for production  
- [ ] Cloud Logging + Cloud Monitoring configured  

---

## 3.2 GKE Node Pool Management

```

gcloud container node-pools upgrade <pool> \
  --cluster <cluster> --region <region>

```

Checklist:
- [ ] Surge upgrades enabled  
- [ ] Rolling update tested  
- [ ] Version skew validated  

---

# 4. Cloud Run Operations

## 4.1 Deploy

```

gcloud run deploy <service> \
  --image gcr.io/<project>/<image>:tag \
  --region <region> \
  --platform managed

```

Checklist:
- [ ] Concurrency set appropriately  
- [ ] VPC connector for private services  
- [ ] Min instances for warm starts  
- [ ] IAM: no unauthenticated access unless intended  

---

# 5. IAM Best Practices

Checklist:
- [ ] Use IAM roles, not primitive Owner/Editor  
- [ ] Service accounts for workloads  
- [ ] Workload Identity for GKE  
- [ ] Keyless auth preferred  
- [ ] No long-lived SA keys  
- [ ] IAM Recommender reviewed regularly  

---

# 6. Cloud Storage (GCS)

Checklist:
- [ ] Uniform bucket-level access enabled  
- [ ] Bucket encryption (KMS)  
- [ ] Retention policy enforced  
- [ ] Access logs enabled  
- [ ] Avoid publicly readable buckets  

---

# 7. Cloud Logging & Monitoring

## 7.1 Logging

```

gcloud logging read "resource.type=gke_container" --limit 50

```

Checklist:
- [ ] Logs routed to SIEM if required  
- [ ] Log-based metrics created  
- [ ] Retention configured  

---

## 7.2 Monitoring

Key metrics:
- L7 LB latency  
- GKE pod restarts  
- CPU, memory, throttling  
- Pub/Sub backlog  
- Cloud Run cold starts  

Checklist:
- [ ] Alerts on high latency & errors  
- [ ] Dashboards per microservice  
- [ ] SLOs implemented via Cloud Monitoring  

---

# 8. Pub/Sub Operations

```

gcloud pubsub subscriptions describe <sub>

```

Checklist:
- [ ] Backlog monitored  
- [ ] Dead-letter topics configured  
- [ ] Message retention configured  

---

# 9. SQL / Spanner / Firestore

## Cloud SQL
- [ ] Automated backups enabled  
- [ ] Failover replicas configured  
- [ ] High CPU & connection alerts  

## Spanner
- [ ] Multi-region if required  
- [ ] Workload isolation  

## Firestore
- [ ] Security rules validation  
- [ ] Indexes verified  

---

# 10. Incident Response (GCP)

## High Latency
- Check GKE workloads  
- Check load balancer capacity  
- Scale Cloud Run or GKE pods  

## GKE Pod Failures
- `kubectl describe pod`  
- Node pool issues  
- Resource limits too low  

## IAM Denied
- Check IAM role  
- Check service account  
- Check access boundary policies  

---

# 11. Final GCP Ops Checklist

- [ ] IAM least privilege  
- [ ] No public buckets  
- [ ] GKE Workload Identity  
- [ ] Autopilot/Standard documented  
- [ ] Monitoring + SLOs configured  
- [ ] Pub/Sub backlog safe  
- [ ] Backups tested  

---

# END
```
