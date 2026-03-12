```markdown
# SQL Security & Audit Template

*Purpose: A complete operational checklist and documentation template for performing SQL security reviews, privilege audits, PII assessments, and compliance-focused database evaluations.*

---

# 1. Overview

**Environment:**  
- [ ] Production  
- [ ] Staging  
- [ ] Development  

**Database:**  
- [ ] Postgres  
- [ ] MySQL  
- [ ] MariaDB  
- [ ] Other: __________

**Scope of Audit:**  
- [ ] SQL injection review  
- [ ] Privilege/role audit  
- [ ] PII classification  
- [ ] Encryption review  
- [ ] Logging & audit trails  
- [ ] Compliance check (HIPAA/GDPR/SOX/PCI)  
- [ ] Network access controls  
- [ ] Data retention & deletion policy  

**Date:**  
[YYYY-MM-DD]  
**Auditor:**  
[Name]

---

# 2. SQL Injection Audit

### 2.1 Application Query Review

Check all relevant parts of the stack:

- [ ] All queries use parameters (no string interpolation)  
- [ ] ORM uses prepared statements  
- [ ] Dynamic SQL validated or rewritten  
- [ ] No concatenated conditions  
- [ ] No unsafe LIKE patterns with user input  
- [ ] No user input inside ORDER BY without whitelist validation  
- [ ] Sanitization functions applied when appropriate  

### 2.2 Direct SQL Interaction

- [ ] No direct SQL from UI components  
- [ ] No unsafe admin consoles  
- [ ] No ad-hoc manual scripts in production  
- [ ] No unreviewed stored procedures with dynamic SQL  

---

# 3. Privilege & Role Audit

### 3.1 Role Inventory

Paste current roles:

```

<list of roles, grants, and inheritance>

```

### 3.2 Check for Risks

- [ ] No SUPERUSER roles (Postgres)  
- [ ] No ALL PRIVILEGES grants (MySQL, Postgres)  
- [ ] No developers with production write access  
- [ ] Application roles follow least-privilege  
- [ ] Read-only roles truly read-only  
- [ ] Admin roles restricted to DBAs/SRE  
- [ ] No stale or unused roles > 90 days  
- [ ] Passwordless accounts reviewed  
- [ ] Rotation policy in place  

### 3.3 Privilege Escalation Checks

- [ ] No role inheritance that grants broad access  
- [ ] No ability to modify schemas without approval  
- [ ] No ability to disable audit logs  
- [ ] No ability to drop critical tables or indexes  
- [ ] No proxy roles with uncontrolled access  

---

# 4. Network & Access Controls

- [ ] Database not publicly accessible  
- [ ] Firewall restrictions applied  
- [ ] Allowlist enforced  
- [ ] TLS enforced for all connections  
- [ ] No plaintext credentials in code repos  
- [ ] Secrets stored in vault manager (AWS SecretManager, Vault, etc.)  
- [ ] IAM / service accounts use short-lived tokens  
- [ ] No hard-coded passwords in config files  

---

# 5. Data Classification & PII/PHI Review

### 5.1 Data Categories

Mark all applicable:

- [ ] Personal data (PII)  
- [ ] Financial data  
- [ ] Healthcare data (PHI)  
- [ ] Authentication data  
- [ ] Logs containing user identifiers  
- [ ] Transactional data  

### 5.2 PII Storage Rules

- [ ] Minimal retention  
- [ ] Proper deletion supported (GDPR 17)  
- [ ] Pseudonymization where possible  
- [ ] PII encrypted at rest  
- [ ] PII encrypted in transit  
- [ ] Audit logs exclude sensitive fields  
- [ ] No unnecessary duplication of PII across tables  

---

# 6. Encryption Review

### 6.1 Encryption at Rest

- [ ] Disk-level encryption enabled  
- [ ] Key rotation policy documented  
- [ ] Encrypted snapshots/backups  
- [ ] WAL/binlogs encrypted  
- [ ] TDE support evaluated (if applicable)  

### 6.2 Encryption in Transit

- [ ] TLS enforced for connections  
- [ ] Client certificates validated  
- [ ] SSLMode=verify-full (Postgres) where required  
- [ ] No plaintext connections allowed  

---

# 7. Logging & Audit Trails

### 7.1 Database Audit Logging

Check:

- [ ] SELECT audit for sensitive tables  
- [ ] DDL changes logged  
- [ ] Failed logins logged  
- [ ] Permission changes logged  
- [ ] Superuser actions logged  
- [ ] Query logs sanitized  

### 7.2 Log Storage & Privacy

- [ ] Logs encrypted in storage  
- [ ] No sensitive data in logs  
- [ ] Retention policy applied  
- [ ] Access to logs locked down  

---

# 8. Backup & Disaster Recovery Security

- [ ] Backups encrypted  
- [ ] Backup access restricted  
- [ ] Restore tested recently  
- [ ] PITR logs protected  
- [ ] Backups stored in separate region  
- [ ] Backups not left on local disk  
- [ ] Backups exclude unnecessary PII when possible  

---

# 9. Compliance Checks

Check if relevant:

## 9.1 GDPR
- [ ] Right-to-erasure implemented  
- [ ] Data minimization applied  
- [ ] Data export capability  

## 9.2 PCI
- [ ] Card data isolated  
- [ ] Encryption validated  
- [ ] Access restricted  

## 9.3 HIPAA
- [ ] PHI encrypted  
- [ ] Access logging enabled  
- [ ] Breach detection documented  

## 9.4 SOX
- [ ] DDL approvals required  
- [ ] Separate duties for review & execution  
- [ ] Change tracking enforced  

---

# 10. Security Red Flags (Yes = Bad)

| Issue | Yes/No | Notes |
|-------|--------|--------|
| Public DB endpoint | | |
| SUPERUSER accounts | | |
| No TLS | | |
| SQL injection vectors found | | |
| Sensitive logs | | |
| PII stored unencrypted | | |
| Weak passwords | | |
| No password rotation | | |
| Missing audit logs | | |
| Stale roles | | |
| Secrets in code repos | | |

---

# 11. Recommended Fixes

List actionable changes:

1.  
2.  
3.  
4.  

Each fix should include:  
- Expected impact  
- Owner  
- Timeline  
- Risk level  

---

# 12. Final Audit Conclusion

**Overall Security Posture:**  
- [ ] Excellent  
- [ ] Good  
- [ ] Needs Improvement  
- [ ] High Risk  

**Auditor Notes:**  
[Write conclusions]

**Next Review Due:**  
[Date]

---

# 13. Example Completed Audit

**Environment:** Production  
**DB:** Postgres 14  
**Findings:**  
- Stale read-only role with expired password (fixed)  
- Missing TLS enforcement (added `ssl=on`)  
- Logs contained raw emails (updated sanitizer)  
- SUPERUSER used for app migrations (moved to scoped role)  

**Final Rating:** Needs improvement, critical issues resolved.

---

# END
```
