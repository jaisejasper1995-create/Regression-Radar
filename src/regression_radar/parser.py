
"""Secure, deterministic parser for JUnit XML reports."""

from pathlib import Path

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

from regression_radar.models import TestCase, TestOutcome

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_TEST_CASES = 100_000

SUPPORTED_ROOTS = frozenset({"testsuite", "testsuites"})
OUTCOME_MARKERS = {
    "failure": "FAIL",
    "error": "ERROR",
    "skipped": "SKIP",
}


def _normalize_case(element) -> TestCase:
    """Normalize one testcase without changing its identity."""

    classname = element.get("classname")
    name = element.get("name")

    if classname is None or name is None:
        raise ValueError(
            "Testcase must have classname and name attributes"
        )

    if not classname or not name:
        raise ValueError(
            "Testcase classname and name must be nonempty"
        )

    markers = [
        child.tag
        for child in element
        if child.tag in OUTCOME_MARKERS
    ]

    if len(markers) > 1:
        raise ValueError(
            f"Conflicting or repeated outcomes for "
            f"{classname!r}, {name!r}"
        )

    outcome: TestOutcome = "PASS"

    if markers:
        outcome = OUTCOME_MARKERS[markers[0]]

    return TestCase(
        classname=classname,
        name=name,
        outcome=outcome,
    )


def parse_report(path: str | Path) -> tuple[TestCase, ...]:
    """Read and normalize a JUnit XML report securely.

    Reject invalid, ambiguous, or oversized inputs.
    Preserve the input file and return stable ordering.
    """

    report_path = Path(path)

    with report_path.open("rb") as report_file:
        data = report_file.read(MAX_FILE_SIZE + 1)

    if len(data) > MAX_FILE_SIZE:
        raise ValueError(
            f"XML report exceeds {MAX_FILE_SIZE} byte limit"
        )

    try:
        root = ElementTree.fromstring(
            data,
            forbid_dtd=True,
            forbid_entities=True,
            forbid_external=True,
        )
    except (ElementTree.ParseError, DefusedXmlException) as exc:
        raise ValueError(
            f"Invalid or prohibited XML in {report_path.name}"
        ) from exc

    if root.tag not in SUPPORTED_ROOTS:
        raise ValueError(
            f"Unsupported JUnit XML root: {root.tag}"
        )

    cases: list[TestCase] = []
    identities: set[tuple[str, str]] = set()

    for element in root.iter("testcase"):
        if len(cases) >= MAX_TEST_CASES:
            raise ValueError(
                f"Report exceeds {MAX_TEST_CASES} testcase limit"
            )

        case = _normalize_case(element)

        if case.identity in identities:
            raise ValueError(
                f"Duplicate testcase identity: {case.identity!r}"
            )

        identities.add(case.identity)
        cases.append(case)

    if not cases:
        raise ValueError(
            "JUnit XML report contains no testcases"
        )

    return tuple(
        sorted(
            cases,
            key=lambda case: case.identity,
        )
    )
