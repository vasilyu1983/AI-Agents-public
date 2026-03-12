# Psychological Safety in Code Reviews

## Why Psychological Safety Matters

Research in *Empirical Software Engineering* found that **psychological safety directly advances teams' ability to pursue software quality**. When developers feel safe:

- They speak up about potential issues more freely
- They debate solutions constructively
- They ask questions without fear of judgment
- They learn from mistakes rather than hiding them
- They share innovative ideas and alternative approaches

## Core Principles

### 1. Focus on Code, Not People

**BAD: Bad**:
- "You wrote this wrong"
- "Why didn't you know about this pattern?"
- "This is sloppy work"
- "You always miss edge cases"

**GOOD: Good**:
- "This approach might lead to X issue. Consider Y instead"
- "This pattern might help here: [example]"
- "Let's add handling for this edge case: [specific case]"
- "I noticed this edge case. Here's how we could handle it: [suggestion]"

### 2. Ask Questions, Don't Command

**BAD: Bad**:
- "Change this to use X pattern"
- "Fix this immediately"
- "This needs to be refactored"
- "Use Y library instead"

**GOOD: Good**:
- "Have you considered using X pattern? It might help with [specific benefit]"
- "What do you think about refactoring this to improve [specific aspect]?"
- "Could we use Y library here? I've found it helpful for [reason]"
- "QUESTION: Is there a reason for this approach? I'm wondering if [alternative] might work better"

### 3. Explain the "Why"

**BAD: Bad**:
- "Don't do this"
- "Use parameterized queries"
- "This is wrong"
- "Needs error handling"

**GOOD: Good**:
- "This creates a SQL injection vulnerability because user input goes directly into the query. Use parameterized queries to prevent this"
- "REQUIRED: Add error handling here. If the API call fails, the app will crash without user feedback"
- "This approach might cause memory leaks because event listeners aren't cleaned up. Consider using cleanup functions"

### 4. Balance Criticism with Praise

**Don't just point out problems** - acknowledge what's working well:

```
PRAISE: Excellent error handling in the payment processing function.
The fallback mechanism and detailed logging will make debugging much easier.

SUGGESTION: Consider extracting the validation logic (lines 45-67)
into a separate function for better testability.

REQUIRED: This query could lead to N+1 performance issues.
Let's use a JOIN to fetch posts with users in a single query.
```

### 5. Share Learning Moments

**Make reviews a two-way learning experience**:

```
"I didn't know about this ES feature before - thanks for introducing it!
One thing to watch out for is browser compatibility. We might need a polyfill."

"Interesting approach! I learned about this pattern from [resource].
It might help with the scalability concern we discussed."

"QUESTION: I haven't used this library before. What advantages
does it have over [alternative]? I'm curious to learn more."
```

## Comment Structure Templates

### For Bugs and Critical Issues

```
REQUIRED: [Specific issue] on line X

Problem: [Explain what will happen]
Impact: [Why this matters]
Solution: [How to fix it]

Example:
// Current code
[problematic code]

// Suggested fix
[corrected code]

Reasoning: [Why this fix works]
```

### For Design Improvements

```
SUGGESTION: Consider [alternative approach]

Current approach: [What's there now]
Potential issue: [What could be better]
Alternative: [Suggested improvement]
Benefits: [Why this might be better]

This is optional, but I think it would help with [specific aspect].
What do you think?
```

### For Questions and Clarifications

```
QUESTION: [Specific question about approach]

I'm trying to understand [specific aspect]. Could you help me understand:
- Why we chose [approach A] over [approach B]?
- How does this handle [specific scenario]?
- What happens when [edge case]?

This will help me review more effectively.
```

### For Positive Feedback

```
PRAISE: [Specific thing done well]

This is exactly the right approach because:
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

Great work on [specific aspect]!
```

## Communication Patterns

### Pattern: Collaborative Discovery

Instead of telling someone what's wrong, guide them to discover it:

**BAD: Directive**:
```
This function is too complex. Extract the validation logic.
```

**GOOD: Collaborative**:
```
QUESTION: I'm finding this function a bit hard to follow. What do you
think about extracting the validation logic into a helper? It might
make both the main function and the validation easier to test.

Here's how I'm imagining it:
[example code]

Does this make sense, or am I missing something about why it needs
to be together?
```

### Pattern: Offering Alternatives

Present options rather than mandates:

**BAD: Single directive**:
```
Use Zod for validation here.
```

**GOOD: Multiple options**:
```
SUGGESTION: For type-safe validation, we have a few options:

1. Zod - Runtime validation with TypeScript inference
2. Yup - Lighter weight, good for simple cases
3. Custom validation - More control but more code

Given that we're already using Zod elsewhere in the project,
option 1 might give us the most consistency. What do you think?
```

### Pattern: Acknowledging Constraints

Recognize that there may be good reasons for current approach:

**BAD: Assuming**:
```
This should use async/await instead of promises.
```

**GOOD: Acknowledging**:
```
QUESTION: I notice this uses promise chains instead of async/await.
Is there a specific reason for this choice? I'm wondering if
async/await might make the error handling clearer, but I might
be missing a constraint.
```

## Handling Disagreements

### When You Disagree with an Approach

**Step 1**: Understand their reasoning
```
QUESTION: Can you help me understand the reasoning behind [decision]?
I want to make sure I'm considering all the factors you considered.
```

**Step 2**: Present your concern
```
I see your point about [their reasoning]. My concern is that
[specific issue] might occur because [explanation].
```

**Step 3**: Suggest alternatives
```
Would [alternative approach] address both concerns? It would
[solve your issue] while also [addressing my concern].
```

**Step 4**: Escalate if needed (for critical issues only)
```
This is a critical concern because [impact]. Can we get input
from [senior engineer/architect] before proceeding? I want to
make sure we're making the best decision here.
```

### When Someone Disagrees with Your Feedback

**Listen and reconsider**:
```
That's a good point about [their reasoning]. I hadn't considered
[aspect]. Given that, my suggestion might not be the best fit here.
```

**Find middle ground**:
```
I see what you mean about [their point]. What if we [compromise
solution] that addresses both [your concern] and [their concern]?
```

**Agree to disagree on non-critical items**:
```
I understand your perspective. Since this is a SUGGESTION and not
REQUIRED, let's go with your approach. We can revisit if issues arise.
```

## Anti-Patterns to Avoid

### 1. Bikeshedding
Spending disproportionate time on trivial issues:

**BAD: Bad**:
```
Use single quotes instead of double quotes here (20 comments about quote style)
This color should be #FF0000 not #FF0001
Rename `data` to `responseData` (when naming is already clear)
```

**GOOD: Good**:
```
Focus on: logic errors, security issues, performance problems, architectural concerns
Let automated tools handle: formatting, style, trivial naming
```

### 2. Nitpicking Without Impact
Pointing out issues that don't actually matter:

**BAD: Bad**:
```
This function is 51 lines, it should be 50 maximum.
You could save 2 bytes by using ++ instead of += 1.
This comment could be more concise.
```

**GOOD: Good**:
```
This function handles 4 different responsibilities. Consider
extracting the validation logic and error handling into separate
functions to improve testability.
```

### 3. Vague Criticism
Feedback without actionable guidance:

**BAD: Bad**:
```
This doesn't look right.
This is not best practice.
This could be better.
There's a problem here.
```

**GOOD: Good**:
```
This approach might cause race conditions when multiple users
update the same record. Consider using optimistic locking with
a version field.
```

### 4. "Just" Language
Minimizing the work required:

**BAD: Bad**:
```
Just refactor this.
Just add tests.
Just use a different pattern.
Why don't you just rewrite it?
```

**GOOD: Good**:
```
This refactoring would improve maintainability. It would involve:
1. Extracting the validation logic
2. Creating new unit tests
3. Updating the integration tests

Estimated effort: 2-3 hours. Worth it for this critical path?
```

### 5. Approval Without Review
Rubber-stamping without actually reading:

**BAD: Bad**:
```
LGTM (on a 800-line PR reviewed in 30 seconds)
Looks good! (no specific feedback, no questions)
Ship it! (clear issues visible in the code)
```

**GOOD: Good**:
```
Reviewed focused on [specific areas]. Here's what I found:

PRAISE: [specific good things]
REQUIRED: [critical issues]
SUGGESTION: [optional improvements]
QUESTION: [clarifications needed]

Overall looks solid after addressing the REQUIRED items.
```

## Cultural Practices

### 1. Normalize Learning
```
"I learned something new from this PR - thanks for introducing
me to [pattern/library/technique]!"

"Interesting approach! I would have done it differently, but
I can see the benefits of your way."

"QUESTION: Can you explain why this works? I want to learn
this pattern for future use."
```

### 2. Celebrate Good Code
```
PRAISE: This error handling is exemplary. The detailed logging,
graceful fallback, and user-friendly error messages make this
production-ready. Great work!

PRAISE: Excellent test coverage! The edge cases you caught
(empty array, null values, boundary conditions) will prevent
bugs down the line.
```

### 3. Share Context
```
"For context: We had a similar issue in [other project] where
[problem] occurred. That's why I'm suggesting [alternative]."

"FYI: The team decided on [standard] for [situation] in our
last architecture review. See [link to decision]."
```

### 4. Welcome Questions
```
"Great question! Let me explain why we use this pattern..."

"I'm glad you asked about this - it's not obvious. Here's
the reasoning..."

"That's a common source of confusion. The key difference is..."
```

## Review Etiquette

### Timing
- Review within 24 hours of request
- Provide initial feedback even if review isn't complete
- Communicate if you can't review within expected timeframe

### Response
- Respond to author's questions promptly
- Re-review updated code in a timely manner
- Approve promptly when REQUIRED items are addressed

### Tone
- Assume positive intent
- Be respectful and professional
- Use emoji thoughtfully ([OK] [FAIL] [TIP]) but don't overdo it
- Match the team's communication style

## Example: Full Review with Psychological Safety

```
## Summary
This PR adds user authentication to the API. The core logic is solid,
and I appreciate the comprehensive test coverage. A few required
security items to address, and some suggestions for improvement.

## Strengths
PRAISE: Excellent work on the test coverage! You've tested edge cases
I wouldn't have thought of (expired tokens, malformed headers, concurrent
sessions). This will prevent a lot of future bugs.

PRAISE: The error messages are user-friendly and informative without
leaking implementation details. Great balance of helpful and secure.

## Required Changes

### 1. Password Hashing (Security)
REQUIRED: Line 45 - Passwords are stored in plaintext

Problem: If the database is compromised, all user passwords are exposed.
Impact: Critical security vulnerability, violates OWASP guidelines.

Solution: Use bcrypt with salt for password hashing:
```javascript
const bcrypt = require('bcrypt');
const saltRounds = 10;
const hashedPassword = await bcrypt.hash(password, saltRounds);
```

### 2. SQL Injection Prevention
REQUIRED: Line 89 - String concatenation in SQL query

Current:
```javascript
const query = `SELECT * FROM users WHERE email = '${email}'`;
```

This allows SQL injection attacks. Use parameterized queries:
```javascript
const query = 'SELECT * FROM users WHERE email = ?';
const results = await db.query(query, [email]);
```

## Suggestions

### 1. Token Expiration
SUGGESTION: Consider adding token expiration

Current tokens never expire, which increases risk if compromised.
Most auth systems use 1-hour access tokens + refresh tokens.

This is optional for now but we should add it before production.
What do you think about implementing this in a follow-up PR?

### 2. Rate Limiting
SUGGESTION: Add rate limiting to login endpoint

This would prevent brute-force attacks. We could use express-rate-limit:
```javascript
const rateLimit = require('express-rate-limit');
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5 // limit each IP to 5 requests per windowMs
});
```

## Questions

QUESTION: Line 156 - Why store session data in memory?

I'm wondering about scalability - if we have multiple server instances,
users will lose sessions when hitting different servers. Have you
considered Redis for session storage, or is there a reason to keep
it in-memory for now?

## Final Thoughts

Really solid implementation overall! Once the two REQUIRED security
items are addressed, this will be ready to merge. Happy to help if
you have questions about implementing the bcrypt or parameterized
queries.

Thanks for the thorough work on this!
```

## Resources

- **Research**: "Psychological Safety and Software Quality" (Empirical Software Engineering)
- **Google**: "How to Do a Code Review" (engineering practices guide)
- **Microsoft**: "Code Review Best Practices" (Azure DevOps documentation)
- **Book**: "The Fearless Organization" by Amy Edmondson
