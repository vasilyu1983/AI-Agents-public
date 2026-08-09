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

# Keep fields for serialization (Gson, Moshi, Kotlin Serialization)
-keepclassmembers class com.example.model.** {
    <fields>;
}

# Keep names for reflection without preventing shrinking
-keepnames class com.example.** { *; }

# Keep Kotlin Serialization generated serializers
-keepattributes *Annotation*
-keep class **$$serializer { *; }
-keepclassmembers class * {
    kotlinx.serialization.KSerializer serializer(...);
}
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

1. **Reproduce with debug first**: if the crash does not happen with `minifyEnabled false`, R8 is the cause.
2. **Enable R8 on debug temporarily**: set `isMinifyEnabled = true` on the debug build type to iterate faster without signing/alignment overhead.
3. **Print usage**: add `-printusage usage.txt` to `proguard-rules.pro` — R8 writes every removed class and member to this file. Search for the missing class.
4. **Print seeds**: add `-printseeds seeds.txt` — R8 writes every class and member matched by keep rules. Verify your keep rule actually matches.
5. **Print configuration**: add `-printconfiguration full-config.txt` — R8 writes the merged configuration from all consumer rule files. Check for conflicting rules.

## R8 Full Mode vs Compatibility Mode

AGP 8.0+ uses R8 full mode by default. Full mode is more aggressive:

- Removes more unused code, including classes only referenced in keep rules that are never instantiated.
- Does not preserve `Enum.values()` for unused enums.
- Strips `SourceFile` and `LineNumberTable` attributes by default.

To fall back to compatibility mode (less aggressive, matches old ProGuard behavior):

```properties
# gradle.properties
android.enableR8.fullMode=false
```

Use compatibility mode as a diagnostic step. If the crash disappears, the issue is a missing keep rule that full mode exposes.

## Common Libraries Requiring Keep Rules

| Library | Why | Rule Source |
|---------|-----|-------------|
| **Retrofit** | Generic type erasure breaks converter factories | Retrofit ships consumer rules, but custom `Call` adapters may need explicit keeps |
| **Gson** | Field name mapping via reflection | `@SerializedName` fields need `-keepclassmembers`; or migrate to Moshi/Kotlin Serialization |
| **Moshi** | Kotlin reflection adapter reads constructor params | Moshi-kotlin-codegen (KSP) avoids this; reflection adapter needs keep rules |
| **Room** | DAO interfaces and entity classes referenced via annotation processing | Room ships consumer rules, but `@TypeConverter` methods in separate modules may need keeps |
| **Hilt / Dagger** | Generated components and inject constructors | Hilt ships consumer rules; custom `@AssistedFactory` implementations occasionally need keeps |
| **Kotlin Serialization** | Compiler-generated `$serializer` classes | Keep rules in the serialization runtime, but plugin-generated code for external models may need explicit keeps |
| **Navigation Safe Args** | Generated `Directions` and `Args` classes | Usually safe, but custom `NavType` implementations need keeps |

When adding a new library, check its documentation for required ProGuard/R8 rules. Most modern libraries ship consumer rules via `META-INF/proguard/` in their AARs.

## kotlinx-serialization + R8 Full Mode

AGP 8.x defaults R8 to **full mode**, which is more aggressive than compatibility mode and more reliant on correct keep rules. kotlinx-serialization 1.9.0+ interacts with full mode in ways that matter:

### Symptoms

- Release-only crash: `kotlinx.serialization.SerializationException: Serializer for class 'MyData' is not found. Please ensure that class is marked as '@Serializable' and that the serialization compiler plugin is applied.`
- Release-only crash: `java.lang.ExceptionInInitializerError` during the first deserialization after app start.
- Release-only crash with Ktor or Retrofit: serializer lookup falls back to reflection, and R8 has stripped the generated `$serializer` companion.
- R8 build-time warning mentioning a rule like `<1>$*` — the kotlinx-serialization consumer rules use a field-rule syntax whose characters are legal for the JVM but unusual at the source level, and R8 warns on it. The warning is informational from kotlinx-serialization 1.9.0 onward; it does not block the build but can mask real rule failures.

Primary sources: [kotlinx.serialization issue #3033](https://github.com/Kotlin/kotlinx.serialization/issues/3033), [kotlinx.serialization issue #2385](https://github.com/Kotlin/kotlinx.serialization/issues/2385), [Android Developers Blog: Configure and troubleshoot R8 Keep Rules (Nov 2025)](https://android-developers.googleblog.com/2025/11/configure-and-troubleshoot-r8-keep-rules.html).

### Canonical keep rules

kotlinx-serialization ships consumer rules that cover most cases, but R8 full mode can still strip third-party `@Serializable` classes the runtime reaches via reflection. Add these to `proguard-rules.pro` when you see the symptoms above:

```proguard
# Keep the generated $serializer companion for every @Serializable class in the app module
-if @kotlinx.serialization.Serializable class **
-keepclassmembers class <1> {
    *** Companion;
}
-if @kotlinx.serialization.Serializable class ** {
    static ** Companion;
}
-keepclassmembers class <2> {
    kotlinx.serialization.KSerializer serializer(...);
}

# Keep the generated $serializer classes themselves
-if @kotlinx.serialization.Serializable class **
-keep class <1>$$serializer { *; }

# Keep enum values referenced by @Serializable enums (R8 full mode strips Enum.values() for unused enums)
-keepclassmembers @kotlinx.serialization.Serializable class * extends java.lang.Enum {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Verification workflow

1. Enable R8 temporarily on the debug build type (see "Debugging R8 Issues" above) so you can reproduce the crash without signing overhead.
2. Add `-printusage usage.txt` and rebuild. Search `usage.txt` for the `@Serializable` class that crashed — if it appears, R8 removed it.
3. Add the keep rule above, rebuild, and re-verify with `-printseeds seeds.txt` that the rule actually matches.
4. Add a CI smoke test that runs the **release** variant on an emulator and exercises at least one endpoint per `@Serializable` class. A unit test cannot catch this because unit tests run on the JVM without R8.
5. Archive `mapping.txt` for every release so any `SerializationException` stack traces are retraceable.

### Kotlin 2.3+ improvement: Compose stack traces in R8 output

Starting with Kotlin 2.3.0, the Kotlin compiler emits ProGuard mapping entries for Compose composables, so R8-minified crash stack traces show readable composable names after `retrace`. Before 2.3, composable frames in minified stack traces were opaque. If you are still on Kotlin 2.2 or earlier and need readable Compose stack traces, upgrading Kotlin is the fastest win. Source: [kotlinlang.org/docs/whatsnew23.html](https://kotlinlang.org/docs/whatsnew23.html).
