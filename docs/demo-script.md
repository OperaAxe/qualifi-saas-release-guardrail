# Demo script

1. Show the README and explain that FlowDesk is fictional.
2. Run `pytest -m smoke` and show the browser/API checks.
3. Open the dashboard with the synthetic owner account and create a project.
4. Refresh and show that the project remains.
5. Run `pytest -m api` and explain the duplicate webhook oracle.
6. Run `python tools/generate_release_report.py test-results/junit.xml` and open `release-report.md`.
7. Explain how a deliberately failing assertion would produce `not_ready`, a screenshot, a trace, and a non-zero CI exit.
