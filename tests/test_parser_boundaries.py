
"""Boundary and determinism tests for the JUnit XML parser."""

import pytest

from regression_radar.parser import MAX_TEST_CASES, parse_report


def _write_large_report(path, count):
    """Generate unique testcases without exceeding the file-size limit."""
    with path.open("w", encoding="utf-8") as report:
        report.write("<testsuite>")
        for index in range(count):
            report.write(
                f'<testcase classname="s" name="{index}"/>'
            )
        report.write("</testsuite>")


def test_accepts_exact_testcase_limit(tmp_path):
    """Exactly 100,000 testcases must be accepted."""
    path = tmp_path / "at_limit.xml"
    _write_large_report(path, MAX_TEST_CASES)

    cases = parse_report(path)

    assert len(cases) == MAX_TEST_CASES


def test_rejects_testcase_over_limit(tmp_path):
    """100,001 testcases must be rejected."""
    path = tmp_path / "over_limit.xml"
    _write_large_report(path, MAX_TEST_CASES + 1)

    with pytest.raises(ValueError, match="testcase limit"):
        parse_report(path)


def test_ignores_untrusted_producer_summary(tmp_path):
    """Actual testcase records determine normalized totals."""
    path = tmp_path / "wrong_summary.xml"
    path.write_text(
        '<testsuite tests="999" failures="999" errors="999">'
        '<testcase classname="suite" name="passing"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 1
    assert cases[0].outcome == "PASS"


def test_returns_deterministic_identity_order(tmp_path):
    """Output must be sorted by exact (classname, name) identity."""
    path = tmp_path / "unordered.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="z" name="last"/>'
        '<testcase classname="a" name="second"/>'
        '<testcase classname="a" name="first"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert [case.identity for case in cases] == [
        ("a", "first"),
        ("a", "second"),
        ("z", "last"),
    ]


def test_rejects_invalid_utf8(tmp_path):
    """Malformed input bytes must not silently become valid XML."""
    path = tmp_path / "invalid_encoding.xml"
    path.write_bytes(
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<testsuite><testcase classname="s" name="\xff"/>'
        b'</testsuite>'
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_supports_testsuites_root(tmp_path):
    """A testsuites document can contain multiple suites."""
    path = tmp_path / "multiple_suites.xml"
    path.write_text(
        '<testsuites>'
        '<testsuite name="first">'
        '<testcase classname="a" name="one"/>'
        '</testsuite>'
        '<testsuite name="second">'
        '<testcase classname="b" name="two"/>'
        '</testsuite>'
        '</testsuites>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 2
    assert [case.identity for case in cases] == [
        ("a", "one"),
        ("b", "two"),
    ]
