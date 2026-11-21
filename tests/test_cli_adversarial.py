
"""Adversarial black-box tests for Regression Radar's CLI."""

import json
import subprocess
import sys

import pytest


def _run_cli(*arguments):
    """Execute the installed Python package's CLI module."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "regression_radar.cli",
            *map(str, arguments),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _write(path, content):
    path.write_text(content, encoding="utf-8")
    return path


GOOD_XML = (
    '<testsuite>'
    '<testcase classname="suite" name="valid"/>'
    '</testsuite>'
)


@pytest.mark.parametrize(
    ("invalid_xml", "scenario"),
    [
        ("<testsuite><testcase>", "malformed_xml"),
        (
            ('<testsuite>'
            '<testcase classname="suite"/>'
            '</testsuite>'),
            "missing_identity",
        ),
        (
            ('<testsuite>'
            '<testcase classname="suite" name="same"/>'
            '<testcase classname="suite" name="same"/>'
            '</testsuite>'),
            "duplicate_identity",
        ),
        (
            ('<!DOCTYPE testsuite [<!ENTITY x "value">]>'
            '<testsuite>'
            '<testcase classname="suite" name="&x;"/>'
            '</testsuite>'),
            "entity_declaration",
        ),
        (
            ('<testsuite>'
            '<testcase classname="suite" name="same">'
            '<failure/><error/>'
            '</testcase>'
            '</testsuite>'),
            "conflicting_outcomes",
        ),
        (
            ('<testsuite>'
            '<unexpected>'
            '<testcase classname="suite" name="hidden"/>'
            '</unexpected>'
            '</testsuite>'),
            "invalid_structure",
        ),
    ],
)
@pytest.mark.parametrize("invalid_side", ["baseline", "current"])
def test_invalid_report_exits_two(
    tmp_path, invalid_xml, scenario, invalid_side
):
    """Invalid input on either side must fail closed."""
    baseline = _write(tmp_path / "baseline.xml", GOOD_XML)
    current = _write(tmp_path / "current.xml", GOOD_XML)

    invalid_path = baseline if invalid_side == "baseline" else current
    _write(invalid_path, invalid_xml)

    result = _run_cli(baseline, current, "--format", "json")

    assert result.returncode == 2, scenario
    assert result.stdout == ""
    assert "error" in result.stderr.lower()


def test_unreadable_report_path_exits_two(tmp_path):
    """A directory passed instead of a file must not succeed."""
    valid = _write(tmp_path / "valid.xml", GOOD_XML)

    result = _run_cli(valid, tmp_path, "--format", "json")

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip()


def test_no_regression_can_still_have_failing_tests(tmp_path):
    """Exit zero means no NEW regression, not all tests passing."""
    xml = (
        '<testsuite>'
        '<testcase classname="suite" name="already_broken">'
        '<failure/>'
        '</testcase>'
        '</testsuite>'
    )

    baseline = _write(tmp_path / "baseline.xml", xml)
    current = _write(tmp_path / "current.xml", xml)

    result = _run_cli(baseline, current, "--format", "json")

    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["summary"]["new_regressions"] == 0
    assert payload["summary"]["persistent_failures"] == 1


def test_added_failure_does_not_trigger_exit_one(tmp_path):
    """An added failing testcase is not a PASS regression."""
    baseline = _write(tmp_path / "baseline.xml", GOOD_XML)

    current = _write(
        tmp_path / "current.xml",
        '<testsuite>'
        '<testcase classname="suite" name="valid"/>'
        '<testcase classname="suite" name="new_failure">'
        '<failure/>'
        '</testcase>'
        '</testsuite>',
    )

    result = _run_cli(baseline, current, "--format", "json")

    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["summary"]["added"] == 1
    assert payload["summary"]["new_regressions"] == 0


def test_missing_failure_does_not_count_as_resolved(tmp_path):
    """A missing failure must not be reported as fixed."""
    baseline = _write(
        tmp_path / "baseline.xml",
        '<testsuite>'
        '<testcase classname="suite" name="valid"/>'
        '<testcase classname="suite" name="removed">'
        '<failure/>'
        '</testcase>'
        '</testsuite>',
    )

    current = _write(tmp_path / "current.xml", GOOD_XML)

    result = _run_cli(baseline, current, "--format", "json")

    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["summary"]["missing"] == 1
    assert payload["summary"]["resolved"] == 0
