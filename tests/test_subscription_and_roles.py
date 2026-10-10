import pytest
from playwright.sync_api import Page, expect


def login(page: Page, base: str, email: str, password: str) -> None:
    page.goto(base + "/login")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Log in").click()


@pytest.mark.smoke
def test_pro_plan_sees_restricted_feature(page: Page, app_server: str, clean_state: None) -> None:
    login(page, app_server, "owner@example.test", "owner-pass")
    expect(page.get_by_test_id("pro-feature")).to_have_text("Pro analytics enabled")


@pytest.mark.regression
def test_free_plan_does_not_receive_restricted_entitlement(
    page: Page, app_server: str, clean_state: None
) -> None:
    login(page, app_server, "viewer@example.test", "viewer-pass")
    expect(page.get_by_test_id("pro-feature")).to_have_text(
        "Pro analytics unavailable on your plan"
    )


@pytest.mark.regression
def test_viewer_cannot_create_project(page: Page, app_server: str, clean_state: None) -> None:
    login(page, app_server, "viewer@example.test", "viewer-pass")
    response = page.request.post(app_server + "/api/projects", data={"name": "Forbidden"})
    assert response.status == 403
