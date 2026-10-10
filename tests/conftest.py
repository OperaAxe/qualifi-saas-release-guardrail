from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Generator
from pathlib import Path
from urllib import error, request

import pytest
from playwright.sync_api import Playwright

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def app_server() -> Generator[str, None, None]:
    port = _free_port()
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            request.urlopen(base_url + "/", timeout=1)
            break
        except (OSError, error.URLError):
            time.sleep(0.2)
    else:
        output = process.stdout.read() if process.stdout else ""
        process.kill()
        raise RuntimeError(f"FlowDesk did not start: {output}")
    yield base_url
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def clean_state(app_server: str, playwright: Playwright) -> Generator[None, None, None]:
    # Each test starts with a fresh Python process only once per session; clear the demo state through module import.
    from app.main import EVENTS, PROJECTS, SESSIONS

    EVENTS.clear()
    PROJECTS.clear()
    SESSIONS.clear()
    yield
