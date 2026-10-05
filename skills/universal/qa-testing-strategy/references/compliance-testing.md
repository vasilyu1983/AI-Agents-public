# Compliance Testing

How a test strategy produces audit evidence for SOC 2, HIPAA, GDPR and PCI DSS. Scanner and policy-engine mechanics (InSpec, OPA, ZAP, Nuclei, Trivy) are owned by [qa-security-testing](../../qa-security-testing/SKILL.md) and infrastructure controls by [ops-devops-platform](../../ops-devops-platform/SKILL.md). Whether an obligation applies to a given entity is a legal question: route it to qualified counsel, and do not present this table as legal advice.

## Contents

- [Testing Obligations by Standard](#testing-obligations-by-standard)
- [Audit Log Completeness Testing](#audit-log-completeness-testing)
- [Evidence Pipeline Pattern](#evidence-pipeline-pattern)
- [Gate Rules](#gate-rules)
- [Related Resources](#related-resources)

## Testing Obligations by Standard

Legend: **Explicit** = the standard names the activity and a cadence; **Risk-based** = the standard requires appropriate measures and the activity is the usual way to evidence them; **Proposed** = in a proposed rule, not yet in force.

| Testing type | SOC 2 | HIPAA Security Rule | GDPR | PCI DSS v4.x |
|---|---|---|---|---|
| Access control testing | Risk-based (criteria CC6.x) | Explicit safeguard (164.312(a)); test is risk-based | Risk-based (Art. 32) | Explicit (Req. 7, 8) |
| Encryption validation | Risk-based | Addressable (164.312(a)(2)(iv), (e)(2)(ii)) | Risk-based: Art. 32 lists encryption "as appropriate" | Explicit (Req. 3, 4) |
| Audit log testing | Risk-based (CC7.x) | Explicit safeguard (164.312(b)) | Risk-based | Explicit (Req. 10) |
| Penetration testing | Risk-based; commonly annual | **Proposed**: pen testing at least every 12 months under proposed 45 CFR 164.312(h)(2)(iii) in the Security Rule NPRM (Federal Register 2024-30983, check the Federal Register for a final rule before citing it). Today: risk-based via risk analysis | Risk-based (Art. 32(1)(d) "regularly testing") | Explicit: at least every 12 months and after significant change (Req. 11.4) |
| Vulnerability scanning | Risk-based | **Proposed**: no less than every six months under proposed 164.312(h)(2)(i). Today: risk-based | Risk-based | Explicit: at least every three months, internal and external ASV (Req. 11.3) |
| Data retention / erasure testing | Risk-based (privacy criteria) | Risk-based | Explicit rights (Art. 17 erasure; Art. 5(1)(e) storage limitation) | Explicit (Req. 3.2) |
| Incident response testing | Risk-based (CC7.4) | Explicit contingency-plan testing is addressable (164.308(a)(7)(ii)(D)) | Breach notification duties (Art. 33–34) | Explicit (Req. 12.10) |

Re-verify any row before it goes into a customer questionnaire or audit response: requirement numbers and proposed rules change.

## Audit Log Completeness Testing

The expert delta here is testing that every auditable action produces a complete, immutable record, not only that logging is "on".

Pattern:

1. Maintain one list of auditable actions (login, logout, user create/delete, data export, settings change, permission grant) as test data, owned with the access-control matrix.
2. For each action: read the latest audit-log ID, trigger the action, then assert a new entry exists with `action`, `timestamp`, `actor_id`, source address and user agent.
3. Assert immutability: `PATCH` and `DELETE` on an existing entry must be rejected (403/404/405) even for an admin token.
4. Fail the gate when a new auditable endpoint ships without a row in the list (compare the route inventory against the list).

```typescript
for (const { action, trigger } of auditableActions) {
  test(`${action} is recorded in audit log`, async ({ request }) => {
    const lastId = (await (await request.get('/api/admin/audit-logs?limit=1', auth)).json()).data[0]?.id ?? 0;
    await trigger();
    const after = (await (await request.get(`/api/admin/audit-logs?after=${lastId}`, auth)).json()).data;
    const entry = after.find((e: any) => e.action === action);
    expect(entry).toBeDefined();
    for (const field of ['timestamp', 'actor_id', 'ip_address', 'user_agent']) expect(entry[field]).toBeDefined();
  });
}
```

## Evidence Pipeline Pattern

- Every compliance check runs in CI or on a schedule and writes a machine-readable result plus a manifest entry: control ID, description, file, automated yes/no, frequency, last pass timestamp, build or commit identity.
- Store evidence per audit period (`audit-evidence/<period>/<domain>/…`) in write-once storage; the manifest is the index an auditor samples from.
- A check that did not run is a gap, not a pass. The manifest must show missing runs explicitly.
- Map each automated test to a control once (for example SOC 2 CC6.1 encryption at rest, HIPAA 164.312(b) audit controls) and keep that map next to the tests, not in a slide deck.

## Gate Rules

- Access-control (RBAC matrix, privilege-escalation) and audit-log completeness tests run on every PR that touches auth, permissions or auditable endpoints.
- Encryption, residency and configuration checks run on a schedule and on infrastructure changes.
- Never quarantine a compliance or security gate test; a flaky one is fixed or the release is held.

## Related Resources

- [quality-metrics-dashboard.md](quality-metrics-dashboard.md) — release readiness hard gates (security is non-compensatory)
- [test-environment-management.md](test-environment-management.md) — environment isolation and data handling
- [synthetic-test-data.md](synthetic-test-data.md) — keep real personal data out of test environments
- [../SKILL.md](../SKILL.md) — parent testing strategy skill
- [HIPAA Security Rule NPRM (Federal Register 2024-30983)](https://www.federalregister.gov/documents/2025/01/06/2024-30983/hipaa-security-rule-to-strengthen-the-cybersecurity-of-electronic-protected-health-information)
