import pytest


@pytest.mark.api
@pytest.mark.smoke
def test_api_can_create_and_read_project(playwright, app_server: str, clean_state: None) -> None:
    api = playwright.request.new_context(base_url=app_server)
    login = api.post("/login", form={"email": "owner@example.test", "password": "owner-pass"})
    assert login.status == 200 or login.status == 303
    created = api.post(
        "/api/projects", data={"name": "API project", "description": "Created through API"}
    )
    assert created.status == 201, created.text()
    projects = api.get("/api/projects")
    assert projects.status == 200
    assert any(item["name"] == "API project" for item in projects.json())


@pytest.mark.api
@pytest.mark.regression
def test_webhook_processing_is_idempotent(playwright, app_server: str, clean_state: None) -> None:
    api = playwright.request.new_context(base_url=app_server)
    payload = {"event_id": "evt-123", "event_type": "subscription.activated"}
    first = api.post("/api/webhooks/subscription", data=payload)
    second = api.post("/api/webhooks/subscription", data=payload)
    assert first.status == 200 and first.json()["status"] == "processed"
    assert second.status == 200 and second.json()["status"] == "duplicate"


@pytest.mark.api
@pytest.mark.regression
def test_unsupported_webhook_is_rejected(playwright, app_server: str, clean_state: None) -> None:
    api = playwright.request.new_context(base_url=app_server)
    response = api.post(
        "/api/webhooks/subscription", data={"event_id": "evt-bad", "event_type": "unknown"}
    )
    assert response.status == 400


@pytest.mark.api
@pytest.mark.regression
def test_invalid_webhook_does_not_consume_idempotency_key(
    playwright, app_server: str, clean_state: None
) -> None:
    api = playwright.request.new_context(base_url=app_server)
    event_id = "evt-retry-after-validation-failure"

    invalid = api.post(
        "/api/webhooks/subscription",
        data={"event_id": event_id, "event_type": "not-supported"},
    )
    valid_retry = api.post(
        "/api/webhooks/subscription",
        data={"event_id": event_id, "event_type": "subscription.activated"},
    )

    assert invalid.status == 400
    assert valid_retry.status == 200
    assert valid_retry.json()["status"] == "processed"


@pytest.mark.api
@pytest.mark.regression
def test_duplicate_valid_webhook_is_processed_only_once(
    playwright, app_server: str, clean_state: None
) -> None:
    api = playwright.request.new_context(base_url=app_server)
    payload = {"event_id": "evt-once-only", "event_type": "subscription.activated"}

    first = api.post("/api/webhooks/subscription", data=payload)
    duplicate = api.post("/api/webhooks/subscription", data=payload)

    assert first.status == 200
    assert first.json()["status"] == "processed"
    assert duplicate.status == 200
    assert duplicate.json()["status"] == "duplicate"
