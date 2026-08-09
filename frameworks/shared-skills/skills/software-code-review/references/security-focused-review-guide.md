# Security-Focused Code Review Guide

What to look for during code review to catch security vulnerabilities before they ship. This guide is specifically for reviewers examining pull requests -- not for penetration testing or comprehensive security audits. For deep security assessments, use the [software-security-appsec](../../software-security-appsec/SKILL.md) skill.

---

## Table of Contents

1. [Security Review Mindset](#security-review-mindset)
2. [Input Validation Red Flags](#input-validation-red-flags)
3. [Authentication and Authorization](#authentication-and-authorization)
4. [Injection Vulnerabilities](#injection-vulnerabilities)
5. [Secrets Detection](#secrets-detection)
6. [Dependency Review](#dependency-review)
7. [Security Headers and CORS](#security-headers-and-cors)
8. [Common Mistakes by Language](#common-mistakes-by-language)
9. [Security Review Quick Checklist](#security-review-quick-checklist)
10. [Anti-Patterns](#anti-patterns)

---

## Security Review Mindset

### Attacker Thinking During Review

When reviewing code, ask:

- **What can a malicious user send here?** (Unexpected input types, sizes, encodings)
- **What happens if this assumption is wrong?** (Null user, expired token, tampered data)
- **Can this be called in an unintended order?** (Race conditions, TOCTOU)
- **What data crosses a trust boundary?** (Client to Server, Service to Database, User to File system)

### Trust Boundaries to Watch

```text
Untrusted inputs:
  - HTTP request parameters (query, body, headers, cookies)
  - File uploads
  - Webhook payloads from external services
  - URL parameters and path segments
  - Data from external APIs or third-party services
  - Database content that originated from user input
  - Environment variables set by deployment infrastructure
```

### Review Priority

Security review should happen first in multi-pass review. Focus on:

1. **P0**: Authentication bypass, authorization failures, injection, secrets exposure
2. **P1**: Missing input validation, insecure defaults, improper error handling
3. **P2**: Missing security headers, verbose error messages, logging sensitive data

---

## Input Validation Red Flags

### Red Flags to Catch

| Pattern | Risk | What to Look For |
|---------|------|-------------------|
| No validation on request body | Injection, type confusion | Raw `req.body` used without schema validation |
| String concatenation with user input | Injection (SQL, XSS, command) | Template literals or `+` with untrusted data |
| Missing length limits | DoS, buffer issues | No `maxLength` on string inputs, no array size limits |
| Type coercion reliance | Type confusion | Using `==` instead of `===`, trusting `typeof` |
| Missing content-type validation | MIME confusion | File uploads without type checking |
| Direct use of URL parameters | Path traversal, SSRF | `req.params.id` used in file paths or URLs |

### What Good Validation Looks Like

```typescript
// GOOD: Schema validation at the boundary
import { z } from 'zod';

const createUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).trim(),
  age: z.number().int().min(13).max(150),
  role: z.enum(['user', 'admin']),  // Allowlist, not blocklist
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const validated = createUserSchema.parse(body);
  // ... use validated data only
}
```

```typescript
// BAD: No validation, trusting client data
export async function POST(request: NextRequest) {
  const { email, name, role } = await request.json();
  await db.user.create({ data: { email, name, role } });
}
```

### File Upload Validation

Review checklist for file uploads:

1. File type validation (not just extension -- check magic bytes)
2. File size limits enforced server-side
3. Filename sanitization (strip path components)
4. Storage location outside web root
5. No execution permissions on uploaded files

```typescript
// RED FLAG: Trusting file extension
const ext = file.name.split('.').pop();  // Attacker controls this

// BETTER: Validate MIME type and magic bytes
import { fileTypeFromBuffer } from 'file-type';
const type = await fileTypeFromBuffer(buffer);
if (!ALLOWED_TYPES.includes(type?.mime)) {
  throw new Error('Invalid file type');
}
```

---

## Authentication and Authorization

### Authentication Patterns to Verify

| Check | What to Look For |
|-------|-------------------|
| Token validation | Is the JWT signature verified? Is expiration checked? |
| Session management | Are sessions invalidated on logout? Is session ID rotated on privilege change? |
| Password handling | Is bcrypt/argon2 used? Is there a minimum cost factor? |
| MFA bypass | Can MFA be skipped via API? Is the MFA check enforced server-side? |
| Token storage | Is the token stored securely (httpOnly cookie vs localStorage)? |
| Rate limiting | Are login attempts rate-limited? Is there account lockout? |

### Authorization Patterns to Verify

```typescript
// RED FLAG: Missing authorization check
app.delete('/api/posts/:id', async (req, res) => {
  await db.post.delete({ where: { id: req.params.id } });
  // Anyone can delete any post!
});

// CORRECT: Verify ownership/permission
app.delete('/api/posts/:id', authenticate, async (req, res) => {
  const post = await db.post.findUnique({
    where: { id: req.params.id }
  });
  if (!post) return res.status(404).json({ error: 'Not found' });
  if (post.authorId !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  await db.post.delete({ where: { id: req.params.id } });
});
```

### IDOR (Insecure Direct Object Reference)

The most common authorization vulnerability. Watch for:

```text
RED FLAG: User-supplied ID used without ownership check
  GET /api/users/:userId/documents/:docId
  Does the code verify that userId matches the authenticated user?
  Does the code verify that docId belongs to userId?

RED FLAG: Sequential IDs enabling enumeration
  GET /api/invoices/1001
  GET /api/invoices/1002
  Attacker iterates to find other users' invoices
```

### Privilege Escalation Checks

```typescript
// RED FLAG: Role set from client input via mass assignment
const user = await db.user.create({
  data: { ...req.body }
  // If req.body contains { role: 'admin' }, privilege escalation
});

// CORRECT: Explicitly set allowed fields
const user = await db.user.create({
  data: {
    email: validated.email,
    name: validated.name,
    role: 'user',  // Default; admin set through separate workflow
  }
});
```

---

## Injection Vulnerabilities

### SQL Injection

```typescript
// RED FLAG: String interpolation in SQL
const query = `SELECT * FROM users WHERE email = '${email}'`;

// CORRECT: Parameterized queries
const user = await db.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);
// Or use an ORM that parameterizes automatically
const user = await prisma.user.findUnique({ where: { email } });
```

**Review trigger**: Any raw SQL string that includes a variable. Even ORMs can be vulnerable if using raw query methods.

### XSS (Cross-Site Scripting)

Patterns to flag during review:

| Pattern | Risk Level | Safer Alternative |
|---------|------------|-------------------|
| Setting innerHTML from user data | Critical | Use `textContent` or sanitize with DOMPurify |
| React `dangerouslySetInnerHTML` with user content | Critical | Sanitize input before rendering |
| User data in `href`/`src` attributes | High | Validate URL scheme (http/https only) |
| Template string injection in HTML | High | Use framework's auto-escaping |
| `document.write` with dynamic content | High | Use DOM APIs instead |

**URL validation example:**

```typescript
const isValidUrl = (url: string) => {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
};
```

### CSRF (Cross-Site Request Forgery)

Red flags during review:

- State-changing GET requests (attacker triggers via `<img src=...>`)
- Missing CSRF token on form submissions
- No SameSite attribute on session cookies

Correct patterns:

- Use SameSite=Strict or SameSite=Lax cookies
- Validate CSRF token on all state-changing requests
- Use framework-provided CSRF protection

### Command Injection

```typescript
// RED FLAG: User input passed to shell commands
// Any use of shell execution with variable arguments

// CORRECT: Use execFile with argument array (no shell interpolation)
import { execFile } from 'child_process';
execFile('convert', [userFilename, 'output.png']);
```

### Path Traversal

```typescript
// RED FLAG: User input in file paths
const filePath = path.join('/uploads', req.params.filename);
// Attacker payload: ../../etc/passwd

// CORRECT: Validate resolved path stays within allowed directory
const basePath = path.resolve('/uploads');
const filePath = path.resolve(basePath, req.params.filename);
if (!filePath.startsWith(basePath)) {
  return res.status(400).json({ error: 'Invalid path' });
}
```

---

## Secrets Detection

### Hardcoded Secrets to Watch For

| Secret Type | Pattern to Search | Example |
|-------------|-------------------|---------|
| API keys | `key`, `apikey`, `api_key` | `const API_KEY = "sk-..."` |
| Passwords | `password`, `passwd`, `secret` | `DB_PASSWORD = "prod123"` |
| Tokens | `token`, `bearer`, `jwt` | `const TOKEN = "eyJ..."` |
| Connection strings | `mongodb://`, `postgres://` | Full URLs with credentials |
| Private keys | `-----BEGIN`, `PRIVATE KEY` | RSA/SSH keys in code |
| AWS credentials | `AKIA`, `aws_secret` | AWS access key IDs start with AKIA |
| Webhook secrets | `webhook_secret`, `signing_secret` | Hardcoded webhook validation keys |

### What to Look For in Diffs

- Live secret keys or tokens assigned as string literals
- Configuration files with real credentials checked into git
- Test files using real (non-fake) tokens or API keys
- Environment variable fallbacks with real values: `process.env.KEY || "real-key"`

**Correct pattern**: Environment variables without fallbacks to real values, and test files using clearly fake placeholder values.

### Automated Detection

```yaml
# Pre-commit hook for secret scanning
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

### Logging Secrets

Red flags in logging code:

- Logging entire request objects (may contain Authorization header)
- Logging user data objects (may contain password hashes)
- Logging configuration objects (may contain connection strings)

**Correct pattern**: Sanitize objects before logging by removing sensitive fields (authorization, cookie, password, token).

---

## Dependency Review

### What to Check on New Dependencies

| Check | Why It Matters |
|-------|----------------|
| Package popularity | Low-download packages have less community scrutiny |
| Maintenance status | Unmaintained packages accumulate vulnerabilities |
| Permission scope | Does it need filesystem/network access? |
| Dependency tree depth | Transitive dependencies expand attack surface |
| Known vulnerabilities | Check npm audit / Snyk / GitHub advisories |
| License compatibility | Some licenses have viral clauses |

### Review Process for Dependency Changes

```text
New dependency added?
  -> Why? Is there a lighter alternative?
  -> Check download count and last publish date
  -> Run vulnerability scan (npm audit, Snyk)
  -> Review dependency's package.json for post-install scripts

Version bumped?
  -> Major version? Check changelog for breaking changes
  -> Patch for security fix? Verify the CVE
```

### Supply Chain Attacks to Watch For

| Attack Vector | Indicator |
|---------------|-----------|
| Typosquatting | Package name similar to popular package |
| Dependency confusion | Private package name exists on public registry |
| Post-install scripts | Suspicious scripts in dependency's package.json |
| Maintainer compromise | Sudden new version from previously inactive package |

---

## Security Headers and CORS

### Headers to Verify

Check that these security headers are set in response middleware:

| Header | Recommended Value |
|--------|-------------------|
| X-Content-Type-Options | `nosniff` |
| X-Frame-Options | `DENY` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Permissions-Policy | `camera=(), microphone=(), geolocation=()` |
| Content-Security-Policy | `default-src 'self'; script-src 'self'` |
| Strict-Transport-Security | `max-age=63072000; includeSubDomains; preload` |

### CORS Configuration Red Flags

| Pattern | Risk |
|---------|------|
| `origin: '*'` (wildcard) | Any site can make requests |
| Reflecting the request Origin header | Equivalent to wildcard |
| Wildcard + credentials | Browsers block but intent is wrong |
| No origin validation on state-changing endpoints | CSRF-like attacks |

**Correct pattern**: Explicit allowlist of trusted origins, validated on each request.

```typescript
const ALLOWED_ORIGINS = [
  'https://app.example.com',
  'https://admin.example.com',
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
}));
```

---

## Common Mistakes by Language

### JavaScript/TypeScript

| Mistake | Risk | Fix |
|---------|------|-----|
| Setting `innerHTML` from user data | XSS | Use `textContent` or sanitize |
| Prototype pollution via object spread | RCE/DoS | Validate keys, freeze prototypes |
| Regex DoS (ReDoS) | DoS | Use safe regex patterns, set timeout |
| Insecure randomness (`Math.random()`) | Predictable tokens | Use `crypto.randomUUID()` |
| Unvalidated redirects | Phishing | Validate against URL allowlist |

### Python

| Mistake | Risk | Fix |
|---------|------|-----|
| `pickle.loads()` on untrusted data | RCE | Use JSON or validated formats |
| `yaml.load()` without safe loader | RCE | Use `yaml.safe_load()` |
| Shell commands with user input | Command injection | Use `subprocess.run()` with list args |
| Mass assignment via `**kwargs` | Privilege escalation | Explicit field assignment |
| Template injection | RCE | Use `render_template()` with files, not strings |

### Go

| Mistake | Risk | Fix |
|---------|------|-----|
| Ignoring error returns | Logic bypass | Always check errors |
| Using `text/template` for HTML | XSS | Use `html/template` |
| `InsecureSkipVerify: true` | MITM | Verify TLS certificates |
| Race conditions on shared state | Data corruption | Use `sync.Mutex` or channels |
| Unchecked type assertions | Panics | Use two-value assertion form |

### Java/Kotlin

| Mistake | Risk | Fix |
|---------|------|-----|
| Default XML parser config | XXE | Disable external entities |
| `ObjectInputStream.readObject()` | RCE | Use JSON, validate types |
| String concatenation in JPQL | SQL injection | Use parameterized queries |
| Unparameterized logging | Log injection | Use parameterized log format |
| Weak cipher defaults | Broken encryption | Specify full transform (e.g., AES/GCM/NoPadding) |

---

## Security Review Quick Checklist

Use this 10-item checklist for every PR that touches security-sensitive code:

### The 10-Point Security Check

- [ ] **1. Input validation**: All user inputs validated with schema (Zod, Joi, etc.) at trust boundary
- [ ] **2. Authentication**: Auth checks present on all protected endpoints; tokens validated server-side
- [ ] **3. Authorization**: Ownership/permission verified before data access or modification (no IDOR)
- [ ] **4. No injection**: No string concatenation with user data in SQL, HTML, shell commands, or file paths
- [ ] **5. No secrets**: No hardcoded keys, tokens, passwords, or connection strings in code
- [ ] **6. Dependency safety**: New dependencies reviewed for popularity, maintenance, vulnerabilities
- [ ] **7. Error handling**: Errors do not leak stack traces, internal paths, or database schema to clients
- [ ] **8. Logging safety**: No sensitive data (passwords, tokens, PII) written to logs
- [ ] **9. CORS/headers**: CORS configured with explicit allowlist; security headers present
- [ ] **10. Cryptography**: Using standard libraries (bcrypt/argon2 for passwords; AES-GCM for encryption); no custom crypto

---

## Anti-Patterns

### 1. Security as an Afterthought

**Problem**: Security review happens only before launch, not during regular PRs.

**Fix**: Include security checks in every review. Use the 10-point checklist above.

### 2. Trusting the Framework Blindly

**Problem**: Assuming the ORM prevents all SQL injection or the framework handles all XSS.

**Fix**: Verify that framework protections are not bypassed. Raw queries, unsafe HTML rendering, and custom middleware can circumvent framework safety.

### 3. Security by Obscurity

**Problem**: Relying on hidden URLs, undocumented APIs, or unpredictable IDs for security.

**Fix**: Always enforce authentication and authorization regardless of endpoint discoverability.

### 4. Reviewing Only the Happy Path

**Problem**: Checking that the feature works correctly but not what happens with malicious input.

**Fix**: For each input, ask: "What if an attacker sends the worst possible value here?"

### 5. Ignoring Transitive Dependencies

**Problem**: Reviewing direct dependencies but ignoring the packages they depend on.

**Fix**: Use `npm audit`, Snyk, or Dependabot to scan the full dependency tree. Review lockfile changes for unexpected transitive additions.

---

## Cross-References

- [review-checklist-comprehensive.md](review-checklist-comprehensive.md) -- Full review checklist including security section
- [operational-playbook.md](operational-playbook.md) -- Priority ratings (P0 for security issues)
- [automation-tools.md](automation-tools.md) -- Snyk, Semgrep, Trivy, and other security scanners
- [../../software-security-appsec/SKILL.md](../../software-security-appsec/SKILL.md) -- Deep security audits, threat modeling, OWASP Top 10
- [../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md) -- Shared secure review checklist
