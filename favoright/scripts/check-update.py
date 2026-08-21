#!/usr/bin/env python3
"""Check the published Favoright skill version once per day without updating it."""

from __future__ import annotations

import argparse
import base64
import json
import os
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

REPOSITORY = "designly1/favoright-skill"
VERSION_PATH = "favoright/VERSION"
CHECK_INTERVAL = timedelta(days=1)


def utc_now() -> datetime:
    return datetime.now(UTC)


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def version_key(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.strip().removeprefix("v").split("."))
    except ValueError as error:
        raise ValueError(f"Invalid numeric version: {value!r}") from error


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "favoright-skill-update-checker"})
    with urlopen(request, timeout=15) as response:  # noqa: S310 - fixed GitHub API origin
        return json.load(response)


def read_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as temporary:
        json.dump(state, temporary, indent=2, sort_keys=True)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Ignore the daily check interval.")
    parser.add_argument("--state-path", type=Path, help="Override the persisted state path.")
    arguments = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    installed_version = (skill_dir / "VERSION").read_text().strip()
    codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    state_path = arguments.state_path or codex_root / "state" / "favoright-skill-update.json"
    state = read_state(state_path)
    now = utc_now()
    last_checked = parse_timestamp(state.get("lastCheckedAt"))

    if not arguments.force and last_checked and now - last_checked < CHECK_INTERVAL:
        print(json.dumps({"status": "skipped", "last_checked_at": state["lastCheckedAt"], "state_path": str(state_path)}))
        return 0

    content = fetch_json(f"https://api.github.com/repos/{REPOSITORY}/contents/{VERSION_PATH}?ref=main")
    remote_version = base64.b64decode(content["content"]).decode().strip()
    commit = fetch_json(f"https://api.github.com/repos/{REPOSITORY}/commits/main")["sha"]
    update_available = version_key(remote_version) > version_key(installed_version)
    needs_notification = update_available and state.get("lastNotifiedVersion") != remote_version
    new_state = {
        **state,
        "lastCheckedAt": now.isoformat(),
        "installedVersion": installed_version,
        "remoteVersion": remote_version,
        "remoteCommit": commit,
    }
    if needs_notification:
        new_state["lastNotifiedVersion"] = remote_version
    write_state(state_path, new_state)
    print(json.dumps({
        "status": "checked",
        "installed_version": installed_version,
        "remote_version": remote_version,
        "remote_commit": commit,
        "update_available": update_available,
        "needs_notification": needs_notification,
        "state_path": str(state_path),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
