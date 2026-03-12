# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New features that have been added but not yet released

### Changed

- Changes to existing functionality

### Deprecated

- Features that are marked for removal in upcoming releases

### Removed

- Features that have been removed

### Fixed

- Bug fixes

### Security

- Security patches and improvements

## [2.1.0] - 2025-01-20

### Added

- User profile avatars with upload functionality (#234)
- Dark mode support across all pages (#245)
- Export data to CSV feature in admin dashboard (#256)
- Rate limiting middleware (100 req/min per user) (#267)
- GraphQL subscriptions for real-time updates (#278)

### Changed

- Updated Node.js from 18.x to 20.x LTS (#289)
- Migrated from REST to GraphQL for user queries (breaking change) (#290)
- Improved database query performance by 40% with optimized indexes (#301)
- Refactored authentication flow to use JWT refresh tokens (#312)

### Deprecated

- `/api/v1/users/search` endpoint (use GraphQL `users` query instead)
- XML response format (will be removed in v3.0.0)

### Security

- Updated `jsonwebtoken` to 9.0.2 to fix CVE-2025-XXXX (#323)
- Implemented Content Security Policy headers (#334)
- Added CSRF protection to all state-changing endpoints (#345)

## [2.0.0] - 2024-12-15

### Added

- Multi-tenancy support with organization isolation (#123)
- Two-factor authentication via TOTP (#134)
- Comprehensive audit logging for compliance (#145)
- Webhook integration system for third-party apps (#156)
- New `/api/v2/reports` endpoint for generating analytics reports (#167)

### Changed

- **BREAKING:** Minimum Node.js version is now 18.x (was 16.x)
- **BREAKING:** Database schema migration required (see migration guide)
- **BREAKING:** API authentication now requires Bearer token (removed API key support)
- Redesigned user interface with Material Design components
- Improved error messages with more context and troubleshooting steps
- Database connection pooling increased from 10 to 50 connections

### Removed

- **BREAKING:** Legacy XML API endpoints (deprecated in v1.5.0)
- **BREAKING:** Support for IE11 browser
- Unused `oldFeature` configuration option
- Deprecated `/api/v1/legacy/users` endpoint

### Fixed

- Memory leak in WebSocket connection handler (#178)
- Race condition in concurrent order processing (#189)
- Incorrect timezone handling for scheduled reports (#190)
- SQL injection vulnerability in search endpoint (CVE-2024-XXXX) (#201)

### Security

- Migrated password hashing from bcrypt to Argon2id (#212)
- Implemented rate limiting to prevent brute force attacks (#223)
- Added automated security scanning in CI/CD pipeline (#234)

## [1.5.0] - 2024-10-01

### Added

- Email notification system with templating (#89)
- User preferences page for customization (#90)
- Bulk import/export functionality for admin users (#91)
- API documentation with interactive Swagger UI (#92)

### Changed

- Updated all dependencies to latest versions
- Improved test coverage from 75% to 90%
- Enhanced logging with structured JSON format

### Deprecated

- XML API endpoints (use JSON instead, will be removed in v2.0.0)

### Fixed

- Pagination bug returning duplicate results (#93)
- Date formatting inconsistency across timezones (#94)
- File upload failing for files >10MB (#95)

## [1.4.1] - 2024-09-15

### Fixed

- Critical hotfix: Database connection pool exhaustion under high load (#81)
- User session expiring prematurely (#82)
- Incorrect currency conversion in checkout (#83)

### Security

- Updated `express` to 4.18.2 to address ReDoS vulnerability (#84)

## [1.4.0] - 2024-09-01

### Added

- Search functionality with full-text search (#67)
- User activity dashboard with charts (#68)
- API versioning support (v1 and v2 endpoints) (#69)

### Changed

- Improved Docker image size (reduced by 40%) (#70)
- Optimized database queries for better performance (#71)

### Fixed

- Login redirect loop for certain edge cases (#72)
- Broken pagination on user list page (#73)

## [1.3.0] - 2024-08-01

### Added

- OAuth2 authentication with Google and GitHub (#45)
- User roles and permissions system (#46)
- Automated database backups to S3 (#47)

### Changed

- Migrated from MongoDB to PostgreSQL (#48)
- Updated UI framework from Bootstrap 4 to Bootstrap 5 (#49)

### Fixed

- Performance issues with large dataset exports (#50)
- CORS configuration blocking valid requests (#51)

## [1.2.0] - 2024-07-01

### Added

- RESTful API with JWT authentication (#23)
- File attachment support for user profiles (#24)
- Admin panel for user management (#25)

### Changed

- Improved error handling with better error messages (#26)
- Updated branding and logo (#27)

### Fixed

- Form validation errors not displaying correctly (#28)
- Email delivery failures for certain providers (#29)

## [1.1.0] - 2024-06-01

### Added

- User registration and login functionality (#12)
- Password reset via email (#13)
- Basic user profile management (#14)

### Fixed

- Database migration script errors (#15)
- Broken CSS on mobile devices (#16)

## [1.0.0] - 2024-05-01

### Added

- Initial release of the application
- Basic CRUD operations for resources
- PostgreSQL database integration
- Express.js REST API
- User authentication with JWT
- Docker deployment configuration
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new features (backward-compatible)
- **PATCH** version for bug fixes (backward-compatible)

## Categories

- **Added:** New features
- **Changed:** Changes to existing functionality
- **Deprecated:** Features marked for removal
- **Removed:** Removed features
- **Fixed:** Bug fixes
- **Security:** Security patches and improvements

## Issue References

Each change includes a reference to the related issue/PR number (e.g., #123).

## Links

[Unreleased]: https://github.com/username/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/username/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/username/repo/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/username/repo/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/username/repo/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/username/repo/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/username/repo/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/username/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/username/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/username/repo/releases/tag/v1.0.0
