# Learning guide

## What this project teaches

The guardrail combines UI and API checks because a browser assertion alone cannot always prove server state. API checks can prepare data and verify post-conditions; browser checks validate the customer-visible journey.

## Difficult scenarios

1. **Unauthenticated access:** the API must reject requests without a session.
2. **Persistence after refresh:** the UI must show the server-backed record again, not only a temporary DOM value.
3. **Entitlement denial:** the free plan must not receive a restricted feature.
4. **Duplicate webhook:** the same event ID must not be processed twice.
5. **Failure evidence:** a failed browser test should leave a screenshot/trace that explains the state.

## Interview questions

- Why test both through the browser and through the API? — They validate different layers and make state assertions stronger.
- Why is the webhook test idempotent? — Event delivery can be retried; duplicate processing can create billing or state errors.
- What makes a release not ready? — Any required check failure, regardless of the aggregate pass rate.
- What would you change for production? — Replace in-memory state, add stable test-data APIs, secrets handling, service contracts, and environment-aware CI.

## Limitations

The application is fictional and intentionally local. Passing tests demonstrate the implemented scenarios only; they do not prove complete product quality or security.
