# Compliance Testing

Compliance testing patterns for regulated environments -- automating audit evidence, validating security controls, and enforcing policy-as-code for SOC 2, HIPAA, GDPR, and PCI-DSS.

## Contents

- Compliance Standards Overview
- Compliance-as-Code
- Audit Evidence Automation
- Access Control Testing
- Data Residency Verification
- Encryption Validation
- PII Handling Tests
- Data Retention Policy Enforcement
- Audit Log Completeness Testing
- Penetration Testing Requirements
- Vulnerability Scanning Cadence
- Compliance Test Matrices
- CI Integration for Compliance Gates
- Documentation and Evidence Collection
- Compliance Testing Checklist
- Related Resources

---

## Compliance Standards Overview

| Standard | Scope | Key Requirements | Applies To |
|----------|-------|-----------------|------------|
| **SOC 2** | Service organizations | Security, availability, processing integrity, confidentiality, privacy | SaaS, cloud services |
| **HIPAA** | Healthcare data | PHI protection, access controls, audit trails, encryption | Healthcare apps |
| **GDPR** | EU personal data | Consent, right to erasure, data portability, breach notification | Any app with EU users |
| **PCI-DSS** | Payment card data | Cardholder data protection, network security, access control | E-commerce, payments |

### Testing Obligations by Standard

| Testing Type | SOC 2 | HIPAA | GDPR | PCI-DSS |
|-------------|-------|-------|------|---------|
| Access control testing | Required | Required | Required | Required |
| Encryption validation | Required | Required | Required | Required |
| Audit log testing | Required | Required | Recommended | Required |
| Penetration testing | Recommended | Required | Recommended | Required (annual) |
| Vulnerability scanning | Recommended | Required | Recommended | Required (quarterly) |
| Data retention testing | Recommended | Required | Required | Required |
| Incident response testing | Recommended | Required | Required | Required |

---

## Compliance-as-Code

### Chef InSpec

InSpec defines compliance controls as testable code. Each control maps to a specific regulatory requirement.

```ruby
# controls/encryption.rb
control 'ENCRYPT-001' do
  impact 1.0
  title 'Data at rest must be encrypted'
  desc 'All database volumes and storage must use AES-256 encryption.'
  tag compliance: ['SOC2-CC6.1', 'HIPAA-164.312(a)(2)(iv)', 'PCI-DSS-3.4']

  describe aws_ebs_volumes do
    it { should exist }
    its('entries') { should all(be_encrypted) }
  end

  describe aws_rds_instances do
    it { should exist }
    its('entries') { should all(have_storage_encrypted) }
  end

  describe aws_s3_buckets do
    it { should exist }
  end
end

control 'ENCRYPT-002' do
  impact 1.0
  title 'Data in transit must use TLS 1.2+'
  desc 'All external endpoints must enforce TLS 1.2 or higher.'
  tag compliance: ['SOC2-CC6.7', 'PCI-DSS-4.1']

  describe ssl(host: 'api.example.com', port: 443) do
    it { should be_enabled }
    its('protocols') { should_not include 'ssl2' }
    its('protocols') { should_not include 'ssl3' }
    its('protocols') { should_not include 'tls1.0' }
    its('protocols') { should_not include 'tls1.1' }
  end
end
```

```bash
# Run InSpec compliance checks
inspec exec controls/ --reporter cli json:results/compliance-report.json
```

### Open Policy Agent (OPA)

OPA validates infrastructure configurations and API requests against policy.

```rego
# policy/data_residency.rego
package compliance.data_residency

# GDPR: EU data must stay in EU regions
allowed_eu_regions := {"eu-west-1", "eu-west-2", "eu-central-1", "eu-north-1"}

deny[msg] {
    resource := input.resources[_]
    resource.type == "aws_rds_instance"
    resource.tags.data_classification == "eu_personal_data"
    not allowed_eu_regions[resource.region]
    msg := sprintf(
        "RDS instance '%s' with EU personal data is in non-EU region '%s'",
        [resource.name, resource.region]
    )
}

# PCI-DSS: Cardholder data must be in PCI-scoped environments
deny[msg] {
    resource := input.resources[_]
    resource.tags.data_classification == "cardholder_data"
    not resource.tags.pci_scope == "true"
    msg := sprintf(
        "Resource '%s' contains cardholder data but is not in PCI scope",
        [resource.name]
    )
}
```

```bash
# Evaluate OPA policy
opa eval --data policy/ --input infrastructure.json "data.compliance.data_residency.deny"
```

### Terraform Compliance

```python
# features/encryption.feature (BDD for Terraform)
Feature: Encryption controls
  In order to comply with SOC2 and PCI-DSS
  As an infrastructure engineer
  I need to ensure all storage is encrypted

  Scenario: All S3 buckets must be encrypted
    Given I have aws_s3_bucket defined
    Then it must have server_side_encryption_configuration

  Scenario: All RDS instances must be encrypted
    Given I have aws_rds_cluster defined
    Then it must have storage_encrypted
    And its value must be true

  Scenario: All EBS volumes must be encrypted
    Given I have aws_ebs_volume defined
    Then it must have encrypted
    And its value must be true
```

```bash
# Run terraform-compliance
terraform plan -out=plan.out
terraform show -json plan.out > plan.json
terraform-compliance -p plan.json -f features/
```

---

## Audit Evidence Automation

### Evidence Collection Pipeline

```python
#!/usr/bin/env python3
"""Automated audit evidence collection for SOC2/HIPAA."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

def collect_evidence(output_dir: str = "audit-evidence"):
    """Collect compliance evidence artifacts."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    evidence_dir = Path(output_dir) / timestamp
    evidence_dir.mkdir(parents=True, exist_ok=True)

    evidence = {}

    # 1. Infrastructure compliance scan
    result = subprocess.run(
        ["inspec", "exec", "controls/", "--reporter", "json"],
        capture_output=True, text=True
    )
    (evidence_dir / "inspec-results.json").write_text(result.stdout)
    evidence["infrastructure_scan"] = {
        "tool": "Chef InSpec",
        "timestamp": timestamp,
        "file": "inspec-results.json",
    }

    # 2. Access control audit
    iam_report = subprocess.run(
        ["aws", "iam", "generate-credential-report"],
        capture_output=True, text=True
    )
    subprocess.run(
        ["aws", "iam", "get-credential-report", "--output", "json"],
        capture_output=True, text=True,
        stdout=open(evidence_dir / "iam-credentials.json", "w")
    )
    evidence["access_control"] = {
        "tool": "AWS IAM",
        "timestamp": timestamp,
        "file": "iam-credentials.json",
    }

    # 3. Vulnerability scan results
    vuln_result = subprocess.run(
        ["trivy", "image", "--format", "json", "myapp:latest"],
        capture_output=True, text=True
    )
    (evidence_dir / "vulnerability-scan.json").write_text(vuln_result.stdout)
    evidence["vulnerability_scan"] = {
        "tool": "Trivy",
        "timestamp": timestamp,
        "file": "vulnerability-scan.json",
    }

    # Write evidence manifest
    (evidence_dir / "manifest.json").write_text(
        json.dumps(evidence, indent=2)
    )
    print(f"Evidence collected in: {evidence_dir}")

if __name__ == "__main__":
    collect_evidence()
```

### CI Evidence Collection

```yaml
# .github/workflows/compliance-evidence.yml
name: Compliance Evidence Collection
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am UTC
  workflow_dispatch:

jobs:
  collect-evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run InSpec compliance scan
        run: |
          inspec exec controls/ \
            --reporter cli json:evidence/inspec-results.json

      - name: Run vulnerability scan
        run: |
          trivy image --format json --output evidence/vuln-scan.json myapp:latest

      - name: Run access control audit
        run: python scripts/audit-access-controls.py > evidence/access-audit.json

      - name: Upload evidence artifacts
        uses: actions/upload-artifact@v4
        with:
          name: compliance-evidence-${{ github.run_id }}
          path: evidence/
          retention-days: 365  # Keep for audit period
```

---

## Access Control Testing

### RBAC Verification

```typescript
import { test, expect } from '@playwright/test';

const roles = ['admin', 'editor', 'viewer', 'guest'] as const;

const accessMatrix = {
  '/admin/users': { admin: 200, editor: 403, viewer: 403, guest: 401 },
  '/admin/settings': { admin: 200, editor: 403, viewer: 403, guest: 401 },
  '/api/posts': { admin: 200, editor: 200, viewer: 200, guest: 401 },
  '/api/posts/create': { admin: 201, editor: 201, viewer: 403, guest: 401 },
  '/api/posts/delete': { admin: 200, editor: 403, viewer: 403, guest: 401 },
};

for (const [endpoint, expected] of Object.entries(accessMatrix)) {
  for (const role of roles) {
    test(`${role} accessing ${endpoint} returns ${expected[role]}`, async ({ request }) => {
      const token = await getTokenForRole(role);
      const response = await request.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(response.status()).toBe(expected[role]);
    });
  }
}
```

### Privilege Escalation Tests

```typescript
test.describe('Privilege escalation prevention', () => {
  test('viewer cannot modify own role to admin', async ({ request }) => {
    const viewerToken = await getTokenForRole('viewer');
    const response = await request.patch('/api/users/me', {
      headers: { Authorization: `Bearer ${viewerToken}` },
      data: { role: 'admin' },
    });
    // Should either reject or ignore the role field
    expect(response.status()).toBe(403);
  });

  test('user cannot access another user private data', async ({ request }) => {
    const userAToken = await getTokenForRole('user', 'user-a@example.com');
    const response = await request.get('/api/users/user-b-id/private', {
      headers: { Authorization: `Bearer ${userAToken}` },
    });
    expect(response.status()).toBe(403);
  });
});
```

---

## Data Residency Verification

```typescript
test.describe('Data residency compliance', () => {
  test('EU user data stored in EU region', async ({ request }) => {
    // Create EU user
    const createResponse = await request.post('/api/users', {
      data: {
        email: 'eu-user@example.de',
        country: 'DE',
        name: 'Test EU User',
      },
    });
    const userId = (await createResponse.json()).id;

    // Verify storage region via admin API
    const regionResponse = await request.get(`/api/admin/data-location/${userId}`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const location = await regionResponse.json();
    expect(location.region).toMatch(/^eu-/);
    expect(location.database).toMatch(/eu-/);
  });
});
```

### Infrastructure Residency Check

```ruby
# InSpec: verify data residency
control 'GDPR-RESIDENCY-001' do
  impact 1.0
  title 'EU personal data must reside in EU regions'
  tag compliance: ['GDPR-Art.44']

  aws_rds_instances.where(tags: { data_region: 'eu' }).entries.each do |db|
    describe db do
      its('availability_zone') { should match(/^eu-/) }
    end
  end

  aws_s3_buckets.where(tags: { data_region: 'eu' }).entries.each do |bucket|
    describe bucket do
      its('region') { should match(/^eu-/) }
    end
  end
end
```

---

## Encryption Validation

### At-Rest Encryption

```ruby
# InSpec: encryption at rest
control 'ENCRYPT-AT-REST-001' do
  impact 1.0
  title 'All databases encrypted at rest with AES-256'
  tag compliance: ['SOC2-CC6.1', 'HIPAA-164.312(a)(2)(iv)', 'PCI-DSS-3.4']

  aws_rds_instances.entries.each do |db|
    describe db do
      it { should have_storage_encrypted }
    end
  end
end
```

### In-Transit Encryption

```typescript
import { test, expect } from '@playwright/test';
import https from 'https';
import tls from 'tls';

test('API endpoint enforces TLS 1.2+', async () => {
  const host = 'api.example.com';

  const result = await new Promise<tls.TLSSocket>((resolve, reject) => {
    const socket = tls.connect({ host, port: 443, servername: host }, () => {
      resolve(socket);
    });
    socket.on('error', reject);
  });

  const protocol = result.getProtocol();
  expect(['TLSv1.2', 'TLSv1.3']).toContain(protocol);

  result.destroy();
});

test('HTTP redirects to HTTPS', async ({ request }) => {
  // This test verifies HTTP to HTTPS redirect
  const response = await request.get('http://api.example.com/', {
    maxRedirects: 0,
  });
  expect(response.status()).toBe(301);
  expect(response.headers()['location']).toMatch(/^https:/);
});
```

---

## PII Handling Tests

```typescript
test.describe('PII protection', () => {
  test('PII not exposed in API responses to unauthorized roles', async ({ request }) => {
    const viewerToken = await getTokenForRole('viewer');
    const response = await request.get('/api/users', {
      headers: { Authorization: `Bearer ${viewerToken}` },
    });
    const users = await response.json();

    for (const user of users.data) {
      expect(user).not.toHaveProperty('ssn');
      expect(user).not.toHaveProperty('date_of_birth');
      expect(user.email).toMatch(/^[\w]{1,3}\*+@/); // Masked email
      expect(user.phone).toMatch(/^\*+\d{4}$/);      // Last 4 digits only
    }
  });

  test('PII not logged in application logs', async ({ request }) => {
    // Trigger an operation that processes PII
    await request.post('/api/users', {
      data: { email: 'pii-test@example.com', ssn: '123-45-6789', name: 'PII Test' },
    });

    // Check recent logs via admin API
    const logsResponse = await request.get('/api/admin/logs?last=100', {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const logs = await logsResponse.json();
    const logText = JSON.stringify(logs);

    expect(logText).not.toContain('123-45-6789');
    expect(logText).not.toContain('pii-test@example.com');
  });

  test('GDPR right to erasure works completely', async ({ request }) => {
    // Create user with PII
    const createResp = await request.post('/api/users', {
      data: { email: 'delete-me@example.com', name: 'Delete Me', phone: '+1234567890' },
    });
    const userId = (await createResp.json()).id;

    // Request erasure
    const deleteResp = await request.delete(`/api/users/${userId}/gdpr-erase`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    expect(deleteResp.status()).toBe(200);

    // Verify erasure
    const verifyResp = await request.get(`/api/admin/data-audit/${userId}`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const audit = await verifyResp.json();
    expect(audit.user_record).toBeNull();
    expect(audit.audit_logs_anonymized).toBe(true);
    expect(audit.backups_queued_for_purge).toBe(true);
  });
});
```

---

## Data Retention Policy Enforcement

```typescript
test.describe('Data retention policies', () => {
  test('expired data is purged according to policy', async ({ request }) => {
    const policyResponse = await request.get('/api/admin/retention-policies', {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const policies = await policyResponse.json();

    // Verify each policy has been enforced
    for (const policy of policies) {
      const auditResp = await request.get(
        `/api/admin/retention-audit?data_type=${policy.data_type}`,
        { headers: { Authorization: `Bearer ${adminToken}` } },
      );
      const audit = await auditResp.json();

      expect(audit.oldest_record_age_days).toBeLessThanOrEqual(policy.retention_days);
      expect(audit.expired_records_count).toBe(0);
    }
  });
});
```

### Retention Policy Matrix

| Data Type | SOC 2 | HIPAA | GDPR | PCI-DSS |
|-----------|-------|-------|------|---------|
| Audit logs | 1 year | 6 years | Per purpose | 1 year |
| User accounts | Per policy | 6 years after last interaction | Until consent withdrawn | Per policy |
| Payment data | 7 years (financial) | N/A | Minimal necessary | Until no longer needed |
| Session logs | 90 days | 6 years | 30 days | 90 days |
| Backup data | 90 days | 6 years | Same as source | 90 days |

---

## Audit Log Completeness Testing

```typescript
test.describe('Audit log completeness', () => {
  const auditableActions = [
    { action: 'user.login', trigger: () => login('test@example.com') },
    { action: 'user.logout', trigger: () => logout() },
    { action: 'user.create', trigger: () => createUser({ email: 'new@example.com' }) },
    { action: 'user.delete', trigger: () => deleteUser('test-user-id') },
    { action: 'data.export', trigger: () => exportData('users') },
    { action: 'settings.change', trigger: () => updateSettings({ mfa: true }) },
    { action: 'permission.grant', trigger: () => grantPermission('user-id', 'admin') },
  ];

  for (const { action, trigger } of auditableActions) {
    test(`${action} is recorded in audit log`, async ({ request }) => {
      const beforeResp = await request.get('/api/admin/audit-logs?limit=1', {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      const before = await beforeResp.json();
      const lastId = before.data[0]?.id || 0;

      // Trigger the auditable action
      await trigger();

      // Verify audit log entry
      const afterResp = await request.get(`/api/admin/audit-logs?after=${lastId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      const after = await afterResp.json();

      const entry = after.data.find((e: any) => e.action === action);
      expect(entry).toBeDefined();
      expect(entry.timestamp).toBeDefined();
      expect(entry.actor_id).toBeDefined();
      expect(entry.ip_address).toBeDefined();
      expect(entry.user_agent).toBeDefined();
    });
  }

  test('audit logs are immutable', async ({ request }) => {
    const logsResp = await request.get('/api/admin/audit-logs?limit=1', {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const logEntry = (await logsResp.json()).data[0];

    // Attempt to modify audit log (should fail)
    const modifyResp = await request.patch(`/api/admin/audit-logs/${logEntry.id}`, {
      headers: { Authorization: `Bearer ${adminToken}` },
      data: { action: 'tampered' },
    });
    expect([403, 404, 405]).toContain(modifyResp.status());

    // Attempt to delete audit log (should fail)
    const deleteResp = await request.delete(`/api/admin/audit-logs/${logEntry.id}`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    expect([403, 404, 405]).toContain(deleteResp.status());
  });
});
```

---

## Penetration Testing Requirements

| Standard | Frequency | Scope | Required By |
|----------|-----------|-------|-------------|
| SOC 2 | Annual (recommended) | External + internal | Trust services criteria |
| HIPAA | Annual (recommended) | All ePHI systems | Security rule |
| GDPR | Risk-based | Data processing systems | Art. 32 |
| PCI-DSS | Annual (external), quarterly (internal) | Cardholder data environment | Req. 11.3 |

### Pen Test Automation (Supplemental)

```bash
# OWASP ZAP baseline scan (automated)
docker run --rm -t zaproxy/zap-stable zap-baseline.py \
  -t https://staging.example.com \
  -r zap-report.html \
  -J zap-report.json \
  -l WARN

# Nuclei vulnerability scanner
nuclei -u https://staging.example.com \
  -t cves/ \
  -t vulnerabilities/ \
  -t misconfigurations/ \
  -o nuclei-results.txt \
  -severity critical,high
```

---

## Vulnerability Scanning Cadence

| Scan Type | Frequency | Tool Examples | CI Integration |
|-----------|-----------|---------------|----------------|
| Dependency scan | Every commit | Snyk, Dependabot, npm audit | PR gate |
| Container scan | Every build | Trivy, Grype, Snyk Container | Build gate |
| SAST (static) | Every commit | Semgrep, CodeQL, SonarQube | PR gate |
| DAST (dynamic) | Weekly / pre-release | OWASP ZAP, Nuclei | Scheduled CI |
| Infrastructure | Weekly | ScoutSuite, Prowler | Scheduled CI |

```yaml
# GitHub Actions: vulnerability scanning pipeline
name: Security Scans
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 4 * * 1'  # Weekly Monday 4am

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
      - uses: snyk/actions/node@master
        with:
          args: --severity-threshold=high

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:scan .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:scan
          severity: CRITICAL,HIGH
          exit-code: 1

  sast-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: p/owasp-top-ten
```

---

## Compliance Test Matrices

### SOC 2 Test Matrix (Excerpt)

| Control | Test | Automation | Frequency |
|---------|------|------------|-----------|
| CC6.1 - Encryption at rest | InSpec `ENCRYPT-AT-REST-001` | Fully automated | Weekly |
| CC6.7 - Encryption in transit | TLS version check | Fully automated | Daily |
| CC6.1 - Access control | RBAC matrix test | Fully automated | Every PR |
| CC7.2 - Security monitoring | Audit log completeness | Fully automated | Daily |
| CC8.1 - Change management | PR approval requirement | GitHub branch protection | Every PR |

### HIPAA Test Matrix (Excerpt)

| Safeguard | Test | Automation | Frequency |
|-----------|------|------------|-----------|
| 164.312(a)(1) - Access control | User auth + RBAC tests | Fully automated | Every PR |
| 164.312(a)(2)(iv) - Encryption | At-rest + in-transit checks | Fully automated | Weekly |
| 164.312(b) - Audit controls | Audit log completeness | Fully automated | Daily |
| 164.312(c)(1) - Integrity | Data checksums, immutable logs | Fully automated | Daily |
| 164.312(d) - Authentication | MFA enforcement test | Fully automated | Every PR |
| 164.312(e)(1) - Transmission security | TLS enforcement | Fully automated | Daily |

---

## CI Integration for Compliance Gates

```yaml
# .github/workflows/compliance-gate.yml
name: Compliance Gate
on:
  pull_request:
    branches: [main]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run compliance tests
        run: |
          npm run test:compliance
          inspec exec controls/ --reporter json:compliance-results.json

      - name: Evaluate compliance gate
        run: |
          python scripts/evaluate-compliance.py compliance-results.json
          # Exits non-zero if any critical controls fail

      - name: Upload compliance report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report
          path: compliance-results.json
```

---

## Documentation and Evidence Collection

### Evidence Folder Structure

```text
audit-evidence/
├── 2026-Q1/
│   ├── manifest.json              # Evidence index
│   ├── infrastructure/
│   │   ├── inspec-results.json    # Infrastructure compliance scan
│   │   ├── terraform-plan.json    # Infrastructure drift check
│   │   └── network-scan.json      # Network security scan
│   ├── access-control/
│   │   ├── iam-audit.json         # IAM credential report
│   │   ├── rbac-test-results.json # RBAC verification
│   │   └── mfa-audit.json        # MFA enrollment status
│   ├── vulnerability/
│   │   ├── dependency-scan.json   # Dependency vulnerabilities
│   │   ├── container-scan.json    # Container image scan
│   │   └── pentest-report.pdf     # Annual penetration test
│   └── data-protection/
│       ├── encryption-audit.json  # Encryption validation
│       ├── residency-check.json   # Data residency verification
│       └── retention-audit.json   # Data retention compliance
```

### Evidence Manifest

```json
{
  "audit_period": "2026-Q1",
  "generated_at": "2026-04-01T00:00:00Z",
  "standards": ["SOC2", "HIPAA"],
  "evidence": [
    {
      "control": "CC6.1",
      "description": "Encryption at rest verification",
      "file": "infrastructure/inspec-results.json",
      "automated": true,
      "frequency": "weekly",
      "last_pass": "2026-03-28T06:00:00Z"
    }
  ]
}
```

---

## Compliance Testing Checklist

### Initial Setup

- [ ] Map regulatory requirements to testable controls
- [ ] Write InSpec / OPA policies for infrastructure controls
- [ ] Implement RBAC verification tests
- [ ] Create encryption validation tests (at-rest + in-transit)
- [ ] Build audit log completeness tests
- [ ] Set up vulnerability scanning pipeline
- [ ] Configure evidence collection automation

### Ongoing Operations

- [ ] Weekly: automated infrastructure compliance scan
- [ ] Weekly: vulnerability scan results reviewed
- [ ] Monthly: access control audit (IAM review)
- [ ] Quarterly: compliance test matrix updated
- [ ] Quarterly: evidence folder archived
- [ ] Annually: penetration test (PCI-DSS, SOC 2)
- [ ] Annually: compliance framework mapping reviewed

### Pre-Audit Preparation

- [ ] Evidence folder complete for audit period
- [ ] All critical controls passing
- [ ] Remediation plan for any open findings
- [ ] Access provisioned for auditors
- [ ] Key personnel briefed on audit scope
- [ ] Previous audit findings addressed

---

## Related Resources

- [test-environment-management.md](./test-environment-management.md) -- secrets management and environment isolation
- [quality-metrics-dashboard.md](./quality-metrics-dashboard.md) -- compliance metrics in dashboards
- [operational-playbook.md](./operational-playbook.md) -- CI gates for compliance enforcement
- [SKILL.md](../SKILL.md) -- parent testing strategy skill
- [Chef InSpec Documentation](https://docs.chef.io/inspec/)
- [Open Policy Agent](https://www.openpolicyagent.org/docs/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [SOC 2 Trust Services Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/trustservices.html)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)
