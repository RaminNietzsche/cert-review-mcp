"""Locate the data and profile directories.

Resolution order: $CERT_REVIEW_HOME, then the repository root (editable
install or running from a checkout).
"""
from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    env = os.environ.get("CERT_REVIEW_HOME")
    if env:
        return Path(env)
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "data" / "rules.json").exists():
        return checkout
    import sys
    return Path(sys.prefix) / "share" / "cert-review"


def data_dir() -> Path:
    return home() / "data"


def profiles_dir() -> Path:
    return home() / "profiles"
