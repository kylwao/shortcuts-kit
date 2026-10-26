"""Regression tests against the in-repo ``examples/FoodAnalysis/V0.7`` sample.

The assertions are snapshot-level; they're *expected* to need updating if the
example is replaced by a newer version.
"""

from __future__ import annotations

from pathlib import Path

from shortcuts_src import plist_io
from shortcuts_src.compile import compile_source
from shortcuts_src.decompile import decompile_input, inspect_input
from shortcuts_src.flow import render_flow

_EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "FoodAnalysis" / "V0.7"
_STEM = "刚炫了啥 Bite Dance V0.7"
_FIXTURE_JSON = _EXAMPLE_DIR / f"{_STEM}.source.json"
_FIXTURE_XML = _EXAMPLE_DIR / f"{_STEM}.source.xml"
_ACTION_COUNT = 462


def test_xml_and_json_sources_are_equivalent():
    xml_obj = plist_io.loads(_FIXTURE_XML.read_bytes())
    json_obj = plist_io.loads(_FIXTURE_JSON.read_bytes())
    assert xml_obj == json_obj
    rebuilt = plist_io.loads(plist_io.dump_binary(json_obj))
    assert rebuilt == json_obj


def test_flow_renders_expected_markers():
    obj = plist_io.loads(_FIXTURE_JSON.read_bytes())
    md = render_flow(obj)
    assert f"动作数量：**{_ACTION_COUNT}**" in md
    assert "刚炫了啥（Bite Dance） V0.7" in md
    assert "豆包 AI 助手" in md
    assert "从菜单中选择" in md


def test_inspect_contains_key_lines():
    joined = "\n".join(inspect_input(str(_FIXTURE_JSON)))
    assert f"actions: {_ACTION_COUNT}" in joined


def test_decompile_into_tmp_roundtrips(tmp_path: Path):
    out = decompile_input(str(_FIXTURE_XML), out_dir=str(tmp_path), name="real")
    json_obj = plist_io.loads(out.files["json"].read_bytes())
    xml_obj = plist_io.loads(out.files["xml"].read_bytes())
    assert json_obj == xml_obj == out.shortcut


def test_compile_unsigned_roundtrips(tmp_path: Path):
    out = compile_source(
        str(_FIXTURE_JSON),
        out_path=str(tmp_path / "real.unsigned.shortcut"),
        allow_unsigned=True,
    )
    rebuilt = plist_io.loads(Path(out).read_bytes())
    assert rebuilt == plist_io.loads(_FIXTURE_JSON.read_bytes())
