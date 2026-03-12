# Zero Trust Architecture — Implementation Guide

Modern security architecture based on "never trust, always verify" principles for cloud-native and distributed systems (Jan 2026).

---

## Overview

Zero Trust Architecture (ZTA) eliminates implicit trust based on network location, requiring continuous verification of all users, devices, and services regardless of their position relative to network perimeters.

**Key Principle**: Never trust, always verify.

---

## 2026 Updates

### NSA Zero Trust Implementation Guidelines (ZIGs) — January 2026

The NSA released the first products in the Zero Trust Implementation Guidelines (ZIGs) series on January 14, 2026:

1. **Primer**: Strategy and principles for ZT implementation
2. **Discovery Phase**: Guidance for beginning ZT journey

Key recommendations:

- Start with identity pillar (strongest security impact)
- Implement continuous diagnostics and monitoring (CDM)
- Deploy micro-segmentation incrementally
- Integrate AI/ML for behavioral analytics and SOAR

### Pentagon Zero Trust Strategy 2.0 (Expected March 2026)

DoD zero trust requirements for FY2027:

- **91 capability outcomes** for target ZT on unclassified/secret networks
- **61 additional outcomes** for advanced ZT by FY2032
- Expansion to OT, IoT, defense critical infrastructure, weapon systems

### AI Integration with Zero Trust

2026 organizations implementing Zero Trust with AI report:

- **76% fewer successful breaches**
- **Incident response time**: Days → Minutes
- **Behavioral analytics**: Real-time anomaly detection
- **SOAR integration**: Automated response workflows

---

## NIST Zero Trust Principles (SP 800-207)

1. **All data sources and services are resources**
2. **Communication is secured regardless of network location**
3. **Access to resources is granted per-session**
4. **Access decisions are dynamic and policy-based**
5. **Enterprise monitors and measures security posture**
6. **Authentication and authorization are strict before access**
7. **Collect as much information as possible for security posture**

---

## CISA Zero Trust Maturity Model

### Five Pillars

1. **Identity**: User and device authentication
2. **Devices**: Endpoint security and compliance
3. **Networks**: Encrypted, segmented communication
4. **Applications**: Secure app access and APIs
5. **Data**: Data classification and protection

### Maturity Levels

- **Traditional**: Perimeter-based security
- **Initial**: Beginning zero trust implementation
- **Advanced**: Comprehensive zero trust controls
- **Optimal**: Fully automated, dynamic zero trust

---

## Architecture Components

### 1. Identity and Access Management (IAM)

**Single Sign-On (SSO)**

```javascript
// OAuth 2.0 + OpenID Connect flow
const express = require('express');
const passport = require('passport');
const OIDCStrategy = require('passport-azure-ad').OIDCStrategy;

passport.use(new OIDCStrategy({
  identityMetadata: 'https://login.microsoftonline.com/tenant/.well-known/openid-configuration',
  clientID: process.env.CLIENT_ID,
  responseType: 'code id_token',
  responseMode: 'form_post',
  redirectUrl: 'https://app.example.com/auth/callback',
  allowHttpForRedirectUrl: false,
  clientSecret: process.env.CLIENT_SECRET,
  validateIssuer: true,
  issuer: 'https://sts.windows.net/tenant-id/',
  passReqToCallback: false,
  scope: ['profile', 'email', 'openid']
}, (iss, sub, profile, accessToken, refreshToken, done) => {
  // Verify user and create session
  return done(null, profile);
}));

app.get('/auth/login',
  passport.authenticate('azuread-openidconnect', {
    failureRedirect: '/login'
  })
);
```

**Multi-Factor Authentication (MFA)**

```javascript
// Verify MFA token
const speakeasy = require('speakeasy');

const verifyMFA = (token, secret) => {
  return speakeasy.totp.verify({
    secret: secret,
    encoding: 'base32',
    token: token,
    window: 1  // Allow 1 time step before/after for clock drift
  });
};

// Middleware requiring MFA
const requireMFA = async (req, res, next) => {
  if (!req.user.mfaEnabled) {
    return res.status(403).json({
      error: 'MFA required but not enabled'
    });
  }

  const token = req.headers['x-mfa-token'];
  if (!token || !verifyMFA(token, req.user.mfaSecret)) {
    return res.status(401).json({ error: 'Invalid MFA token' });
  }

  next();
};
```

---

### 2. Device Security

**Device Posture Assessment**

```javascript
// Device trust verification middleware
const assessDeviceTrust = async (req, res, next) => {
  const deviceId = req.headers['x-device-id'];
  const device = await DeviceRegistry.findById(deviceId);

  if (!device) {
    return res.status(403).json({
      error: 'Unknown device'
    });
  }

  // Check device compliance
  const checks = {
    osUpdated: device.osVersion >= MIN_OS_VERSION,
    antivirus: device.antivirusEnabled && device.antivirusUpdated,
    encrypted: device.diskEncrypted,
    jailbroken: !device.jailbroken,
    lastSeen: Date.now() - device.lastSeenAt < 24 * 60 * 60 * 1000
  };

  const trustScore = Object.values(checks).filter(Boolean).length / Object.keys(checks).length;

  if (trustScore < 0.8) {
    return res.status(403).json({
      error: 'Device does not meet security requirements',
      violations: Object.entries(checks)
        .filter(([key, value]) => !value)
        .map(([key]) => key)
    });
  }

  req.deviceTrustScore = trustScore;
  next();
};

app.use('/api', assessDeviceTrust);
```

---

### 3. Network Segmentation

**Micro-Segmentation with Service Mesh (Istio)**

```yaml
# Authorization policy - deny by default
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  {}  # Empty spec = deny all

---
# Allow specific service-to-service communication
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-to-backend
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

**Mutual TLS (mTLS)**

```yaml
# Istio PeerAuthentication - enforce mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # Require mTLS for all traffic
```

**Application-Level mTLS**

```javascript
// Node.js HTTPS server with client certificate verification
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('server-key.pem'),
  cert: fs.readFileSync('server-cert.pem'),
  ca: fs.readFileSync('ca-cert.pem'),
  requestCert: true,
  rejectUnauthorized: true
};

https.createServer(options, (req, res) => {
  const cert = req.socket.getPeerCertificate();

  if (!req.client.authorized) {
    return res.writeHead(401).end('Unauthorized');
  }

  // Verify certificate subject
  if (cert.subject.CN !== 'authorized-client') {
    return res.writeHead(403).end('Forbidden');
  }

  res.writeHead(200);
  res.end('Authenticated via mTLS');
}).listen(8443);
```

---

### 4. Policy-Based Access Control

**Open Policy Agent (OPA) Integration**

```javascript
// OPA policy enforcement middleware
const axios = require('axios');

const enforcePolicy = (resource, action) => {
  return async (req, res, next) => {
    const input = {
      user: {
        id: req.user.id,
        roles: req.user.roles,
        groups: req.user.groups
      },
      resource: resource,
      action: action,
      context: {
        time: new Date().toISOString(),
        ip: req.ip,
        deviceTrustScore: req.deviceTrustScore
      }
    };

    try {
      const response = await axios.post('http://opa:8181/v1/data/authz/allow', {
        input
      });

      if (!response.data.result) {
        return res.status(403).json({
          error: 'Access denied by policy'
        });
      }

      next();
    } catch (error) {
      logger.error('OPA evaluation failed', error);
      return res.status(500).json({
        error: 'Policy evaluation failed'
      });
    }
  };
};

// Usage
app.delete('/api/users/:id',
  authenticate,
  enforcePolicy('user', 'delete'),
  deleteUser
);
```

**OPA Policy (Rego)**

```rego
# authz.rego
package authz

import future.keywords.if

default allow = false

# Allow if user is admin
allow if {
  input.user.roles[_] == "admin"
}

# Allow user delete if:
# 1. User is manager
# 2. Request is during business hours
# 3. Device trust score > 0.9
allow if {
  input.resource == "user"
  input.action == "delete"
  input.user.roles[_] == "manager"
  is_business_hours
  input.context.deviceTrustScore > 0.9
}

is_business_hours if {
  time.weekday(input.context.time) >= 1
  time.weekday(input.context.time) <= 5
  hour := time.clock(input.context.time)[0]
  hour >= 9
  hour < 17
}
```

---

### 5. Workload Identity

**SPIFFE/SPIRE Implementation**

```yaml
# Kubernetes workload identity
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-service
  namespace: production

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      serviceAccountName: backend-service
      containers:
      - name: backend
        image: backend:v1
        env:
        - name: SPIFFE_ENDPOINT_SOCKET
          value: unix:///run/spire/sockets/agent.sock
        volumeMounts:
        - name: spire-agent-socket
          mountPath: /run/spire/sockets
          readOnly: true
      volumes:
      - name: spire-agent-socket
        hostPath:
          path: /run/spire/sockets
          type: Directory
```

**Retrieve Workload Identity**

```javascript
// Get SVID (SPIFFE Verifiable Identity Document)
const { SpiffeWorkloadApi } = require('@spiffe/node-spiffe');

const getWorkloadIdentity = async () => {
  const client = new SpiffeWorkloadApi();
  const svid = await client.fetchX509Svid();

  return {
    spiffeId: svid.spiffeId.toString(),
    certificate: svid.certificate,
    privateKey: svid.privateKey
  };
};

// Use SVID for mTLS
const identity = await getWorkloadIdentity();
const tlsOptions = {
  cert: identity.certificate,
  key: identity.privateKey
};
```

---

### 6. Just-In-Time (JIT) Access

**Temporary Privilege Elevation**

```javascript
// JIT access grant system
const grantTemporaryAccess = async (userId, resource, duration) => {
  const grant = {
    userId,
    resource,
    grantedAt: Date.now(),
    expiresAt: Date.now() + duration,
    status: 'active'
  };

  await AccessGrants.create(grant);

  // Schedule automatic revocation
  setTimeout(async () => {
    await AccessGrants.updateOne(
      { _id: grant._id },
      { status: 'expired' }
    );
    await auditLog('jit_access_expired', grant);
  }, duration);

  return grant;
};

// Verify temporary access
const checkJITAccess = async (req, res, next) => {
  const grant = await AccessGrants.findOne({
    userId: req.user.id,
    resource: req.path,
    status: 'active',
    expiresAt: { $gt: Date.now() }
  });

  if (!grant) {
    return res.status(403).json({
      error: 'No active temporary access grant'
    });
  }

  next();
};

// Request temporary admin access
app.post('/api/access/request', authenticate, async (req, res) => {
  const { resource, reason, duration } = req.body;

  // Require manager approval
  const approval = await requestApproval({
    requestedBy: req.user.id,
    resource,
    reason,
    duration
  });

  if (!approval.approved) {
    return res.status(403).json({
      error: 'Access request denied',
      reason: approval.reason
    });
  }

  const grant = await grantTemporaryAccess(
    req.user.id,
    resource,
    duration
  );

  res.json({ grant });
});
```

---

### 7. Continuous Monitoring

**Security Event Logging**

```javascript
// Comprehensive security event logging
const logSecurityEvent = async (event) => {
  const securityEvent = {
    timestamp: new Date(),
    eventType: event.type,
    severity: event.severity,
    user: {
      id: event.userId,
      ip: event.ip,
      deviceId: event.deviceId
    },
    action: event.action,
    resource: event.resource,
    outcome: event.outcome,
    context: {
      userAgent: event.userAgent,
      geoLocation: event.geoLocation,
      deviceTrustScore: event.deviceTrustScore
    }
  };

  await SecurityEvents.create(securityEvent);

  // Alert on suspicious activity
  if (event.severity === 'high' || event.outcome === 'denied') {
    await alertSecurityTeam(securityEvent);
  }
};

// Middleware to log all security-relevant events
app.use((req, res, next) => {
  res.on('finish', () => {
    logSecurityEvent({
      type: 'api_access',
      severity: res.statusCode >= 400 ? 'high' : 'low',
      userId: req.user?.id,
      ip: req.ip,
      deviceId: req.headers['x-device-id'],
      action: req.method,
      resource: req.path,
      outcome: res.statusCode < 400 ? 'allowed' : 'denied',
      userAgent: req.headers['user-agent']
    });
  });
  next();
});
```

---

## Implementation Roadmap

### Phase 1: Foundation (0-3 months)
- [ ] Implement SSO with MFA
- [ ] Deploy device management platform
- [ ] Enable basic network segmentation
- [ ] Establish security logging

### Phase 2: Advanced Controls (3-6 months)
- [ ] Deploy service mesh with mTLS
- [ ] Implement policy-based access control (OPA)
- [ ] Deploy workload identity (SPIFFE/SPIRE)
- [ ] Enable continuous device posture assessment

### Phase 3: Optimization (6-12 months)
- [ ] Implement JIT access
- [ ] Deploy behavioral analytics
- [ ] Automate policy enforcement
- [ ] Full zero trust coverage across all systems

---

## Best Practices

**Identity**
- Enforce MFA on all accounts
- Use short-lived credentials (< 1 hour)
- Implement adaptive authentication based on risk
- Regular access reviews and least privilege enforcement

**Network**
- Default deny all traffic
- Encrypt all communication (TLS 1.3+, mTLS)
- Micro-segmentation at service level
- Monitor and log all network flows

**Access Control**
- Dynamic, context-aware authorization
- Time-boxed access grants
- Require re-authentication for sensitive operations
- Audit all access decisions

**Monitoring**
- Log all authentication and authorization events
- Correlate events across identity, device, and network
- Automated anomaly detection
- Real-time alerting on policy violations

---

## Tools and Technologies

| Component | Tools |
|-----------|-------|
| **Identity Provider** | Okta, Auth0, Azure AD, Keycloak |
| **Device Management** | Jamf, Intune, Workspace ONE |
| **Service Mesh** | Istio, Linkerd, Consul Connect |
| **Policy Engine** | Open Policy Agent (OPA), Styra |
| **Workload Identity** | SPIFFE/SPIRE, Vault |
| **SIEM** | Splunk, Elastic Security, Chronicle |

---

## References

- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model)
- [Google BeyondCorp Papers](https://cloud.google.com/beyondcorp)
- [SPIFFE Specification](https://spiffe.io/docs/)
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/)
- [Istio Security](https://istio.io/latest/docs/concepts/security/)
