# Component Discovery Patterns

This resource provides language-specific and framework-specific patterns for discovering documentable components in codebases.

---

## Contents

- Overview
- .NET/C# Codebase
- Node.js/TypeScript Codebase
- Python Codebase
- Go Codebase
- Java/Spring Codebase
- React/Frontend Codebase
- Discovery Commands
- Cross-Reference Discovery
- Documentation Coverage Commands
- Multi-Language Projects
- Best Practices
- Related Resources

## Overview

Discovery patterns help identify all components that should be documented across different technology stacks. Use these patterns with your search tool (grep, ripgrep, IDE search) to find undocumented components.

---

## .NET/C# Codebase

### API Layer

```bash
# Find all controllers
**/*Controller.cs
**/Controllers/**/*.cs

# Find all API models
**/*Request.cs
**/*Response.cs
**/*Dto.cs
**/Models/Api/**/*.cs
```

### Service Layer

```bash
# Find all services
**/*Service.cs
**/Services/**/*.cs

# Find all handlers (CQRS)
**/*Handler.cs
**/*CommandHandler.cs
**/*QueryHandler.cs
**/Commands/**/*.cs
**/Queries/**/*.cs
```

### Data Layer

```bash
# Find all DbContexts
**/*DbContext.cs
**/*Context.cs

# Find all entities
**/*Entity.cs
**/Entities/**/*.cs
**/Models/Data/**/*.cs

# Find all migrations
**/Migrations/**/*.cs
```

### Messaging Layer

```bash
# Find all Kafka/message handlers
**/*MessageHandler.cs
**/*Consumer.cs
**/*Producer.cs
**/*EventHandler.cs

# Find all message models
**/Models/Kafka/**/*.cs
**/Models/Messages/**/*.cs
**/Events/**/*.cs
```

### Infrastructure Layer

```bash
# Find all background services
**/*HostedService.cs
**/*BackgroundService.cs
**/*Job.cs
**/Jobs/**/*.cs

# Find all configuration options
**/*Options.cs
**/*Settings.cs
**/*Configuration.cs
**/Configuration/**/*.cs
```

---

## Node.js/TypeScript Codebase

### API Layer

```bash
# Find all routes/controllers
**/routes/**/*.ts
**/routes/**/*.js
**/controllers/**/*.ts
**/controllers/**/*.js

# Find all API validators
**/validators/**/*.ts
**/schemas/**/*.ts
```

### Service Layer

```bash
# Find all services
**/services/**/*.ts
**/services/**/*.js

# Find all use cases
**/use-cases/**/*.ts
**/usecases/**/*.ts
```

### Data Layer

```bash
# Find all models
**/models/**/*.ts
**/models/**/*.js
**/entities/**/*.ts

# Find all repositories
**/repositories/**/*.ts
**/repositories/**/*.js
```

### Middleware

```bash
# Find all middleware
**/middleware/**/*.ts
**/middleware/**/*.js
**/middlewares/**/*.ts
```

### Event Handlers

```bash
# Find all event handlers
**/events/**/*.ts
**/handlers/**/*.ts
**/subscribers/**/*.ts
**/listeners/**/*.ts
```

### Configuration

```bash
# Find all config files
**/config/**/*.ts
**/config/**/*.js
**/*.config.ts
**/*.config.js
```

---

## Python Codebase

### API Layer

```bash
# Find all views/endpoints
**/views.py
**/routes.py
**/api/**/*.py
**/endpoints/**/*.py

# Find all serializers
**/serializers.py
**/schemas.py
```

### Service Layer

```bash
# Find all services
**/services/**/*.py
**/use_cases/**/*.py
```

### Data Layer

```bash
# Find all models
**/models.py
**/models/**/*.py

# Find all repositories
**/repositories/**/*.py
**/db/**/*.py
```

### Background Tasks

```bash
# Find all tasks/jobs
**/tasks.py
**/celery/**/*.py
**/workers/**/*.py
```

### Configuration

```bash
# Find all settings
**/settings.py
**/config.py
**/config/**/*.py
```

---

## Go Codebase

### API Layer

```bash
# Find all handlers
**/handlers/**/*.go
**/api/**/*.go

# Find all routes
**/routes/**/*.go
**/router/**/*.go
```

### Service Layer

```bash
# Find all services
**/services/**/*.go
**/service/**/*.go
```

### Data Layer

```bash
# Find all models
**/models/**/*.go
**/entities/**/*.go

# Find all repositories
**/repository/**/*.go
**/repositories/**/*.go
```

### Configuration

```bash
# Find all config
**/config/**/*.go
```

---

## Java/Spring Codebase

### API Layer

```bash
# Find all controllers
**/*Controller.java
**/controllers/**/*.java

# Find all REST endpoints
@RestController
@RequestMapping
```

### Service Layer

```bash
# Find all services
**/*Service.java
**/services/**/*.java

# Find all components
@Service
@Component
```

### Data Layer

```bash
# Find all entities
**/*Entity.java
**/entities/**/*.java
**/models/**/*.java

# Find all repositories
**/*Repository.java
**/repositories/**/*.java
```

### Configuration

```bash
# Find all configuration
**/*Configuration.java
**/*Config.java
**/config/**/*.java
```

---

## React/Frontend Codebase

### Components

```bash
# Find all components
**/components/**/*.tsx
**/components/**/*.jsx

# Find all pages
**/pages/**/*.tsx
**/app/**/*.tsx (Next.js)
```

### State Management

```bash
# Find all stores
**/store/**/*.ts
**/stores/**/*.ts
**/state/**/*.ts

# Find all reducers
**/reducers/**/*.ts
**/slices/**/*.ts
```

### API Layer

```bash
# Find all API clients
**/api/**/*.ts
**/services/**/*.ts
**/lib/api/**/*.ts
```

### Hooks

```bash
# Find all custom hooks
**/hooks/**/*.ts
use*.ts
```

---

## Discovery Commands

### Using ripgrep (rg)

```bash
# Find all exported functions
rg "export (function|const)" --type ts

# Find all classes
rg "^class \w+" --type cs

# Find all API routes
rg "@(Get|Post|Put|Delete|Patch)" --type cs
rg "router\.(get|post|put|delete|patch)" --type ts

# Find all database models
rg "class.*DbContext" --type cs
rg "class.*extends Model" --type ts
```

### Using grep

```bash
# Find all controllers
grep -r "Controller" --include="*.cs"

# Find all services
grep -r "Service" --include="*.ts"

# Find all endpoints
grep -r "@api" --include="*.py"
```

### Using find + grep

```bash
# Find all TypeScript service files
find . -name "*Service.ts" -o -name "*service.ts"

# Find all Python models
find . -name "models.py"

# Find all configuration files
find . -name "*Config.cs" -o -name "*Options.cs"
```

---

## Cross-Reference Discovery

### Find Kafka Topics

```bash
# .NET
rg "Topic = \"" --type cs
rg "KafkaTopicAttribute" --type cs

# Node.js
rg "topic:" --type ts
rg "TOPIC_" --type ts

# Python
rg "topic=" --type py
```

### Find External API Integrations

```bash
# HTTP clients
rg "HttpClient" --type cs
rg "axios\." --type ts
rg "requests\." --type py

# Base URLs
rg "BaseAddress|baseURL|base_url"
```

### Find Webhooks

```bash
# Webhook handlers
rg "webhook" -i
rg "callback" -i

# Signature verification
rg "signature|hmac" -i
```

---

## Documentation Coverage Commands

### Count undocumented components

```bash
# Count total controllers
CONTROLLERS=$(rg "class.*Controller" --type cs | wc -l)

# Count documented endpoints
DOCUMENTED=$(rg "## Endpoints" docs/api/ | wc -l)

# Calculate gap
echo "Gap: $(($CONTROLLERS - $DOCUMENTED))"
```

### Generate component list

```bash
# Extract all controller names
rg "class (\w+)Controller" --type cs -r '$1' --no-filename | sort

# Extract all service names
rg "class (\w+)Service" --type cs -r '$1' --no-filename | sort

# Extract all Kafka topics
rg "Topic = \"(\w+)\"" --type cs -r '$1' --no-filename | sort | uniq
```

---

## Multi-Language Projects

For projects with multiple languages:

1. Run discovery for each language separately
2. Consolidate results in coverage report
3. Prioritize by component type (API > Services > Config)

### Example workflow

```bash
# Discover .NET components
rg "Controller|Service|DbContext" --type cs > discovered-dotnet.txt

# Discover TypeScript components
rg "Controller|Service|Repository" --type ts > discovered-ts.txt

# Discover Python components
rg "views|models|tasks" --type py > discovered-py.txt

# Compare with docs
diff discovered-dotnet.txt documented-components.txt
```

---

## Best Practices

1. **Start broad, then narrow**: Begin with file patterns, then search for specific annotations/decorators
2. **Check naming conventions**: Adjust patterns based on project conventions (Service vs service, Controller vs controller)
3. **Search for interfaces too**: Many projects define contracts in separate interface files
4. **Look for tests**: Test files often reveal undocumented components
5. **Check migrations**: Database migration files reveal schema changes that may need documentation

---

## Related Resources

- [Audit Workflows](audit-workflows.md) - How to use these patterns in systematic audits
- [Priority Framework](priority-framework.md) - How to prioritize discovered components
