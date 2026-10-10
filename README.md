# QualiFi SaaS Release Guardrail

A **real, local demonstration project** showing how a QA engineer can protect critical SaaS workflows before release. It builds and tests a fictional product called **FlowDesk**; it is not a production application or a client engagement.

The project demonstrates Python, Playwright browser automation, Playwright API testing, business-journey regression coverage, CI, failure evidence, and a release-readiness report generated from actual JUnit results.

## What it protects

- Authentication and protected-page access
- Project creation and persistence
- Subscription entitlement boundaries
- Owner/editor/viewer permission behavior
- Simulated subscription webhook processing and duplicate-event handling

## Architecture

- `app/main.py` — small FastAPI demonstration SaaS with in-memory state
- `tests/` — browser and API tests grouped by business journey
- `tests/conftest.py` — starts an isolated local server for the test session
- `tools/generate_release_report.py` — converts the real JUnit output into JSON and Markdown
- `.github/workflows/ci.yml` — installs Python/Playwright, runs tests, and uploads evidence

The demo deliberately uses in-memory state and fictional credentials so it is safe and free to run. It does not implement real payments.

## Setup

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Bash

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Run the demo application

```bash
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Demo accounts are documented in the login page and are intentionally synthetic.

## Run tests

```bash
pytest
python tools/generate_release_report.py test-results/junit.xml
```

Useful selections:

```bash
pytest -m smoke
pytest -m api
pytest tests/test_core_workflow.py
```

On a failed Playwright test, inspect `test-results/` for screenshots and traces. Open a trace with `playwright show-trace path/to/trace.zip` or use the local Trace Viewer. The CI workflow uploads these files as an artifact.

## Release decision

The report generator marks the release `not_ready` if any test case fails. A high pass percentage does not override a failed required check. The report is derived from the JUnit file produced by the test runner; no result is fabricated.

## CI behavior

GitHub Actions runs on pushes and pull requests to `main`. It installs Python 3.13, installs Chromium with OS dependencies, runs the suite, generates the report even if tests fail, and uploads JUnit results, screenshots, traces, and reports. The workflow has read-only repository permissions.

## Failure diagnosis

- **Test failure:** the application returned behavior different from the asserted oracle.
- **Application defect:** the test is reproducible and the implementation violates the documented behavior.
- **Environment problem:** the browser, dependency, port, or process could not start.
- **Potential flake:** reruns pass without a code change; investigate timing, isolation, and test data before suppressing it.

## Limitations

This is a portfolio demonstration, not a production security review, performance benchmark, payment integration, or claim of complete coverage. The in-memory app is intentionally small. A production guardrail would add persistent test data isolation, secrets management, service contracts, observability, and deployment-environment coverage.

See the learning and demo documents for interview preparation and a screen-share walkthrough.
