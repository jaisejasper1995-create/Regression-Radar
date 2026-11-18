
"""Adversarial and accounting tests for the comparison engine."""

import pytest

from regression_radar.comparison import compare_reports
from regression_radar.models import TestCase as CaseModel


def case(name, outcome, classname="suite"):
    return CaseModel(
        classname=classname,
        name=name,
        outcome=outcome,
    )


@pytest.mark.parametrize("side", ["baseline", "current"])
def test_rejects_duplicate_identities(side):
    """Neither input may contain duplicate testcase identities."""
    duplicate = (
        case("same", "PASS"),
        case("same", "FAIL"),
    )

    baseline = duplicate if side == "baseline" else ()
    current = duplicate if side == "current" else ()

    with pytest.raises(ValueError, match="Duplicate"):
        compare_reports(baseline, current)


@pytest.mark.parametrize("side", ["baseline", "current"])
@pytest.mark.parametrize("outcome", ["UNKNOWN", "", "pass"])
def test_rejects_invalid_outcomes(side, outcome):
    """Unsupported statuses must fail closed."""
    invalid = (case("example", outcome),)

    baseline = invalid if side == "baseline" else ()
    current = invalid if side == "current" else ()

    with pytest.raises(ValueError, match="Unsupported"):
        compare_reports(baseline, current)


def test_added_failure_is_not_regression():
    """A newly appearing failure is an added test."""
    result = compare_reports(
        (),
        (case("new", "ERROR"),),
    )

    assert len(result.added) == 1
    assert len(result.new_regressions) == 0
    assert len(result.resolved) == 0


def test_missing_failure_is_not_resolved():
    """A disappearing error is not a fixed test."""
    result = compare_reports(
        (case("removed", "ERROR"),),
        (),
    )

    assert len(result.missing) == 1
    assert len(result.resolved) == 0


def test_unchanged_skip_is_separate():
    """SKIP to SKIP is not an actual skip transition."""
    result = compare_reports(
        (case("example", "SKIP"),),
        (case("example", "SKIP"),),
    )

    assert len(result.unchanged_skips) == 1
    assert len(result.skip_transitions) == 0
    assert len(result.new_regressions) == 0


def test_skip_to_failure_is_not_new_regression():
    """A previously skipped test cannot be a PASS regression."""
    result = compare_reports(
        (case("example", "SKIP"),),
        (case("example", "FAIL"),),
    )

    assert len(result.skip_transitions) == 1
    assert len(result.new_regressions) == 0


def test_mixed_summary_categories_are_disjoint():
    """Each comparison category must remain distinct."""
    baseline = (
        case("regression", "PASS"),
        case("resolved", "FAIL"),
        case("persistent", "ERROR"),
        case("unchanged_skip", "SKIP"),
        case("skip_change", "SKIP"),
        case("removed", "FAIL"),
    )

    current = (
        case("regression", "FAIL"),
        case("resolved", "PASS"),
        case("persistent", "FAIL"),
        case("unchanged_skip", "SKIP"),
        case("skip_change", "PASS"),
        case("added", "ERROR"),
    )

    result = compare_reports(baseline, current)

    assert len(result.new_regressions) == 1
    assert len(result.resolved) == 1
    assert len(result.persistent_failures) == 1
    assert len(result.unchanged_skips) == 1
    assert len(result.skip_transitions) == 1
    assert len(result.added) == 1
    assert len(result.missing) == 1


def test_added_and_missing_order_is_deterministic():
    """Added and missing categories use sorted identity order."""
    baseline = (
        case("z", "PASS"),
        case("a", "PASS"),
    )
    current = (
        case("y", "PASS"),
        case("b", "PASS"),
    )

    result = compare_reports(baseline, current)

    assert [item.name for item in result.added] == ["b", "y"]
    assert [item.name for item in result.missing] == ["a", "z"]
