# Regression Radar v0.1.0 — Test Matrix

**Phase:** 1 — Engineering Baseline
**Status:** PROPOSED — Not yet approved
**Production implementation:** NOT STARTED
**Executed automated tests:** 0

## 1. Testing Principles

Every test must have a known expected result before implementation.

Tests must not be modified simply to make an implementation pass.

Each case will be recorded as PASS, FAIL, BLOCKED, or NOT RUN.

Every failure must have an explanation and an investigation record.

Fixture inputs must be deterministic and preserved.

## 2. Status-Transition Matrix

The following 16 transitions cover every combination of the four normalized test outcomes.

| Test ID | Baseline | Current | Expected classification |
|---|---|---|---|
| RR-T001 | PASS | PASS | Unchanged pass |
| RR-T002 | PASS | FAIL | New regression |
| RR-T003 | PASS | ERROR | New regression |
| RR-T004 | PASS | SKIP | Skip transition |
| RR-T005 | FAIL | PASS | Resolved failure |
| RR-T006 | FAIL | FAIL | Persistent failure |
| RR-T007 | FAIL | ERROR | Persistent failure |
| RR-T008 | FAIL | SKIP | Skip transition |
| RR-T009 | ERROR | PASS | Resolved failure |
| RR-T010 | ERROR | FAIL | Persistent failure |
| RR-T011 | ERROR | ERROR | Persistent failure |
| RR-T012 | ERROR | SKIP | Skip transition |
| RR-T013 | SKIP | PASS | Skip transition |
| RR-T014 | SKIP | FAIL | Skip transition |
| RR-T015 | SKIP | ERROR | Skip transition |
| RR-T016 | SKIP | SKIP | Unchanged skip |

**Required evidence:** The classification, original status, and current status must match the expected values.

## 3. Added and Missing Tests

| Test ID | Scenario | Expected behavior |
|---|---|---|
| RR-T017 | Test appears only in current report | Added test |
| RR-T018 | Test appears only in baseline report | Missing test |
| RR-T019 | Previously failing test disappears | Missing, not resolved |
| RR-T020 | Previously failing test becomes skipped | Skip transition, not resolved |
| RR-T021 | New failing test appears without a baseline match | Added test, with FAIL preserved |
| RR-T022 | Multiple missing and added tests | Every identity classified once |

## 4. Identity and Duplicate Tests

| Test ID | Scenario | Expected behavior |
|---|---|---|
| RR-T023 | Identical classname and name | Same test identity |
| RR-T024 | Same name, different classname | Different identities |
| RR-T025 | Different capitalization | Different identities |
| RR-T026 | Different internal whitespace | Different identities |
| RR-T027 | Missing classname | Reject |
| RR-T028 | Missing name | Reject |
| RR-T029 | Empty classname | Reject |
| RR-T030 | Empty name | Reject |
| RR-T031 | Duplicate identity in one report | Reject |
| RR-T032 | Different XML testcase ordering | Same comparison result |
| RR-T033 | Same identity across different suites within one report | Reject duplicate |
| RR-T034 | Leading or trailing spaces in identity | Preserve exactly; no silent trimming |

## 5. XML Parsing and Normalization

| Test ID | Scenario | Expected behavior |
|---|---|---|
| RR-T035 | Single testsuite root | Accept |
| RR-T036 | Multiple suites under testsuites | Accept |
| RR-T037 | Nested test suites | Collect each testcase once |
| RR-T038 | Passing testcase | PASS |
| RR-T039 | Failure child | FAIL |
| RR-T040 | Error child | ERROR |
| RR-T041 | Skipped child | SKIP |
| RR-T042 | Repeated outcome markers | Reject |
| RR-T043 | Conflicting outcome markers | Reject |
| RR-T044 | Malformed XML | Reject |
| RR-T045 | Unsupported root | Reject |
| RR-T046 | No testcases | Reject |
| RR-T047 | Incorrect producer summary attributes | Derive counts from testcases |
| RR-T048 | Unknown non-outcome testcase metadata | Do not alter classification |

## 6. XML Security and Resource Limits

| Test ID | Scenario | Expected behavior |
|---|---|---|
| RR-T049 | File larger than 5 MiB | Reject |
| RR-T050 | File exactly at allowed size limit | Evaluate normally |
| RR-T051 | Prohibited entity declaration | Reject |
| RR-T052 | External entity reference | Reject; never fetch external resource |
| RR-T053 | Malicious entity expansion | Reject |
| RR-T054 | Missing input file | Actionable error |
| RR-T055 | Unreadable input file | Actionable error |
| RR-T056 | File exceeds testcase-count limit | Reject |
| RR-T057 | Input file after comparison | Unchanged |
| RR-T058 | Invalid encoding or decoding | Reject without crash |
| RR-T059 | Large but permitted report | Deterministic result within limits |

Security tests must use controlled local fixtures. They must not contact external services.

## 7. Comparison Engine and Reporting

| Test ID | Scenario | Expected behavior |
|---|---|---|
| RR-T060 | Identical reports | No new regressions |
| RR-T061 | Same inputs repeated | Identical reports |
| RR-T062 | Different testcase ordering | Identical comparison |
| RR-T063 | Mixed outcomes | Correct category totals |
| RR-T064 | Original inputs compared | No mutation |
| RR-T065 | Empty regression category | Correct zero count |
| RR-T066 | Persistent FAIL becomes ERROR | Preserve both statuses |
| RR-T067 | JSON reporting | Stable, valid structure |
| RR-T068 | Text reporting | Readable classifications |
| RR-T069 | Escaped or special characters | Valid output |
| RR-T070 | Summary counts | Reconcile with all classifications |

## 8. CLI Behavior

| Test ID | Scenario | Expected result |
|---|---|---|
| RR-T071 | Valid comparison, no regressions | Exit 0 |
| RR-T072 | One or more new regressions | Exit 1 |
| RR-T073 | Invalid input file | Exit 2 |
| RR-T074 | Malformed XML | Exit 2 |
| RR-T075 | Missing required CLI argument | Exit 2 |
| RR-T076 | Unsupported output format | Exit 2 |
| RR-T077 | CLI help | Exit 0 |
| RR-T078 | JSON format selected | Valid JSON |
| RR-T079 | Text format selected | Human-readable report |
| RR-T080 | Missing tests without new regressions | Exit 0, missing tests visible |
| RR-T081 | Skipped transitions without new regressions | Exit 0, skips visible |

## 9. Packaging and Release Validation

| Test ID | Scenario | Expected result |
|---|---|---|
| RR-T082 | Package builds into wheel | PASS |
| RR-T083 | Wheel installs into clean environment | PASS |
| RR-T084 | Installed command launches | PASS |
| RR-T085 | Installed command compares fixture reports | PASS |
| RR-T086 | Python 3.11 CI | PASS |
| RR-T087 | Python 3.12 CI | PASS |
| RR-T088 | Python 3.13 CI | PASS |
| RR-T089 | Ruff static checks | PASS |
| RR-T090 | Git history secrets scan | Zero unresolved findings |
| RR-T091 | Release documentation | Complete and accurate |
| RR-T092 | Release commit and tag | Exact verified commit |
| RR-T093 | Publication | Only after explicit owner approval |

## 10. Requirements Traceability

| Requirements | Primary test coverage |
|---|---|
| RR-001–RR-003 | T035–T059, T073–T076 |
| RR-004–RR-005 | T023–T034 |
| RR-006 | T038–T043 |
| RR-007–RR-013 | T001–T022 |
| RR-014–RR-015 | T060–T066, T070 |
| RR-016–RR-020 | T061, T067–T081 |
| RR-021 | T086–T088 |
| RR-022–RR-025 | T049–T059, T082–T085 |
| RR-026 | Requirements-to-tests evidence review |
| RR-027 | T086–T089 |
| RR-028 | T082–T085 |
| RR-029 | T090–T092 |
| RR-030 | T093 |

This matrix defines 93 planned test scenarios or verification checks. Some may become multiple parameterized test executions. Their existence in this document does not mean they have been implemented or passed.

## 11. Test Execution Rules

- Each test must be linked to an expected result.
- Store normal and adversarial XML fixtures separately.
- Keep historical evidence.
- Investigate failures before modifying production code.
- Do not silently weaken assertions.
- Do not claim a PASS without execution evidence.
- Test counts must reflect actual pytest results.
- Release verification checks must remain distinguishable from automated unit tests.

## 12. Current Verification State

**Test matrix:** DOCUMENTED — NOT APPROVED
**Automated tests implemented:** 0
**Automated tests executed:** 0
**Requirements implementation:** NOT STARTED
**Release verification:** NOT RUN

---

**Engineering principle:** Test the claim — not just the demo.
