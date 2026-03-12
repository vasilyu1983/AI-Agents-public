# Cryptography Standards & Best Practices

Comprehensive guide to implementing cryptography correctly in modern applications.

---

## Core Principles

**1. Never Roll Your Own Crypto**: Use established libraries and algorithms
**2. Use Strong Defaults**: AES-256-GCM, bcrypt with cost 12+, TLS 1.3
**3. Crypto Agility**: Design systems to upgrade algorithms without breaking changes
**4. Key Management**: Secure key generation, storage, rotation, and destruction
**5. Random Values**: Use cryptographically secure random number generators

---

## Password Hashing

### Pattern 1: bcrypt (Recommended)

```javascript
const bcrypt = require('bcrypt');

// Hash password
const hashPassword = async (password) => {
  const saltRounds = 12; // 2^12 iterations (adjust based on performance)

  const hash = await bcrypt.hash(password, saltRounds);
  return hash;
};

// Verify password
const verifyPassword = async (password, hash) => {
  const valid = await bcrypt.compare(password, hash);
  return valid;
};

// Example usage
const registerUser = async (email, password) => {
  const passwordHash = await hashPassword(password);

  const user = await User.create({
    email,
    passwordHash
  });

  return user;
};

const authenticateUser = async (email, password) => {
  const user = await User.findOne({ email });

  if (!user) {
    // Constant-time response to prevent timing attacks
    await bcrypt.compare(password, '$2b$12$constantTimeHashValue');
    throw new AuthenticationError('Invalid credentials');
  }

  const valid = await verifyPassword(password, user.passwordHash);

  if (!valid) {
    throw new AuthenticationError('Invalid credentials');
  }

  return user;
};
```

**Cost Factor Recommendations:**
- **Cost 10**: ~10 hashes/second (minimum acceptable)
- **Cost 12**: ~3 hashes/second (recommended)
- **Cost 14**: ~1 hash/second (high security)

**When to rehash:**
```javascript
const needsRehash = (hash) => {
  // bcrypt hashes start with $2b$12$ (cost 12)
  const currentCost = 12;
  const hashCost = parseInt(hash.split('$')[2]);

  return hashCost < currentCost;
};

const loginAndRehash = async (email, password) => {
  const user = await authenticateUser(email, password);

  // Rehash if using old cost factor
  if (needsRehash(user.passwordHash)) {
    const newHash = await hashPassword(password);
    await User.findByIdAndUpdate(user.id, { passwordHash: newHash });
  }

  return user;
};
```

### Pattern 2: Argon2 (Best for New Projects)

```javascript
const argon2 = require('argon2');

// Hash password
const hashPassword = async (password) => {
  const hash = await argon2.hash(password, {
    type: argon2.argon2id, // Hybrid mode (recommended)
    memoryCost: 2 ** 16,   // 64 MB
    timeCost: 3,           // 3 iterations
    parallelism: 1         // 1 thread
  });

  return hash;
};

// Verify password
const verifyPassword = async (password, hash) => {
  try {
    return await argon2.verify(hash, password);
  } catch (error) {
    return false;
  }
};
```

**Argon2 Type Selection:**
- **argon2id**: Hybrid (recommended) - resistant to both side-channel and GPU attacks
- **argon2i**: Data-independent - best for password hashing
- **argon2d**: Data-dependent - best for cryptocurrency

### Pattern 3: scrypt

```javascript
const crypto = require('crypto');

// Hash password
const hashPassword = (password) => {
  return new Promise((resolve, reject) => {
    const salt = crypto.randomBytes(16);

    crypto.scrypt(password, salt, 64, {
      N: 16384,    // CPU/memory cost
      r: 8,        // Block size
      p: 1,        // Parallelization
      maxmem: 32 * 1024 * 1024 // 32 MB
    }, (err, derivedKey) => {
      if (err) reject(err);

      resolve(salt.toString('hex') + ':' + derivedKey.toString('hex'));
    });
  });
};

// Verify password
const verifyPassword = (password, hash) => {
  return new Promise((resolve, reject) => {
    const [salt, key] = hash.split(':');

    crypto.scrypt(password, Buffer.from(salt, 'hex'), 64, {
      N: 16384,
      r: 8,
      p: 1,
      maxmem: 32 * 1024 * 1024
    }, (err, derivedKey) => {
      if (err) reject(err);

      resolve(derivedKey.toString('hex') === key);
    });
  });
};
```

**Never Use:**
- [FAIL] MD5
- [FAIL] SHA-1
- [FAIL] Plain SHA-256 (without salting and iterations)
- [FAIL] Custom password hashing schemes

---

## Symmetric Encryption

### Pattern 1: AES-256-GCM (Recommended)

```javascript
const crypto = require('crypto');

// Encrypt data
const encrypt = (plaintext, key) => {
  // Key must be 32 bytes for AES-256
  if (key.length !== 32) {
    throw new Error('Key must be 32 bytes');
  }

  // Generate random IV (12 bytes for GCM)
  const iv = crypto.randomBytes(12);

  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

  let ciphertext = cipher.update(plaintext, 'utf8', 'hex');
  ciphertext += cipher.final('hex');

  // Get authentication tag
  const authTag = cipher.getAuthTag();

  return {
    ciphertext,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex')
  };
};

// Decrypt data
const decrypt = (ciphertext, key, iv, authTag) => {
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    key,
    Buffer.from(iv, 'hex')
  );

  // Set authentication tag
  decipher.setAuthTag(Buffer.from(authTag, 'hex'));

  let plaintext = decipher.update(ciphertext, 'hex', 'utf8');
  plaintext += decipher.final('utf8');

  return plaintext;
};

// Example: Encrypt user data
const encryptUserData = (data, masterKey) => {
  const plaintext = JSON.stringify(data);
  const encrypted = encrypt(plaintext, masterKey);

  // Store in database
  return {
    data: encrypted.ciphertext,
    iv: encrypted.iv,
    authTag: encrypted.authTag
  };
};

const decryptUserData = (encrypted, masterKey) => {
  const plaintext = decrypt(
    encrypted.data,
    masterKey,
    encrypted.iv,
    encrypted.authTag
  );

  return JSON.parse(plaintext);
};
```

**Key Generation:**
```javascript
// Generate random 256-bit key
const generateKey = () => {
  return crypto.randomBytes(32);
};

// Derive key from password (for user-encrypted data)
const deriveKey = async (password, salt) => {
  return new Promise((resolve, reject) => {
    crypto.scrypt(password, salt, 32, {
      N: 16384,
      r: 8,
      p: 1
    }, (err, derivedKey) => {
      if (err) reject(err);
      resolve(derivedKey);
    });
  });
};
```

### Pattern 2: AES-256-CBC (Legacy Support)

```javascript
// Use GCM instead if possible (CBC doesn't provide authentication)

const encryptCBC = (plaintext, key) => {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);

  let ciphertext = cipher.update(plaintext, 'utf8', 'hex');
  ciphertext += cipher.final('hex');

  return {
    ciphertext,
    iv: iv.toString('hex')
  };
};

const decryptCBC = (ciphertext, key, iv) => {
  const decipher = crypto.createDecipheriv(
    'aes-256-cbc',
    key,
    Buffer.from(iv, 'hex')
  );

  let plaintext = decipher.update(ciphertext, 'hex', 'utf8');
  plaintext += decipher.final('utf8');

  return plaintext;
};
```

**Never Use:**
- [FAIL] DES / 3DES
- [FAIL] RC4
- [FAIL] AES-ECB mode
- [FAIL] Hardcoded encryption keys
- [FAIL] Same IV for multiple encryptions

---

## Asymmetric Encryption

### Pattern 1: RSA

```javascript
const crypto = require('crypto');

// Generate RSA key pair
const generateKeyPair = () => {
  return new Promise((resolve, reject) => {
    crypto.generateKeyPair('rsa', {
      modulusLength: 4096, // 4096 bits (2048 minimum)
      publicKeyEncoding: {
        type: 'spki',
        format: 'pem'
      },
      privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem',
        cipher: 'aes-256-cbc',
        passphrase: process.env.KEY_PASSPHRASE
      }
    }, (err, publicKey, privateKey) => {
      if (err) reject(err);
      resolve({ publicKey, privateKey });
    });
  });
};

// Encrypt with public key
const encryptRSA = (plaintext, publicKey) => {
  const buffer = Buffer.from(plaintext, 'utf8');

  const encrypted = crypto.publicEncrypt(
    {
      key: publicKey,
      padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
      oaepHash: 'sha256'
    },
    buffer
  );

  return encrypted.toString('base64');
};

// Decrypt with private key
const decryptRSA = (ciphertext, privateKey, passphrase) => {
  const buffer = Buffer.from(ciphertext, 'base64');

  const decrypted = crypto.privateDecrypt(
    {
      key: privateKey,
      passphrase,
      padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
      oaepHash: 'sha256'
    },
    buffer
  );

  return decrypted.toString('utf8');
};
```

**RSA Best Practices:**
- Minimum 2048-bit keys (4096 recommended for long-term security)
- Use OAEP padding (never use PKCS1 v1.5)
- Protect private keys with strong passphrases
- Rotate keys periodically

### Pattern 2: Elliptic Curve (ECDH)

```javascript
// Generate ECDH key pair
const generateECDHKeyPair = () => {
  return crypto.generateKeyPairSync('ec', {
    namedCurve: 'secp256k1', // Or 'prime256v1', 'secp384r1'
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem'
    }
  });
};

// Derive shared secret
const deriveSharedSecret = (privateKey, publicKey) => {
  const ecdh = crypto.createECDH('secp256k1');
  ecdh.setPrivateKey(privateKey, 'pem');

  const otherPublicKey = crypto.createPublicKey(publicKey);
  const sharedSecret = ecdh.computeSecret(otherPublicKey);

  return sharedSecret;
};
```

---

## Digital Signatures

### Pattern 1: RSA-PSS

```javascript
// Sign data
const signData = (data, privateKey, passphrase) => {
  const sign = crypto.createSign('SHA256');
  sign.update(data);
  sign.end();

  const signature = sign.sign({
    key: privateKey,
    passphrase,
    padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
    saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST
  });

  return signature.toString('base64');
};

// Verify signature
const verifySignature = (data, signature, publicKey) => {
  const verify = crypto.createVerify('SHA256');
  verify.update(data);
  verify.end();

  return verify.verify(
    {
      key: publicKey,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST
    },
    Buffer.from(signature, 'base64')
  );
};

// Example: Sign API request
const signRequest = (requestBody, privateKey) => {
  const timestamp = Date.now();
  const payload = JSON.stringify({ ...requestBody, timestamp });

  const signature = signData(payload, privateKey, process.env.KEY_PASSPHRASE);

  return {
    payload,
    signature,
    timestamp
  };
};
```

### Pattern 2: ECDSA

```javascript
// Sign with ECDSA
const signECDSA = (data, privateKey) => {
  const sign = crypto.createSign('SHA256');
  sign.update(data);
  sign.end();

  const signature = sign.sign(privateKey);
  return signature.toString('base64');
};

// Verify ECDSA signature
const verifyECDSA = (data, signature, publicKey) => {
  const verify = crypto.createVerify('SHA256');
  verify.update(data);
  verify.end();

  return verify.verify(publicKey, Buffer.from(signature, 'base64'));
};
```

---

## Hashing

### Pattern 1: SHA-256 (Data Integrity)

```javascript
// Hash data
const hashData = (data) => {
  const hash = crypto.createHash('sha256');
  hash.update(data);
  return hash.digest('hex');
};

// HMAC (keyed hash for message authentication)
const hmac = (data, key) => {
  const hmac = crypto.createHmac('sha256', key);
  hmac.update(data);
  return hmac.digest('hex');
};

// Example: File integrity check
const verifyFileIntegrity = async (filepath, expectedHash) => {
  const fileBuffer = await fs.readFile(filepath);
  const actualHash = hashData(fileBuffer);

  return actualHash === expectedHash;
};

// Example: API request signing
const signAPIRequest = (requestData, secretKey) => {
  const payload = JSON.stringify(requestData);
  const signature = hmac(payload, secretKey);

  return {
    payload,
    signature
  };
};

const verifyAPIRequest = (payload, signature, secretKey) => {
  const expectedSignature = hmac(payload, secretKey);
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
};
```

**Hash Functions:**
- **SHA-256**: Standard for data integrity
- **SHA-384/512**: Higher security margin
- **SHA-3**: Latest standard (Keccak)

**Never Use:**
- [FAIL] MD5
- [FAIL] SHA-1
- [FAIL] CRC32 (for security purposes)

---

## Random Number Generation

### Pattern 1: Cryptographically Secure Random

```javascript
// Generate random bytes
const generateRandomBytes = (length) => {
  return crypto.randomBytes(length);
};

// Generate random token
const generateToken = () => {
  return crypto.randomBytes(32).toString('hex');
};

// Generate random UUID
const generateUUID = () => {
  return crypto.randomUUID();
};

// Generate random integer in range
const randomInt = (min, max) => {
  const range = max - min;
  const bytesNeeded = Math.ceil(Math.log2(range) / 8);
  const maxValue = Math.pow(256, bytesNeeded);
  const randomValue = crypto.randomBytes(bytesNeeded).readUIntBE(0, bytesNeeded);

  // Avoid modulo bias
  if (randomValue >= maxValue - (maxValue % range)) {
    return randomInt(min, max);
  }

  return min + (randomValue % range);
};
```

**Never Use:**
- [FAIL] Math.random() for security purposes
- [FAIL] Timestamp-based "random" values
- [FAIL] Sequential IDs for security tokens

---

## TLS/SSL Configuration

### Pattern 1: Node.js HTTPS Server

```javascript
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('/path/to/private-key.pem'),
  cert: fs.readFileSync('/path/to/certificate.pem'),
  ca: fs.readFileSync('/path/to/ca-cert.pem'),

  // TLS 1.3 only
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3',

  // Cipher suites (TLS 1.3 ciphers)
  ciphers: [
    'TLS_AES_256_GCM_SHA384',
    'TLS_AES_128_GCM_SHA256',
    'TLS_CHACHA20_POLY1305_SHA256'
  ].join(':'),

  // Prefer server cipher order
  honorCipherOrder: true,

  // Disable session resumption (optional, for max security)
  sessionTimeout: 0
};

const server = https.createServer(options, app);
server.listen(443);
```

### Pattern 2: Express Security Headers

```javascript
const helmet = require('helmet');

app.use(helmet({
  // Strict Transport Security
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },

  // Certificate Transparency
  expectCt: {
    maxAge: 86400,
    enforce: true
  }
}));
```

**TLS Best Practices:**
- Use TLS 1.3 only (disable 1.2, 1.1, 1.0)
- Use strong cipher suites
- Enable HSTS with preload
- Implement certificate pinning for mobile apps
- Use certificate transparency
- Rotate certificates before expiration

---

## Key Management

### Pattern 1: Environment Variables

```javascript
// Load from .env file
require('dotenv').config();

const SECRET_KEY = Buffer.from(process.env.SECRET_KEY, 'hex');
const JWT_SECRET = process.env.JWT_SECRET;

// Never hardcode keys
// BAD: const SECRET_KEY = 'hardcoded-key-12345';
```

### Pattern 2: Key Management Service

```javascript
const AWS = require('aws-sdk');
const kms = new AWS.KMS();

// Encrypt data with KMS
const encryptWithKMS = async (plaintext) => {
  const params = {
    KeyId: process.env.KMS_KEY_ID,
    Plaintext: plaintext
  };

  const result = await kms.encrypt(params).promise();
  return result.CiphertextBlob.toString('base64');
};

// Decrypt data with KMS
const decryptWithKMS = async (ciphertext) => {
  const params = {
    CiphertextBlob: Buffer.from(ciphertext, 'base64')
  };

  const result = await kms.decrypt(params).promise();
  return result.Plaintext.toString('utf8');
};

// Generate data encryption key
const generateDataKey = async () => {
  const params = {
    KeyId: process.env.KMS_KEY_ID,
    KeySpec: 'AES_256'
  };

  const result = await kms.generateDataKey(params).promise();

  return {
    plaintextKey: result.Plaintext,
    encryptedKey: result.CiphertextBlob.toString('base64')
  };
};
```

### Pattern 3: HashiCorp Vault

```javascript
const vault = require('node-vault')({
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN
});

// Store secret
const storeSecret = async (path, data) => {
  await vault.write(path, { data });
};

// Retrieve secret
const retrieveSecret = async (path) => {
  const result = await vault.read(path);
  return result.data.data;
};

// Example usage
const getEncryptionKey = async () => {
  const secret = await retrieveSecret('secret/data/encryption-key');
  return Buffer.from(secret.key, 'hex');
};
```

**Key Management Best Practices:**
- Never commit keys to version control
- Use key management services (AWS KMS, Azure Key Vault, HashiCorp Vault)
- Rotate keys periodically
- Implement key versioning
- Secure key backup and recovery
- Separate encryption keys by environment
- Use envelope encryption for large data

---

## References

- [NIST Cryptographic Standards](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
