
# Regression Radar

**Deterministic JUnit XML regression detection for software QA.**

Regression Radar is a Python command-line tool that compares two JUnit XML reports and identifies changes in individual test outcomes.

The goal is simple: distinguish genuine regressions from existing failures, resolved failures, skipped tests, and changes in test inventory.

## Features

- Secure XML parsing using `defusedxml`
- Deterministic testcase matching and sorting
- All 16 transitions between PASS, FAIL, ERROR, and SKIP
- Separate classification of new regressions and resolved failures
- Persistent-failure tracking
- Separate handling of added and missing tests
- Separate counts for unchanged skips and skip transitions
- Human-readable text and structured JSON output
- Documented exit codes for CI integration
- Rejection of duplicate testcase identities
- Input-size and testcase-count limits

## Requirements

- Python 3.11 or newer
- Supported platforms: Python-compatible operating systems

The initial implementation has been manually exercised on Windows with Python 3.13.

## Installation

Clone the repository and open a terminal in the project directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Install in editable mode with development tools:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

On Windows, the installed executable is:

```powershell
.\.venv\Scripts\regression-radar.exe
```

On other platforms, activate the appropriate virtual environment and use the installed `regression-radar` command.

## Usage

Compare a baseline report with a current report:

```powershell
regression-radar baseline.xml current.xml
```

Request JSON output:

```powershell
regression-radar baseline.xml current.xml --format json
```

Display help:

```powershell
regression-radar --help
```

The baseline and current files must identify matching tests using the same `classname` and `name` values.

## Regression classification

| Baseline | Current | Classification |
|---|---|---|
| PASS | FAIL | NEW_REGRESSION |
| PASS | ERROR | NEW_REGRESSION |
| FAIL | PASS | RESOLVED |
| ERROR | PASS | RESOLVED |
| FAIL | ERROR | PERSISTENT_FAILURE |
| ERROR | FAIL | PERSISTENT_FAILURE |
| PASS | PASS | UNCHANGED_PASS |
| SKIP | SKIP | UNCHANGED_SKIP |
| SKIP | FAIL | SKIP_TRANSITION |
| PASS | SKIP | SKIP_TRANSITION |

All 16 supported status transitions are classified.

Newly added testcases and missing testcases are reported separately.

An added failing testcase is not automatically classified as a new regression. A missing failing testcase is not classified as resolved.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | No new regressions detected |
| 1 | One or more new regressions detected |
| 2 | Invalid arguments, invalid input, or handled execution error |

An exit code of 0 does not mean every testcase passed. It means no new PASS-to-FAIL or PASS-to-ERROR regressions were detected.

## JSON report

The JSON report includes:

- `schema_version`
- `summary`
- `transitions`
- `added`
- `missing`

Summary values are derived from normalized testcase records rather than producer-supplied XML totals.

JSON arrays follow deterministic testcase identity ordering.

## XML input policy

Supported root elements:

- `testsuite`
- `testsuites`

Supported content includes multiple suites and nested test suites.

Testcases are identified by the exact pair:

`(classname, name)`

Identity comparisons preserve case and whitespace.

The parser rejects:

- Malformed XML
- Duplicate testcase identities
- Missing or empty identity attributes
- Conflicting or repeated outcome markers
- Prohibited DTD and XML entity declarations
- Unsupported root elements
- Invalid testcase placement
- Reports larger than 5 MiB
- Reports exceeding 100,000 testcases
- Reports containing no testcases

## Development verification

Run the automated test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -W error
```

Check Python source formatting and lint rules:

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
```

## Scope and limitations

Regression Radar v0.1.0 is intentionally focused on deterministic test-result comparison.

It does not currently provide:

- AI-generated root-cause analysis
- Automatic code fixes
- Cloud storage or hosted dashboards
- Timing-based performance regression analysis
- Complete compatibility with every vendor-specific JUnit extension

It is a read-only comparison tool and does not modify the original XML reports.

## Project status

The XML parser, comparison engine, and initial CLI implementation have been developed and locally tested.

Additional adversarial validation, packaging verification, CI integration, and public release checks remain part of the v0.1.0 roadmap.

## License

Regression Radar is licensed under the MIT License. See [LICENSE](LICENSE) for details.
