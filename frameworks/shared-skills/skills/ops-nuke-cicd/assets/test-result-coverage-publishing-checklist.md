# Test Result and Coverage Publishing Checklist

- Verify each test target writes JUnit XML to `artifacts/`.
- Verify collector is set to `XPlat Code Coverage;Format=cobertura`.
- Verify raw coverage files exist under `artifacts/coverage-report/**/coverage.cobertura.xml`.
- Verify merge target runs after all required test targets.
- Verify ReportGenerator emits Cobertura + HTML summary into `artifacts/coverage-report`.
- Verify CI artifact collector paths match real output locations.
- Verify CI test-report parser includes all `*-test-result.xml` files.
- Verify failed tests still emit logs and partial results when possible.

