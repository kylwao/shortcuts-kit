"""Talk to the public iCloud Shortcuts CloudKit Records API.

Given a share URL like ``https://www.icloud.com/shortcuts/<id>`` we fetch
``https://www.icloud.com/shortcuts/api/records/<id>`` and follow
``fields.shortcut.value.downloadURL`` to retrieve the *unsigned* binary plist
representation of the workflow. This is the same technique used by
0xdevalias' notes and the huangzhuxing/ShortcutSourceTool project.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

_SHORTCUT_URL_RE = re.compile(
    r"^https?://(?:www\.)?icloud\.com/shortcuts/([A-Fa-f0-9]{32})(?:[/?#]|$)"
)
_API_URL = "https://www.icloud.com/shortcuts/api/records/{id}"
_USER_AGENT = "shortcuts-src/0.1 (+https://github.com/huangzhuxing/ShortcutSourceTool)"


def is_icloud_shortcut_url(value: str) -> bool:
    """Return True if value looks like an iCloud shortcut share URL."""
    return bool(_SHORTCUT_URL_RE.match(value.strip()))


def extract_record_id(url: str) -> str:
    """Extract the 32-char hex record id from an iCloud shortcut URL."""
    m = _SHORTCUT_URL_RE.match(url.strip())
    if not m:
        raise ValueError(f"not a valid iCloud shortcut URL: {url!r}")
    return m.group(1)


@dataclass(frozen=True)
class ICloudShortcutRecord:
    """Slim view of the CloudKit record response."""

    record_id: str
    name: str
    download_url: str
    signed_download_url: Optional[str]
    raw: dict


def _http_get(url: str, *, timeout: float = 30.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.read()
    except urllib.error.URLError as exc:
        # Bundled Python installs on macOS sometimes lack up-to-date CA certs,
        # which produces SSL certificate verification failures. Retry once with
        # verification disabled and warn loudly, unless the user forbids it via
        # SHORTCUTS_SRC_SSL_STRICT=1.
        reason = getattr(exc, "reason", None)
        is_cert_error = isinstance(reason, ssl.SSLCertVerificationError) or (
            isinstance(reason, ssl.SSLError) and "CERTIFICATE_VERIFY_FAILED" in str(reason)
        )
        if not is_cert_error or os.environ.get("SHORTCUTS_SRC_SSL_STRICT") == "1":
            raise
        print(
            f"warning: TLS certificate verification failed for {url!r}; "
            "retrying insecurely. Set SHORTCUTS_SRC_SSL_STRICT=1 to disable this fallback.",
            file=sys.stderr,
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:  # noqa: S310
            return resp.read()


def fetch_record(url_or_id: str, *, timeout: float = 30.0) -> ICloudShortcutRecord:
    """Fetch the CloudKit record metadata for a shortcut.

    Accepts either a full ``https://www.icloud.com/shortcuts/<id>`` URL or a
    bare 32-char hex record id.
    """
    record_id = extract_record_id(url_or_id) if url_or_id.startswith("http") else url_or_id.strip()
    if not re.fullmatch(r"[A-Fa-f0-9]{32}", record_id):
        raise ValueError(f"invalid record id: {record_id!r}")

    body = _http_get(_API_URL.format(id=record_id), timeout=timeout)
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"CloudKit response was not JSON: {exc}") from exc

    if data.get("deleted"):
        raise RuntimeError(f"shortcut {record_id} is marked deleted upstream")

    fields = data.get("fields") or {}
    shortcut_field = (fields.get("shortcut") or {}).get("value") or {}
    signed_field = (fields.get("signedShortcut") or {}).get("value") or {}
    name_field = (fields.get("name") or {}).get("value")

    download_url = shortcut_field.get("downloadURL")
    if not download_url:
        raise RuntimeError(
            "CloudKit record has no unsigned shortcut downloadURL "
            "(the shortcut may have been removed or is gallery-only)."
        )
    download_url = download_url.replace(r"\/", "/")
    signed_url = signed_field.get("downloadURL")
    if signed_url:
        signed_url = signed_url.replace(r"\/", "/")

    return ICloudShortcutRecord(
        record_id=record_id,
        name=name_field or record_id,
        download_url=download_url,
        signed_download_url=signed_url,
        raw=data,
    )


def download_unsigned_bplist(record: ICloudShortcutRecord, *, timeout: float = 60.0) -> bytes:
    """Download the raw bytes of the unsigned shortcut binary plist."""
    body = _http_get(record.download_url, timeout=timeout)
    if not body:
        raise RuntimeError("downloaded shortcut was empty")
    return body


def fetch_unsigned_bplist(url_or_id: str, *, timeout: float = 60.0) -> tuple[ICloudShortcutRecord, bytes]:
    """Convenience helper: record + bytes in one call."""
    record = fetch_record(url_or_id, timeout=timeout)
    data = download_unsigned_bplist(record, timeout=timeout)
    return record, data
