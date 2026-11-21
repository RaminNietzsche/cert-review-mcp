"""Release hygiene: runtime and package metadata must agree."""
from pathlib import Path

import cert_review


def test_version_matches_pyproject():
    root = Path(__file__).resolve().parents[1]
    for line in (root / "pyproject.toml").read_text().splitlines():
        if line.startswith("version = "):
            pkg_ver = line.split("=", 1)[1].strip().strip('"')
            break
    else:
        raise AssertionError("version not found in pyproject.toml")
    assert cert_review.__version__ == pkg_ver