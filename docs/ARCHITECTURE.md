# Regression Radar v0.1.0 — Architecture Baseline

**Project:** Regression Radar
**Phase:** 1 — Engineering Baseline
**Status:** Proposed architecture, pending review
**Requirements reference:** docs/REQUIREMENTS.md
**Implementation status:** NOT STARTED

---

## 1. System Overview

Regression Radar is a local-first Python command-line application that compares two JUnit XML test reports.

Its purpose is to detect changes in test outcomes while avoiding misleading conclusions about missing, skipped, or ambiguous tests.

The architecture separates input validation, XML parsing, outcome normalization, comparison, reporting, and CLI behavior.

## 2. Processing Pipeline

```text
BASELINE XML          CURRENT XML
      |                    |
      v                    v
 Secure XML Parser    Secure XML Parser
      |                    |
      v                    v
 Normalized Cases     Normalized Cases
      |                    |
      +---------+----------+
                |
                v
       Comparison Engine
                |
                v
       Classified Changes
                |
         +------+------+
         |             |
         v             v
      Text Report   JSON Report
         |             |
         +------+------+
                |
                v
          CLI Exit Code
```

Each component shall be testable independently.

## 3. Proposed Project Modules

### `models.py`

Defines immutable data structures for normalized test cases, comparison results, and summaries.

Suggested structures:

- `TestCase`
- `TestOutcome`
- `TestTransition`
- `ComparisonSummary`
- `ComparisonReport`

Normalized statuses:

- PASS
- FAIL
- ERROR
- SKIP

### `parser.py`

Responsible for secure XML input handling.

Responsibilities:

- Read local XML files.
- Enforce a maximum file size.
- Parse XML using defusedxml.
- Accept supported JUnit-style root structures.
- Extract test-case attributes and outcomes.
- Reject invalid or ambiguous records.
- Detect duplicate test identities.
- Return normalized test cases.

The parser must never modify input files.

### `comparison.py`

Responsible for comparing normalized baseline and current test cases.

Responsibilities:

- Match tests by stable identity.
- Detect changed outcomes.
- Classify added and missing tests.
- Preserve original and current statuses.
- Produce deterministic comparison results.
- Calculate summary counts.

The comparison engine must not perform filesystem operations or make network requests.

### `reporting.py`

Responsible for producing human-readable and machine-readable reports.

Responsibilities:

- Text summaries.
- JSON serialization.
- Stable field names.
- Deterministic ordering.
- Clear display of failures and missing tests.

### `cli.py`

Responsible for command-line argument handling and process exit codes.

The CLI coordinates the parser, comparison engine, and reporting components.

### `__main__.py`

Provides support for running the tool through:

`python -m regression_radar`

## 4. Test Identity Policy

Each test must have a stable identity.

For v0.1.0, identity consists of:

`(classname, name)`

Rules:

1. Both attributes must exist and be nonempty.
2. Attribute values are preserved exactly after XML decoding.
3. Case, internal whitespace, and punctuation remain significant.
4. No lowercasing, trimming, or other implicit normalization is performed.
5. XML test-case ordering does not affect identity.
6. Duplicate identities within a single report are rejected.
7. Test-suite names are not automatically added to identity.
8. An ambiguous identity produces an explicit input error.

This is the initial strict identity policy. Reports that omit `classname` will not be supported in v0.1.0 unless the requirements are formally revised.

## 5. Outcome Normalization

A test case with no failure, error, or skipped child element is classified as PASS.

A test case containing a failure element is classified as FAIL.

A test case containing an error element is classified as ERROR.

A test case containing a skipped element is classified as SKIP.

A testcase containing multiple outcome markers, including repeated markers of the same type, is rejected as ambiguous.

Unknown vendor-specific testcase children may be ignored only when they do not affect the normalized outcome.

## 6. Classification Rules

Every test identity in the union of baseline and current reports must receive exactly one comparison classification.

| Baseline | Current | Classification |
|---|---|---|
| PASS | PASS | Unchanged pass |
| PASS | FAIL | New regression |
| PASS | ERROR | New regression |
| FAIL | PASS | Resolved failure |
| ERROR | PASS | Resolved failure |
| FAIL | FAIL | Persistent failure |
| FAIL | ERROR | Persistent failure |
| ERROR | FAIL | Persistent failure |
| ERROR | ERROR | Persistent failure |
| SKIP | SKIP | Unchanged skip |
| PASS | SKIP | Skip-related transition |
| FAIL | SKIP | Skip-related transition |
| ERROR | SKIP | Skip-related transition |
| SKIP | PASS | Skip-related transition |
| SKIP | FAIL | Skip-related transition |
| SKIP | ERROR | Skip-related transition |
| Absent | Any status | Added test |
| Any status | Absent | Missing test |

An absent test is different from a skipped test.

A FAIL-to-ERROR transition is persistent failure, with both statuses retained.

A SKIP-to-FAIL transition is explicitly visible but is not silently classified as a PASS-to-FAIL regression.

## 7. Deterministic Comparison

Given the same normalized inputs, the comparison engine must produce equal results.

Requirements:

- No timestamps generated during comparison.
- No randomly generated identifiers.
- No dependence on dictionary or XML ordering.
- Stable sorting by test identity.
- Stable classification and summary rules.
- No hidden mutation of input structures.

The baseline and current states must remain distinguishable.

## 8. Input Security

The XML parser will use defusedxml.

Initial resource limits:

- Maximum file size: 5 MiB per report.
- Maximum normalized test cases: 100,000 per report.
- Reject malformed XML.
- Reject prohibited entity or document-type constructs.
- Reject duplicate identities.
- Reject missing required identity attributes.
- Reject conflicting outcome markers.
- Reject documents containing no test cases.

These limits are design requirements, not verified protections yet.

The parser must read files with bounded input handling and must not retrieve external XML entities or network resources.

## 9. JUnit XML Compatibility

Supported root elements:

- `testsuite`
- `testsuites`

Supported content:

- One or more test suites.
- Multiple test cases.
- Nested test-suite structures.
- PASS, FAIL, ERROR, and SKIP outcomes.

Test cases shall be collected once each, including those in nested suites.

Summary attributes such as tests, failures, errors, and skipped may appear in JUnit XML.

For v0.1.0, Regression Radar shall derive its authoritative counts from normalized test cases rather than trusting producer-supplied summary attributes.

Producer-specific metadata and timing fields are not comparison criteria.

## 10. CLI Interface

Planned usage:

```text
regression-radar compare --baseline baseline.xml --current current.xml
```

Optional output selection:

```text
regression-radar compare --baseline baseline.xml --current current.xml --format json
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Valid comparison with zero new regressions |
| 1 | Valid comparison with one or more new regressions |
| 2 | Invalid input or execution failure |

Missing tests and skip transitions are always reported, even when exit code 0 applies.

Future policy-based exit codes are outside the v0.1.0 scope.

## 11. Error Handling

Invalid reports must never generate a successful comparison.

Errors shall distinguish:

- Missing files
- Unreadable files
- Oversized reports
- Malformed XML
- Unsupported XML roots
- Missing test identifiers
- Duplicate identifiers
- Conflicting test outcomes
- Input resource-limit violations

Errors should include actionable context without unnecessarily exposing local file contents or secrets.

## 12. Test Strategy

Testing will be divided into:

1. Parser unit tests
2. Normalization tests
3. Complete status-transition matrix tests
4. Duplicate and missing-identity tests
5. Malformed XML and security tests
6. Determinism tests
7. Reporting tests
8. CLI integration tests
9. Packaging and installation tests
10. GitHub CI verification

Each test must record an expected behavior and actual outcome.

No requirement may be marked PASS solely because implementation code exists.

## 13. Engineering Boundaries

The parser does not classify regressions.

The comparison engine does not read XML files.

The reporting module does not modify comparison outcomes.

The CLI does not duplicate parsing or classification rules.

Modules shall communicate through documented data structures.

## 14. Release Criteria

A release candidate requires:

- Traceable requirements.
- Passing automated tests.
- Passing static analysis.
- Reproducible reports.
- Validated malicious-input handling.
- Isolated wheel installation.
- Installed CLI execution.
- Successful GitHub Actions.
- Documented known limitations.
- Security scan.
- Final verification report.
- Explicit owner approval before publication.

## 15. Current Verification Status

**Architecture:** DOCUMENTED — NOT APPROVED
**Parser:** NOT RUN
**Comparison engine:** NOT RUN
**CLI:** NOT RUN
**Test suite:** NOT RUN
**Release:** NOT STARTED

---

**Engineering principle:** Test the claim — not just the demo.

### XML Structural Validation Clarification

For v0.1.0, a testcase must be a direct child of a testsuite.

Nested testsuite elements are supported. Testcases or testsuites
hidden inside unrelated metadata containers are rejected rather
than silently collected.

Harmless vendor-specific testcase metadata is permitted when it
does not alter test identity or outcome normalization.

This clarification was introduced after adversarial structural
tests identified overly permissive testcase traversal.
