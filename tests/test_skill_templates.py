"""Keep the Skill's blank template compilable."""

from __future__ import annotations

from pathlib import Path

from shortcuts_src import plist_io
from shortcuts_src.compile import compile_source
from shortcuts_src.flow import render_flow

_TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "apple-shortcuts"
    / "templates"
    / "blank.source.json"
)


def test_blank_template_compiles_and_renders(tmp_path: Path):
    obj = plist_io.loads(_TEMPLATE.read_bytes())
    uuids = [a["WFWorkflowActionParameters"]["UUID"] for a in obj["WFWorkflowActions"]]
    assert len(uuids) == len(set(uuids))

    out = compile_source(
        str(_TEMPLATE),
        out_path=str(tmp_path / "blank.unsigned.shortcut"),
        allow_unsigned=True,
    )
    assert plist_io.loads(Path(out).read_bytes()) == obj
    assert "动作数量：**3**" in render_flow(obj)
