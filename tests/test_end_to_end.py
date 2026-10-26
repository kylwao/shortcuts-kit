"""End-to-end tests against the in-repo minimal fixture.

These tests do not depend on anything outside the repository.
"""

from __future__ import annotations

import plistlib
from pathlib import Path

from shortcuts_src import plist_io
from shortcuts_src.compile import compile_source
from shortcuts_src.decompile import decompile_input, inspect_input

_FIXTURE_DIR = Path(__file__).parent / "fixtures"
_FIXTURE_JSON = _FIXTURE_DIR / "minimal.source.json"
_FIXTURE_XML = _FIXTURE_DIR / "minimal.source.xml"


def test_fixture_files_exist():
    assert _FIXTURE_JSON.exists()
    assert _FIXTURE_XML.exists()


def test_json_and_xml_fixtures_are_semantically_equal():
    assert plist_io.loads(_FIXTURE_JSON.read_bytes()) == plist_io.loads(_FIXTURE_XML.read_bytes())


def test_json_to_binary_roundtrip_is_lossless():
    obj = plist_io.loads(_FIXTURE_JSON.read_bytes())
    rebuilt = plist_io.loads(plist_io.dump_binary(obj))
    assert rebuilt == obj


def test_decompile_from_local_xml_emits_four_files(tmp_path: Path):
    out = decompile_input(str(_FIXTURE_XML), out_dir=str(tmp_path), name="mini")
    assert out.name == "mini"
    for label in ("xml", "json", "flow.md", "meta.json"):
        assert out.files[label] is not None and out.files[label].exists(), f"missing {label}"
    # bplist only when --keep-bplist passed
    assert out.files["bplist"] is None

    reparsed_xml = plist_io.loads(out.files["xml"].read_bytes())
    reparsed_json = plist_io.loads(out.files["json"].read_bytes())
    assert reparsed_xml == reparsed_json == out.shortcut


def test_compile_allow_unsigned_produces_valid_bplist(tmp_path: Path):
    out = compile_source(
        str(_FIXTURE_JSON),
        out_path=str(tmp_path / "out.shortcut"),
        allow_unsigned=True,
    )
    assert out.exists()
    raw = out.read_bytes()
    assert raw.startswith(b"bplist00")
    parsed = plistlib.loads(raw)
    assert parsed == plist_io.loads(_FIXTURE_JSON.read_bytes())


def test_inspect_reports_action_count_and_first_comment():
    lines = inspect_input(str(_FIXTURE_JSON))
    joined = "\n".join(lines)
    assert "actions: 9" in joined
    assert "minimal test fixture" in joined
