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
