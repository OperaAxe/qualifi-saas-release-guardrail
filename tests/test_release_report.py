import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_report(tmp_path: Path, xml: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    source = tmp_path / "junit.xml"
    source.write_text(xml, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_release_report.py"), str(source)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    report = json.loads((tmp_path / "release-report.json").read_text(encoding="utf-8"))
    return result, report


def test_empty_junit_report_is_not_ready(tmp_path: Path) -> None:
    result, report = run_report(
        tmp_path, '<testsuite name="pytest" tests="0" failures="0" errors="0"/>'
    )

    assert report["readiness"] == "not_ready"
    assert report["counts"] == {"passed": 0, "failed": 0, "skipped": 0}
    assert result.returncode == 1


def test_any_failed_required_check_blocks_release(tmp_path: Path) -> None:
    xml = """<testsuite name="pytest" tests="2" failures="1" errors="0" skipped="0">
      <testcase classname="test_login" name="valid_login"/>
      <testcase classname="test_checkout" name="checkout_validation">
        <failure message="Expected confirmation, got validation error"/>
      </testcase>
    </testsuite>"""
    result, report = run_report(tmp_path, xml)

    assert report["readiness"] == "not_ready"
    assert report["counts"]["passed"] == 1
    assert report["counts"]["failed"] == 1
    assert result.returncode == 1


def test_all_passed_checks_allow_ready_decision(tmp_path: Path) -> None:
    xml = """<testsuite name="pytest" tests="2" failures="0" errors="0" skipped="0">
      <testcase classname="test_login" name="valid_login"/>
      <testcase classname="test_cart" name="remove_item"/>
    </testsuite>"""
    result, report = run_report(tmp_path, xml)

    assert report["readiness"] == "ready"
    assert report["counts"]["passed"] == 2
    assert result.returncode == 0
