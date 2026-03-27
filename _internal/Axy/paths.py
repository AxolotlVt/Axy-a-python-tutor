
# ==============================================================================
# Copyright (c) 2026 Axo. All rights reserved.
# 
# This software is proprietary and confidential.
# Unauthorized copying, distribution, modification, or use of this file,
# via any medium, is strictly prohibited without the express written 
# consent of the developer.
# 
# AXY - Local Python Mentor
# ==============================================================================
from __future__ import annotations
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

APP_NAME = "Axy"


def is_frozen_app() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_bundle_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def _get_user_app_root() -> Path:
    if os.name == "nt":
        base = (
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or str(Path.home() / "AppData" / "Local")
        )
        return Path(base) / APP_NAME

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME

    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / APP_NAME
    return Path.home() / ".local" / "share" / APP_NAME


def get_runtime_root() -> Path:
    override = os.environ.get("AXY_RUNTIME_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    if is_frozen_app():
        return _get_user_app_root()

    return get_bundle_root()


def get_data_dir() -> Path:
    override = os.environ.get("AXY_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return get_runtime_root() / "data"


def get_streamlit_dir() -> Path:
    return get_runtime_root() / ".streamlit"


def get_chats_dir() -> Path:
    return get_data_dir() / "chats"


def get_archive_dir() -> Path:
    return get_data_dir() / "archive"


def get_users_path() -> Path:
    return get_data_dir() / "users.json"


def get_chat_history_path() -> Path:
    return get_data_dir() / "chat_history.json"


def get_memories_path() -> Path:
    return get_data_dir() / "memories.json"


def get_spotify_key_path() -> Path:
    return get_data_dir() / "spotify_key.key"


def get_spotify_secret_path() -> Path:
    return get_data_dir() / "spotify_secret.enc"


def get_spotify_cache_path() -> Path:
    return get_data_dir() / ".spotifycache"


def get_main_script_path() -> Path:
    return get_bundle_root() / "main.py"


def _resource_data_path(*parts: str) -> Path:
    return get_bundle_root() / "data" / Path(*parts)


def _resource_streamlit_config() -> Path:
    return get_bundle_root() / ".streamlit" / "config.toml"


def _write_default_json(path: Path, payload: Any) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _copy_if_missing(source: Path, destination: Path) -> None:
    if source.exists() and not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def prepare_runtime_environment() -> None:
    data_dir = get_data_dir()
    chats_dir = get_chats_dir()
    archive_dir = get_archive_dir()
    streamlit_dir = get_streamlit_dir()

    data_dir.mkdir(parents=True, exist_ok=True)
    chats_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    streamlit_dir.mkdir(parents=True, exist_ok=True)

    _write_default_json(get_users_path(), {})
    _write_default_json(get_chat_history_path(), [])
    _write_default_json(get_memories_path(), {})

    _copy_if_missing(_resource_streamlit_config(), streamlit_dir / "config.toml")
    _copy_if_missing(_resource_data_path("spotify_key.key"), get_spotify_key_path())
    _copy_if_missing(_resource_data_path("spotify_secret.enc"), get_spotify_secret_path())
