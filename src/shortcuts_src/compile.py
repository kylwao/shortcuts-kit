"""compile: edited XML / JSON source  ->  signed .shortcut file.

On macOS 13+ the official ``shortcuts`` CLI ships at ``/usr/bin/shortcuts``
and exposes ``shortcuts sign -m <mode> -i <in> -o <out>`` which wraps an
unsigned binary plist into an AEA-signed ``.shortcut``. We shell out to
it rather than reimplementing AEA signing.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from . import plist_io
from .profile import (
    DENSITIES,
    DENSITY_BRANCH,
    inject_dev_telemetry,
)

_SHORTCUTS_BIN = "/usr/bin/shortcuts"
_VALID_MODES = ("anyone", "people-who-know-me")
_VALID_PROFILES = ("dev", "release")


def _resolve_shortcuts_cli() -> str:
    path = shutil.which("shortcuts") or (_SHORTCUTS_BIN if Path(_SHORTCUTS_BIN).exists() else None)
    if not path:
        raise RuntimeError(
            "The macOS `shortcuts` CLI was not found. It ships with macOS 13+. "
            "If you only need an unsigned file, re-run with --allow-unsigned."
        )
    return path


def _load_shortcut(source_path: Path) -> dict:
    data = source_path.read_bytes()
    obj = plist_io.loads(data)
    if not isinstance(obj, dict):
        raise ValueError(f"{source_path}: top-level source value is not a dict")
    if "WFWorkflowActions" not in obj:
        raise ValueError(
            f"{source_path}: missing WFWorkflowActions (this doesn't look like a shortcut source file)"
        )
    return obj


def _infer_category(source_path: Path) -> str:
    """Infer a category name from the source path, defaulting to "misc".

    Looks for ``MyShortcuts/<category>/...`` in the path; falls back to the
    deepest folder name that isn't a version directory like ``V0.1``.
    """
    parts = source_path.resolve().parts
    if "MyShortcuts" in parts:
        idx = parts.index("MyShortcuts")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    for name in reversed(parts[:-1]):
        if not (name.startswith("V") and name[1:2].isdigit()):
            return name
    return "misc"


def compile_source(
    source: str,
    *,
    out_path: Optional[str] = None,
    mode: str = "anyone",
    keep_unsigned: bool = False,
    allow_unsigned: bool = False,
    profile: str = "release",
    telemetry: str = DENSITY_BRANCH,
    category: Optional[str] = None,
    shortcut_name: Optional[str] = None,
) -> Path:
    """Compile an edited XML / JSON shortcut back into a ``.shortcut``.

    Returns the path to the output file. When ``allow_unsigned=True`` the
    output is a raw unsigned bplist with a ``.shortcut`` extension;
    otherwise it is passed through ``shortcuts sign``.

    ``profile='dev'`` injects telemetry actions (see
    :mod:`shortcuts_src.profile`). ``telemetry`` selects the injection
    density (one of ``header-summary`` / ``branch`` / ``full``; ignored
    when ``profile='release'``).
    """
    if mode not in _VALID_MODES:
        raise ValueError(f"invalid signing mode {mode!r}; expected one of {_VALID_MODES}")
    if profile not in _VALID_PROFILES:
        raise ValueError(f"invalid profile {profile!r}; expected one of {_VALID_PROFILES}")
    if telemetry not in DENSITIES:
        raise ValueError(f"invalid telemetry density {telemetry!r}; expected one of {DENSITIES}")

    src = Path(source).expanduser()
    if not src.exists():
        raise FileNotFoundError(src)

    shortcut = _load_shortcut(src)

    base = src.stem
    if base.endswith(".source"):
        base = base[: -len(".source")]

    if profile == "dev":
        inferred_category = category or _infer_category(src)
        inferred_name = shortcut_name or base
        shortcut = inject_dev_telemetry(
            shortcut,
            shortcut_name=inferred_name,
            category=inferred_category,
            density=telemetry,
        )

    binary = plist_io.dump_binary(shortcut)

    if out_path is None:
        suffix = ".unsigned.shortcut" if allow_unsigned else ".signed.shortcut"
        out = src.with_name(f"{base}{suffix}")
    else:
        out = Path(out_path).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)

    if allow_unsigned:
        out.write_bytes(binary)
        return out

    cli = _resolve_shortcuts_cli()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        unsigned = tmp_path / f"{base}.unsigned.shortcut"
        unsigned.write_bytes(binary)

        if keep_unsigned:
            kept = out.with_name(f"{base}.unsigned.shortcut")
            kept.write_bytes(binary)

        result = subprocess.run(
            [cli, "sign", "--mode", mode, "--input", str(unsigned), "--output", str(out)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip() or "<no stderr>"
            stdout = (result.stdout or "").strip()
            raise RuntimeError(
                "`shortcuts sign` failed (exit "
                f"{result.returncode}).\nstderr: {stderr}"
                + (f"\nstdout: {stdout}" if stdout else "")
            )
    return out
