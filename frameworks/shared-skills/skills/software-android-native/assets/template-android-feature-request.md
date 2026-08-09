# Android Feature Request Template

Implement one bounded native Android slice.

## Goal

- Feature:
- User-visible outcome:

## Repo facts

- App module path:
- Build variant:
- Package name:
- Relevant screen or flow:

## Constraints

- Minimum API level:
- Must preserve:
- Out of scope:

## Execution requirements

- Build with `./gradlew :app:assembleDebug` (or configured variant).
- Install with `adb install -r` on the target emulator or device.
- Launch and verify the intended screen.
- Capture one screenshot or UI hierarchy for visual changes.
- Run the smallest relevant automated test scope.

## Report back with

- changed behavior
- validation performed
- residual risks
- any new data safety, permissions, or SDK implications
