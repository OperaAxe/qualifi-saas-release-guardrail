# Manual QA walkthrough: FlowDesk release guardrail

Use this as a five-minute screen-share walkthrough. Start with the product behavior, then show how the checks protect it.

## 1. Set the context

“FlowDesk is fictional. I’m not presenting it as a finished SaaS product. I’m using it to show how I test the workflows that would affect users, support volume, and revenue.”

## 2. Login and logout

Open the app. Log in with the synthetic owner account shown on the login page. Confirm the dashboard appears. Log out. Try to open the dashboard again.

Ask: **What should happen if a session expires or logout is incomplete?**

## 3. Create and keep a project

Create a project named `Release checklist`. Confirm it appears. Refresh the page and confirm it is still there.

Ask: **Did the product save the object, or did it only show a success message?**

## 4. Check the user boundary

Log in as the viewer. Confirm the viewer can see the allowed dashboard state but cannot create a project. The test suite repeats that forbidden action through the API, because a hidden button is not server-side authorization.

## 5. Check subscription behavior

Compare the owner’s Pro state with the viewer’s Free state. Confirm the restricted feature has a clear message and that the API also protects the entitlement.

## 6. Check the webhook edge case

Send the same subscription event twice. The first request should process. The duplicate should be reported as a duplicate rather than applying the event again.

## 7. Show the automation

Run `pytest -m smoke`, then open the test results. Explain that the browser tests replay the user journey and the API tests check the rules behind the UI.

## 8. Show the release decision

Run `python tools/generate_release_report.py test-results/junit.xml`. Open `release-report.md`. Explain that a required failure produces `not_ready`; the report is derived from the JUnit output, not written by hand.

## The line to use in an interview

“I start with the workflow manually so I understand the user risk. I automate the checks that are expensive to repeat, and I keep the assertion tied to a business outcome—like data surviving refresh, a viewer being denied by the API, or a duplicate subscription event not creating a second side effect.”
