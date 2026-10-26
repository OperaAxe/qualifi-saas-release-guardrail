from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import Cookie, FastAPI, Form, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="FlowDesk Demo SaaS", version="0.1.0")

USERS = {
    "owner@example.test": {"password": "owner-pass", "role": "owner", "plan": "pro"},
    "editor@example.test": {"password": "editor-pass", "role": "editor", "plan": "pro"},
    "viewer@example.test": {"password": "viewer-pass", "role": "viewer", "plan": "free"},
}
SESSIONS: dict[str, str] = {}
PROJECTS: dict[str, dict[str, Any]] = {}
EVENTS: dict[str, dict[str, Any]] = {}


class ProjectIn(BaseModel):
    name: str
    description: str = ""


def current_user(session: str | None) -> tuple[str, dict[str, Any]] | None:
    email = SESSIONS.get(session or "")
    return (email, USERS[email]) if email else None


def require_user(session: str | None) -> tuple[str, dict[str, Any]]:
    user = current_user(session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return user


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<!doctype html><html><head><title>{title}</title>
    <style>body{{font-family:system-ui;max-width:760px;margin:40px auto;padding:0 16px}}
    label,input,textarea,button{{display:block;margin:8px 0}}input,textarea{{width:100%;padding:8px}}
    button{{padding:8px 14px}}.card{{border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0}}
    .muted{{color:#666}}</style></head><body>{body}</body></html>""")


@app.get("/", response_class=HTMLResponse)
def home(session: str | None = Cookie(default=None, alias="flowdesk_session")) -> HTMLResponse:
    user = current_user(session)
    if not user:
        return page(
            "FlowDesk Login",
            "<h1>FlowDesk</h1><p>Release guardrail demo application.</p><a href='/login'>Log in</a>",
        )
    email, details = user
    projects = [p for p in PROJECTS.values() if p["owner"] == email]
    cards = "".join(
        f"<li data-project='{p['id']}'><strong>{p['name']}</strong>: {p['description']}</li>"
        for p in projects
    )
    restricted = (
        "<p data-testid='pro-feature'>Pro analytics enabled</p>"
        if details["plan"] == "pro"
        else "<p data-testid='pro-feature'>Pro analytics unavailable on your plan</p>"
    )
    return page(
        "FlowDesk Dashboard",
        f"<h1>FlowDesk dashboard</h1><p data-testid='user'>{email} ({details['role']})</p>{restricted}<form method='post' action='/logout'><button>Log out</button></form><h2>Projects</h2><form method='post' action='/projects'><label>Name<input name='name' required></label><label>Description<textarea name='description'></textarea></label><button>Create project</button></form><ul data-testid='projects'>{cards}</ul>",
    )


@app.get("/login", response_class=HTMLResponse)
def login_page() -> HTMLResponse:
    return page(
        "FlowDesk Login",
        "<h1>Log in to FlowDesk</h1><form method='post' action='/login'><label>Email<input name='email' type='email' required></label><label>Password<input name='password' type='password' required></label><button>Log in</button></form><p class='muted'>Demo users: owner@example.test / owner-pass</p>",
    )


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)) -> RedirectResponse:
    if email not in USERS or USERS[email]["password"] != password:
        return RedirectResponse("/login?error=invalid", status_code=303)
    token = uuid4().hex
    SESSIONS[token] = email
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("flowdesk_session", token, httponly=True, samesite="lax")
    return response


@app.post("/logout")
def logout(
    response: Response, session: str | None = Cookie(default=None, alias="flowdesk_session")
) -> RedirectResponse:
    SESSIONS.pop(session or "", None)
    result = RedirectResponse("/login", status_code=303)
    result.delete_cookie("flowdesk_session")
    return result


@app.get("/api/me")
def me(session: str | None = Cookie(default=None, alias="flowdesk_session")) -> dict[str, Any]:
    email, details = require_user(session)
    return {"email": email, **{k: details[k] for k in ("role", "plan")}}


@app.get("/api/projects")
def list_projects(
    session: str | None = Cookie(default=None, alias="flowdesk_session"),
) -> list[dict[str, Any]]:
    email, _ = require_user(session)
    return [p for p in PROJECTS.values() if p["owner"] == email]


@app.post("/api/projects", status_code=201)
def create_project(
    project: ProjectIn, session: str | None = Cookie(default=None, alias="flowdesk_session")
) -> dict[str, Any]:
    email, details = require_user(session)
    if details["role"] == "viewer":
        raise HTTPException(status_code=403, detail="Viewer cannot create projects")
    item = {
        "id": uuid4().hex,
        "owner": email,
        "name": project.name,
        "description": project.description,
        "created_at": datetime.now(UTC).isoformat(),
    }
    PROJECTS[item["id"]] = item
    return item


@app.post("/projects")
def create_project_form(
    name: str = Form(...),
    description: str = Form(""),
    session: str | None = Cookie(default=None, alias="flowdesk_session"),
) -> RedirectResponse:
    create_project(ProjectIn(name=name, description=description), session)
    return RedirectResponse("/", status_code=303)


@app.get("/api/analytics")
def analytics(
    session: str | None = Cookie(default=None, alias="flowdesk_session"),
) -> dict[str, str]:
    _, details = require_user(session)
    if details["plan"] != "pro":
        raise HTTPException(status_code=402, detail="Active Pro subscription required")
    return {"status": "enabled", "metric": "weekly_active_users"}


class WebhookIn(BaseModel):
    event_id: str
    event_type: str


@app.post("/api/webhooks/subscription")
def subscription_webhook(event: WebhookIn) -> dict[str, str]:
    # Validate before reserving the idempotency key. A bad first delivery
    # must not make a later valid retry look like a duplicate.
    if event.event_type not in {"subscription.activated", "subscription.failed"}:
        raise HTTPException(status_code=400, detail="Unsupported event")
    if event.event_id in EVENTS:
        return {"status": "duplicate", "event_id": event.event_id}
    EVENTS[event.event_id] = {"type": event.event_type}
    return {"status": "processed", "event_id": event.event_id}
