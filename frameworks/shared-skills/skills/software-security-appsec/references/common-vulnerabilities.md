# Common Vulnerabilities Catalog

Comprehensive catalog of common security vulnerabilities with prevention strategies.

---

## Path Traversal (Directory Traversal)

**Attack**: Access files outside intended directory using `../` sequences.

### Vulnerable Code

```javascript
// Bad: No path validation
app.get('/files/:filename', (req, res) => {
  const filepath = path.join('/uploads', req.params.filename);
  res.sendFile(filepath);
});

// Attack: GET /files/../../etc/passwd
// Result: Reads system password file
```

### Secure Code

```javascript
// Good: Validate and sanitize path
const getFile = (filename) => {
  // Remove path separators and null bytes
  const clean = path.basename(filename).replace(/\0/g, '');

  if (clean !== filename || clean.length === 0) {
    throw new ValidationError('Invalid filename');
  }

  // Resolve to absolute path and verify it's in allowed directory
  const uploadsDir = path.resolve('/uploads');
  const filepath = path.resolve(uploadsDir, clean);

  if (!filepath.startsWith(uploadsDir)) {
    throw new SecurityError('Path traversal detected');
  }

  // Verify file exists and is a file (not directory)
  const stats = fs.statSync(filepath);
  if (!stats.isFile()) {
    throw new ValidationError('Not a file');
  }

  return filepath;
};

app.get('/files/:filename', (req, res) => {
  try {
    const filepath = getFile(req.params.filename);
    res.sendFile(filepath);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

---

## Insecure Deserialization

**Attack**: Execute arbitrary code by manipulating serialized objects.

### Vulnerable Code

```javascript
// Bad: Unsafe deserialization
app.post('/api/load-config', (req, res) => {
  const config = eval(req.body.config); // BAD: Extremely dangerous
  res.json(config);
});

// Bad: Using pickle in Python (if attacker controls input)
// config = pickle.loads(user_input)
```

### Secure Code

```javascript
// Good: Use JSON.parse with validation
const loadConfig = (configString) => {
  try {
    const config = JSON.parse(configString);

    // Validate schema
    const schema = Joi.object({
      theme: Joi.string().valid('light', 'dark'),
      language: Joi.string().valid('en', 'es', 'fr'),
      notifications: Joi.boolean()
    });

    const { error, value } = schema.validate(config);

    if (error) {
      throw new ValidationError('Invalid configuration');
    }

    return value;
  } catch (error) {
    throw new ValidationError('Failed to parse configuration');
  }
};

app.post('/api/load-config', (req, res) => {
  const config = loadConfig(req.body.config);
  res.json(config);
});
```

---

## XML External Entity (XXE) Injection

**Attack**: Reference external entities in XML to read files or perform SSRF.

### Vulnerable Code

```javascript
// Bad: Parse XML without disabling external entities
const xml2js = require('xml2js');

app.post('/api/upload-xml', async (req, res) => {
  const parser = new xml2js.Parser(); // VULNERABLE: Default settings allow XXE
  const result = await parser.parseStringPromise(req.body.xml);
  res.json(result);
});

// Attack XML:
// <?xml version="1.0"?>
// <!DOCTYPE foo [
//   <!ENTITY xxe SYSTEM "file:///etc/passwd">
// ]>
// <data>&xxe;</data>
```

### Secure Code

```javascript
// Good: Disable external entities
const xml2js = require('xml2js');

app.post('/api/upload-xml', async (req, res) => {
  const parser = new xml2js.Parser({
    explicitRoot: true,
    explicitArray: false,
    // Disable entity expansion
    xmlns: false,
    // Limit nesting depth
    normalize: false,
    trim: true
  });

  try {
    const result = await parser.parseStringPromise(req.body.xml);
    res.json(result);
  } catch (error) {
    res.status(400).json({ error: 'Invalid XML' });
  }
});

// Better: Use JSON instead of XML when possible
```

---

## Insecure Direct Object References (IDOR)

**Attack**: Access resources by manipulating IDs without authorization checks.

### Vulnerable Code

```javascript
// Bad: No authorization check
app.get('/api/invoices/:id', authenticate, async (req, res) => {
  const invoice = await Invoice.findById(req.params.id);
  res.json(invoice);
});

// Attack: User changes invoice ID in URL to view others' invoices
// GET /api/invoices/12345 (own invoice)
// GET /api/invoices/12346 (someone else's invoice) - VULNERABLE
```

### Secure Code

```javascript
// Good: Verify ownership
app.get('/api/invoices/:id', authenticate, async (req, res) => {
  const invoice = await Invoice.findById(req.params.id);

  if (!invoice) {
    return res.status(404).json({ error: 'Invoice not found' });
  }

  // Verify user owns this invoice
  if (invoice.userId !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  res.json(invoice);
});

// Better: Use UUIDs instead of sequential IDs
const invoice = await Invoice.create({
  id: crypto.randomUUID(), // Random, non-guessable ID
  userId: req.user.id,
  amount: req.body.amount
});
```

---

## Mass Assignment

**Attack**: Modify unintended fields by including them in request body.

### Vulnerable Code

```javascript
// Bad: Accept all fields from request
app.post('/api/users', async (req, res) => {
  const user = await User.create(req.body); // DANGEROUS: Accepts any field
  res.json(user);
});

// Attack:
// POST /api/users
// {
//   "email": "user@example.com",
//   "password": "password123",
//   "role": "admin"  // ATTACK: Attacker sets their role to admin
// }
```

### Secure Code

```javascript
// Good: Explicitly allow only specific fields
app.post('/api/users', async (req, res) => {
  const allowedFields = ['email', 'password', 'name'];

  const userData = {};
  for (const field of allowedFields) {
    if (req.body[field] !== undefined) {
      userData[field] = req.body[field];
    }
  }

  // Set secure defaults
  userData.role = 'user';
  userData.emailVerified = false;

  const user = await User.create(userData);
  res.json(user);
});

// Alternative: Use schema validation
const userSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(12).required(),
  name: Joi.string().max(100).required()
  // role is not in schema, so it can't be set
});

app.post('/api/users', async (req, res) => {
  const { error, value } = userSchema.validate(req.body);

  if (error) {
    return res.status(400).json({ error: error.details });
  }

  const user = await User.create({
    ...value,
    role: 'user',
    emailVerified: false
  });

  res.json(user);
});
```

---

## Server-Side Template Injection (SSTI)

**Attack**: Execute code by injecting template syntax.

### Vulnerable Code

```javascript
// Bad: User input directly in template
const ejs = require('ejs');

app.get('/greet', (req, res) => {
  const name = req.query.name;
  const template = `<h1>Hello <%= ${name} %></h1>`; // DANGEROUS: User input in template
  const html = ejs.render(template);
  res.send(html);
});

// Attack: /greet?name=process.exit()
```

### Secure Code

```javascript
// Good: Pass data as variables, don't construct template from user input
app.get('/greet', (req, res) => {
  const name = req.query.name;

  res.render('greet', {
    name: name // EJS auto-escapes by default
  });
});

// greet.ejs:
// <h1>Hello <%= name %></h1>
```

---

## Race Conditions

**Attack**: Exploit timing window between check and use (TOCTOU).

### Vulnerable Code

```javascript
// Bad: Race condition in money transfer
const transferMoney = async (fromUserId, toUserId, amount) => {
  const fromUser = await User.findById(fromUserId);

  // Check balance
  if (fromUser.balance < amount) {
    throw new Error('Insufficient funds');
  }

  // [WARNING] Race condition window here!
  // Multiple requests can pass the check before balance is updated

  // Update balances
  await User.findByIdAndUpdate(fromUserId, {
    $inc: { balance: -amount }
  });

  await User.findByIdAndUpdate(toUserId, {
    $inc: { balance: amount }
  });
};
```

### Secure Code

```javascript
// Good: Use atomic operations or transactions
const transferMoney = async (fromUserId, toUserId, amount) => {
  const session = await mongoose.startSession();

  try {
    await session.withTransaction(async () => {
      // Atomic decrement with check
      const result = await User.findOneAndUpdate(
        {
          _id: fromUserId,
          balance: { $gte: amount } // Check in same operation
        },
        {
          $inc: { balance: -amount }
        },
        { session, new: true }
      );

      if (!result) {
        throw new Error('Insufficient funds');
      }

      // Atomic increment
      await User.findByIdAndUpdate(
        toUserId,
        { $inc: { balance: amount } },
        { session }
      );
    });
  } finally {
    session.endSession();
  }
};

// Alternative: Use database-level locks
const transferMoneyWithLock = async (fromUserId, toUserId, amount) => {
  // Acquire lock
  const lock = await acquireLock(`transfer:${fromUserId}`);

  try {
    const fromUser = await User.findById(fromUserId);

    if (fromUser.balance < amount) {
      throw new Error('Insufficient funds');
    }

    await User.findByIdAndUpdate(fromUserId, {
      $inc: { balance: -amount }
    });

    await User.findByIdAndUpdate(toUserId, {
      $inc: { balance: amount }
    });
  } finally {
    await lock.release();
  }
};
```

---

## Open Redirect

**Attack**: Redirect users to malicious sites via URL parameter.

### Vulnerable Code

```javascript
// Bad: Unvalidated redirect
app.get('/redirect', (req, res) => {
  const url = req.query.url;
  res.redirect(url); // VULNERABLE: Can redirect to any site
});

// Attack: /redirect?url=https://malicious-site.com
```

### Secure Code

```javascript
// Good: Validate redirect URL
const isValidRedirect = (url) => {
  try {
    const parsed = new URL(url);

    // Only allow same origin
    const currentOrigin = `${req.protocol}://${req.get('host')}`;

    if (parsed.origin !== currentOrigin) {
      return false;
    }

    return true;
  } catch (error) {
    return false;
  }
};

app.get('/redirect', (req, res) => {
  const url = req.query.url;

  if (!isValidRedirect(url)) {
    return res.status(400).json({ error: 'Invalid redirect URL' });
  }

  res.redirect(url);
});

// Better: Use path-only redirects
const allowedPaths = ['/dashboard', '/profile', '/settings'];

app.get('/redirect', (req, res) => {
  const path = req.query.path;

  if (!allowedPaths.includes(path)) {
    return res.status(400).json({ error: 'Invalid redirect path' });
  }

  res.redirect(path);
});
```

---

## HTTP Response Splitting

**Attack**: Inject CRLF characters to inject headers or create XSS.

### Vulnerable Code

```javascript
// Bad: Unsanitized header values
app.get('/set-language', (req, res) => {
  const lang = req.query.lang;
  res.setHeader('Content-Language', lang); // VULNERABLE: Can inject headers
  res.send('Language set');
});

// Attack: /set-language?lang=en%0D%0ASet-Cookie:%20admin=true
// Injects: Content-Language: en\r\nSet-Cookie: admin=true
```

### Secure Code

```javascript
// Good: Validate and sanitize header values
const sanitizeHeaderValue = (value) => {
  // Remove CRLF characters
  return value.replace(/[\r\n]/g, '');
};

app.get('/set-language', (req, res) => {
  const lang = req.query.lang;

  // Validate against allowlist
  const allowedLanguages = ['en', 'es', 'fr', 'de'];

  if (!allowedLanguages.includes(lang)) {
    return res.status(400).json({ error: 'Invalid language' });
  }

  res.setHeader('Content-Language', lang);
  res.send('Language set');
});
```

---

## Clickjacking

**Attack**: Trick users into clicking on hidden elements via iframe.

### Vulnerable Code

```html
<!-- No protection against framing -->
<!DOCTYPE html>
<html>
<body>
  <h1>Transfer Money</h1>
  <form action="/transfer" method="POST">
    <button type="submit">Confirm Transfer</button>
  </form>
</body>
</html>
```

### Secure Code

```javascript
// Good: X-Frame-Options header
app.use((req, res, next) => {
  res.setHeader('X-Frame-Options', 'DENY');
  // Or: 'SAMEORIGIN' to allow framing by same origin
  next();
});

// Better: Content-Security-Policy frame-ancestors
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy', "frame-ancestors 'none'");
  next();
});

// Using Helmet
const helmet = require('helmet');

app.use(helmet({
  frameguard: { action: 'deny' }
}));
```

---

## Insufficient Logging

**Attack**: Perform malicious actions without detection.

### Vulnerable Code

```javascript
// Bad: No logging
app.post('/api/transfer', authenticate, async (req, res) => {
  await transferMoney(req.user.id, req.body.recipientId, req.body.amount);
  res.json({ success: true });
});
```

### Secure Code

```javascript
// Good: Comprehensive security logging
const logger = require('winston');

const securityLogger = logger.createLogger({
  level: 'info',
  format: logger.format.combine(
    logger.format.timestamp(),
    logger.format.json()
  ),
  transports: [
    new logger.transports.File({ filename: 'security.log' }),
    new logger.transports.Console()
  ]
});

app.post('/api/transfer', authenticate, async (req, res) => {
  const { recipientId, amount } = req.body;

  // Log before action
  securityLogger.info('Transfer initiated', {
    userId: req.user.id,
    recipientId,
    amount,
    ip: req.ip,
    userAgent: req.get('user-agent'),
    timestamp: new Date().toISOString()
  });

  try {
    await transferMoney(req.user.id, recipientId, amount);

    // Log success
    securityLogger.info('Transfer completed', {
      userId: req.user.id,
      recipientId,
      amount
    });

    res.json({ success: true });
  } catch (error) {
    // Log failure
    securityLogger.warn('Transfer failed', {
      userId: req.user.id,
      recipientId,
      amount,
      error: error.message
    });

    res.status(400).json({ error: error.message });
  }
});

// Log authentication failures
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await authenticateUser(email, password);

    securityLogger.info('Login successful', {
      userId: user.id,
      email,
      ip: req.ip
    });

    res.json({ token: generateToken(user) });
  } catch (error) {
    securityLogger.warn('Login failed', {
      email,
      ip: req.ip,
      reason: 'invalid_credentials'
    });

    res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

---

## Sensitive Data Exposure

**Attack**: Access sensitive data through logs, errors, or insecure storage.

### Vulnerable Code

```javascript
// Bad: Logging sensitive data
logger.info('User registered', {
  email: user.email,
  password: user.password, // BAD: Never log passwords
  ssn: user.ssn, // BAD: Never log PII
  creditCard: user.creditCard // BAD: Never log payment info
});

// Bad: Returning sensitive data in API
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user); // BAD: Returns password hash, tokens, etc.
});
```

### Secure Code

```javascript
// Good: Sanitize logs
const sanitizeForLogging = (data) => {
  const sanitized = { ...data };

  const sensitiveFields = ['password', 'passwordHash', 'ssn', 'creditCard', 'token'];

  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  }

  return sanitized;
};

logger.info('User registered', sanitizeForLogging({
  email: user.email,
  password: user.password
}));

// Good: Return only necessary fields
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);

  res.json({
    id: user.id,
    email: user.email,
    name: user.name,
    createdAt: user.createdAt
    // Exclude: passwordHash, tokens, etc.
  });
});

// Better: Use serializers
class UserSerializer {
  static serialize(user) {
    return {
      id: user.id,
      email: user.email,
      name: user.name,
      createdAt: user.createdAt
    };
  }
}

app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(UserSerializer.serialize(user));
});
```

---

## Unvalidated Redirects and Forwards

**Attack**: Use application as proxy to bypass security controls.

### Vulnerable Code

```javascript
// Bad: Forward requests without validation
app.get('/proxy', async (req, res) => {
  const url = req.query.url;
  const response = await fetch(url); // VULNERABLE: SSRF vulnerability
  const data = await response.text();
  res.send(data);
});

// Attack: /proxy?url=http://localhost:6379/
// Can access internal services
```

### Secure Code

```javascript
// Good: Validate destination
const allowedDomains = ['api.example.com', 'cdn.example.com'];

const isAllowedUrl = (urlString) => {
  try {
    const url = new URL(urlString);

    // Check protocol
    if (!['http:', 'https:'].includes(url.protocol)) {
      return false;
    }

    // Check domain allowlist
    if (!allowedDomains.includes(url.hostname)) {
      return false;
    }

    return true;
  } catch (error) {
    return false;
  }
};

app.get('/proxy', async (req, res) => {
  const url = req.query.url;

  if (!isAllowedUrl(url)) {
    return res.status(400).json({ error: 'Invalid URL' });
  }

  const response = await fetch(url, {
    redirect: 'manual', // Prevent redirect-based bypass
    timeout: 5000
  });

  const data = await response.text();
  res.send(data);
});
```

---

## References

- [CWE Top 25](https://cwe.mitre.org/top25/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
