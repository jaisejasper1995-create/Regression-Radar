
"""Black-box tests for Regression Radar's command-line interface."""

import json
import subprocess
import sys

import pytest


def _write_report(path, cases):
    """Write a controlled JUnit report."""
    lines = ["<testsuite>"]

    for name, outcome in cases:
        lines.append(f'<testcase classname="suite" name="{name}">')

        if outcome == "FAIL":
            lines.append("<failure/>")
        elif outcome == "ERROR":
            lines.append("<error/>")
        elif outcome == "SKIP":
            lines.append("<skipped/>")

        lines.append("</testcase>")

    lines.append("</testsuite>")
    path.write_text("".join(lines), encoding="utf-8")


def _run_cli(*arguments):
    """Execute the CLI through the installed Python environment."""
    return subprocess.run(
        [sys.executable, "-m", "regression_radar.cli", *map(str, arguments)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_returns_zero_without_regressions(tmp_path):
    baseline = tmp_path / "baseline.xml"
    current = tmp_path / "current.xml"

    _write_report(baseline, [("one", "PASS")])
    _write_report(current, [("one", "PASS")])

    result = _run_cli(baseline, current)

    assert result.returncode == 0
    assert "regression" in result.stdout.lower()


def test_cli_returns_one_for_new_regression(tmp_path):
    baseline = tmp_path / "baseline.xml"
    current = tmp_path / "current.xml"

    _write_report(baseline, [("one", "PASS")])
    _write_report(current, [("one", "FAIL")])

    result = _run_cli(baseline, current)

    assert result.returncode == 1
    assert "NEW_REGRESSION" in result.stdout


def test_cli_returns_two_for_invalid_input(tmp_path):
    baseline = tmp_path / "baseline.xml"
    current = tmp_path / "missing.xml"

    _write_report(baseline, [("one", "PASS")])

    result = _run_cli(baseline, current)

    assert result.returncode == 2
    assert result.stderr.strip()


def test_cli_json_is_parseable(tmp_path):
    baseline = tmp_path / "baseline.xml"
    current = tmp_path / "current.xml"

    _write_report(baseline, [("one", "PASS")])
    _write_report(current, [("one", "ERROR")])

    result = _run_cli(baseline, current, "--format", "json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)

    assert payload["summary"]["new_regressions"] == 1
    assert payload["transitions"][0]["classification"] == "NEW_REGRESSION"


def test_cli_json_is_deterministic(tmp_path):
    baseline = tmp_path / "baseline.xml"
    current = tmp_path / "current.xml"

    _write_report(baseline, [("z", "PASS"), ("a", "PASS")])
    _write_report(current, [("a", "FAIL"), ("z", "PASS")])

    first = _run_cli(baseline, current, "--format", "json")
    second = _run_cli(baseline, current, "--format", "json")

    assert first.returncode == second.returncode == 1
    assert first.stdout == second.stdout


@pytest.mark.parametrize(
    "arguments",
    [
        (),
        ("only-one-report.xml",),
        ("--format", "invalid"),
    ],
)
def test_cli_rejects_invalid_arguments(arguments):
    result = _run_cli(*arguments)

    assert result.returncode == 2


def test_cli_reports_added_and_missing_separately(tmp_path):
    baseline = tmp_path / "baseline.xml"
    current = tmp_path / "current.xml"

    _write_report(
        baseline,
        [("unchanged", "PASS"), ("removed", "FAIL")],
    )
    _write_report(
        current,
        [("unchanged", "PASS"), ("added", "FAIL")],
    )

    result = _run_cli(baseline, current, "--format", "json")

    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["summary"]["new_regressions"] == 0
    assert payload["summary"]["added"] == 1
    assert payload["summary"]["missing"] == 1
