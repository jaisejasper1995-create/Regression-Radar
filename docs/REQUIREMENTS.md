# Regression Radar v0.1.0 — Requirements Baseline

**Project:** Regression Radar
**Phase:** 1 — Engineering Baseline
**Status:** Proposed baseline; pending review and verification
**Scope:** Local-first deterministic JUnit XML regression analysis

## 1. Purpose

Regression Radar compares two automated test reports and identifies changes in test outcomes between a baseline execution and a current execution.

The primary objective is to identify new regressions reliably without confusing skipped, missing, or newly introduced tests with confirmed fixes.

## 2. Functional Requirements

### RR-001 — Input reports

The tool shall accept exactly two report paths: baseline and current.

### RR-002 — Supported format

Version 0.1.0 shall support JUnit-style XML containing `testsuite` or `testsuites` roots, including multiple test suites.

### RR-003 — Secure parsing

The tool shall use hardened XML parsing and reject prohibited XML constructs, malformed documents, and inputs exceeding documented resource limits.

### RR-004 — Test identification

Test identity shall be based on the test case's `classname` and `name` attributes, with an explicit normalization policy.

Test identity must not depend on XML element ordering.

### RR-005 — Duplicate identities

Duplicate normalized identities within one report shall be rejected rather than silently overwritten.

### RR-006 — Outcome normalization

Each test case shall be normalized to one of four statuses:

- PASS
- FAIL
- ERROR
- SKIP

A testcase containing multiple conflicting outcome markers shall be rejected.

### RR-007 — New regressions

A transition from PASS to FAIL or ERROR shall be classified as a new regression.

### RR-008 — Resolved failures

A transition from FAIL or ERROR to PASS shall be classified as resolved.

### RR-009 — Persistent failures

Tests that fail or error in both runs shall be reported as persistent failures, with the original and current statuses preserved.

### RR-010 — Unchanged passes

Tests passing in both reports shall be classified as unchanged passes.

### RR-011 — Newly introduced tests

Tests present only in the current report shall be reported as added tests, not automatically classified as regressions or fixes.

### RR-012 — Missing tests

Tests present only in the baseline report shall be reported as missing tests, not as resolved failures.

### RR-013 — Skipped tests

Transitions involving SKIP shall be reported separately.

A previously failing test that becomes skipped must not be classified as fixed.

### RR-014 — Deterministic comparison

Identical inputs shall produce identical classification results regardless of testcase ordering.

### RR-015 — Summary totals

The tool shall report:

- Baseline test count
- Current test count
- New regressions
- Resolved failures
- Persistent failures
- Unchanged passes
- Added tests
- Missing tests
- Skip-related transitions

### RR-016 — Text reporting

The CLI shall provide a readable summary, including individual test identifiers for important changes.

### RR-017 — JSON reporting

The CLI shall support a machine-readable JSON report with documented field names and stable structure.

### RR-018 — CLI exit codes

The proposed exit-code contract is:

| Code | Meaning |
|---|---|
| 0 | Valid comparison, no new regressions |
| 1 | Valid comparison, one or more new regressions |
| 2 | Invalid input, parsing failure, or execution error |

Missing tests and skip transitions shall be visible in the report; stricter policies may be considered after v0.1.0.

### RR-019 — Error reporting

The tool shall produce predictable, actionable error messages without misleading PASS results.

### RR-020 — Reproducibility

Equivalent inputs shall yield equivalent reports. Unnecessary timestamps, random identifiers, or environment-specific values shall not affect comparison output.

## 3. Nonfunctional Requirements

### RR-021 — Python compatibility

Target Python 3.11, 3.12, and 3.13.

### RR-022 — Local-first operation

Version 0.1.0 shall run locally without requiring cloud services, accounts, or API keys.

### RR-023 — Input preservation

Input reports shall not be modified by comparison operations.

### RR-024 — Resource protection

The parser shall enforce a documented maximum input-file size and reject excessively large inputs before parsing.

### RR-025 — Dependency control

Runtime dependencies shall be declared in project packaging configuration.

### RR-026 — Automated verification

Functional requirements shall have traceable positive, negative, or adversarial test coverage where applicable.

### RR-027 — CI verification

GitHub Actions shall execute automated tests, static analysis, and an installed-CLI smoke test.

### RR-028 — Clean installation

The release package shall be installed and tested in an isolated environment.

### RR-029 — Release evidence

Test results, limitations, security-scan outcomes, packaging checks, and release commits shall be documented.

### RR-030 — Human approval

Public publication and release tagging require explicit approval from the project owner.

## 4. Out of Scope for v0.1.0

- Graphical dashboards
- AI-generated root-cause explanations
- Cloud storage
- Automatic GitHub issue creation
- Historical trend databases
- Automatic test execution
- Self-healing or automatic code modification
- Full support for every vendor-specific JUnit XML extension
- Performance benchmarking and load testing

## 5. Engineering Rules

1. No requirement is marked PASS without recorded evidence.
2. Failed tests must be investigated rather than weakened.
3. Actual results must remain separate from expected results.
4. All detected regressions must remain visible in reports.
5. No silent dropping of invalid or ambiguous test results.
6. Changes in requirements require review and documented approval.
7. The frozen v0.1.0 scope takes priority over additional features.
8. Project progress shall use PASS, FAIL, BLOCKED, and NOT RUN accurately.

## 6. Phase 1 Acceptance Criteria

Phase 1 is complete only when:

- Requirements have been reviewed and approved.
- Architecture and interfaces are documented.
- Test identities and status-transition rules are frozen.
- Test matrix maps to requirements.
- Project structure and environment are verified.
- Initial Git baseline is preserved.
- No unverified functionality is represented as implemented.

## 7. Current Verification State

**Project structure:** Prepared; visually reviewed.
**Python and Git availability:** Verified through terminal screenshots.
**Requirements implementation:** NOT RUN.
**Automated tests:** NOT RUN.
**Production code:** NOT STARTED.
**Release:** NOT STARTED.

---

**Engineering principle:** Test the claim — not just the demo.
