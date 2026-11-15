
"""Adversarial tests for Regression Radar's XML parser."""

import pytest

from regression_radar.parser import MAX_FILE_SIZE, parse_report


@pytest.mark.parametrize(
    "marker",
    ["failure", "error", "skipped"],
)
def test_rejects_repeated_outcome_markers(tmp_path, marker):
    """Two markers of the same type are invalid."""
    path = tmp_path / "repeated.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="suite" name="test_one">'
        f'<{marker}/><{marker}/>'
        '</testcase>'
        '</testsuite>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_preserves_identity_whitespace(tmp_path):
    """Spaces in identifiers must never be stripped."""
    path = tmp_path / "spaces.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname=" suite " name=" test_one "/>'
        '</testsuite>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 1
    assert cases[0].identity == (" suite ", " test_one ")


def test_identity_is_case_sensitive(tmp_path):
    """Different letter case means different identities."""
    path = tmp_path / "case.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="Suite" name="Test"/>'
        '<testcase classname="suite" name="Test"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 2
    assert cases[0].identity == ("Suite", "Test")
    assert cases[1].identity == ("suite", "Test")


def test_rejects_file_over_size_limit(tmp_path):
    """Input must not exceed the frozen 5 MiB limit."""
    path = tmp_path / "oversized.xml"
    path.write_bytes(b"x" * (MAX_FILE_SIZE + 1))

    with pytest.raises(ValueError, match="exceeds"):
        parse_report(path)


def test_accepts_file_at_exact_size_limit(tmp_path):
    """Exactly 5 MiB is permitted if XML is valid."""
    path = tmp_path / "boundary.xml"

    prefix = (
        b'<testsuite>'
        b'<testcase classname="s" name="t"/>'
        b'</testsuite>'
    )
    data = prefix + b" " * (MAX_FILE_SIZE - len(prefix))

    assert len(data) == MAX_FILE_SIZE
    path.write_bytes(data)

    cases = parse_report(path)

    assert len(cases) == 1
    assert cases[0].identity == ("s", "t")


def test_rejects_zero_byte_file(tmp_path):
    """An empty file cannot become a valid report."""
    path = tmp_path / "zero.xml"
    path.write_bytes(b"")

    with pytest.raises(ValueError):
        parse_report(path)


def test_rejects_doctype_without_entities(tmp_path):
    """DTD declarations themselves must be prohibited."""
    path = tmp_path / "doctype.xml"
    path.write_text(
        '<!DOCTYPE testsuite>'
        '<testsuite>'
        '<testcase classname="suite" name="test_one"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_report(path)


def test_preserves_escaped_identity_characters(tmp_path):
    """Normal XML escaping must not corrupt identities."""
    path = tmp_path / "escaped.xml"
    path.write_text(
        '<testsuite>'
        '<testcase classname="A&amp;B" name="x&lt;y"/>'
        '</testsuite>',
        encoding="utf-8",
    )

    cases = parse_report(path)

    assert len(cases) == 1
    assert cases[0].identity == ("A&B", "x<y")
