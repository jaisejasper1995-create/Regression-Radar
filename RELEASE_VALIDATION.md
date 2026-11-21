# Regression Radar v0.1.0 â€” Release Validation

## Project
- Owner: Richard Ottman
- Purpose: Deterministic JUnit XML regression analysis
- License: MIT
- Release status: NOT YET RELEASED

## Verified Test Evidence
- 98 automated tests passed with warnings treated as errors.
- Ruff checks passed.
- Six GitHub Actions jobs reported passing by the project owner:
  Windows and Ubuntu, Python 3.11, 3.12, and 3.13.
- Wheel and source distribution built successfully.
- Both distributions passed Twine metadata checks without warnings.
- Clean Windows/Python 3.13 wheel installation succeeded.
- pip check reported no broken dependencies.
- Exit code 0 verified: no new regressions.
- Exit code 1 verified: PASS-to-FAIL regression.
- Exit code 2 verified: invalid input.

## Security Evidence
- pip-audit reported no known vulnerabilities among auditable packages.
- The unpublished local Regression Radar package was skipped by pip-audit.
- Bandit -ll reported no medium- or high-severity findings.
- 394 source lines scanned; no #nosec exclusions.
- Preliminary tracked-file and Git-history review reported clean.

## Known Limitations
- Static analysis does not guarantee the absence of vulnerabilities.
- Credential-pattern searching cannot detect every possible secret.
- Independent Windows/Python 3.13 source-distribution installation passed; dependency check passed and CLI returned exit code 0.
- Final documentation and packaging changes require fresh CI results.

## Final Release Checklist
- [ ] Verify MIT LICENSE and README.
- [ ] Validate package metadata and packaged license.
- [ ] Re-run pytest, Ruff, build, and Twine checks.
- [ ] Independently install and test source distribution.
- [ ] Review release-candidate contents for unintended files or secrets.
- [ ] Commit and push documentation changes.
- [ ] Confirm six CI jobs pass for the release candidate.
- [ ] Obtain explicit approval before public release.

## Authorization
No public visibility change, Git tag, GitHub Release, or PyPI publication
is authorized by this document.
