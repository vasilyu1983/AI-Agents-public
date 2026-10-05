# XcodeGen Resource Packaging

XcodeGen and other project generators can produce packaging failures that look like runtime bugs.

Common failure patterns:

- resource folders copied as malformed folder references
- unresolved build-setting placeholders in `Info.plist`
- bundle metadata pointing to an executable path that was never produced
- project generation drift after editing the generator spec but not regenerating the project

When installation fails with messages such as “missing bundle executable”:

1. inspect the generated project spec
2. inspect the built `.app`
3. verify `Info.plist` expansion
4. verify the executable file exists where the bundle metadata expects it

Do this before editing Swift or SwiftUI files.

## Resource packaging rules

- If the repo generates Xcode projects, inspect the generator spec before blaming Swift code.
- Wrong resource declarations can create bundles that build but do not install correctly.
- Resource-folder copies, malformed folder references, or unresolved build settings often surface as install-time failures, not compile-time failures.

## Project File Discovery

When a project uses XcodeGen with `sources: [path: AppName]`, all `.swift` files in that directory tree are auto-discovered — but only when the project is regenerated.

**Symptom:** `cannot find 'MyNewView' in scope` after creating a new Swift file, even though the file exists on disk.

**Fix:** Run the project's generation script (typically `scripts/generate-xcodeproj.sh`) or `xcodegen generate` directly. The `.xcodeproj/project.pbxproj` will be updated with the new file references.

**Common pattern:** After creating multiple new files in a feature directory, regenerate once, then build.

For repos managed directly through `.xcodeproj/project.pbxproj`, new Swift files may exist on disk but still be invisible to the build until they are added to the correct target membership. In that case, edit the project file or use Xcode to register the file before investigating feature code.
