# ProGuard/R8 Triage

## Table of Contents

- [When R8 Is Active](#when-r8-is-active)
- [Common Runtime Errors from R8 Stripping](#common-runtime-errors-from-r8-stripping)
- [Keep Rules](#keep-rules)
- [Mapping File Usage](#mapping-file-usage)
- [Debugging R8 Issues](#debugging-r8-issues)
- [R8 Full Mode vs Compatibility Mode](#r8-full-mode-vs-compatibility-mode)
- [Common Libraries Requiring Keep Rules](#common-libraries-requiring-keep-rules)
- [kotlinx-serialization + R8 Full Mode](#kotlinx-serialization--r8-full-mode)

## When R8 Is Active

R8 is the default code shrinker and obfuscator for Android. It runs when `minifyEnabled true` is set in a build type:

```kotlin
buildTypes {
    release {
        isMinifyEnabled = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

**Debug builds** have `minifyEnabled false` by default. If a crash happens only in release, R8 stripping is the first suspect.

To temporarily enable R8 on debug builds for testing:

```kotlin
debug {
    isMinifyEnabled = true
    proguardFiles(
        getDefaultProguardFile("proguard-android-optimize.txt"),
        "proguard-rules.pro"
    )
}
```

## Common Runtime Errors from R8 Stripping

| Error | Likely Cause |
|-------|-------------|
| `ClassNotFoundException` | R8 removed an entire class not referenced statically |
| `NoSuchMethodError` | R8 removed or renamed a method accessed via reflection |
| `NoSuchFieldError` | R8 removed a field accessed via serialization or reflection |
| `JsonSyntaxException` / `JsonParseException` | R8 renamed fields that Gson/Moshi maps by name |
| Retrofit call returns null or wrong type | R8 removed generic type information needed for converter |
| Reflection-based DI fails silently | R8 removed constructors or factory methods |

## Keep Rules

Add keep rules to `proguard-rules.pro` (project level) or the library's consumer rules:

```proguard
# Keep an entire class
-keep class com.example.model.User { *; }

# Keep all implementations of an interface
-keep class * implements com.example.api.ApiService { *; }

# Illustrative reflection-field rule: restrict to fields actually reflected on
-keepclassmembers class com.example.model.** {
    <fields>;
}

# Keep names for reflection without preventing shrinking
-keepnames class com.example.** { *; }

```

## Mapping File Usage

R8 produces `mapping.txt` at `app/build/outputs/mapping/<variant>/mapping.txt`. This file maps obfuscated names back to original names.

**Retrace a stack trace**:

```bash
# Using the Android SDK retrace tool
$ANDROID_HOME/cmdline-tools/latest/bin/retrace mapping.txt stacktrace.txt

# Or using the R8 retrace jar directly
java -jar r8.jar retrace mapping.txt stacktrace.txt
```

**Archive every release mapping file**: without the matching `mapping.txt`, crash reports from a release build are unreadable. Store it alongside the APK/AAB in your release artifacts.

**Firebase Crashlytics**: upload the mapping file automatically by applying the `com.google.firebase.crashlytics` Gradle plugin. For manual upload: Firebase Console > Crashlytics > Upload mapping file.

**Google Play Console**: upload `mapping.txt` alongside each AAB in the Play Console for deobfuscated crash reports.

## Debugging R8 Issues

1. **Compare controlled variants**: disable minification in the same release-like configuration. A debug/release difference alone cannot isolate R8 because flags, signing and endpoints may differ.
2. **Enable R8 on debug temporarily**: set `isMinifyEnabled = true` on the debug build type to iterate faster without signing/alignment overhead.
3. **Print usage**: add `-printusage usage.txt` to `proguard-rules.pro` — R8 writes every removed class and member to this file. Search for the missing class.
4. **Print seeds**: add `-printseeds seeds.txt` — R8 writes every class and member matched by keep rules. Verify your keep rule actually matches.
5. **Print configuration**: add `-printconfiguration full-config.txt` — R8 writes the merged configuration from all consumer rule files. Check for conflicting rules.

## R8 Full Mode vs Compatibility Mode

AGP 8.0+ uses R8 full mode by default. Full mode is more aggressive:

- Removes more unused code, including classes only referenced in keep rules that are never instantiated.
- Does not preserve `Enum.values()` for unused enums.
- Attribute retention depends on resolved R8/AGP, reachability and keep rules; check the [R8 FAQ](https://r8.googlesource.com/r8/+/refs/heads/main/compatibility-faq.md) rather than assuming a blanket removal.

To fall back to compatibility mode (less aggressive, matches old ProGuard behavior):

```properties
# gradle.properties
android.enableR8.fullMode=false
```

Where the resolved AGP still supports this flag, use it only as an isolation step. A changed result implicates optimization configuration; inspect the merged rules and stack before concluding a specific missing keep.

## Common Libraries Requiring Keep Rules

| Library | Why | Rule Source |
|---------|-----|-------------|
| **Retrofit** | Generic type erasure breaks converter factories | Retrofit ships consumer rules, but custom `Call` adapters may need explicit keeps |
| **Gson** | Field name mapping via reflection | `@SerializedName` fields need `-keepclassmembers`; or migrate to Moshi/Kotlin Serialization |
| **Moshi** | Kotlin reflection adapter reads constructor params | Moshi-kotlin-codegen (KSP) avoids this; reflection adapter needs keep rules |
| **Room** | DAO interfaces and entity classes referenced via annotation processing | Room ships consumer rules, but `@TypeConverter` methods in separate modules may need keeps |
| **Hilt / Dagger** | Generated components and inject constructors | Hilt ships consumer rules; custom `@AssistedFactory` implementations occasionally need keeps |
| **Kotlin Serialization** | Serializer discovery, particularly named companions | Library supplies consumer rules; use its documented named-companion additions when applicable |
| **Navigation Safe Args** | Generated `Directions` and `Args` classes | Usually safe, but custom `NavType` implementations need keeps |

When adding a new library, check its documentation for required ProGuard/R8 rules. Most modern libraries ship consumer rules via `META-INF/proguard/` in their AARs.

## kotlinx-serialization + R8 Full Mode

For release-only `SerializationException` or initialization failures:

1. Verify that the serialization compiler plugin matches the Kotlin compiler and is applied to the model's module; inspect the runtime dependency actually resolved.
2. Read the merged consumer configuration (`-printconfiguration`). [Serialization's Android guidance](https://github.com/Kotlin/kotlinx.serialization/blob/master/README.md#android) says its library supplies rules for retained serializable classes. Named companion objects require the documented mode-specific additions; scope them to those model classes.
3. Compare the same release-like build with minification disabled, then inspect `-printusage` / `-printseeds` for the failing class and discovery path. Add the smallest rule that the reproducer demonstrates is needed; do not paste a blanket keep of all serializers.
4. Exercise the failing serialization paths in a minified-variant device test and archive the matching `mapping.txt`; ordinary JVM unit tests do not execute Android's R8 output.

## Compose Group-Key Stack Traces

[Kotlin 2.3.0](https://kotlinlang.org/docs/whatsnew23.html#compose-compiler-stack-traces-for-minified-android-applications) adds group-key ProGuard mappings. The diagnostic mode also needs Compose runtime 1.10 or newer and `Composer.setDiagnosticStackTraceMode(ComposeStackTraceMode.GroupKeys)` before composable content. Archive and retrace the matching mapping to interpret the appended Compose frames; upgrading Kotlin alone does not enable the mode. Check the resolved toolchain's API/opt-in requirements before adding the call.
