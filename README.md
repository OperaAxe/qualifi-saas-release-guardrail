# QualiFi SaaS Release Guardrail

[![CI](https://github.com/OperaAxe/qualifi-saas-release-guardrail/actions/workflows/ci.yml/badge.svg)](https://github.com/OperaAxe/qualifi-saas-release-guardrail/actions/workflows/ci.yml)

A small fictional SaaS app used to connect user-facing checks, API regression tests, webhook handling, and release decisions. The aim is to make the release report depend on test evidence rather than a manually supplied green status.

## A regression worth catching

The demo handles subscription webhooks. One test sends an event ID with an unsupported event type, confirms that the request is rejected, and then retries the same ID with a supported event.

That retry should be processed. If the app records an event ID before validating the event type, the invalid request can make a later valid retry look like a duplicate.

## What is covered

- Login and session access
- Project creation and persistence after refresh
- Role and plan restrictions
- API validation and webhook idempotency
- Release-report decisions based on JUnit results

The report must not mark a run ready when required tests fail or when no tests have passed.

## Run locally

Requires Python 3.11 or newer.

```bash
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies, create the report directory, and run the tests:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "from pathlib import Path; Path('test-results').mkdir(exist_ok=True)"
python -m playwright install chromium
pytest
```

Start the demo application with:

```bash
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Demo users and roles are defined in `app/main.py`.

## Scope

**Status: in development.** The application uses synthetic records and in-memory state. It is a local testing exercise, not a payment integration or a claim that a real SaaS product is production-ready.
