
"""Tests for Regression Radar's secure JUnit XML parser.

Phase 2: Test-first implementation.
These tests define expected behavior before parser.py exists.
"""

from pathlib import Path

import pytest

from regression_radar.parser import parse_report

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("filename", "expected_outcome"),
    [
        ("pass.xml", "PASS"),
        ("fail.xml", "FAIL"),
        ("error.xml", "ERROR"),
        ("skip.xml", "SKIP"),
    ],
)
def test_four_supported_outcomes(filename, expected_outcome):
    """Normalize the four documented JUnit outcomes."""
    cases = parse_report(FIXTURES / filename)

    assert len(cases) == 1
    assert cases[0].outcome == expected_outcome


def test_preserves_test_identity():
    """Identity must retain classname and name exactly."""
    cases = parse_report(FIXTURES / "pass.xml")

    assert cases[0].classname == "sample.tests"
    assert cases[0].name == "test_pass"


def test_rejects_missing_file(tmp_path):
    """A nonexistent report must not produce a valid result."""
    with pytest.raises((OSError, ValueError)):
        parse_report(tmp_path / "missing.xml")


def test_rejects_malformed_xml(tmp_path):
    """Malformed XML must fail closed."""
    path = tmp_path / "malformed.xml"
    path.write_text("<testsuite><testcase>", encoding="utf-8")

    with pytest.raises(ValueError):
        parse_report(path)


def test_rejects_duplicate_identity(tmp_path):
    """Duplicate classname/name pairs must not be merged."""
    path = tmp_path / "duplicates.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="suite" name="same"/>'
        '<testcase classname="suite" name="same"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


@pytest.mark.parametrize(
    "attributes",
    [
        'name="test_example"',
        'classname="suite"',
        'classname="" name="test_example"',
        'classname="suite" name=""',
    ],
)
def test_rejects_missing_or_empty_identity(tmp_path, attributes):
    """Both identity attributes must be present and nonempty."""
    path = tmp_path / "invalid_identity.xml"
    path.write_text(
        f"<testsuite><testcase {attributes}/></testsuite>",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_rejects_conflicting_outcomes(tmp_path):
    """One testcase cannot represent two different outcomes."""
    path = tmp_path / "conflicting.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="suite" name="test_example">'
        '<failure/><error/>'
        '</testcase>'
        '</testsuite>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_rejects_unsupported_root(tmp_path):
    """Only supported JUnit XML root structures are valid."""
    path = tmp_path / "unsupported.xml"
    path.write_text(
        '<report><testcase classname="suite" name="test"/></report>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_rejects_empty_report(tmp_path):
    """An empty JUnit test suite must not silently pass."""
    path = tmp_path / "empty.xml"
    path.write_text("<testsuite/>", encoding="utf-8")

    with pytest.raises(ValueError):
        parse_report(path)


def test_rejects_entity_declarations(tmp_path):
    """Hostile XML entity declarations must be rejected."""
    path = tmp_path / "entity.xml"
    path.write_text(
        '<!DOCTYPE testsuite ['
        '<!ENTITY secret "unexpected">'
        ']>'
        '<testsuite>'
        '<testcase classname="suite" name="&secret;"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_nested_suites_collect_each_test_once(tmp_path):
    """Nested JUnit suites must not duplicate testcase records."""
    path = tmp_path / "nested.xml"
    path.write_text(
        '<testsuites>'
        '<testsuite name="parent">'
        '<testcase classname="suite" name="first"/>'
        '<testsuite name="child">'
        '<testcase classname="suite" name="second"/>'
        '</testsuite>'
        '</testsuite>'
        '</testsuites>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 2
    assert {case.name for case in cases} == {"first", "second"}
