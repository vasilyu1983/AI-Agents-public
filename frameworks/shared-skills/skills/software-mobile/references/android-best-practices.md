# Android Best Practices

Comprehensive guide to Android development best practices for production applications.

---

## Architecture

**MVVM Pattern:**
- Use ViewModel for business logic
- StateFlow for observable state
- Repository pattern for data access
- Dependency injection with Hilt/Koin

**Clean Architecture:**
- Presentation Layer: UI + ViewModels
- Domain Layer: Use Cases + Business Logic
- Data Layer: Repositories + Network/Database

---

## State Management

**Best Practices:**
- `remember` for local UI state
- `ViewModel` for screen-level state
- `StateFlow` for observable state
- `collectAsState()` to observe in Composables

**State Scope:**
- Local: `remember { mutableStateOf() }`
- Screen-level: `ViewModel + StateFlow`
- Global: Singleton/Dependency Injection
- Persistent: DataStore, Room Database

---

## Concurrency

**Kotlin Coroutines:**
- Use `suspend` functions for async operations
- `viewModelScope` for ViewModel coroutines
- `lifecycleScope` for Activity/Fragment
- Handle cancellation with `try-finally`

**Flow:**
- Use `Flow` for streaming data
- Use `StateFlow` for state management
- Use `SharedFlow` for events
- Use `collectAsState()` in Composables

---

## Networking

**Retrofit:**
- Use `suspend` functions with Retrofit
- Handle errors with sealed classes
- Implement retry logic with interceptors
- Use Gson/Moshi for JSON parsing

**OkHttp:**
- Add logging interceptor for debugging
- Implement authentication interceptor
- Configure timeouts (30-60 seconds)
- Enable HTTP/2 and connection pooling

---

## Security

### Play Integrity API (Preferred — SafetyNet Deprecated)

SafetyNet Attestation is deprecated. Prefer Play Integrity API for device/app integrity signals; confirm any Google Play enforcement deadlines in current policy docs.

**Migration Steps:**

1. Remove SafetyNet dependencies from `build.gradle`
2. Add Play Integrity dependency (use the latest stable version)
3. Update server-side verification to decode Play Integrity tokens
4. Test with Play Integrity API Test app

```kotlin
// Play Integrity API usage
val integrityManager = IntegrityManagerFactory.create(context)

suspend fun requestIntegrityToken(nonce: String): IntegrityTokenResponse {
    val request = IntegrityTokenRequest.builder()
        .setNonce(nonce)
        .build()

    return integrityManager
        .requestIntegrityToken(request)
        .await()
}
```

**Key Differences from SafetyNet:**

- Returns encrypted token (decrypt server-side via Google API)
- Includes app licensing verdict, device integrity, and account details
- Rate limits apply — cache verdicts appropriately
- Requires Play Console project linking

**Credential Storage:**

- Use EncryptedSharedPreferences for tokens
- NEVER use plain SharedPreferences for sensitive data
- Use KeyStore for cryptographic keys

**Network Security:**

- Use HTTPS for all requests
- Consider certificate pinning only with a documented rotation and failure-mode plan (pinning can break connectivity)
- Use Network Security Config

**Permissions:**

- Request permissions at runtime (Android 6+)
- Explain why permissions are needed
- Handle permission denial gracefully

---

## Performance

### Jetpack Compose Performance (Version-Agnostic)

**Compose Optimization:**

- Prefer immutable UI state models; mark stable types with `@Immutable`/`@Stable` when appropriate
- Use `remember` for expensive computations and stable objects (e.g., formatters)
- Use `derivedStateOf` for computed state derived from other state
- Keep lambdas stable; avoid recreating callbacks in tight recomposition loops
- Use `LazyColumn`/`LazyRow` for large lists; set stable keys
- Avoid work in composition; move I/O to ViewModel + coroutines

**Lifecycle-safe collection:**

- Prefer `collectAsStateWithLifecycle()` for `Flow`/`StateFlow` to avoid collecting in the background

**Startup and scrolling:**

- Use Baseline Profiles and Macrobenchmark for repeatable startup/jank regressions
- Measure cold start and recomposition hotspots via Android Studio Profiler + Compose tooling

### Legacy Compose Optimization

**Compose Optimization:**

- Use `remember` to cache expensive computations
- Use `LazyColumn`/`LazyRow` for large lists
- Avoid recomposition with `key()`
- Use `derivedStateOf` for computed state

**Image Loading:**
- Use Coil or Glide for image loading
- Implement caching (memory + disk)
- Resize images before displaying
- Use placeholder/error images

**Memory Management:**
- Avoid memory leaks with `viewModelScope`
- Use LeakCanary for detection
- Cancel coroutines in `onCleared()`

---

## Testing

**Unit Tests:**
- Test ViewModels with JUnit
- Mock dependencies with Mockito/MockK
- Test coroutines with `runTest`
- Aim for 80%+ code coverage

**UI Tests:**
- Use Espresso for UI testing
- Test critical user flows
- Use Page Object pattern

**Compose Testing:**
- Use `composeTestRule`
- Test UI state changes
- Verify user interactions

---

## Accessibility

**TalkBack:**
- Add content descriptions to images
- Use semantic components
- Test with TalkBack enabled

**Text Scaling:**
- Support font scaling
- Use `sp` for text sizes
- Test at 200% font size

**Color Contrast:**
- Follow Material Design guidelines
- Support Dark Theme
- Ensure WCAG AA compliance

---

## Play Store Guidelines

**Submission Checklist:**

- [ ] Privacy policy URL
- [ ] Data safety section completed
- [ ] App signing configured
- [ ] Screenshots for all supported devices
- [ ] Age rating set correctly
- [ ] Target SDK meets current Google Play requirements (verify policy + deadlines)
- [ ] Play Integrity API integrated (SafetyNet removed)
- [ ] No crashes or ANRs
- [ ] Proper error handling

**Review Process:**
- Expect 1-3 day review time
- Test on multiple devices
- Use pre-launch reports

---

## Deployment

**Versioning:**
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Increment `versionCode` for each release
- Update `versionName` appropriately

**CI/CD:**
- Use GitHub Actions or Bitrise
- Automate builds and tests
- Deploy to internal/beta tracks first
- Gradual rollout to production

---

## References

For implementation details, see:
- `assets/kotlin/template-kotlin.md` - Full Android app template
- `assets/cross-platform/template-platform-patterns.md` - Platform patterns

---

This guide provides production-ready best practices for building secure, performant, and accessible Android applications.
