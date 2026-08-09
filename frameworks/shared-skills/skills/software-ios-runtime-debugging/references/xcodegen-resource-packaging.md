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
