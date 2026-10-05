# Authorization Implementation Template

Copy-paste ready implementation for RBAC, ABAC, and permission-based authorization.

---

## Role-Based Access Control (RBAC)

### Roles and Permissions Definition

```javascript
// config/permissions.js

// Define permissions
const PERMISSIONS = {
  // User permissions
  USERS_READ: 'users:read',
  USERS_WRITE: 'users:write',
  USERS_DELETE: 'users:delete',

  // Post permissions
  POSTS_READ: 'posts:read',
  POSTS_WRITE: 'posts:write',
  POSTS_DELETE: 'posts:delete',
  POSTS_PUBLISH: 'posts:publish',

  // Settings permissions
  SETTINGS_READ: 'settings:read',
  SETTINGS_WRITE: 'settings:write',

  // Billing permissions
  BILLING_READ: 'billing:read',
  BILLING_WRITE: 'billing:write'
};

// Define roles
const ROLES = {
  ADMIN: 'admin',
  MODERATOR: 'moderator',
  EDITOR: 'editor',
  USER: 'user',
  GUEST: 'guest'
};

// Role-permission mapping
const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.USERS_READ,
    PERMISSIONS.USERS_WRITE,
    PERMISSIONS.USERS_DELETE,
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE,
    PERMISSIONS.POSTS_DELETE,
    PERMISSIONS.POSTS_PUBLISH,
    PERMISSIONS.SETTINGS_READ,
    PERMISSIONS.SETTINGS_WRITE,
    PERMISSIONS.BILLING_READ,
    PERMISSIONS.BILLING_WRITE
  ],
  [ROLES.MODERATOR]: [
    PERMISSIONS.USERS_READ,
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE,
    PERMISSIONS.POSTS_DELETE
  ],
  [ROLES.EDITOR]: [
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE,
    PERMISSIONS.POSTS_PUBLISH
  ],
  [ROLES.USER]: [
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE
  ],
  [ROLES.GUEST]: [
    PERMISSIONS.POSTS_READ
  ]
};

// Helper functions
const getRolePermissions = (role) => {
  return ROLE_PERMISSIONS[role] || [];
};

const hasPermission = (role, permission) => {
  const permissions = getRolePermissions(role);
  return permissions.includes(permission);
};

const hasAnyPermission = (role, requiredPermissions) => {
  const permissions = getRolePermissions(role);
  return requiredPermissions.some(p => permissions.includes(p));
};

const hasAllPermissions = (role, requiredPermissions) => {
  const permissions = getRolePermissions(role);
  return requiredPermissions.every(p => permissions.includes(p));
};

module.exports = {
  PERMISSIONS,
  ROLES,
  ROLE_PERMISSIONS,
  getRolePermissions,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions
};
```

### Authorization Middleware

```javascript
// middleware/authorize.js
const { hasPermission, hasAllPermissions } = require('../config/permissions');

// Require specific role(s)
const requireRole = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required: allowedRoles,
        current: req.user.role
      });
    }

    next();
  };
};

// Require specific permission(s)
const requirePermission = (...requiredPermissions) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const userPermissions = getRolePermissions(req.user.role);

    const hasRequiredPermissions = requiredPermissions.every(
      permission => userPermissions.includes(permission)
    );

    if (!hasRequiredPermissions) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required: requiredPermissions,
        current: userPermissions
      });
    }

    next();
  };
};

// Require any of the specified permissions
const requireAnyPermission = (...permissions) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const userPermissions = getRolePermissions(req.user.role);

    const hasAnyPermission = permissions.some(
      permission => userPermissions.includes(permission)
    );

    if (!hasAnyPermission) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required: permissions,
        current: userPermissions
      });
    }

    next();
  };
};

// Resource ownership check
const requireOwnership = (getResourceOwnerId) => {
  return async (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    // Admins bypass ownership check
    if (req.user.role === 'admin') {
      return next();
    }

    try {
      const ownerId = await getResourceOwnerId(req);

      if (ownerId !== req.user.userId) {
        return res.status(403).json({ error: 'Not authorized to access this resource' });
      }

      next();
    } catch (error) {
      res.status(500).json({ error: 'Authorization check failed' });
    }
  };
};

module.exports = {
  requireRole,
  requirePermission,
  requireAnyPermission,
  requireOwnership
};
```

### Usage Examples

```javascript
// routes/users.js
const express = require('express');
const authenticate = require('../middleware/authenticate');
const { requireRole, requirePermission } = require('../middleware/authorize');
const { PERMISSIONS, ROLES } = require('../config/permissions');

const router = express.Router();

// List users (requires users:read permission)
router.get('/',
  authenticate,
  requirePermission(PERMISSIONS.USERS_READ),
  async (req, res) => {
    const users = await User.find();
    res.json(users);
  }
);

// Create user (requires users:write permission)
router.post('/',
  authenticate,
  requirePermission(PERMISSIONS.USERS_WRITE),
  async (req, res) => {
    const user = await User.create(req.body);
    res.json(user);
  }
);

// Delete user (admin only)
router.delete('/:id',
  authenticate,
  requireRole(ROLES.ADMIN),
  async (req, res) => {
    await User.findByIdAndDelete(req.params.id);
    res.json({ message: 'User deleted' });
  }
);

module.exports = router;
```

```javascript
// routes/posts.js
const express = require('express');
const authenticate = require('../middleware/authenticate');
const { requirePermission, requireOwnership } = require('../middleware/authorize');
const { PERMISSIONS } = require('../config/permissions');

const router = express.Router();

// Public: Read posts
router.get('/', async (req, res) => {
  const posts = await Post.find({ published: true });
  res.json(posts);
});

// Authenticated: Create post
router.post('/',
  authenticate,
  requirePermission(PERMISSIONS.POSTS_WRITE),
  async (req, res) => {
    const post = await Post.create({
      ...req.body,
      authorId: req.user.userId
    });
    res.json(post);
  }
);

// Owner or moderator: Update post
router.put('/:id',
  authenticate,
  requireAnyPermission(PERMISSIONS.POSTS_WRITE, PERMISSIONS.POSTS_DELETE),
  requireOwnership(async (req) => {
    const post = await Post.findById(req.params.id);
    return post.authorId;
  }),
  async (req, res) => {
    const post = await Post.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(post);
  }
);

// Moderator or admin: Delete post
router.delete('/:id',
  authenticate,
  requirePermission(PERMISSIONS.POSTS_DELETE),
  async (req, res) => {
    await Post.findByIdAndDelete(req.params.id);
    res.json({ message: 'Post deleted' });
  }
);

module.exports = router;
```

---

## Attribute-Based Access Control (ABAC)

### Policy Engine

```javascript
// utils/policyEngine.js

class PolicyEngine {
  constructor() {
    this.policies = [];
  }

  addPolicy(policy) {
    this.policies.push(policy);
  }

  async evaluate(context) {
    for (const policy of this.policies) {
      const result = await policy.evaluate(context);

      // Explicit allow
      if (result === 'allow') {
        return true;
      }

      // Explicit deny (takes precedence)
      if (result === 'deny') {
        return false;
      }

      // Continue to next policy
    }

    // Deny by default
    return false;
  }
}

// Base policy class
class Policy {
  constructor(name) {
    this.name = name;
  }

  async evaluate(context) {
    throw new Error('evaluate() must be implemented');
  }
}

module.exports = { PolicyEngine, Policy };
```

### Example Policies

```javascript
// policies/adminPolicy.js
const { Policy } = require('../utils/policyEngine');

class AdminPolicy extends Policy {
  constructor() {
    super('AdminPolicy');
  }

  async evaluate(context) {
    // Admins can do anything
    if (context.user.role === 'admin') {
      return 'allow';
    }

    return 'continue';
  }
}

module.exports = AdminPolicy;
```

```javascript
// policies/ownershipPolicy.js
const { Policy } = require('../utils/policyEngine');

class OwnershipPolicy extends Policy {
  constructor() {
    super('OwnershipPolicy');
  }

  async evaluate(context) {
    const { user, resource, action } = context;

    // Owners can edit/delete their own resources
    if (['edit', 'delete'].includes(action)) {
      if (resource.ownerId === user.userId) {
        return 'allow';
      }

      return 'deny';
    }

    return 'continue';
  }
}

module.exports = OwnershipPolicy;
```

```javascript
// policies/timeBasedPolicy.js
const { Policy } = require('../utils/policyEngine');

class TimeBasedPolicy extends Policy {
  constructor() {
    super('TimeBasedPolicy');
  }

  async evaluate(context) {
    const { user, action } = context;

    // Sensitive operations only during business hours (9 AM - 5 PM)
    if (action === 'delete' && user.role !== 'admin') {
      const hour = new Date().getHours();

      if (hour < 9 || hour > 17) {
        return 'deny';
      }
    }

    return 'continue';
  }
}

module.exports = TimeBasedPolicy;
```

```javascript
// policies/departmentPolicy.js
const { Policy } = require('../utils/policyEngine');

class DepartmentPolicy extends Policy {
  constructor() {
    super('DepartmentPolicy');
  }

  async evaluate(context) {
    const { user, resource, action } = context;

    // Users can only access resources from their department
    if (action === 'read') {
      if (resource.department === user.department) {
        return 'allow';
      }

      return 'deny';
    }

    return 'continue';
  }
}

module.exports = DepartmentPolicy;
```

### Initialize Policy Engine

```javascript
// config/authorization.js
const { PolicyEngine } = require('../utils/policyEngine');
const AdminPolicy = require('../policies/adminPolicy');
const OwnershipPolicy = require('../policies/ownershipPolicy');
const TimeBasedPolicy = require('../policies/timeBasedPolicy');
const DepartmentPolicy = require('../policies/departmentPolicy');

const policyEngine = new PolicyEngine();

// Add policies (order matters - earlier policies take precedence)
policyEngine.addPolicy(new AdminPolicy());
policyEngine.addPolicy(new OwnershipPolicy());
policyEngine.addPolicy(new TimeBasedPolicy());
policyEngine.addPolicy(new DepartmentPolicy());

module.exports = policyEngine;
```

### ABAC Middleware

```javascript
// middleware/abac.js
const policyEngine = require('../config/authorization');

const authorize = (action, resourceType, getResource) => {
  return async (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
      // Load resource
      const resource = await getResource(req);

      if (!resource) {
        return res.status(404).json({ error: 'Resource not found' });
      }

      // Build context
      const context = {
        user: {
          userId: req.user.userId,
          email: req.user.email,
          role: req.user.role,
          department: req.user.department
        },
        resource: {
          id: resource.id,
          type: resourceType,
          ownerId: resource.ownerId,
          department: resource.department,
          classification: resource.classification
        },
        action,
        environment: {
          time: new Date(),
          ipAddress: req.ip,
          userAgent: req.get('user-agent')
        }
      };

      // Evaluate policy
      const allowed = await policyEngine.evaluate(context);

      if (!allowed) {
        return res.status(403).json({ error: 'Access denied' });
      }

      // Attach resource to request for use in handler
      req.resource = resource;
      next();
    } catch (error) {
      res.status(500).json({ error: 'Authorization check failed' });
    }
  };
};

module.exports = authorize;
```

### ABAC Usage Example

```javascript
// routes/documents.js
const express = require('express');
const authenticate = require('../middleware/authenticate');
const authorize = require('../middleware/abac');
const Document = require('../models/Document');

const router = express.Router();

// Read document
router.get('/:id',
  authenticate,
  authorize('read', 'document', async (req) => {
    return await Document.findById(req.params.id);
  }),
  (req, res) => {
    res.json(req.resource);
  }
);

// Update document
router.put('/:id',
  authenticate,
  authorize('edit', 'document', async (req) => {
    return await Document.findById(req.params.id);
  }),
  async (req, res) => {
    const updated = await Document.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );
    res.json(updated);
  }
);

// Delete document
router.delete('/:id',
  authenticate,
  authorize('delete', 'document', async (req) => {
    return await Document.findById(req.params.id);
  }),
  async (req, res) => {
    await Document.findByIdAndDelete(req.params.id);
    res.json({ message: 'Document deleted' });
  }
);

module.exports = router;
```

---

## Relationship-Based Access Control (ReBAC)

### Permission Model

```javascript
// models/ResourcePermission.js
const mongoose = require('mongoose');

const resourcePermissionSchema = new mongoose.Schema({
  resourceType: {
    type: String,
    required: true,
    enum: ['document', 'project', 'folder']
  },
  resourceId: {
    type: String,
    required: true
  },
  userId: {
    type: String,
    required: true
  },
  relationship: {
    type: String,
    required: true,
    enum: ['owner', 'editor', 'viewer']
  },
  grantedBy: String,
  grantedAt: {
    type: Date,
    default: Date.now
  }
});

// Compound index for fast lookups
resourcePermissionSchema.index({ resourceType: 1, resourceId: 1, userId: 1 });

module.exports = mongoose.model('ResourcePermission', resourcePermissionSchema);
```

### Permission Utilities

```javascript
// utils/permissions.js
const ResourcePermission = require('../models/ResourcePermission');

const RELATIONSHIPS = {
  OWNER: 'owner',
  EDITOR: 'editor',
  VIEWER: 'viewer'
};

// Check if user has relationship to resource
const hasRelationship = async (userId, resourceType, resourceId, relationship) => {
  const permission = await ResourcePermission.findOne({
    userId,
    resourceType,
    resourceId,
    relationship
  });

  return !!permission;
};

// Check if user has any of the specified relationships
const hasAnyRelationship = async (userId, resourceType, resourceId, relationships) => {
  const permission = await ResourcePermission.findOne({
    userId,
    resourceType,
    resourceId,
    relationship: { $in: relationships }
  });

  return !!permission;
};

// Grant access to resource
const grantAccess = async (userId, resourceType, resourceId, relationship, grantedBy) => {
  // Check if permission already exists
  const existing = await ResourcePermission.findOne({
    userId,
    resourceType,
    resourceId
  });

  if (existing) {
    // Update existing permission
    existing.relationship = relationship;
    existing.grantedBy = grantedBy;
    await existing.save();
    return existing;
  }

  // Create new permission
  return await ResourcePermission.create({
    userId,
    resourceType,
    resourceId,
    relationship,
    grantedBy
  });
};

// Revoke access to resource
const revokeAccess = async (userId, resourceType, resourceId) => {
  await ResourcePermission.deleteOne({
    userId,
    resourceType,
    resourceId
  });
};

// Get all users with access to resource
const getResourceCollaborators = async (resourceType, resourceId) => {
  return await ResourcePermission.find({
    resourceType,
    resourceId
  }).populate('userId');
};

// Get all resources user has access to
const getUserResources = async (userId, resourceType) => {
  return await ResourcePermission.find({
    userId,
    resourceType
  });
};

module.exports = {
  RELATIONSHIPS,
  hasRelationship,
  hasAnyRelationship,
  grantAccess,
  revokeAccess,
  getResourceCollaborators,
  getUserResources
};
```

### ReBAC Middleware

```javascript
// middleware/rebac.js
const { hasAnyRelationship, RELATIONSHIPS } = require('../utils/permissions');

const requireRelationship = (resourceType, ...allowedRelationships) => {
  return async (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const resourceId = req.params.id;

    try {
      const hasAccess = await hasAnyRelationship(
        req.user.userId,
        resourceType,
        resourceId,
        allowedRelationships
      );

      if (!hasAccess) {
        return res.status(403).json({ error: 'Access denied' });
      }

      next();
    } catch (error) {
      res.status(500).json({ error: 'Authorization check failed' });
    }
  };
};

module.exports = { requireRelationship };
```

### ReBAC Usage Example

```javascript
// routes/projects.js
const express = require('express');
const authenticate = require('../middleware/authenticate');
const { requireRelationship } = require('../middleware/rebac');
const { RELATIONSHIPS, grantAccess, revokeAccess } = require('../utils/permissions');

const router = express.Router();

// View project (owner, editor, or viewer)
router.get('/:id',
  authenticate,
  requireRelationship('project',
    RELATIONSHIPS.OWNER,
    RELATIONSHIPS.EDITOR,
    RELATIONSHIPS.VIEWER
  ),
  async (req, res) => {
    const project = await Project.findById(req.params.id);
    res.json(project);
  }
);

// Edit project (owner or editor)
router.put('/:id',
  authenticate,
  requireRelationship('project',
    RELATIONSHIPS.OWNER,
    RELATIONSHIPS.EDITOR
  ),
  async (req, res) => {
    const project = await Project.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );
    res.json(project);
  }
);

// Delete project (owner only)
router.delete('/:id',
  authenticate,
  requireRelationship('project', RELATIONSHIPS.OWNER),
  async (req, res) => {
    await Project.findByIdAndDelete(req.params.id);
    res.json({ message: 'Project deleted' });
  }
);

// Share project (owner only)
router.post('/:id/share',
  authenticate,
  requireRelationship('project', RELATIONSHIPS.OWNER),
  async (req, res) => {
    const { userId, relationship } = req.body;

    await grantAccess(
      userId,
      'project',
      req.params.id,
      relationship,
      req.user.userId
    );

    res.json({ message: 'Access granted' });
  }
);

// Revoke access (owner only)
router.delete('/:id/share/:userId',
  authenticate,
  requireRelationship('project', RELATIONSHIPS.OWNER),
  async (req, res) => {
    await revokeAccess(req.params.userId, 'project', req.params.id);
    res.json({ message: 'Access revoked' });
  }
);

module.exports = router;
```

---

## Testing

```javascript
// tests/authorization.test.js
const request = require('supertest');
const app = require('../app');
const User = require('../models/User');
const Post = require('../models/Post');

describe('Authorization', () => {
  let adminToken, userToken, moderatorToken;
  let adminUser, regularUser, moderatorUser;

  beforeEach(async () => {
    // Create users
    adminUser = await User.create({
      email: 'admin@example.com',
      passwordHash: await hashPassword('password'),
      role: 'admin'
    });

    regularUser = await User.create({
      email: 'user@example.com',
      passwordHash: await hashPassword('password'),
      role: 'user'
    });

    moderatorUser = await User.create({
      email: 'moderator@example.com',
      passwordHash: await hashPassword('password'),
      role: 'moderator'
    });

    // Generate tokens
    adminToken = generateAccessToken(adminUser);
    userToken = generateAccessToken(regularUser);
    moderatorToken = generateAccessToken(moderatorUser);
  });

  test('Admin can delete any post', async () => {
    const post = await Post.create({
      title: 'Test Post',
      authorId: regularUser.id
    });

    const res = await request(app)
      .delete(`/api/posts/${post.id}`)
      .set('Authorization', `Bearer ${adminToken}`);

    expect(res.status).toBe(200);
  });

  test('Regular user cannot delete others posts', async () => {
    const post = await Post.create({
      title: 'Test Post',
      authorId: adminUser.id
    });

    const res = await request(app)
      .delete(`/api/posts/${post.id}`)
      .set('Authorization', `Bearer ${userToken}`);

    expect(res.status).toBe(403);
  });

  test('Moderator can delete any post', async () => {
    const post = await Post.create({
      title: 'Test Post',
      authorId: regularUser.id
    });

    const res = await request(app)
      .delete(`/api/posts/${post.id}`)
      .set('Authorization', `Bearer ${moderatorToken}`);

    expect(res.status).toBe(200);
  });
});
```

---

## Security Checklist

- [ ] Deny by default authorization
- [ ] Check authorization on every request
- [ ] Don't cache authorization decisions
- [ ] Log authorization failures
- [ ] Test vertical and horizontal privilege escalation
- [ ] Use indirect object references (UUIDs)
- [ ] Implement proper error messages (don't leak info)
- [ ] Consider using ABAC for complex scenarios
- [ ] Document permission model clearly
- [ ] Regular audit of permissions
