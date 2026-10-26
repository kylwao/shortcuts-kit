"""Tests for the log ingestion subsystem.

No iCloud / network / brctl access; uses only synthetic JSONL files in
tmp_path. The `download_icloud=False` flag (and staying outside the iCloud
root path) ensures brctl is never invoked.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from shortcuts_src.ingest import (
    Run,
    cross_reference,
    discover_project_debuglogs,
    ingest,
    parse_run,
    read_runs,
    render_report,
)

_FIXTURE_JSON = Path(__file__).parent / "fixtures" / "minimal.source.json"


def _write_jsonl(path: Path, *objs) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n",
        encoding="utf-8",
    )
    return path


def test_parse_run_happy_path(tmp_path: Path):
    log = _write_jsonl(
        tmp_path / "ok.jsonl",
        {"t": "header", "runId": "RUN-OK", "name": "mini", "cat": "test"},
        {"t": "step", "n": 3, "id": "is.workflow.actions.conditional", "uuid": "44444444-4444-4444-8444-444444444444", "ok": True},
        {"t": "summary", "ok": True},
    )
    run = parse_run(log)
    assert run.run_id == "RUN-OK"
    assert run.shortcut_name == "mini"
    assert len(run.steps) == 1
    assert run.summary is not None
    assert run.ok is True
    assert run.aborted is False


def test_parse_run_aborted_detected(tmp_path: Path):
    log = _write_jsonl(
        tmp_path / "aborted.jsonl",
        {"t": "header", "runId": "RUN-X", "name": "mini", "cat": "test"},
        {"t": "step", "n": 3, "id": "is.workflow.actions.conditional", "uuid": "u1", "ok": True},
        {"t": "step", "n": 5, "id": "com.bot.doubao.AskAssistantIntent", "uuid": "u2", "ok": True},
        # no summary
    )
    run = parse_run(log)
    assert run.aborted is True
    assert run.ok is False
    assert run.first_fail_step == 6  # last step.n (5) + 1


def test_parse_run_corrupt_header(tmp_path: Path):
    log = tmp_path / "corrupt.jsonl"
    log.write_text("this is not json\nnot even close\n", encoding="utf-8")
    run = parse_run(log)
    assert run.corrupt is True
    assert run.ok is False


def test_parse_run_tolerates_bad_lines(tmp_path: Path):
    log = tmp_path / "mixed.jsonl"
    log.write_text(
        '{"t":"header","runId":"X","name":"mini","cat":"test"}\n'
        "{ this is corrupt\n"
        '{"t":"step","n":1,"id":"is.workflow.actions.gettext","uuid":"u","ok":true}\n'
        '{"t":"summary","ok":true}\n',
        encoding="utf-8",
    )
    run = parse_run(log)
    assert run.ok is True
    assert len(run.steps) == 1


def test_read_runs_dedup_and_sort(tmp_path: Path):
    _write_jsonl(tmp_path / "a.jsonl", {"t": "header", "runId": "A", "name": "n", "cat": "c"}, {"t": "summary", "ok": True})
    _write_jsonl(tmp_path / "sub" / "b.log", {"t": "header", "runId": "B", "name": "n", "cat": "c"}, {"t": "summary", "ok": True})
    runs = read_runs([tmp_path], download_icloud=False)
    assert [r.run_id for r in runs] == ["A", "B"] or [r.run_id for r in runs] == ["B", "A"]
    # passing the same directory twice should not duplicate
    runs2 = read_runs([tmp_path, tmp_path], download_icloud=False)
    assert len(runs2) == 2


def test_cross_reference_pins_uuid_to_line_number(tmp_path: Path):
    log = _write_jsonl(
        tmp_path / "x.jsonl",
        {"t": "header", "runId": "R", "name": "mini", "cat": "test"},
        {"t": "step", "n": 3, "id": "is.workflow.actions.conditional",
         "uuid": "44444444-4444-4444-8444-444444444444", "ok": True},
        {"t": "summary", "ok": True},
    )
    runs = read_runs([tmp_path], download_icloud=False)
    runs = cross_reference(runs, _FIXTURE_JSON)
    step = runs[0].steps[0]
    assert step.source_index == 3
    assert step.source_line is not None and step.source_line > 0


def test_discover_project_debuglogs(tmp_path: Path):
    (tmp_path / "MyShortcuts" / "FoodAnalysis" / "V0.1" / "debuglog").mkdir(parents=True)
    (tmp_path / "MyShortcuts" / "FoodAnalysis" / "V0.2" / "debuglog").mkdir(parents=True)
    (tmp_path / "MyShortcuts" / "OtherCat" / "V1.0" / "debuglog").mkdir(parents=True)
    (tmp_path / "MyShortcuts" / "OtherCat" / "V1.0" / "notlog").mkdir(parents=True)
    found = discover_project_debuglogs(tmp_path)
    assert len(found) == 3
    assert all(p.name == "debuglog" for p in found)


def test_ingest_end_to_end_without_icloud(tmp_path: Path):
    # Create both iCloud-like and debuglog-style sources in tmp_path
    _write_jsonl(
        tmp_path / "cloud" / "RUN-OK.jsonl",
        {"t": "header", "runId": "RUN-OK", "name": "mini", "cat": "test"},
        {"t": "step", "n": 3, "id": "is.workflow.actions.conditional",
         "uuid": "44444444-4444-4444-8444-444444444444", "ok": True},
        {"t": "summary", "ok": True},
    )
    _write_jsonl(
        tmp_path / "MyShortcuts" / "test" / "V0.1" / "debuglog" / "RUN-BAD.log",
        {"t": "header", "runId": "RUN-BAD", "name": "mini", "cat": "test"},
        {"t": "step", "n": 7, "id": "com.bot.doubao.AskAssistantIntent",
         "uuid": "22222222-2222-4222-8222-222222222222", "ok": False, "out": "timeout"},
        # no summary -> aborted
    )
    runs, report = ingest(
        log_dirs=[tmp_path / "cloud"] + [tmp_path / "MyShortcuts" / "test" / "V0.1" / "debuglog"],
        source=_FIXTURE_JSON,
        project_root=tmp_path,
    )
    assert len(runs) == 2
    ok_run = next(r for r in runs if r.run_id == "RUN-OK")
    bad_run = next(r for r in runs if r.run_id == "RUN-BAD")
    assert ok_run.ok
    assert not bad_run.ok and bad_run.aborted
    # Report mentions both run ids and the count summary line
    assert "RUN-OK"[:8] in report
    assert "RUN-BAD"[:8] in report
    assert "2 次运行" in report


def test_ingest_only_failed_filter(tmp_path: Path):
    _write_jsonl(
        tmp_path / "ok.jsonl",
        {"t": "header", "runId": "OK", "name": "n", "cat": "c"},
        {"t": "summary", "ok": True},
    )
    _write_jsonl(
        tmp_path / "bad.jsonl",
        {"t": "header", "runId": "BAD", "name": "n", "cat": "c"},
        # no summary
    )
    runs, _ = ingest(log_dirs=[tmp_path], project_root=tmp_path, only_failed=True)
    assert len(runs) == 1 and runs[0].run_id == "BAD"


def test_render_report_empty_is_safe():
    report = render_report([])
    assert "没有日志" in report or "0 次运行" in report
