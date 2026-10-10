import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_user_can_login_and_logout(page: Page, app_server: str, clean_state: None) -> None:
    page.goto(app_server + "/login")
    page.get_by_label("Email").fill("owner@example.test")
    page.get_by_label("Password").fill("owner-pass")
    page.get_by_role("button", name="Log in").click()
    expect(page.get_by_test_id("user")).to_contain_text("owner@example.test")
    page.get_by_role("button", name="Log out").click()
    expect(page).to_have_url(app_server + "/login")
    page.goto(app_server + "/")
    expect(page.get_by_role("link", name="Log in")).to_be_visible()


@pytest.mark.regression
def test_protected_api_rejects_anonymous_request(
    playwright, app_server: str, clean_state: None
) -> None:
    response = playwright.request.new_context(base_url=app_server).get("/api/me")
    assert response.status == 401
