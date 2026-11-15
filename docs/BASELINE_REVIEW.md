# Regression Radar v0.1.0 — Phase 1 Baseline Review

**Status:** Proposed for owner approval
**Phase:** 1 — Engineering Baseline
**Implementation:** NOT STARTED

## Review Scope

This review compares the drafted requirements, architecture, test matrix, and project status.

The review assesses specification consistency. It does not constitute production-code validation or an automated test execution.

## Confirmed Design Decisions

1. Input: Two JUnit XML test reports.
2. Test identity: Exact `(classname, name)` pair.
3. Outcomes: PASS, FAIL, ERROR, SKIP.
4. New regression: PASS to FAIL or ERROR.
5. Resolved failure: FAIL or ERROR to PASS.
6. Persistent failure: FAIL or ERROR in both reports.
7. Added tests and missing tests remain separate classifications.
8. Skipped tests never count as confirmed fixes.
9. Invalid or ambiguous XML must be rejected.
10. Identical normalized inputs must produce identical comparison results.
11. Reports must support text and JSON output.
12. CLI exit codes: 0 for no new regressions, 1 for new regressions, 2 for invalid input or execution errors.

## Clarification A — Skip Accounting

The comparison summary shall maintain separate counts for:

- Unchanged skips: SKIP to SKIP.
- Skip-related transitions: SKIP to or from a different outcome.

Both categories shall be included in total classification reconciliation.

The test matrix shall verify these categories separately.

## Clarification B — JUnit Summary Attributes

The authoritative counts shall be derived from normalized testcase records.

Producer-supplied summary attributes are informational and shall not override the parsed testcase counts.

Compatibility limitations shall be documented.

## Requirements Coverage

Thirty requirements and 93 planned verification scenarios have been documented.

The matrix includes the 16 normalized outcome transitions, added and missing tests, parser validation, adversarial cases, CLI behavior, packaging, and release checks.

These are planned checks, not completed test executions.

## Current Evidence

- Project structure: Verified
- Python and Git: Available
- Requirements: Documented
- Architecture: Documented
- Test matrix: Documented
- Project status: Documented
- Production tests: NOT RUN
- Implementation: NOT STARTED
- Initial baseline commit: PENDING

## Approval Gate

Approval freezes the Phase 1 specification, including the clarifications above, as the baseline for v0.1.0 implementation.

Subsequent requirement changes must be documented and reviewed.

**Engineering principle:** Test the claim — not just the demo.
