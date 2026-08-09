# LLM Deployment Checklist Template

*Purpose: Field-ready checklist and playbook for safely deploying LLMs, RAG, or agentic systems to staging and production environments, with rollback, monitoring, and post-deploy quality gates.*

---

## When to Use

Use this template when:

- Releasing a new LLM-powered app, RAG/agentic service, or major update
- Moving from development/staging to production
- Need to pass security, compliance, and LLMOps review before go-live

---

## Structure

This template has 5 main sections:

1. **Preflight Readiness** – staging, tests, and backup
2. **Deployment Rollout** – staged, canary, or blue/green releases
3. **Monitoring & Observability** – latency, cost, usage, error, and abuse monitoring
4. **Incident & Rollback Plan** – what to do if critical metrics fail or bugs are found
5. **Post-Deployment Review** – quality gates, regression checks, and user feedback

---

# TEMPLATE STARTS HERE

## 1. Preflight Readiness

- [ ] All code, prompts, models, and pipeline configs in version control
- [ ] Regression, edge-case, and adversarial tests all passing
- [ ] Data pipeline/feeds validated and locked
- [ ] “Last known good” model/pipeline checkpoint archived
- [ ] Access/secret management reviewed (keys, API tokens, RBAC)
- [ ] Staging environment matches production as closely as possible

## 2. Deployment Rollout

- [ ] Deploy to staging and run smoke/regression tests
- [ ] Canary/blue-green: Route small % of traffic to new model/service first
- [ ] Monitor all key metrics live; abort if critical issues seen
- [ ] Full rollout only after canary passes quality gates

## 3. Monitoring & Observability

- [ ] Logs for all requests, outputs, and errors enabled
- [ ] Dashboards for latency (p50/p95), usage, and cost live
- [ ] Real-time alerts for high error, OOM, safety/abuse events
- [ ] Prompts and models versioned and tracked in all logs
- [ ] Output sampling for manual review

## 4. Incident & Rollback Plan

- [ ] Documented, tested rollback script (to last stable version)
- [ ] Incident thresholds: latency, hallucination, outage, cost, safety
- [ ] Escalation path for on-call/response (24/7 for critical prod)
- [ ] Failover or fallback model available if primary fails

## 5. Post-Deployment Review

- [ ] All quality gates (accuracy, faithfulness, latency, safety, cost) passed in prod
- [ ] Edge/adversarial cases checked live
- [ ] User feedback and error/abuse reports monitored daily
- [ ] Weekly regression re-run after go-live
- [ ] Archive all logs, incidents, and test results for audit

---

# COMPLETE PLAYBOOK EXAMPLE

**LLM/RAG/Agentic Prod Release Flow**

```
1. Freeze code, data, prompt, and model versions.
2. Run full test suite in staging; archive passing logs.
3. Deploy canary to 5% of users/traffic.
4. Monitor: latency <2s, hallucination <3%, error rate <1%.
5. If metrics pass after X hours, rollout to 100%.
6. If any incident threshold hit:
   - Roll back to last stable deploy (scripted)
   - Notify on-call, triage root cause, fix or hot-patch
7. Post-launch: Sample outputs, gather user feedback, schedule postmortem.
8. Document all failures, actions, and lessons for future deployments.
```

---

## Release-Readiness Checklist

- [ ] All code/prompt/model/data versioned and auditable
- [ ] Regression, edge, and abuse tests passing in prod
- [ ] Canary/staged rollout configured and tested
- [ ] Live monitoring and alerting enabled for all critical metrics
- [ ] Incident rollback and on-call escalation documented and tested
- [ ] All deployment, monitoring, and rollback steps reviewed by ops/QA/lead

---

*For ongoing monitoring, see [references/llmops-best-practices.md]. For eval patterns and emergency playbooks, see [references/eval-patterns.md].*
