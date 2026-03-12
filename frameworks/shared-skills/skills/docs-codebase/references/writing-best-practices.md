# Technical Writing Best Practices

Comprehensive guide to writing clear, effective technical documentation.

## Table of Contents

- [Core Principles](#core-principles)
- [Writing for Your Audience](#writing-for-your-audience)
- [Structure and Organization](#structure-and-organization)
- [Language and Style](#language-and-style)
- [Code Examples](#code-examples)
- [Visual Elements](#visual-elements)
- [Editing and Review](#editing-and-review)

---

## Core Principles

### 1. Know Your Purpose

Every piece of documentation should have a clear purpose:

- **Tutorial:** Teach a specific skill (learning-oriented)
- **How-to guide:** Solve a specific problem (task-oriented)
- **Reference:** Provide detailed information (information-oriented)
- **Explanation:** Clarify and deepen understanding (understanding-oriented)

**Example:**

```markdown
# Bad: Mixed purposes
"Understanding and Installing PostgreSQL"

# Good: Clear purpose
"Installing PostgreSQL" (How-to guide)
"PostgreSQL Architecture Overview" (Explanation)
```

### 2. Write for Scanning

Most readers scan rather than read word-for-word.

**Techniques:**
- Use descriptive headings
- Keep paragraphs short (3-5 sentences)
- Use bullet points and numbered lists
- Highlight key information
- Add visual breaks

**Example:**

```markdown
# Bad
PostgreSQL is a powerful, open source object-relational database system that uses and extends the SQL language combined with many features that safely store and scale complicated data workloads. It has been actively developed for over 30 years and has earned a strong reputation for reliability, feature robustness, and performance.

# Good
PostgreSQL is an open-source relational database with these key features:

- SQL support with advanced extensions
- ACID compliance for data integrity
- Horizontal scaling capabilities
- 30+ years of active development
- Strong reputation for reliability and performance
```

### 3. Be Consistent

Consistency reduces cognitive load and builds trust.

**Maintain consistency in:**
- Terminology (choose one term and stick with it)
- Formatting (headings, code blocks, lists)
- Voice and tone
- Document structure

**Example:**

```markdown
# Bad: Inconsistent terminology
"Click the submit button"
"Press the save control"
"Select the confirm option"

# Good: Consistent terminology
"Click the Submit button"
"Click the Save button"
"Click the Confirm button"
```

---

## Writing for Your Audience

### 1. Identify Your Audience

Know who you're writing for:

- **Beginners:** Need more context, step-by-step instructions, explanations
- **Intermediate:** Want practical examples, common patterns, best practices
- **Advanced:** Need technical details, edge cases, performance considerations

### 2. Adjust Technical Level

**For beginners:**
```markdown
# Installing Node.js

Node.js is a JavaScript runtime that lets you run JavaScript outside the browser.

**Prerequisites:** None (we'll guide you through everything)

**Step 1: Download Node.js**
1. Go to https://nodejs.org
2. Click the green "LTS" button
3. Wait for the download to complete
```

**For advanced users:**
```markdown
# Node.js Installation

```bash
# Via nvm (recommended for version management)
nvm install --lts
nvm use --lts

# Verify installation
node --version
npm --version
```
```

### 3. Define Jargon and Acronyms

**First use:**
```markdown
API (Application Programming Interface) - a set of rules that allows programs to talk to each other
```

**Thereafter:**
```markdown
The API returns JSON data...
```

---

## Structure and Organization

### 1. Start with Context

Every document should answer:
- What is this?
- Why should I care?
- What will I learn/accomplish?

**Example:**

```markdown
# User Authentication Guide

This guide explains how to implement user authentication in your application.

**You will learn:**
- Setting up OAuth2 with Google and GitHub
- Managing user sessions securely
- Implementing password reset flows

**Prerequisites:**
- Node.js 18+ installed
- Basic understanding of Express.js
- A registered OAuth application
```

### 2. Use the Inverted Pyramid

Put the most important information first.

**Good structure:**
1. **What** - Quick description and main point
2. **Why** - Context and benefits
3. **How** - Detailed instructions
4. **Advanced** - Edge cases and optimizations

**Example:**

```markdown
## Caching with Redis

**What:** Redis is an in-memory data store used for caching frequently accessed data.

**Why:** Reduces database load and improves response times by up to 10x.

**How:**
1. Install Redis: `npm install redis`
2. Connect to Redis...
3. Cache database queries...

**Advanced:**
- Cache invalidation strategies
- Redis cluster setup
- Monitoring and debugging
```

### 3. Create a Logical Flow

**For tutorials:**
1. Learning objectives
2. Prerequisites
3. Step-by-step instructions
4. Verification/testing
5. Next steps

**For reference docs:**
1. Overview
2. Quick start
3. Detailed reference (alphabetical or by category)
4. Examples
5. Related resources

---

## Language and Style

### 1. Use Active Voice

**Passive (weak):**
```markdown
The database is queried by the API.
The error was encountered during deployment.
```

**Active (strong):**
```markdown
The API queries the database.
We encountered an error during deployment.
```

### 2. Use Imperative Mood for Instructions

**Wrong:**
```markdown
You should install the dependencies.
You can run the tests.
```

**Correct:**
```markdown
Install the dependencies.
Run the tests.
```

### 3. Keep Sentences Short and Simple

**Complex:**
```markdown
In order to facilitate the establishment of a connection to the database,
it is necessary to configure the environment variables.
```

**Simple:**
```markdown
Configure environment variables to connect to the database.
```

**Rule of thumb:** Aim for 15-20 words per sentence.

### 4. Use Concrete, Specific Language

**Vague:**
```markdown
The application might be slow if there are many users.
```

**Specific:**
```markdown
Response times increase to 2-3 seconds when handling 1000+ concurrent users.
```

### 5. Avoid Filler Words

**Wordy:**
```markdown
It is important to note that you should basically make sure to always
validate user input in order to prevent security vulnerabilities.
```

**Concise:**
```markdown
Validate user input to prevent security vulnerabilities.
```

**Common filler words to avoid:**
- basically
- actually
- really
- very
- quite
- just
- simply
- in order to
- it is important to note that

### 6. Use Second Person

**Good:**
```markdown
You can install the package with npm.
Run your tests to verify the installation.
```

**Avoid:**
```markdown
One can install the package...
Users should run their tests...
```

---

## Code Examples

### 1. Make Examples Complete and Runnable

**Bad (incomplete):**
```javascript
user.save();
```

**Good (complete):**
```javascript
const user = new User({
  email: 'user@example.com',
  name: 'John Doe'
});

await user.save();
console.log('User saved successfully');
```

### 2. Explain What the Code Does

**Template:**
```markdown
**Example: [What this example demonstrates]**

[Brief explanation of what this code does and why]

```language
[Code]
```

**Output:**
```
[Expected output]
```
```

**Real example:**
```markdown
**Example: Create a new user with validation**

This example shows how to create a user with email validation and error handling.

```javascript
async function createUser(email, name) {
  if (!isValidEmail(email)) {
    throw new Error('Invalid email address');
  }

  const user = new User({ email, name });
  await user.save();
  return user;
}
```

**Output:**
```
User { id: '123', email: 'user@example.com', name: 'John Doe' }
```
```

### 3. Use Syntax Highlighting

Always specify the language:

````markdown
```javascript
console.log('Hello, world!');
```

```bash
npm install express
```

```json
{
  "name": "my-app",
  "version": "1.0.0"
}
```
````

### 4. Show Error Cases

Don't just show the happy path.

```javascript
// Good: Shows both success and error cases
try {
  const user = await getUser(id);
  console.log(user.name);
} catch (error) {
  if (error.code === 'USER_NOT_FOUND') {
    console.error('User not found');
  } else {
    console.error('Unexpected error:', error);
  }
}
```

---

## Visual Elements

### 1. Use Diagrams for Complex Concepts

```markdown
# Database Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │─────▶│  API Server │─────▶│  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
```
```

Or use Mermaid for interactive diagrams:

````markdown
```mermaid
sequenceDiagram
    Client->>API: POST /users
    API->>Database: INSERT user
    Database-->>API: Success
    API-->>Client: 201 Created
```
````

### 2. Use Tables for Comparisons

```markdown
| Feature | Option A | Option B |
|---------|----------|----------|
| Performance | Fast | Moderate |
| Ease of use | Complex | Simple |
| Cost | High | Low |
```

### 3. Use Screenshots Strategically

**When to use screenshots:**
- UI workflows
- Visual verification steps
- Complex interfaces

**Best practices:**
- Annotate screenshots with arrows/highlights
- Keep screenshots up-to-date
- Provide alt text for accessibility
- Optimize image size

---

## Editing and Review

### 1. Self-Editing Checklist

**Content:**
- [ ] Purpose is clear
- [ ] Audience level is appropriate
- [ ] Information is accurate and up-to-date
- [ ] All steps are tested and work
- [ ] Examples are complete and runnable

**Structure:**
- [ ] Logical flow from beginning to end
- [ ] Headings are descriptive and hierarchical
- [ ] Paragraphs are short and focused
- [ ] Lists are used appropriately

**Language:**
- [ ] Active voice used
- [ ] Imperative mood for instructions
- [ ] No jargon without explanation
- [ ] No filler words
- [ ] Consistent terminology

**Code:**
- [ ] Syntax highlighting specified
- [ ] Code is complete and runnable
- [ ] Code is explained
- [ ] Error cases shown

**Formatting:**
- [ ] Consistent style
- [ ] No broken links
- [ ] Images have alt text
- [ ] Table of contents (for long docs)

### 2. Read It Aloud

Reading aloud helps catch:
- Awkward phrasing
- Run-on sentences
- Missing words
- Confusing logic

### 3. Test Your Instructions

**Critical:** Follow your own documentation step-by-step to verify it works.

### 4. Get Feedback

Ask someone else to review:
- Technical accuracy
- Clarity
- Completeness
- Tone

---

## Common Mistakes to Avoid

### 1. Assuming Knowledge

**Bad:**
```markdown
Simply configure the OAuth2 flow.
```

**Good:**
```markdown
Configure OAuth2 authentication:

1. Register your application at https://console.cloud.google.com
2. Copy your Client ID and Client Secret
3. Set the redirect URI to http://localhost:3000/auth/callback
```

### 2. Using Vague Pronouns

**Bad:**
```markdown
When the server connects to the database, it sends a query.
This might fail if this is not configured correctly.
```

**Good:**
```markdown
When the server connects to the database, the server sends a query.
The connection might fail if the database credentials are not configured correctly.
```

### 3. Overusing "Should"

**Weak:**
```markdown
You should install Node.js.
You should run the tests.
```

**Strong:**
```markdown
Install Node.js.
Run the tests.
```

### 4. Burying the Lead

**Bad:**
```markdown
## Database Configuration

PostgreSQL is a powerful database that has been around for 30 years...
[3 paragraphs of history]
...
To configure PostgreSQL, set DATABASE_URL=...
```

**Good:**
```markdown
## Database Configuration

Set the `DATABASE_URL` environment variable:

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

PostgreSQL is a powerful... [background information follows]
```

---

## Writing for Different Document Types

### README Files

**Must include:**
1. One-line description
2. Key features
3. Installation instructions
4. Basic usage example
5. Links to detailed docs

**Keep it short:** 200-400 lines max.

### API Documentation

**For each endpoint:**
1. HTTP method and path
2. Description
3. Authentication requirements
4. Request parameters (query, path, body)
5. Response format with example
6. Status codes
7. cURL example

### Tutorials

**Structure:**
1. What you'll build
2. Prerequisites
3. Step-by-step instructions
4. Verification/testing
5. Next steps

**Voice:** Friendly, encouraging, educational.

### Reference Documentation

**Structure:**
1. Alphabetical or categorical organization
2. Consistent format for each entry
3. Complete parameter/return documentation
4. Examples for each entry

**Voice:** Concise, precise, neutral.

---

## Resources

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/)
- [Write the Docs](https://www.writethedocs.org/)
- [Hemingway Editor](https://hemingwayapp.com/) - Readability tool
- [Grammarly](https://www.grammarly.com/) - Grammar and style checker
