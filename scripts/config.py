"""Tek yerden profil ayarları: scripts/profile.json."""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "profile.json"), encoding="utf-8") as _f:
    PROFILE = json.load(_f)

USERNAME = PROFILE["username"]
DISPLAY_NAME = PROFILE["display_name"]
LOCATION = PROFILE["location"]
ROLE = PROFILE["role"]
INFO_ROWS = [tuple(row) for row in PROFILE["rows"]]


def resolve_username() -> str:
    env = os.environ.get("GH_PROFILE_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER")
    if env:
        return env.strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in repo:
        return repo.split("/", 1)[0]
    return USERNAME


def prompt_user() -> str:
    return resolve_username()
