
"""Verify that unexpected CLI failures cannot masquerade as regressions."""


from regression_radar import cli
from regression_radar.models import TestCase as CaseModel


def _unexpected_failure(*args, **kwargs):
    """Simulate an unexpected internal execution error."""
    raise RuntimeError("simulated internal failure")


def test_unexpected_parser_exception_returns_two(
    monkeypatch, capsys
):
    """Unexpected parser errors must use exit code 2."""
    monkeypatch.setattr(cli, "parse_report", _unexpected_failure)

    exit_code = cli.main(["baseline.xml", "current.xml"])

    output = capsys.readouterr()

    assert exit_code == 2
    assert output.out == ""
    assert "error" in output.err.lower()


def test_unexpected_json_render_exception_returns_two(
    monkeypatch, capsys
):
    """An internal reporting failure must not signal a regression."""
    case = CaseModel(
        classname="suite",
        name="example",
        outcome="PASS",
    )

    monkeypatch.setattr(
        cli,
        "parse_report",
        lambda path: (case,),
    )
    monkeypatch.setattr(
        cli,
        "_json_report",
        _unexpected_failure,
    )

    exit_code = cli.main([
        "baseline.xml",
        "current.xml",
        "--format",
        "json",
    ])

    output = capsys.readouterr()

    assert exit_code == 2
    assert output.out == ""
    assert "error" in output.err.lower()
