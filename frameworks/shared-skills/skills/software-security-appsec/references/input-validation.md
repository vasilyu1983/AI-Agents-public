# Input Validation & Sanitization

Comprehensive guide to preventing injection attacks through proper input validation and output encoding.

---

## Core Principles

**1. Never Trust User Input**: All input from users, external systems, or files is potentially malicious
**2. Allowlist Over Blocklist**: Define what IS allowed, not what ISN'T
**3. Validate Early, Sanitize Late**: Validate at entry, sanitize at output
**4. Defense in Depth**: Multiple layers of validation and encoding
**5. Context-Specific Encoding**: Different encoding for HTML, JavaScript, SQL, URLs

---

## Input Validation Patterns

### Pattern 1: Allowlist Validation

```javascript
// Good: Strict allowlist for username
const validateUsername = (username) => {
  // Only alphanumeric and underscore, 3-20 characters
  const regex = /^[a-zA-Z0-9_]{3,20}$/;

  if (!regex.test(username)) {
    throw new ValidationError('Username must be 3-20 alphanumeric characters or underscores');
  }

  return username;
};

// Good: Email validation
const validateEmail = (email) => {
  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  if (!regex.test(email) || email.length > 254) {
    throw new ValidationError('Invalid email format');
  }

  return email.toLowerCase().trim();
};

// Good: Phone number validation
const validatePhone = (phone) => {
  // E.164 format: +[country code][number]
  const regex = /^\+[1-9]\d{1,14}$/;

  if (!regex.test(phone)) {
    throw new ValidationError('Phone number must be in E.164 format');
  }

  return phone;
};

// Good: URL validation
const validateUrl = (url) => {
  try {
    const parsed = new URL(url);

    // Only allow HTTP/HTTPS
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new ValidationError('Only HTTP/HTTPS URLs allowed');
    }

    // Optional: Check domain allowlist
    const allowedDomains = ['example.com', 'api.example.com'];
    if (!allowedDomains.includes(parsed.hostname)) {
      throw new ValidationError('Domain not allowed');
    }

    return url;
  } catch (error) {
    throw new ValidationError('Invalid URL');
  }
};
```

### Pattern 2: Data Type Validation

```javascript
// Good: Type validation with schema
const Joi = require('joi');

const userSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(20).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(13).max(120).required(),
  website: Joi.string().uri().optional(),
  bio: Joi.string().max(500).optional()
});

const validateUser = (data) => {
  const { error, value } = userSchema.validate(data, {
    abortEarly: false,
    stripUnknown: true
  });

  if (error) {
    const errors = error.details.map(detail => ({
      field: detail.path.join('.'),
      message: detail.message
    }));

    throw new ValidationError('Validation failed', { errors });
  }

  return value;
};

// Usage
app.post('/api/users', (req, res) => {
  try {
    const validatedData = validateUser(req.body);
    const user = await User.create(validatedData);
    res.json(user);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

### Pattern 3: File Upload Validation

```javascript
const multer = require('multer');
const path = require('path');
const crypto = require('crypto');

// Good: Comprehensive file upload validation
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, '/uploads/temp/');
  },
  filename: (req, file, cb) => {
    // Generate random filename to prevent directory traversal
    const randomName = crypto.randomBytes(16).toString('hex');
    const ext = path.extname(file.originalname);
    cb(null, `${randomName}${ext}`);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
    files: 1
  },
  fileFilter: (req, file, cb) => {
    // Allowlist MIME types
    const allowedMimes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'application/pdf'
    ];

    if (!allowedMimes.includes(file.mimetype)) {
      return cb(new Error('Invalid file type'));
    }

    // Allowlist extensions
    const allowedExts = ['.jpg', '.jpeg', '.png', '.gif', '.pdf'];
    const ext = path.extname(file.originalname).toLowerCase();

    if (!allowedExts.includes(ext)) {
      return cb(new Error('Invalid file extension'));
    }

    cb(null, true);
  }
});

// Additional validation: Verify file content
const verifyFileContent = async (filepath, expectedMime) => {
  const FileType = await import('file-type');
  const type = await FileType.fileTypeFromFile(filepath);

  if (!type || type.mime !== expectedMime) {
    throw new ValidationError('File content does not match extension');
  }

  return true;
};

// Usage
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    // Verify file content matches MIME type
    await verifyFileContent(req.file.path, req.file.mimetype);

    // Scan for malware (optional)
    // await scanForMalware(req.file.path);

    // Move to permanent storage
    const finalPath = `/uploads/${req.file.filename}`;
    await fs.rename(req.file.path, finalPath);

    res.json({ filename: req.file.filename });
  } catch (error) {
    // Clean up file on error
    await fs.unlink(req.file.path).catch(() => {});
    res.status(400).json({ error: error.message });
  }
});
```

### Pattern 4: SVG File Upload Security (2024)

SVG files can contain embedded JavaScript and are a common XSS vector. Apply multiple defense layers:

```javascript
const DOMPurify = require('isomorphic-dompurify');
const sharp = require('sharp');
const fs = require('fs').promises;

// Strategy 1: SVG Sanitization (preserve vector format)
const sanitizeSvgFile = async (filepath) => {
  const svgContent = await fs.readFile(filepath, 'utf8');

  // Whitelist-based sanitization
  const clean = DOMPurify.sanitize(svgContent, {
    USE_PROFILES: { svg: true, svgFilters: true },
    ALLOWED_TAGS: [
      'svg', 'circle', 'ellipse', 'line', 'path', 'polygon',
      'polyline', 'rect', 'g', 'defs', 'clipPath', 'linearGradient',
      'radialGradient', 'stop', 'filter', 'feGaussianBlur',
      'feOffset', 'feBlend', 'feColorMatrix'
    ],
    ALLOWED_ATTR: [
      'width', 'height', 'viewBox', 'xmlns', 'fill', 'stroke',
      'stroke-width', 'd', 'cx', 'cy', 'r', 'rx', 'ry', 'x', 'y',
      'x1', 'y1', 'x2', 'y2', 'points', 'id', 'class', 'transform',
      'gradientUnits', 'gradientTransform', 'offset', 'stop-color',
      'stop-opacity', 'stdDeviation', 'in', 'result'
    ],
    FORBID_TAGS: [
      'script', 'foreignObject', 'iframe', 'embed', 'object',
      'use', 'image', 'a', 'animate', 'animateTransform', 'set'
    ],
    FORBID_ATTR: [
      'onload', 'onclick', 'onmouseover', 'onerror', 'onbegin',
      'onend', 'onrepeat', 'onabort', 'onfocus', 'onblur',
      'xlink:href', 'href'
    ]
  });

  // Additional validation: Check for data URIs
  if (clean.includes('data:') || clean.includes('javascript:')) {
    throw new ValidationError('Forbidden content detected in SVG');
  }

  return clean;
};

// Strategy 2: Convert SVG to Raster (most secure)
const convertSvgToRaster = async (svgPath, outputPath) => {
  const svgBuffer = await fs.readFile(svgPath);

  await sharp(svgBuffer)
    .png()
    .resize(2000, 2000, {
      fit: 'inside',
      withoutEnlargement: true
    })
    .toFile(outputPath);

  return outputPath;
};

// Strategy 3: Serve with CSP (if preserving SVG)
const serveSvgWithCSP = (req, res, next) => {
  res.setHeader('Content-Security-Policy', "script-src 'none'; style-src 'none'");
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Content-Type', 'image/svg+xml');
  next();
};

// Comprehensive SVG upload handler
app.post('/api/upload-svg', upload.single('svg'), async (req, res) => {
  try {
    const file = req.file;

    // Validate SVG extension
    if (path.extname(file.originalname).toLowerCase() !== '.svg') {
      throw new ValidationError('Invalid file extension');
    }

    // Validate MIME type
    if (file.mimetype !== 'image/svg+xml') {
      throw new ValidationError('Invalid MIME type');
    }

    // Validate filename doesn't bypass with spaces (CVE-2024-11404)
    if (file.originalname.includes(' .svg') || /\s+\.svg$/i.test(file.originalname)) {
      throw new ValidationError('Invalid filename format');
    }

    // Option A: Sanitize and preserve as SVG
    const cleanSvg = await sanitizeSvgFile(file.path);
    const svgPath = `/uploads/svg/${crypto.randomUUID()}.svg`;
    await fs.writeFile(svgPath, cleanSvg);

    // Option B: Convert to PNG (recommended for user avatars, etc.)
    const pngPath = `/uploads/images/${crypto.randomUUID()}.png`;
    await convertSvgToRaster(file.path, pngPath);

    // Clean up temp file
    await fs.unlink(file.path);

    res.json({
      svg: svgPath,  // Serve with CSP
      png: pngPath   // Safe to serve normally
    });
  } catch (error) {
    await fs.unlink(req.file.path).catch(() => {});
    res.status(400).json({ error: error.message });
  }
});

// SVG serving route with CSP
app.get('/uploads/svg/:filename', serveSvgWithCSP, async (req, res) => {
  const filename = path.basename(req.params.filename);
  const filepath = path.join('/uploads/svg', filename);

  // Additional security: Validate file exists and is in allowed directory
  const resolvedPath = path.resolve(filepath);
  const uploadsDir = path.resolve('/uploads/svg');

  if (!resolvedPath.startsWith(uploadsDir)) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  res.sendFile(resolvedPath);
});
```

### Pattern 5: Advanced File Content Validation

```javascript
// Verify file content matches claimed type (magic bytes)
const validateFileContent = async (filepath, claimedMime) => {
  const FileType = await import('file-type');
  const buffer = await fs.readFile(filepath);

  // Check magic bytes
  const detectedType = await FileType.fileTypeFromBuffer(buffer);

  if (!detectedType) {
    throw new ValidationError('Unable to detect file type');
  }

  if (detectedType.mime !== claimedMime) {
    throw new ValidationError(
      `File content (${detectedType.mime}) does not match claimed type (${claimedMime})`
    );
  }

  // Additional checks for image files
  if (claimedMime.startsWith('image/')) {
    const sharp = require('sharp');

    try {
      const metadata = await sharp(filepath).metadata();

      // Validate dimensions
      if (metadata.width > 10000 || metadata.height > 10000) {
        throw new ValidationError('Image dimensions too large');
      }

      // Detect decompression bombs
      const pixelCount = metadata.width * metadata.height;
      if (pixelCount > 100000000) { // 100 megapixels
        throw new ValidationError('Image too large (possible decompression bomb)');
      }
    } catch (error) {
      throw new ValidationError('Invalid or corrupt image file');
    }
  }

  return true;
};
```

### File Upload Security Checklist

**Validation:**

- [ ] Validate file extension (allowlist, case-insensitive)
- [ ] Validate MIME type (server-side, not client `Content-Type`)
- [ ] Verify file content matches claimed type (magic bytes)
- [ ] Validate file size limits
- [ ] Check filename for path traversal attempts
- [ ] Detect CVE-2024-11404 bypass (spaces before extension)

**SVG-Specific:**

- [ ] Sanitize SVG with DOMPurify or convert to raster
- [ ] Remove script tags, foreignObject, event handlers
- [ ] Block data URIs and javascript: protocols
- [ ] Serve SVGs with CSP: script-src 'none'
- [ ] Validate SVG only contains safe elements/attributes

**Storage:**

- [ ] Generate random filenames (crypto.randomUUID())
- [ ] Store outside web root or serve from separate domain
- [ ] Use path.resolve() and verify paths stay in allowed directory
- [ ] Set restrictive file permissions

**Serving:**

- [ ] Set X-Content-Type-Options: nosniff
- [ ] Validate path before serving (prevent traversal)
- [ ] Add CSP headers for SVG/HTML files
- [ ] Consider malware scanning for untrusted uploads

---

## SQL Injection Prevention

### Pattern 1: Parameterized Queries

```javascript
// Bad: String concatenation (VULNERABLE)
const getUserBad = async (email) => {
  const query = `SELECT * FROM users WHERE email = '${email}'`;
  const [rows] = await db.execute(query);
  return rows[0];
};

// Attack: email = "' OR '1'='1"
// Result: SELECT * FROM users WHERE email = '' OR '1'='1'
// Returns all users!

// Good: Parameterized query
const getUserGood = async (email) => {
  const query = 'SELECT * FROM users WHERE email = ?';
  const [rows] = await db.execute(query, [email]);
  return rows[0];
};

// Good: Named parameters (PostgreSQL)
const getUserPg = async (email) => {
  const query = 'SELECT * FROM users WHERE email = $1';
  const result = await pool.query(query, [email]);
  return result.rows[0];
};

// Good: Multiple parameters
const searchUsers = async (name, role, active) => {
  const query = `
    SELECT * FROM users
    WHERE name LIKE ?
      AND role = ?
      AND active = ?
  `;
  const [rows] = await db.execute(query, [`%${name}%`, role, active]);
  return rows;
};
```

### Pattern 2: ORM Usage

```javascript
// Good: Sequelize ORM
const getUserSequelize = async (email) => {
  return await User.findOne({
    where: { email }
  });
};

const searchUsersSequelize = async (filters) => {
  return await User.findAll({
    where: {
      name: { [Op.like]: `%${filters.name}%` },
      role: filters.role,
      active: filters.active
    }
  });
};

// Good: Prisma ORM
const getUserPrisma = async (email) => {
  return await prisma.user.findUnique({
    where: { email }
  });
};

// Good: TypeORM
const getUserTypeORM = async (email) => {
  return await userRepository.findOne({
    where: { email }
  });
};
```

### Pattern 3: Escaping (Last Resort)

```javascript
// Only use if parameterized queries are not possible
const mysql = require('mysql2');

const escapeAndQuery = async (email) => {
  const escapedEmail = mysql.escape(email);
  const query = `SELECT * FROM users WHERE email = ${escapedEmail}`;
  const [rows] = await db.execute(query);
  return rows[0];
};

// Still vulnerable to second-order SQL injection!
// Always prefer parameterized queries.
```

---

## XSS Prevention

### Pattern 1: Output Encoding

```javascript
// Bad: Direct output (VULNERABLE)
app.get('/profile', (req, res) => {
  const html = `
    <h1>Welcome, ${req.user.name}</h1>
    <p>${req.user.bio}</p>
  `;
  res.send(html);
});

// Attack: name = "<script>alert('XSS')</script>"
// Result: Script executes in browser

// Good: HTML escaping
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

app.get('/profile', (req, res) => {
  const html = `
    <h1>Welcome, ${escapeHtml(req.user.name)}</h1>
    <p>${escapeHtml(req.user.bio)}</p>
  `;
  res.send(html);
});

// Good: Use templating engines with auto-escaping
app.set('view engine', 'ejs'); // EJS escapes by default

app.get('/profile', (req, res) => {
  res.render('profile', {
    name: req.user.name, // Auto-escaped
    bio: req.user.bio    // Auto-escaped
  });
});
```

### Pattern 2: HTML Sanitization

```javascript
// Good: Sanitize rich text input
const DOMPurify = require('isomorphic-dompurify');

const sanitizeHtml = (dirty) => {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'title'],
    ALLOWED_URI_REGEXP: /^https?:\/\//
  });
};

app.post('/api/posts', (req, res) => {
  const sanitizedContent = sanitizeHtml(req.body.content);

  const post = await Post.create({
    title: req.body.title,
    content: sanitizedContent
  });

  res.json(post);
});
```

### Pattern 3: Content Security Policy

```javascript
// Good: Strict CSP headers
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' 'nonce-" + req.nonce + "'; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: https:; " +
    "font-src 'self' data:; " +
    "connect-src 'self'; " +
    "frame-ancestors 'none'; " +
    "base-uri 'self'; " +
    "form-action 'self'"
  );

  next();
});

// Generate nonce for inline scripts
app.use((req, res, next) => {
  req.nonce = crypto.randomBytes(16).toString('base64');
  next();
});

// Use nonce in templates
// <script nonce="${nonce}">...</script>
```

---

## CSRF Prevention

### Pattern 1: Synchronizer Token Pattern

```javascript
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

// Setup CSRF protection
app.use(cookieParser());
const csrfProtection = csrf({ cookie: true });

// Render form with token
app.get('/transfer', csrfProtection, (req, res) => {
  res.render('transfer', {
    csrfToken: req.csrfToken()
  });
});

// Validate token on submission
app.post('/transfer', csrfProtection, (req, res) => {
  // Token automatically validated by middleware
  processTransfer(req.body);
  res.json({ success: true });
});

// Client-side: Include token in forms
// <input type="hidden" name="_csrf" value="{{csrfToken}}">

// Client-side: Include token in AJAX requests
// fetch('/transfer', {
//   method: 'POST',
//   headers: {
//     'CSRF-Token': csrfToken
//   },
//   body: JSON.stringify(data)
// });
```

### Pattern 2: Double-Submit Cookie

```javascript
// Generate CSRF token
const generateCsrfToken = () => {
  return crypto.randomBytes(32).toString('hex');
};

// Set CSRF cookie
app.use((req, res, next) => {
  if (!req.cookies.csrfToken) {
    const token = generateCsrfToken();

    res.cookie('csrfToken', token, {
      httpOnly: false, // Must be readable by JavaScript
      secure: true,
      sameSite: 'strict'
    });

    req.csrfToken = token;
  } else {
    req.csrfToken = req.cookies.csrfToken;
  }

  next();
});

// Validate CSRF token
const validateCsrfToken = (req, res, next) => {
  const tokenFromCookie = req.cookies.csrfToken;
  const tokenFromHeader = req.headers['x-csrf-token'];

  if (!tokenFromCookie || !tokenFromHeader || tokenFromCookie !== tokenFromHeader) {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }

  next();
};

// Apply to state-changing routes
app.post('/api/*', validateCsrfToken);
app.put('/api/*', validateCsrfToken);
app.delete('/api/*', validateCsrfToken);
```

### Pattern 3: SameSite Cookies

```javascript
// Good: SameSite attribute for session cookies
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    secure: true,
    httpOnly: true,
    sameSite: 'strict', // Prevents CSRF attacks
    maxAge: 30 * 60 * 1000
  }
}));

// Strict: Cookie only sent with same-site requests
// Lax: Cookie sent with top-level navigation (GET)
// None: Cookie sent with all requests (requires secure: true)
```

---

## NoSQL Injection Prevention

```javascript
// Bad: Direct object injection (VULNERABLE)
const getUserBad = async (email) => {
  return await User.findOne({ email: req.body.email });
};

// Attack: email = { $ne: null }
// Result: Returns first user (always true condition)

// Good: Validate data type
const getUserGood = async (email) => {
  if (typeof email !== 'string') {
    throw new ValidationError('Email must be a string');
  }

  return await User.findOne({ email });
};

// Good: Sanitize MongoDB operators
const sanitizeObject = (obj) => {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  const sanitized = {};

  for (const [key, value] of Object.entries(obj)) {
    // Remove keys starting with $
    if (key.startsWith('$')) {
      continue;
    }

    sanitized[key] = typeof value === 'object'
      ? sanitizeObject(value)
      : value;
  }

  return sanitized;
};

const getUserSanitized = async (filters) => {
  const sanitizedFilters = sanitizeObject(filters);
  return await User.findOne(sanitizedFilters);
};

// Good: Use schema validation
const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    validate: {
      validator: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
      message: 'Invalid email format'
    }
  }
});
```

---

## Command Injection Prevention

```javascript
// Bad: Unvalidated shell execution (VULNERABLE)
const { exec } = require('child_process');

const convertImage = (filename) => {
  exec(`convert ${filename} output.png`);
};

// Attack: filename = "input.jpg; rm -rf /"
// Result: Deletes all files!

// Good: Use libraries instead of shell
const sharp = require('sharp');

const convertImage = async (inputPath) => {
  // Validate input path
  const safePath = path.resolve('/uploads', path.basename(inputPath));

  await sharp(safePath)
    .resize(800, 600)
    .toFile('/output/converted.png');
};

// Good: If shell is necessary, use execFile with array
const { execFile } = require('child_process');

const pingHost = (hostname) => {
  // Strict validation
  const hostnameRegex = /^[a-zA-Z0-9.-]+$/;

  if (!hostnameRegex.test(hostname)) {
    throw new ValidationError('Invalid hostname');
  }

  // execFile doesn't invoke shell, uses array for args
  execFile('ping', ['-c', '4', hostname], (error, stdout) => {
    if (error) {
      throw error;
    }

    console.log(stdout);
  });
};
```

---

## Path Traversal Prevention

```javascript
// Bad: Unvalidated file access (VULNERABLE)
const getFileBad = (filename) => {
  const filepath = path.join('/uploads', filename);
  return fs.readFileSync(filepath);
};

// Attack: filename = "../../etc/passwd"
// Result: Reads system password file!

// Good: Validate and sanitize filename
const getFileGood = (filename) => {
  // Remove path separators and null bytes
  const cleanFilename = path.basename(filename).replace(/\0/g, '');

  if (cleanFilename !== filename) {
    throw new ValidationError('Invalid filename');
  }

  // Resolve to absolute path and verify it's in allowed directory
  const uploadsDir = path.resolve('/uploads');
  const filepath = path.resolve(uploadsDir, cleanFilename);

  if (!filepath.startsWith(uploadsDir)) {
    throw new ValidationError('Path traversal detected');
  }

  return fs.readFileSync(filepath);
};

// Good: Use allowlist for file access
const allowedFiles = new Set(['file1.txt', 'file2.pdf', 'image.jpg']);

const getFileAllowlist = (filename) => {
  if (!allowedFiles.has(filename)) {
    throw new ValidationError('File not found');
  }

  const filepath = path.join('/uploads', filename);
  return fs.readFileSync(filepath);
};
```

---

## LDAP Injection Prevention

```javascript
// Bad: Unescaped LDAP filter (VULNERABLE)
const searchUserBad = (username) => {
  const filter = `(uid=${username})`;
  return ldapClient.search('ou=users,dc=example,dc=com', { filter });
};

// Attack: username = "*)(uid=*"
// Result: Returns all users

// Good: Escape LDAP special characters
const escapeLdap = (str) => {
  return str.replace(/[\\*()]/g, '\\$&');
};

const searchUserGood = (username) => {
  const escapedUsername = escapeLdap(username);
  const filter = `(uid=${escapedUsername})`;
  return ldapClient.search('ou=users,dc=example,dc=com', { filter });
};
```

---

## Validation Best Practices

### Comprehensive Validation Function

```javascript
const validator = {
  // String validation
  string: (value, { minLength = 0, maxLength = Infinity, pattern = null } = {}) => {
    if (typeof value !== 'string') {
      throw new ValidationError('Must be a string');
    }

    if (value.length < minLength) {
      throw new ValidationError(`Minimum length is ${minLength}`);
    }

    if (value.length > maxLength) {
      throw new ValidationError(`Maximum length is ${maxLength}`);
    }

    if (pattern && !pattern.test(value)) {
      throw new ValidationError('Invalid format');
    }

    return value;
  },

  // Number validation
  number: (value, { min = -Infinity, max = Infinity, integer = false } = {}) => {
    const num = Number(value);

    if (isNaN(num)) {
      throw new ValidationError('Must be a number');
    }

    if (integer && !Number.isInteger(num)) {
      throw new ValidationError('Must be an integer');
    }

    if (num < min) {
      throw new ValidationError(`Minimum value is ${min}`);
    }

    if (num > max) {
      throw new ValidationError(`Maximum value is ${max}`);
    }

    return num;
  },

  // Array validation
  array: (value, { minLength = 0, maxLength = Infinity, itemValidator = null } = {}) => {
    if (!Array.isArray(value)) {
      throw new ValidationError('Must be an array');
    }

    if (value.length < minLength) {
      throw new ValidationError(`Minimum length is ${minLength}`);
    }

    if (value.length > maxLength) {
      throw new ValidationError(`Maximum length is ${maxLength}`);
    }

    if (itemValidator) {
      return value.map((item, index) => {
        try {
          return itemValidator(item);
        } catch (error) {
          throw new ValidationError(`Item ${index}: ${error.message}`);
        }
      });
    }

    return value;
  },

  // Enum validation
  enum: (value, allowedValues) => {
    if (!allowedValues.includes(value)) {
      throw new ValidationError(`Must be one of: ${allowedValues.join(', ')}`);
    }

    return value;
  }
};

// Usage
const validatePost = (data) => {
  return {
    title: validator.string(data.title, { minLength: 1, maxLength: 200 }),
    content: validator.string(data.content, { maxLength: 10000 }),
    tags: validator.array(data.tags, {
      maxLength: 5,
      itemValidator: (tag) => validator.string(tag, { maxLength: 20 })
    }),
    status: validator.enum(data.status, ['draft', 'published', 'archived'])
  };
};
```

---

## References

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
