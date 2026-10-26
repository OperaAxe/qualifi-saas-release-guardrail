from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def build_report(source: Path) -> dict:
    root = ET.parse(source).getroot()
    cases: list[dict[str, str]] = []

    for case in root.iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        result = (
            "failed"
            if failure is not None or error is not None
            else "skipped"
            if skipped is not None
            else "passed"
        )
        cases.append(
            {
                "name": case.attrib.get("name", "unknown"),
                "classname": case.attrib.get("classname", ""),
                "status": result,
            }
        )

    counts = {
        key: sum(item["status"] == key for item in cases)
        for key in ("passed", "failed", "skipped")
    }
    # An empty report is not evidence that a release is safe. Require at least
    # one passed check and no failures before describing this demo as ready.
    ready = counts["failed"] == 0 and counts["passed"] > 0

    return {
        "readiness": "ready" if ready else "not_ready",
        "rules": [
            "A release is not ready when any required automated check fails.",
            "A report with no passed test cases is not evidence of readiness.",
        ],
        "counts": counts,
        "checks": cases,
    }


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "test-results/junit.xml")
    output_json = Path("release-report.json")
    output_md = Path("release-report.md")
    if not source.exists():
        print(f"Missing test report: {source}")
        return 2

    report = build_report(source)
    output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    counts = report["counts"]
    lines = [
        "# FlowDesk release-readiness report",
        "",
        f"**Decision:** `{report['readiness']}`",
        "",
        "## Actual test results",
        "",
        f"- Passed: {counts['passed']}",
        f"- Failed: {counts['failed']}",
        f"- Skipped: {counts['skipped']}",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{item['status']}` — {item['classname']}::{item['name']}"
        for item in report["checks"]
    )
    lines += [
        "",
        "## Decision rule",
        "",
        "This report is generated from the JUnit XML produced by the test run. "
        "It does not infer readiness from a percentage or from a manually written example.",
    ]
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_json} and {output_md}; decision={report['readiness']}")
    return 0 if report["readiness"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
