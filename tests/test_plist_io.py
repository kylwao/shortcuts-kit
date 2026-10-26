"""Unit tests for plist_io: format sniffing and lossless serialization."""

from __future__ import annotations

import datetime as _dt

import pytest

from shortcuts_src import plist_io


def test_sniff_format_variants():
    assert plist_io.sniff_format(b"bplist00\x00\x00") == "bplist"
    assert plist_io.sniff_format(b"<?xml version='1.0'?><plist/>") == "xml"
    assert plist_io.sniff_format(b"<plist><dict/></plist>") == "xml"
    assert plist_io.sniff_format(b'{"a":1}') == "json"
    assert plist_io.sniff_format(b"[1,2]") == "json"
    assert plist_io.sniff_format(b"AEA1payload") == "aea"
    assert plist_io.sniff_format(b"") == "unknown"
    assert plist_io.sniff_format(b"garbage") == "unknown"


def test_roundtrip_primitives():
    # plist doesn't model a NULL/None value, so we don't test it here.
    obj = {"a": 1, "b": 2.5, "c": "unicode 中文", "d": True, "e": False, "f": [1, "x"]}
    xml_bytes = plist_io.dump_xml(obj)
    json_bytes = plist_io.dump_json(obj)
    bin_bytes = plist_io.dump_binary(obj)
    assert plist_io.loads(xml_bytes) == obj
    assert plist_io.loads(json_bytes) == obj
    assert plist_io.loads(bin_bytes) == obj


def test_json_sentinel_for_bytes_and_dates():
    payload = {
        "blob": b"\x00\x01binary\xff",
        "when": _dt.datetime(2026, 4, 17, 19, 32, 10),
    }
    encoded = plist_io.dump_json(payload)
    # sentinel keys must appear in the encoded JSON text
    assert b"__bplist_data_base64__" in encoded
    assert b"__bplist_date_iso__" in encoded
    roundtrip = plist_io.loads(encoded)
    assert roundtrip == payload, "sentinel-encoded JSON must decode back to original"


def test_binary_output_starts_with_bplist_magic():
    obj = {"hello": "world"}
    assert plist_io.dump_binary(obj).startswith(b"bplist00")


def test_xml_output_has_plist_header():
    obj = {"hello": "world"}
    xml = plist_io.dump_xml(obj)
    assert xml.startswith(b"<?xml")
    assert b"<plist" in xml and b"</plist>" in xml


def test_loads_rejects_unknown_format():
    with pytest.raises(ValueError):
        plist_io.loads(b"not a plist and not json")


def test_field_order_preserved_through_binary_roundtrip():
    ordered = {"z": 1, "a": 2, "m": 3}
    bin_bytes = plist_io.dump_binary(ordered)
    restored = plist_io.loads(bin_bytes)
    assert list(restored.keys()) == list(ordered.keys())
