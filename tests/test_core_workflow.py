import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_user_creates_project_and_data_persists_after_refresh(
    page: Page, app_server: str, clean_state: None
) -> None:
    page.goto(app_server + "/login")
    page.get_by_label("Email").fill("owner@example.test")
    page.get_by_label("Password").fill("owner-pass")
    page.get_by_role("button", name="Log in").click()
    page.get_by_label("Name").fill("Release smoke suite")
    page.get_by_label("Description").fill("Critical revenue workflow")
    page.get_by_role("button", name="Create project").click()
    expect(page.get_by_test_id("projects")).to_contain_text("Release smoke suite")
    page.reload()
    expect(page.get_by_test_id("projects")).to_contain_text("Critical revenue workflow")
