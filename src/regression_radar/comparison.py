
"""Deterministic comparison of normalized JUnit test results."""

from dataclasses import dataclass
from typing import Literal

from regression_radar.models import TestCase

Classification = Literal[
    "NEW_REGRESSION",
    "RESOLVED",
    "PERSISTENT_FAILURE",
    "UNCHANGED_PASS",
    "UNCHANGED_SKIP",
    "SKIP_TRANSITION",
]

FAILURE_OUTCOMES = frozenset({"FAIL", "ERROR"})
VALID_OUTCOMES = frozenset({"PASS", "FAIL", "ERROR", "SKIP"})


@dataclass(frozen=True)
class Transition:
    """Outcome change for a testcase present in both reports."""

    identity: tuple[str, str]
    before: str
    after: str
    classification: Classification


@dataclass(frozen=True)
class ComparisonResult:
    """Immutable comparison result with separate categories."""

    transitions: tuple[Transition, ...]
    added: tuple[TestCase, ...]
    missing: tuple[TestCase, ...]

    @property
    def new_regressions(self) -> tuple[Transition, ...]:
        return tuple(
            item
            for item in self.transitions
            if item.classification == "NEW_REGRESSION"
        )

    @property
    def resolved(self) -> tuple[Transition, ...]:
        return tuple(
            item
            for item in self.transitions
            if item.classification == "RESOLVED"
        )

    @property
    def persistent_failures(self) -> tuple[Transition, ...]:
        return tuple(
            item
            for item in self.transitions
            if item.classification == "PERSISTENT_FAILURE"
        )

    @property
    def skip_transitions(self) -> tuple[Transition, ...]:
        return tuple(
            item
            for item in self.transitions
            if item.classification == "SKIP_TRANSITION"
        )

    @property
    def unchanged_skips(self) -> tuple[Transition, ...]:
        return tuple(
            item
            for item in self.transitions
            if item.classification == "UNCHANGED_SKIP"
        )


def _classify(before: str, after: str) -> Classification:
    """Classify one of the sixteen supported status transitions."""

    if before == "PASS" and after in FAILURE_OUTCOMES:
        return "NEW_REGRESSION"

    if before in FAILURE_OUTCOMES and after == "PASS":
        return "RESOLVED"

    if before in FAILURE_OUTCOMES and after in FAILURE_OUTCOMES:
        return "PERSISTENT_FAILURE"

    if before == "SKIP" and after == "SKIP":
        return "UNCHANGED_SKIP"

    if "SKIP" in (before, after):
        return "SKIP_TRANSITION"

    return "UNCHANGED_PASS"


def _index_cases(
    cases: tuple[TestCase, ...] | list[TestCase],
) -> dict[tuple[str, str], TestCase]:
    """Index testcases without silently overwriting duplicates."""

    indexed: dict[tuple[str, str], TestCase] = {}

    for case in cases:
        if case.outcome not in VALID_OUTCOMES:
            raise ValueError(
                f"Unsupported outcome: {case.outcome!r}"
            )

        if case.identity in indexed:
            raise ValueError(
                f"Duplicate testcase identity: {case.identity!r}"
            )

        indexed[case.identity] = case

    return indexed


def compare_reports(
    baseline: tuple[TestCase, ...] | list[TestCase],
    current: tuple[TestCase, ...] | list[TestCase],
) -> ComparisonResult:
    """Compare baseline and current normalized testcases.

    Added and missing tests remain separate from transitions.
    Results use deterministic identity ordering.
    """

    baseline_index = _index_cases(baseline)
    current_index = _index_cases(current)

    common_keys = sorted(baseline_index.keys() & current_index.keys())
    added_keys = sorted(current_index.keys() - baseline_index.keys())
    missing_keys = sorted(baseline_index.keys() - current_index.keys())

    transitions = tuple(
        Transition(
            identity=identity,
            before=baseline_index[identity].outcome,
            after=current_index[identity].outcome,
            classification=_classify(
                baseline_index[identity].outcome,
                current_index[identity].outcome,
            ),
        )
        for identity in common_keys
    )

    return ComparisonResult(
        transitions=transitions,
        added=tuple(current_index[key] for key in added_keys),
        missing=tuple(baseline_index[key] for key in missing_keys),
    )
