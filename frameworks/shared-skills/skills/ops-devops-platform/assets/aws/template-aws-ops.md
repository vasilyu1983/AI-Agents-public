```markdown
# AWS Operations Template (DevOps)

*Purpose: A comprehensive operational template for running, deploying, securing, diagnosing, and managing workloads on AWS.*

---

# 1. Overview

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-account  

**Task Type:**  
- [ ] Deploy service  
- [ ] IAM configuration  
- [ ] Networking (VPC, SGs, Subnets)  
- [ ] ECS/EKS operations  
- [ ] S3 operations  
- [ ] RDS/ElastiCache changes  
- [ ] Scaling  
- [ ] Monitoring/CloudWatch  
- [ ] Incident Response  

---

# 2. Core AWS Architecture Patterns

## 2.1 VPC Baseline

Checklist:
- [ ] Multi-AZ subnets (public, private)  
- [ ] Private subnets for services  
- [ ] Public subnets only for LBs  
- [ ] NAT Gateways for outbound traffic  
- [ ] SGs least privilege  
- [ ] NACLs optional unless strict segmentation required  

---

## 2.2 EKS Deployment Pattern

```

kubectl apply -f deployment.yaml
kubectl rollout status deployment/app

```

Checklist:
- [ ] IAM roles for service accounts (IRSA) used  
- [ ] Cluster autoscaler installed  
- [ ] Nodegroups updated safely  
- [ ] ALB ingress or NLB configured  
- [ ] CloudWatch Container Insights enabled  

---

## 2.3 ECS Fargate Deployment

```

aws ecs update-service \
  --cluster <cluster> \
  --service <service> \
  --force-new-deployment

```

Checklist:
- [ ] Task definitions versioned  
- [ ] CPU/memory set  
- [ ] Task role least-privilege  
- [ ] LB health checks configured  

---

## 2.4 Lambda Deployment

```

aws lambda update-function-code \
  --function-name <name> \
  --zip-file fileb://function.zip

```

Checklist:
- [ ] Timeout < 30s  
- [ ] Memory tuned  
- [ ] Retries & DLQ configured  
- [ ] CloudWatch alarms created  

---

# 3. IAM Operations

## 3.1 IAM Least Privilege Checklist

- [ ] No wildcard: “\*” permissions  
- [ ] Separate roles: Admin / Deploy / ReadOnly  
- [ ] Rotate IAM keys every 90 days or disable  
- [ ] Use IAM roles for workloads (EKS IRSA / ECS Task Roles)  
- [ ] MFA required for human users  
- [ ] No inline policies  

---

# 4. S3 Operations

## 4.1 Secure Bucket

Checklist:
- [ ] Block public access enabled  
- [ ] Versioning enabled  
- [ ] SSE-KMS encryption  
- [ ] Lifecycle rules active  
- [ ] Access restricted to IAM roles  

---

# 5. CloudWatch Monitoring

## 5.1 Key Metrics

- CPUUtilization  
- Memory (CW Agent/Container Insights)  
- ALB 5xx errors  
- API Gateway errors  
- Lambda duration & errors  
- RDS CPU, connections, free storage  

---

## 5.2 Logs

```

aws logs tail /aws/lambda/<function> --follow

```

Checklist:
- [ ] Log retention configured  
- [ ] Structured JSON logs  
- [ ] Metric filters created  

---

# 6. RDS & Database Ops

## 6.1 Failover

```

aws rds reboot-db-instance --db-instance-identifier <id> --force-failover

```

Checklist:
- [ ] Backups verified  
- [ ] Multi-AZ required for prod  
- [ ] Enhanced monitoring enabled  

---

## 6.2 Parameter Group Updates
- Apply during maintenance window unless safe  
- Reboot required depending on parameter type  

---

# 7. Scaling & Auto Scaling

## 7.1 EC2 ASG

Checklist:
- [ ] Health checks green  
- [ ] Warm pools optional  
- [ ] Scheduled scaling for predictable peaks  

## 7.2 DynamoDB Auto Scaling

Checklist:
- [ ] Read/write capacity policies set  
- [ ] Throttles monitored  

---

# 8. Incident Response (AWS)

## 8.1 High CPU on EC2

- Check `top`  
- Check CloudWatch metrics  
- Scale ASG or fix noisy neighbor  

## 8.2 ALB 5xx Spikes

- Check target health  
- Check EKS/ECS logs  
- Restart failing tasks  

## 8.3 S3 Access Denied

- Check IAM role  
- Check bucket policies  
- Check block public access  

---

# 9. Final AWS Ops Checklist

- [ ] IAM least privilege  
- [ ] Encryption everywhere  
- [ ] Monitoring/alerts configured  
- [ ] Multi-AZ for all critical resources  
- [ ] Backups validated  
- [ ] Versioning & lifecycle rules  
- [ ] Logs retained properly  
- [ ] Autoscaling configured  

---

# END
```
