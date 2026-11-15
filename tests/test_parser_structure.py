
"""Tests for supported JUnit XML element structure."""

import pytest

from regression_radar.parser import parse_report


@pytest.mark.parametrize(
    "xml",
    [
        (
            '<testsuite>'
            '<unexpected>'
            '<testcase classname="suite" name="hidden"/>'
            '</unexpected>'
            '</testsuite>'
        ),
        (
            '<testsuites>'
            '<testcase classname="suite" name="orphan"/>'
            '</testsuites>'
        ),
        (
            '<testsuites>'
            '<unexpected>'
            '<testsuite>'
            '<testcase classname="suite" name="hidden"/>'
            '</testsuite>'
            '</unexpected>'
            '</testsuites>'
        ),
    ],
)
def test_rejects_invalid_testcase_structure(tmp_path, xml):
    """Reject testcases outside supported suite paths."""
    path = tmp_path / "invalid_structure.xml"
    path.write_text(xml, encoding="utf-8")

    with pytest.raises(ValueError):
        parse_report(path)


def test_allows_vendor_metadata_inside_testcase(tmp_path):
    """Harmless metadata must not invalidate a testcase."""
    path = tmp_path / "vendor_metadata.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="suite" name="example">'
        '<system-out>diagnostic output</system-out>'
        '<properties><property name="environment" value="test"/>'
        '</properties>'
        '</testcase>'
        '</testsuite>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 1
    assert cases[0].identity == ("suite", "example")
    assert cases[0].outcome == "PASS"
