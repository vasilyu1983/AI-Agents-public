# Threat Modeling Guide — Methodology and Practice (Jan 2026)

Practical threat modeling for software teams. Covers STRIDE, PASTA, data flow diagrams, attack trees, risk scoring, and lightweight approaches for agile teams. Use threat modeling to find security design flaws before they become vulnerabilities in production.

---

## When to Threat Model

| Trigger | Scope | Effort |
|---------|-------|--------|
| **New system or service** | Full system DFD, all trust boundaries | 2-4 hours |
| **Major feature or architecture change** | Incremental: new components and data flows only | 1-2 hours |
| **New third-party integration** | Integration boundary: data exchange, auth, trust | 30-60 min |
| **Compliance requirement** (SOC 2, PCI, HIPAA) | Full system review per compliance scope | 4-8 hours |
| **Post-incident** | Affected subsystem, re-evaluate assumptions | 1-2 hours |
| **Sprint planning (lightweight)** | New user stories with security implications | 15-30 min |

### When NOT to Threat Model

- Minor UI changes with no data flow changes
- Documentation-only updates
- Dependency version bumps (use dependency scanning instead)
- Bug fixes that don't change architecture or data flow

---

## STRIDE Methodology

STRIDE is Microsoft's threat classification framework. Each letter represents a threat category that maps to a security property violation.

### STRIDE Categories

| Threat | Security Property Violated | Example | Typical Mitigation |
|--------|--------------------------|---------|-------------------|
| **S**poofing | Authentication | Attacker impersonates a user or service | MFA, mTLS, certificate pinning |
| **T**ampering | Integrity | Attacker modifies data in transit or at rest | HMAC, digital signatures, checksums |
| **R**epudiation | Non-repudiation | User denies performing an action | Audit logging, digital signatures, timestamps |
| **I**nformation Disclosure | Confidentiality | Sensitive data exposed to unauthorized party | Encryption (TLS, AES), access control, data classification |
| **D**enial of Service | Availability | System rendered unavailable | Rate limiting, auto-scaling, CDN, circuit breakers |
| **E**levation of Privilege | Authorization | User gains higher access than intended | RBAC/ABAC, least privilege, input validation |

### Applying STRIDE

For each element in your data flow diagram, ask:

```text
For [element]:
  S — Can an attacker pretend to be this element or its users?
  T — Can an attacker modify data flowing through or stored by this element?
  R — Can a user deny they performed an action through this element?
  I — Can an attacker read data they shouldn't from this element?
  D — Can an attacker make this element unavailable?
  E — Can an attacker gain unauthorized capabilities through this element?
```

### STRIDE-per-Element Matrix

| DFD Element | S | T | R | I | D | E |
|-------------|---|---|---|---|---|---|
| External entity (user, service) | X | | | | | |
| Process (application logic) | X | X | X | X | X | X |
| Data store (database, file) | | X | | X | X | |
| Data flow (API call, message) | | X | | X | X | |
| Trust boundary | | | | | | X |

---

## PASTA — Process for Attack Simulation and Threat Analysis

PASTA is a risk-centric, attacker-focused methodology with seven stages. It complements STRIDE by incorporating business context and attacker motivation.

### Seven Stages

| Stage | Activity | Output |
|-------|----------|--------|
| 1. Define Objectives | Identify business objectives and security requirements | Business impact analysis, compliance requirements |
| 2. Define Technical Scope | Document application architecture, technologies, dependencies | Architecture diagrams, technology inventory |
| 3. Application Decomposition | Create DFDs, identify trust boundaries, enumerate entry points | Data flow diagrams, attack surface inventory |
| 4. Threat Analysis | Research relevant threats using threat intelligence | Threat library mapped to your application |
| 5. Vulnerability Analysis | Map known vulnerabilities to attack surface | Vulnerability inventory, CVE mapping |
| 6. Attack Modeling | Build attack trees, simulate attack scenarios | Attack trees, exploitation scenarios |
| 7. Risk and Impact Analysis | Score risks, prioritize mitigations | Risk-ranked threat list, mitigation roadmap |

### When to Use PASTA vs STRIDE

| Criterion | STRIDE | PASTA |
|-----------|--------|-------|
| **Speed** | Fast (1-2 hours) | Thorough (4-8 hours) |
| **Focus** | Technical threats per component | Business risk and attacker motivation |
| **Best for** | Feature-level threat modeling | System-level or compliance-driven reviews |
| **Team** | Engineering team | Cross-functional (eng + product + security) |
| **Output** | Threat list per component | Risk-ranked roadmap with business justification |

---

## Data Flow Diagrams (DFDs)

DFDs are the foundation of threat modeling. They visualize how data moves through your system and where trust boundaries exist.

### DFD Elements

| Symbol | Element | Description | Example |
|--------|---------|-------------|---------|
| Rectangle | External Entity | User, third-party system, browser | "Mobile App User" |
| Circle | Process | Application logic that transforms data | "Auth Service" |
| Parallel lines | Data Store | Database, file system, cache | "PostgreSQL" |
| Arrow | Data Flow | Data moving between elements | "HTTPS API call" |
| Dashed line | Trust Boundary | Security context change | "Internet ↔ DMZ" |

### Example: Web Application DFD

```text
┌──────────────────────────────────── INTERNET ──────────────────────────────────┐
│                                                                                │
│  ┌─────────┐         HTTPS          ┌──────────┐                              │
│  │ Browser │ ───────────────────────>│ CDN/WAF  │                              │
│  └─────────┘                         └────┬─────┘                              │
│                                           │                                    │
├ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ TRUST BOUNDARY ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│                                           │                                    │
│                                      ┌────▼─────┐      ┌──────────┐           │
│                                      │ API      │──────>│ Auth     │           │
│                                      │ Gateway  │<──────│ Service  │           │
│                                      └────┬─────┘      └──────────┘           │
│                                           │                                    │
│                              ┌────────────┼────────────┐                       │
│                              │            │            │                       │
│                         ┌────▼───┐  ┌─────▼────┐ ┌────▼───┐                   │
│                         │ User   │  │ Order    │ │ Payment│                   │
│                         │ Service│  │ Service  │ │ Service│                   │
│                         └────┬───┘  └─────┬────┘ └────┬───┘                   │
│                              │            │            │                       │
├ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ DATA BOUNDARY ─ ─ ─│─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│                              │            │            │                       │
│                         ┌────▼───┐  ┌─────▼────┐ ┌────▼───┐                   │
│                         │Users DB│  │Orders DB │ │Payment │                   │
│                         │        │  │          │ │ Gateway│ (external)        │
│                         └────────┘  └──────────┘ └────────┘                   │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Trust Boundaries to Identify

| Boundary | What Changes | Threats to Consider |
|----------|-------------|---------------------|
| Internet → DMZ | From untrusted to semi-trusted | Spoofing, injection, DoS |
| DMZ → Internal network | From semi-trusted to trusted | Lateral movement, SSRF |
| Service → Database | From compute to data | SQL injection, access control |
| Service → Service | Between microservices | Auth bypass, data tampering |
| Internal → Third-party | From your control to external | Data leak, supply chain |
| User → Admin | Privilege level change | Elevation of privilege |

---

## Attack Tree Construction

Attack trees decompose a high-level attack goal into sub-goals, showing the different paths an attacker could take.

### Structure

```text
GOAL: Steal user payment data
├─ AND: Gain access to payment database
│   ├─ OR: SQL injection via search endpoint
│   │   ├─ Find unparameterized query
│   │   └─ Bypass WAF rules
│   ├─ OR: Compromise database credentials
│   │   ├─ Extract from environment variables
│   │   ├─ Find in source code / config files
│   │   └─ Intercept connection string in transit
│   └─ OR: Exploit SSRF to reach internal database
│       ├─ Find URL parameter that fetches external resources
│       └─ Bypass SSRF filters (DNS rebinding, IP encoding)
├─ AND: Exfiltrate data without detection
│   ├─ OR: Disable or evade logging
│   ├─ OR: Use legitimate-looking queries (low and slow)
│   └─ OR: Exfiltrate through DNS or ICMP channels
└─ OR: Intercept data in transit
    ├─ TLS downgrade attack
    ├─ Compromise TLS certificate
    └─ Man-in-the-middle via compromised network
```

### Building Effective Attack Trees

1. Start with the attacker's goal (what they want to achieve)
2. Decompose into AND/OR nodes (what they need to do)
3. Continue decomposing until leaf nodes are actionable attack steps
4. Annotate each leaf with: difficulty (Low/Medium/High), detection likelihood, impact
5. Identify the cheapest/easiest path — that is what gets exploited first

---

## Threat Modeling for Microservices

Microservices introduce unique threat modeling concerns not present in monolithic applications.

### Microservices-Specific Threats

| Component | Threats | Mitigations |
|-----------|---------|-------------|
| **Service-to-service calls** | Auth bypass, data tampering, replay attacks | mTLS, JWT propagation, request signing |
| **API gateway** | Single point of failure, auth bypass, rate limit evasion | Redundancy, defense in depth, per-service auth |
| **Message queues** (Kafka, RabbitMQ) | Message injection, eavesdropping, replay | Encryption in transit, message signing, access control |
| **Service mesh** (Istio, Linkerd) | Sidecar bypass, control plane compromise | mTLS enforcement, RBAC policies, network policies |
| **Shared databases** | Cross-service data access, schema confusion | Database-per-service, schema isolation, row-level security |
| **Service discovery** | Poisoned service registry, DNS spoofing | Authenticated registration, signed service records |
| **Distributed config** (Consul, etcd) | Secret exposure, config tampering | Encryption at rest, access control, audit logging |

### Microservices DFD Pattern

```text
For each service boundary, document:
1. Inbound data flows: who calls this service, with what auth?
2. Outbound data flows: what does this service call?
3. Data stores: what data does this service own?
4. Shared resources: caches, queues, config stores
5. Trust level: does this service handle PII, financial data, admin operations?
```

---

## Threat Modeling for Web Applications

### Standard Web App DFD Components

| Component | STRIDE Focus | Key Questions |
|-----------|-------------|---------------|
| Client (browser) | S, T, I | Can client-side code be tampered? Is sensitive data stored client-side? |
| CDN/Edge | D, T | Can cached content be poisoned? Is edge config secure? |
| Load balancer | D, S | Can health checks be spoofed? Is TLS terminated securely? |
| Web server | S, T, R, I, D, E | All STRIDE categories apply to the core application |
| Session store | S, T, I | Can sessions be hijacked? Is session data encrypted? |
| Database | T, I, D | SQL injection? Encryption at rest? Backup security? |
| File storage | T, I | Path traversal? Upload validation? Access control? |
| Email service | S, R | Can email be spoofed? Are transactional emails logged? |
| Payment processor | S, T, I | Is communication encrypted? Are webhooks verified? |

---

## Risk Scoring

### CVSS (Common Vulnerability Scoring System)

CVSS v3.1 is the industry standard for vulnerability severity scoring.

| Metric Group | Factors | Purpose |
|-------------|---------|---------|
| **Base** | Attack vector, complexity, privileges, user interaction, scope, CIA impact | Intrinsic severity |
| **Temporal** | Exploit maturity, remediation level, report confidence | Current real-world risk |
| **Environmental** | Modified base metrics, CIA requirements | Organization-specific context |

| Score Range | Severity | Typical Response |
|-------------|----------|-----------------|
| 9.0 - 10.0 | Critical | Patch within 24 hours, P0 incident |
| 7.0 - 8.9 | High | Patch within 7 days, P1 |
| 4.0 - 6.9 | Medium | Patch within 30 days, P2 |
| 0.1 - 3.9 | Low | Patch in next release, P3 |

### DREAD (Simplified Risk Model)

DREAD is simpler than CVSS and useful for threat model workshops where CVSS is too granular.

| Factor | Question | Score |
|--------|----------|-------|
| **D**amage | How bad is the impact? | 1-10 |
| **R**eproducibility | How easy to reproduce? | 1-10 |
| **E**xploitability | How easy to exploit? | 1-10 |
| **A**ffected users | How many users impacted? | 1-10 |
| **D**iscoverability | How easy to find? | 1-10 |

**Risk Score** = (D + R + E + A + D) / 5

| Score | Risk Level | Action |
|-------|-----------|--------|
| 8-10 | Critical | Fix immediately |
| 5-7 | High | Fix in current sprint |
| 3-4 | Medium | Fix in next sprint |
| 1-2 | Low | Backlog |

### Custom Risk Matrix

For organizations that need a tailored approach:

```text
Risk = Likelihood × Impact

LIKELIHOOD:
  5 — Almost certain (will happen within months)
  4 — Likely (known exploits exist, low skill required)
  3 — Possible (exploits require moderate skill)
  2 — Unlikely (requires significant effort or insider access)
  1 — Rare (theoretical, no known exploits)

IMPACT:
  5 — Catastrophic (full data breach, regulatory penalties, existential)
  4 — Major (significant data exposure, service outage >4 hours)
  3 — Moderate (limited data exposure, service degradation)
  2 — Minor (minimal data exposure, brief disruption)
  1 — Negligible (no data exposure, no user impact)
```

| | Impact 1 | Impact 2 | Impact 3 | Impact 4 | Impact 5 |
|---|---------|---------|---------|---------|---------|
| **Likelihood 5** | 5 (Med) | 10 (High) | 15 (High) | 20 (Crit) | 25 (Crit) |
| **Likelihood 4** | 4 (Med) | 8 (High) | 12 (High) | 16 (Crit) | 20 (Crit) |
| **Likelihood 3** | 3 (Low) | 6 (Med) | 9 (High) | 12 (High) | 15 (High) |
| **Likelihood 2** | 2 (Low) | 4 (Med) | 6 (Med) | 8 (High) | 10 (High) |
| **Likelihood 1** | 1 (Low) | 2 (Low) | 3 (Low) | 4 (Med) | 5 (Med) |

---

## Tooling

| Tool | Type | Best For | Cost |
|------|------|----------|------|
| **Microsoft Threat Modeling Tool** | Desktop app | STRIDE-based DFD modeling, Windows teams | Free |
| **OWASP Threat Dragon** | Web/desktop | Open source, cross-platform DFD + threats | Free |
| **IriusRisk** | SaaS platform | Enterprise, automated threat libraries, compliance mapping | Paid |
| **Threagile** | CLI (Go) | Infrastructure-as-code threat models, YAML-based | Free |
| **draw.io / diagrams.net** | Diagramming | Quick DFDs when specialized tools are unavailable | Free |
| **Miro / FigJam** | Collaborative whiteboard | Remote team workshops, low-fidelity DFDs | Free/Paid |

### Tool Selection Decision

```text
Team size and budget:
  ├─ Solo or small team, no budget
  │   └─ OWASP Threat Dragon or draw.io
  ├─ Engineering team, standard process needed
  │   └─ Microsoft Threat Modeling Tool (Windows) or Threagile (CLI)
  ├─ Enterprise, compliance requirements
  │   └─ IriusRisk (automated libraries, audit trail)
  └─ Remote workshop, collaborative session
      └─ Miro or FigJam with DFD template
```

---

## Lightweight Threat Modeling for Agile Teams

Full STRIDE analysis for every sprint is impractical. Use this 15-minute approach for stories with security implications.

### The 15-Minute Threat Model

Run during sprint planning or design review for any story that:
- Adds a new API endpoint or data store
- Changes authentication, authorization, or data flow
- Integrates a new third-party service
- Handles PII, financial data, or credentials

```text
STEP 1: WHAT ARE WE BUILDING? (3 min)
- Sketch the data flow on a whiteboard or shared doc
- Identify: inputs, outputs, data stores, external services

STEP 2: WHAT CAN GO WRONG? (7 min)
- Walk through STRIDE for each new/changed component:
  S: Can someone pretend to be someone else?
  T: Can data be modified without detection?
  R: Can someone deny they did something?
  I: Can sensitive data leak?
  D: Can this be taken down?
  E: Can someone get more access than intended?

STEP 3: WHAT ARE WE GOING TO DO ABOUT IT? (5 min)
- For each identified threat:
  - Accept (risk is low and within tolerance)
  - Mitigate (add control as part of this story)
  - Defer (create a follow-up security story with justification)

DOCUMENT:
| Threat | STRIDE | Risk | Action | Owner |
|--------|--------|------|--------|-------|
| [threat] | [S/T/R/I/D/E] | [H/M/L] | [Accept/Mitigate/Defer] | [Name] |
```

### Security Story Template

When a threat requires a separate story:

```text
AS A security engineer,
I WANT [specific mitigation],
SO THAT [specific threat] is addressed.

ACCEPTANCE CRITERIA:
- [ ] [Specific, testable security requirement]
- [ ] [Specific, testable security requirement]

THREAT CONTEXT:
- Identified in threat model for [feature]
- STRIDE category: [S/T/R/I/D/E]
- Risk score: [H/M/L]
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Threat model once, never update | Architecture changes invalidate old model | Re-model on significant architecture changes |
| Model everything in one session | Fatigue leads to shallow analysis | Scope to specific components or changes |
| Only security team does threat modeling | Developers know the system best | Collaborative session: devs + security |
| No follow-through on findings | Threats identified but never mitigated | Track mitigations as backlog items with owners |
| Focus only on external threats | Insider threats and misconfiguration ignored | Include internal actors and operational errors |
| Perfect DFD before any analysis | Delays analysis indefinitely | "Good enough" DFD; refine as you model |
| CVSS score without context | 7.5 in isolated system != 7.5 in payment service | Apply environmental scoring to your context |
| Threat modeling as checkbox exercise | No real threats identified or mitigated | Judge by mitigations shipped, not documents produced |

---

## Threat Model Review Checklist

- [ ] DFD covers all components, data stores, and external services
- [ ] Trust boundaries are explicitly marked
- [ ] Each component has been analyzed with STRIDE (or chosen methodology)
- [ ] Identified threats are scored (CVSS, DREAD, or custom risk matrix)
- [ ] Each threat has a disposition: Accept, Mitigate, Transfer, or Avoid
- [ ] Mitigations are assigned to specific owners with deadlines
- [ ] Model is stored in version control or accessible repository
- [ ] Model includes date and trigger for next review

---

## References

- [Microsoft STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/)
- [PASTA Threat Modeling](https://versprite.com/tag/pasta-threat-modeling/)
- [Shostack, Adam. Threat Modeling: Designing for Security. Wiley, 2014.](https://shostack.org/books/threat-modeling-book)
- [NIST SP 800-154 — Guide to Data-Centric Threat Modeling](https://csrc.nist.gov/pubs/sp/800/154/ipd)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview, threat modeling mentioned in decision tree and OWASP A06
- [secure-design-principles.md](secure-design-principles.md) — Defense in depth, least privilege principles
- [owasp-top-10.md](owasp-top-10.md) — A06: Insecure Design (threat modeling as primary control)
- [api-security-patterns.md](api-security-patterns.md) — API-specific threats for API components in DFDs
- [incident-response-playbook.md](incident-response-playbook.md) — Post-incident threat model review trigger
- [zero-trust-architecture.md](zero-trust-architecture.md) — Trust boundary design and zero-trust principles
