```markdown
# SQL Backup & Restore Template (DR-Ready)

*Purpose: A complete template for planning, executing, validating, and documenting database backups, restores, retention policies, DR scenarios, and integrity verification.*

---

## 1. Backup Overview

**Database:**  
- [ ] Postgres  
- [ ] MySQL  
- [ ] Other: ____________

**Environment:**  
- [ ] Production  
- [ ] Staging  
- [ ] Development  

**Reason for Backup:**  
- [ ] Scheduled backup  
- [ ] Pre-deployment snapshot  
- [ ] Pre-migration backup  
- [ ] Pre-index rebuild  
- [ ] Manual request  
- [ ] DR simulation  

**Requested By:**  
[Name]

**Date:**  
[YYYY-MM-DD]

---

## 2. Backup Configuration Summary

| Item | Value |
|------|--------|
| Backup Type | Full / Incremental / Differential / PITR |
| Target Storage | S3 / GCS / Local / NFS / Blob |
| Encryption | Yes/No |
| Compression | Yes/No |
| Retention Period | days/weeks/months |
| Expected Backup Size | |
| Expected Time Window | |
| Performance Impact | Low / Medium / High |

---

## 3. Backup Command(s)

### 3.1 Postgres

**Full Backup (pg_dump):**
```

pg_dump -Fc -Z9 -f backup_$(date +%F).dump <database_name>

```

**Physical Backup (pg_basebackup):**
```

pg_basebackup -D /backups/base -Ft -z -P -X stream

```

**WAL Archiving (PITR):**
```

archive_command = 'cp %p /wal-archive/%f'

```

---

### 3.2 MySQL

**Logical Backup (mysqldump):**
```

mysqldump --single-transaction --routines --events --quick <database> \
  | gzip > backup_$(date +%F).sql.gz

```

**Physical Backup (XtraBackup):**
```

xtrabackup --backup --target-dir=/backups/base

```

**Binlog Backup:**
```

mysqlbinlog --read-from-remote-server --raw \
  --result-file=/binlogs <host-binlog-index>

```

---

## 4. Backup Verification Steps

### 4.1 Structural Verification
- [ ] File exists  
- [ ] File size reasonable  
- [ ] Not truncated  
- [ ] Checksums verified  
- [ ] Backup metadata stored  

### 4.2 Logical Verification (recommended weekly)
```

pg_restore --list backup.dump

```
or
```

mysql --execute="SHOW TABLES;"

```

Checklist:
- [ ] Table count matches  
- [ ] Schema versions match  
- [ ] No corrupted dump entries  

---

## 5. Restore Plan (Dry Run Recommended)

### 5.1 Restore Summary

**Restore Type:**  
- [ ] Full  
- [ ] PITR  
- [ ] Table-level restore  
- [ ] Point snapshot recovery  
- [ ] Replica rebuild  

**Destination:**  
- [ ] Local instance  
- [ ] Staging environment  
- [ ] New production node  
- [ ] On-demand restore environment  

---

## 6. Restore Commands

### 6.1 Postgres

**Full Restore:**
```

createdb restored_db
pg_restore -Fc -j 4 -d restored_db backup.dump

```

**PITR Restore:**  
(Requires WAL archive)

```

restore_command = 'cp /wal-archive/%f %p'
recovery_target_time = '2023-05-10 18:00:00'

```

---

### 6.2 MySQL

**Logical Restore:**
```

gunzip < backup.sql.gz | mysql restored_db

```

**XtraBackup Restore:**
```

xtrabackup --prepare --target-dir=/backups/base
xtrabackup --copy-back --target-dir=/backups/base

```

---

## 7. Recovery Validation

### 7.1 Logical Validation
- [ ] Row count diff < 0.1%  
- [ ] Index structures valid  
- [ ] Constraints validated  
- [ ] Application queries tested  

### 7.2 Functional Validation
- [ ] Key API endpoints work  
- [ ] No missing reference data  
- [ ] Views and functions compile  
- [ ] Time-based lookups validated  

### 7.3 Performance Validation
- [ ] Slow queries not regressed  
- [ ] Indexes used correctly  
- [ ] No unexpected locks  

---

## 8. Retention & Rotation Plan

| Backup Type | Frequency | Retention | Location |
|-------------|-----------|-----------|----------|
| Full | Daily | 30 days | S3 |
| WAL/Binlog | Every 5 min | 7 days | S3 |
| Snapshots | Weekly | 12 weeks | Cloud provider |

Checklist:
- [ ] Automated cleanup enabled  
- [ ] Archive lifecycle rules configured  
- [ ] Offsite/region redundancy verified  

---

## 9. DR (Disaster Recovery) Capability

### 9.1 RPO (Recovery Point Objective)
Target: [e.g., ≤ 5 minutes]

Actual Achieved:  
[Value collected from binlog/WAL frequency]

### 9.2 RTO (Recovery Time Objective)
Target: [e.g., ≤ 30 minutes]

Actual Achieved:  
[Test restoration speed]

### 9.3 DR Test Summary
- [ ] Annual full DR drill  
- [ ] Quarterly restore validation  
- [ ] Replica rebuild tested  
- [ ] Restore from oldest backup tested  

---

## 10. Failure Scenarios & Procedures

### 10.1 Corruption
- Recover from last known good backup  
- Validate via row count & checksum  

### 10.2 Accidental Deletes/Drops
- Use PITR logs to restore  
- Apply filtered restore
  
### 10.3 Bad Deployment
- Roll forward via restore into shadow DB  
- Compare diffs  

### 10.4 Replica Desync
- Rebuild replica from backup  
- Apply logs until consistent  

---

## 11. Final Approval

| Role | Approved? | Name | Date |
|------|-----------|-------|-------|
| SQL Engineer | [ ] | | |
| DBA | [ ] | | |
| SRE / Platform | [ ] | | |
| Security | [ ] | | |

---

## 12. Completed Example

**Scenario:**  
PITR restore required due to accidental mass deletion.

**Backup Used:**  
`pg_basebackup` + WAL archive

**Restore Commands:**
```

createdb recovered_db
pg_restore -d recovered_db backup.dump

```

Replay WAL to target time:
```

recovery_target_time = '2023-05-10 18:33:01'

```

**Verification:**  
[check] Records restored  
[check] No index corruption  
[check] RTO: 18 minutes  
[check] RPO: < 60 seconds  

---

# END
```
