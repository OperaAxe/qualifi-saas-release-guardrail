# QualiFi SaaS Release Guardrail

> **Playbook status: in progress.** I'm using a small fictional SaaS app to practise the path from manual testing to repeatable release checks. I’m still adding scenarios and tightening the report rules, so this is a working playbook—not a production-readiness claim.

[![CI](https://github.com/OperaAxe/qualifi-saas-release-guardrail/actions/workflows/ci.yml/badge.svg)](https://github.com/OperaAxe/qualifi-saas-release-guardrail/actions/workflows/ci.yml)

## What this project is for

FlowDesk is a demo app with login, projects, role/plan restrictions, and subscription webhooks. The useful part is the QA approach: start with a user journey, decide what would prove it worked, then turn important checks into regression tests and a release report.

## A real example in this repository: webhook retry

The demo accepts only supported subscription events. One regression scenario tests this sequence:

1. Send an event ID with an unsupported event type.
2. Confirm the request is rejected.
3. Retry the same ID with a supported event type.
4. Confirm the valid retry is processed.

The order matters. If the app records the event ID before validating the type, the valid retry can be mistaken for a duplicate. This scenario uses synthetic local data; it isn't a claim about a production payment system.

## Current coverage

- Login and session access
- Project creation and persistence after refresh
- Viewer/owner plan and role behaviour
- API validation and subscription webhook idempotency
- Release report decisions based on JUnit test results

The release report must not mark a run as ready if a required check fails—or if no tests passed. Test evidence should be real output, not a manually written green result.

## Run locally

Use Python 3.13 or newer.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
pytest
```

Start the demo app with:

```bash
python -m uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000. Demo accounts and their roles are in app/main.py.

## How I'm approaching QA

I want each check to have a clear question and a result that can be verified. A request returning 403 isn't always enough: when a forbidden action might have changed data, I read the record back and check for side effects. The same principle applies to release reporting—a green message is not evidence unless it came from the test run.

## Limits and next steps

This project uses a fictional app, synthetic records, and in-memory state. It does not certify a real SaaS service, replace a penetration test, or prove complete coverage. I'm still expanding the cases, checking CI behaviour, and improving the examples as I learn.

## Contact

- GitHub: [OperaAxe](https://github.com/OperaAxe)
- LinkedIn: [davidchristianj](https://linkedin.com/in/davidchristianj)
- Upwork: [Christian David](https://upwork.com/freelancers/~010e703beaa0687103)
