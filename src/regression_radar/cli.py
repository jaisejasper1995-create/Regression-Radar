
"""Command-line interface and deterministic reports for Regression Radar."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from regression_radar.comparison import ComparisonResult, compare_reports
from regression_radar.parser import parse_report


def _build_summary(result: ComparisonResult) -> dict[str, int]:
    """Derive counts from normalized comparison records."""
    return {
        "new_regressions": len(result.new_regressions),
        "resolved": len(result.resolved),
        "persistent_failures": len(result.persistent_failures),
        "unchanged_pass": sum(
            item.classification == "UNCHANGED_PASS"
            for item in result.transitions
        ),
        "unchanged_skips": len(result.unchanged_skips),
        "skip_transitions": len(result.skip_transitions),
        "added": len(result.added),
        "missing": len(result.missing),
        "matched": len(result.transitions),
        "baseline_total": len(result.transitions) + len(result.missing),
        "current_total": len(result.transitions) + len(result.added),
    }


def _json_report(result: ComparisonResult) -> str:
    """Produce stable, machine-readable JSON output."""
    payload = {
        "schema_version": "1.0",
        "summary": _build_summary(result),
        "transitions": [
            asdict(item) for item in result.transitions
        ],
        "added": [
            asdict(item) for item in result.added
        ],
        "missing": [
            asdict(item) for item in result.missing
        ],
    }

    return json.dumps(payload, indent=2, ensure_ascii=True)


def _text_report(result: ComparisonResult) -> str:
    """Produce a deterministic human-readable comparison report."""
    summary = _build_summary(result)

    lines = [
        "Regression Radar v0.1.0",
        "JUnit XML regression comparison",
        "",
        "Summary:",
    ]

    for key, value in summary.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Transitions:"])

    for item in result.transitions:
        classname, name = item.identity
        lines.append(
            f"  {classname}::{name} "
            f"{item.before} -> {item.after} "
            f"[{item.classification}]"
        )

    lines.append("")
    lines.append("Added tests:")

    for item in result.added:
        lines.append(
            f"  {item.classname}::{item.name} [{item.outcome}]"
        )

    lines.append("")
    lines.append("Missing tests:")

    for item in result.missing:
        lines.append(
            f"  {item.classname}::{item.name} [{item.outcome}]"
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run comparison and return the documented exit code."""
    parser = argparse.ArgumentParser(
        prog="regression-radar",
        description="Compare two JUnit XML reports for new regressions.",
    )

    parser.add_argument(
        "baseline",
        type=Path,
        help="Path to the baseline JUnit XML report",
    )
    parser.add_argument(
        "current",
        type=Path,
        help="Path to the current JUnit XML report",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args(argv)

    try:
        baseline_cases = parse_report(args.baseline)
        current_cases = parse_report(args.current)

        result = compare_reports(
            baseline_cases,
            current_cases,
        )
    except (OSError, ValueError) as exc:
        print(f"Regression Radar error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(_json_report(result))
    else:
        print(_text_report(result))

    return 1 if result.new_regressions else 0


if __name__ == "__main__":
    sys.exit(main())
