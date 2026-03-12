# Dependency Selection Guide

**When to Use**: Deciding whether to add a new dependency or choosing between similar packages.

---

## Minimal Dependencies Principle

Every dependency added to your project increases:
- Attack surface area
- Bundle size
- Maintenance burden
- Supply chain risk
- Build complexity

**Golden Rule**: The best dependency is the one you don't add.

---

## Questions to Ask Before Adding a Dependency

### 1. Do I Really Need This?

**Can I implement this in <100 lines of code?**

Many utility libraries can be replaced with simple native implementations:

```javascript
// BAD: Don't add 'is-odd' package
const isOdd = require('is-odd')

// GOOD: Use simple function
const isOdd = (n) => n % 2 !== 0

// BAD: Don't add 'left-pad' package
const leftPad = require('left-pad')

// GOOD: Use native method
const leftPad = (str, len) => str.padStart(len, '0')

// BAD: Don't add 'axios' for simple requests
const axios = require('axios')
const data = await axios.get(url)

// GOOD: Use native fetch
const response = await fetch(url)
const data = await response.json()
```

**Native alternatives often exist:**

| Instead of | Use Native |
|-----------|------------|
| `moment` | `Intl.DateTimeFormat`, `Date` |
| `lodash.debounce` | Simple timeout wrapper |
| `uuid` | `crypto.randomUUID()` (Node 14.17+) |
| `axios` | `fetch` API |
| `is-array` | `Array.isArray()` |
| `query-string` | `URLSearchParams` |

### 2. Is This Package Well-Maintained?

**Maintenance Checklist:**

- [ ] **Last commit within 6 months** - Active development
- [ ] **Active issue resolution** - Check open/closed ratio
- [ ] **Weekly downloads >10k** - Community adoption
- [ ] **Multiple maintainers** - Bus factor > 1
- [ ] **CI/Tests passing** - Quality assurance
- [ ] **Changelog maintained** - Clear release notes
- [ ] **Responsive to security issues** - Check GitHub Security tab

**Red Flags:**

- [WARNING] No commits in 2+ years
- [WARNING] Low weekly downloads (<1000)
- [WARNING] No tests or CI
- [WARNING] Single maintainer with no recent activity
- [WARNING] Many open security issues
- [WARNING] No documentation or examples

**Where to Check:**

```bash
# View package metadata
npm info <package>

# Check GitHub activity
npm repo <package>

# View npm package page
npm home <package>
```

### 3. What's the Dependency Tree Size?

**View dependency tree:**

```bash
npm ls <package>        # Show dependency tree
npm info <package>      # Show package metadata
pnpm why <package>      # Show why package is installed
```

**Example output:**

```bash
$ npm ls axios
myapp@1.0.0
└─┬ axios@1.6.0
  ├── follow-redirects@1.15.3
  ├── form-data@4.0.0
  │ ├── asynckit@0.4.0
  │ ├── combined-stream@1.0.8
  │ │ └── delayed-stream@1.0.0
  │ └── mime-types@2.1.35
  │   └── mime-db@1.52.0
  └── proxy-from-env@1.1.0
```

**Red Flags:**

- Large dependency tree (>50 transitive deps)
- Circular dependencies
- Conflicting peer dependencies
- Multiple versions of same package

### 4. What's the Bundle Size Impact?

**For JavaScript/TypeScript:**

Use [Bundlephobia](https://bundlephobia.com/) to check:

- **Minified size** - Production bundle impact
- **Minified + gzipped** - Network transfer size
- **Tree-shakeable** - Can unused code be removed?

**Command-line check:**

```bash
# Check package size
npm info <package> size

# Compare with alternative
npm info date-fns size
npm info dayjs size
npm info moment size
```

**Example comparison:**

| Package | Minified | Gzipped | Verdict |
|---------|----------|---------|---------|
| `moment` | 229 kB | 71.6 kB | [FAIL] Too large |
| `date-fns` | 78.4 kB | 13.4 kB | GOOD |
| `dayjs` | 6.5 kB | 2.6 kB | [OK] Best |

**Guidelines:**

- <10 kB gzipped: [OK] Excellent
- 10-50 kB gzipped: [YELLOW] Acceptable
- >50 kB gzipped: [WARNING] Evaluate carefully
- >100 kB gzipped: [FAIL] Likely too large

### 5. What Are the Security Risks?

**Security audit:**

```bash
# Check for vulnerabilities
npm audit
npm audit --json | jq '.vulnerabilities'

# Check specific package
npm audit <package>

# Use third-party scanners
npx snyk test
```

**Check vulnerability databases:**

- [npm advisory database](https://github.com/advisories)
- [Snyk vulnerability DB](https://snyk.io/vuln/)
- [CVE database](https://cve.mitre.org/)

**Red Flags:**

- Critical/High severity CVEs in last 12 months
- Known supply chain attacks
- No security policy (`SECURITY.md`)
- No contact for security issues

### 6. Are There Better Alternatives?

**Evaluation matrix:**

| Criterion | Tool/Check |
|-----------|-----------|
| Popularity | npm registry, GitHub stars |
| Maintenance | Last commit, issue response time |
| Bundle Size | Bundlephobia |
| Performance | Benchmarks, real-world tests |
| Security | npm audit, Snyk |
| Documentation | README, website quality |
| API Design | TypeScript support, ease of use |
| Dependencies | `npm ls`, transitive count |
| License | Check LICENSE file |

---

## Choosing Between Similar Packages

### Step-by-Step Evaluation

**1. Create comparison table:**

| Criterion | Package A | Package B | Package C |
|-----------|-----------|-----------|-----------|
| Weekly downloads | 10M | 5M | 1M |
| Bundle size (gzipped) | 13 kB | 7 kB | 25 kB |
| Last update | 2 weeks | 1 month | 6 months |
| GitHub stars | 45k | 20k | 8k |
| Open issues | 150 | 50 | 300 |
| TypeScript support | [OK] | [OK] | [FAIL] |
| Tree-shakeable | [OK] | [OK] | [FAIL] |
| CVEs (last 12mo) | 0 | 0 | 2 |

**2. Test API ergonomics:**

Try each package in a sandbox:

```javascript
// Package A
import { format } from 'date-fns'
format(new Date(), 'yyyy-MM-dd')

// Package B
import dayjs from 'dayjs'
dayjs().format('YYYY-MM-DD')

// Package C - Native
new Intl.DateTimeFormat('en-CA').format(new Date())
```

**3. Consider ecosystem fit:**

- Does it work with your framework? (React, Vue, Angular)
- Does it support your build tools? (Vite, webpack, esbuild)
- Is it actively used in your stack's ecosystem?

**4. Document your choice:**

Create an Architecture Decision Record (ADR):

```markdown
# ADR 001: Date Library Selection

## Status
Accepted

## Context
We need a date formatting/manipulation library for the user dashboard.

## Decision
Use `date-fns` over `dayjs` and `moment`.

## Rationale
- Tree-shakeable (import only what we use)
- TypeScript support (native types)
- 13 kB gzipped vs moment's 71 kB
- Active maintenance (weekly releases)
- No security issues in last 2 years
- Functional API fits our codebase style

## Alternatives Considered
- `moment`: Deprecated, too large
- `dayjs`: Smaller, but less mature ecosystem
- Native `Intl`: Insufficient for complex formatting needs

## Consequences
- Bundle size increase: +13 kB gzipped
- Team needs to learn date-fns API
- Migration path from moment already documented
```

---

## Real-World Examples

### Example 1: Date Libraries (JavaScript)

| Library | Bundle Size | Downloads/week | Last Update | Verdict |
|---------|------------|----------------|-------------|---------|
| `moment` | 229 kB | 10M+ | Maintenance mode | [FAIL] Deprecated |
| `date-fns` | 13 kB | 12M+ | Active | [OK] Recommended |
| `dayjs` | 7 kB | 10M+ | Active | [OK] Lightweight alternative |
| Native `Intl` | 0 kB | Native | N/A | [OK] Best (no dependency) |

**Recommendation**: Use native `Intl` for simple formatting, `date-fns` for complex needs.

### Example 2: HTTP Clients (JavaScript)

| Library | Bundle Size | Downloads/week | TypeScript | Verdict |
|---------|------------|----------------|------------|---------|
| `axios` | 14 kB | 50M+ | [OK] | GOOD (features-rich) |
| `got` | 50 kB | 5M+ | [OK] | [YELLOW] Node.js only |
| `ky` | 5 kB | 2M+ | [OK] | [OK] Lightweight |
| Native `fetch` | 0 kB | Native | [OK] | [OK] Best (modern browsers) |

**Recommendation**: Use native `fetch` for simple requests, `axios` for complex needs (interceptors, retries).

### Example 3: State Management (React)

| Library | Bundle Size | Learning Curve | Ecosystem | Verdict |
|---------|------------|----------------|-----------|---------|
| Redux | 6 kB | High | Large | [OK] Enterprise apps |
| Zustand | 3 kB | Low | Growing | [OK] Simple apps |
| Jotai | 3 kB | Medium | Modern | [OK] Atomic state |
| Context API | 0 kB | Low | Native | [OK] Simple state |

**Recommendation**: Start with Context API, add Zustand for global state, Redux for complex apps only.

---

## Checklist: Before Adding Any Dependency

Use this checklist for EVERY dependency you consider adding:

**Necessity:**
- [ ] Can I implement this in <100 lines of native code?
- [ ] Does a native alternative exist? (check MDN, language docs)
- [ ] Is this solving a real problem (not premature optimization)?

**Maintenance:**
- [ ] Last commit within 6 months?
- [ ] Active issue resolution?
- [ ] Weekly downloads >10k?
- [ ] Multiple maintainers?
- [ ] CI/tests passing?

**Quality:**
- [ ] Bundle size acceptable? (<50 kB gzipped)
- [ ] Dependency tree reasonable? (<20 transitive deps)
- [ ] TypeScript support? (if using TypeScript)
- [ ] Tree-shakeable? (for JS libraries)
- [ ] Good documentation?

**Security:**
- [ ] No critical/high CVEs in last 12 months?
- [ ] Has security policy (`SECURITY.md`)?
- [ ] Passed `npm audit` / `snyk test`?
- [ ] License compatible with project?

**Alternatives:**
- [ ] Compared 2-3 alternatives?
- [ ] Documented choice in ADR?
- [ ] Team reviewed decision?

---

## When to REJECT a Dependency

**Automatic Rejection Criteria:**

1. **Critical security vulnerability** with no fix available
2. **Abandoned package** (no commits in 2+ years)
3. **Incompatible license** (GPL in proprietary project)
4. **Massive bundle size** (>100 kB for simple utility)
5. **Better native alternative** exists (e.g., fetch vs axios for simple GET)
6. **Can implement in <50 lines** of simple code

**Example rejections:**

```javascript
// BAD: REJECT: 'is-odd' package (1 line native implementation)
// npm install is-odd
const isOdd = (n) => n % 2 !== 0

// BAD: REJECT: 'left-pad' package (1 line native)
// npm install left-pad
const leftPad = (str, len) => str.padStart(len, '0')

// BAD: REJECT: 'moment' (deprecated, 229 kB)
// Use date-fns (13 kB) or native Intl

// BAD: REJECT: 'request' (deprecated since 2020)
// Use axios or native fetch
```

---

## Summary

**The Dependency Decision Tree:**

```
Should I add this dependency?
    ├─ Can I implement in <100 LOC? → YES → Don't add
    ├─ Is there a native alternative? → YES → Use native
    ├─ Is it well-maintained? → NO → Don't add
    ├─ Bundle size acceptable? → NO → Find alternative
    ├─ Security audit clean? → NO → Don't add
    └─ All checks pass → Add with caution, document choice
```

**Remember:** Every dependency is a liability. Add dependencies deliberately, not reflexively.
