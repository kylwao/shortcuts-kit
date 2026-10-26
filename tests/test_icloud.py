"""Unit tests for the iCloud URL helpers (no network access)."""

from __future__ import annotations

import pytest

from shortcuts_src.icloud import extract_record_id, is_icloud_shortcut_url


def test_valid_urls():
    assert is_icloud_shortcut_url("https://www.icloud.com/shortcuts/0123456789abcdef0123456789abcdef")
    assert is_icloud_shortcut_url("https://icloud.com/shortcuts/0123456789abcdef0123456789abcdef/")
    assert is_icloud_shortcut_url("https://www.icloud.com/shortcuts/0123456789ABCDEF0123456789ABCDEF?foo=bar")


def test_invalid_urls():
    assert not is_icloud_shortcut_url("")
    assert not is_icloud_shortcut_url("https://example.com/")
    assert not is_icloud_shortcut_url("https://www.icloud.com/shortcuts/tooshort")
    assert not is_icloud_shortcut_url("https://www.icloud.com/other/0123456789abcdef0123456789abcdef")


def test_extract_record_id_case_preserved():
    record_id = extract_record_id("https://www.icloud.com/shortcuts/0123456789ABCDEF0123456789ABCDEF")
    assert record_id == "0123456789ABCDEF0123456789ABCDEF"


def test_extract_record_id_rejects_invalid():
    with pytest.raises(ValueError):
        extract_record_id("https://example.com/")
