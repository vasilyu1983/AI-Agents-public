# Advanced XSS Techniques — Comprehensive Defense Guide

Modern XSS attack vectors including SVG-based XSS, mutation XSS (mXSS), polyglot payloads, and context-aware output encoding strategies based on 2024-2025 threat research.

---

## SVG-Based XSS Attacks

### Overview

SVG (Scalable Vector Graphics) files are a lesser-known but powerful vector for XSS attacks. SVG files can contain embedded JavaScript code that executes when the image is rendered in a browser, creating vulnerabilities where malicious code executes in the context of other users' sessions.

### Attack Vectors

#### 1. Direct Script Injection

```xml
<!-- Attack: Basic SVG with script tag -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert('XSS')</script>
</svg>

<!-- Attack: SVG with onload event -->
<svg onload="alert('XSS')">
</svg>

<!-- Attack: SVG with event handlers -->
<svg>
  <circle onload="alert('XSS')" />
  <circle onclick="alert('XSS')" />
  <animate onbegin="alert('XSS')" attributeName="x"/>
</svg>
```

#### 2. ForeignObject Element

The `foreignObject` element allows inclusion of elements from different XML namespaces, enabling HTML/XHTML injection:

```xml
<!-- Attack: ForeignObject with HTML injection -->
<svg xmlns="http://www.w3.org/2000/svg">
  <foreignObject width="100" height="100">
    <body xmlns="http://www.w3.org/1999/xhtml">
      <script>alert('XSS')</script>
      <iframe src="javascript:alert('XSS')"></iframe>
    </body>
  </foreignObject>
</svg>
```

This enables attacks like phishing, same-origin bypass, CSRF, and more.

#### 3. Data URI Schemes

```xml
<!-- Attack: SVG with data URI -->
<svg xmlns="http://www.w3.org/2000/svg">
  <image href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxzY3JpcHQ+YWxlcnQoJ1hTUycpPC9zY3JpcHQ+PC9zdmc+" />
</svg>
```

### Real-World Examples (2024)

**Plane v0.23 CVE**: Authenticated users could upload SVG files containing malicious JavaScript as profile images, which executed in victims' browsers when viewing the profile.

**PrivateBin <v1.4.0**: Persistent XSS vulnerability in SVG attachments allowed stored XSS attacks.

### Defense Strategies

#### Strategy 1: Content Security Policy (CSP)

```javascript
// Good: Strict CSP for SVG serving routes
app.use('/uploads/svg', (req, res, next) => {
  res.setHeader('Content-Security-Policy', "script-src 'none'; style-src 'none'");
  res.setHeader('X-Content-Type-Options', 'nosniff');
  next();
});
```

**Note**: GitHub uses this approach for user-uploaded SVGs.

#### Strategy 2: SVG Sanitization

```javascript
// Good: Whitelist-based SVG sanitization
const sanitizeSvg = (svgContent) => {
  const DOMPurify = require('isomorphic-dompurify');

  const clean = DOMPurify.sanitize(svgContent, {
    USE_PROFILES: { svg: true, svgFilters: true },
    ALLOWED_TAGS: [
      'svg', 'circle', 'ellipse', 'line', 'path', 'polygon',
      'polyline', 'rect', 'g', 'defs', 'clipPath', 'linearGradient',
      'radialGradient', 'stop', 'filter'
    ],
    ALLOWED_ATTR: [
      'width', 'height', 'viewBox', 'xmlns', 'fill', 'stroke',
      'stroke-width', 'd', 'cx', 'cy', 'r', 'x', 'y', 'x1', 'y1',
      'x2', 'y2', 'points', 'id', 'class'
    ],
    // Block all event handlers
    FORBID_ATTR: [
      'onload', 'onclick', 'onmouseover', 'onerror', 'onbegin',
      'onend', 'onrepeat', 'onabort'
    ],
    // Block script and foreignObject
    FORBID_TAGS: ['script', 'foreignObject', 'iframe', 'embed', 'object']
  });

  return clean;
};

// Usage
app.post('/api/upload-svg', upload.single('svg'), async (req, res) => {
  const svgContent = await fs.readFile(req.file.path, 'utf8');

  // Sanitize SVG
  const cleanSvg = sanitizeSvg(svgContent);

  // Save sanitized version
  await fs.writeFile(`/uploads/clean/${req.file.filename}`, cleanSvg);

  res.json({ success: true });
});
```

#### Strategy 3: Rendering Context Control

```html
<!-- Good: SVG in img tag (browser prevents script execution) -->
<img src="/uploads/user-avatar.svg" alt="User avatar">

<!-- WARNING: Opening SVG in new tab bypasses this protection! -->
```

Modern browsers do not execute scripts inside `<img>` tags, making this approach safe for embedded SVGs. However, if users open the SVG in a new tab (right-click → "Open in new tab"), this protection is circumvented.

#### Strategy 4: Convert to Raster Format

```javascript
// Good: Convert SVG to PNG on upload (eliminates all script risks)
const sharp = require('sharp');

app.post('/api/upload-svg', upload.single('svg'), async (req, res) => {
  const svgBuffer = await fs.readFile(req.file.path);

  // Convert to PNG
  const pngBuffer = await sharp(svgBuffer)
    .png()
    .resize(800, 800, { fit: 'inside' })
    .toBuffer();

  const filename = `${crypto.randomUUID()}.png`;
  await fs.writeFile(`/uploads/${filename}`, pngBuffer);

  // Delete original SVG
  await fs.unlink(req.file.path);

  res.json({ filename });
});
```

---

## Mutation XSS (mXSS)

### Overview

Mutation XSS occurs when HTML is sanitized, stored, and then reparsed, causing the DOM structure to mutate and introduce XSS vulnerabilities. The HTML spec warns that "serializing and reparsing HTML fragments may not return the original tree structure," which is the root cause of mXSS.

### Why mXSS Works

The pattern `div.innerHTML = DOMPurify.sanitize(html)` is "prone to mutation XSS by design" because:

1. DOMPurify sanitizes the HTML string
2. Browser parses the sanitized HTML
3. JavaScript serializes the DOM back to string (e.g., for storage)
4. Browser reparses the serialized HTML
5. The reparsed DOM may differ from step 2, introducing XSS

### Recent DOMPurify Bypasses (2024)

#### Bypass 1: Namespace Confusion (DOMPurify ≤ 2.0.17)

```html
<!-- Attack: MathML namespace confusion -->
<form>
  <math>
    <mtext></form>
      <form>
        <mglyph>
          <style></math>
            <img src onerror=alert('XSS')>
```

The `mglyph` and `malignmark` elements exist in the MathML namespace when they're direct children of MathML text integration points, causing namespace changes on reparsing.

#### Bypass 2: DOMPurify 3.1.0 (April 2024)

Full bypass discovered by @IcesFont using new mutation concepts involving node flattening and form reordering.

#### Bypass 3: Comment-Based Mutations

```html
<!-- Attack: Encoded HTML comments -->
<div><!-- &lt;img src=x onerror=alert('XSS')&gt; --></div>
```

DOMPurify's patch looked for mutations in text nodes but didn't account for comments, allowing bypasses.

#### Bypass 4: Second-Order DOM Clobbering (DOMPurify 3.1.2)

Combined "Elevator" HTML mutation technique with second-order DOM clobbering.

### Defense Against mXSS

```javascript
// Good: Avoid innerHTML pattern entirely
// Use DOM methods instead
const createSafeElement = (tagName, textContent) => {
  const element = document.createElement(tagName);
  element.textContent = textContent; // textContent is XSS-safe
  return element;
};

// Good: Use modern framework with auto-escaping
// React example
const UserComment = ({ comment }) => {
  return <div>{comment}</div>; // React auto-escapes
};

// Good: If you must use innerHTML, use DOMPurify with RETURN_DOM
const sanitizeForInnerHTML = (dirty) => {
  const clean = DOMPurify.sanitize(dirty, {
    RETURN_DOM: true,
    RETURN_DOM_FRAGMENT: true
  });

  // Append DOM nodes directly instead of innerHTML
  targetElement.appendChild(clean);
};

// Good: Server-side sanitization + CSP
app.post('/api/comments', async (req, res) => {
  // Sanitize on server
  const clean = DOMPurify.sanitize(req.body.comment, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  });

  await Comment.create({ content: clean });
  res.json({ success: true });
});

// Client-side: Add CSP to prevent any script execution
res.setHeader('Content-Security-Policy',
  "default-src 'self'; script-src 'none'; object-src 'none'");
```

### Best Practices

1. **Use modern frameworks** (React, Vue, Angular) with built-in XSS protection
2. **Avoid innerHTML** when possible; use `textContent` or DOM methods
3. **If using DOMPurify**, use `RETURN_DOM` instead of string output
4. **Implement strict CSP** as defense-in-depth
5. **Keep sanitization libraries updated** (mXSS bypasses are discovered regularly)
6. **Sanitize server-side** + client-side (defense in depth)

---

## Context-Aware Output Encoding

### Overview

Different output contexts require different encoding methods. Using HTML entity encoding in JavaScript context won't prevent XSS and may even introduce vulnerabilities.

### The Five Critical Contexts

#### Context 1: HTML Element Content

```javascript
// Bad: No encoding
const html = `<div>${userInput}</div>`;

// Good: HTML entity encoding
const escapeHtml = (text) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  return text.replace(/[&<>"'/]/g, (char) => map[char]);
};

const safe = `<div>${escapeHtml(userInput)}</div>`;
```

#### Context 2: HTML Attribute

```javascript
// Bad: No encoding (vulnerable even with quotes)
const html = `<input value="${userInput}">`;
// Attack: userInput = '" onload="alert(\'XSS\')'

// Good: HTML attribute encoding (encode ALL non-alphanumeric)
const escapeHtmlAttribute = (text) => {
  return text.replace(/[^a-zA-Z0-9]/g, (char) => {
    return `&#x${char.charCodeAt(0).toString(16)};`;
  });
};

const safe = `<input value="${escapeHtmlAttribute(userInput)}">`;

// Better: Use data attributes for complex values
const safe2 = `<div data-user="${escapeHtmlAttribute(JSON.stringify(user))}"></div>`;
```

#### Context 3: JavaScript

```javascript
// Bad: No encoding (extremely dangerous)
const script = `<script>var name = "${userInput}";</script>`;
// Attack: userInput = '"; alert("XSS"); //'

// Good: JavaScript string encoding
const escapeJavaScript = (text) => {
  return text.replace(/[^a-zA-Z0-9]/g, (char) => {
    const code = char.charCodeAt(0);
    if (code < 256) {
      return `\\x${code.toString(16).padStart(2, '0')}`;
    }
    return `\\u${code.toString(16).padStart(4, '0')}`;
  });
};

const safe = `<script>var name = "${escapeJavaScript(userInput)}";</script>`;

// Better: Use JSON encoding + textContent
const better = `
<script>
  var userData = ${JSON.stringify({ name: userInput })};
  document.getElementById('name').textContent = userData.name;
</script>
`;

// Best: Avoid inline scripts entirely
// Use data attributes + external script
const best = `<div id="user-name" data-name="${escapeHtmlAttribute(userInput)}"></div>`;
// External script reads data attribute safely
```

#### Context 4: CSS

```javascript
// Bad: User input in style tag
const style = `<style>.user { color: ${userInput}; }</style>`;
// Attack: userInput = 'red; } body { background: url(javascript:alert(1)); } .x {'

// Good: CSS encoding
const escapeCss = (text) => {
  return text.replace(/[^a-zA-Z0-9]/g, (char) => {
    return `\\${char.charCodeAt(0).toString(16)} `;
  });
};

const safe = `<style>.user { color: ${escapeCss(userInput)}; }</style>`;

// Better: Validate against allowlist
const allowedColors = ['red', 'blue', 'green', 'black', 'white'];

const validateColor = (color) => {
  if (!allowedColors.includes(color)) {
    throw new ValidationError('Invalid color');
  }
  return color;
};

const safer = `<style>.user { color: ${validateColor(userInput)}; }</style>`;

// Best: Use inline style with DOM API
element.style.color = userInput; // Browser handles encoding
```

#### Context 5: URL

```javascript
// Bad: User input in href
const html = `<a href="${userInput}">Click</a>`;
// Attack: userInput = 'javascript:alert(1)'

// Good: URL encoding + protocol validation
const escapeUrl = (url) => {
  // Validate protocol first
  const allowedProtocols = ['http:', 'https:', 'mailto:'];

  try {
    const parsed = new URL(url);

    if (!allowedProtocols.includes(parsed.protocol)) {
      throw new Error('Invalid protocol');
    }

    // URL constructor handles encoding
    return parsed.href;
  } catch (error) {
    // Not a valid URL, encode as path
    return encodeURIComponent(url);
  }
};

const safe = `<a href="${escapeUrl(userInput)}">Click</a>`;

// Better: Allowlist domains
const validateUrl = (url) => {
  const allowedDomains = ['example.com', 'trusted.com'];

  try {
    const parsed = new URL(url);

    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new Error('Invalid protocol');
    }

    if (!allowedDomains.includes(parsed.hostname)) {
      throw new Error('Domain not allowed');
    }

    return parsed.href;
  } catch (error) {
    throw new ValidationError('Invalid URL');
  }
};
```

### Context Decision Tree

```
User Input → Output Context?
│
├─ HTML Element Content → HTML Entity Encoding
│   └─ Example: <div>${escape(input)}</div>
│
├─ HTML Attribute → HTML Attribute Encoding (all non-alphanumeric)
│   └─ Example: <input value="${escapeAttr(input)}">
│
├─ JavaScript → JavaScript Hex Encoding
│   └─ Example: <script>var x = "${escapeJS(input)}";</script>
│
├─ CSS → CSS Hex Encoding + Allowlist
│   └─ Example: <style>.x { color: ${escapeCSS(input)}; }</style>
│
└─ URL → URL Encoding + Protocol Validation
    └─ Example: <a href="${escapeURL(input)}">
```

### Encoding Libraries (2024)

```javascript
// OWASP Encoder (Java)
// import org.owasp.encoder.Encode;
// String safe = Encode.forHtml(userInput);
// String safeJS = Encode.forJavaScript(userInput);

// Microsoft AntiXSS (.NET)
// using Microsoft.Security.Application;
// string safe = Encoder.HtmlEncode(userInput);
// string safeJS = Encoder.JavaScriptEncode(userInput);

// Node.js - he library
const he = require('he');

const encodeByContext = (input, context) => {
  switch (context) {
    case 'html':
      return he.encode(input);

    case 'htmlAttribute':
      return he.encode(input, { useNamedReferences: false });

    case 'javascript':
      return input.replace(/[^a-zA-Z0-9]/g, (char) => {
        return `\\x${char.charCodeAt(0).toString(16).padStart(2, '0')}`;
      });

    case 'css':
      return input.replace(/[^a-zA-Z0-9]/g, (char) => {
        return `\\${char.charCodeAt(0).toString(16)} `;
      });

    case 'url':
      return encodeURIComponent(input);

    default:
      throw new Error('Unknown context');
  }
};
```

---

## Polyglot XSS Payloads

### Overview

Polyglot XSS payloads are snippets of code designed to work across multiple contexts (HTML, JavaScript, attributes, URLs) simultaneously. They leverage multiple encoding, injection, and obfuscation techniques to bypass filters and confuse parsers.

### Why Polyglots are Dangerous

1. **Context-agnostic**: Work regardless of where input is reflected
2. **Bypass filters**: Use obfuscation to evade pattern matching
3. **Hard to detect**: Traditional scanners struggle with polyglot syntax
4. **Multiple attack vectors**: Exploit several contexts at once

### Classic Polyglot Example (0xsobky)

```javascript
// This payload works in multiple contexts
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```

This works in:
- HTML element content
- HTML attribute (with/without quotes)
- JavaScript string (single/double quotes)
- URL context
- CSS context

### Recent Research (2024)

#### USENIX Security 2024: Genetic Algorithm Generation

Researchers used genetic algorithms to automatically generate polyglot payloads that work across even more contexts, making them harder to detect.

#### Machine Learning Detection (December 2024)

Despite advances in polyglot generation, detection remains limited. Traditional pattern matching fails, and ML-based detection is still in early stages.

### Defense Against Polyglots

```javascript
// Bad: Single-context encoding (polyglot bypasses)
const weak = `<div>${escapeHtml(userInput)}</div>`;
// If userInput is reflected elsewhere in JS context, polyglot may work

// Good: Multi-layer defense
const strongDefense = {
  // Layer 1: Input validation (allowlist)
  validate: (input) => {
    // Strict allowlist - reject anything suspicious
    if (/<script|javascript:|on\w+=/i.test(input)) {
      throw new ValidationError('Invalid input detected');
    }
    return input;
  },

  // Layer 2: Context-specific encoding
  encode: (input, context) => {
    const validated = strongDefense.validate(input);

    switch (context) {
      case 'html':
        return escapeHtml(validated);
      case 'js':
        return escapeJavaScript(validated);
      case 'url':
        return escapeUrl(validated);
      default:
        throw new Error('Unknown context');
    }
  },

  // Layer 3: CSP
  csp: "default-src 'self'; script-src 'self' 'nonce-{random}'; object-src 'none'",

  // Layer 4: Additional headers
  headers: {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block'
  }
};

// Usage
app.get('/profile', (req, res) => {
  const userName = req.query.name;

  res.set(strongDefense.headers);
  res.set('Content-Security-Policy', strongDefense.csp);

  res.send(`
    <div>${strongDefense.encode(userName, 'html')}</div>
    <script nonce="{random}">
      var name = "${strongDefense.encode(userName, 'js')}";
    </script>
  `);
});
```

### Polyglot Detection Patterns

```javascript
// Good: Detect common polyglot patterns
const detectPolyglot = (input) => {
  const polyglotPatterns = [
    // Mixed quotes and context switching
    /['"]\s*\/?\*.*?\*\s*\/?\s*['"]/i,

    // JavaScript protocol in unusual contexts
    /javascript\s*:/i,

    // Event handlers with encoding
    /on\w+\s*=\s*[\w\(\)]/i,

    // HTML tags with unusual attributes
    /<\w+[^>]*on\w+\s*=/i,

    // Script tags with obfuscation
    /<script[\s\S]*?>/i,

    // SVG with events
    /<svg[^>]*on\w+/i,

    // Data URIs
    /data:text\/html/i,

    // Multiple encoding layers
    /&#x[0-9a-f]{2}/i
  ];

  for (const pattern of polyglotPatterns) {
    if (pattern.test(input)) {
      return true;
    }
  }

  return false;
};

// Usage
app.post('/api/comment', (req, res) => {
  const comment = req.body.comment;

  if (detectPolyglot(comment)) {
    logger.warn('Polyglot XSS attempt detected', {
      input: comment,
      ip: req.ip
    });

    return res.status(400).json({ error: 'Invalid input' });
  }

  // Proceed with sanitization
  const clean = DOMPurify.sanitize(comment);
  res.json({ success: true });
});
```

---

## 2024 Threat Landscape

### Major Incidents

**June 2024: Polyfill.io Supply Chain Attack**
- Single JavaScript injection compromised 100,000+ websites
- Largest JavaScript injection attack of 2024
- Highlights importance of:
  - Subresource Integrity (SRI)
  - Dependency auditing
  - CSP strict-dynamic

### Emerging Trends

1. **AI-Generated Polyglots**: Genetic algorithms creating novel payloads
2. **Framework Bypasses**: XSS in React, Vue, Angular (improper use of `dangerouslySetInnerHTML`, `v-html`)
3. **Supply Chain XSS**: Compromised npm packages injecting XSS
4. **mXSS Evolution**: New namespace confusion techniques

### 2025 Recommendations

1. **Adopt strict CSP** with nonces/hashes (not `unsafe-inline`)
2. **Use Trusted Types API** (Chrome/Edge) to prevent DOM XSS
3. **Implement SRI** for all third-party scripts
4. **Regular dependency audits** (npm audit, Snyk, Dependabot)
5. **Framework security best practices** (avoid dangerous methods)
6. **Server-side sanitization** + client-side encoding (defense in depth)

---

## Comprehensive Defense Checklist

### Input Layer
- [ ] Strict allowlist validation on all inputs
- [ ] Length limits enforced
- [ ] Data type validation (string, number, email, URL)
- [ ] Reject inputs matching polyglot patterns

### Processing Layer
- [ ] Server-side sanitization with DOMPurify
- [ ] Context-aware output encoding (HTML, JS, CSS, URL)
- [ ] Avoid innerHTML; use textContent or DOM methods
- [ ] Use modern frameworks with auto-escaping

### Output Layer
- [ ] CSP headers with nonces/hashes (no `unsafe-inline`)
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] Trusted Types API enabled (if supported)

### File Upload Layer
- [ ] SVG sanitization or rasterization
- [ ] MIME type validation (server-side)
- [ ] File content verification (magic bytes)
- [ ] CSP for SVG serving routes
- [ ] Serve user uploads from separate domain

### Monitoring Layer
- [ ] Log all XSS attempts (polyglot detection)
- [ ] Real-time alerting on suspicious patterns
- [ ] Regular security audits and penetration testing
- [ ] Dependency vulnerability scanning

---

## References

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP DOM-based XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [PortSwigger: DOMPurify Mutation XSS Bypasses](https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss)
- [USENIX Security 2024: Polyglot Synthesis](https://www.usenix.org/conference/usenixsecurity24)
- [GitHub Security Advisories: SVG XSS (2024)](https://github.com/makeplane/plane/security/advisories/GHSA-rcg8-g69v-x23j)
