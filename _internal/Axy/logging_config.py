"""Centralized logging configuration for Axy.

Call :func:`setup_logging` early in the application (e.g., in `main.py`).
Controls via environment variables:
- LOG_LEVEL (DEBUG, INFO, WARNING, ERROR) default INFO
- LOG_JSON (1/0) whether to output a compact key=value style (default 0)
"""
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

import logging
import os
from typing import Optional


def setup_logging(level: Optional[str] = None, json: Optional[bool] = None) -> None:
    """Configure root logger for the application.

    - level: optional override for level (string). If None, reads env LOG_LEVEL.
    - json: if True, uses a compact key=value formatter. If None, reads env LOG_JSON.
    """
    lvl = (level or os.environ.get("LOG_LEVEL") or "INFO").upper()
    use_json = json if json is not None else os.environ.get("LOG_JSON", "0") in ("1", "true", "True")

    numeric = getattr(logging, lvl, logging.INFO)

    handler = logging.StreamHandler()
    if use_json:
        fmt = "%(asctime)s level=%(levelname)s name=%(name)s msg=%(message)s"
    else:
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric)
    # Remove existing handlers to avoid duplicate logs when called multiple times
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
