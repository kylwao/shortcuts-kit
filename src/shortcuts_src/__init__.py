"""shortcuts-src: decompile / compile Apple Shortcuts between signed .shortcut
files (or iCloud share URLs) and editable XML / JSON source code.

The package version is single-sourced from ``pyproject.toml``: installed
packages read it via :func:`importlib.metadata.version`; when running from a
source checkout (e.g. the ``scripts/install.sh`` launcher) it is parsed from
the adjacent ``pyproject.toml``. Falls back to ``"0.0.0+local"``.
"""

from __future__ import annotations

import re
from pathlib import Path

try:  # Python 3.8+
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version
except ImportError:  # pragma: no cover - only triggers on Py 3.7 local dev
    _pkg_version = None  # type: ignore[assignment]

    class PackageNotFoundError(Exception):  # type: ignore[no-redef]
        pass


def _version_from_checkout() -> str:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    try:
        match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"), re.M)
    except OSError:
        return "0.0.0+local"
    return f"{match.group(1)}+checkout" if match else "0.0.0+local"


def _resolve_version() -> str:
    if (Path(__file__).resolve().parents[2] / "pyproject.toml").is_file():
        return _version_from_checkout()
    if _pkg_version is None:
        return "0.0.0+local"
    try:
        return _pkg_version("shortcuts-src")
    except PackageNotFoundError:
        return "0.0.0+local"


__version__ = _resolve_version()

__all__ = ["__version__"]
