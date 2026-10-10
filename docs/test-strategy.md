# Test strategy

## Scope

The suite tests FlowDesk's highest-risk demonstration journeys at two layers:

1. Browser journeys verify user-visible behavior and persistence.
2. API checks verify authentication, project state, entitlement boundaries, and webhook semantics.

## Test design

Each scenario has isolated state, a meaningful oracle, and a marker. Positive checks prove allowed behavior; negative checks prove that forbidden behavior stays forbidden. The API tests use Playwright's `APIRequestContext` through the pytest-playwright fixture.

## Evidence

Pytest emits JUnit XML. Playwright retains traces on failure and screenshots on failure. The report generator reads the JUnit file and makes a documented readiness decision.

## Next extensions

Add database-backed fixtures, contract tests, accessibility checks, cross-browser projects, and deployment smoke tests. These are planned extensions, not implemented claims.
