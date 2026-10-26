"""Unified plist / JSON IO helpers.

Apple Shortcut workflows are stored as binary property lists
(``bplist00``) but users will naturally want to edit either XML plists or
JSON. This module auto-detects the input format and provides loss-less
dumpers for all three, with the in-memory representation always being a
plain Python ``dict``.
"""

from __future__ import annotations

import base64
import datetime as _dt
import io
import json
import plistlib
from pathlib import Path
from typing import Any, Union

_BPLIST_MAGIC = b"bplist00"
_XML_PLIST_HINTS = (b"<?xml", b"<plist")

# Sentinel keys used in our JSON representation to round-trip plist-only
# value types (bytes, dates) that JSON doesn't natively support.
_BYTES_KEY = "__bplist_data_base64__"
_DATE_KEY = "__bplist_date_iso__"


def sniff_format(data: bytes) -> str:
    """Return one of 'bplist' | 'xml' | 'json' | 'aea' | 'unknown'."""
    if not data:
        return "unknown"
    if data.startswith(_BPLIST_MAGIC):
        return "bplist"
    if data[:4] == b"AEA1":
        return "aea"
    head = data.lstrip()[:16]
    if head.startswith(_XML_PLIST_HINTS):
        return "xml"
    if head[:1] in (b"{", b"["):
        return "json"
    return "unknown"


def _encode_for_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _encode_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_encode_for_json(v) for v in obj]
    if isinstance(obj, (bytes, bytearray)):
        return {_BYTES_KEY: base64.b64encode(bytes(obj)).decode("ascii")}
    if isinstance(obj, _dt.datetime):
        return {_DATE_KEY: obj.isoformat()}
    return obj


def _decode_from_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        if set(obj.keys()) == {_BYTES_KEY}:
            return base64.b64decode(obj[_BYTES_KEY])
        if set(obj.keys()) == {_DATE_KEY}:
            return _dt.datetime.fromisoformat(obj[_DATE_KEY])
        return {k: _decode_from_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decode_from_json(v) for v in obj]
    return obj


def loads(data: bytes) -> Any:
    """Parse bytes as a plist/JSON/AEA-encoded shortcut and return a Python obj."""
    fmt = sniff_format(data)
    if fmt == "bplist" or fmt == "xml":
        return plistlib.loads(data)
    if fmt == "json":
        text = data.decode("utf-8")
        return _decode_from_json(json.loads(text))
    if fmt == "aea":
        from .aea import decrypt_bytes  # local import avoids cycle
        return plistlib.loads(decrypt_bytes(data))
    raise ValueError("unable to determine plist/JSON format from input bytes")


def load_path(path: Union[str, Path]) -> Any:
    return loads(Path(path).read_bytes())


def dump_binary(obj: Any) -> bytes:
    """Serialize a shortcut dict as a binary plist (bplist00)."""
    return plistlib.dumps(obj, fmt=plistlib.FMT_BINARY, sort_keys=False)


def dump_xml(obj: Any) -> bytes:
    """Serialize as XML plist with a stable, Apple-compatible header."""
    return plistlib.dumps(obj, fmt=plistlib.FMT_XML, sort_keys=False)


def dump_json(obj: Any, *, indent: int = 2) -> bytes:
    """Serialize as UTF-8 JSON, preserving bytes/dates via sentinel keys."""
    buf = io.StringIO()
    json.dump(
        _encode_for_json(obj),
        buf,
        ensure_ascii=False,
        indent=indent,
        sort_keys=False,
    )
    buf.write("\n")
    return buf.getvalue().encode("utf-8")


def write_bytes(path: Union[str, Path], data: bytes) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return out
