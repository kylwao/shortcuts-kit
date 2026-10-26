"""Tests for ``shortcuts-src check``: structural validation of a workflow."""

from __future__ import annotations

from pathlib import Path

from shortcuts_src import plist_io
from shortcuts_src.check import check_input, check_workflow
from shortcuts_src.cli import main

_ROOT = Path(__file__).resolve().parents[1]
_MINIMAL = _ROOT / "tests" / "fixtures" / "minimal.source.json"
_TEMPLATE = _ROOT / "skills" / "apple-shortcuts" / "templates" / "blank.source.json"
_EXAMPLE = _ROOT / "examples" / "FoodAnalysis" / "V0.7" / "刚炫了啥 Bite Dance V0.7.source.json"

# minimal fixture: 0 comment, 1 gettext, 2 setvariable (uses #1), 3 if, 4 gettext,
# 5 otherwise, 6 gettext, 7 end if, 8 showresult
_IF = "is.workflow.actions.conditional"
_REPEAT = "is.workflow.actions.repeat.count"
_GROUP = "55555555-5555-4555-8555-555555555555"
_MISSING = "F0000000-0000-4000-8000-000000000000"


def _minimal() -> dict:
    return plist_io.load_path(_MINIMAL)


def _actions(shortcut: dict) -> list:
    return shortcut["WFWorkflowActions"]


def _params(shortcut: dict, index: int) -> dict:
    return _actions(shortcut)[index]["WFWorkflowActionParameters"]


def _flow(identifier: str, mode: int, group: str, uuid: str) -> dict:
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": {"UUID": uuid, "GroupingIdentifier": group, "WFControlFlowMode": mode},
    }


def _errors(findings: list) -> list:
    return [(f.index, f.code) for f in findings if f.severity == "error"]


def _warnings(findings: list) -> list:
    return [(f.index, f.code) for f in findings if f.severity == "warning"]


def test_clean_sources_have_no_findings():
    assert check_workflow(_minimal()) == []
    assert check_workflow(plist_io.load_path(_TEMPLATE)) == []


def test_example_has_no_errors_and_one_stale_reference():
    # Action #5 keeps a Date slot its "in the last 7 days" filter no longer uses; Shortcuts.app wrote it.
    findings = check_workflow(plist_io.load_path(_EXAMPLE))
    assert _errors(findings) == []
    assert _warnings(findings) == [(5, "dangling-ref")]


def test_duplicate_uuid_is_an_error_ignoring_case():
    shortcut = _minimal()
    _params(shortcut, 4)["UUID"] = "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"
    assert _errors(check_workflow(shortcut)) == [(8, "duplicate-uuid")]


def test_actions_without_uuid_are_allowed():
    shortcut = _minimal()
    for index in (4, 6):
        del _params(shortcut, index)["UUID"]
    assert check_workflow(shortcut) == []


def test_unclosed_block_is_reported_at_its_start():
    shortcut = _minimal()
    del _actions(shortcut)[7]
    assert _errors(check_workflow(shortcut)) == [(3, "unclosed-block")]


def test_end_without_start_is_an_error():
    shortcut = _minimal()
    _actions(shortcut).append(
        _flow(_IF, 2, "C0000000-0000-4000-8000-000000000000", "C0000000-0000-4000-8000-000000000001")
    )
    assert _errors(check_workflow(shortcut)) == [(9, "end-without-start")]


def test_branch_outside_block_is_an_error():
    shortcut = _minimal()
    _actions(shortcut).append(
        _flow(_IF, 1, "C0000000-0000-4000-8000-000000000000", "C0000000-0000-4000-8000-000000000001")
    )
    assert _errors(check_workflow(shortcut)) == [(9, "branch-outside-block")]


def test_interleaved_blocks_are_an_error():
    shortcut = _minimal()
    outer, inner = "D0000000-0000-4000-8000-00000000000A", "D0000000-0000-4000-8000-00000000000B"
    _actions(shortcut).extend(
        [
            _flow(_IF, 0, outer, "D0000000-0000-4000-8000-000000000001"),
            _flow(_REPEAT, 0, inner, "D0000000-0000-4000-8000-000000000002"),
            _flow(_IF, 2, outer, "D0000000-0000-4000-8000-000000000003"),
            _flow(_REPEAT, 2, inner, "D0000000-0000-4000-8000-000000000004"),
        ]
    )
    assert _errors(check_workflow(shortcut)) == [(11, "interleaved-block")]


def test_block_actions_must_share_one_identifier():
    shortcut = _minimal()
    _actions(shortcut)[7]["WFWorkflowActionIdentifier"] = _REPEAT
    assert _errors(check_workflow(shortcut)) == [(7, "identifier-mismatch")]


def test_grouping_identifier_reused_by_another_block_is_an_error():
    shortcut = _minimal()
    _actions(shortcut).extend(
        [
            _flow(_IF, 0, _GROUP, "E0000000-0000-4000-8000-000000000001"),
            _flow(_IF, 2, _GROUP, "E0000000-0000-4000-8000-000000000002"),
        ]
    )
    assert _errors(check_workflow(shortcut)) == [(9, "reused-grouping-id")]


def test_control_flow_action_needs_grouping_identifier():
    shortcut = _minimal()
    del _params(shortcut, 5)["GroupingIdentifier"]
    assert _errors(check_workflow(shortcut)) == [(5, "missing-grouping-id")]


def test_control_flow_mode_must_be_integer_0_1_or_2():
    shortcut = _minimal()
    _params(shortcut, 7)["WFControlFlowMode"] = "2"
    assert _errors(check_workflow(shortcut)) == [(3, "unclosed-block"), (7, "invalid-control-flow-mode")]


def test_reference_to_missing_action_is_a_warning():
    shortcut = _minimal()
    _params(shortcut, 2)["WFInput"]["Value"]["OutputUUID"] = _MISSING
    findings = check_workflow(shortcut)
    assert _errors(findings) == []
    assert _warnings(findings) == [(2, "dangling-ref")]


def test_references_inside_text_tokens_are_checked():
    template = plist_io.load_path(_TEMPLATE)
    _params(template, 2)["Text"]["Value"]["attachmentsByRange"]["{5, 1}"]["OutputUUID"] = _MISSING
    assert _warnings(check_workflow(template)) == [(2, "dangling-ref")]


def test_reference_to_itself_or_a_later_action_is_a_warning():
    shortcut = _minimal()
    _params(shortcut, 2)["WFInput"]["Value"]["OutputUUID"] = "88888888-8888-4888-8888-888888888888"
    _params(shortcut, 8)["Text"] = {
        "Value": {"OutputUUID": "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA", "Type": "ActionOutput", "OutputName": "Result"},
        "WFSerializationType": "WFTextTokenAttachment",
    }
    findings = check_workflow(shortcut)
    assert _errors(findings) == []
    assert _warnings(findings) == [(2, "forward-ref"), (8, "forward-ref")]


def test_xml_findings_point_at_the_action_line(tmp_path: Path):
    shortcut = _minimal()
    del _actions(shortcut)[7]
    path = tmp_path / "broken.source.xml"
    path.write_bytes(plist_io.dump_xml(shortcut))
    (finding,) = check_input(str(path)).findings
    lines = path.read_text(encoding="utf-8").splitlines()
    assert finding.index == 3
    assert lines[finding.line - 1].strip() == "<key>WFWorkflowActionIdentifier</key>"
    assert _IF in lines[finding.line]


def test_binary_input_has_no_line_numbers(tmp_path: Path):
    shortcut = _minimal()
    del _actions(shortcut)[7]
    path = tmp_path / "broken.shortcut"
    path.write_bytes(plist_io.dump_binary(shortcut))
    (finding,) = check_input(str(path)).findings
    assert finding.line is None


def test_cli_check_passes_clean_source(capsys):
    assert main(["check", str(_MINIMAL)]) == 0
    assert "0 errors, 0 warnings, 9 actions" in capsys.readouterr().out


def test_cli_check_exits_zero_when_only_warnings(capsys):
    assert main(["check", str(_EXAMPLE)]) == 0
    out = capsys.readouterr().out
    assert "warning #5 " in out
    assert "0 errors, 1 warning, 462 actions" in out


def test_cli_check_fails_on_errors_and_points_at_the_json_line(tmp_path: Path, capsys):
    shortcut = _minimal()
    _params(shortcut, 4)["UUID"] = "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"
    path = tmp_path / "broken.source.json"
    path.write_bytes(plist_io.dump_json(shortcut))
    assert main(["check", str(path)]) == 1
    out = capsys.readouterr().out
    lines = path.read_text(encoding="utf-8").splitlines()
    line = next(n for n, text in enumerate(lines, start=1) if '"is.workflow.actions.showresult"' in text)
    assert f"error #8 L{line} showresult [duplicate-uuid]" in out
    assert "1 error, 0 warnings, 9 actions" in out
