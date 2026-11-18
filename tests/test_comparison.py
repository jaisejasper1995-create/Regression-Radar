
"""Test-first coverage for Regression Radar comparison behavior."""

from itertools import product

import pytest

from regression_radar.comparison import compare_reports
from regression_radar.models import TestCase as CaseModel

STATUSES = ("PASS", "FAIL", "ERROR", "SKIP")


def make_case(name, outcome, classname="suite"):
    return CaseModel(
        classname=classname,
        name=name,
        outcome=outcome,
    )


@pytest.mark.parametrize(
    ("before", "after"),
    list(product(STATUSES, repeat=2)),
)
def test_all_sixteen_status_transitions(before, after):
    """Every supported transition must receive a classification."""
    baseline = (make_case("example", before),)
    current = (make_case("example", after),)

    result = compare_reports(baseline, current)

    assert len(result.transitions) == 1
    transition = result.transitions[0]

    assert transition.identity == ("suite", "example")
    assert transition.before == before
    assert transition.after == after

    if before == "PASS" and after in {"FAIL", "ERROR"}:
        expected = "NEW_REGRESSION"
    elif before in {"FAIL", "ERROR"} and after == "PASS":
        expected = "RESOLVED"
    elif before in {"FAIL", "ERROR"} and after in {"FAIL", "ERROR"}:
        expected = "PERSISTENT_FAILURE"
    elif before == "SKIP" and after == "SKIP":
        expected = "UNCHANGED_SKIP"
    elif "SKIP" in {before, after}:
        expected = "SKIP_TRANSITION"
    else:
        expected = "UNCHANGED_PASS"

    assert transition.classification == expected


def test_added_test_is_not_new_regression():
    """An added failing test must not be mislabeled a regression."""
    result = compare_reports(
        (),
        (make_case("new", "FAIL"),),
    )

    assert len(result.added) == 1
    assert result.added[0].identity == ("suite", "new")
    assert len(result.new_regressions) == 0


def test_missing_test_is_not_resolved():
    """A disappearing failure is not evidence of a fix."""
    result = compare_reports(
        (make_case("missing", "FAIL"),),
        (),
    )

    assert len(result.missing) == 1
    assert result.missing[0].identity == ("suite", "missing")
    assert len(result.resolved) == 0


def test_comparison_order_is_deterministic():
    """Changing testcase input order cannot change comparison order."""
    baseline = (
        make_case("z", "PASS"),
        make_case("a", "PASS"),
    )
    current = (
        make_case("a", "FAIL"),
        make_case("z", "FAIL"),
    )

    result = compare_reports(baseline, current)

    assert [
        item.identity for item in result.transitions
    ] == [
        ("suite", "a"),
        ("suite", "z"),
    ]


def test_identical_passing_reports_have_no_regressions():
    """Unchanged PASS cases must not trigger regression detection."""
    baseline = (make_case("example", "PASS"),)
    current = (make_case("example", "PASS"),)

    result = compare_reports(baseline, current)

    assert len(result.new_regressions) == 0
    assert result.transitions[0].classification == "UNCHANGED_PASS"
