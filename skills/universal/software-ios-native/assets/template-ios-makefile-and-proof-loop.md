# iOS Makefile and Proof Loop Template

Use one command surface for agents and humans.

## Makefile Shape

```makefile
SCHEME ?= MyApp
DESTINATION ?= platform=iOS Simulator,name=iPhone 16 Pro,OS=latest
RESULT_BUNDLE ?= build/TestResults.xcresult

.PHONY: build test archive clean

build:
	xcodebuild build -scheme $(SCHEME) -destination '$(DESTINATION)'

test:
	rm -rf $(RESULT_BUNDLE)
	xcodebuild test -scheme $(SCHEME) -destination '$(DESTINATION)' -resultBundlePath $(RESULT_BUNDLE)

archive:
	xcodebuild archive -scheme $(SCHEME) -destination 'generic/platform=iOS'

clean:
	xcodebuild clean -scheme $(SCHEME)
```

Add `xcbeautify` when available, but keep a plain `xcodebuild` fallback.

## Proof Loop

1. `make build`
2. inspect destination and bundle ID
3. uninstall stale app from simulator or device
4. install fresh build
5. launch and capture screenshot/log marker
6. `make test`
7. archive before release claims

For Xcode Cloud, commit generated files or regenerate them in `ci_scripts/ci_post_clone.sh`.
