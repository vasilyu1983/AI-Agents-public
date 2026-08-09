# Android Proof Checklist

- [ ] The module path, build variant, and package name were verified rather than guessed.
- [ ] Emulator or device availability was checked before relying on install and launch.
- [ ] Any volatile claim was backed by a primary source checked recently.
- [ ] The implementation built successfully in the intended configuration.
- [ ] The app installed and launched on the intended emulator or device.
- [ ] A user-facing proof artifact exists for UI changes (screenshot or UI hierarchy).
- [ ] The smallest relevant automated test scope was executed or explicitly deferred.
- [ ] Data safety, permissions, and third-party SDK implications were reviewed.
- [ ] ProGuard/R8 rules were verified for release builds if applicable.
- [ ] Residual risks were reported explicitly.
