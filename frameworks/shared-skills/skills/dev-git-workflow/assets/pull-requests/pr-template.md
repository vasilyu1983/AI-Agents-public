# Pull Request Description Template

Copy this template for high-quality pull request descriptions.

---

## Summary
[1-2 sentence description of what changed and why]

## Motivation
[Business or technical reason for this change]

Why is this change needed? What problem does it solve?

## Changes
[Detailed list of what changed]
- Added X feature
- Refactored Y module
- Fixed Z bug

## Implementation Details
[Technical approach and key decisions]

- Chose approach A over B because [reason]
- Used library X for [specific need]
- Considered edge cases: [list]

## Testing
[How you verified this works]

- [ ] Unit tests added (coverage: X%)
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Tested on Chrome, Firefox, Safari
- [ ] Tested edge cases: [list]

## Screenshots/Videos
[For UI changes - delete if not applicable]

**Before:**
[image or video]

**After:**
[image or video]

## Performance Impact
[If applicable - delete if not relevant]

- Benchmark results: [data]
- Load time: before X ms -> after Y ms
- Database queries: optimized from N to M

## Security Considerations
[If applicable - delete if not relevant]

- Input validation added for [fields]
- Authorization check for [resource]
- No secrets in code (verified)
- Tested for OWASP Top 10 vulnerabilities

## Deployment Notes
[Important information for deployment]

- Database migration required: `npm run migrate`
- Feature flag: `ENABLE_FEATURE_X` (default: false)
- Environment variable: `API_TIMEOUT=5000`
- Backward compatible: Yes/No

## Rollback Plan
[If needed]

- Disable feature flag `ENABLE_FEATURE_X`
- Or: Revert commit abc123
- Or: Run rollback migration: `npm run migrate:down`

## Related Issues
Fixes #234
Relates to #456
Part of epic #789

## Questions for Reviewers
[Specific areas where you want feedback]

- Is the error handling approach appropriate?
- Should we add more test coverage for X?
- Any performance concerns with this implementation?

---

## Examples

### Example 1: Feature Addition

## Summary
Add user profile editing with avatar upload and real-time validation

## Motivation
User research shows 60% of users want to customize their profiles.
Adding profile editing reduces support tickets by allowing self-service updates.

Target metric: Reduce profile-related support tickets by 40%

## Changes
- Added profile edit form with real-time validation
- Implemented avatar upload with image cropping
- Added profile update API endpoint with rate limiting
- Updated user model with new fields (bio, location, website)

## Implementation Details
**Avatar Upload:**
- Used `multer` for file upload handling
- Implemented client-side image cropping with `react-easy-crop`
- Images stored in S3 with CDN caching
- Max file size: 5MB, formats: JPG, PNG
- Auto-generate thumbnails (100x100, 400x400)

**Validation:**
- Real-time validation using Zod schema
- Debounced input (500ms) to reduce API calls
- Username uniqueness check with 2s cache
- Email format validation with disposable email check

**Security:**
- Rate limiting: 10 profile updates per hour per user
- File upload validation (magic number check, not just extension)
- XSS prevention on bio field
- CSRF token required for updates

## Testing
- [x] Unit tests: Zod schemas, upload utils (coverage: 95%)
- [x] Integration tests: profile update API, file upload flow
- [x] E2E tests: full edit flow with Playwright
- [x] Manual testing: Tested on Chrome, Firefox, Safari, Mobile
- [x] Edge cases tested:
  - Large avatar upload (5MB+) -> Shows error
  - Invalid image format -> Shows error
  - Duplicate username -> Shows error
  - XSS attempt in bio -> Sanitized

## Screenshots
**Profile Edit Form:**
![Profile edit form](https://example.com/screenshots/edit-form.png)

**Avatar Cropping:**
![Avatar crop tool](https://example.com/screenshots/crop.png)

## Performance Impact
- Avatar upload: average 2.5s for 2MB image
- Profile save: average 120ms
- Added Redis caching for username uniqueness checks
- Database query optimized with index on users.username

## Security Considerations
- File upload validates magic numbers (not just extension)
- Bio field sanitized with DOMPurify to prevent XSS
- Rate limiting prevents abuse (10 updates/hour)
- CSRF token required for all update requests
- No PII logged in application logs

## Deployment Notes
**Database Migration Required:**
```bash
npm run migrate:profile-fields
```

Adds columns: bio (text), location (varchar), website (varchar), avatar_url (varchar)

**Environment Variables:**
```env
AWS_S3_BUCKET=user-avatars
AWS_S3_REGION=us-east-1
CDN_URL=https://cdn.example.com
```

**Feature Flag:**
- `ENABLE_PROFILE_EDIT` (default: false)
- Enable after successful staging verification

**Backward Compatible:** Yes (all new fields nullable)

## Rollback Plan
1. Disable feature flag: `ENABLE_PROFILE_EDIT=false`
2. Or rollback migration: `npm run migrate:down profile-fields`
3. Or revert commit: `git revert abc123`

## Related Issues
Fixes #234 (User profile editing)
Fixes #456 (Avatar upload)
Relates to #567 (Account settings redesign)
Part of epic #789 (User experience improvements)

## Questions for Reviewers
1. Should we add more image formats (WebP, AVIF)?
2. Is 10 updates/hour rate limit too strict?
3. Any concerns with S3 storage costs for avatars?
4. Should we add A/B testing for the new profile page?

---

### Example 2: Bug Fix

## Summary
Fix race condition in user registration causing duplicate accounts

## Motivation
Production issue: 0.5% of registrations create duplicate user accounts
when submitted multiple times rapidly (double-click, slow network retry).

Impact: 50 duplicate accounts per day, causing login failures and support tickets.

## Changes
- Added database unique constraint on users.email
- Implemented transaction handling for user creation
- Added idempotency key to registration API
- Improved error handling for duplicate email errors

## Implementation Details
**Root Cause:**
Registration endpoint didn't handle concurrent requests. When user double-clicked
"Sign Up" or network retried, two requests reached the server simultaneously
before the first user was committed to database.

**Fix:**
1. Database level: Added unique constraint on users.email (prevents duplicates)
2. Application level: Wrapped user creation in transaction
3. API level: Added idempotency key header (dedupe retries)

**Idempotency:**
```javascript
// Client sends: Idempotency-Key: uuid
// Server caches registration attempts for 24h
// Duplicate requests return original response
```

## Testing
- [x] Unit tests: transaction rollback, constraint violations
- [x] Integration tests: concurrent registration requests
- [x] Load tests: 100 concurrent registrations with same email
- [x] Manual tests: Double-click submit, network retry scenarios

**Test Results:**
- Before: 5/100 concurrent requests created duplicates
- After: 0/100 duplicates, proper error returned

## Performance Impact
- Negligible (< 5ms added latency for unique constraint check)
- Idempotency cache uses Redis (1MB memory for 1000 requests)

## Security Considerations
- Unique constraint prevents email enumeration attacks (same error for existing)
- Idempotency keys expire after 24h
- No rate limiting changes (existing 10 requests/hour remains)

## Deployment Notes
**Database Migration Required:**
```bash
npm run migrate:user-email-unique
```

**Migration Steps:**
1. Identify existing duplicates: `npm run fix:duplicate-users`
2. Manually resolve duplicates (merge or delete)
3. Run migration to add unique constraint
4. Deploy new code

**Downtime:** None (migration runs online)
**Backward Compatible:** Yes

**Monitoring:**
- Alert on duplicate email errors (expected during migration)
- Track idempotency cache hit rate

## Rollback Plan
1. Revert code deploy (keeps constraint, no duplicates)
2. Or drop constraint: `ALTER TABLE users DROP CONSTRAINT users_email_unique;`
   (Note: This allows duplicates again, not recommended)

## Related Issues
Fixes #789 (Duplicate user accounts)
Relates to #790 (Registration error handling)

## Questions for Reviewers
1. Should we add the same constraint to users.username?
2. Is 24h too long for idempotency key expiration?
3. Do we need to backfill idempotency keys for existing users?

---

## When to Use Each Section

### Always Include
- Summary
- Motivation
- Changes
- Testing
- Related Issues

### Include When Applicable
- Implementation Details (for complex changes)
- Screenshots (for UI changes)
- Performance Impact (if performance changed)
- Security Considerations (if security-related)
- Deployment Notes (if requires deployment steps)
- Rollback Plan (for risky changes)
- Questions for Reviewers (when you need specific feedback)

### Can Omit
- Screenshots (for backend-only changes)
- Performance Impact (for documentation changes)
- Security Considerations (for non-security changes)
- Deployment Notes (for fully backward-compatible changes)
- Rollback Plan (for low-risk changes like docs, tests)

---

## Copy-Paste Template

```markdown
## Summary


## Motivation


## Changes
-

## Implementation Details


## Testing
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots
[Delete if not applicable]

## Performance Impact
[Delete if not applicable]

## Security Considerations
[Delete if not applicable]

## Deployment Notes


## Rollback Plan


## Related Issues
Fixes #

## Questions for Reviewers
```
