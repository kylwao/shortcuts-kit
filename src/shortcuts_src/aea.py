"""Detect and (best-effort) decrypt Apple Encrypted Archive (AEA) shortcuts.

``.shortcut`` files downloaded from iCloud since iOS 15 are wrapped in the
AEA container (``AEA1`` magic). For shortcuts signed in "Anyone" /
"People Who Know The Link" modes the AEA envelope is signed but not
password-protected, so ``/usr/bin/aea decrypt`` (profile 0) can unwrap
them locally on macOS.

For Apple Gallery-signed shortcuts the envelope uses a keypair we don't
have, so we raise a helpful error and suggest the iCloud URL path
instead.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Union

AEA_MAGIC = b"AEA1"
_AEA_BIN = "/usr/bin/aea"


def is_aea(data: Union[bytes, Path, str]) -> bool:
    """Return True if the first four bytes are the AEA magic."""
    if isinstance(data, (str, Path)):
        try:
            with open(data, "rb") as fp:
                head = fp.read(4)
        except OSError:
            return False
        return head == AEA_MAGIC
    return bool(data) and data[:4] == AEA_MAGIC


def _ensure_aea_cli() -> str:
    path = shutil.which("aea") or (_AEA_BIN if Path(_AEA_BIN).exists() else None)
    if not path:
        raise RuntimeError(
            "AEA-signed .shortcut detected but the `aea` CLI was not found. "
            "Install macOS 13+ which ships /usr/bin/aea, or re-run with the "
            "iCloud share URL so the unsigned version can be fetched directly."
        )
    return path


def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt AEA-wrapped bytes, returning the inner payload (typically a bplist).

    Only succeeds for self-signed shortcuts (anyone / people-who-know-the-link).
    """
    if not is_aea(data):
        raise ValueError("input is not AEA-wrapped (missing AEA1 magic)")
    aea = _ensure_aea_cli()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "input.aea"
        dst = tmp_path / "output.bin"
        src.write_bytes(data)
        result = subprocess.run(
            [aea, "decrypt", "-i", str(src), "-o", str(dst)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                "failed to decrypt AEA shortcut. This usually means the shortcut "
                "was signed by Apple (Gallery) and cannot be unwrapped without "
                "Apple's key. Try passing the iCloud share URL instead.\n"
                f"aea said: {stderr or '<no output>'}"
            )
        return dst.read_bytes()


def decrypt_file(path: Union[str, Path]) -> bytes:
    """Read an AEA file from disk and return its decrypted payload."""
    data = Path(path).read_bytes()
    return decrypt_bytes(data)
