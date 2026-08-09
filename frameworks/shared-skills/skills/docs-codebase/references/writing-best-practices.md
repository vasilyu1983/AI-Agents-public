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
- [AI-Writing Tells: Recognition and Fixes](#ai-writing-tells-recognition-and-fixes)

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
- Node.js 20+ installed
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

## AI-Writing Tells: Recognition and Fixes

**Scope: this section governs authored documentation prose** (READMEs, guides, ADRs, runbooks, reference docs) — the same axis as every other section in this file. **It does not govern agent conversational output** (what an agent says in chat while doing a task); that is a different axis and this library currently has no dedicated guidance for it (see [Residual Gap](#residual-gap) below). Where a tell shows up differently in the two contexts, the table notes it.

These patterns exist because LLM text generation has predictable statistical habits: it reaches for the same intensifiers, the same three-item lists, the same hedges, more often than a human writer would. None of them prove a document was AI-written on their own — flag **clusters** of tells, not one isolated hit, and never gut a sentence that happens to use one flagged word in a legitimate way. A single "however" or one em dash is not a defect.

| Tell | Why it reads as AI-generated | Fix |
|------|------------------------------|-----|
| **Inflated significance** — "stands as a testament to," "marks a pivotal moment," "underscores its importance," "represents a shift" | Puffs up an ordinary fact by claiming it symbolizes something larger, without evidence for the larger claim. | State the fact plainly. Cut the claim about broader significance unless a source supports it. |
| **AI-vocabulary words** — delve, crucial, intricate, tapestry, testament, underscore (verb), pivotal, landscape (abstract noun), foster, garner, showcase, leverage (verb) | These words spike sharply in frequency in post-2023 text and cluster together. | Replace with the plain word: "use" not "leverage," "detailed" not "intricate," "show" not "showcase." |
| **Copula avoidance** — "serves as," "stands as," "boasts," "features [a]," "offers [a]" in place of "is"/"are"/"has" | Elaborate constructions substituted for simple statements of fact. | Use "is," "are," or "has" directly: "the tool is X," not "the tool serves as X." |
| **Negative parallelisms / tailing negations** — "It's not just X, it's Y," or a clause tacked on as "no guessing," "no wasted effort" | An overused rhetorical shape that reads as templated rather than considered. | Write the plain positive statement, or turn the tailing fragment into a real clause: "so the user doesn't have to guess." |
| **Rule-of-three overuse** — forcing every list or claim into exactly three items ("faster, safer, and more reliable") | Real requirements rarely come in even groups of three; the pattern signals a filled-in template rather than an observed fact. | List however many items are actually true. Two is fine. Five is fine. |
| **Elegant variation** — cycling synonyms for the same referent across sentences ("the function," "this method," "the routine," "said logic") | Avoids repeating a word at the cost of clarity — a reader has to work out these all mean the same thing. | Repeat the exact term. In technical docs, consistent terminology (already required above, see [Be Consistent](#3-be-consistent)) beats variety. |
| **False ranges** — "from X to Y" where X and Y are not points on a real scale ("from the smallest bug fix to the grandest architectural vision") | Manufactures a sense of comprehensive scope without the range being meaningful or measurable. | Name the actual set of things covered, without the borrowed structure of a scale. |
| **Em dash / en dash overuse** — leaning on `—` or `–` as a universal connector | One of the most statistically reliable single-token AI tells; overuse also just makes prose harder to parse (was that an aside, a list break, or a new clause?). | Replace with a period, comma, colon, or parentheses depending on the relationship. A single em dash for a genuine aside is fine; several per paragraph is the tell. |
| **Boldface overuse** — bolding phrases mechanically throughout a paragraph, not just true key terms | Turns emphasis into noise; if everything is bold, nothing is. | Bold only the term being defined or the one thing a scanning reader must not miss. |
| **Inline-header vertical lists** — `- **Term:** sentence restating the term` repeated down a list | A templated shape, not a description of an actual capability list. | Either drop the bold lead-in and let the sentence stand, or convert to prose if the items relate to each other. |
| **Emojis as bullet/heading decoration** | Decorative emojis on every bullet or heading read as autogenerated formatting rather than an intentional signal. | Remove unless the emoji itself carries meaning the reader needs (e.g., a status icon in a table). |
| **Knowledge-cutoff disclaimers and speculative gap-filling** — "as of [date]," "while specific details are limited," followed by invented plausible-sounding filler | Two related tells: stale training-cutoff caveats left in text, and confident-sounding guesses dressed up as fact when a source is missing. | State plainly that the information is not available, or cut the sentence. Never fill an unknown with a plausible-sounding guess. |
| **Hyphenated word pair overuse** — hyphenating compounds like "high-quality," "data-driven," "real-time" even in predicate position ("the report is high-quality") | Humans hyphenate attributive compounds ("a high-quality report") but usually drop the hyphen in predicate position ("the report is high quality"). AI applies the hyphen uniformly. | Keep the hyphen only when the compound sits before the noun it modifies. Drop it when the compound follows the noun. |
| **Persuasive authority tropes** — "the real question is," "at its core," "what really matters," "fundamentally" | Signals a manufactured pivot to a "deeper truth" that the following sentence usually doesn't deliver — it just restates an ordinary point with more ceremony. | Cut the framing phrase and state the point directly. |
| **Signposting and announcements** — "Let's dive in," "here's what you need to know," "let's break this down," in explanatory prose | Announces what the text is about to do instead of doing it; reads as a tutorial-script narrator rather than the documentation itself. | Delete the announcement and start with the content. |
| **Fragmented headers** — a heading immediately followed by a one-line paragraph that just restates the heading before real content starts | A rhetorical warm-up that adds a sentence without adding information. | Delete the throwaway line; start the section with the first substantive sentence. |
| **Diff-anchored writing** — documentation phrased as narrating a change ("this replaces the old approach of...") rather than describing the current state | Forces a reader to reconstruct history to understand what the code does today. Correct in changelogs and migration guides, wrong everywhere else. | Describe the thing as it is now. Save "replaces X" framing for changelog and migration-guide entries, where it's the point. |
| **Aphorism formulas** — "X is the language of Y," "X becomes a trap," "the architecture of Z" | Turns an ordinary claim into a reusable-sounding aphorism that feels profound but adds no precision. | Replace with the concrete claim the aphorism is gesturing at. |
| **Conversational rhetorical openers** — "Honestly?," "Here's the thing," "Look," used as a theatrical pause before an ordinary point | Manufactures fake candor before delivering a routine statement — the tell is the pause-and-reveal structure, not the word itself. | State the point without the staged lead-in. |
| **Curly quotation marks** in plain-text contexts (code comments, config, CLI examples) | Straight quotes are required where curly quotes break parsing; curly quotes appearing there usually means text was pasted from a chat UI without adjustment. | Use straight quotes (`"`) in anything that might be parsed. This is a mechanical check, not a style judgment — curly quotes in prose alone are not a tell (most editors auto-curl by default). |
| **Sycophantic/servile tone** — "Great question!," "You're absolutely right," "That's an excellent point" | People-pleasing filler that has no place in reference material and, in agent conversation, reads as flattery rather than a genuine assessment. | In docs: delete outright. In agent speech: give the direct assessment without the preamble. |
| **Collaborative-communication artifacts** — "I hope this helps!," "Let me know if you'd like me to expand," "Would you like examples?" | Text written as chatbot correspondence, pasted into content that has no reader to address this way. | Delete. Documentation has no back-and-forth to refer to. |

### Already covered elsewhere in this guide

Three tells from the source taxonomy overlap with sections earlier in this file. Rather than duplicate them, this section defers to the existing guidance:

- **Passive voice and subjectless fragments** ("No configuration file needed") — see [Use Active Voice](#1-use-active-voice).
- **Filler phrases** ("in order to," "it is important to note that") and **excessive hedging** ("could potentially possibly") — see [Avoid Filler Words](#5-avoid-filler-words).
- **Overusing "should"** as a substitute for imperative instructions — see [Overusing "Should"](#3-overusing-should).

### Docs prose vs. agent speech

Most tells above read as defects in both axes — inflated significance, copula avoidance, false ranges, and the vocabulary list are just as wrong in a chat response as in a README. A few apply asymmetrically:

- **Signposting** ("Let's dive in") and **conversational rhetorical openers** ("Honestly?") are near-universal complaints about agent chat replies, but appear far less often in already-written docs, since nobody drafts a README by narrating their own process.
- **Collaborative-communication artifacts** ("I hope this helps!") and **sycophantic tone** ("Great question!") are almost exclusively an agent-speech problem — they leak into docs only when a chat transcript gets pasted into a file without cleanup.
- **Diff-anchored writing** and **fragmented headers** are near-exclusively a docs problem; they describe a written artifact's structure, not a conversational turn.

### Attribution

This taxonomy is adapted, in this file's own voice and condensed, from [blader/humanizer](https://github.com/blader/humanizer) at commit `523374dee72d67c7b2b5f858ea0094ffda49c3ac` (MIT license), extracted 2026-08-09. The source project itself derives its taxonomy from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide (WikiProject AI Cleanup).

Of the source's 33 patterns: **22** are reproduced above as distinct table rows; **3** are covered by cross-reference to this file's existing sections (passive voice, filler phrases, excessive hedging — see [Already covered elsewhere in this guide](#already-covered-elsewhere-in-this-guide)); **8** were cut:

- Too narrow to Wikipedia-style encyclopedic or travel-article prose, with little application to technical docs: undue emphasis on media coverage/notability, promotional heritage-article language ("nestled," "breathtaking"), vague sourcing attributions ("experts believe"), formulaic "Challenges and Future Prospects" sections, generic upbeat closing paragraphs.
- Too subjective to check by reading a single paragraph, requiring a broader read of the whole document's rhythm: manufactured-punchline / staccato-drama pacing, superficial "-ing"-ending analysis treated as a category distinct from inflated significance (folded into that row instead).
- **Title case in headings** was cut deliberately, not as noise: it is a genuine style choice, not a reliable AI tell. Sentence case vs. title case is a house-style decision (this file already uses sentence case in its own H2/H3 headings, which is worth noting as the convention here, but that's a style pick, not evidence of AI authorship either way).

### Residual gap

This section governs written documentation only. **Agent conversational output — how an agent talks while doing a task, in chat, in commit messages, in PR descriptions — remains otherwise ungoverned in this library.** Several of the tells above (signposting, sycophantic tone, collaborative-communication artifacts, conversational rhetorical openers) were originally flagged as an agent-speech problem, not a docs-prose problem, and this file does not close that gap; it only borrows the taxonomy for the axis it already owns. A dedicated agent-speech style contract, if one gets built, belongs in a different file (likely alongside `.claude/rules/coding-behavior.md` or an agent-persona reference), not here.

---

## Resources

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/)
- [Write the Docs](https://www.writethedocs.org/)
- [Hemingway Editor](https://hemingwayapp.com/) - Readability tool
- [Grammarly](https://www.grammarly.com/) - Grammar and style checker
