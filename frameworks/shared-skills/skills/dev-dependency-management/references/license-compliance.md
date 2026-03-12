# Open-Source License Compliance

> Operational reference for auditing, managing, and enforcing open-source license compliance. Covers license types, compatibility rules, automated tooling, CI/CD integration, and enterprise workflows.

**Freshness anchor:** January 2026 — aligned with SPDX 2.3, FOSSA 3.x, Licensee CLI, and current OSI-approved license list (opensource.org).

---

## License Quick Reference

### Common License Types

| License | SPDX ID | Type | Commercial Use | Modification | Distribution | Copyleft | Patent Grant |
|---|---|---|---|---|---|---|---|
| MIT | `MIT` | Permissive | Yes | Yes | Yes | No | No |
| Apache 2.0 | `Apache-2.0` | Permissive | Yes | Yes | Yes | No | Yes |
| BSD 2-Clause | `BSD-2-Clause` | Permissive | Yes | Yes | Yes | No | No |
| BSD 3-Clause | `BSD-3-Clause` | Permissive | Yes | Yes | Yes | No | No |
| ISC | `ISC` | Permissive | Yes | Yes | Yes | No | No |
| LGPL 2.1 | `LGPL-2.1-only` | Weak Copyleft | Yes | Yes | Yes | File-level | No |
| MPL 2.0 | `MPL-2.0` | Weak Copyleft | Yes | Yes | Yes | File-level | Yes |
| GPL 2.0 | `GPL-2.0-only` | Strong Copyleft | Yes | Yes | Must open-source | Project-level | No |
| GPL 3.0 | `GPL-3.0-only` | Strong Copyleft | Yes | Yes | Must open-source | Project-level | Yes |
| AGPL 3.0 | `AGPL-3.0-only` | Network Copyleft | Yes | Yes | Must open-source (incl. SaaS) | Network-level | Yes |
| BSL 1.1 | `BUSL-1.1` | Source Available | Time-delayed | Yes | Restricted | Varies | No |
| SSPL | `SSPL-1.0` | Source Available | Restricted | Yes | Restricted | Service-level | No |
| Unlicense | `Unlicense` | Public Domain | Yes | Yes | Yes | No | No |

### Risk Classification

| Risk Level | Licenses | Action |
|---|---|---|
| Low (auto-approve) | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense | No review needed |
| Medium (review required) | LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0 | Legal review for linking model |
| High (legal approval required) | GPL-2.0, GPL-3.0 | Must not link into proprietary code without isolation |
| Critical (block by default) | AGPL-3.0, SSPL, BUSL-1.1, Commons Clause | Block unless explicit legal exception |
| Unknown | No license detected | Block — treat as all-rights-reserved |

---

## License Compatibility Matrix

### Can I combine these licenses in one project?

| Outbound License → | MIT | Apache-2.0 | LGPL-3.0 | GPL-3.0 | AGPL-3.0 |
|---|---|---|---|---|---|
| **MIT** dep | Yes | Yes | Yes | Yes | Yes |
| **Apache-2.0** dep | Yes | Yes | Yes | Yes | Yes |
| **LGPL-3.0** dep | Yes | Yes | Yes | Yes | Yes |
| **GPL-3.0** dep | No | No | No | Yes | Yes |
| **AGPL-3.0** dep | No | No | No | No | Yes |

**Reading the matrix:** Row = dependency license. Column = your project's license. "Yes" = compatible combination.

### GPL Contamination Decision Tree

```
Does your project link to a GPL-licensed library?
├── NO → No GPL obligation
├── YES
│   ├── Is it LGPL?
│   │   ├── Dynamic linking only → OK, no contamination
│   │   └── Static linking or modification → LGPL obligations apply to modified files
│   ├── Is it GPL?
│   │   ├── Is the GPL code in a separate process (CLI tool, microservice)?
│   │   │   ├── YES → Generally safe (separate work)
│   │   │   └── NO (linked into your binary/runtime)
│   │   │       └── Your project MUST be GPL-licensed
│   │   └── Is there a "classpath exception" or similar?
│   │       └── YES → Read exception terms carefully
│   └── Is it AGPL?
│       └── Does your application serve users over a network?
│           ├── YES → Must provide source to ALL users (including SaaS users)
│           └── NO → Same as GPL
```

---

## Automated Tooling

### Tool Comparison

| Tool | Type | Languages | CI/CD | Output | Cost |
|---|---|---|---|---|---|
| FOSSA | SaaS + CLI | 20+ | GitHub, GitLab, Jenkins | Dashboard, SBOM | Free (small), paid |
| license-checker (npm) | CLI | Node.js | Any | JSON, CSV | Free (MIT) |
| pip-licenses | CLI | Python | Any | JSON, CSV, table | Free (MIT) |
| cargo-license | CLI | Rust | Any | JSON, table | Free |
| go-licenses | CLI | Go | Any | CSV, template | Free (Apache-2.0) |
| Licensee | CLI (Ruby) | Any (file-based) | Any | JSON | Free (MIT) |
| SPDX SBOM tools | Spec + tools | Multi | Any | SPDX JSON/RDF | Free |
| Scancode-toolkit | CLI | Multi | Any | JSON, SPDX | Free (Apache-2.0) |

### npm: license-checker

```bash
# List all licenses
npx license-checker --json

# Check for prohibited licenses
npx license-checker --failOn "GPL-2.0-only;GPL-3.0-only;AGPL-3.0-only"

# Exclude dev dependencies
npx license-checker --production --json

# Output CSV for legal review
npx license-checker --production --csv --out licenses.csv

# Custom allow list
npx license-checker --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"
```

### Python: pip-licenses

```bash
# List all licenses
pip-licenses --format=table

# JSON output for automation
pip-licenses --format=json --output-file=licenses.json

# Fail on disallowed licenses
pip-licenses --fail-on="GNU General Public License v3 (GPLv3)"

# Allow-list mode
pip-licenses --allow-only="MIT License;Apache Software License;BSD License"
```

### Go: go-licenses

```bash
# Check all licenses
go-licenses check ./...

# Save license files
go-licenses save ./... --save_path=third_party/licenses

# Report format
go-licenses report ./... --template=csv
```

### FOSSA CLI

```bash
# Initialize project
fossa init

# Analyze dependencies
fossa analyze

# Check policy compliance (blocks on violations)
fossa test

# Generate SBOM
fossa report attribution --format spdx
```

---

## CI/CD Integration

### Pipeline Configuration

```yaml
# GitHub Actions example
name: License Compliance
on: [pull_request]

jobs:
  license-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: npm ci

      - name: Check licenses
        run: |
          npx license-checker \
            --production \
            --failOn "GPL-2.0-only;GPL-3.0-only;AGPL-3.0-only;SSPL-1.0" \
            --excludePackages "my-internal-package@1.0.0"

      - name: Generate license report
        run: npx license-checker --production --csv --out licenses.csv

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: license-report
          path: licenses.csv
```

### CI Checklist

- [ ] License check runs on every PR
- [ ] Production dependencies only (exclude devDependencies)
- [ ] Fail on high-risk licenses (GPL, AGPL, SSPL, BUSL)
- [ ] Alert on unknown/undetected licenses
- [ ] License report generated and stored as artifact
- [ ] SBOM generated on release builds
- [ ] New dependency additions flagged for review
- [ ] Quarterly full audit scheduled (catch reclassified licenses)

### Handling CI Failures

```
License check failed
├── Unknown license detected
│   ├── Check package source for LICENSE file
│   ├── If permissive → add to known-licenses override
│   ├── If restrictive → remove package, find alternative
│   └── If no license → treat as proprietary, do not use
├── GPL/AGPL detected
│   ├── Is it a dev-only dependency? → Move to devDependencies, exclude from check
│   ├── Is it a CLI tool (separate process)? → Document as system-level tool, may be acceptable
│   └── Is it linked into the application? → Replace with permissive alternative
└── New dependency added with medium-risk license
    └── Flag for legal review, create ticket
```

---

## Enterprise Compliance Workflow

### License Approval Process

```
Developer adds new dependency
├── Automated CI scan runs
│   ├── PASS (all licenses in allow-list) → Auto-approved
│   ├── WARN (medium-risk license) → Requires engineering lead review
│   └── FAIL (high-risk or unknown) → Requires legal review
│
├── Review process
│   ├── Engineering lead evaluates usage context (linking model, distribution)
│   ├── Legal reviews obligations and compatibility
│   └── Decision recorded in license policy document
│
└── Outcome
    ├── APPROVED → Add to allow-list with conditions
    ├── APPROVED WITH CONDITIONS → Document restrictions (e.g., dynamic linking only)
    └── REJECTED → Find alternative, document reason
```

### Policy Document Template

```markdown
## License Policy

### Auto-Approved Licenses
- MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense, CC0-1.0

### Conditionally Approved
- LGPL-2.1, LGPL-3.0: Dynamic linking only, no static linking
- MPL-2.0: File-level changes must be published

### Prohibited (Require Exception)
- GPL-2.0, GPL-3.0, AGPL-3.0, SSPL, BUSL-1.1, Commons Clause

### Exceptions
| Package | License | Approved By | Date | Conditions |
|---|---|---|---|---|
| libfoo | GPL-2.0 | Legal/Jane | 2026-01 | Separate process only, not linked |

### Review Cadence
- Quarterly full audit
- Annual policy review with legal
```

---

## Dual Licensing Considerations

### Common Dual-License Models

| Package | Open Source License | Commercial License | When to buy |
|---|---|---|---|
| MySQL | GPL-2.0 | Oracle Commercial | Proprietary product embedding |
| Qt | LGPL-3.0 / GPL | Qt Commercial | Static linking, no LGPL obligations |
| MongoDB | SSPL | MongoDB Enterprise | SaaS offering MongoDB as a service |
| Elasticsearch | SSPL + Elastic License | Elastic Cloud | Offering as managed search service |

### Decision Framework

```
Is the dual-licensed software used in a way that triggers copyleft?
├── NO → Use open-source license, no commercial needed
├── YES
│   ├── Can you comply with copyleft terms?
│   │   ├── YES (willing to open-source) → Use open-source license
│   │   └── NO → Purchase commercial license
│   └── Is the cost justified vs alternatives?
│       ├── YES → Purchase commercial license
│       └── NO → Evaluate permissively-licensed alternatives
```

---

## SBOM Generation

### Software Bill of Materials (SBOM) Checklist

- [ ] SBOM generated on every release build
- [ ] Format: SPDX 2.3 JSON or CycloneDX 1.6 JSON
- [ ] Includes: package name, version, license, supplier, hash
- [ ] Stored alongside release artifacts
- [ ] Meets regulatory requirements (US Executive Order 14028 for federal software)

### Generation Commands

```bash
# Trivy SPDX SBOM
trivy fs --format spdx-json --output sbom.spdx.json .

# CycloneDX (Node.js)
npx @cyclonedx/cyclonedx-npm --output-file sbom.cdx.json

# CycloneDX (Python)
cyclonedx-py environment --output sbom.cdx.json

# Syft (multi-language)
syft . -o spdx-json > sbom.spdx.json
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| No license checks in CI | Non-compliant dependency discovered after release | Add automated scanning to PR pipeline |
| Treating "no license" as permissive | Legally means all-rights-reserved | Block unlicensed packages, contact maintainer |
| GPL dependency in proprietary SaaS | License violation, legal risk | Replace with permissive alternative or isolate |
| License check only at initial add | Dependencies change licenses on major updates | Scan on every build, not just when adding |
| Manual license tracking spreadsheet | Outdated within weeks, incomplete | Automate with FOSSA, license-checker, or similar |
| Ignoring transitive dependencies | GPL can be deep in the tree | Scan full resolved tree, not just direct deps |
| No AGPL policy | AGPL in SaaS requires source disclosure | Block AGPL by default, require legal exception |
| Copy-pasting code without checking license | Snippet from GPL project contaminates codebase | Check license before copying any external code |
| No exception documentation | Approved exceptions lost, re-litigated | Maintain exceptions list with dates and reviewers |

---

## Cross-References

- `dev-dependency-management/references/version-conflict-resolution.md` — resolving version conflicts in licensed packages
- `dev-dependency-management/references/container-dependency-patterns.md` — scanning container images for license compliance
- `software-security-appsec/references/threat-modeling-guide.md` — supply chain security
- `startup-legal-basics/references/ip-protection-guide.md` — intellectual property considerations
- `startup-legal-basics/SKILL.md` — broader legal compliance guidance
