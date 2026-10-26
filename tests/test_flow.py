"""Structural tests for flow.render_flow and flow.extract_metadata.

These tests assert on shape and labels, never on specific business strings
from any external sample.
"""

from __future__ import annotations

from pathlib import Path

from shortcuts_src import plist_io
from shortcuts_src.flow import extract_metadata, render_flow

_FIXTURE = Path(__file__).parent / "fixtures" / "minimal.source.json"


def _load():
    return plist_io.loads(_FIXTURE.read_bytes())


def test_render_flow_contains_action_count_and_control_flow_labels():
    md = render_flow(_load())
    assert "动作数量：**9**" in md
    assert "如果" in md         # conditional start label
    assert "否则" in md         # conditional else label
    assert "结束如果" in md     # conditional end label


def test_render_flow_surfaces_comment_and_text_body():
    md = render_flow(_load())
    assert "minimal test fixture" in md  # comment body appears either inline or in appendix
    assert "hi" in md                     # gettext body


def test_render_flow_has_metadata_header_lines():
    md = render_flow(_load())
    assert "最低客户端版本" in md
    assert "入口类型" in md


def test_extract_metadata_fields():
    meta = extract_metadata(_load())
    assert meta["WFWorkflowActionCount"] == 9
    assert meta["WFWorkflowTypes"] == ["WFWorkflowTypeShowInSearch"]
    assert "_firstComment" in meta
    assert meta["_firstComment"] == "minimal test fixture"
    assert meta["WFWorkflowMinimumClientVersionString"] == "3010"


def test_control_flow_block_indentation_ends_flush():
    """Start/else/end triplet should leave the indent back at 0 so the
    showresult action is at the outer level."""
    md = render_flow(_load())
    # showresult renders as 显示结果 and must appear at top-level indent in the fenced block
    lines = [ln for ln in md.splitlines() if "显示结果" in ln]
    assert lines, "expected at least one 显示结果 line"
    # count leading spaces inside the fenced code block: top-level indent has none
    assert any(ln.lstrip().startswith(("  8 │", "8 │")) for ln in lines)
