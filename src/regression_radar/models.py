
"""Immutable data models for Regression Radar."""

from dataclasses import dataclass
from typing import Literal

TestOutcome = Literal["PASS", "FAIL", "ERROR", "SKIP"]


@dataclass(frozen=True)
class TestCase:
    """One normalized JUnit XML test result."""

    classname: str
    name: str
    outcome: TestOutcome

    @property
    def identity(self) -> tuple[str, str]:
        """Return the exact, case-sensitive test identity."""
        return self.classname, self.name
